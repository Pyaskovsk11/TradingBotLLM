from datetime import datetime, timedelta
import pytest
from sqlalchemy.orm import Session

from app.crud import crud_trade
from app.models.trade import Trade
from app.schemas.trade import TradeCreate, TradeUpdate, TradeType


def test_create_trade(db: Session) -> None:
    """Test creating a trade through CRUD."""
    trade_in = TradeCreate(
        symbol="BTCUSDT",
        type=TradeType.BUY,
        quantity=1.0,
        price=50000.0,
        portfolio_id=1
    )
    trade = crud_trade.trade.create(db, obj_in=trade_in)
    
    assert trade.id is not None
    assert trade.symbol == "BTCUSDT"
    assert trade.type == TradeType.BUY
    assert trade.quantity == 1.0
    assert trade.price == 50000.0
    assert trade.portfolio_id == 1


def test_get_trades_by_portfolio(db: Session) -> None:
    """Test getting trades by portfolio."""
    # Create test trades
    trade1 = Trade(
        symbol="BTCUSDT",
        type=TradeType.BUY,
        quantity=1.0,
        price=50000.0,
        timestamp=datetime.utcnow(),
        portfolio_id=1
    )
    trade2 = Trade(
        symbol="ETHUSDT",
        type=TradeType.SELL,
        quantity=2.0,
        price=3000.0,
        timestamp=datetime.utcnow(),
        portfolio_id=1
    )
    db.add_all([trade1, trade2])
    db.commit()

    # Get trades by portfolio
    trades = crud_trade.trade.get_by_portfolio(db, portfolio_id=1)
    assert len(trades) == 2
    assert trades[0].symbol in ["BTCUSDT", "ETHUSDT"]
    assert trades[1].symbol in ["BTCUSDT", "ETHUSDT"]


def test_get_trades_by_symbol(db: Session) -> None:
    """Test getting trades by symbol."""
    # Create test trades
    trade1 = Trade(
        symbol="BTCUSDT",
        type=TradeType.BUY,
        quantity=1.0,
        price=50000.0,
        timestamp=datetime.utcnow(),
        portfolio_id=1
    )
    trade2 = Trade(
        symbol="BTCUSDT",
        type=TradeType.SELL,
        quantity=0.5,
        price=51000.0,
        timestamp=datetime.utcnow(),
        portfolio_id=1
    )
    db.add_all([trade1, trade2])
    db.commit()

    # Get trades by symbol
    trades = crud_trade.trade.get_by_symbol(db, symbol="BTCUSDT", portfolio_id=1)
    assert len(trades) == 2
    assert all(trade.symbol == "BTCUSDT" for trade in trades)


def test_get_trades_by_time_range(db: Session) -> None:
    """Test getting trades by time range."""
    now = datetime.utcnow()
    trade1 = Trade(
        symbol="BTCUSDT",
        type=TradeType.BUY,
        quantity=1.0,
        price=50000.0,
        timestamp=now - timedelta(hours=1),
        portfolio_id=1
    )
    trade2 = Trade(
        symbol="ETHUSDT",
        type=TradeType.SELL,
        quantity=2.0,
        price=3000.0,
        timestamp=now + timedelta(hours=1),
        portfolio_id=1
    )
    db.add_all([trade1, trade2])
    db.commit()

    # Get trades by time range
    trades = crud_trade.trade.get_by_time_range(
        db,
        portfolio_id=1,
        start_time=now - timedelta(hours=2),
        end_time=now + timedelta(hours=2)
    )
    assert len(trades) == 2


def test_get_trades_by_type(db: Session) -> None:
    """Test getting trades by type."""
    # Create test trades
    trade1 = Trade(
        symbol="BTCUSDT",
        type=TradeType.BUY,
        quantity=1.0,
        price=50000.0,
        timestamp=datetime.utcnow(),
        portfolio_id=1
    )
    trade2 = Trade(
        symbol="ETHUSDT",
        type=TradeType.BUY,
        quantity=2.0,
        price=3000.0,
        timestamp=datetime.utcnow(),
        portfolio_id=1
    )
    db.add_all([trade1, trade2])
    db.commit()

    # Get trades by type
    trades = crud_trade.trade.get_by_type(db, portfolio_id=1, trade_type=TradeType.BUY)
    assert len(trades) == 2
    assert all(trade.type == TradeType.BUY for trade in trades)


def test_update_trade(db: Session) -> None:
    """Test updating a trade."""
    # Create test trade
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

    # Update trade
    trade_update = TradeUpdate(quantity=2.0, price=51000.0)
    updated_trade = crud_trade.trade.update(db, db_obj=trade, obj_in=trade_update)
    
    assert updated_trade.quantity == 2.0
    assert updated_trade.price == 51000.0
    assert updated_trade.symbol == "BTCUSDT"  # Unchanged 