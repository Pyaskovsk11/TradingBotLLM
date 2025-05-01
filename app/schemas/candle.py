"""Candle schemas."""
from datetime import datetime
from pydantic import BaseModel


class Candle(BaseModel):
    """Candle schema."""
    
    symbol: str
    interval: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    number_of_trades: int
    taker_buy_volume: float
    taker_buy_quote_volume: float
