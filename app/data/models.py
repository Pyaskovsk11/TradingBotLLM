from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    base_asset = Column(String)
    quote_asset = Column(String)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    candlesticks = relationship("Candlestick", back_populates="symbol")

class Candlestick(Base):
    __tablename__ = "candlesticks"

    id = Column(Integer, primary_key=True, index=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"))
    open_time = Column(DateTime, index=True)
    close_time = Column(DateTime)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)
    quote_volume = Column(Float)
    trades = Column(Integer)
    taker_buy_base_volume = Column(Float)
    taker_buy_quote_volume = Column(Float)
    interval = Column(String)  # e.g., "1m", "5m", "1h", "1d"
    created_at = Column(DateTime, default=datetime.utcnow)

    symbol = relationship("Symbol", back_populates="candlesticks") 