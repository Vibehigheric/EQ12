#!/usr/bin/env python3
"""
EQ12 Advanced Bankroll Optimizer - Multi-Strategy Portfolio Management
=====================================================================

Advanced bankroll management system beyond Kelly Criterion:
- Fractional Kelly with correlation adjustments
- Portfolio theory applied to sports betting
- Optimal f calculations for maximum growth
- Risk parity and volatility targeting
- Multi-timeframe bankroll allocation
- Integration with existing EdgeGod system

Features:
- Portfolio-based bankroll allocation across multiple bets
- Correlation-adjusted position sizing
- Dynamic risk management with volatility targeting
- Multi-strategy allocation (Kelly, Optimal F, Fixed Fractional)
- Real-time bankroll monitoring and adjustments
- Advanced risk metrics (Sharpe, Sortino, Maximum Drawdown)

Author: EQ12 Development Team
Date: October 6, 2025
Version: 1.0.0
"""

import asyncio
import json
import logging
import math
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize

# EQ12 Integration
try:
    from eq12_advanced_correlation_engine import EQ12AdvancedCorrelationEngine

    EQ12_CORRELATION = True
except ImportError:
    EQ12_CORRELATION = False
    print("⚠️ Correlation engine not available - using basic Kelly")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/bankroll_optimizer.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12BankrollOptimizer")


class SizingStrategy(Enum):
    """Available position sizing strategies"""

    KELLY = "kelly"
    FRACTIONAL_KELLY = "fractional_kelly"
    OPTIMAL_F = "optimal_f"
    RISK_PARITY = "risk_parity"
    VOLATILITY_TARGET = "volatility_target"
    FIXED_FRACTIONAL = "fixed_fractional"


@dataclass
class BettingPosition:
    """Represents a betting position in the portfolio"""

    bet_id: str
    description: str
    odds: float
    win_probability: float
    stake: float
    expected_value: float
    kelly_fraction: float
    risk_score: float
    correlation_group: str | None = None
    entry_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: str = "open"  # open, won, lost, void

    @property
    def expected_return(self) -> float:
        """Expected return of the position"""
        return self.expected_value / 100.0  # Convert percentage to decimal

    @property
    def potential_loss(self) -> float:
        """Maximum potential loss"""
        return -self.stake

    @property
    def potential_win(self) -> float:
        """Potential win amount"""
        if self.odds > 0:
            return self.stake * (self.odds / 100)
        else:
            return self.stake * (100 / abs(self.odds))


@dataclass
class PortfolioMetrics:
    """Portfolio performance and risk metrics"""

    total_value: float
    allocated_capital: float
    available_capital: float
    expected_return: float
    portfolio_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float

    correlation_risk: float = 0.0
    concentration_risk: float = 0.0
    total_positions: int = 0
    active_positions: int = 0


