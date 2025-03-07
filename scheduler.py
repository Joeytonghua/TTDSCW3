import time
from fetch_gnews import save_gnews

def scheduled_fetch():
    """定时更新新闻，每6小时运行一次"""
    while True:
        print("⏳ 正在抓取最新新闻...")
        save_gnews()
        print("✅ 新闻更新完成，等待 6 小时后继续")
        time.sleep(6 * 3600)  # 6 小时

if __name__ == "__main__":
    scheduled_fetch()
