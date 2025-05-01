"""Binance exchange implementation module."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import aiohttp
from .base import BaseExchange


class BinanceExchange(BaseExchange):
    """Binance exchange API implementation."""

    BASE_URL = "https://api.binance.com"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize Binance client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        super().__init__(api_key, api_secret)
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        """Async context manager enter."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.session.close()

    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make GET request to Binance API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        async with self.session.get(f"{self.BASE_URL}{endpoint}", params=params) as response:
            response.raise_for_status()
            return await response.json()

    async def get_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get candlestick data from Binance.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            interval: Candlestick interval (e.g. '1m', '5m', '1h', '1d')
            limit: Number of candles to get (max 1000)
            start_time: Start time for historical data
            end_time: End time for historical data
            
        Returns:
            List of candlestick data with keys:
            - open_time: Candle open time
            - open: Open price
            - high: High price
            - low: Low price
            - close: Close price
            - volume: Volume
            - close_time: Candle close time
            - quote_volume: Quote asset volume
            - trades: Number of trades
            - taker_buy_volume: Taker buy base asset volume
            - taker_buy_quote_volume: Taker buy quote asset volume
        """
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": min(limit, 1000)
        }
        
        if start_time:
            params["startTime"] = int(start_time.timestamp() * 1000)
        if end_time:
            params["endTime"] = int(end_time.timestamp() * 1000)

        data = await self._get("/api/v3/klines", params)
        
        return [
            {
                "open_time": datetime.fromtimestamp(candle[0] / 1000),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5]),
                "close_time": datetime.fromtimestamp(candle[6] / 1000),
                "quote_volume": float(candle[7]),
                "trades": int(candle[8]),
                "taker_buy_volume": float(candle[9]),
                "taker_buy_quote_volume": float(candle[10])
            }
            for candle in data
        ]

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current 24hr ticker data from Binance.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            
        Returns:
            Current price and 24h statistics
        """
        return await self._get("/api/v3/ticker/24hr", {"symbol": symbol.upper()})

    async def get_order_book(
        self,
        symbol: str,
        limit: int = 100
    ) -> Dict[str, List[List[float]]]:
        """Get current order book from Binance.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            limit: Depth of the order book (max 5000)
            
        Returns:
            Order book with bids and asks
        """
        data = await self._get(
            "/api/v3/depth",
            {
                "symbol": symbol.upper(),
                "limit": min(limit, 5000)
            }
        )
        
        return {
            "bids": [[float(price), float(qty)] for price, qty in data["bids"]],
            "asks": [[float(price), float(qty)] for price, qty in data["asks"]]
        }

    async def get_recent_trades(
        self,
        symbol: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent trades from Binance.
        
        Args:
            symbol: Trading pair symbol (e.g. 'BTCUSDT')
            limit: Number of trades to get (max 1000)
            
        Returns:
            List of recent trades
        """
        return await self._get(
            "/api/v3/trades",
            {
                "symbol": symbol.upper(),
                "limit": min(limit, 1000)
            }
        )

    async def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information and trading rules from Binance.
        
        Returns:
            Exchange information including symbols, limits, etc.
        """
        return await self._get("/api/v3/exchangeInfo") 