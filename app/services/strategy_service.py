"""Trading strategy service module."""
from typing import List, Optional
from decimal import Decimal
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from binance.client import Client

from app.core.logging import strategy_logger, error_logger
from app.models.strategy import Strategy
from app.models.position import Position
from app.schemas.order import OrderCreate
from app.services.risk_service import RiskService
from app.core.config import settings


class StrategyService:
    """Service for managing and executing trading strategies."""

    def __init__(self, db: Session, is_demo: bool = True):
        """Initialize strategy service."""
        self.db = db
        self.is_demo = is_demo
        self.risk_service = RiskService(db)
        self.client = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)

    def get_active_strategies(self) -> List[Strategy]:
        """Get list of active trading strategies."""
        return self.db.query(Strategy).filter(Strategy.is_active == True).all()

    async def execute_strategy(self, strategy: Strategy) -> None:
        """
        Execute a trading strategy.
        
        Args:
            strategy: Strategy to execute
        """
        try:
            # Get market data
            df = self._get_market_data(strategy.symbol, strategy.timeframe)
            
            # Apply strategy
            signals = self._apply_strategy(strategy.type, df)
            
            if signals:
                strategy_logger.info(
                    f"Strategy {strategy.type} generated signals",
                    extra={
                        "strategy_id": strategy.id,
                        "symbol": strategy.symbol,
                        "signals": len(signals)
                    }
                )
                
                # Process signals
                await self._process_signals(strategy, signals)
                
        except Exception as e:
            error_logger.error(
                f"Error executing strategy: {str(e)}",
                extra={"strategy_id": strategy.id}
            )

    def _get_market_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Get market data from Binance."""
        try:
            # Get klines data
            klines = self.client.get_klines(
                symbol=symbol,
                interval=timeframe,
                limit=100
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close',
                'volume', 'close_time', 'quote_volume', 'trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # Convert types
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
                
            return df
            
        except Exception as e:
            error_logger.error(
                f"Error getting market data: {str(e)}",
                extra={"symbol": symbol, "timeframe": timeframe}
            )
            return pd.DataFrame()

    def _apply_strategy(self, strategy_type: str, df: pd.DataFrame) -> List[dict]:
        """
        Apply trading strategy to market data.
        
        Supported strategies:
        - MA_CROSS: Moving Average Crossover
        - RSI: Relative Strength Index
        - MACD: Moving Average Convergence Divergence
        - BB: Bollinger Bands
        """
        signals = []
        
        try:
            if strategy_type == "MA_CROSS":
                signals = self._ma_cross_strategy(df)
            elif strategy_type == "RSI":
                signals = self._rsi_strategy(df)
            elif strategy_type == "MACD":
                signals = self._macd_strategy(df)
            elif strategy_type == "BB":
                signals = self._bollinger_bands_strategy(df)
            
            strategy_logger.info(
                f"Applied {strategy_type} strategy",
                extra={"signals": len(signals)}
            )
            return signals
            
        except Exception as e:
            error_logger.error(
                f"Error applying strategy: {str(e)}",
                extra={"strategy_type": strategy_type}
            )
            return []

    def _ma_cross_strategy(self, df: pd.DataFrame) -> List[dict]:
        """Moving Average Crossover strategy."""
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA50'] = df['close'].rolling(window=50).mean()
        
        signals = []
        for i in range(1, len(df)):
            # Check for crossover
            if df['MA20'].iloc[i-1] < df['MA50'].iloc[i-1] and \
               df['MA20'].iloc[i] > df['MA50'].iloc[i]:
                signals.append({
                    'type': 'BUY',
                    'price': df['close'].iloc[i],
                    'timestamp': df['timestamp'].iloc[i]
                })
            elif df['MA20'].iloc[i-1] > df['MA50'].iloc[i-1] and \
                 df['MA20'].iloc[i] < df['MA50'].iloc[i]:
                signals.append({
                    'type': 'SELL',
                    'price': df['close'].iloc[i],
                    'timestamp': df['timestamp'].iloc[i]
                })
        
        return signals

    def _rsi_strategy(self, df: pd.DataFrame) -> List[dict]:
        """RSI strategy."""
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        signals = []
        for i in range(1, len(df)):
            if df['RSI'].iloc[i-1] < 30 and df['RSI'].iloc[i] > 30:
                signals.append({
                    'type': 'BUY',
                    'price': df['close'].iloc[i],
                    'timestamp': df['timestamp'].iloc[i]
                })
            elif df['RSI'].iloc[i-1] > 70 and df['RSI'].iloc[i] < 70:
                signals.append({
                    'type': 'SELL',
                    'price': df['close'].iloc[i],
                    'timestamp': df['timestamp'].iloc[i]
                })
        
        return signals

    async def _process_signals(self, strategy: Strategy, signals: List[dict]) -> None:
        """Process trading signals."""
        for signal in signals:
            try:
                # Create order
                order = OrderCreate(
                    symbol=strategy.symbol,
                    type=signal['type'],
                    price=Decimal(str(signal['price'])),
                    quantity=self._calculate_position_size(strategy, signal['price']),
                    strategy_id=strategy.id
                )
                
                # Validate order
                current_positions = self._get_current_positions(strategy.symbol)
                is_valid, reason = self.risk_service.validate_order(order, current_positions)
                
                if is_valid:
                    if self.is_demo:
                        strategy_logger.info(
                            "Demo mode: Order would be placed",
                            extra={
                                "order": order.dict(),
                                "strategy_id": strategy.id
                            }
                        )
                    else:
                        # Execute order
                        # TODO: Implement order execution
                        pass
                else:
                    strategy_logger.warning(
                        f"Order validation failed: {reason}",
                        extra={"strategy_id": strategy.id}
                    )
                    
            except Exception as e:
                error_logger.error(
                    f"Error processing signal: {str(e)}",
                    extra={
                        "strategy_id": strategy.id,
                        "signal": signal
                    }
                )

    def _calculate_position_size(self, strategy: Strategy, price: float) -> Decimal:
        """Calculate position size based on risk parameters."""
        account_size = Decimal("10000.0")  # TODO: Get from account
        risk_per_trade = Decimal("0.01")  # 1% risk per trade
        
        position_size = (account_size * risk_per_trade) / Decimal(str(price))
        return position_size.quantize(Decimal("0.00000001"))

    def _get_current_positions(self, symbol: str) -> List[Position]:
        """Get current positions for a symbol."""
        return self.db.query(Position).filter(
            Position.symbol == symbol,
            Position.is_open == True
        ).all() 