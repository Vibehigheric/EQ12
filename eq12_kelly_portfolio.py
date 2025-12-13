#!/usr/bin/env python3
"""
EQ12 GODSTACK - Kelly & Portfolio Sizer
Fractional Kelly with drawdown guard; allocate across 3 buckets:
"Core SGP", "Alt-line ladder", "Lottery long-shot"

Core Features:
- Fractional Kelly criterion with risk management
- Portfolio allocation across risk categories
- Drawdown protection and position sizing
- Dynamic bet sizing based on edge and variance
- Bankroll management with stop-loss triggers
- Multi-bet correlation adjustments
"""

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/kelly_portfolio.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class RiskCategory(Enum):
    """Risk categories for portfolio allocation"""

    CORE_SGP = "core_sgp"  # High confidence, moderate correlation
    ALT_LINE_LADDER = "alt_line"  # Medium confidence, ladder betting
    LOTTERY_LONGSHOT = "lottery"  # Low confidence, high payout
    HEDGE_INSURANCE = "hedge"  # Risk mitigation bets


class BetStatus(Enum):
    """Status of individual bets"""

    PENDING = "pending"
    PLACED = "placed"
    WON = "won"
    LOST = "lost"
    PUSHED = "pushed"
    CANCELLED = "cancelled"


@dataclass
class KellyBet:
    """Individual bet with Kelly sizing calculation"""

    bet_id: str
    category: RiskCategory

    # Bet details
    description: str
    market_type: str
    selection: str
    line: float | None

    # Odds and probabilities
    offered_odds: int  # American format
    true_probability: float
    implied_probability: float
    edge: float  # Expected edge percentage

    # Kelly calculations
    raw_kelly_fraction: float
    adjusted_kelly_fraction: float
    recommended_bet_size: float
    max_bet_size: float

    # Risk metrics
    variance: float
    correlation_adjustment: float
    confidence_level: float

    # Portfolio allocation
    bucket_allocation: float  # Percentage of bucket to risk
    total_allocation: float  # Percentage of total bankroll

    # Metadata
    bet_timestamp: datetime
    status: BetStatus
    actual_bet_amount: float | None = None
    result: str | None = None


@dataclass
class PortfolioBucket:
    """Risk-based portfolio bucket"""

    bucket_name: str
    category: RiskCategory

    # Allocation settings
    max_allocation_pct: float  # Max % of bankroll for this bucket
    current_allocation_pct: float  # Current % allocated
    available_allocation: float  # Remaining allocation

    # Risk parameters
    max_bet_pct: float  # Max single bet as % of bucket
    kelly_fraction_multiplier: float  # Fractional Kelly multiplier
    min_edge_threshold: float  # Minimum edge to consider
    min_confidence_threshold: float  # Minimum confidence to bet

    # Performance tracking
    total_bets: int
    winning_bets: int
    total_wagered: float
    total_returned: float
    net_profit: float
    roi: float

    # Current bets
    active_bets: list[KellyBet]


@dataclass
class DrawdownProtection:
    """Drawdown protection parameters"""

    # Drawdown thresholds
    warning_drawdown_pct: float  # Warn at this % drawdown
    stop_loss_drawdown_pct: float  # Stop betting at this % drawdown
    severe_drawdown_pct: float  # Emergency position reduction

    # Current state
    peak_bankroll: float
    current_drawdown_pct: float
    protection_active: bool

    # Actions
    reduce_sizing_factor: float  # Reduce bet sizes by this factor
    pause_new_bets: bool
    emergency_hedge_trigger: bool


