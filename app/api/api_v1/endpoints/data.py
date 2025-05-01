"""Data endpoints."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.data.binance_service import BinanceService
from app.schemas.candle import Candle
from app.schemas.symbol import Symbol

router = APIRouter()
binance_service = BinanceService()


@router.get("/symbols", response_model=List[Symbol])
def get_symbols(
    current_user = Depends(deps.get_current_active_user),
) -> List[Symbol]:
    """Get available trading symbols.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List[Symbol]: List of available symbols
    """
    try:
        exchange_info = binance_service.client.get_exchange_info()
        return [
            Symbol(
                symbol=symbol['symbol'],
                base_asset=symbol['baseAsset'],
                quote_asset=symbol['quoteAsset']
            )
            for symbol in exchange_info['symbols']
            if symbol['status'] == 'TRADING'
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting symbols: {str(e)}"
        )


@router.get("/candles/{symbol}", response_model=List[Candle])
def get_candles(
    symbol: str,
    interval: str = "1h",
    limit: int = 100,
    current_user = Depends(deps.get_current_active_user),
) -> List[Candle]:
    """Get candlestick data for a symbol.
    
    Args:
        symbol: Trading pair symbol (e.g. BTCUSDT)
        interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
        limit: Number of candles to return
        current_user: Current authenticated user
        
    Returns:
        List[Candle]: List of candles
    """
    try:
        return binance_service.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting candles: {str(e)}"
        )
