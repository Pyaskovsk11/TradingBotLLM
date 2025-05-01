"""Main API router."""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, trading, portfolio

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])

# Import and include other routers here
# from .endpoints import users, items, etc.
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(items.router, prefix="/items", tags=["items"]) 