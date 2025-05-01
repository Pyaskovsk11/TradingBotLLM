"""Trading signals generation module."""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.signal import Signal, SignalType, SignalStrength
from app.services.analysis.processor import MarketDataProcessor
from app.services.analysis.levels import LevelAnalyzer

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Service for generating trading signals."""

    def __init__(
        self,
        session: AsyncSession,
        data_processor: MarketDataProcessor,
        level_analyzer: LevelAnalyzer
    ):
        """Initialize signal generator.
        
        Args:
            session: Database session
            data_processor: Market data processor instance
            level_analyzer: Level analyzer instance
        """
        self.session = session
        self.data_processor = data_processor
        self.level_analyzer = level_analyzer

    async def generate_signals(
        self,
        symbol: str,
        interval: str
    ) -> List[Dict[str, Any]]:
        """Generate trading signals for a symbol.
        
        Args:
            symbol: Trading pair symbol
            interval: Candlestick interval
            
        Returns:
            List of trading signals
        """
        # Get market analysis
        analysis = await self.data_processor.analyze_market(
            symbol=symbol,
            interval=interval,
            lookback_periods=100
        )
        
        if not analysis:
            return []
        
        # Get nearest levels
        levels = await self.level_analyzer.get_nearest_levels(
            symbol=symbol,
            price=analysis['price']['close']
        )
        
        signals = []
        
        # Check for level-based signals
        level_signals = await self._check_level_signals(
            symbol=symbol,
            analysis=analysis,
            levels=levels
        )
        signals.extend(level_signals)
        
        # Check for trend signals
        trend_signals = await self._check_trend_signals(
            symbol=symbol,
            analysis=analysis
        )
        signals.extend(trend_signals)
        
        # Check for momentum signals
        momentum_signals = await self._check_momentum_signals(
            symbol=symbol,
            analysis=analysis
        )
        signals.extend(momentum_signals)
        
        # Check for volume signals
        volume_signals = await self._check_volume_signals(
            symbol=symbol,
            analysis=analysis
        )
        signals.extend(volume_signals)
        
        # Save signals to database
        await self._save_signals(signals)
        
        return signals

    async def _check_level_signals(
        self,
        symbol: str,
        analysis: Dict[str, Any],
        levels: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Check for level-based trading signals.
        
        Args:
            symbol: Trading pair symbol
            analysis: Market analysis data
            levels: Support and resistance levels
            
        Returns:
            List of level-based signals
        """
        signals = []
        current_price = analysis['price']['close']
        
        # Check support levels
        for support in levels['support']:
            price_diff = (current_price - support['price']) / support['price']
            
            if 0 <= price_diff <= 0.002:  # Price is testing support
                # Calculate signal strength based on level properties
                strength = self._calculate_signal_strength(
                    level_strength=support['strength'],
                    trend_strength=analysis['trend']['strength'],
                    volume_confirmation=support['volume_confirmation']
                )
                
                signals.append({
                    'symbol': symbol,
                    'type': SignalType.LEVEL_BOUNCE,
                    'strength': strength,
                    'price': current_price,
                    'timestamp': datetime.utcnow(),
                    'indicators': {
                        'level_price': support['price'],
                        'level_strength': support['strength'],
                        'trend_direction': analysis['trend']['direction'],
                        'trend_strength': analysis['trend']['strength'],
                        'volume_confirmation': support['volume_confirmation']
                    },
                    'description': (
                        f"Price bouncing off support at {support['price']:.2f} "
                        f"with {support['strength']:.2f} strength"
                    ),
                    'confidence': min(
                        support['strength'] * 
                        (1 + analysis['trend']['strength'] / 100) *
                        support['volume_confirmation'],
                        1.0
                    )
                })
        
        # Check resistance levels
        for resistance in levels['resistance']:
            price_diff = (resistance['price'] - current_price) / current_price
            
            if 0 <= price_diff <= 0.002:  # Price is testing resistance
                # Calculate signal strength
                strength = self._calculate_signal_strength(
                    level_strength=resistance['strength'],
                    trend_strength=analysis['trend']['strength'],
                    volume_confirmation=resistance['volume_confirmation']
                )
                
                signals.append({
                    'symbol': symbol,
                    'type': SignalType.LEVEL_BOUNCE,
                    'strength': strength,
                    'price': current_price,
                    'timestamp': datetime.utcnow(),
                    'indicators': {
                        'level_price': resistance['price'],
                        'level_strength': resistance['strength'],
                        'trend_direction': analysis['trend']['direction'],
                        'trend_strength': analysis['trend']['strength'],
                        'volume_confirmation': resistance['volume_confirmation']
                    },
                    'description': (
                        f"Price bouncing off resistance at {resistance['price']:.2f} "
                        f"with {resistance['strength']:.2f} strength"
                    ),
                    'confidence': min(
                        resistance['strength'] * 
                        (1 + analysis['trend']['strength'] / 100) *
                        resistance['volume_confirmation'],
                        1.0
                    )
                })
        
        return signals

    async def _check_trend_signals(
        self,
        symbol: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for trend-following signals.
        
        Args:
            symbol: Trading pair symbol
            analysis: Market analysis data
            
        Returns:
            List of trend signals
        """
        signals = []
        
        # Check for strong trend with momentum
        if (analysis['trend']['direction'] in ['strong_up', 'strong_down'] and
            analysis['trend']['strength'] > 25):
            
            # Calculate signal strength
            strength = self._calculate_signal_strength(
                trend_strength=analysis['trend']['strength'],
                momentum_confirmation=analysis['momentum']['rsi'],
                volume_confirmation=analysis['volume']['taker_buy'] / 
                                  analysis['volume']['total']
            )
            
            signals.append({
                'symbol': symbol,
                'type': SignalType.TREND_CONTINUATION,
                'strength': strength,
                'price': analysis['price']['close'],
                'timestamp': datetime.utcnow(),
                'indicators': {
                    'trend_direction': analysis['trend']['direction'],
                    'trend_strength': analysis['trend']['strength'],
                    'rsi': analysis['momentum']['rsi'],
                    'volume_ratio': analysis['volume']['taker_buy'] / 
                                  analysis['volume']['total']
                },
                'description': (
                    f"Strong {analysis['trend']['direction']} trend with "
                    f"ADX {analysis['trend']['strength']:.1f}"
                ),
                'confidence': min(
                    analysis['trend']['strength'] / 100 *
                    (1 + abs(50 - analysis['momentum']['rsi']) / 50),
                    1.0
                )
            })
        
        return signals

    async def _check_momentum_signals(
        self,
        symbol: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for momentum-based signals.
        
        Args:
            symbol: Trading pair symbol
            analysis: Market analysis data
            
        Returns:
            List of momentum signals
        """
        signals = []
        
        # Check for oversold/overbought conditions
        rsi = analysis['momentum']['rsi']
        stoch_k = analysis['momentum']['stoch_rsi_k']
        stoch_d = analysis['momentum']['stoch_rsi_d']
        williams_r = analysis['momentum']['williams_r']
        
        if (rsi < 30 and stoch_k < 20 and williams_r < -80):
            # Oversold condition
            strength = self._calculate_signal_strength(
                momentum_confirmation=abs(50 - rsi) / 50,
                volume_confirmation=analysis['volume']['taker_buy'] / 
                                  analysis['volume']['total']
            )
            
            signals.append({
                'symbol': symbol,
                'type': SignalType.MOMENTUM,
                'strength': strength,
                'price': analysis['price']['close'],
                'timestamp': datetime.utcnow(),
                'indicators': {
                    'rsi': rsi,
                    'stoch_rsi_k': stoch_k,
                    'stoch_rsi_d': stoch_d,
                    'williams_r': williams_r
                },
                'description': (
                    f"Oversold conditions: RSI={rsi:.1f}, "
                    f"Stoch RSI={stoch_k:.1f}, Williams %R={williams_r:.1f}"
                ),
                'confidence': min(
                    (30 - rsi) / 30 *
                    (20 - stoch_k) / 20 *
                    (abs(-80 - williams_r) / 20),
                    1.0
                )
            })
            
        elif (rsi > 70 and stoch_k > 80 and williams_r > -20):
            # Overbought condition
            strength = self._calculate_signal_strength(
                momentum_confirmation=abs(50 - rsi) / 50,
                volume_confirmation=analysis['volume']['taker_sell'] / 
                                  analysis['volume']['total']
            )
            
            signals.append({
                'symbol': symbol,
                'type': SignalType.MOMENTUM,
                'strength': strength,
                'price': analysis['price']['close'],
                'timestamp': datetime.utcnow(),
                'indicators': {
                    'rsi': rsi,
                    'stoch_rsi_k': stoch_k,
                    'stoch_rsi_d': stoch_d,
                    'williams_r': williams_r
                },
                'description': (
                    f"Overbought conditions: RSI={rsi:.1f}, "
                    f"Stoch RSI={stoch_k:.1f}, Williams %R={williams_r:.1f}"
                ),
                'confidence': min(
                    (rsi - 70) / 30 *
                    (stoch_k - 80) / 20 *
                    (abs(-20 - williams_r) / 20),
                    1.0
                )
            })
        
        return signals

    async def _check_volume_signals(
        self,
        symbol: str,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for volume-based signals.
        
        Args:
            symbol: Trading pair symbol
            analysis: Market analysis data
            
        Returns:
            List of volume signals
        """
        signals = []
        
        # Check for volume spikes
        current_volume = analysis['volume']['total']
        avg_volume = sum(p['volume'] for p in analysis['volume']['profile']) / len(analysis['volume']['profile'])
        volume_ratio = current_volume / avg_volume
        
        if volume_ratio > 2.0:  # Volume spike (2x average)
            # Calculate signal strength
            strength = self._calculate_signal_strength(
                volume_confirmation=volume_ratio,
                trend_strength=analysis['trend']['strength']
            )
            
            signals.append({
                'symbol': symbol,
                'type': SignalType.VOLUME_SPIKE,
                'strength': strength,
                'price': analysis['price']['close'],
                'timestamp': datetime.utcnow(),
                'indicators': {
                    'volume_ratio': volume_ratio,
                    'trend_direction': analysis['trend']['direction'],
                    'price_change': analysis['price']['change']
                },
                'description': (
                    f"Volume spike {volume_ratio:.1f}x average with "
                    f"{analysis['price']['change']:.1f}% price change"
                ),
                'confidence': min(
                    volume_ratio / 5 *  # Normalize by 5x volume
                    (1 + abs(analysis['price']['change']) / 10),  # Price change impact
                    1.0
                )
            })
        
        return signals

    @staticmethod
    def _calculate_signal_strength(
        level_strength: float = 0.0,
        trend_strength: float = 0.0,
        momentum_confirmation: float = 0.0,
        volume_confirmation: float = 0.0
    ) -> SignalStrength:
        """Calculate signal strength based on various factors.
        
        Args:
            level_strength: Strength of price level (0-1)
            trend_strength: Strength of trend (ADX 0-100)
            momentum_confirmation: Momentum indicator confirmation (0-1)
            volume_confirmation: Volume confirmation (0-1)
            
        Returns:
            Signal strength enum value
        """
        # Normalize trend strength to 0-1
        trend_strength = min(trend_strength / 100, 1.0)
        
        # Calculate composite strength
        factors = []
        if level_strength > 0:
            factors.append(level_strength)
        if trend_strength > 0:
            factors.append(trend_strength)
        if momentum_confirmation > 0:
            factors.append(momentum_confirmation)
        if volume_confirmation > 0:
            factors.append(volume_confirmation)
        
        if not factors:
            return SignalStrength.WEAK
            
        strength = sum(factors) / len(factors)
        
        if strength >= 0.7:
            return SignalStrength.STRONG
        elif strength >= 0.4:
            return SignalStrength.MEDIUM
        else:
            return SignalStrength.WEAK

    async def _save_signals(self, signals: List[Dict[str, Any]]):
        """Save signals to database.
        
        Args:
            signals: List of signals to save
        """
        for signal_data in signals:
            signal = Signal(
                symbol=signal_data['symbol'],
                type=signal_data['type'],
                strength=signal_data['strength'],
                price=signal_data['price'],
                timestamp=signal_data['timestamp'],
                indicators=signal_data['indicators'],
                description=signal_data['description'],
                confidence=signal_data['confidence'],
                is_valid=True
            )
            self.session.add(signal)
        
        await self.session.commit() 