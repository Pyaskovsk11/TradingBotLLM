from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.trade import Trade
from app.schemas.trade import TradeCreate, TradeUpdate


class CRUDTrade(CRUDBase[Trade, TradeCreate, TradeUpdate]):
    def get_by_portfolio(
        self, db: Session, *, portfolio_id: int, skip: int = 0, limit: int = 100
    ) -> List[Trade]:
        """Get trades by portfolio with pagination."""
        return (
            db.query(self.model)
            .filter(Trade.portfolio_id == portfolio_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_symbol(
        self, db: Session, *, symbol: str, portfolio_id: int, skip: int = 0, limit: int = 100
    ) -> List[Trade]:
        """Get trades by symbol and portfolio with pagination."""
        return (
            db.query(self.model)
            .filter(Trade.symbol == symbol, Trade.portfolio_id == portfolio_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_time_range(
        self,
        db: Session,
        *,
        portfolio_id: int,
        start_time: datetime,
        end_time: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Trade]:
        """Get trades by time range with pagination."""
        return (
            db.query(self.model)
            .filter(
                Trade.portfolio_id == portfolio_id,
                Trade.timestamp >= start_time,
                Trade.timestamp <= end_time
            )
            .order_by(Trade.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
        self, db: Session, *, portfolio_id: int, trade_type: str, skip: int = 0, limit: int = 100
    ) -> List[Trade]:
        """Get trades by type with pagination."""
        return (
            db.query(self.model)
            .filter(Trade.portfolio_id == portfolio_id, Trade.type == trade_type)
            .order_by(Trade.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


trade = CRUDTrade(Trade) 