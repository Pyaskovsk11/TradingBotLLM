"""Level model module."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, Enum, Index, Boolean
from app.models.base import Base
import enum


class LevelType(str, enum.Enum):
    """Enum for level types."""
    SUPPORT = "support"
    RESISTANCE = "resistance"


class Level(Base):
    """Model for storing key price levels."""

    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    type = Column(Enum(LevelType), nullable=False)
    strength = Column(Float, nullable=False)  # 0-1 scale
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_tested = Column(DateTime)
    is_active = Column(Boolean, default=True)
    confidence = Column(Float, nullable=False)  # 0-1 scale
    volume_confirmation = Column(Float)  # Volume at this level
    number_of_tests = Column(Integer, default=0)
    
    # Create indexes for faster queries
    __table_args__ = (
        Index('idx_symbol_price', 'symbol', 'price'),
        Index('idx_active_levels', 'symbol', 'is_active'),
    )

    def __repr__(self) -> str:
        """String representation of the level."""
        return f"<Level {self.symbol} {self.type} {self.price}>" 