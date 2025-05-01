"""Technical indicators calculation module."""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from ta.trend import (
    EMAIndicator,
    ADXIndicator,
    SuperTrendIndicator,
)
from ta.momentum import (
    RSIIndicator,
    StochRSIIndicator,
    WilliamsRIndicator,
)
from ta.volume import (
    OnBalanceVolumeIndicator,
    VolumeWeightedAveragePrice,
)


class TechnicalIndicators:
    """Technical analysis indicators calculator."""

    def __init__(self, df: pd.DataFrame):
        """Initialize indicators calculator.
        
        Args:
            df: DataFrame with OHLCV data with columns:
                - timestamp
                - open
                - high
                - low
                - close
                - volume
        """
        self.df = df.copy()
        self._prepare_data()

    def _prepare_data(self):
        """Prepare data for indicator calculation."""
        # Ensure DataFrame is sorted by timestamp
        self.df.sort_values('timestamp', inplace=True)
        
        # Reset index to ensure proper calculation
        self.df.reset_index(drop=True, inplace=True)

    def calculate_all(self) -> pd.DataFrame:
        """Calculate all technical indicators.
        
        Returns:
            DataFrame with all indicators
        """
        # Trend indicators
        self._add_ema_indicators()
        self._add_supertrend()
        self._add_adx()
        
        # Momentum indicators
        self._add_rsi()
        self._add_stoch_rsi()
        self._add_williams_r()
        
        # Volume indicators
        self._add_obv()
        self._add_vwap()
        
        return self.df

    def _add_ema_indicators(self):
        """Add EMA indicators with different periods."""
        periods = [8, 21, 55, 200]
        
        for period in periods:
            ema = EMAIndicator(close=self.df['close'], window=period)
            self.df[f'ema_{period}'] = ema.ema_indicator()

    def _add_supertrend(self, period: int = 10, multiplier: float = 3.0):
        """Add SuperTrend indicator."""
        supertrend = SuperTrendIndicator(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            window=period,
            multiplier=multiplier
        )
        self.df['supertrend'] = supertrend.supertrend()
        self.df['supertrend_direction'] = supertrend.supertrend_direction()

    def _add_adx(self, period: int = 14):
        """Add ADX indicator."""
        adx = ADXIndicator(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            window=period
        )
        self.df['adx'] = adx.adx()
        self.df['adx_pos'] = adx.adx_pos()
        self.df['adx_neg'] = adx.adx_neg()

    def _add_rsi(self, period: int = 14):
        """Add RSI indicator."""
        rsi = RSIIndicator(close=self.df['close'], window=period)
        self.df['rsi'] = rsi.rsi()

    def _add_stoch_rsi(self, period: int = 14, smooth1: int = 3, smooth2: int = 3):
        """Add Stochastic RSI indicator."""
        stoch_rsi = StochRSIIndicator(
            close=self.df['close'],
            window=period,
            smooth1=smooth1,
            smooth2=smooth2
        )
        self.df['stoch_rsi_k'] = stoch_rsi.stochrsi_k()
        self.df['stoch_rsi_d'] = stoch_rsi.stochrsi_d()

    def _add_williams_r(self, period: int = 14):
        """Add Williams %R indicator."""
        williams_r = WilliamsRIndicator(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            lbp=period
        )
        self.df['williams_r'] = williams_r.williams_r()

    def _add_obv(self):
        """Add On-Balance Volume indicator."""
        obv = OnBalanceVolumeIndicator(close=self.df['close'], volume=self.df['volume'])
        self.df['obv'] = obv.on_balance_volume()

    def _add_vwap(self):
        """Add Volume Weighted Average Price."""
        vwap = VolumeWeightedAveragePrice(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            volume=self.df['volume']
        )
        self.df['vwap'] = vwap.volume_weighted_average_price()

    @staticmethod
    def get_trend_direction(row: pd.Series) -> str:
        """Determine trend direction based on EMAs.
        
        Args:
            row: DataFrame row with EMA values
            
        Returns:
            Trend direction: 'strong_up', 'up', 'neutral', 'down', 'strong_down'
        """
        ema_8 = row['ema_8']
        ema_21 = row['ema_21']
        ema_55 = row['ema_55']
        ema_200 = row['ema_200']
        
        if ema_8 > ema_21 > ema_55 > ema_200:
            return 'strong_up'
        elif ema_8 > ema_21 and ema_21 > ema_55:
            return 'up'
        elif ema_8 < ema_21 < ema_55 < ema_200:
            return 'strong_down'
        elif ema_8 < ema_21 and ema_21 < ema_55:
            return 'down'
        else:
            return 'neutral'

    def add_trend_direction(self):
        """Add trend direction column based on EMAs."""
        self.df['trend_direction'] = self.df.apply(self.get_trend_direction, axis=1)

    def get_support_resistance(
        self,
        window: int = 20,
        num_touches: int = 2,
        price_threshold: float = 0.02
    ) -> Dict[str, list]:
        """Find support and resistance levels.
        
        Args:
            window: Number of candles to look back
            num_touches: Minimum number of touches required
            price_threshold: Maximum % difference to consider same level
            
        Returns:
            Dictionary with support and resistance levels
        """
        levels = {
            'support': [],
            'resistance': []
        }
        
        for i in range(window, len(self.df)):
            window_data = self.df.iloc[i-window:i+1]
            
            # Find local minima (support)
            local_min = window_data[
                (window_data['low'] <= window_data['low'].shift(1)) &
                (window_data['low'] <= window_data['low'].shift(-1))
            ]['low'].values
            
            # Find local maxima (resistance)
            local_max = window_data[
                (window_data['high'] >= window_data['high'].shift(1)) &
                (window_data['high'] >= window_data['high'].shift(-1))
            ]['high'].values
            
            # Count touches for each level
            for level in local_min:
                touches = len(window_data[
                    (window_data['low'] >= level * (1 - price_threshold)) &
                    (window_data['low'] <= level * (1 + price_threshold))
                ])
                if touches >= num_touches:
                    levels['support'].append(level)
            
            for level in local_max:
                touches = len(window_data[
                    (window_data['high'] >= level * (1 - price_threshold)) &
                    (window_data['high'] <= level * (1 + price_threshold))
                ])
                if touches >= num_touches:
                    levels['resistance'].append(level)
        
        # Remove duplicates and sort
        levels['support'] = sorted(list(set(levels['support'])))
        levels['resistance'] = sorted(list(set(levels['resistance'])))
        
        return levels 