from app.crawlers.yahoo_finance import YahooFinanceCrawler
from app.core.database import SessionLocal

def test_stock_crawler():
    """测试股票数据爬虫"""
    print("开始测试股票数据爬取...")
    db = SessionLocal()
    try:
        crawler = YahooFinanceCrawler(db)
        # 获取过去一年的数据
        success = crawler.crawl_stock_data(["AAPL", "GOOGL"], "1y")
        print(f"爬取结果: {'成功' if success else '失败'}")
    finally:
        db.close()

if __name__ == "__main__":
    test_stock_crawler() 