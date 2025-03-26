import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
import logging
from app.core.database import SessionLocal
from app.models.crawler import StockData
import time
import json
import requests
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)

class StockCrawler:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.session = requests.Session()
        retries = Retry(total=5,
                       backoff_factor=0.1,
                       status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
    def _get_stock_data(self, symbol: str, period: str = "1d", retry_count: int = 0) -> Optional[pd.DataFrame]:
        """获取股票数据，带重试机制"""
        try:
            logger.info(f"开始获取股票 {symbol} 的数据...")
            
            # 添加重试逻辑
            for attempt in range(self.max_retries):
                try:
                    # 使用session进行请求
                    stock = yf.Ticker(symbol, session=self.session)
                    data = stock.history(period=period)
                    
                    if not data.empty:
                        # 检查数据是否有效
                        if data.isnull().any().any():
                            logger.warning(f"股票 {symbol} 的数据包含空值")
                            data = data.fillna(method='ffill').fillna(method='bfill')
                            
                        # 验证数据的有效性
                        if len(data) > 0 and all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
                            return data
                            
                        logger.warning(f"股票 {symbol} 的数据格式不完整")
                    else:
                        logger.warning(f"第 {attempt + 1} 次尝试获取 {symbol} 数据为空")
                        
                    time.sleep(self.retry_delay * (attempt + 1))
                    
                except Exception as e:
                    logger.warning(f"第 {attempt + 1} 次尝试获取 {symbol} 数据失败: {str(e)}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                    continue
            
            # 尝试使用备用数据源
            try:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                backup_data = yf.download(symbol, 
                                        start=start_date.strftime('%Y-%m-%d'),
                                        end=end_date.strftime('%Y-%m-%d'),
                                        progress=False)
                if not backup_data.empty:
                    logger.info(f"使用备用数据源获取 {symbol} 的数据成功")
                    return backup_data
            except Exception as e:
                logger.error(f"备用数据源获取 {symbol} 的数据失败: {str(e)}")
            
            logger.error(f"获取股票 {symbol} 的数据失败")
            return None
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 的数据时发生错误: {str(e)}")
            return None

    def crawl_stock_data(self, symbols: List[str], period: str = "1d") -> bool:
        """爬取多个股票的数据"""
        success = True
        db = SessionLocal()
        
        try:
            for symbol in symbols:
                try:
                    data = self._get_stock_data(symbol, period)
                    if data is not None and not data.empty:
                        # 保存数据到数据库
                        for index, row in data.iterrows():
                            try:
                                # 确保数据类型正确
                                stock_data = StockData(
                                    symbol=symbol,
                                    date=index,
                                    open_price=float(row['Open']),
                                    high_price=float(row['High']),
                                    low_price=float(row['Low']),
                                    close_price=float(row['Close']),
                                    volume=int(row['Volume'])
                                )
                                db.add(stock_data)
                            except (ValueError, TypeError) as e:
                                logger.error(f"处理股票 {symbol} 在 {index} 的数据时发生错误: {str(e)}")
                                continue
                                
                        try:
                            db.commit()
                            logger.info(f"成功保存股票 {symbol} 的数据")
                        except Exception as e:
                            logger.error(f"保存股票 {symbol} 数据到数据库时发生错误: {str(e)}")
                            db.rollback()
                            success = False
                    else:
                        logger.warning(f"未找到股票 {symbol} 的数据")
                        success = False
                        
                except Exception as e:
                    logger.error(f"处理股票 {symbol} 数据时发生错误: {str(e)}")
                    success = False
                    continue
                    
        except Exception as e:
            logger.error(f"爬取股票数据时发生错误: {str(e)}")
            success = False
        finally:
            db.close()
            
        return success 