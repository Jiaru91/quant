from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.crawler import StockData, FinancialReport, News
from config.dev import settings
import pandas as pd
from datetime import datetime, timedelta

# 创建数据库连接
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def check_stock_data():
    """检查股票数据"""
    try:
        # 获取股票数据统计
        stock_count = db.query(StockData).count()
        symbols = db.query(StockData.symbol).distinct().all()
        symbols = [symbol[0] for symbol in symbols]
        
        # 获取最近24小时的数据
        recent_data = db.query(StockData).filter(
            StockData.created_at >= datetime.now() - timedelta(hours=24)
        ).all()
        
        print("\n=== 股票数据统计 ===")
        print(f"总记录数: {stock_count}")
        print(f"股票代码: {symbols}")
        print(f"最近24小时新增记录数: {len(recent_data)}")
        
        if recent_data:
            print("\n最新数据示例:")
            for data in recent_data[:5]:  # 显示前5条记录
                print(f"股票: {data.symbol}, 日期: {data.date}, "
                      f"收盘价: {data.close_price}, 成交量: {data.volume}")
    except Exception as e:
        print(f"检查股票数据时出错: {str(e)}")

def check_financial_reports():
    """检查财务报表数据"""
    try:
        # 获取财务报表统计
        report_count = db.query(FinancialReport).count()
        companies = db.query(FinancialReport.company_symbol).distinct().all()
        companies = [company[0] for company in companies]
        
        # 获取最近24小时的数据
        recent_reports = db.query(FinancialReport).filter(
            FinancialReport.created_at >= datetime.now() - timedelta(hours=24)
        ).all()
        
        print("\n=== 财务报表统计 ===")
        print(f"总记录数: {report_count}")
        print(f"公司列表: {companies}")
        print(f"最近24小时新增记录数: {len(recent_reports)}")
        
        if recent_reports:
            print("\n最新报表示例:")
            for report in recent_reports[:5]:
                print(f"公司: {report.company_symbol}, 类型: {report.report_type}, "
                      f"日期: {report.report_date}")
    except Exception as e:
        print(f"检查财务报表时出错: {str(e)}")

def check_news():
    """检查新闻数据"""
    try:
        # 获取新闻统计
        news_count = db.query(News).count()
        
        # 获取最近24小时的数据
        recent_news = db.query(News).filter(
            News.created_at >= datetime.now() - timedelta(hours=24)
        ).all()
        
        print("\n=== 新闻数据统计 ===")
        print(f"总记录数: {news_count}")
        print(f"最近24小时新增记录数: {len(recent_news)}")
        
        if recent_news:
            print("\n最新新闻示例:")
            for news in recent_news[:5]:
                print(f"标题: {news.title}")
                print(f"发布时间: {news.published_date}")
                print(f"来源: {news.source}")
                print("---")
    except Exception as e:
        print(f"检查新闻数据时出错: {str(e)}")

if __name__ == "__main__":
    print("开始检查数据库数据...")
    check_stock_data()
    check_financial_reports()
    check_news()
    print("\n数据检查完成!") 