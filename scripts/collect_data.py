"""Script for testing market data collection."""
import asyncio
import logging
from datetime import datetime
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.exchange.binance import BinanceExchange
from app.services.data.collector import MarketDataCollector
from app.db.session import async_session_maker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Trading pairs to collect data for
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
# Candlestick intervals
INTERVALS = ["1m", "5m", "15m", "1h", "4h", "1d"]


async def main():
    """Run market data collection."""
    # Create exchange client
    exchange = BinanceExchange()
    
    # Create database session
    async with async_session_maker() as session:
        # Create data collector
        collector = MarketDataCollector(
            exchange=exchange,
            session=session,
            symbols=SYMBOLS,
            intervals=INTERVALS
        )
        
        try:
            # Start collecting data
            await collector.start()
            
            # Run until interrupted
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Stopping data collection...")
            await collector.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass 