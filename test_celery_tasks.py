from app.crawlers.tasks import crawl_stock_data, crawl_financial_reports, crawl_news

def test_tasks():
    """测试Celery任务"""
    print("开始测试Celery任务...")
    
    # 测试股票数据爬取
    symbols = ["AAPL"]
    print("测试股票数据爬取...")
    crawl_stock_data.delay(symbols, "1d")
    
    # 测试财务报表爬取
    print("测试财务报表爬取...")
    crawl_financial_reports.delay(symbols, "10-K")
    
    # 测试新闻爬取
    print("测试新闻爬取...")
    crawl_news.delay(symbols, 1)
    
    print("任务已提交到Celery队列，请查看日志文件获取执行结果。")

if __name__ == "__main__":
    test_tasks() 