import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import requests
from sqlalchemy.orm import Session
from app.crawlers.base import BaseCrawler
from app.models.crawler import News
from config.dev import settings

logger = logging.getLogger(__name__)

class NewsCrawler(BaseCrawler):
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_news(self, symbol: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取新闻数据
        :param symbol: 股票代码
        :param days: 获取最近几天的新闻
        :return: 新闻数据列表
        """
        try:
            params = {
                "function": "NEWS_SENTIMENT",
                "tickers": symbol,
                "apikey": self.api_key,
                "limit": 50  # 限制返回的新闻数量
            }
            
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if "feed" not in data:
                logger.warning(f"未找到股票 {symbol} 的新闻数据")
                return []

            # 过滤最近几天的新闻
            cutoff_date = datetime.now() - timedelta(days=days)
            news_list = []
            
            for item in data["feed"]:
                time_published = datetime.strptime(item["time_published"], "%Y%m%dT%H%M%S")
                if time_published >= cutoff_date:
                    news_list.append(item)
            
            return news_list

        except Exception as e:
            logger.error(f"获取股票 {symbol} 的新闻数据时出错: {str(e)}")
            return []

    def save_news(self, news_data: Dict[str, Any]) -> bool:
        """
        保存新闻到数据库
        :param news_data: 新闻数据
        :return: 是否保存成功
        """
        try:
            # 生成内容哈希
            content = news_data.get("summary", "")
            content_hash = self.generate_hash(content)
            
            # 检查是否已存在
            if self.is_duplicate(content_hash, News):
                return False
            
            # 创建新闻对象
            news = News(
                title=news_data.get("title", ""),
                content=content,
                source=news_data.get("source", ""),
                url=news_data.get("url", ""),
                content_hash=content_hash,
                published_date=datetime.strptime(news_data["time_published"], "%Y%m%dT%H%M%S")
            )
            
            # 保存到数据库
            self.db.add(news)
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"保存新闻时出错: {str(e)}")
            self.db.rollback()
            return False

    def crawl_news(self, symbol: str, days: int = 7) -> bool:
        """
        爬取并保存新闻
        :param symbol: 股票代码
        :param days: 获取最近几天的新闻
        :return: 是否成功
        """
        try:
            logger.info(f"开始爬取股票 {symbol} 的新闻...")
            news_list = self.fetch_news(symbol, days)
            
            if not news_list:
                logger.warning(f"未找到股票 {symbol} 的新闻")
                return True
            
            saved_count = 0
            for news_data in news_list:
                if self.save_news(news_data):
                    saved_count += 1
            
            logger.info(f"成功保存 {saved_count} 条新闻")
            return True
            
        except Exception as e:
            logger.error(f"爬取股票 {symbol} 的新闻时出错: {str(e)}")
            return False 