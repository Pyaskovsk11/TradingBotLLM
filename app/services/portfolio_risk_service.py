"""Portfolio risk analysis service module."""
from typing import Dict, List
from decimal import Decimal
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from binance.client import Client

from app.core.logging import risk_logger
from app.models.position import Position
from app.core.config import settings


class PortfolioRiskService:
    """Service for portfolio risk analysis and management."""

    def __init__(self, db: Session):
        """Initialize portfolio risk service."""
        self.db = db
        self.client = Client(settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET)
        self.max_portfolio_risk = Decimal("0.05")  # 5% maximum portfolio risk
        self.correlation_threshold = 0.7  # Correlation threshold for risk warning

    def analyze_portfolio_risk(self, positions: List[Position]) -> Dict[str, any]:
        """
        Analyze portfolio risk metrics.
        
        Args:
            positions: List of open positions
            
        Returns:
            Dictionary with risk metrics
        """
        try:
            if not positions:
                return {
                    "total_exposure": Decimal("0"),
                    "portfolio_var": Decimal("0"),
                    "risk_level": "LOW",
                    "diversification_score": Decimal("0"),
                    "correlation_warning": False
                }

            # Calculate basic metrics
            total_exposure = sum(pos.current_value for pos in positions)
            portfolio_weights = [
                pos.current_value / total_exposure for pos in positions
            ]

            # Get historical data for VaR calculation
            historical_data = self._get_historical_data(positions)
            
            # Calculate Value at Risk (VaR)
            portfolio_var = self._calculate_var(historical_data, portfolio_weights)
            
            # Calculate correlation matrix
            correlation_matrix = historical_data.corr()
            high_correlation = self._check_high_correlation(correlation_matrix)
            
            # Calculate diversification score
            diversification_score = self._calculate_diversification_score(
                correlation_matrix, portfolio_weights
            )

            # Determine risk level
            risk_level = self._determine_risk_level(
                portfolio_var, diversification_score, len(positions)
            )

            risk_metrics = {
                "total_exposure": total_exposure,
                "portfolio_var": Decimal(str(portfolio_var)),
                "risk_level": risk_level,
                "diversification_score": Decimal(str(diversification_score)),
                "correlation_warning": high_correlation
            }

            risk_logger.info(
                "Portfolio risk analysis completed",
                extra={
                    "metrics": {k: str(v) for k, v in risk_metrics.items()},
                    "positions_count": len(positions)
                }
            )

            return risk_metrics

        except Exception as e:
            risk_logger.error(
                f"Error analyzing portfolio risk: {str(e)}",
                extra={"positions_count": len(positions)}
            )
            return {}

    def _get_historical_data(self, positions: List[Position]) -> pd.DataFrame:
        """Get historical price data for all positions."""
        try:
            # Get last 30 days of data
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=30)
            
            data_frames = {}
            for position in positions:
                klines = self.client.get_historical_klines(
                    position.symbol,
                    Client.KLINE_INTERVAL_1DAY,
                    start_str=str(int(start_time.timestamp() * 1000)),
                    end_str=str(int(end_time.timestamp() * 1000))
                )
                
                df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
                df['close'] = pd.to_numeric(df['close'])
                data_frames[position.symbol] = df['close']
            
            return pd.DataFrame(data_frames)

        except Exception as e:
            risk_logger.error(f"Error getting historical data: {str(e)}")
            return pd.DataFrame()

    def _calculate_var(self, historical_data: pd.DataFrame, weights: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk using historical simulation."""
        try:
            # Calculate daily returns
            returns = historical_data.pct_change().dropna()
            
            # Calculate portfolio returns
            portfolio_returns = returns.dot(weights)
            
            # Calculate VaR
            var = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            return abs(var)

        except Exception as e:
            risk_logger.error(f"Error calculating VaR: {str(e)}")
            return 0.0

    def _check_high_correlation(self, correlation_matrix: pd.DataFrame) -> bool:
        """Check for high correlation between assets."""
        try:
            # Get upper triangle of correlation matrix
            upper_triangle = correlation_matrix.where(
                np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
            )
            
            # Check if any correlation exceeds threshold
            return (upper_triangle.abs() > self.correlation_threshold).any().any()

        except Exception as e:
            risk_logger.error(f"Error checking correlations: {str(e)}")
            return False

    def _calculate_diversification_score(self, correlation_matrix: pd.DataFrame, weights: List[float]) -> float:
        """Calculate portfolio diversification score."""
        try:
            # Convert weights to numpy array
            weights = np.array(weights)
            
            # Calculate weighted correlation
            weighted_corr = np.dot(np.dot(weights, correlation_matrix), weights)
            
            # Convert to diversification score (1 - weighted correlation)
            # Higher score means better diversification
            return 1 - weighted_corr

        except Exception as e:
            risk_logger.error(f"Error calculating diversification score: {str(e)}")
            return 0.0

    def _determine_risk_level(self, var: float, diversification_score: float, position_count: int) -> str:
        """Determine overall portfolio risk level."""
        try:
            # Base risk on VaR
            if var > 0.1:  # More than 10% VaR
                risk_level = "HIGH"
            elif var > 0.05:  # 5-10% VaR
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            # Adjust for diversification
            if diversification_score < 0.3 and position_count > 1:
                risk_level = "HIGH"  # Poor diversification
            elif diversification_score > 0.7 and risk_level == "HIGH":
                risk_level = "MEDIUM"  # Good diversification can reduce high risk

            return risk_level

        except Exception as e:
            risk_logger.error(f"Error determining risk level: {str(e)}")
            return "UNKNOWN" 