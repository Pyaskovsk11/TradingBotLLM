"""Order model module."""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, Enum, Index
from app.models.base import Base
import enum


class OrderSide(str, enum.Enum):
    """Enum for order sides."""
    BUY = "buy"
    SELL = "sell"


class OrderType(str, enum.Enum):
    """Enum for order types."""
    LIMIT = "limit"
    MARKET = "market"


class Order(Base):
    """Model for storing order book data."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    order_id = Column(String, unique=True, nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    type = Column(Enum(OrderType), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, nullable=False)  # NEW, FILLED, CANCELED, etc.
    filled_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float)
    average_price = Column(Float)

    # Create indexes for faster queries
    __table_args__ = (
        Index('idx_orders_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_orders_order_id', 'order_id'),
    )

    def __repr__(self) -> str:
        """String representation of the order."""
        return f"<Order {self.order_id} {self.symbol} {self.side} {self.status}>" 