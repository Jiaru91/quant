from app.crawlers.stock_crawler import StockCrawler
from app.core.database import SessionLocal
from app.models.crawler import StockData
from datetime import datetime, timedelta
import pandas as pd

def test_stock_data_storage():
    """测试股票数据爬取和存储"""
    print("开始测试股票数据爬取和存储...")
    
    # 1. 爬取数据
    print("\n1. 开始爬取股票数据...")
    crawler = StockCrawler()
    symbols = ["AAPL"]  # 使用苹果股票进行测试
    success = crawler.crawl_stock_data(symbols, period="1d")  # 只获取最近一天的数据
    
    if not success:
        print("❌ 爬取数据失败")
        return
    print("✅ 爬取数据成功")
        
    # 2. 验证数据存储
    print("\n2. 验证数据存储...")
    db = SessionLocal()
    try:
        # 获取今天的数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        # 查询数据库
        stored_data = db.query(StockData).filter(
            StockData.symbol == "AAPL",
            StockData.date >= start_date,
            StockData.date <= end_date
        ).all()
        
        if not stored_data:
            print("❌ 未找到存储的数据")
            return
            
        # 将数据转换为DataFrame以便更好地显示
        data_list = []
        for record in stored_data:
            data_list.append({
                "日期": record.date,
                "开盘价": record.open_price,
                "最高价": record.high_price,
                "最低价": record.low_price,
                "收盘价": record.close_price,
                "成交量": record.volume
            })
        
        df = pd.DataFrame(data_list)
        print("\n✅ 数据存储成功！数据概览：")
        print("\n", df.to_string(index=False))
            
    except Exception as e:
        print(f"❌ 查询数据时出错: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_stock_data_storage() 