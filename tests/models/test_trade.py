from datetime import datetime
import pytest
from sqlalchemy.orm import Session

from app.models.trade import Trade
from app.schemas.trade import TradeType


def test_create_trade(db: Session) -> None:
    """Test creating a trade."""
    trade = Trade(
        symbol="BTCUSDT",
        type=TradeType.BUY,
        quantity=1.0,
        price=50000.0,
        timestamp=datetime.utcnow(),
        portfolio_id=1
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)

    assert trade.id is not None
    assert trade.symbol == "BTCUSDT"
    assert trade.type == TradeType.BUY
    assert trade.quantity == 1.0
    assert trade.price == 50000.0
    assert trade.portfolio_id == 1


def test_trade_relationships(db: Session) -> None:
    """Test trade relationships."""
    trade = Trade(
        symbol="ETHUSDT",
        type=TradeType.SELL,
        quantity=2.0,
        price=3000.0,
        timestamp=datetime.utcnow(),
        portfolio_id=1
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)

    assert trade.portfolio is None  # Portfolio should be loaded separately
    assert trade.__repr__() == f"<Trade ETHUSDT sell 2.0@3000.0>"


def test_trade_validation(db: Session) -> None:
    """Test trade validation."""
    with pytest.raises(Exception):
        # Test invalid trade type
        Trade(
            symbol="BTCUSDT",
            type="invalid",  # Invalid type
            quantity=1.0,
            price=50000.0,
            timestamp=datetime.utcnow(),
            portfolio_id=1
        )

    with pytest.raises(Exception):
        # Test negative quantity
        Trade(
            symbol="BTCUSDT",
            type=TradeType.BUY,
            quantity=-1.0,  # Invalid quantity
            price=50000.0,
            timestamp=datetime.utcnow(),
            portfolio_id=1
        )

    with pytest.raises(Exception):
        # Test negative price
        Trade(
            symbol="BTCUSDT",
            type=TradeType.BUY,
            quantity=1.0,
            price=-50000.0,  # Invalid price
            timestamp=datetime.utcnow(),
            portfolio_id=1
        ) 