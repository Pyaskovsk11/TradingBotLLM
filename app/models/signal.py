"""Signal models module."""
from datetime import datetime
from enum import Enum
from typing import Dict, Any
from sqlalchemy import Column, String, Float, DateTime, Boolean, JSON, Enum as SQLEnum

from app.database import Base


class SignalType(str, Enum):
    """Trading signal types."""
    
    LEVEL_BOUNCE = "level_bounce"  # Price bouncing from support/resistance
    TREND_CONTINUATION = "trend_continuation"  # Strong trend continuation
    MOMENTUM = "momentum"  # Momentum-based signals (oversold/overbought)
    VOLUME_SPIKE = "volume_spike"  # Significant volume increase


class SignalStrength(str, Enum):
    """Signal strength levels."""
    
    WEAK = "weak"  # Low confidence signal
    MEDIUM = "medium"  # Medium confidence signal
    STRONG = "strong"  # High confidence signal


class Signal(Base):
    """Trading signal model."""
    
    __tablename__ = "signals"

    id = Column(String, primary_key=True)
    symbol = Column(String, nullable=False, index=True)
    type = Column(SQLEnum(SignalType), nullable=False)
    strength = Column(SQLEnum(SignalStrength), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    indicators = Column(JSON, nullable=False)  # Technical indicators values
    description = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)  # Signal confidence score (0-1)
    is_valid = Column(Boolean, default=True)  # Whether signal is still valid
    
    def __init__(
        self,
        symbol: str,
        type: SignalType,
        strength: SignalStrength,
        price: float,
        timestamp: datetime,
        indicators: Dict[str, Any],
        description: str,
        confidence: float,
        is_valid: bool = True
    ):
        """Initialize signal.
        
        Args:
            symbol: Trading pair symbol
            type: Signal type
            strength: Signal strength
            price: Current price
            timestamp: Signal generation time
            indicators: Technical indicators values
            description: Signal description
            confidence: Signal confidence score (0-1)
            is_valid: Whether signal is still valid
        """
        self.id = f"{symbol}_{type}_{timestamp.timestamp()}"
        self.symbol = symbol
        self.type = type
        self.strength = strength
        self.price = price
        self.timestamp = timestamp
        self.indicators = indicators
        self.description = description
        self.confidence = confidence
        self.is_valid = is_valid

    def __repr__(self) -> str:
        """String representation of the signal."""
        return f"<Signal {self.symbol} {self.type} {self.strength}>" 