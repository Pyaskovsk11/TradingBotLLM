"""Base exchange interface module."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseExchange(ABC):
    """Abstract base class for cryptocurrency exchanges."""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize exchange client.
        
        Args:
            api_key: API key for authenticated requests
            api_secret: API secret for authenticated requests
        """
        self.api_key = api_key
        self.api_secret = api_secret

    @abstractmethod
    async def get_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get candlestick data from exchange.
        
        Args:
            symbol: Trading pair symbol
            interval: Candlestick interval
            limit: Number of candles to get
            start_time: Start time for historical data
            end_time: End time for historical data
            
        Returns:
            List of candlestick data
        """
        pass

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker data.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current price and 24h statistics
        """
        pass

    @abstractmethod
    async def get_order_book(
        self,
        symbol: str,
        limit: int = 100
    ) -> Dict[str, List[List[float]]]:
        """Get current order book.
        
        Args:
            symbol: Trading pair symbol
            limit: Depth of the order book
            
        Returns:
            Order book with bids and asks
        """
        pass

    @abstractmethod
    async def get_recent_trades(
        self,
        symbol: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent trades.
        
        Args:
            symbol: Trading pair symbol
            limit: Number of trades to get
            
        Returns:
            List of recent trades
        """
        pass

    @abstractmethod
    async def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information and trading rules.
        
        Returns:
            Exchange information including symbols, limits, etc.
        """
        pass 