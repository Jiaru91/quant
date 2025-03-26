from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.services.llm_service import LLMService
from app.services.analysis_service import AnalysisService
from app.models.crawler import StockData, FinancialReport, News
from datetime import datetime, timedelta
import pandas as pd

router = APIRouter()
llm_service = LLMService()
analysis_service = AnalysisService()

@router.get("/stock/{symbol}")
async def predict_stock(
    symbol: str,
    days: int = 30,
    prediction_horizon: str = "short",  # short, medium, long
    db: Session = Depends(get_db)
):
    """预测股票走势"""
    try:
        # 获取历史数据
        stock_data = db.query(StockData).filter(
            StockData.symbol == symbol,
            StockData.date >= datetime.now() - timedelta(days=days)
        ).all()
        
        if not stock_data:
            raise HTTPException(status_code=404, detail="未找到股票数据")
        
        # 转换为DataFrame
        df = pd.DataFrame([{
            'date': data.date,
            'open': data.open,
            'high': data.high,
            'low': data.low,
            'close': data.close,
            'volume': data.volume
        } for data in stock_data])
        
        # 计算技术指标
        technical_indicators = analysis_service.analyze_technical_indicators(df)
        
        # 获取最新财务报表
        financial_report = db.query(FinancialReport).filter(
            FinancialReport.company_symbol == symbol
        ).order_by(FinancialReport.report_date.desc()).first()
        
        # 获取最新新闻
        news = db.query(News).filter(
            News.content.like(f"%{symbol}%")
        ).order_by(News.published_date.desc()).limit(5).all()
        
        # 分析新闻
        news_analysis = await llm_service.analyze_news([{
            'title': n.title,
            'content': n.content,
            'source': n.source,
            'published_date': n.published_date
        } for n in news])
        
        # 分析财务报表
        if financial_report:
            financial_analysis = await llm_service.analyze_financial_report({
                'content': financial_report.content,
                'report_type': financial_report.report_type,
                'report_date': financial_report.report_date
            })
        else:
            financial_analysis = {"error": "未找到财务报表数据"}
        
        # 预测股价
        prediction = await llm_service.predict_stock_price(
            technical_data=technical_indicators,
            fundamental_data=financial_analysis,
            news_analysis=news_analysis
        )
        
        # 计算波动率
        volatility = analysis_service.calculate_volatility(df['close'])
        
        # 检测异常值
        anomalies = analysis_service.detect_anomalies(df[['close', 'volume']])
        
        return {
            "symbol": symbol,
            "prediction": prediction,
            "volatility": volatility.iloc[-1] if not volatility.empty else None,
            "anomalies": len(anomalies),
            "confidence_score": prediction.get("confidence_score", 0.0),
            "technical_indicators": technical_indicators,
            "fundamental_analysis": financial_analysis,
            "news_sentiment": news_analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trend/{symbol}")
async def predict_trend(
    symbol: str,
    timeframe: str = "weekly",  # weekly, monthly, quarterly
    db: Session = Depends(get_db)
):
    """预测市场趋势"""
    try:
        # 根据时间框架确定历史数据范围
        days_map = {
            "weekly": 30,
            "monthly": 90,
            "quarterly": 180
        }
        days = days_map.get(timeframe, 30)
        
        # 获取历史数据
        stock_data = db.query(StockData).filter(
            StockData.symbol == symbol,
            StockData.date >= datetime.now() - timedelta(days=days)
        ).all()
        
        if not stock_data:
            raise HTTPException(status_code=404, detail="未找到股票数据")
        
        # 转换为DataFrame
        df = pd.DataFrame([{
            'date': data.date,
            'close': data.close,
            'volume': data.volume
        } for data in stock_data])
        
        # 计算趋势指标
        ma_20 = df['close'].rolling(window=20).mean()
        ma_50 = df['close'].rolling(window=50).mean()
        
        # 判断趋势
        current_price = df['close'].iloc[-1]
        trend = "上升" if current_price > ma_20.iloc[-1] > ma_50.iloc[-1] else \
                "下降" if current_price < ma_20.iloc[-1] < ma_50.iloc[-1] else \
                "震荡"
        
        # 计算趋势强度
        trend_strength = abs(ma_20.iloc[-1] - ma_50.iloc[-1]) / ma_50.iloc[-1]
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "trend": trend,
            "trend_strength": float(trend_strength),
            "current_price": float(current_price),
            "ma_20": float(ma_20.iloc[-1]),
            "ma_50": float(ma_50.iloc[-1])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/{symbol}")
async def analyze_market_sentiment(
    symbol: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """分析市场情绪"""
    try:
        # 获取新闻数据
        news = db.query(News).filter(
            News.content.like(f"%{symbol}%"),
            News.published_date >= datetime.now() - timedelta(days=days)
        ).order_by(News.published_date.desc()).all()
        
        if not news:
            raise HTTPException(status_code=404, detail="未找到新闻数据")
        
        # 分析新闻情绪
        sentiment_analysis = await llm_service.analyze_news([{
            'title': n.title,
            'content': n.content,
            'source': n.source,
            'published_date': n.published_date
        } for n in news])
        
        # 获取股票数据
        stock_data = db.query(StockData).filter(
            StockData.symbol == symbol,
            StockData.date >= datetime.now() - timedelta(days=days)
        ).all()
        
        if stock_data:
            # 转换为DataFrame
            df = pd.DataFrame([{
                'date': data.date,
                'close': data.close,
                'volume': data.volume
            } for data in stock_data])
            
            # 计算波动率
            volatility = analysis_service.calculate_volatility(df['close'])
            
            # 计算成交量变化
            volume_change = df['volume'].pct_change()
            
            market_data = {
                "volatility": float(volatility.iloc[-1]) if not volatility.empty else None,
                "volume_change": float(volume_change.iloc[-1]) if not volume_change.empty else None
            }
        else:
            market_data = {}
        
        return {
            "symbol": symbol,
            "sentiment_analysis": sentiment_analysis,
            "market_data": market_data,
            "news_count": len(news)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 