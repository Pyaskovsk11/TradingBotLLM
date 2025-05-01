"""Binance service module."""
from typing import Optional, List
from datetime import datetime
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException

from app.config import get_settings
from app.models.candle import Candle
from app.models.order import Order
from app.models.signal import Signal
from app.models.level import Level

settings = get_settings()


class BinanceService:
    """Binance service class."""
    
    def __init__(self):
        """Initialize Binance service."""
        self.client = Client(
            api_key=settings.BINANCE_API_KEY,
            api_secret=settings.BINANCE_API_SECRET,
            testnet=settings.TRADING_MODE == "test"
        )
        
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Candle]:
        """Get klines.
        
        Args:
            symbol: Symbol
            interval: Interval
            start_time: Start time
            end_time: End time
            limit: Limit
            
        Returns:
            List[Candle]: List of candles
        """
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                startTime=int(start_time.timestamp() * 1000) if start_time else None,
                endTime=int(end_time.timestamp() * 1000) if end_time else None,
                limit=limit
            )
            return [
                Candle(
                    symbol=symbol,
                    interval=interval,
                    timestamp=datetime.fromtimestamp(k[0] / 1000),
                    open_price=float(k[1]),
                    high_price=float(k[2]),
                    low_price=float(k[3]),
                    close_price=float(k[4]),
                    volume=float(k[5]),
                    number_of_trades=int(k[8]),
                    taker_buy_volume=float(k[9]),
                    taker_buy_quote_volume=float(k[10])
                )
                for k in klines
            ]
        except BinanceAPIException as e:
            print(f"Error getting klines: {e}")
            return []
