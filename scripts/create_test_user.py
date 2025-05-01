"""Script to create a test user."""
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from app.core.security import get_password_hash
from app.crud import crud_user
from app.db.session import SessionLocal
from app.schemas.user import UserCreate


def create_test_user():
    """Create a test user."""
    db = SessionLocal()
    try:
        user_in = UserCreate(
            email="test@example.com",
            password="test123",
            is_active=True,
            is_superuser=False,
        )
        user = crud_user.user.get_by_email(db, email=user_in.email)
        if not user:
            user_in.password = get_password_hash(user_in.password)
            user = crud_user.user.create(db, obj_in=user_in)
            print(f"Created test user: {user.email}")
        else:
            print(f"User already exists: {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user() 