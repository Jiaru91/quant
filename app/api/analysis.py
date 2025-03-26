from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.core.database import get_db
from app.services.llm_service import LLMService
from app.services.analysis_service import AnalysisService
from app.models.crawler import StockData, FinancialReport, News
from app.models.analysis import StockAnalysis
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
llm_service = LLMService()
analysis_service = AnalysisService()

class NaNJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and np.isnan(obj):
            return None
        if isinstance(obj, pd.DataFrame):
            return obj.replace({np.nan: None}).to_dict()
        if isinstance(obj, pd.Series):
            return obj.replace({np.nan: None}).to_dict()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def clean_nan_values(data: Any) -> Any:
    """清理数据中的NaN值"""
    if isinstance(data, (int, float)) and np.isnan(data):
        return None
    elif isinstance(data, dict):
        return {k: clean_nan_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_nan_values(item) for item in data]
    elif isinstance(data, pd.DataFrame):
        return data.replace({np.nan: None}).to_dict()
    elif isinstance(data, pd.Series):
        return data.replace({np.nan: None}).to_dict()
    elif isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, datetime):
        return data.isoformat()
    return data

@router.get("/stock/{symbol}")
def analyze_stock(
    symbol: str,
    days: Optional[int] = 60,
    db: Session = Depends(get_db)
) -> Dict:
    """分析股票数据并返回结果"""
    try:
        # 获取历史数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stock_data = (
            db.query(StockData)
            .filter(
                StockData.symbol == symbol,
                StockData.date >= start_date,
                StockData.date <= end_date
            )
            .order_by(StockData.date.asc())
            .all()
        )
        
        if not stock_data:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票 {symbol} 的历史数据"
            )
            
        # 转换为DataFrame
        df = pd.DataFrame([
            {
                'date': data.date,
                'open': data.open,
                'high': data.high,
                'low': data.low,
                'close': data.close,
                'volume': data.volume
            }
            for data in stock_data
        ])
        df.set_index('date', inplace=True)
        
        # 执行分析
        analysis_results = analysis_service.analyze_stock_data(df)
        
        # 保存分析结果
        saved_analysis = analysis_service.save_analysis_results(
            db, symbol, analysis_results
        )
        
        if not saved_analysis:
            logger.warning(f"分析结果保存失败: {symbol}")
            
        return analysis_results
        
    except Exception as e:
        logger.error(f"分析股票数据时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"分析过程中发生错误: {str(e)}"
        )
        
@router.get("/stock/{symbol}/history")
def get_analysis_history(
    symbol: str,
    days: Optional[int] = 30,
    db: Session = Depends(get_db)
) -> List[Dict]:
    """获取股票分析历史记录"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        analysis_history = (
            db.query(StockAnalysis)
            .filter(
                StockAnalysis.symbol == symbol,
                StockAnalysis.analysis_date >= start_date,
                StockAnalysis.analysis_date <= end_date
            )
            .order_by(StockAnalysis.analysis_date.desc())
            .all()
        )
        
        if not analysis_history:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票 {symbol} 的分析历史记录"
            )
            
        return [
            {
                'symbol': record.symbol,
                'analysis_date': record.analysis_date,
                'ma_5': record.ma_5,
                'ma_10': record.ma_10,
                'ma_20': record.ma_20,
                'rsi_14': record.rsi_14,
                'macd': record.macd,
                'macd_signal': record.macd_signal,
                'macd_hist': record.macd_hist,
                'bollinger_upper': record.bollinger_upper,
                'bollinger_middle': record.bollinger_middle,
                'bollinger_lower': record.bollinger_lower,
                'volatility': record.volatility,
                'atr': record.atr,
                'trend': record.trend,
                'trend_strength': record.trend_strength,
                'support_levels': record.support_levels,
                'resistance_levels': record.resistance_levels,
                'technical_score': record.technical_score,
                'risk_level': record.risk_level,
                'trading_suggestion': record.trading_suggestion
            }
            for record in analysis_history
        ]
        
    except Exception as e:
        logger.error(f"获取分析历史记录时发生错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取分析历史记录时发生错误: {str(e)}"
        )

@router.get("/financial/{symbol}")
async def analyze_financial_report(
    symbol: str,
    report_type: str = "10-K",
    db: Session = Depends(get_db)
):
    """分析财务报表"""
    try:
        # 获取财务报表
        reports = db.query(FinancialReport).filter(
            FinancialReport.company_symbol == symbol,
            FinancialReport.report_type == report_type
        ).order_by(FinancialReport.report_date.desc()).limit(4).all()
        
        if not reports:
            raise HTTPException(status_code=404, detail="未找到财务报表数据")
        
        # 分析每份报表
        analyses = []
        for report in reports:
            analysis = await llm_service.analyze_financial_report({
                'content': report.content,
                'report_type': report.report_type,
                'report_date': report.report_date
            })
            analyses.append(analysis)
        
        # 解决可能的冲突
        if len(analyses) > 1:
            resolution = await llm_service.resolve_conflicts(analyses)
        else:
            resolution = analyses[0]
        
        # 清理NaN值
        result = {
            "symbol": symbol,
            "report_type": report_type,
            "analyses": clean_nan_values(analyses),
            "resolution": clean_nan_values(resolution)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"分析财务报表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news/{symbol}")
async def analyze_news(
    symbol: str,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """分析新闻数据"""
    try:
        # 获取新闻
        news = db.query(News).filter(
            News.content.like(f"%{symbol}%"),
            News.published_date >= datetime.now() - timedelta(days=days)
        ).order_by(News.published_date.desc()).all()
        
        if not news:
            raise HTTPException(status_code=404, detail="未找到新闻数据")
        
        # 分析新闻
        analysis = await llm_service.analyze_news([{
            'title': n.title,
            'content': n.content,
            'source': n.source,
            'published_date': n.published_date
        } for n in news])
        
        # 清理NaN值
        result = {
            "symbol": symbol,
            "news_count": len(news),
            "analysis": clean_nan_values(analysis)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"分析新闻数据时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 