class KellyPortfolioManager:
    """Main Kelly criterion portfolio management system"""

    def __init__(self, initial_bankroll: float = 10000.0):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.peak_bankroll = initial_bankroll

        # Portfolio buckets
        self.buckets = self._initialize_buckets()

        # Drawdown protection
        self.drawdown_protection = DrawdownProtection(
            warning_drawdown_pct=10.0,
            stop_loss_drawdown_pct=25.0,
            severe_drawdown_pct=40.0,
            peak_bankroll=initial_bankroll,
            current_drawdown_pct=0.0,
            protection_active=False,
            reduce_sizing_factor=1.0,
            pause_new_bets=False,
            emergency_hedge_trigger=False,
        )

        # Bet tracking
        self.all_bets: list[KellyBet] = []
        self.bet_counter = 0

        # Performance metrics
        self.performance_history = []

        logger.info(f"Kelly Portfolio Manager initialized with ${initial_bankroll:,.2f}")

    def _initialize_buckets(self) -> dict[RiskCategory, PortfolioBucket]:
        """Initialize portfolio buckets with default allocations"""

        buckets = {
            RiskCategory.CORE_SGP: PortfolioBucket(
                bucket_name="Core SGP Plays",
                category=RiskCategory.CORE_SGP,
                max_allocation_pct=40.0,
                current_allocation_pct=0.0,
                available_allocation=40.0,
                max_bet_pct=15.0,  # Max 15% of bucket per bet
                kelly_fraction_multiplier=0.25,  # Conservative 1/4 Kelly
                min_edge_threshold=3.0,  # Minimum 3% edge
                min_confidence_threshold=0.75,
                total_bets=0,
                winning_bets=0,
                total_wagered=0.0,
                total_returned=0.0,
                net_profit=0.0,
                roi=0.0,
                active_bets=[],
            ),
            RiskCategory.ALT_LINE_LADDER: PortfolioBucket(
                bucket_name="Alt Line Ladders",
                category=RiskCategory.ALT_LINE_LADDER,
                max_allocation_pct=30.0,
                current_allocation_pct=0.0,
                available_allocation=30.0,
                max_bet_pct=10.0,
                kelly_fraction_multiplier=0.20,  # 1/5 Kelly
                min_edge_threshold=2.0,  # 2% edge threshold
                min_confidence_threshold=0.65,
                total_bets=0,
                winning_bets=0,
                total_wagered=0.0,
                total_returned=0.0,
                net_profit=0.0,
                roi=0.0,
                active_bets=[],
            ),
            RiskCategory.LOTTERY_LONGSHOT: PortfolioBucket(
                bucket_name="Lottery Long-shots",
                category=RiskCategory.LOTTERY_LONGSHOT,
                max_allocation_pct=20.0,
                current_allocation_pct=0.0,
                available_allocation=20.0,
                max_bet_pct=5.0,  # Small bets only
                kelly_fraction_multiplier=0.10,  # Very conservative 1/10 Kelly
                min_edge_threshold=15.0,  # Need big edge for lottery plays
                min_confidence_threshold=0.40,
                total_bets=0,
                winning_bets=0,
                total_wagered=0.0,
                total_returned=0.0,
                net_profit=0.0,
                roi=0.0,
                active_bets=[],
            ),
            RiskCategory.HEDGE_INSURANCE: PortfolioBucket(
                bucket_name="Hedge & Insurance",
                category=RiskCategory.HEDGE_INSURANCE,
                max_allocation_pct=10.0,
                current_allocation_pct=0.0,
                available_allocation=10.0,
                max_bet_pct=20.0,  # Can be larger for hedging
                kelly_fraction_multiplier=1.0,  # Full sizing for hedges
                min_edge_threshold=-5.0,  # Allow negative edge for insurance
                min_confidence_threshold=0.50,
                total_bets=0,
                winning_bets=0,
                total_wagered=0.0,
                total_returned=0.0,
                net_profit=0.0,
                roi=0.0,
                active_bets=[],
            ),
        }

        return buckets

    def calculate_kelly_fraction(
        self, true_prob: float, offered_odds: int
    ) -> tuple[float, dict[str, float]]:
        """Calculate Kelly fraction for a bet"""

        # Convert American odds to decimal
        decimal_odds = offered_odds / 100 + 1 if offered_odds > 0 else 100 / abs(offered_odds) + 1

        # Kelly formula: f = (bp - q) / b
        # where f = fraction to bet, b = odds received, p = true probability, q = 1-p
        b = decimal_odds - 1  # Net odds
        p = true_prob
        q = 1 - p

        raw_kelly = (b * p - q) / b if b > 0 else 0.0

        # Calculate additional metrics
        implied_prob = 1 / decimal_odds
        edge = (true_prob * decimal_odds - 1) * 100  # Edge as percentage

        # Variance calculation for Kelly
        variance = p * (b**2) + q * (-1) ** 2 - (b * p - q) ** 2

        metrics = {
            "decimal_odds": decimal_odds,
            "implied_probability": implied_prob,
            "edge_percentage": edge,
            "variance": variance,
            "optimal_fraction": raw_kelly,
        }

        return max(0.0, raw_kelly), metrics

    def size_bet(self, bet_details: dict[str, Any], category: RiskCategory) -> KellyBet | None:
        """Calculate optimal bet size for a given opportunity"""

        # Get bet parameters
        true_prob = bet_details.get("true_probability", 0.5)
        offered_odds = bet_details.get("offered_odds", 100)
        confidence = bet_details.get("confidence_level", 0.8)
        description = bet_details.get("description", "Unknown bet")

        # Calculate Kelly fraction
        raw_kelly, metrics = self.calculate_kelly_fraction(true_prob, offered_odds)

        # Check if bet meets minimum criteria
        bucket = self.buckets[category]
        if metrics["edge_percentage"] < bucket.min_edge_threshold:
            logger.info(
                f"Bet rejected: Edge {metrics['edge_percentage']:.2f}% < {bucket.min_edge_threshold}%"
            )
            return None

        if confidence < bucket.min_confidence_threshold:
            logger.info(
                f"Bet rejected: Confidence {confidence:.2f} < {bucket.min_confidence_threshold}"
            )
            return None

        # Check drawdown protection
        if self.drawdown_protection.pause_new_bets and category != RiskCategory.HEDGE_INSURANCE:
            logger.warning("New bets paused due to drawdown protection")
            return None

        # Apply fractional Kelly and bucket constraints
        adjusted_kelly = raw_kelly * bucket.kelly_fraction_multiplier

        # Apply drawdown sizing reduction
        if self.drawdown_protection.protection_active:
            adjusted_kelly *= self.drawdown_protection.reduce_sizing_factor

        # Calculate bet sizes
        bucket_size = self.current_bankroll * (bucket.max_allocation_pct / 100)
        max_bet_from_bucket = bucket_size * (bucket.max_bet_pct / 100)

        # Kelly-suggested size (as fraction of current bankroll)
        kelly_suggested_size = self.current_bankroll * adjusted_kelly

        # Final bet size (smaller of Kelly suggestion and bucket limit)
        recommended_size = min(kelly_suggested_size, max_bet_from_bucket)

        # Additional constraints
        min_bet_size = 10.0  # Minimum practical bet size
        max_practical_size = self.current_bankroll * 0.05  # Never more than 5% of total bankroll

        final_bet_size = max(min_bet_size, min(recommended_size, max_practical_size))

        # Create bet object
        self.bet_counter += 1
        bet = KellyBet(
            bet_id=f"bet_{self.bet_counter}",
            category=category,
            description=description,
            market_type=bet_details.get("market_type", "unknown"),
            selection=bet_details.get("selection", "unknown"),
            line=bet_details.get("line"),
            offered_odds=offered_odds,
            true_probability=true_prob,
            implied_probability=metrics["implied_probability"],
            edge=metrics["edge_percentage"],
            raw_kelly_fraction=raw_kelly,
            adjusted_kelly_fraction=adjusted_kelly,
            recommended_bet_size=final_bet_size,
            max_bet_size=max_bet_from_bucket,
            variance=metrics["variance"],
            correlation_adjustment=bet_details.get("correlation_adjustment", 0.0),
            confidence_level=confidence,
            bucket_allocation=((final_bet_size / bucket_size) * 100 if bucket_size > 0 else 0),
            total_allocation=(final_bet_size / self.current_bankroll) * 100,
            bet_timestamp=datetime.now(UTC),
            status=BetStatus.PENDING,
        )

        logger.info(f"Sized bet: ${final_bet_size:.2f} ({bet.total_allocation:.2f}% of bankroll)")
        return bet

    def place_bet(self, bet: KellyBet, actual_amount: float | None = None) -> bool:
        """Place a bet and update portfolio tracking"""

        if actual_amount is None:
            actual_amount = bet.recommended_bet_size

        # Check if we have sufficient bankroll
        if actual_amount > self.current_bankroll:
            logger.error(
                f"Insufficient bankroll: ${actual_amount:.2f} > ${self.current_bankroll:.2f}"
            )
            return False

        # Update bet
        bet.actual_bet_amount = actual_amount
        bet.status = BetStatus.PLACED

        # Update bankroll (reduce by bet amount)
        self.current_bankroll -= actual_amount

        # Add to tracking
        self.all_bets.append(bet)
        bucket = self.buckets[bet.category]
        bucket.active_bets.append(bet)
        bucket.total_bets += 1
        bucket.total_wagered += actual_amount
        bucket.current_allocation_pct += (actual_amount / self.initial_bankroll) * 100

        logger.info(f"Placed bet {bet.bet_id}: ${actual_amount:.2f} on {bet.description}")
        return True

    def settle_bet(self, bet_id: str, result: str, payout: float = 0.0) -> bool:
        """Settle a completed bet"""

        # Find bet
        bet = None
        for b in self.all_bets:
            if b.bet_id == bet_id:
                bet = b
                break

        if not bet:
            logger.error(f"Bet {bet_id} not found")
            return False

        if bet.status != BetStatus.PLACED:
            logger.error(f"Bet {bet_id} not in placed status")
            return False

        # Update bet
        bet.result = result
        if result.lower() == "won":
            bet.status = BetStatus.WON
            self.current_bankroll += payout
        elif result.lower() == "lost":
            bet.status = BetStatus.LOST
        elif result.lower() == "pushed":
            bet.status = BetStatus.PUSHED
            self.current_bankroll += bet.actual_bet_amount  # Return original stake
        else:
            logger.error(f"Unknown result: {result}")
            return False

        # Update bucket tracking
        bucket = self.buckets[bet.category]
        if bet.status == BetStatus.WON:
            bucket.winning_bets += 1
            bucket.total_returned += payout
            bucket.net_profit += payout - bet.actual_bet_amount
        elif bet.status == BetStatus.PUSHED:
            bucket.total_returned += bet.actual_bet_amount

        # Update bucket allocation
        bucket.current_allocation_pct -= (bet.actual_bet_amount / self.initial_bankroll) * 100
        bucket.roi = (
            (bucket.net_profit / bucket.total_wagered * 100) if bucket.total_wagered > 0 else 0
        )

        # Remove from active bets
        bucket.active_bets = [b for b in bucket.active_bets if b.bet_id != bet_id]

        # Update peak bankroll and check drawdown
        if self.current_bankroll > self.peak_bankroll:
            self.peak_bankroll = self.current_bankroll
            self.drawdown_protection.peak_bankroll = self.peak_bankroll

        self._update_drawdown_protection()

        logger.info(f"Settled bet {bet_id}: {result}, Bankroll: ${self.current_bankroll:.2f}")
        return True

    def _update_drawdown_protection(self):
        """Update drawdown protection status"""

        current_drawdown = ((self.peak_bankroll - self.current_bankroll) / self.peak_bankroll) * 100
        self.drawdown_protection.current_drawdown_pct = current_drawdown

        if current_drawdown >= self.drawdown_protection.severe_drawdown_pct:
            self.drawdown_protection.pause_new_bets = True
            self.drawdown_protection.reduce_sizing_factor = 0.25
            self.drawdown_protection.emergency_hedge_trigger = True
            self.drawdown_protection.protection_active = True
            logger.error(f"SEVERE DRAWDOWN: {current_drawdown:.2f}% - Emergency measures activated")

        elif current_drawdown >= self.drawdown_protection.stop_loss_drawdown_pct:
            self.drawdown_protection.pause_new_bets = True
            self.drawdown_protection.reduce_sizing_factor = 0.5
            self.drawdown_protection.protection_active = True
            logger.warning(f"STOP LOSS TRIGGERED: {current_drawdown:.2f}% - Pausing new bets")

        elif current_drawdown >= self.drawdown_protection.warning_drawdown_pct:
            self.drawdown_protection.reduce_sizing_factor = 0.75
            self.drawdown_protection.protection_active = True
            logger.warning(f"DRAWDOWN WARNING: {current_drawdown:.2f}% - Reducing bet sizes")

        else:
            self.drawdown_protection.protection_active = False
            self.drawdown_protection.pause_new_bets = False
            self.drawdown_protection.reduce_sizing_factor = 1.0

    def get_portfolio_summary(self) -> dict[str, Any]:
        """Get comprehensive portfolio summary"""

        total_active_bets = sum(len(bucket.active_bets) for bucket in self.buckets.values())
        total_at_risk = sum(
            bet.actual_bet_amount or 0
            for bucket in self.buckets.values()
            for bet in bucket.active_bets
        )

        overall_roi = (
            (self.current_bankroll - self.initial_bankroll) / self.initial_bankroll
        ) * 100

        bucket_summaries = {}
        for category, bucket in self.buckets.items():
            bucket_summaries[category.value] = {
                "name": bucket.bucket_name,
                "max_allocation_pct": bucket.max_allocation_pct,
                "current_allocation_pct": bucket.current_allocation_pct,
                "available_allocation": bucket.available_allocation - bucket.current_allocation_pct,
                "total_bets": bucket.total_bets,
                "winning_bets": bucket.winning_bets,
                "win_rate": (
                    (bucket.winning_bets / bucket.total_bets * 100) if bucket.total_bets > 0 else 0
                ),
                "total_wagered": bucket.total_wagered,
                "net_profit": bucket.net_profit,
                "roi": bucket.roi,
                "active_bets": len(bucket.active_bets),
            }

        return {
            "bankroll": {
                "initial": self.initial_bankroll,
                "current": self.current_bankroll,
                "peak": self.peak_bankroll,
                "total_return": self.current_bankroll - self.initial_bankroll,
                "roi_percentage": overall_roi,
            },
            "drawdown_protection": {
                "current_drawdown_pct": self.drawdown_protection.current_drawdown_pct,
                "protection_active": self.drawdown_protection.protection_active,
                "new_bets_paused": self.drawdown_protection.pause_new_bets,
                "sizing_factor": self.drawdown_protection.reduce_sizing_factor,
            },
            "active_positions": {
                "total_bets": total_active_bets,
                "total_at_risk": total_at_risk,
                "risk_percentage": (
                    (total_at_risk / self.current_bankroll * 100)
                    if self.current_bankroll > 0
                    else 0
                ),
            },
            "buckets": bucket_summaries,
            "total_bets_placed": len(self.all_bets),
            "summary_timestamp": datetime.now(UTC).isoformat(),
        }

    def export_portfolio_report(self, output_path: str | None = None) -> str:
        """Export comprehensive portfolio report"""

        if not output_path:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            output_path = f"C:/EQ12/logs/portfolio_report_{timestamp}.json"

        report = {
            "portfolio_summary": self.get_portfolio_summary(),
            "all_bets": [asdict(bet) for bet in self.all_bets],
            "performance_metrics": self._calculate_performance_metrics(),
            "recommendations": self._generate_recommendations(),
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Portfolio report exported to {output_path}")
        return output_path

    def _calculate_performance_metrics(self) -> dict[str, Any]:
        """Calculate detailed performance metrics"""

        settled_bets = [
            bet
            for bet in self.all_bets
            if bet.status in [BetStatus.WON, BetStatus.LOST, BetStatus.PUSHED]
        ]

        if not settled_bets:
            return {"message": "No settled bets for analysis"}

        won_bets = [bet for bet in settled_bets if bet.status == BetStatus.WON]
        [bet for bet in settled_bets if bet.status == BetStatus.LOST]

        win_rate = len(won_bets) / len(settled_bets) * 100 if settled_bets else 0

        # Calculate actual vs expected performance
        expected_wins = sum(bet.true_probability for bet in settled_bets)
        actual_wins = len(won_bets)
        calibration_error = (
            abs(actual_wins - expected_wins) / len(settled_bets) if settled_bets else 0
        )

        return {
            "total_settled_bets": len(settled_bets),
            "win_rate": win_rate,
            "expected_win_rate": ((expected_wins / len(settled_bets) * 100) if settled_bets else 0),
            "calibration_error": calibration_error,
            "average_edge": (
                sum(bet.edge for bet in settled_bets) / len(settled_bets) if settled_bets else 0
            ),
            "sharpe_ratio": self._calculate_sharpe_ratio(settled_bets),
            "max_drawdown": self._calculate_max_drawdown(),
        }

    def _calculate_sharpe_ratio(self, bets: list[KellyBet]) -> float:
        """Calculate Sharpe ratio of betting returns"""

        if len(bets) < 2:
            return 0.0

        returns = []
        for bet in bets:
            if bet.actual_bet_amount and bet.actual_bet_amount > 0:
                if bet.status == BetStatus.WON:
                    payout = bet.actual_bet_amount * (abs(bet.offered_odds) / 100 + 1)
                    return_pct = (payout - bet.actual_bet_amount) / bet.actual_bet_amount
                elif bet.status == BetStatus.LOST:
                    return_pct = -1.0
                else:  # PUSHED
                    return_pct = 0.0

                returns.append(return_pct)

        if not returns:
            return 0.0

        mean_return = np.mean(returns)
        std_return = np.std(returns) if len(returns) > 1 else 0

        return (mean_return / std_return) if std_return > 0 else 0.0

    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown experienced"""

        return self.drawdown_protection.current_drawdown_pct

    def _generate_recommendations(self) -> list[str]:
        """Generate portfolio management recommendations"""

        recommendations = []

        # Bankroll recommendations
        if self.drawdown_protection.current_drawdown_pct > 15:
            recommendations.append("Consider reducing bet sizes until drawdown recovers")

        # Bucket allocation recommendations
        for _category, bucket in self.buckets.items():
            if bucket.roi < -10 and bucket.total_bets > 5:
                recommendations.append(f"Review {bucket.bucket_name} strategy - negative ROI")

            if bucket.current_allocation_pct > bucket.max_allocation_pct * 0.9:
                recommendations.append(f"{bucket.bucket_name} near allocation limit")

        # Performance recommendations
        settled_bets = [
            bet for bet in self.all_bets if bet.status in [BetStatus.WON, BetStatus.LOST]
        ]
        if len(settled_bets) > 10:
            win_rate = len([bet for bet in settled_bets if bet.status == BetStatus.WON]) / len(
                settled_bets
            )
            expected_win_rate = sum(bet.true_probability for bet in settled_bets) / len(
                settled_bets
            )

            if win_rate < expected_win_rate - 0.1:
                recommendations.append(
                    "Actual win rate significantly below expected - review probability estimates"
                )

        return recommendations


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 Kelly Portfolio Manager")
    parser.add_argument("--demo", action="store_true", help="Run demo simulation")
    parser.add_argument("--bankroll", type=float, default=10000, help="Initial bankroll")
    parser.add_argument("--export", action="store_true", help="Export portfolio report")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize portfolio manager
    portfolio = KellyPortfolioManager(initial_bankroll=args.bankroll)

    if args.demo:
        print(f"💰 KELLY PORTFOLIO DEMO - Starting Bankroll: ${args.bankroll:,.2f}")

        # Sample bets for different categories
        sample_bets = [
            {
                "description": "Yankees ML + Cole 7K + Under 8",
                "category": RiskCategory.CORE_SGP,
                "true_probability": 0.58,
                "offered_odds": +165,
                "confidence_level": 0.82,
                "market_type": "sgp",
                "selection": "parlay",
            },
            {
                "description": "Game Total Alt Under 7.5",
                "category": RiskCategory.ALT_LINE_LADDER,
                "true_probability": 0.48,
                "offered_odds": +140,
                "confidence_level": 0.70,
                "market_type": "alt_total",
                "selection": "under",
            },
            {
                "description": "Perfect Game +50000",
                "category": RiskCategory.LOTTERY_LONGSHOT,
                "true_probability": 0.0008,
                "offered_odds": +50000,
                "confidence_level": 0.45,
                "market_type": "novelty",
                "selection": "yes",
            },
        ]

        print("\n🎯 SIZING SAMPLE BETS:")
        sized_bets = []

        for bet_info in sample_bets:
            category = bet_info.pop("category")
            sized_bet = portfolio.size_bet(bet_info, category)

            if sized_bet:
                sized_bets.append(sized_bet)
                print(f"\n   {sized_bet.category.value.upper()}:")
                print(f"      Description: {sized_bet.description}")
                print(
                    f"      True Prob: {sized_bet.true_probability:.3f} | Odds: {sized_bet.offered_odds:+d}"
                )
                print(
                    f"      Edge: {sized_bet.edge:.2f}% | Kelly: {sized_bet.raw_kelly_fraction:.4f}"
                )
                print(
                    f"      Recommended Size: ${sized_bet.recommended_bet_size:.2f} ({sized_bet.total_allocation:.2f}% of bankroll)"
                )
            else:
                print(f"\n   ❌ Bet rejected: {bet_info['description']}")

        # Place bets
        print("\n📍 PLACING BETS:")
        for bet in sized_bets:
            if portfolio.place_bet(bet):
                print(f"   ✅ Placed: ${bet.actual_bet_amount:.2f} on {bet.description}")

        # Show portfolio summary
        print("\n📊 PORTFOLIO SUMMARY:")
        summary = portfolio.get_portfolio_summary()

        print(
            f"   Bankroll: ${summary['bankroll']['current']:,.2f} (${summary['bankroll']['total_return']:+,.2f})"
        )
        print(f"   Active Bets: {summary['active_positions']['total_bets']}")
        print(
            f"   At Risk: ${summary['active_positions']['total_at_risk']:,.2f} ({summary['active_positions']['risk_percentage']:.2f}%)"
        )

        print("\n🗂️ BUCKET ALLOCATIONS:")
        for _bucket_name, bucket_data in summary["buckets"].items():
            print(f"   {bucket_data['name']}:")
            print(
                f"      Allocated: {bucket_data['current_allocation_pct']:.1f}% / {bucket_data['max_allocation_pct']:.1f}%"
            )
            print(f"      Active Bets: {bucket_data['active_bets']}")
            print(f"      ROI: {bucket_data['roi']:+.1f}%")

        # Simulate some bet outcomes
        print("\n🎲 SIMULATING BET OUTCOMES:")

        import random

        for bet in sized_bets:
            # Simulate outcome based on true probability
            if random.random() < bet.true_probability:
                # Won
                if bet.offered_odds > 0:
                    payout = bet.actual_bet_amount * (bet.offered_odds / 100 + 1)
                else:
                    payout = bet.actual_bet_amount * (100 / abs(bet.offered_odds) + 1)

                portfolio.settle_bet(bet.bet_id, "won", payout)
                print(f"   ✅ WON: {bet.description} - Payout: ${payout:.2f}")
            else:
                # Lost
                portfolio.settle_bet(bet.bet_id, "lost")
                print(f"   ❌ LOST: {bet.description}")

        # Final summary
        final_summary = portfolio.get_portfolio_summary()
        print("\n🏆 FINAL RESULTS:")
        print(f"   Final Bankroll: ${final_summary['bankroll']['current']:,.2f}")
        print(f"   Total Return: ${final_summary['bankroll']['total_return']:+,.2f}")
        print(f"   ROI: {final_summary['bankroll']['roi_percentage']:+.2f}%")

        if final_summary["drawdown_protection"]["protection_active"]:
            print(
                f"   ⚠️ Drawdown Protection Active: {final_summary['drawdown_protection']['current_drawdown_pct']:.1f}%"
            )

        if args.export:
            report_path = portfolio.export_portfolio_report()
            print(f"\n💾 Portfolio report exported to: {report_path}")

    else:
        print("❌ Use --demo to run Kelly portfolio simulation")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
