"""Database initialization module."""
import logging
from sqlalchemy.orm import Session
from app.db.session import engine
from app.models.base import Base

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize database with required tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise 