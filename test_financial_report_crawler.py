from app.crawlers.financial_report import FinancialReportCrawler
from app.core.database import SessionLocal

def test_financial_report_crawler():
    """测试财务报表爬虫"""
    print("开始测试财务报表爬取...")
    db = SessionLocal()
    try:
        crawler = FinancialReportCrawler(db)
        # 获取年报和季报
        for report_type in ["10-K", "10-Q"]:
            success = crawler.crawl_financial_reports("AAPL", report_type)
            print(f"爬取 {report_type} 结果: {'成功' if success else '失败'}")
    finally:
        db.close()

if __name__ == "__main__":
    test_financial_report_crawler() 