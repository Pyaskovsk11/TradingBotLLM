"""Database initialization script."""
from app.database import Base, engine
from app.models.signal import Signal

def init_db():
    """Initialize database and create all tables."""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.") 