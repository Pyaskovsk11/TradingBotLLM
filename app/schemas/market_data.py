"""Market data schemas module."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Candle(BaseModel):
    """Candlestick data model."""
    
    symbol: str = Field(..., description="Trading pair symbol")
    interval: str = Field(..., description="Candlestick interval")
    open_time: datetime = Field(..., description="Candle open time")
    open_price: float = Field(..., description="Open price")
    high_price: float = Field(..., description="High price")
    low_price: float = Field(..., description="Low price")
    close_price: float = Field(..., description="Close price")
    volume: float = Field(..., description="Trading volume")
    close_time: datetime = Field(..., description="Candle close time")
    quote_volume: float = Field(..., description="Quote asset volume")
    trades: int = Field(..., description="Number of trades")
    taker_buy_volume: float = Field(..., description="Taker buy base asset volume")
    taker_buy_quote_volume: float = Field(..., description="Taker buy quote asset volume")


class OrderBookLevel(BaseModel):
    """Order book price level model."""
    
    price: float = Field(..., description="Price level")
    quantity: float = Field(..., description="Quantity at price level")


class OrderBook(BaseModel):
    """Order book model."""
    
    symbol: str = Field(..., description="Trading pair symbol")
    bids: List[OrderBookLevel] = Field(..., description="List of bid orders")
    asks: List[OrderBookLevel] = Field(..., description="List of ask orders")
    timestamp: datetime = Field(..., description="Order book snapshot time")


class Trade(BaseModel):
    """Trade model."""
    
    symbol: str = Field(..., description="Trading pair symbol")
    id: int = Field(..., description="Trade ID")
    price: float = Field(..., description="Trade price")
    quantity: float = Field(..., description="Trade quantity")
    quote_quantity: float = Field(..., description="Quote asset quantity")
    time: datetime = Field(..., description="Trade time")
    is_buyer_maker: bool = Field(..., description="True if buyer is maker")
    is_best_match: bool = Field(..., description="True if trade is best price match")


class Ticker(BaseModel):
    """24-hour ticker model."""
    
    symbol: str = Field(..., description="Trading pair symbol")
    price_change: float = Field(..., description="Price change")
    price_change_percent: float = Field(..., description="Price change percent")
    weighted_avg_price: float = Field(..., description="Weighted average price")
    prev_close_price: float = Field(..., description="Previous day's close price")
    last_price: float = Field(..., description="Latest price")
    last_quantity: float = Field(..., description="Latest quantity")
    bid_price: float = Field(..., description="Best bid price")
    ask_price: float = Field(..., description="Best ask price")
    open_price: float = Field(..., description="Open price")
    high_price: float = Field(..., description="High price")
    low_price: float = Field(..., description="Low price")
    volume: float = Field(..., description="Total volume")
    quote_volume: float = Field(..., description="Total quote asset volume")
    open_time: datetime = Field(..., description="Open time")
    close_time: datetime = Field(..., description="Close time")
    first_id: int = Field(..., description="First trade ID")
    last_id: int = Field(..., description="Last trade ID")
    count: int = Field(..., description="Total number of trades") 