"""User schemas."""
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """User create schema."""
    password: str


class UserUpdate(UserBase):
    """User update schema."""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """User in database base schema."""
    id: int

    class Config:
        """Pydantic config."""
        from_attributes = True


class User(UserInDBBase):
    """User schema."""
    pass


class UserInDB(UserInDBBase):
    """User in database schema."""
    hashed_password: str
