import aiohttp
import asyncio
import datetime
import hashlib
import json
from queries import QUERIES  # 从独立的 queries.py 文件导入
from config import GNEWS_API_KEY, GNEWS_BASE_URL
from database import insert_news, check_duplicate  # check_duplicate 用于去重

# API 限制：每天 25,000 条
TARGET_COUNT = 10000000
BATCH_SIZE = 100  # API 每次返回 100 条
START_YEAR = 2009  # 从 2009 年抓取
END_YEAR = 2025  # 直到 2025 年

async def fetch_news(session, query, from_date, to_date):
    """从 GNews API 异步获取新闻"""
    url = (f"{GNEWS_BASE_URL}q={query}&lang=en&max={BATCH_SIZE}&apikey={GNEWS_API_KEY}"
           f"&from={from_date}&to={to_date}")
    
    async with session.get(url) as response:
        if response.status != 200:
            print(f"❌ 请求失败: {await response.text()}")
            return []
        
        data = await response.json()
        return data.get("articles", [])

async def save_gnews():
    """遍历 2009-2025 年，每个类别，每个关键词，抓取新闻"""
    total_saved = 0
    async with aiohttp.ClientSession() as session:
        for year in range(START_YEAR, END_YEAR + 1):
            for category, keywords in QUERIES.items():
                for query in keywords:
                    if total_saved >= TARGET_COUNT:
                        break

                    # 设置时间范围
                    from_date = f"{year}-01-01T00:00:00Z"
                    to_date = f"{year}-12-31T23:59:59Z"

                    print(f"📢 正在抓取: {query} ({category}) {year}")
                    articles = await fetch_news(session, query, from_date, to_date)

                    for article in articles:
                        if total_saved >= TARGET_COUNT:
                            break

                        title = article.get("title", "No Title")
                        description = article.get("description", "No Description")
                        content = article.get("content", "No Content")
                        url = article.get("url", "No URL")
                        published_at = article.get("publishedAt", "No Date")
                        source_name = article.get("source", {}).get("name", "Unknown Source")
                        source_url = article.get("source", {}).get("url", "No Source URL")

                        # 计算 hash（去重）
                        news_hash = hashlib.md5(f"{title}{published_at}".encode()).hexdigest()
                        if check_duplicate(news_hash):
                            continue  # 跳过重复数据

                        if content:
                            insert_news(news_hash, title, description, content, url, published_at, source_name, source_url)
                            total_saved += 1

                    print(f"📊 当前已存入: {total_saved}/{TARGET_COUNT}")
                    await asyncio.sleep(1)  # 避免 API 限制

    print(f"✅ 总共存入 {total_saved} 篇新闻")

if __name__ == "__main__":
    asyncio.run(save_gnews())
