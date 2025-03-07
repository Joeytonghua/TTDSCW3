import sqlite3
from config import DB_PATH

def create_table():
    """创建数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        content TEXT,
        url TEXT,
        published_at TEXT,
        source_name TEXT,
        source_url TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_news(news_hash, title, description, content, url, published_at, source_name, source_url):
    """插入新闻（去重存储）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO news (id, title, description, content, url, published_at, source_name, source_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (news_hash, title, description, content, url, published_at, source_name, source_url))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # 发现重复数据，不插入
    finally:
        conn.close()

def check_duplicate(news_hash):
    """检查新闻是否已经存在（去重逻辑）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM news WHERE id=?", (news_hash,))
    exists = cursor.fetchone()
    conn.close()
    return exists is not None  # 如果存在，则返回 True


if __name__ == "__main__":
    create_table()
