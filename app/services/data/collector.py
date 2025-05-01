"""Market data collector module."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.services.exchange.base import BaseExchange
from app.schemas.market_data import Candle, OrderBook, Trade, Ticker
from app.models.candle import Candle as CandleModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

logger = logging.getLogger(__name__)


class MarketDataCollector:
    """Service for collecting market data from exchange."""

    def __init__(
        self,
        exchange: BaseExchange,
        session: AsyncSession,
        symbols: List[str],
        intervals: List[str] = ["1m", "5m", "15m", "1h", "4h", "1d"]
    ):
        """Initialize market data collector.
        
        Args:
            exchange: Exchange API client
            session: Database session
            symbols: List of trading pairs to collect data for
            intervals: List of candlestick intervals to collect
        """
        self.exchange = exchange
        self.session = session
        self.symbols = [s.upper() for s in symbols]
        self.intervals = intervals
        self._running = False
        self._tasks = []

    async def start(self):
        """Start collecting market data."""
        if self._running:
            logger.warning("Market data collector is already running")
            return

        self._running = True
        self._tasks = [
            asyncio.create_task(self._collect_candles(symbol, interval))
            for symbol in self.symbols
            for interval in self.intervals
        ]
        
        logger.info(
            f"Started market data collection for {len(self.symbols)} symbols "
            f"and {len(self.intervals)} intervals"
        )

    async def stop(self):
        """Stop collecting market data."""
        if not self._running:
            return

        self._running = False
        for task in self._tasks:
            task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks = []
        
        logger.info("Stopped market data collection")

    async def _collect_candles(self, symbol: str, interval: str):
        """Collect candlestick data for a symbol and interval.
        
        Args:
            symbol: Trading pair symbol
            interval: Candlestick interval
        """
        while self._running:
            try:
                # Get last candle from database
                last_candle = await self._get_last_candle(symbol, interval)
                start_time = None
                
                if last_candle:
                    start_time = last_candle.timestamp + timedelta(seconds=1)

                # Get new candles from exchange
                candles = await self.exchange.get_candles(
                    symbol=symbol,
                    interval=interval,
                    start_time=start_time,
                    limit=1000
                )

                if not candles:
                    await asyncio.sleep(5)
                    continue

                # Convert to models and save to database
                db_candles = []
                for candle_data in candles:
                    candle = CandleModel(
                        symbol=symbol,
                        interval=interval,
                        timestamp=candle_data["open_time"],
                        open_price=candle_data["open"],
                        high_price=candle_data["high"],
                        low_price=candle_data["low"],
                        close_price=candle_data["close"],
                        volume=candle_data["volume"],
                        number_of_trades=candle_data["trades"],
                        taker_buy_volume=candle_data["taker_buy_volume"],
                        taker_buy_quote_volume=candle_data["taker_buy_quote_volume"]
                    )
                    db_candles.append(candle)

                if db_candles:
                    self.session.add_all(db_candles)
                    await self.session.commit()
                    
                    logger.debug(
                        f"Saved {len(db_candles)} candles for {symbol} {interval}"
                    )

                # Sleep until next candle
                await self._wait_for_next_candle(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    f"Error collecting candles for {symbol} {interval}: {str(e)}"
                )
                await asyncio.sleep(5)

    async def _get_last_candle(
        self,
        symbol: str,
        interval: str
    ) -> Optional[CandleModel]:
        """Get the last candle from database.
        
        Args:
            symbol: Trading pair symbol
            interval: Candlestick interval
            
        Returns:
            Last candle or None if no candles exist
        """
        query = (
            select(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.interval == interval
            )
            .order_by(CandleModel.timestamp.desc())
            .limit(1)
        )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _wait_for_next_candle(self, interval: str):
        """Wait until the start of next candle.
        
        Args:
            interval: Candlestick interval
        """
        interval_seconds = {
            "1m": 60,
            "5m": 300,
            "15m": 900,
            "1h": 3600,
            "4h": 14400,
            "1d": 86400
        }[interval]

        now = datetime.utcnow().timestamp()
        next_candle = (now // interval_seconds + 1) * interval_seconds
        wait_time = next_candle - now
        
        await asyncio.sleep(wait_time) 