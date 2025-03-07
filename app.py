import os
import time
from flask import Flask, render_template, request, jsonify
import sqlite3
import re
from config import DB_PATH
from flask_cors import CORS
import math
import search_functions as search_functions
from evaluation import tfidf, bm25


def create_app():
    """使用工厂模式创建Flask应用"""
    app = Flask(__name__)

    # 启用CORS支持，允许前端访问
    CORS(app, resources={r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }})

    # 使用with_appcontext替代before_first_request
    # 我们改为在应用启动前初始化索引

    def check_required_files():
        """检查必要的文件是否存在"""
        files_to_check = [
            {"path": "inverted_index.json", "type": "索引文件"},
            {"path": DB_PATH, "type": "数据库文件"}
        ]

        missing_files = []
        for file_info in files_to_check:
            if not os.path.exists(file_info["path"]):
                missing_files.append(f"{file_info['type']} ({file_info['path']})")

        if missing_files:
            print("警告: 以下必要文件不存在:")
            for missing in missing_files:
                print(f" - {missing}")
            return False
        return True

    def classify_search_query(query):
        """根据查询类型调用不同的搜索函数"""
        query = query.strip().lower()  # 统一转换为小写

        # 近邻搜索匹配：#数字 + 词1 + 词2
        proximity_pattern = r"^#\d+\s+\w+\s+\w+$"

        # 短语搜索匹配："xxx xxx"
        phrase_pattern = r'^".+"$'

        # 布尔搜索匹配
        and_not_pattern = r"\b\w+\s+and\s+not\s+\w+\b"
        and_pattern = r"\b\w+\s+and\s+\w+\b"
        or_pattern = r"\b\w+\s+or\s+\w+\b"
        not_pattern = r"\bnot\s+\w+\b"

        # 根据匹配模式选择搜索函数
        if re.match(proximity_pattern, query):
            return search_functions.proximity_search(query)
        elif re.match(phrase_pattern, query):
            return search_functions.phrase_search(query)
        elif re.match(and_not_pattern, query):
            return search_functions.boolean_search_and_not(query)
        elif re.match(and_pattern, query):
            return search_functions.boolean_search_and(query)
        elif re.match(or_pattern, query):
            return search_functions.boolean_search_or(query)
        else:
            return search_functions.keyword_search(query)

    def query_news(query, method="tfidf", page=1, limit=10):
        """
        搜索数据库中的新闻

        参数:
        - query: 搜索关键词
        - method: 搜索方法 (tfidf或bm25)
        - page: 页码
        - limit: 每页结果数

        返回:
        - 搜索结果列表
        - 总结果数
        """
        # 确保索引已加载
        if app.config.get('FIRST_REQUEST', True):
            search_functions.initialize_index()
            app.config['FIRST_REQUEST'] = False

        start_time = time.time()

        # 执行搜索
        all_results = classify_search_query(query)
        print(f"查询分类完成，耗时: {time.time() - start_time:.4f} 秒")

        # 根据method对结果进行排序
        rank_start = time.time()
        if method == "tfidf":
            all_results = tfidf(all_results, query)
        elif method == "bm25":
            all_results = bm25(all_results, query)
        print(f"排序完成，方法: {method}，耗时: {time.time() - rank_start:.4f} 秒")

        # 计算总结果数和总页数
        total_results = len(all_results)
        total_pages = math.ceil(total_results / limit)

        # 分页
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paged_results = all_results[start_idx:end_idx]

        # 将结果转换为字典列表
        formatted_results = []
        for row in paged_results:
            result = {
                "id": row['id'],
                "title": row['title'],
                "snippet": row['snippet'][:300] + "..." if row['snippet'] and len(row['snippet']) > 300 else row[
                    'snippet'],
                "content": row['content'],
                "url": row['url'],
                "publishedDate": row['published_at'],
                "source": row['source_name'],
                "sourceUrl": row['source_url']
            }
            formatted_results.append(result)

        # 计算总耗时
        total_time = time.time() - start_time
        print(f"搜索完成，总耗时: {total_time:.4f} 秒，结果数: {total_results}")

        return formatted_results, total_results, total_pages

    @app.route("/")
    def home():
        """首页路由"""
        # 确保索引已加载
        if app.config.get('FIRST_REQUEST', True):
            search_functions.initialize_index()
            app.config['FIRST_REQUEST'] = False

        return render_template("index.html")

    @app.route("/api/search", methods=["GET"])
    def search():
        """API端点，用于处理搜索请求"""
        try:
            query = request.args.get("query", "").strip()
            method = request.args.get("method", "tfidf")
            page = int(request.args.get("page", 1))
            limit = int(request.args.get("limit", 10))

            if not query:
                return jsonify({
                    "results": [],
                    "totalResults": 0,
                    "totalPages": 0
                })

            # 打印调试信息
            print(f"Processing search query: '{query}', method: {method}, page: {page}, limit: {limit}")

            results, total_results, total_pages = query_news(query, method, page, limit)

            return jsonify({
                "results": results,
                "totalResults": total_results,
                "totalPages": total_pages
            })
        except Exception as e:
            # 打印详细错误信息到后端控制台
            import traceback
            print(f"ERROR in search route: {str(e)}")
            print(traceback.format_exc())

            # 返回友好的错误信息给前端
            return jsonify({
                "error": f"搜索处理出错: {str(e)}",
                "results": [],
                "totalResults": 0,
                "totalPages": 0
            }), 500

    @app.route("/api/suggestions", methods=["GET"])
    def get_suggestions():
        """API端点，提供搜索建议"""
        # 确保索引已加载
        if app.config.get('FIRST_REQUEST', True):
            search_functions.initialize_index()
            app.config['FIRST_REQUEST'] = False

        query = request.args.get("query", "").strip()

        if not query or len(query) < 2:
            return jsonify({"suggestions": []})

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 基于部分匹配获取标题建议
        cursor.execute(
            "SELECT DISTINCT title FROM news WHERE title LIKE ? LIMIT 10",
            ('%' + query + '%',)
        )

        suggestions = [row[0] for row in cursor.fetchall()]
        conn.close()

        return jsonify({"suggestions": suggestions})

    @app.route("/api/stats", methods=["GET"])
    def get_stats():
        """API端点，提供索引和搜索统计信息"""
        # 确保索引已加载
        if app.config.get('FIRST_REQUEST', True):
            search_functions.initialize_index()
            app.config['FIRST_REQUEST'] = False

        try:
            # 获取索引信息
            from redis_index_manager import index_manager
            index, doc_id_map = index_manager.get_index()

            return jsonify({
                "index_stats": {
                    "terms_count": len(index),
                    "documents_count": len(doc_id_map),
                    "status": "loaded"
                }
            })
        except Exception as e:
            return jsonify({
                "error": f"获取统计信息出错: {str(e)}",
                "index_stats": {
                    "status": "error"
                }
            }), 500

    # 设置一个初始标记来跟踪是否是第一次请求
    app.config['FIRST_REQUEST'] = True

    # 检查所需的文件
    if check_required_files():
        print("✅ 所有必要文件已找到")
    else:
        print("⚠️ 部分必要文件缺失，应用可能无法正常工作")

    return app


# 创建应用实例
app = create_app()

if __name__ == "__main__":
    # 启动Flask应用，禁用自动重载以保持索引在内存中
    app.run(debug=True, port=5001, use_reloader=False)