class EQ12AdvancedBankrollOptimizer:
    """
    Advanced bankroll management system with portfolio optimization
    """

    def __init__(self, initial_bankroll: float = 10000.0, eq12_root: str = "C:/EQ12"):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.eq12_root = Path(eq12_root)
        self.db_path = self.eq12_root / "logs" / "bankroll_optimizer.db"

        # Portfolio management
        self.positions: list[BettingPosition] = []
        self.closed_positions: list[BettingPosition] = []
        self.correlation_matrix = np.eye(0)  # Will be expanded as positions are added

        # Risk parameters
        self.max_portfolio_risk = 0.15  # Maximum 15% of bankroll at risk
        self.max_single_position = 0.05  # Maximum 5% per position
        self.target_volatility = 0.20  # Target 20% annual volatility
        self.correlation_threshold = 0.3  # Reduce sizing if correlation > 30%

        # Strategy parameters
        self.default_strategy = SizingStrategy.FRACTIONAL_KELLY
        self.kelly_fraction = 0.25  # Quarter Kelly for safety
        self.risk_free_rate = 0.05  # 5% risk-free rate for Sharpe calculation

        # Initialize components
        self._initialize_database()

        if EQ12_CORRELATION:
            self.correlation_engine = EQ12AdvancedCorrelationEngine()

        logger.info(
            f"💰 EQ12 Advanced Bankroll Optimizer initialized with ${initial_bankroll:,.2f}"
        )

    def _initialize_database(self):
        """Initialize SQLite database for bankroll tracking"""
        self.db_path.parent.mkdir(exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bet_id TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    odds REAL NOT NULL,
                    win_probability REAL NOT NULL,
                    stake REAL NOT NULL,
                    expected_value REAL NOT NULL,
                    kelly_fraction REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    correlation_group TEXT,
                    entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    exit_time DATETIME,
                    status TEXT DEFAULT 'open',
                    actual_return REAL,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS bankroll_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    bankroll_value REAL NOT NULL,
                    allocated_capital REAL NOT NULL,
                    available_capital REAL NOT NULL,
                    total_positions INTEGER NOT NULL,
                    portfolio_risk REAL NOT NULL,
                    expected_return REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS portfolio_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    calculation_date DATE UNIQUE NOT NULL,
                    total_value REAL NOT NULL,
                    allocated_capital REAL NOT NULL,
                    available_capital REAL NOT NULL,
                    expected_return REAL NOT NULL,
                    portfolio_volatility REAL NOT NULL,
                    sharpe_ratio REAL NOT NULL,
                    max_drawdown REAL NOT NULL,
                    win_rate REAL NOT NULL,
                    profit_factor REAL NOT NULL,
                    correlation_risk REAL NOT NULL,
                    concentration_risk REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
                CREATE INDEX IF NOT EXISTS idx_positions_entry_time ON positions(entry_time);
                CREATE INDEX IF NOT EXISTS idx_bankroll_timestamp ON bankroll_history(timestamp);
            """
            )

        logger.info("💾 Bankroll optimizer database initialized")

    def calculate_kelly_criterion(self, win_prob: float, odds: float) -> float:
        """
        Calculate Kelly Criterion fraction
        """
        if win_prob <= 0 or win_prob >= 1:
            return 0.0

        # Convert American odds to decimal
        decimal_odds = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1

        # Kelly formula: f = (bp - q) / b
        b = decimal_odds - 1  # Net odds
        p = win_prob
        q = 1 - p

        kelly_fraction = (b * p - q) / b

        return max(0.0, kelly_fraction)

    def calculate_optimal_f(self, returns_history: list[float]) -> float:
        """
        Calculate Optimal F for maximum geometric growth
        """
        if not returns_history or len(returns_history) < 10:
            return 0.02  # Default 2% if insufficient history

        def objective(f):
            if f <= 0:
                return -float("inf")

            geometric_mean = 1.0
            for ret in returns_history:
                new_value = 1 + (f * ret)
                if new_value <= 0:
                    return -float("inf")
                geometric_mean *= new_value

            return -(geometric_mean ** (1.0 / len(returns_history)) - 1)

        # Find optimal f using optimization
        result = optimize.minimize_scalar(objective, bounds=(0.001, 0.5), method="bounded")

        return min(result.x, 0.25) if result.success else 0.02

    async def calculate_correlation_adjusted_sizing(self, new_position: BettingPosition) -> float:
        """
        Calculate position size adjusted for correlations with existing positions
        """
        if not self.positions or not EQ12_CORRELATION:
            return new_position.kelly_fraction * self.kelly_fraction

        # Create correlation matrix for all positions including new one
        all_positions = [*self.positions, new_position]
        n = len(all_positions)
        correlation_matrix = np.eye(n)

        # Calculate correlations between positions
        for i in range(n):
            for j in range(i + 1, n):
                # Use correlation engine to get correlation
                try:
                    if hasattr(self, "correlation_engine"):
                        # Mock correlation calculation - replace with actual correlation data
                        correlation = await self._get_position_correlation(
                            all_positions[i], all_positions[j]
                        )
                        correlation_matrix[i, j] = correlation
                        correlation_matrix[j, i] = correlation
                except Exception as e:
                    logger.warning(f"⚠️ Could not calculate correlation: {e}")

        # Calculate portfolio variance with correlations
        weights = np.array([pos.stake / self.current_bankroll for pos in all_positions])
        volatilities = np.array([self._estimate_position_volatility(pos) for pos in all_positions])

        portfolio_variance = np.dot(
            weights, np.dot(correlation_matrix * np.outer(volatilities, volatilities), weights)
        )
        portfolio_volatility = np.sqrt(portfolio_variance)

        # Adjust sizing based on correlation risk
        correlation_adjustment = 1.0
        if portfolio_volatility > self.target_volatility:
            correlation_adjustment = self.target_volatility / portfolio_volatility

        # Apply correlation penalty for highly correlated positions
        max_correlation = np.max(correlation_matrix[:-1, -1]) if n > 1 else 0.0
        if max_correlation > self.correlation_threshold:
            correlation_penalty = 1.0 - (max_correlation - self.correlation_threshold)
            correlation_adjustment *= correlation_penalty

        base_sizing = new_position.kelly_fraction * self.kelly_fraction
        return base_sizing * correlation_adjustment

    async def _get_position_correlation(
        self, pos1: BettingPosition, pos2: BettingPosition
    ) -> float:
        """
        Get correlation between two positions
        """
        # This is a simplified correlation estimation
        # In production, this would use historical data and the correlation engine

        # Same sport/game correlations
        if pos1.correlation_group and pos1.correlation_group == pos2.correlation_group:
            return 0.6  # High correlation for same game props

        # Different sports
        return 0.1  # Low base correlation

    def _estimate_position_volatility(self, position: BettingPosition) -> float:
        """
        Estimate volatility of a betting position
        """
        # Simple volatility estimation based on odds and probability
        win_prob = position.win_probability

        win_return = position.odds / 100 if position.odds > 0 else 100 / abs(position.odds)

        expected_return = win_prob * win_return - (1 - win_prob)
        variance = (
            win_prob * (win_return - expected_return) ** 2
            + (1 - win_prob) * (-1 - expected_return) ** 2
        )

        return math.sqrt(variance)

    async def optimize_position_size(
        self,
        bet_description: str,
        odds: float,
        win_probability: float,
        expected_value: float,
        strategy: SizingStrategy = None,
        correlation_group: str | None = None,
    ) -> dict[str, Any]:
        """
        Optimize position size using selected strategy
        """
        if strategy is None:
            strategy = self.default_strategy

        # Calculate base Kelly fraction
        kelly_fraction = self.calculate_kelly_criterion(win_probability, odds)

        # Create position object for analysis
        position = BettingPosition(
            bet_id=f"pos_{int(datetime.now().timestamp())}",
            description=bet_description,
            odds=odds,
            win_probability=win_probability,
            stake=0.0,  # Will be calculated
            expected_value=expected_value,
            kelly_fraction=kelly_fraction,
            risk_score=self._calculate_risk_score(odds, win_probability),
            correlation_group=correlation_group,
        )

        # Apply sizing strategy
        if strategy == SizingStrategy.KELLY:
            sizing_fraction = kelly_fraction
        elif strategy == SizingStrategy.FRACTIONAL_KELLY:
            sizing_fraction = kelly_fraction * self.kelly_fraction
        elif strategy == SizingStrategy.OPTIMAL_F:
            # Use historical returns to calculate optimal F
            historical_returns = self._get_historical_returns()
            optimal_f = self.calculate_optimal_f(historical_returns)
            sizing_fraction = optimal_f
        elif strategy == SizingStrategy.RISK_PARITY:
            sizing_fraction = await self._calculate_risk_parity_sizing(position)
        elif strategy == SizingStrategy.VOLATILITY_TARGET:
            sizing_fraction = await self._calculate_volatility_target_sizing(position)
        elif strategy == SizingStrategy.FIXED_FRACTIONAL:
            sizing_fraction = 0.02  # Fixed 2%
        else:
            sizing_fraction = kelly_fraction * self.kelly_fraction

        # Apply correlation adjustment
        if EQ12_CORRELATION and self.positions:
            correlation_adjusted_sizing = await self.calculate_correlation_adjusted_sizing(position)
            sizing_fraction = min(sizing_fraction, correlation_adjusted_sizing)

        # Apply risk limits
        sizing_fraction = min(sizing_fraction, self.max_single_position)

        # Calculate final stake
        stake = self.current_bankroll * sizing_fraction

        # Check portfolio risk limits
        total_allocated = sum(pos.stake for pos in self.positions) + stake
        if total_allocated > self.current_bankroll * self.max_portfolio_risk:
            # Reduce stake to stay within portfolio risk limit
            max_additional_stake = (self.current_bankroll * self.max_portfolio_risk) - sum(
                pos.stake for pos in self.positions
            )
            stake = max(0, max_additional_stake)
            sizing_fraction = stake / self.current_bankroll

        position.stake = stake

        return {
            "recommended_stake": stake,
            "sizing_fraction": sizing_fraction,
            "kelly_fraction": kelly_fraction,
            "strategy_used": strategy.value,
            "correlation_adjustment": (
                sizing_fraction / (kelly_fraction * self.kelly_fraction)
                if kelly_fraction > 0
                else 1.0
            ),
            "risk_score": position.risk_score,
            "expected_return": position.expected_return * stake,
            "max_loss": stake,
            "position_details": position,
        }

    def _calculate_risk_score(self, odds: float, win_probability: float) -> float:
        """
        Calculate risk score for a position (0-1 scale)
        """
        # Higher risk for extreme odds or probabilities
        odds_risk = min(abs(odds) / 1000, 1.0) if odds != 0 else 0.5

        # Higher risk for extreme probabilities
        prob_risk = abs(win_probability - 0.5) * 2

        # Combined risk score
        return (odds_risk + prob_risk) / 2

    async def _calculate_risk_parity_sizing(self, position: BettingPosition) -> float:
        """
        Calculate position size using risk parity approach
        """
        position_volatility = self._estimate_position_volatility(position)

        if not self.positions:
            # First position gets base allocation
            return self.max_single_position

        # Calculate average volatility of existing positions
        avg_volatility = np.mean(
            [self._estimate_position_volatility(pos) for pos in self.positions]
        )

        # Size inversely proportional to volatility
        risk_parity_fraction = (avg_volatility / position_volatility) * self.max_single_position

        return min(risk_parity_fraction, self.max_single_position)

    async def _calculate_volatility_target_sizing(self, position: BettingPosition) -> float:
        """
        Calculate position size to target specific volatility
        """
        position_volatility = self._estimate_position_volatility(position)

        if position_volatility <= 0:
            return 0.0

        # Size to contribute target volatility to portfolio
        target_contribution = (
            self.target_volatility / 10
        )  # Each position contributes 1/10 of target
        sizing_fraction = target_contribution / position_volatility

        return min(sizing_fraction, self.max_single_position)

    def _get_historical_returns(self) -> list[float]:
        """
        Get historical returns for optimal F calculation
        """
        # Get returns from closed positions
        returns = []
        for pos in self.closed_positions:
            if pos.status in ["won", "lost"]:
                ret = pos.potential_win / pos.stake if pos.status == "won" else -1.0
                returns.append(ret)

        # If insufficient history, use simulated returns based on typical betting outcomes
        if len(returns) < 10:
            # Simulate typical betting returns (55% win rate, average odds +100/-110)
            np.random.seed(42)
            for _ in range(50):
                if np.random.random() < 0.55:  # Win
                    returns.append(np.random.uniform(0.8, 1.2))  # 80-120% return
                else:  # Loss
                    returns.append(-1.0)

        return returns

    def add_position(self, position: BettingPosition) -> bool:
        """
        Add a new position to the portfolio
        """
        try:
            # Check if position already exists
            if any(pos.bet_id == position.bet_id for pos in self.positions):
                logger.warning(f"⚠️ Position {position.bet_id} already exists")
                return False

            # Add position
            self.positions.append(position)

            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO positions (
                        bet_id, description, odds, win_probability, stake,
                        expected_value, kelly_fraction, risk_score, correlation_group
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        position.bet_id,
                        position.description,
                        position.odds,
                        position.win_probability,
                        position.stake,
                        position.expected_value,
                        position.kelly_fraction,
                        position.risk_score,
                        position.correlation_group,
                    ),
                )

            # Update bankroll tracking
            self._update_bankroll_history()

            logger.info(f"✅ Added position: {position.description} - Stake: ${position.stake:.2f}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to add position: {e}")
            return False

    def close_position(self, bet_id: str, outcome: str, actual_return: float | None = None) -> bool:
        """
        Close a position and record the outcome
        """
        try:
            # Find position
            position = None
            for i, pos in enumerate(self.positions):
                if pos.bet_id == bet_id:
                    position = self.positions.pop(i)
                    break

            if not position:
                logger.warning(f"⚠️ Position {bet_id} not found")
                return False

            # Update position status
            position.status = outcome

            # Calculate actual return if not provided
            if actual_return is None:
                if outcome == "won":
                    actual_return = position.potential_win
                elif outcome == "lost":
                    actual_return = position.potential_loss
                else:  # void
                    actual_return = 0.0

            # Update bankroll
            self.current_bankroll += actual_return

            # Move to closed positions
            self.closed_positions.append(position)

            # Update database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE positions
                    SET status = ?, exit_time = CURRENT_TIMESTAMP, actual_return = ?
                    WHERE bet_id = ?
                """,
                    (outcome, actual_return, bet_id),
                )

            # Update bankroll history
            self._update_bankroll_history()

            logger.info(
                f"✅ Closed position: {position.description} - Outcome: {outcome} - Return: ${actual_return:.2f}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to close position: {e}")
            return False

    def _update_bankroll_history(self):
        """Update bankroll history in database"""
        try:
            allocated_capital = sum(pos.stake for pos in self.positions)
            available_capital = self.current_bankroll - allocated_capital

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO bankroll_history (
                        bankroll_value, allocated_capital, available_capital,
                        total_positions, portfolio_risk, expected_return
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        self.current_bankroll,
                        allocated_capital,
                        available_capital,
                        len(self.positions),
                        allocated_capital / self.current_bankroll,
                        sum(pos.expected_return * pos.stake for pos in self.positions),
                    ),
                )
        except Exception as e:
            logger.error(f"❌ Failed to update bankroll history: {e}")

    def calculate_portfolio_metrics(self) -> PortfolioMetrics:
        """
        Calculate comprehensive portfolio metrics
        """
        # Basic portfolio values
        allocated_capital = sum(pos.stake for pos in self.positions)
        available_capital = self.current_bankroll - allocated_capital

        # Expected return
        expected_return = (
            sum(pos.expected_return * pos.stake for pos in self.positions) / self.current_bankroll
            if self.current_bankroll > 0
            else 0.0
        )

        # Portfolio volatility (simplified)
        if self.positions:
            position_volatilities = [
                self._estimate_position_volatility(pos) * pos.stake / self.current_bankroll
                for pos in self.positions
            ]
            portfolio_volatility = np.sqrt(sum(vol**2 for vol in position_volatilities))
        else:
            portfolio_volatility = 0.0

        # Performance metrics from closed positions
        if self.closed_positions:
            returns = []
            wins = 0
            losses = 0
            total_win_amount = 0
            total_loss_amount = 0

            for pos in self.closed_positions:
                if pos.status == "won":
                    wins += 1
                    return_pct = pos.potential_win / pos.stake
                    returns.append(return_pct)
                    total_win_amount += pos.potential_win
                elif pos.status == "lost":
                    losses += 1
                    returns.append(-1.0)
                    total_loss_amount += pos.stake

            win_rate = wins / len(self.closed_positions) if self.closed_positions else 0.0
            avg_win = total_win_amount / wins if wins > 0 else 0.0
            avg_loss = total_loss_amount / losses if losses > 0 else 0.0
            profit_factor = (
                total_win_amount / total_loss_amount if total_loss_amount > 0 else float("inf")
            )

            # Sharpe ratio
            if returns:
                avg_return = np.mean(returns)
                return_std = np.std(returns) if len(returns) > 1 else 0.1
                sharpe_ratio = (
                    (avg_return - self.risk_free_rate) / return_std if return_std > 0 else 0.0
                )
            else:
                sharpe_ratio = 0.0

            # Maximum drawdown (simplified)
            cumulative_returns = np.cumprod([1 + r for r in returns])
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdowns = (cumulative_returns - running_max) / running_max
            max_drawdown = abs(np.min(drawdowns)) if len(drawdowns) > 0 else 0.0
        else:
            win_rate = avg_win = avg_loss = profit_factor = sharpe_ratio = max_drawdown = 0.0

        # Risk metrics
        correlation_risk = self._calculate_correlation_risk()
        concentration_risk = self._calculate_concentration_risk()

        return PortfolioMetrics(
            total_value=self.current_bankroll,
            allocated_capital=allocated_capital,
            available_capital=available_capital,
            expected_return=expected_return,
            portfolio_volatility=portfolio_volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            correlation_risk=correlation_risk,
            concentration_risk=concentration_risk,
            total_positions=len(self.positions) + len(self.closed_positions),
            active_positions=len(self.positions),
        )

    def _calculate_correlation_risk(self) -> float:
        """
        Calculate portfolio correlation risk
        """
        if len(self.positions) < 2:
            return 0.0

        # Count positions in same correlation groups
        correlation_groups = {}
        for pos in self.positions:
            if pos.correlation_group:
                correlation_groups[pos.correlation_group] = (
                    correlation_groups.get(pos.correlation_group, 0) + pos.stake
                )

        # Calculate concentration in correlated bets
        total_allocated = sum(pos.stake for pos in self.positions)
        if total_allocated == 0:
            return 0.0

        max_group_allocation = max(correlation_groups.values()) if correlation_groups else 0
        correlation_risk = max_group_allocation / total_allocated

        return correlation_risk

    def _calculate_concentration_risk(self) -> float:
        """
        Calculate position concentration risk (Herfindahl-Hirschman Index)
        """
        if not self.positions:
            return 0.0

        total_allocated = sum(pos.stake for pos in self.positions)
        if total_allocated == 0:
            return 0.0

        # Calculate HHI
        hhi = sum((pos.stake / total_allocated) ** 2 for pos in self.positions)

        # Normalize to 0-1 scale (1 = maximum concentration, 0 = perfect diversification)
        n_positions = len(self.positions)
        min_hhi = 1.0 / n_positions  # Perfect diversification
        concentration_risk = (hhi - min_hhi) / (1.0 - min_hhi) if n_positions > 1 else 0.0

        return max(0.0, concentration_risk)

    def generate_portfolio_report(self) -> dict[str, Any]:
        """
        Generate comprehensive portfolio report
        """
        metrics = self.calculate_portfolio_metrics()

        # Position breakdown
        positions_by_sport = {}
        positions_by_risk = {"low": 0, "medium": 0, "high": 0}

        for pos in self.positions:
            # Group by sport (simplified)
            sport = pos.correlation_group or "other"
            positions_by_sport[sport] = positions_by_sport.get(sport, 0) + pos.stake

            # Group by risk level
            if pos.risk_score < 0.3:
                positions_by_risk["low"] += pos.stake
            elif pos.risk_score < 0.7:
                positions_by_risk["medium"] += pos.stake
            else:
                positions_by_risk["high"] += pos.stake

        return {
            "report_timestamp": datetime.now(UTC).isoformat(),
            "bankroll_summary": {
                "current_bankroll": self.current_bankroll,
                "initial_bankroll": self.initial_bankroll,
                "total_return": ((self.current_bankroll / self.initial_bankroll) - 1) * 100,
                "allocated_capital": metrics.allocated_capital,
                "available_capital": metrics.available_capital,
                "allocation_percentage": (metrics.allocated_capital / self.current_bankroll) * 100,
            },
            "performance_metrics": {
                "expected_return": metrics.expected_return * 100,
                "portfolio_volatility": metrics.portfolio_volatility * 100,
                "sharpe_ratio": metrics.sharpe_ratio,
                "max_drawdown": metrics.max_drawdown * 100,
                "win_rate": metrics.win_rate * 100,
                "profit_factor": metrics.profit_factor,
            },
            "risk_metrics": {
                "correlation_risk": metrics.correlation_risk * 100,
                "concentration_risk": metrics.concentration_risk * 100,
                "portfolio_risk": (metrics.allocated_capital / self.current_bankroll) * 100,
            },
            "position_breakdown": {
                "total_positions": metrics.total_positions,
                "active_positions": metrics.active_positions,
                "by_sport": positions_by_sport,
                "by_risk_level": positions_by_risk,
            },
            "recommendations": self._generate_recommendations(metrics),
        }

    def _generate_recommendations(self, metrics: PortfolioMetrics) -> list[str]:
        """
        Generate portfolio recommendations based on current metrics
        """
        recommendations = []

        # Risk-based recommendations
        if metrics.correlation_risk > 0.5:
            recommendations.append(
                "⚠️ High correlation risk detected - consider diversifying across different sports/markets"
            )

        if metrics.concentration_risk > 0.4:
            recommendations.append(
                "⚠️ Portfolio too concentrated - reduce position sizes or add more positions"
            )

        if (metrics.allocated_capital / self.current_bankroll) > self.max_portfolio_risk:
            recommendations.append(
                "🚨 Portfolio risk exceeds maximum limit - reduce position sizes"
            )

        # Performance recommendations
        if metrics.sharpe_ratio < 0.5:
            recommendations.append(
                "📈 Low risk-adjusted returns - consider higher probability bets or better odds"
            )

        if metrics.win_rate < 0.5 and len(self.closed_positions) > 10:
            recommendations.append("🎯 Win rate below 50% - review bet selection criteria")

        # Opportunity recommendations
        if metrics.available_capital > self.current_bankroll * 0.8:
            recommendations.append(
                "💰 High cash allocation - consider adding positions if good opportunities arise"
            )

        if not recommendations:
            recommendations.append("✅ Portfolio metrics look healthy - continue current strategy")

        return recommendations


