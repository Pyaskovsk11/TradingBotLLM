"""Candle model module."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, Index
from app.models.base import Base


class Candle(Base):
    """Model for storing candlestick data."""

    __tablename__ = "candles"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    interval = Column(String, nullable=False)  # '5m', '15m', etc.
    timestamp = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    number_of_trades = Column(Integer, nullable=False)
    taker_buy_volume = Column(Float, nullable=False)
    taker_buy_quote_volume = Column(Float, nullable=False)

    # Create indexes for faster queries
    __table_args__ = (
        Index('idx_symbol_interval_timestamp', 'symbol', 'interval', 'timestamp'),
    )

    def __repr__(self) -> str:
        """String representation of the candle."""
        return f"<Candle {self.symbol} {self.interval} {self.timestamp}>" 