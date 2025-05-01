from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
from binance.client import Client

from app.strategies.base import BaseStrategy
from app.schemas.position import PositionType


class TrendFollowingStrategy(BaseStrategy):
    """Trend following strategy implementation."""
    
    def __init__(self, strategy, client: Client):
        super().__init__(strategy)
        self.client = client
        self.ema_fast = 20
        self.ema_slow = 50
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
    async def analyze_market(self, data: Dict[str, Any]) -> Optional[PositionType]:
        """Analyze market data using trend following indicators."""
        # Получение исторических данных
        klines = self.client.get_historical_klines(
            self.strategy.symbol,
            self.strategy.timeframe,
            limit=100
        )
        
        # Преобразование в DataFrame
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        # Конвертация типов
        df['close'] = df['close'].astype(float)
        
        # Расчет индикаторов
        df['ema_fast'] = df['close'].ewm(span=self.ema_fast).mean()
        df['ema_slow'] = df['close'].ewm(span=self.ema_slow).mean()
        
        # Расчет RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Получение последних значений
        last_row = df.iloc[-1]
        
        # Сигналы
        ema_cross = last_row['ema_fast'] > last_row['ema_slow']
        rsi_condition = last_row['rsi'] < self.rsi_oversold or last_row['rsi'] > self.rsi_overbought
        
        # Определение направления
        if ema_cross and last_row['rsi'] < self.rsi_oversold:
            return PositionType.LONG
        elif not ema_cross and last_row['rsi'] > self.rsi_overbought:
            return PositionType.SHORT
            
        return None
        
    def calculate_volatility(self, data: Dict[str, Any]) -> float:
        """Calculate market volatility."""
        returns = np.diff(np.log(data['close']))
        return np.std(returns) * np.sqrt(252)  # Годовая волатильность 