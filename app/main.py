"""Main application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import settings
from app.api.v1.api import api_router

import asyncio
import logging
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.strategy_service import StrategyService
from app.core.logging import trading_logger, error_logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Set up trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this in production
)

app.include_router(api_router, prefix=settings.API_V1_STR)

async def run_trading_bot(is_demo: bool = True):
    """Run the trading bot in demo or real mode."""
    db: Session = SessionLocal()
    try:
        service = StrategyService(db, is_demo=is_demo)
        
        while True:
            try:
                # Получаем активные стратегии
                strategies = service.get_active_strategies()
                
                # Выполняем каждую стратегию
                for strategy in strategies:
                    await service.execute_strategy(strategy)
                
                # Обновляем позиции
                await service.update_positions()
                
                # Ждем 1 минуту перед следующей итерацией
                await asyncio.sleep(60)
                
            except Exception as e:
                error_logger.error(f"Error in trading loop: {str(e)}")
                await asyncio.sleep(60)  # Ждем перед повторной попыткой
                
    except Exception as e:
        error_logger.error(f"Fatal error: {str(e)}")
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Trading Bot API"}


if __name__ == "__main__":
    # Запуск в демо-режиме
    asyncio.run(run_trading_bot(is_demo=True)) 