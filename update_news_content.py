import sqlite3
import aiohttp
import asyncio
import random
import tqdm  # 进度条
import requests
from bs4 import BeautifulSoup
from config import DB_PATH

# 限制最大并发请求数
MAX_CONCURRENT_REQUESTS = 5
TIMEOUT = 15  # 请求超时时间

# 伪装成移动设备，减少封锁
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# 发送 Cookie 以跳过弹窗
COOKIES = {
    "euconsent": "true",
    "gdpr": "1",
    "cookie-consent": "accepted",
}


def fetch_with_requests(url):
    """使用 requests 处理超长 HTTP 头的网站"""
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Referer": url,
        }
        response = requests.get(url, headers=headers, cookies=COOKIES, timeout=TIMEOUT, allow_redirects=True)
        if response.status_code != 200:
            print(f"❌ requests 访问失败 {url}，状态码: {response.status_code}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        full_text = "\n".join([p.get_text() for p in paragraphs]).strip()
        return full_text if full_text else None
    except Exception as e:
        print(f"⚠️ requests 解析失败 {url}: {e}")
        return None


async def fetch_full_content(session, url, bar):
    """异步获取完整新闻正文"""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": url,
    }

    try:
        async with session.get(url, headers=headers, cookies=COOKIES, timeout=TIMEOUT,
                               allow_redirects=True) as response:
            if response.status in [403, 404]:
                print(f"🚫 访问被拒绝（{response.status}），跳过：{url}")
                bar.update(1)
                return None
            if response.status != 200:
                print(f"❌ 访问失败 {url}，状态码: {response.status}")
                bar.update(1)
                return None

            html = await response.text(encoding="utf-8", errors="ignore")
            try:
                soup = BeautifulSoup(html, "html.parser")
            except Exception:
                soup = BeautifulSoup(html, "html5lib")

            article = soup.find("article")
            if article:
                paragraphs = article.find_all("p")
            else:
                content_divs = ["article-content", "entry-content", "post-content", "news-content"]
                for div_class in content_divs:
                    article = soup.find("div", class_=div_class)
                    if article:
                        paragraphs = article.find_all("p")
                        break
                else:
                    main = soup.find("main")
                    if main:
                        paragraphs = main.find_all("p")
                    else:
                        bar.update(1)
                        return None

            full_text = "\n".join([p.get_text() for p in paragraphs]).strip()
            bar.update(1)
            return full_text if full_text else None

    except asyncio.TimeoutError:
        print(f"⚠️ 请求超时: {url}")
        bar.update(1)
        return None
    except aiohttp.ClientError as e:
        # 如果是 Header 过长错误，直接用 requests 处理
        if "Got more than" in str(e) and "when reading Header value is too long" in str(e):
            print(f"⚠️ Header 过长，切换 requests 处理: {url}")
            content = fetch_with_requests(url)
            bar.update(1)
            return content
        print(f"⚠️ 网络错误 {url}: {e}")
        bar.update(1)
        return None


async def update_news_content():
    """异步更新数据库，将 content 替换为从 URL 解析的完整新闻正文"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, url, content FROM news ORDER BY published_at DESC")
    news_items = cursor.fetchall()
    
    failed_news_ids = []  # 存储需要删除的新闻 ID
    updated_data = []
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=100, ssl=False)) as session:
        with tqdm.tqdm(total=len(news_items), desc="正在爬取新闻") as bar:
            async def process_news(news_id, url, old_content):
                async with sem:
                    await asyncio.sleep(random.uniform(0.2, 0.8))
                    new_content = await fetch_full_content(session, url, bar)
                    
                    if not new_content or len(new_content) < 50:
                        print(f"❌ 获取失败，记录待删除新闻: {news_id}")
                        failed_news_ids.append(news_id)
                        return  # 直接返回，跳过存储
                    
                    updated_data.append((new_content, news_id))

            tasks = [process_news(news_id, url, old_content) for news_id, url, old_content in news_items]
            await asyncio.gather(*tasks)

    # 删除获取失败的新闻
    if failed_news_ids:
        cursor.executemany("DELETE FROM news WHERE id = ?", [(news_id,) for news_id in failed_news_ids])
        print(f"🗑️ 已删除 {len(failed_news_ids)} 条无效新闻")

    # 更新新闻内容
    if updated_data:
        cursor.executemany("UPDATE news SET content = ? WHERE id = ?", updated_data)
        print(f"🎉 更新完成，共更新 {len(updated_data)} 条新闻")

    # 额外删除 content 单词数少于 15 的新闻
    cursor.execute("DELETE FROM news WHERE (LENGTH(content) - LENGTH(REPLACE(content, ' ', ''))) < 100")
    deleted_rows = cursor.rowcount
    print(f"🗑️ 额外删除 {deleted_rows} 条单词数过少的新闻")
    conn.commit()
    conn.close()


def run_async():
    import sys
    try:
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(update_news_content())
    except KeyboardInterrupt:
        print("\n🛑 用户终止，安全退出...")


if __name__ == "__main__":
    run_async()
