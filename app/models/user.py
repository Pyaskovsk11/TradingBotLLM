"""User model."""
from sqlalchemy import Boolean, Column, String
from app.models.base import Base


class User(Base):
    """User model."""
    
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
