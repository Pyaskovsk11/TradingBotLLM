from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud import crud_strategy
from app.schemas.strategy import Strategy, StrategyCreate, StrategyUpdate


router = APIRouter()


@router.get("/", response_model=List[Strategy])
def read_strategies(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve strategies for current user.
    """
    strategies = crud_strategy.strategy.get_by_owner(
        db, owner_id=current_user.id, skip=skip, limit=limit
    )
    return strategies


@router.post("/", response_model=Strategy)
def create_strategy(
    *,
    db: Session = Depends(get_db),
    strategy_in: StrategyCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new strategy.
    """
    strategy = crud_strategy.strategy.create_with_owner(
        db, obj_in=strategy_in, owner_id=current_user.id
    )
    return strategy


@router.put("/{strategy_id}", response_model=Strategy)
def update_strategy(
    *,
    db: Session = Depends(get_db),
    strategy_id: int,
    strategy_in: StrategyUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a strategy.
    """
    strategy = crud_strategy.strategy.get(db, id=strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail="The strategy with this id does not exist in the system",
        )
    if strategy.owner_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    strategy = crud_strategy.strategy.update(
        db, db_obj=strategy, obj_in=strategy_in
    )
    return strategy


@router.get("/{strategy_id}", response_model=Strategy)
def read_strategy(
    *,
    db: Session = Depends(get_db),
    strategy_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get strategy by id.
    """
    strategy = crud_strategy.strategy.get(db, id=strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=404,
            detail="The strategy with this id does not exist in the system",
        )
    if strategy.owner_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Not enough permissions"
        )
    return strategy


@router.get("/active/", response_model=List[Strategy])
def read_active_strategies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get active strategies for current user.
    """
    strategies = crud_strategy.strategy.get_active_strategies(
        db, owner_id=current_user.id
    )
    return strategies 