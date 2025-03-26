import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.logging_config import logger
from app.crawlers.base import BaseCrawler
from app.models.crawler import StockData
import time

class YahooFinanceCrawler(BaseCrawler):
    def __init__(self, db: Session):
        super().__init__(db)
        self.max_retries = 3
        self.retry_delay = 2  # 重试延迟（秒）

    def fetch_stock_data(self, symbol: str, period: str = "1y") -> Optional[List[StockData]]:
        """
        获取股票数据
        :param symbol: 股票代码
        :param period: 时间周期 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        :return: 股票数据列表
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"开始获取股票 {symbol} 的数据（第{attempt + 1}次尝试）...")
                stock = yf.Ticker(symbol)
                
                # 尝试获取股票信息以验证股票代码是否有效
                info = stock.info
                if not info:
                    logger.warning(f"股票代码 {symbol} 可能无效")
                    return None

                # 获取历史数据
                df = stock.history(period=period)
                
                if df.empty:
                    logger.warning(f"未找到股票 {symbol} 的数据，将在 {self.retry_delay} 秒后重试...")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return None

                stock_data_list = []
                for date, row in df.iterrows():
                    stock_data = StockData(
                        symbol=symbol,
                        date=date,
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        volume=int(row['Volume'])
                    )
                    stock_data_list.append(stock_data)

                logger.info(f"成功获取股票 {symbol} 的 {len(stock_data_list)} 条数据")
                return stock_data_list

            except Exception as e:
                logger.error(f"获取股票 {symbol} 数据时出错: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"将在 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"已达到最大重试次数 ({self.max_retries})，放弃获取股票 {symbol} 的数据")
                    return None

    def save_stock_data(self, stock_data_list: List[StockData]) -> bool:
        """
        保存股票数据到数据库
        :param stock_data_list: 股票数据列表
        :return: 是否保存成功
        """
        try:
            saved_count = 0
            for stock_data in stock_data_list:
                # 检查是否已存在相同日期的数据
                existing_data = self.db.query(StockData).filter(
                    StockData.symbol == stock_data.symbol,
                    StockData.date == stock_data.date
                ).first()

                if not existing_data:
                    self.db.add(stock_data)
                    saved_count += 1

            self.db.commit()
            logger.info(f"成功保存 {saved_count} 条新数据到数据库")
            return True
        except Exception as e:
            logger.error(f"保存股票数据时出错: {str(e)}")
            self.db.rollback()
            return False

    def crawl_stock_data(self, symbols: List[str], period: str = "1y") -> bool:
        """
        爬取并保存多个股票的数据
        :param symbols: 股票代码列表
        :param period: 时间周期
        :return: 是否成功
        """
        success = True
        for symbol in symbols:
            logger.info(f"开始爬取股票 {symbol} 的数据...")
            stock_data_list = self.fetch_stock_data(symbol, period)
            if stock_data_list:
                if not self.save_stock_data(stock_data_list):
                    success = False
                    logger.error(f"保存股票 {symbol} 的数据失败")
            else:
                success = False
                logger.error(f"获取股票 {symbol} 的数据失败")
        return success 