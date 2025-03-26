from celery import shared_task, group
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.crawlers.yahoo_finance import YahooFinanceCrawler
from app.crawlers.financial_report import FinancialReportCrawler
from app.crawlers.news import NewsCrawler
import logging
from typing import List
from app.crawlers.stock_crawler import StockCrawler
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def crawl_stock_data(self, symbols: List[str], period: str = "1d"):
    """爬取股票数据的Celery任务"""
    try:
        logger.info(f"开始爬取股票数据: {symbols}")
        crawler = StockCrawler()
        success = crawler.crawl_stock_data(symbols, period)
        if not success:
            raise Exception(f"Failed to crawl stock data for symbols: {symbols}")
        return success
    except Exception as e:
        logger.error(f"爬取股票数据时发生错误: {str(e)}")
        raise self.retry(exc=e)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def crawl_financial_reports(self, symbols: List[str], report_type: str = "10-K"):
    """爬取财务报告的Celery任务"""
    try:
        logger.info(f"开始爬取财务报告: {symbols}")
        crawler = FinancialReportCrawler()
        success = crawler.crawl_financial_reports(symbols, report_type)
        if not success:
            raise Exception(f"Failed to crawl financial reports for symbols: {symbols}")
        return success
    except Exception as e:
        logger.error(f"爬取财务报告时发生错误: {str(e)}")
        raise self.retry(exc=e)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True
)
def crawl_news(self, symbols: List[str], days: int = 7):
    """爬取新闻的Celery任务"""
    try:
        logger.info(f"开始爬取新闻: {symbols}")
        db = SessionLocal()
        crawler = NewsCrawler(db)
        success = crawler.crawl_news(symbols, days)
        if not success:
            raise Exception(f"Failed to crawl news for symbols: {symbols}")
        return success
    except Exception as e:
        logger.error(f"爬取新闻时发生错误: {str(e)}")
        raise self.retry(exc=e)
    finally:
        db.close()

@shared_task
def schedule_crawling_tasks():
    """调度爬虫任务的Celery任务"""
    symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "META"]
    
    # 创建任务组
    tasks = group(
        crawl_stock_data.s(symbols, "1d"),
        crawl_financial_reports.s(symbols, "10-K"),
        crawl_news.s(symbols, 7)
    )
    
    # 执行任务组
    return tasks.apply_async() 