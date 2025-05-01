from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.schemas.position import PositionType, PositionStatus


class Position(Base):
    """Position model for tracking open positions."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    type = Column(Enum(PositionType), nullable=False)  # LONG или SHORT
    status = Column(Enum(PositionStatus), nullable=False, default=PositionStatus.OPEN)
    
    # Параметры позиции
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
    leverage = Column(Float, nullable=False)
    
    # Управление рисками
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    trailing_stop = Column(Float, nullable=True)
    
    # P&L
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    
    # Временные метки
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Связи
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    
    strategy = relationship("Strategy", back_populates="positions")
    portfolio = relationship("Portfolio", back_populates="positions")
    trades = relationship("Trade", back_populates="position")

    def __repr__(self) -> str:
        return f"<Position {self.symbol} {self.type} {self.quantity}@{self.entry_price}>" 