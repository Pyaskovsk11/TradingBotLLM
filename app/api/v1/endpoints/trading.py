"""Trading endpoints."""
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud.crud_order import order_crud
from app.crud.crud_signal import signal_crud
from app.schemas.order import Order, OrderCreate
from app.schemas.signal import Signal, SignalCreate
from app.schemas.user import User
from app.services.trading_service import TradingService

router = APIRouter()


@router.post("/orders", response_model=Order)
async def create_order(
    *,
    db: Annotated[Session, Depends(get_db)],
    order_in: OrderCreate,
    current_user: Annotated[User, Depends(get_current_user)]
) -> Order:
    """Create new trading order."""
    trading_service = TradingService()
    
    # Validate order parameters
    if not trading_service.validate_order(order_in):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order parameters"
        )
    
    # Create order
    order = order_crud.create_with_owner(
        db=db, obj_in=order_in, owner_id=current_user.id
    )
    
    # Execute order if needed
    if order_in.execute_immediately:
        trading_service.execute_order(order)
    
    return order


@router.get("/orders", response_model=List[Order])
async def get_orders(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100
) -> List[Order]:
    """Get list of user's orders."""
    return order_crud.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )


@router.post("/signals", response_model=Signal)
async def create_signal(
    *,
    db: Annotated[Session, Depends(get_db)],
    signal_in: SignalCreate,
    current_user: Annotated[User, Depends(get_current_user)]
) -> Signal:
    """Create new trading signal."""
    return signal_crud.create_with_owner(
        db=db, obj_in=signal_in, owner_id=current_user.id
    )


@router.get("/signals", response_model=List[Signal])
async def get_signals(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100
) -> List[Signal]:
    """Get list of user's trading signals."""
    return signal_crud.get_multi_by_owner(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    ) 