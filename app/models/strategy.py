from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.models.base import Base


class Strategy(Base):
    """Strategy model for storing trading strategies."""
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    symbol = Column(String, nullable=False)  # Торговая пара
    timeframe = Column(String, nullable=False)  # Таймфрейм (1m, 5m, 15m, 1h, 4h, 1d)
    
    # Параметры стратегии
    leverage = Column(Float, default=5.0)  # Максимальное плечо
    max_position_size = Column(Float, default=0.1)  # Максимальный размер позиции от депозита
    stop_loss = Column(Float, default=0.02)  # Стоп-лосс в процентах
    take_profit = Column(Float, default=0.04)  # Тейк-профит в процентах
    trailing_stop = Column(Float, default=0.01)  # Трейлинг-стоп в процентах
    
    # Дополнительные параметры
    parameters = Column(JSON, nullable=True)  # Дополнительные параметры в JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Связи
    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")
    positions = relationship("Position", back_populates="strategy")

    def __repr__(self) -> str:
        return f"<Strategy {self.name} ({self.symbol})>" 