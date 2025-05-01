from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.schemas.trade import TradeType


class Trade(Base):
    """Trade model for storing trading operations."""
    
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    type = Column(Enum(TradeType), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)

    portfolio = relationship("Portfolio", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")

    # Composite index for common queries
    __table_args__ = (
        Index('ix_trades_portfolio_timestamp', 'portfolio_id', 'timestamp'),
    )

    def __repr__(self) -> str:
        return f"<Trade {self.symbol} {self.type} {self.quantity}@{self.price}>" 