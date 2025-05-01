from datetime import datetime, timedelta
from typing import Dict, Any
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.trade import Trade
from app.schemas.trade import TradeType


client = TestClient(app)


def test_create_trade() -> None:
    """Test creating a trade through API."""
    trade_data = {
        "symbol": "BTCUSDT",
        "type": TradeType.BUY,
        "quantity": 1.0,
        "price": 50000.0,
        "portfolio_id": 1
    }
    response = client.post("/api/trades/", json=trade_data)
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "BTCUSDT"
    assert data["type"] == TradeType.BUY
    assert data["quantity"] == 1.0
    assert data["price"] == 50000.0
    assert data["portfolio_id"] == 1


def test_get_trades() -> None:
    """Test getting all trades."""
    response = client.get("/api/trades/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_trade() -> None:
    """Test getting a specific trade."""
    # First create a trade
    trade_data = {
        "symbol": "BTCUSDT",
        "type": TradeType.BUY,
        "quantity": 1.0,
        "price": 50000.0,
        "portfolio_id": 1
    }
    create_response = client.post("/api/trades/", json=trade_data)
    trade_id = create_response.json()["id"]

    # Then get it
    response = client.get(f"/api/trades/{trade_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == trade_id
    assert data["symbol"] == "BTCUSDT"


def test_update_trade() -> None:
    """Test updating a trade."""
    # First create a trade
    trade_data = {
        "symbol": "BTCUSDT",
        "type": TradeType.BUY,
        "quantity": 1.0,
        "price": 50000.0,
        "portfolio_id": 1
    }
    create_response = client.post("/api/trades/", json=trade_data)
    trade_id = create_response.json()["id"]

    # Then update it
    update_data = {
        "quantity": 2.0,
        "price": 51000.0
    }
    response = client.put(f"/api/trades/{trade_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 2.0
    assert data["price"] == 51000.0
    assert data["symbol"] == "BTCUSDT"  # Unchanged


def test_delete_trade() -> None:
    """Test deleting a trade."""
    # First create a trade
    trade_data = {
        "symbol": "BTCUSDT",
        "type": TradeType.BUY,
        "quantity": 1.0,
        "price": 50000.0,
        "portfolio_id": 1
    }
    create_response = client.post("/api/trades/", json=trade_data)
    trade_id = create_response.json()["id"]

    # Then delete it
    response = client.delete(f"/api/trades/{trade_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == trade_id

    # Verify it's deleted
    get_response = client.get(f"/api/trades/{trade_id}")
    assert get_response.status_code == 404


def test_get_trades_by_portfolio() -> None:
    """Test getting trades by portfolio."""
    response = client.get("/api/trades/portfolio/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_trades_by_symbol() -> None:
    """Test getting trades by symbol."""
    response = client.get("/api/trades/symbol/BTCUSDT?portfolio_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(trade["symbol"] == "BTCUSDT" for trade in data)


def test_get_trades_by_time_range() -> None:
    """Test getting trades by time range."""
    now = datetime.utcnow()
    start_time = (now - timedelta(hours=1)).isoformat()
    end_time = (now + timedelta(hours=1)).isoformat()
    
    response = client.get(
        f"/api/trades/time-range?portfolio_id=1&start_time={start_time}&end_time={end_time}"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_trades_by_type() -> None:
    """Test getting trades by type."""
    response = client.get(f"/api/trades/type/{TradeType.BUY}?portfolio_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(trade["type"] == TradeType.BUY for trade in data) 