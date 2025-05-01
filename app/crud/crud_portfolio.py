from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate


class CRUDPortfolio(CRUDBase[Portfolio, PortfolioCreate, PortfolioUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Portfolio]:
        """Get portfolio by user with pagination."""
        return (
            db.query(self.model)
            .filter(Portfolio.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_symbol(
        self, db: Session, *, symbol: str, user_id: int
    ) -> Optional[Portfolio]:
        """Get portfolio by symbol and user."""
        return (
            db.query(self.model)
            .filter(Portfolio.symbol == symbol, Portfolio.user_id == user_id)
            .first()
        )

    def update_quantity(
        self, db: Session, *, db_obj: Portfolio, quantity: float
    ) -> Portfolio:
        """Update portfolio quantity."""
        db_obj.quantity = quantity
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_average_price(
        self, db: Session, *, db_obj: Portfolio, average_price: float
    ) -> Portfolio:
        """Update portfolio average price."""
        db_obj.average_price = average_price
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


portfolio = CRUDPortfolio(Portfolio) 