# Integration with existing EdgeGod system
async def integrate_bankroll_optimizer_with_edgegod(
    parlay_legs: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Integration point with existing EdgeGod parlay system
    """
    optimizer = EQ12AdvancedBankrollOptimizer()

    # Calculate optimal sizing for the parlay
    total_odds = 1
    for leg in parlay_legs:
        leg_odds = leg.get("odds", 100)
        if leg_odds > 0:
            total_odds *= 1 + leg_odds / 100
        else:
            total_odds *= 1 + 100 / abs(leg_odds)

    # Convert back to American odds
    american_odds = (total_odds - 1) * 100 if total_odds >= 2 else -100 / (total_odds - 1)

    # Estimate parlay win probability (simplified)
    win_prob = 1.0
    for leg in parlay_legs:
        leg_prob = leg.get("win_probability", 0.5)
        win_prob *= leg_prob

    # Calculate expected value
    expected_value = (win_prob * abs(american_odds) / 100 - (1 - win_prob)) * 100

    # Optimize position size
    sizing_result = await optimizer.optimize_position_size(
        bet_description=f"Parlay ({len(parlay_legs)} legs)",
        odds=american_odds,
        win_probability=win_prob,
        expected_value=expected_value,
        correlation_group="parlay",
    )

    return {
        "original_parlay": parlay_legs,
        "parlay_odds": american_odds,
        "win_probability": win_prob,
        "expected_value": expected_value,
        "optimal_sizing": sizing_result,
        "portfolio_metrics": optimizer.calculate_portfolio_metrics(),
        "recommendations": optimizer._generate_recommendations(
            optimizer.calculate_portfolio_metrics()
        ),
    }


# CLI interface
async def main():
    """Main function for CLI testing"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Advanced Bankroll Optimizer")
    parser.add_argument("--test", action="store_true", help="Run optimizer test")
    parser.add_argument("--report", action="store_true", help="Generate portfolio report")
    parser.add_argument("--bankroll", type=float, default=10000, help="Initial bankroll amount")

    args = parser.parse_args()

    optimizer = EQ12AdvancedBankrollOptimizer(initial_bankroll=args.bankroll)

    if args.test:
        # Test with sample bet
        print("💰 Testing bankroll optimization...")

        result = await optimizer.optimize_position_size(
            bet_description="Test Bet - Team A ML",
            odds=150,  # +150 American odds
            win_probability=0.55,
            expected_value=12.5,
            strategy=SizingStrategy.FRACTIONAL_KELLY,
        )

        print("✅ Optimization complete:")
        print(f"   Recommended Stake: ${result['recommended_stake']:.2f}")
        print(f"   Sizing Fraction: {result['sizing_fraction']:.1%}")
        print(f"   Kelly Fraction: {result['kelly_fraction']:.1%}")
        print(f"   Strategy Used: {result['strategy_used']}")
        print(f"   Expected Return: ${result['expected_return']:.2f}")

        # Add the position
        position = result["position_details"]
        optimizer.add_position(position)

        print("\n📊 Portfolio after adding position:")
        metrics = optimizer.calculate_portfolio_metrics()
        print(f"   Allocated Capital: ${metrics.allocated_capital:.2f}")
        print(f"   Available Capital: ${metrics.available_capital:.2f}")
        print(f"   Portfolio Risk: {metrics.allocated_capital / optimizer.current_bankroll:.1%}")

    if args.report:
        print("📊 Generating portfolio report...")
        report = optimizer.generate_portfolio_report()
        print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
