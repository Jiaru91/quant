from celery import Celery
from celery.schedules import crontab
from config.dev import settings

# 创建 Celery 实例
celery_app = Celery(
    "quant",
    broker='amqp://guest:guest@localhost:5672//',
    backend='rpc://',
    include=[
        'app.crawlers.tasks'  # 包含任务模块
    ]
)

# Celery 配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    broker_connection_retry_on_startup=True,  # 添加这个配置
    
    # 配置定时任务
    beat_schedule={
        # 股票数据 - 每个交易日（周一到周五）的收盘后更新
        'crawl-stock-data-daily': {
            'task': 'app.crawlers.tasks.crawl_stock_data',
            'schedule': crontab(hour=16, minute=30, day_of_week='1-5'),  # 每个工作日下午4:30
            'args': (["AAPL", "GOOGL", "MSFT", "AMZN", "META"], "1d")
        },
        
        # 年度财务报表 - 每周一更新
        'crawl-annual-reports-weekly': {
            'task': 'app.crawlers.tasks.crawl_financial_reports',
            'schedule': crontab(hour=1, minute=0, day_of_week='1'),  # 每周一凌晨1点
            'args': (["AAPL", "GOOGL", "MSFT", "AMZN", "META"], "10-K")
        },
        
        # 季度财务报表 - 每周一更新
        'crawl-quarterly-reports-weekly': {
            'task': 'app.crawlers.tasks.crawl_financial_reports',
            'schedule': crontab(hour=2, minute=0, day_of_week='1'),  # 每周一凌晨2点
            'args': (["AAPL", "GOOGL", "MSFT", "AMZN", "META"], "10-Q")
        },
        
        # 新闻数据 - 每天更新两次
        'crawl-news-morning': {
            'task': 'app.crawlers.tasks.crawl_news',
            'schedule': crontab(hour=9, minute=30),  # 每天早上9:30
            'args': (["AAPL", "GOOGL", "MSFT", "AMZN", "META"], 1)
        },
        'crawl-news-evening': {
            'task': 'app.crawlers.tasks.crawl_news',
            'schedule': crontab(hour=16, minute=30),  # 每天下午4:30
            'args': (["AAPL", "GOOGL", "MSFT", "AMZN", "META"], 1)
        }
    }
)

if __name__ == '__main__':
    celery_app.start() 