import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.strategy_service import StrategyService
from app.models.strategy import Strategy
from app.models.position import Position
from app.schemas.position import PositionType, PositionStatus


@pytest.fixture
def mock_db():
    return Mock(spec=Session)


@pytest.fixture
def strategy_service(mock_db):
    return StrategyService(mock_db)


@pytest.fixture
def sample_strategy():
    return Strategy(
        id=1,
        name="Test Strategy",
        symbol="BTCUSDT",
        is_active=True,
        max_position_size=0.1,
        leverage=2,
        stop_loss=0.05,
        take_profit=0.1,
        trailing_stop=0.03
    )


@pytest.fixture
def sample_position():
    return Position(
        id=1,
        strategy_id=1,
        symbol="BTCUSDT",
        type=PositionType.LONG,
        status=PositionStatus.OPEN,
        entry_price=50000.0,
        current_price=51000.0,
        quantity=0.1,
        leverage=2,
        stop_loss=47500.0,
        take_profit=55000.0,
        trailing_stop=0.03
    )


def test_get_strategy(strategy_service, mock_db, sample_strategy):
    mock_db.query.return_value.filter.return_value.first.return_value = sample_strategy
    
    result = strategy_service.get_strategy(1)
    
    assert result == sample_strategy
    mock_db.query.assert_called_once()


def test_get_active_strategies(strategy_service, mock_db, sample_strategy):
    mock_db.query.return_value.filter.return_value.all.return_value = [sample_strategy]
    
    result = strategy_service.get_active_strategies()
    
    assert result == [sample_strategy]
    mock_db.query.assert_called_once()


@pytest.mark.asyncio
async def test_execute_strategy(strategy_service, mock_db, sample_strategy):
    with patch('binance.client.Client.get_symbol_ticker') as mock_ticker:
        mock_ticker.return_value = {'price': '50000.0'}
        
        await strategy_service.execute_strategy(sample_strategy)
        
        mock_ticker.assert_called_once_with(symbol=sample_strategy.symbol)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_positions(strategy_service, mock_db, sample_position):
    mock_db.query.return_value.filter.return_value.all.return_value = [sample_position]
    
    with patch('binance.client.Client.get_symbol_ticker') as mock_ticker:
        mock_ticker.return_value = {'price': '52000.0'}
        
        await strategy_service.update_positions()
        
        assert sample_position.current_price == 52000.0
        assert sample_position.unrealized_pnl == 400.0  # (52000 - 50000) * 0.1 * 2
        mock_db.commit.assert_called_once()


def test_calculate_pnl(strategy_service, sample_position):
    # Test long position
    pnl = strategy_service._calculate_pnl(sample_position)
    assert pnl == 200.0  # (51000 - 50000) * 0.1 * 2
    
    # Test short position
    sample_position.type = PositionType.SHORT
    pnl = strategy_service._calculate_pnl(sample_position)
    assert pnl == -200.0  # -(51000 - 50000) * 0.1 * 2


def test_should_close_position(strategy_service, sample_position):
    # Test stop loss for long position
    sample_position.current_price = 47000.0
    assert strategy_service._should_close_position(sample_position)
    
    # Test take profit for long position
    sample_position.current_price = 56000.0
    assert strategy_service._should_close_position(sample_position)
    
    # Test stop loss for short position
    sample_position.type = PositionType.SHORT
    sample_position.current_price = 53000.0
    assert strategy_service._should_close_position(sample_position)
    
    # Test take profit for short position
    sample_position.current_price = 45000.0
    assert strategy_service._should_close_position(sample_position)
    
    # Test position should stay open
    sample_position.current_price = 51000.0
    assert not strategy_service._should_close_position(sample_position) 