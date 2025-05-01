"""Market data processing module."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candle import Candle as CandleModel
from .indicators import TechnicalIndicators


class MarketDataProcessor:
    """Service for processing market data."""

    def __init__(self, session: AsyncSession):
        """Initialize market data processor.
        
        Args:
            session: Database session
        """
        self.session = session

    async def get_candles(
        self,
        symbol: str,
        interval: str,
        limit: int = 1000,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """Get candlestick data from database.
        
        Args:
            symbol: Trading pair symbol
            interval: Candlestick interval
            limit: Number of candles to get
            start_time: Start time for historical data
            end_time: End time for historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        # Build query
        query = (
            select(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.interval == interval
            )
            .order_by(CandleModel.timestamp.desc())
            .limit(limit)
        )
        
        if start_time:
            query = query.filter(CandleModel.timestamp >= start_time)
        if end_time:
            query = query.filter(CandleModel.timestamp <= end_time)
            
        # Execute query
        result = await self.session.execute(query)
        candles = result.scalars().all()
        
        if not candles:
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'timestamp': c.timestamp,
                'open': c.open_price,
                'high': c.high_price,
                'low': c.low_price,
                'close': c.close_price,
                'volume': c.volume,
                'trades': c.number_of_trades,
                'taker_buy_volume': c.taker_buy_volume,
                'taker_buy_quote_volume': c.taker_buy_quote_volume
            }
            for c in candles
        ])
        
        # Sort by timestamp
        df.sort_values('timestamp', inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        return df

    async def analyze_market(
        self,
        symbol: str,
        interval: str,
        lookback_periods: int = 100
    ) -> Dict[str, Any]:
        """Analyze market data for a symbol.
        
        Args:
            symbol: Trading pair symbol
            interval: Candlestick interval
            lookback_periods: Number of periods to analyze
            
        Returns:
            Dictionary with market analysis including:
            - Technical indicators
            - Trend direction
            - Support/resistance levels
            - Volume profile
        """
        # Get candlestick data
        df = await self.get_candles(
            symbol=symbol,
            interval=interval,
            limit=lookback_periods
        )
        
        if df.empty:
            return {}
            
        # Calculate indicators
        indicators = TechnicalIndicators(df)
        df = indicators.calculate_all()
        
        # Add trend direction
        indicators.add_trend_direction()
        
        # Get support/resistance levels
        levels = indicators.get_support_resistance()
        
        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(df)
        
        # Get current market state
        current = df.iloc[-1]
        prev = df.iloc[-2]
        
        return {
            'symbol': symbol,
            'interval': interval,
            'timestamp': current.timestamp,
            'price': {
                'open': current.open,
                'high': current.high,
                'low': current.low,
                'close': current.close,
                'change': (current.close - prev.close) / prev.close * 100
            },
            'volume': {
                'total': current.volume,
                'taker_buy': current.taker_buy_volume,
                'taker_sell': current.volume - current.taker_buy_volume,
                'profile': volume_profile
            },
            'trend': {
                'direction': current.trend_direction,
                'strength': current.adx,
                'supertrend': current.supertrend_direction
            },
            'momentum': {
                'rsi': current.rsi,
                'stoch_rsi_k': current.stoch_rsi_k,
                'stoch_rsi_d': current.stoch_rsi_d,
                'williams_r': current.williams_r
            },
            'levels': levels,
            'indicators': {
                'ema_8': current.ema_8,
                'ema_21': current.ema_21,
                'ema_55': current.ema_55,
                'ema_200': current.ema_200,
                'vwap': current.vwap,
                'obv': current.obv
            }
        }

    def _calculate_volume_profile(
        self,
        df: pd.DataFrame,
        num_bins: int = 10
    ) -> List[Dict[str, float]]:
        """Calculate volume profile.
        
        Args:
            df: DataFrame with OHLCV data
            num_bins: Number of price bins
            
        Returns:
            List of dictionaries with price levels and volumes
        """
        # Calculate price range
        price_min = df['low'].min()
        price_max = df['high'].max()
        bin_size = (price_max - price_min) / num_bins
        
        # Create bins
        bins = []
        for i in range(num_bins):
            price_level = price_min + bin_size * i
            mask = (df['low'] <= price_level) & (df['high'] >= price_level)
            volume = df.loc[mask, 'volume'].sum()
            
            bins.append({
                'price_level': price_level,
                'volume': volume
            })
            
        return sorted(bins, key=lambda x: x['volume'], reverse=True) 