from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class StockAnalysis(Base):
    """股票分析结果表"""
    __tablename__ = "stock_analysis"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    analysis_date = Column(DateTime, default=datetime.now)
    
    # 技术分析指标
    ma_5 = Column(Float)  # 5日移动平均
    ma_10 = Column(Float)  # 10日移动平均
    ma_20 = Column(Float)  # 20日移动平均
    rsi_14 = Column(Float)  # 14日RSI
    macd = Column(Float)  # MACD
    macd_signal = Column(Float)  # MACD信号线
    macd_hist = Column(Float)  # MACD柱状图
    bollinger_upper = Column(Float)  # 布林带上轨
    bollinger_middle = Column(Float)  # 布林带中轨
    bollinger_lower = Column(Float)  # 布林带下轨
    
    # 波动率指标
    volatility = Column(Float)  # 波动率
    atr = Column(Float)  # 平均真实范围
    
    # 趋势指标
    trend = Column(String)  # 趋势方向(上升/下降/横盘)
    trend_strength = Column(Float)  # 趋势强度
    
    # 支撑/阻力位
    support_levels = Column(JSON)  # 支撑位列表
    resistance_levels = Column(JSON)  # 阻力位列表
    
    # 预测结果
    price_prediction = Column(Float)  # 价格预测
    prediction_interval = Column(JSON)  # 预测区间
    confidence_score = Column(Float)  # 预测置信度
    
    # 综合分析
    technical_score = Column(Float)  # 技术面评分
    risk_level = Column(String)  # 风险水平
    trading_suggestion = Column(String)  # 交易建议
    analysis_summary = Column(String)  # 分析总结

class NewsAnalysis(Base):
    """新闻分析结果表"""
    __tablename__ = "news_analysis"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    analysis_date = Column(DateTime, default=datetime.now)
    
    # 情感分析
    sentiment_score = Column(Float)  # 情感得分
    sentiment_label = Column(String)  # 情感标签(积极/消极/中性)
    
    # 主题分析
    topics = Column(JSON)  # 主要话题
    key_entities = Column(JSON)  # 关键实体
    
    # 影响分析
    market_impact = Column(String)  # 市场影响
    impact_score = Column(Float)  # 影响程度
    
    # 综合分析
    news_summary = Column(String)  # 新闻摘要
    analysis_summary = Column(String)  # 分析总结

class FinancialAnalysis(Base):
    """财务分析结果表"""
    __tablename__ = "financial_analysis"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    analysis_date = Column(DateTime, default=datetime.now)
    report_type = Column(String)  # 报表类型(10-K/10-Q)
    
    # 财务指标
    revenue_growth = Column(Float)  # 收入增长率
    profit_margin = Column(Float)  # 利润率
    eps = Column(Float)  # 每股收益
    pe_ratio = Column(Float)  # 市盈率
    debt_ratio = Column(Float)  # 负债率
    current_ratio = Column(Float)  # 流动比率
    
    # 财务健康度
    financial_health_score = Column(Float)  # 财务健康评分
    risk_assessment = Column(String)  # 风险评估
    
    # 综合分析
    strength_factors = Column(JSON)  # 优势因素
    weakness_factors = Column(JSON)  # 劣势因素
    analysis_summary = Column(String)  # 分析总结 