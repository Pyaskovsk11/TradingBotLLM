from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.strategy import Strategy
from app.models.position import Position
from app.schemas.position import PositionType


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.positions: Dict[str, Position] = {}
        
    @abstractmethod
    async def analyze_market(self, data: Dict[str, Any]) -> Optional[PositionType]:
        """Analyze market data and return trading signal."""
        pass
        
    def calculate_position_size(self, balance: float, volatility: float) -> float:
        """Calculate position size based on balance and volatility."""
        max_size = self.strategy.max_position_size * balance
        risk_adjusted_size = balance * self.strategy.leverage / volatility
        return min(max_size, risk_adjusted_size)
        
    def calculate_stop_loss(self, entry_price: float, position_type: PositionType) -> float:
        """Calculate stop loss price."""
        if position_type == PositionType.LONG:
            return entry_price * (1 - self.strategy.stop_loss)
        return entry_price * (1 + self.strategy.stop_loss)
        
    def calculate_take_profit(self, entry_price: float, position_type: PositionType) -> float:
        """Calculate take profit price."""
        if position_type == PositionType.LONG:
            return entry_price * (1 + self.strategy.take_profit)
        return entry_price * (1 - self.strategy.take_profit)
        
    def update_trailing_stop(self, position: Position, current_price: float) -> Optional[float]:
        """Update trailing stop price."""
        if position.unrealized_pnl <= 0:
            return position.trailing_stop
            
        if position.type == PositionType.LONG:
            new_stop = current_price * (1 - self.strategy.trailing_stop)
            return max(position.trailing_stop, new_stop)
        else:
            new_stop = current_price * (1 + self.strategy.trailing_stop)
            return min(position.trailing_stop, new_stop)
            
    def should_close_position(self, position: Position, current_price: float) -> bool:
        """Check if position should be closed."""
        if position.type == PositionType.LONG:
            return (
                current_price <= position.stop_loss or
                current_price >= position.take_profit or
                (position.trailing_stop and current_price <= position.trailing_stop)
            )
        return (
            current_price >= position.stop_loss or
            current_price <= position.take_profit or
            (position.trailing_stop and current_price >= position.trailing_stop)
        ) 