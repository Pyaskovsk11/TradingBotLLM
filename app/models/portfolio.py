from typing import List

from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base


class Portfolio(Base):
    """Portfolio model for storing trading portfolios."""
    
    __tablename__ = "portfolios"

    name = Column(String, nullable=False)
    description = Column(String)
    initial_balance = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    user_id = Column(ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="portfolios")
    trades = relationship("Trade", back_populates="portfolio", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Portfolio {self.name}>" 