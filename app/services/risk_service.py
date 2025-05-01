"""Risk analysis service module."""
from typing import Dict, List, Optional
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.logging import risk_logger
from app.models.order import Order
from app.models.position import Position
from app.schemas.order import OrderCreate


class RiskService:
    """Service for risk analysis and management."""

    def __init__(self, db: Session):
        """Initialize risk service."""
        self.db = db
        self.max_position_size: Decimal = Decimal("1000.0")  # Maximum position size in USD
        self.max_daily_loss: Decimal = Decimal("100.0")  # Maximum daily loss in USD
        self.max_leverage: int = 3  # Maximum allowed leverage
        self.position_risk_threshold: Decimal = Decimal("0.02")  # 2% risk per position

    def validate_order(self, order: OrderCreate, current_positions: List[Position]) -> tuple[bool, str]:
        """
        Validate order against risk parameters.
        
        Args:
            order: Order to validate
            current_positions: List of current positions
            
        Returns:
            tuple[bool, str]: (is_valid, reason)
        """
        try:
            # Check position size
            if order.quantity * order.price > self.max_position_size:
                msg = f"Order size ({order.quantity * order.price} USD) exceeds maximum allowed ({self.max_position_size} USD)"
                risk_logger.warning(msg, extra={"order_id": order.id})
                return False, msg

            # Check leverage
            if order.leverage and order.leverage > self.max_leverage:
                msg = f"Leverage ({order.leverage}) exceeds maximum allowed ({self.max_leverage})"
                risk_logger.warning(msg, extra={"order_id": order.id})
                return False, msg

            # Calculate total exposure
            total_exposure = sum(pos.current_value for pos in current_positions)
            new_exposure = total_exposure + (order.quantity * order.price)
            
            # Check total exposure
            if new_exposure > self.max_position_size * Decimal("2"):
                msg = f"Total exposure ({new_exposure} USD) would exceed maximum allowed"
                risk_logger.warning(msg, extra={"order_id": order.id})
                return False, msg

            risk_logger.info(
                "Order passed risk validation",
                extra={
                    "order_id": order.id,
                    "exposure": str(new_exposure),
                    "leverage": order.leverage
                }
            )
            return True, "Order validated successfully"

        except Exception as e:
            error_msg = f"Error validating order: {str(e)}"
            risk_logger.error(error_msg, extra={"order_id": order.id})
            return False, error_msg

    def calculate_position_risk(self, position: Position) -> Dict[str, Decimal]:
        """
        Calculate risk metrics for a position.
        
        Args:
            position: Position to analyze
            
        Returns:
            Dict with risk metrics
        """
        try:
            # Calculate basic risk metrics
            value_at_risk = position.current_value * self.position_risk_threshold
            max_loss = position.entry_price - position.stop_loss if position.stop_loss else 0
            
            risk_metrics = {
                "value_at_risk": value_at_risk,
                "max_loss": Decimal(str(max_loss)),
                "risk_reward_ratio": Decimal("0"),  # Will be calculated if take_profit exists
                "position_risk_percentage": (position.current_value / self.max_position_size) * 100
            }
            
            # Calculate risk/reward ratio if take_profit exists
            if position.take_profit:
                potential_profit = position.take_profit - position.entry_price
                if max_loss != 0:
                    risk_metrics["risk_reward_ratio"] = Decimal(str(potential_profit / max_loss))

            risk_logger.info(
                "Position risk calculated",
                extra={
                    "position_id": position.id,
                    "metrics": {k: str(v) for k, v in risk_metrics.items()}
                }
            )
            return risk_metrics

        except Exception as e:
            error_msg = f"Error calculating position risk: {str(e)}"
            risk_logger.error(error_msg, extra={"position_id": position.id})
            return {} 