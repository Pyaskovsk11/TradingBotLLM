"""Price levels analysis module."""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.level import Level, LevelType
from app.models.candle import Candle as CandleModel


class LevelAnalyzer:
    """Service for analyzing and managing price levels."""

    def __init__(self, session: AsyncSession):
        """Initialize level analyzer.
        
        Args:
            session: Database session
        """
        self.session = session

    async def find_levels(
        self,
        symbol: str,
        interval: str = "1h",
        lookback_periods: int = 500,
        min_touches: int = 3,
        price_threshold: float = 0.002,
        volume_threshold: float = 1.5
    ) -> List[Dict[str, Any]]:
        """Find support and resistance levels.
        
        Args:
            symbol: Trading pair symbol
            interval: Candlestick interval
            lookback_periods: Number of periods to analyze
            min_touches: Minimum number of touches required
            price_threshold: Maximum % difference to consider same level
            volume_threshold: Minimum volume multiplier for confirmation
            
        Returns:
            List of levels with their properties
        """
        # Get candlestick data
        query = (
            select(CandleModel)
            .filter(
                CandleModel.symbol == symbol,
                CandleModel.interval == interval
            )
            .order_by(CandleModel.timestamp.desc())
            .limit(lookback_periods)
        )
        
        result = await self.session.execute(query)
        candles = result.scalars().all()
        
        if not candles:
            return []
            
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'timestamp': c.timestamp,
                'open': c.open_price,
                'high': c.high_price,
                'low': c.low_price,
                'close': c.close_price,
                'volume': c.volume
            }
            for c in candles
        ])
        
        # Sort by timestamp
        df.sort_values('timestamp', inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        # Calculate average volume
        avg_volume = df['volume'].mean()
        
        # Find potential levels
        levels = []
        
        # Look for swing highs (resistance)
        for i in range(2, len(df) - 2):
            if (df['high'].iloc[i] > df['high'].iloc[i-1] and 
                df['high'].iloc[i] > df['high'].iloc[i-2] and
                df['high'].iloc[i] > df['high'].iloc[i+1] and
                df['high'].iloc[i] > df['high'].iloc[i+2] and
                df['volume'].iloc[i] > avg_volume * volume_threshold):
                
                price = df['high'].iloc[i]
                
                # Count touches
                touches = len(df[
                    (df['high'] >= price * (1 - price_threshold)) &
                    (df['high'] <= price * (1 + price_threshold))
                ])
                
                if touches >= min_touches:
                    levels.append({
                        'price': price,
                        'type': LevelType.RESISTANCE,
                        'strength': touches / lookback_periods,
                        'volume_confirmation': df['volume'].iloc[i] / avg_volume,
                        'timestamp': df['timestamp'].iloc[i]
                    })
        
        # Look for swing lows (support)
        for i in range(2, len(df) - 2):
            if (df['low'].iloc[i] < df['low'].iloc[i-1] and 
                df['low'].iloc[i] < df['low'].iloc[i-2] and
                df['low'].iloc[i] < df['low'].iloc[i+1] and
                df['low'].iloc[i] < df['low'].iloc[i+2] and
                df['volume'].iloc[i] > avg_volume * volume_threshold):
                
                price = df['low'].iloc[i]
                
                # Count touches
                touches = len(df[
                    (df['low'] >= price * (1 - price_threshold)) &
                    (df['low'] <= price * (1 + price_threshold))
                ])
                
                if touches >= min_touches:
                    levels.append({
                        'price': price,
                        'type': LevelType.SUPPORT,
                        'strength': touches / lookback_periods,
                        'volume_confirmation': df['volume'].iloc[i] / avg_volume,
                        'timestamp': df['timestamp'].iloc[i]
                    })
        
        return levels

    async def update_levels(
        self,
        symbol: str,
        current_price: float,
        current_volume: float
    ):
        """Update existing levels based on current price action.
        
        Args:
            symbol: Trading pair symbol
            current_price: Current price
            current_volume: Current volume
        """
        # Get all active levels for the symbol
        query = (
            select(Level)
            .filter(
                Level.symbol == symbol,
                Level.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        levels = result.scalars().all()
        
        for level in levels:
            # Check if price is testing the level
            price_diff = abs(current_price - level.price) / level.price
            
            if price_diff <= 0.002:  # 0.2% threshold
                # Update level properties
                level.last_tested = datetime.utcnow()
                level.number_of_tests += 1
                level.volume_confirmation = (
                    level.volume_confirmation * 0.7 +  # Exponential moving average
                    current_volume * 0.3
                )
                level.strength = min(
                    1.0,
                    level.strength * 1.1  # Increase strength on test
                )
            else:
                # Decay strength over time
                time_since_test = (
                    datetime.utcnow() - level.last_tested
                    if level.last_tested
                    else datetime.utcnow() - level.timestamp
                )
                
                if time_since_test > timedelta(days=7):
                    level.strength *= 0.95  # Decay by 5%
                    
                    # Deactivate weak levels
                    if level.strength < 0.2:
                        level.is_active = False
        
        await self.session.commit()

    async def get_nearest_levels(
        self,
        symbol: str,
        price: float,
        num_levels: int = 3
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get nearest support and resistance levels.
        
        Args:
            symbol: Trading pair symbol
            price: Current price
            num_levels: Number of levels to return in each direction
            
        Returns:
            Dictionary with nearest support and resistance levels
        """
        # Get all active levels
        query = (
            select(Level)
            .filter(
                Level.symbol == symbol,
                Level.is_active == True
            )
        )
        
        result = await self.session.execute(query)
        levels = result.scalars().all()
        
        supports = []
        resistances = []
        
        for level in levels:
            level_dict = {
                'price': level.price,
                'strength': level.strength,
                'volume_confirmation': level.volume_confirmation,
                'number_of_tests': level.number_of_tests,
                'last_tested': level.last_tested,
                'distance': abs(price - level.price) / price * 100  # Distance in %
            }
            
            if level.type == LevelType.SUPPORT and level.price < price:
                supports.append(level_dict)
            elif level.type == LevelType.RESISTANCE and level.price > price:
                resistances.append(level_dict)
        
        # Sort by distance and get nearest levels
        supports.sort(key=lambda x: x['distance'])
        resistances.sort(key=lambda x: x['distance'])
        
        return {
            'support': supports[:num_levels],
            'resistance': resistances[:num_levels]
        } 