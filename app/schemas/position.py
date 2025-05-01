from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PositionType(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    LIQUIDATED = "LIQUIDATED"


class PositionBase(BaseModel):
    symbol: str
    type: PositionType
    status: PositionStatus
    entry_price: float
    current_price: float
    quantity: float
    leverage: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop: Optional[float] = None
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0


class PositionCreate(PositionBase):
    strategy_id: int
    portfolio_id: int


class PositionUpdate(PositionBase):
    pass


class PositionInDB(PositionBase):
    id: int
    strategy_id: int
    portfolio_id: int
    opened_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True 