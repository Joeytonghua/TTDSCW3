import sqlite3
from config import DB_PATH
from evaluation import tfidf, bm25
import re

def determine_search_type(query,method):
    """
    确定搜索类型

    参数:
    - query: 搜索关键词
    """
    # 关键词搜索：只有一个关键词
    if len(query.split()) == 1:
        return keywordsearch(query,method)
    
    # 布尔搜索：包含 AND, OR, NOT 关键字
    if any(op in query for op in ["AND", "OR", "NOT"]):
        return boolean_search(query,method)
    
    # 临近搜索：符合 #d(a, b) 语法
    if query.startswith("#") and "(" in query and ")" in query:
        return proximity_search(query,method)
    
    # 默认返回短语搜索
    return phrase_search(query)

def keywordsearch(query,method):
    """
    关键词搜索
    参数:
    - query: 搜索关键词
    返回:
    - 搜索结果列表
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor() 
    # 搜索数据库中content含有query单词的新闻
    cursor.execute(
        "SELECT id, title, description, content, url, published_at, source_name, source_url FROM news "
        "WHERE content LIKE ?",
        ('%' + query + '%',)
    )
    results = cursor.fetchall()
    conn.close()
    # 根据method对结果进行排序
    if method == "tfidf":
        sorted_results = tfidf(results, query)
    elif method == "bm25":
        sorted_results = bm25(results, query)
    else:
        sorted_results = results
    return sorted_results

def boolean_search(query,method):
    """
    布尔搜索

    参数:
    - query: 搜索关键词

    返回:
    - 搜索结果列表
    """
    # 这里添加布尔搜索的实现
    return ["boolean_result1", "boolean_result2"]

def phrase_search(query):
    """
    短语搜索
    参数:
    - query: 搜索关键词
    返回:
    - 搜索结果列表
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()    
    # 搜索数据库中content含有query短语的新闻
    cursor.execute(
        "SELECT id, title, description, content, url, published_at, source_name, source_url FROM news "
        "WHERE content LIKE ?",
        ('%' + query.strip('"') + '%',)
    )
    results = cursor.fetchall()
    conn.close()
    return results


def proximity_search(query, method):
    """
    临近搜索

    参数:
    - query: 搜索关键词
    - method: 搜索方法 (tfidf或bm25)

    返回:
    - 搜索结果列表
    """
    # 解析查询语法 #d(a, b)
    match = re.match(r"#(\d+)\((\w+),\s*(\w+)\)", query)
    if not match:
        return []

    distance = int(match.group(1))
    term1 = match.group(2)
    term2 = match.group(3)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有新闻数据
    cursor.execute(
        "SELECT id, title, description, content, url, published_at, source_name, source_url FROM news"
    )
    all_results = cursor.fetchall()
    conn.close()

    filtered_results = []
    for result in all_results:
        content = result[3].split()
        positions1 = [i for i, word in enumerate(content) if word == term1]
        positions2 = [i for i, word in enumerate(content) if word == term2]

        if any(abs(p1 - p2) <= distance for p1 in positions1 for p2 in positions2):
            filtered_results.append(result)

    # 根据method对结果进行排序
    if method == "tfidf":
        sorted_results = tfidf(filtered_results, f"{term1} {term2}")
    elif method == "bm25":
        sorted_results = bm25(filtered_results, f"{term1} {term2}")
    else:
        sorted_results = filtered_results

    return sorted_results