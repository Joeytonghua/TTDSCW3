import sqlite3

db_file="news.db"
# **数据库查询函数**
def fetch_news_from_db(doc_ids, db_file):
    """从 SQLite 数据库中查询完整新闻数据"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 查询数据库
    placeholders = ",".join(["?" for _ in doc_ids])  # 生成 (?, ?, ?) 形式的参数
    query = f"""
    SELECT id, title, description, content, url, published_at, source_name, source_url 
    FROM news 
    WHERE id IN ({placeholders})
    """
    cursor.execute(query, doc_ids)

    # 获取查询结果
    results = [
        {
            "id": row[0],
            "title": row[1],
            "snippet": row[2],
            "content": row[3],
            "url": row[4],
            "published_at": row[5],
            "source_name": row[6],
            "source_url": row[7],
        }
        for row in cursor.fetchall()
    ]

    conn.close()
    return results