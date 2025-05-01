from typing import Any, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud import crud_trade, crud_portfolio
from app.schemas.trade import Trade, TradeCreate, TradeUpdate
from app.models.user import User


router = APIRouter()


@router.get("/portfolio/{portfolio_id}", response_model=List[Trade])
def read_trades_by_portfolio(
    *,
    db: Session = Depends(get_db),
    portfolio_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get trades by portfolio.
    """
    portfolio = crud_portfolio.portfolio.get(db, id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="The portfolio with this id does not exist in the system",
        )
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    trades = crud_trade.trade.get_by_portfolio(
        db, portfolio_id=portfolio_id, skip=skip, limit=limit
    )
    return trades


@router.post("/", response_model=Trade)
def create_trade(
    *,
    db: Session = Depends(get_db),
    trade_in: TradeCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new trade.
    """
    portfolio = crud_portfolio.portfolio.get(db, id=trade_in.portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="The portfolio with this id does not exist in the system",
        )
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    trade = crud_trade.trade.create(db, obj_in=trade_in)
    return trade


@router.get("/portfolio/{portfolio_id}/symbol/{symbol}", response_model=List[Trade])
def read_trades_by_symbol(
    *,
    db: Session = Depends(get_db),
    portfolio_id: int,
    symbol: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get trades by symbol in portfolio.
    """
    portfolio = crud_portfolio.portfolio.get(db, id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="The portfolio with this id does not exist in the system",
        )
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    trades = crud_trade.trade.get_by_symbol(
        db, symbol=symbol, portfolio_id=portfolio_id, skip=skip, limit=limit
    )
    return trades


@router.get("/portfolio/{portfolio_id}/time-range/", response_model=List[Trade])
def read_trades_by_time_range(
    *,
    db: Session = Depends(get_db),
    portfolio_id: int,
    start_time: datetime,
    end_time: datetime,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get trades by time range in portfolio.
    """
    portfolio = crud_portfolio.portfolio.get(db, id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="The portfolio with this id does not exist in the system",
        )
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    trades = crud_trade.trade.get_by_time_range(
        db,
        portfolio_id=portfolio_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    return trades


@router.get("/portfolio/{portfolio_id}/type/{trade_type}", response_model=List[Trade])
def read_trades_by_type(
    *,
    db: Session = Depends(get_db),
    portfolio_id: int,
    trade_type: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get trades by type in portfolio.
    """
    portfolio = crud_portfolio.portfolio.get(db, id=portfolio_id)
    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="The portfolio with this id does not exist in the system",
        )
    if portfolio.user_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    trades = crud_trade.trade.get_by_type(
        db, portfolio_id=portfolio_id, trade_type=trade_type, skip=skip, limit=limit
    )
    return trades 