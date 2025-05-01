from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TradeType(str, Enum):
    """Enum for trade types."""
    BUY = "buy"
    SELL = "sell"


class TradeBase(BaseModel):
    """Base trade schema."""
    symbol: str = Field(..., min_length=1, max_length=10)
    type: TradeType
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)


class TradeCreate(TradeBase):
    """Schema for creating a trade."""
    portfolio_id: int


class TradeUpdate(BaseModel):
    """Schema for updating a trade."""
    symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    type: Optional[TradeType] = None
    quantity: Optional[float] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)


class TradeInDB(TradeBase):
    """Schema for trade in database."""
    id: int
    timestamp: datetime
    portfolio_id: int

    class Config:
        from_attributes = True


class Trade(TradeInDB):
    """Schema for trade response."""
    pass 