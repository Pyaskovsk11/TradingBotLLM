from typing import Optional
from pydantic import BaseModel


class StrategyBase(BaseModel):
    """Base strategy schema."""
    name: str
    description: Optional[str] = None
    is_active: bool = True


class StrategyCreate(StrategyBase):
    """Schema for strategy creation."""
    pass


class StrategyUpdate(StrategyBase):
    """Schema for strategy update."""
    pass


class Strategy(StrategyBase):
    """Schema for strategy response."""
    id: int
    owner_id: int

    class Config:
        from_attributes = True 