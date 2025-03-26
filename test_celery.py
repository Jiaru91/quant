from app.crawlers.tasks import crawl_stock_data
from datetime import datetime

def test_celery_task():
    """测试 Celery 任务"""
    print(f"\n开始测试 Celery 任务 - {datetime.now()}")
    
    # 测试股票数据爬取任务
    symbols = ["AAPL"]  # 只测试苹果股票
    
    print("\n发送任务到 Celery...")
    result = crawl_stock_data.delay(symbols, "1d")
    
    print("\n等待任务完成...")
    try:
        success = result.get(timeout=30)  # 等待任务完成，最多等待30秒
        if success:
            print("\n✅ 任务成功完成！")
        else:
            print("\n❌ 任务执行失败")
    except Exception as e:
        print(f"\n❌ 任务执行出错: {str(e)}")

if __name__ == "__main__":
    test_celery_task() 