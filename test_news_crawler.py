from app.crawlers.news import NewsCrawler
from app.core.database import SessionLocal

def test_news_crawler():
    """测试新闻数据爬虫"""
    print("开始测试新闻数据爬取...")
    db = SessionLocal()
    try:
        crawler = NewsCrawler(db)
        # 获取过去7天的新闻
        success = crawler.crawl_news("AAPL", days=7)
        print(f"爬取结果: {'成功' if success else '失败'}")
    finally:
        db.close()

if __name__ == "__main__":
    test_news_crawler() 