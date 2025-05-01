from pydantic import BaseModel


class PortfolioBase(BaseModel):
    """Base portfolio schema."""
    symbol: str
    quantity: float
    average_price: float


class PortfolioCreate(PortfolioBase):
    """Schema for portfolio creation."""
    pass


class PortfolioUpdate(PortfolioBase):
    """Schema for portfolio update."""
    pass


class Portfolio(PortfolioBase):
    """Schema for portfolio response."""
    id: int
    user_id: int

    class Config:
        from_attributes = True 