from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud import crud_portfolio
from app.schemas.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate


router = APIRouter()


@router.get("/", response_model=List[Portfolio])
def read_portfolio(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve portfolio for current user.
    """
    portfolio = crud_portfolio.portfolio.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return portfolio


@router.post("/", response_model=Portfolio)
def create_portfolio_item(
    *,
    db: Session = Depends(get_db),
    portfolio_in: PortfolioCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new portfolio item.
    """
    portfolio = crud_portfolio.portfolio.create_with_user(
        db, obj_in=portfolio_in, user_id=current_user.id
    )
    return portfolio


@router.put("/{symbol}", response_model=Portfolio)
def update_portfolio_item(
    *,
    db: Session = Depends(get_db),
    symbol: str,
    portfolio_in: PortfolioUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update portfolio item.
    """
    portfolio = crud_portfolio.portfolio.get_by_symbol(
        db, symbol=symbol, user_id=current_user.id
    )
    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="The portfolio item with this symbol does not exist in the system",
        )
    portfolio = crud_portfolio.portfolio.update(
        db, db_obj=portfolio, obj_in=portfolio_in
    )
    return portfolio


@router.get("/{symbol}", response_model=Portfolio)
def read_portfolio_item(
    *,
    db: Session = Depends(get_db),
    symbol: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get portfolio item by symbol.
    """
    portfolio = crud_portfolio.portfolio.get_by_symbol(
        db, symbol=symbol, user_id=current_user.id
    )
    if not portfolio:
        raise HTTPException(
            status_code=404,
            detail="The portfolio item with this symbol does not exist in the system",
        )
    return portfolio 