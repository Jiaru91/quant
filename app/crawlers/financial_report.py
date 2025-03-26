import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
import requests
from sqlalchemy.orm import Session

from app.crawlers.base import BaseCrawler
from app.models.crawler import FinancialReport
from config.dev import settings

logger = logging.getLogger(__name__)

class FinancialReportCrawler(BaseCrawler):
    def __init__(self, db: Session):
        super().__init__(db)
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"

    def fetch_financial_reports(self, symbol: str, report_type: str = "10-K") -> List[Dict[str, Any]]:
        """
        获取财务报表数据
        :param symbol: 股票代码
        :param report_type: 报告类型 (10-K: 年报, 10-Q: 季报)
        :return: 财务报表数据列表
        """
        try:
            # 根据报告类型选择不同的API函数
            function = "INCOME_STATEMENT"  # 默认获取利润表
            if report_type == "10-K":
                function = "INCOME_STATEMENT"  # 年度利润表
            elif report_type == "10-Q":
                function = "EARNINGS"  # 季度收益报告

            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            reports = []
            if function == "INCOME_STATEMENT" and "annualReports" in data:
                reports = data["annualReports"]
            elif function == "EARNINGS" and "quarterlyEarnings" in data:
                reports = data["quarterlyEarnings"]
            
            if not reports:
                logger.warning(f"未找到股票 {symbol} 的{report_type}报表数据")
                return []

            return reports

        except Exception as e:
            logger.error(f"获取股票 {symbol} 的财务报表数据时出错: {str(e)}")
            return []

    def save_financial_report(self, symbol: str, report_data: Dict[str, Any], report_type: str) -> bool:
        """
        保存财务报表到数据库
        :param symbol: 股票代码
        :param report_data: 报表数据
        :param report_type: 报告类型
        :return: 是否保存成功
        """
        try:
            # 生成报表内容
            content = str(report_data)
            content_hash = self.generate_hash(content)
            
            # 检查是否已存在
            if self.is_duplicate(content_hash, FinancialReport):
                return False
            
            # 获取报表日期
            if report_type == "10-K":
                report_date = datetime.strptime(report_data.get("fiscalDateEnding", ""), "%Y-%m-%d")
            else:
                report_date = datetime.strptime(report_data.get("fiscalDateEnding", ""), "%Y-%m-%d")
            
            # 创建报表对象
            report = FinancialReport(
                company_symbol=symbol,
                report_type=report_type,
                report_date=report_date,
                title=f"{symbol} {report_type} Report {report_date.strftime('%Y-%m-%d')}",
                content=content,
                content_hash=content_hash,
                url=self.base_url  # 使用API URL作为来源
            )
            
            # 保存到数据库
            self.db.add(report)
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"保存财务报表时出错: {str(e)}")
            self.db.rollback()
            return False

    def crawl_financial_reports(self, symbol: str, report_type: str = "10-K") -> bool:
        """
        爬取并保存财务报表
        :param symbol: 股票代码
        :param report_type: 报告类型 (10-K: 年报, 10-Q: 季报)
        :return: 是否成功
        """
        try:
            logger.info(f"开始爬取股票 {symbol} 的{report_type}报表...")
            reports = self.fetch_financial_reports(symbol, report_type)
            
            if not reports:
                logger.warning(f"未找到股票 {symbol} 的{report_type}报表")
                return True
            
            saved_count = 0
            for report_data in reports:
                if self.save_financial_report(symbol, report_data, report_type):
                    saved_count += 1
            
            logger.info(f"成功保存 {saved_count} 份{report_type}报表")
            return True
            
        except Exception as e:
            logger.error(f"爬取股票 {symbol} 的{report_type}报表时出错: {str(e)}")
            return False 