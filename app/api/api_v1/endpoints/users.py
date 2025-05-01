from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_active_superuser
from app.users.models import User, UserSettings
from app.users.schemas import UserInDB, UserUpdate, UserSettingsUpdate

router = APIRouter()

@router.get("/me", response_model=UserInDB)
async def read_user_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user."""
    return current_user

@router.put("/me", response_model=UserInDB)
async def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update current user."""
    if user_in.email and user_in.email != current_user.email:
        user = db.query(User).filter(User.email == user_in.email).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
    
    if user_in.username and user_in.username != current_user.username:
        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
    
    for field, value in user_in.dict(exclude_unset=True).items():
        if field == "password" and value:
            setattr(current_user, "hashed_password", value)
        else:
            setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/me/settings")
async def read_user_settings(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user settings."""
    return current_user.settings

@router.put("/me/settings")
async def update_user_settings(
    *,
    db: Session = Depends(get_db),
    settings_in: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update current user settings."""
    settings = current_user.settings
    for field, value in settings_in.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings

# Admin endpoints
@router.get("/", response_model=List[UserInDB])
async def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """Retrieve users. Only for superusers."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users 