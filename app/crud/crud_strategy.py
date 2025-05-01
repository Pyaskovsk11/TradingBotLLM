from typing import List, Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.strategy import Strategy
from app.schemas.strategy import StrategyCreate, StrategyUpdate


class CRUDStrategy(CRUDBase[Strategy, StrategyCreate, StrategyUpdate]):
    def get_by_owner(
        self, db: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Strategy]:
        """Get strategies by owner with pagination."""
        return (
            db.query(self.model)
            .filter(Strategy.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_strategies(
        self, db: Session, *, owner_id: int
    ) -> List[Strategy]:
        """Get active strategies by owner."""
        return (
            db.query(self.model)
            .filter(Strategy.owner_id == owner_id, Strategy.is_active == True)
            .all()
        )


strategy = CRUDStrategy(Strategy) 