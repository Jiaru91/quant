from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class StockData(Base):
    __tablename__ = "stock_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    date = Column(DateTime, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class FinancialReport(Base):
    __tablename__ = "financial_reports"

    id = Column(Integer, primary_key=True, index=True)
    company_symbol = Column(String, index=True)
    report_type = Column(String)  # 年报、季报等
    report_date = Column(DateTime)
    title = Column(String)
    content = Column(Text)
    content_hash = Column(String, unique=True)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    source = Column(String)
    url = Column(String, unique=True)
    content_hash = Column(String, unique=True)
    published_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_analyzed = Column(Boolean, default=False) 