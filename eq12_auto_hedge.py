#!/usr/bin/env python3
"""
EQ12 GODSTACK - Auto-Hedge Builder
CLI: `python eq12_auto_hedge.py --original-bet "SGP +650" --amount 100 --hedge-threshold 0.20`
Smart hedging for live bets with profit lock and risk management

Core Features:
- Automatic hedge calculation for existing bets
- Live line monitoring for optimal hedge timing
- Risk-free profit lock scenarios
- Partial cashout simulation
- Multi-book arbitrage detection
- Real-time hedge recommendations with SMS alerts
"""

import argparse
import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/auto_hedge.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class HedgeStrategy(Enum):
    """Hedge strategy types"""

    RISK_FREE = "risk_free"  # Lock in guaranteed profit
    PARTIAL_PROFIT = "partial_profit"  # Take partial profit, keep upside
    FULL_HEDGE = "full_hedge"  # Complete hedge for break-even
    ARBITRAGE = "arbitrage"  # Multi-book arbitrage opportunity
    MIDDLE = "middle"  # Middle betting opportunity


class BetStatus(Enum):
    """Original bet status"""

    PENDING = "pending"
    WINNING = "winning"
    LOSING = "losing"
    PUSHED = "pushed"
    CASHED_OUT = "cashed_out"


@dataclass
class OriginalBet:
    """Original bet that needs hedging"""

    bet_id: str
    description: str
    bet_type: str  # "sgp", "straight", "parlay"

    # Bet details
    stake: float
    odds: int
    potential_payout: float

    # Current status
    status: BetStatus
    current_value: float  # Live value if available

    # Legs/components (for SGP/parlay tracking)
    legs: list[dict[str, Any]]
    legs_remaining: list[str]  # Which legs still need to hit

    # Timing
    placed_at: datetime
    expires_at: datetime

    # Book information
    sportsbook: str
    bet_slip_id: str | None = None


@dataclass
class HedgeOption:
    """Individual hedge betting option"""

    hedge_id: str
    strategy: HedgeStrategy

    # Hedge bet details
    hedge_selection: str
    hedge_odds: int
    hedge_stake: float

    # Outcomes
    guaranteed_profit: float
    max_profit: float
    max_loss: float

    # Risk metrics
    win_probability: float
    expected_value: float
    sharpe_ratio: float

    # Execution details
    sportsbook: str
    execution_window: timedelta
    confidence: float

    # Scenario analysis
    outcomes: dict[str, float]  # Different scenarios and profits


@dataclass
class HedgeRecommendation:
    """Complete hedge recommendation"""

    original_bet: OriginalBet
    analysis_time: datetime

    # Market analysis
    current_live_odds: dict[str, int]
    line_movement: dict[str, float]  # How much lines have moved
    market_efficiency: float

    # Hedge options
    primary_recommendation: HedgeOption | None
    alternative_options: list[HedgeOption]

    # Timing analysis
    optimal_hedge_time: datetime | None
    time_decay_factor: float
    urgency_score: float  # 0-1, how urgent to hedge

    # Alerts and actions
    alert_triggers: list[str]
    auto_execute: bool
    reasoning: str


class LiveOddsMonitor:
    """Monitor live odds for hedge opportunities"""

    def __init__(self):
        self.cached_odds = {}
        self.line_history = []

        logger.info("LiveOddsMonitor initialized")

    async def fetch_live_odds(self, game_id: str, markets: list[str]) -> dict[str, int]:
        """Fetch current live odds for specified markets"""

        logger.info(f"Fetching live odds for game {game_id}")

        # In real implementation, this would integrate with multiple sportsbooks
        # For demo, simulate live odds with some movement

        simulated_odds = {
            "home_ml": -145,
            "away_ml": +125,
            "total_over_8.5": -108,
            "total_under_8.5": -112,
            "home_total_over_4.5": +105,
            "away_total_under_4.5": -125,
        }

        # Simulate line movement
        import random

        movement_factor = random.uniform(0.95, 1.05)

        for market in simulated_odds:
            if market in markets:
                base_odds = simulated_odds[market]
                if base_odds > 0:
                    simulated_odds[market] = int(base_odds * movement_factor)
                else:
                    simulated_odds[market] = int(base_odds / movement_factor)

        # Cache for comparison
        self.cached_odds[game_id] = {
            "odds": simulated_odds,
            "timestamp": datetime.now(UTC),
        }

        return simulated_odds

    def calculate_line_movement(self, game_id: str, market: str, original_odds: int) -> float:
        """Calculate how much a line has moved since original bet"""

        if game_id not in self.cached_odds:
            return 0.0

        current_odds = self.cached_odds[game_id]["odds"].get(market)
        if not current_odds:
            return 0.0

        # Calculate percentage movement
        if original_odds > 0 and current_odds > 0:
            movement = (current_odds - original_odds) / original_odds
        elif original_odds < 0 and current_odds < 0:
            movement = (abs(current_odds) - abs(original_odds)) / abs(original_odds)
        else:
            # Sign change (favorite to underdog or vice versa)
            movement = 1.0  # Significant movement

        return movement

    def detect_arbitrage(self, odds_dict: dict[str, dict[str, int]]) -> list[dict[str, Any]]:
        """Detect arbitrage opportunities across books"""

        arb_opportunities = []

        # Check for simple two-way arbitrage
        books = list(odds_dict.keys())

        for book1 in books:
            for book2 in books[books.index(book1) + 1 :]:
                odds1 = odds_dict[book1]
                odds2 = odds_dict[book2]

                # Check moneyline arbitrage
                if "home_ml" in odds1 and "away_ml" in odds2:
                    arb = self._calculate_arbitrage(odds1["home_ml"], odds2["away_ml"])

                    if arb["profit_margin"] > 0:
                        arb_opportunities.append(
                            {
                                "type": "moneyline",
                                "book1": book1,
                                "book2": book2,
                                "bet1": f"Home ML {odds1['home_ml']:+d}",
                                "bet2": f"Away ML {odds2['away_ml']:+d}",
                                "profit_margin": arb["profit_margin"],
                                "stakes": arb["stakes"],
                            }
                        )

        return arb_opportunities

    def _calculate_arbitrage(self, odds1: int, odds2: int) -> dict[str, float]:
        """Calculate arbitrage between two odds"""

        # Convert to decimal odds
        dec1 = (odds1 / 100 + 1) if odds1 > 0 else (100 / abs(odds1) + 1)
        dec2 = (odds2 / 100 + 1) if odds2 > 0 else (100 / abs(odds2) + 1)

        # Calculate implied probabilities
        prob_sum = (1 / dec1) + (1 / dec2)

        if prob_sum < 1:
            # Arbitrage exists
            profit_margin = 1 - prob_sum

            # Calculate optimal stakes for $100 total
            stake1 = 100 / (dec1 * prob_sum)
            stake2 = 100 / (dec2 * prob_sum)

            return {
                "profit_margin": profit_margin,
                "stakes": {"bet1": stake1, "bet2": stake2},
            }
        return {"profit_margin": 0, "stakes": None}


class HedgeCalculator:
    """Core hedge calculation engine"""

    def __init__(self):
        self.risk_tolerance = 0.05  # 5% default risk tolerance
        self.min_profit_threshold = 0.10  # 10% minimum profit to recommend hedge

        logger.info("HedgeCalculator initialized")

    def calculate_hedge_options(
        self, original_bet: OriginalBet, live_odds: dict[str, int]
    ) -> list[HedgeOption]:
        """Calculate all viable hedge options for a bet"""

        logger.info(f"Calculating hedge options for bet {original_bet.bet_id}")

        hedge_options = []

        # Risk-free hedge
        risk_free = self._calculate_risk_free_hedge(original_bet, live_odds)
        if risk_free:
            hedge_options.append(risk_free)

        # Partial profit hedge
        partial_profit = self._calculate_partial_hedge(original_bet, live_odds, 0.5)
        if partial_profit:
            hedge_options.append(partial_profit)

        # Full hedge (break-even)
        full_hedge = self._calculate_full_hedge(original_bet, live_odds)
        if full_hedge:
            hedge_options.append(full_hedge)

        # Middle opportunity
        middle = self._calculate_middle_opportunity(original_bet, live_odds)
        if middle:
            hedge_options.append(middle)

        # Sort by expected value
        hedge_options.sort(key=lambda x: x.expected_value, reverse=True)

        logger.info(f"Generated {len(hedge_options)} hedge options")

        return hedge_options

    def _calculate_risk_free_hedge(
        self, original_bet: OriginalBet, live_odds: dict[str, int]
    ) -> HedgeOption | None:
        """Calculate risk-free hedge option"""

        # Find opposing market
        opposing_odds = self._find_opposing_odds(original_bet, live_odds)
        if not opposing_odds:
            return None

        # Calculate hedge stake for guaranteed profit
        original_decimal = self._american_to_decimal(original_bet.odds)
        hedge_decimal = self._american_to_decimal(opposing_odds)

        # For guaranteed profit, we need:
        # original_stake * (original_decimal - 1) = hedge_stake * (hedge_decimal - 1)

        max_profit_original = original_bet.stake * (original_decimal - 1)
        required_hedge_stake = max_profit_original / (hedge_decimal - 1)

        # Calculate outcomes
        if original_bet.status == BetStatus.WINNING:
            # If original wins: profit = original_payout - original_stake - hedge_stake
            original_wins_profit = max_profit_original - required_hedge_stake

            # If hedge wins: profit = hedge_payout - original_stake - hedge_stake
            hedge_wins_profit = required_hedge_stake * (hedge_decimal - 1) - original_bet.stake
        else:
            # Standard calculation
            original_wins_profit = max_profit_original - required_hedge_stake
            hedge_wins_profit = required_hedge_stake * (hedge_decimal - 1) - original_bet.stake

        # Only recommend if both outcomes are profitable
        if original_wins_profit > 0 and hedge_wins_profit > 0:
            guaranteed_profit = min(original_wins_profit, hedge_wins_profit)

            return HedgeOption(
                hedge_id=f"risk_free_{original_bet.bet_id}",
                strategy=HedgeStrategy.RISK_FREE,
                hedge_selection=self._get_opposing_selection(original_bet),
                hedge_odds=opposing_odds,
                hedge_stake=required_hedge_stake,
                guaranteed_profit=guaranteed_profit,
                max_profit=max(original_wins_profit, hedge_wins_profit),
                max_loss=0.0,
                win_probability=1.0,  # Guaranteed profit
                expected_value=guaranteed_profit,
                sharpe_ratio=float("inf"),  # Risk-free
                sportsbook="BestOdds",
                execution_window=timedelta(minutes=5),
                confidence=0.95,
                outcomes={
                    "original_wins": original_wins_profit,
                    "hedge_wins": hedge_wins_profit,
                },
            )

        return None

    def _calculate_partial_hedge(
        self,
        original_bet: OriginalBet,
        live_odds: dict[str, int],
        hedge_percentage: float,
    ) -> HedgeOption | None:
        """Calculate partial hedge option"""

        opposing_odds = self._find_opposing_odds(original_bet, live_odds)
        if not opposing_odds:
            return None

        original_decimal = self._american_to_decimal(original_bet.odds)
        hedge_decimal = self._american_to_decimal(opposing_odds)

        # Hedge portion of potential profit
        max_profit = original_bet.stake * (original_decimal - 1)
        hedge_amount = max_profit * hedge_percentage / (hedge_decimal - 1)

        # Calculate outcomes
        original_wins_profit = max_profit - hedge_amount
        hedge_wins_profit = hedge_amount * (hedge_decimal - 1) - original_bet.stake

        # Estimate win probability (simplified)
        original_prob = self._estimate_win_probability(original_bet.odds)

        expected_value = (
            original_prob * original_wins_profit + (1 - original_prob) * hedge_wins_profit
        )

        return HedgeOption(
            hedge_id=f"partial_{int(hedge_percentage * 100)}_{original_bet.bet_id}",
            strategy=HedgeStrategy.PARTIAL_PROFIT,
            hedge_selection=self._get_opposing_selection(original_bet),
            hedge_odds=opposing_odds,
            hedge_stake=hedge_amount,
            guaranteed_profit=0.0,  # Not guaranteed
            max_profit=original_wins_profit,
            max_loss=max(0, -hedge_wins_profit),
            win_probability=original_prob,
            expected_value=expected_value,
            sharpe_ratio=expected_value / max(1, abs(hedge_wins_profit)),
            sportsbook="BestOdds",
            execution_window=timedelta(minutes=10),
            confidence=0.80,
            outcomes={
                "original_wins": original_wins_profit,
                "hedge_wins": hedge_wins_profit,
                "hedge_percentage": hedge_percentage,
            },
        )

    def _calculate_full_hedge(
        self, original_bet: OriginalBet, live_odds: dict[str, int]
    ) -> HedgeOption | None:
        """Calculate full hedge for break-even"""

        opposing_odds = self._find_opposing_odds(original_bet, live_odds)
        if not opposing_odds:
            return None

        hedge_decimal = self._american_to_decimal(opposing_odds)

        # Full hedge to break even
        hedge_stake = original_bet.stake

        # Calculate outcomes
        original_wins_profit = original_bet.potential_payout - original_bet.stake - hedge_stake
        hedge_wins_profit = hedge_stake * (hedge_decimal - 1) - original_bet.stake

        # Expected value
        original_prob = self._estimate_win_probability(original_bet.odds)
        expected_value = (
            original_prob * original_wins_profit + (1 - original_prob) * hedge_wins_profit
        )

        return HedgeOption(
            hedge_id=f"full_hedge_{original_bet.bet_id}",
            strategy=HedgeStrategy.FULL_HEDGE,
            hedge_selection=self._get_opposing_selection(original_bet),
            hedge_odds=opposing_odds,
            hedge_stake=hedge_stake,
            guaranteed_profit=0.0,
            max_profit=max(original_wins_profit, hedge_wins_profit),
            max_loss=max(0, -min(original_wins_profit, hedge_wins_profit)),
            win_probability=original_prob,
            expected_value=expected_value,
            sharpe_ratio=expected_value / max(1, hedge_stake),
            sportsbook="BestOdds",
            execution_window=timedelta(minutes=15),
            confidence=0.70,
            outcomes={
                "original_wins": original_wins_profit,
                "hedge_wins": hedge_wins_profit,
            },
        )

    def _calculate_middle_opportunity(
        self, original_bet: OriginalBet, live_odds: dict[str, int]
    ) -> HedgeOption | None:
        """Calculate middle betting opportunity"""

        # Middle opportunities exist for totals and spreads
        if "total" not in original_bet.description.lower():
            return None

        # Find middle range
        original_line = self._extract_line_from_description(original_bet.description)
        if not original_line:
            return None

        # Look for opposing total at different line
        middle_odds = None
        middle_line = None

        for market, odds in live_odds.items():
            if "total" in market.lower():
                line = self._extract_line_from_market(market)
                if line and abs(line - original_line) >= 1.0:  # At least 1 point difference
                    middle_odds = odds
                    middle_line = line
                    break

        if not middle_odds:
            return None

        # Calculate middle opportunity
        hedge_decimal = self._american_to_decimal(middle_odds)
        hedge_stake = original_bet.stake * 0.8  # Conservative sizing

        # Three outcomes: original wins, middle wins (both lose), hedge wins
        original_wins = original_bet.potential_payout - original_bet.stake - hedge_stake
        middle_wins = -(original_bet.stake + hedge_stake)  # Both lose
        hedge_wins = hedge_stake * (hedge_decimal - 1) - original_bet.stake

        # Estimate probabilities (simplified)
        middle_probability = 0.15  # Rough estimate for middle hitting
        original_prob = self._estimate_win_probability(original_bet.odds) * (1 - middle_probability)
        hedge_prob = (1 - middle_probability) - original_prob

        expected_value = (
            original_prob * original_wins
            + middle_probability * middle_wins
            + hedge_prob * hedge_wins
        )

        return HedgeOption(
            hedge_id=f"middle_{original_bet.bet_id}",
            strategy=HedgeStrategy.MIDDLE,
            hedge_selection=f"Total {middle_line}",
            hedge_odds=middle_odds,
            hedge_stake=hedge_stake,
            guaranteed_profit=0.0,
            max_profit=max(original_wins, hedge_wins),
            max_loss=-middle_wins,
            win_probability=original_prob + hedge_prob,
            expected_value=expected_value,
            sharpe_ratio=expected_value / max(1, -middle_wins),
            sportsbook="BestOdds",
            execution_window=timedelta(minutes=20),
            confidence=0.60,
            outcomes={
                "original_wins": original_wins,
                "middle_hits": middle_wins,
                "hedge_wins": hedge_wins,
                "middle_probability": middle_probability,
            },
        )

    def _find_opposing_odds(
        self, original_bet: OriginalBet, live_odds: dict[str, int]
    ) -> int | None:
        """Find the opposing market odds for hedging"""

        # Simple mapping for common bet types
        description = original_bet.description.lower()

        if "home" in description and "ml" in description:
            return live_odds.get("away_ml")
        if "away" in description and "ml" in description:
            return live_odds.get("home_ml")
        if "over" in description:
            return live_odds.get("total_under_8.5")  # Simplified
        if "under" in description:
            return live_odds.get("total_over_8.5")  # Simplified

        return None

    def _get_opposing_selection(self, original_bet: OriginalBet) -> str:
        """Get the opposing selection for hedging"""

        description = original_bet.description.lower()

        if "home" in description and "ml" in description:
            return "Away ML"
        if "away" in description and "ml" in description:
            return "Home ML"
        if "over" in description:
            return "Under Total"
        if "under" in description:
            return "Over Total"

        return "Opposite Selection"

    def _american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds"""

        if american_odds > 0:
            return (american_odds / 100) + 1
        return (100 / abs(american_odds)) + 1

    def _estimate_win_probability(self, american_odds: int) -> float:
        """Estimate win probability from American odds"""

        decimal = self._american_to_decimal(american_odds)
        return 1 / decimal

    def _extract_line_from_description(self, description: str) -> float | None:
        """Extract betting line from description"""

        import re

        match = re.search(r"(\d+\.?\d*)", description)
        if match:
            return float(match.group(1))
        return None

    def _extract_line_from_market(self, market: str) -> float | None:
        """Extract line from market name"""

        import re

        match = re.search(r"(\d+\.?\d*)", market)
        if match:
            return float(match.group(1))
        return None


class AutoHedgeEngine:
    """Main auto-hedge engine"""

    def __init__(self):
        self.live_monitor = LiveOddsMonitor()
        self.calculator = HedgeCalculator()
        self.active_bets = {}
        self.hedge_recommendations = []

        logger.info("AutoHedgeEngine initialized")

    def register_bet(self, bet: OriginalBet) -> str:
        """Register a bet for hedge monitoring"""

        self.active_bets[bet.bet_id] = bet
        logger.info(f"Registered bet {bet.bet_id} for hedge monitoring")

        return bet.bet_id

    async def generate_hedge_recommendation(self, bet_id: str) -> HedgeRecommendation | None:
        """Generate hedge recommendation for a specific bet"""

        if bet_id not in self.active_bets:
            logger.error(f"Bet {bet_id} not found in active bets")
            return None

        original_bet = self.active_bets[bet_id]

        logger.info(f"Generating hedge recommendation for {bet_id}")

        # Fetch current live odds
        live_odds = await self.live_monitor.fetch_live_odds(
            game_id="current_game",  # Would be extracted from bet
            markets=["home_ml", "away_ml", "total_over_8.5", "total_under_8.5"],
        )

        # Calculate line movement
        line_movement = {}
        for market, _odds in live_odds.items():
            movement = self.live_monitor.calculate_line_movement(
                "current_game", market, original_bet.odds
            )
            line_movement[market] = movement

        # Calculate hedge options
        hedge_options = self.calculator.calculate_hedge_options(original_bet, live_odds)

        if not hedge_options:
            logger.info(f"No viable hedge options for bet {bet_id}")
            return None

        # Select primary recommendation
        primary_rec = hedge_options[0]  # Best EV option
        alternatives = hedge_options[1:3]  # Top 2 alternatives

        # Calculate urgency
        time_to_expiry = original_bet.expires_at - datetime.now(UTC)
        urgency_score = max(0, 1 - (time_to_expiry.total_seconds() / 7200))  # 2 hours = max urgency

        # Generate alerts
        alert_triggers = []
        if primary_rec.guaranteed_profit > original_bet.stake * 0.10:  # 10%+ guaranteed profit
            alert_triggers.append("High guaranteed profit available")

        if urgency_score > 0.7:
            alert_triggers.append("Bet expiring soon - hedge window closing")

        if max(line_movement.values()) > 0.15:  # 15%+ line movement
            alert_triggers.append("Significant line movement detected")

        # Auto-execute decision
        auto_execute = (
            primary_rec.guaranteed_profit > original_bet.stake * 0.15
            and primary_rec.confidence > 0.90
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(original_bet, primary_rec, line_movement)

        recommendation = HedgeRecommendation(
            original_bet=original_bet,
            analysis_time=datetime.now(UTC),
            current_live_odds=live_odds,
            line_movement=line_movement,
            market_efficiency=0.85,  # Assumed market efficiency
            primary_recommendation=primary_rec,
            alternative_options=alternatives,
            optimal_hedge_time=datetime.now(UTC) + timedelta(minutes=5),
            time_decay_factor=urgency_score,
            urgency_score=urgency_score,
            alert_triggers=alert_triggers,
            auto_execute=auto_execute,
            reasoning=reasoning,
        )

        self.hedge_recommendations.append(recommendation)

        return recommendation

    def _generate_reasoning(
        self,
        original_bet: OriginalBet,
        primary_hedge: HedgeOption,
        line_movement: dict[str, float],
    ) -> str:
        """Generate human-readable reasoning for hedge recommendation"""

        reasoning_parts = []

        # Strategy reasoning
        if primary_hedge.strategy == HedgeStrategy.RISK_FREE:
            reasoning_parts.append(
                f"Risk-free hedge available with ${primary_hedge.guaranteed_profit:.2f} guaranteed profit"
            )
        elif primary_hedge.strategy == HedgeStrategy.PARTIAL_PROFIT:
            reasoning_parts.append(
                f"Partial hedge to secure ${primary_hedge.max_profit:.2f} while maintaining upside"
            )
        elif primary_hedge.strategy == HedgeStrategy.MIDDLE:
            reasoning_parts.append(
                "Middle betting opportunity detected with potential for both bets to lose"
            )

        # Line movement reasoning
        significant_movement = [k for k, v in line_movement.items() if abs(v) > 0.10]
        if significant_movement:
            reasoning_parts.append(
                f"Favorable line movement of {max(line_movement.values()):.1%} creates hedge value"
            )

        # Time sensitivity
        time_remaining = original_bet.expires_at - datetime.now(UTC)
        if time_remaining < timedelta(hours=2):
            reasoning_parts.append("Limited time window requires immediate action")

        # Risk-reward analysis
        if primary_hedge.expected_value > original_bet.stake * 0.05:
            reasoning_parts.append(
                f"Positive expected value of ${primary_hedge.expected_value:.2f}"
            )

        return "; ".join(reasoning_parts)

    async def monitor_active_bets(self, check_interval: int = 300) -> None:
        """Continuously monitor active bets for hedge opportunities"""

        logger.info("Starting continuous bet monitoring")

        while True:
            current_time = datetime.now(UTC)

            for bet_id, bet in self.active_bets.items():
                # Skip if bet has expired
                if current_time > bet.expires_at:
                    continue

                # Generate recommendation
                recommendation = await self.generate_hedge_recommendation(bet_id)

                if recommendation and recommendation.alert_triggers:
                    logger.info(
                        f"HEDGE ALERT for {bet_id}: {', '.join(recommendation.alert_triggers)}"
                    )

                    # In real implementation, this would send SMS/email alerts
                    print(f"🚨 HEDGE ALERT: {bet.description}")
                    print(f"   Strategy: {recommendation.primary_recommendation.strategy.value}")
                    print(
                        f"   Guaranteed Profit: ${recommendation.primary_recommendation.guaranteed_profit:.2f}"
                    )
                    print(f"   Reasoning: {recommendation.reasoning}")

            # Wait before next check
            await asyncio.sleep(check_interval)


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 Auto-Hedge Builder")
    parser.add_argument("--original-bet", required=True, help="Original bet description")
    parser.add_argument("--odds", type=int, required=True, help="Original bet odds (American)")
    parser.add_argument("--amount", type=float, required=True, help="Original bet amount")
    parser.add_argument(
        "--hedge-threshold",
        type=float,
        default=0.10,
        help="Minimum profit threshold for hedge recommendation",
    )
    parser.add_argument("--monitor", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--export", action="store_true", help="Export recommendation to file")

    args = parser.parse_args()

    print("🔒 EQ12 AUTO-HEDGE BUILDER")
    print(f"Original Bet: {args.original_bet} ({args.odds:+d}) - ${args.amount}")

    # Create original bet object
    bet_id = f"bet_{int(datetime.now(UTC).timestamp())}"

    potential_payout = args.amount * (
        (args.odds / 100 + 1) if args.odds > 0 else (100 / abs(args.odds) + 1)
    )

    original_bet = OriginalBet(
        bet_id=bet_id,
        description=args.original_bet,
        bet_type="sgp",  # Assumed
        stake=args.amount,
        odds=args.odds,
        potential_payout=potential_payout,
        status=BetStatus.PENDING,
        current_value=args.amount,
        legs=[],
        legs_remaining=[],
        placed_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(hours=4),
        sportsbook="DraftKings",
    )

    # Initialize hedge engine
    engine = AutoHedgeEngine()
    engine.register_bet(original_bet)

    # Generate recommendation
    recommendation = await engine.generate_hedge_recommendation(bet_id)

    if not recommendation:
        print("\n❌ No hedge recommendations available at this time")
        return

    print("\n📊 HEDGE ANALYSIS:")
    print(f"   Analysis Time: {recommendation.analysis_time.strftime('%H:%M:%S UTC')}")
    print(f"   Market Efficiency: {recommendation.market_efficiency:.1%}")
    print(f"   Urgency Score: {recommendation.urgency_score:.2f}")

    if recommendation.line_movement:
        print("   Line Movement:")
        for market, movement in recommendation.line_movement.items():
            if abs(movement) > 0.05:  # Show significant movements
                print(f"      {market}: {movement:+.1%}")

    primary = recommendation.primary_recommendation

    print("\n🎯 PRIMARY RECOMMENDATION:")
    print(f"   Strategy: {primary.strategy.value.replace('_', ' ').title()}")
    print(f"   Hedge Bet: {primary.hedge_selection} ({primary.hedge_odds:+d})")
    print(f"   Hedge Amount: ${primary.hedge_stake:.2f}")
    print(f"   Guaranteed Profit: ${primary.guaranteed_profit:.2f}")
    print(f"   Max Profit: ${primary.max_profit:.2f}")
    print(f"   Max Loss: ${primary.max_loss:.2f}")
    print(f"   Expected Value: ${primary.expected_value:.2f}")
    print(f"   Confidence: {primary.confidence:.1%}")

    print("\n📋 OUTCOME SCENARIOS:")
    for scenario, profit in primary.outcomes.items():
        print(f"   {scenario.replace('_', ' ').title()}: ${profit:+.2f}")

    if recommendation.alternative_options:
        print("\n🔄 ALTERNATIVE OPTIONS:")
        for i, alt in enumerate(recommendation.alternative_options[:2], 1):
            print(f"   {i}. {alt.strategy.value.replace('_', ' ').title()}")
            print(f"      Hedge: ${alt.hedge_stake:.2f} @ {alt.hedge_odds:+d}")
            print(f"      Expected Value: ${alt.expected_value:+.2f}")

    if recommendation.alert_triggers:
        print("\n🚨 ALERTS:")
        for alert in recommendation.alert_triggers:
            print(f"   • {alert}")

    print("\n💭 REASONING:")
    print(f"   {recommendation.reasoning}")

    if recommendation.auto_execute:
        print("\n✅ AUTO-EXECUTE RECOMMENDED")
        print("   High confidence hedge with guaranteed profit")
    else:
        print("\n⚠️  MANUAL REVIEW RECOMMENDED")
        print("   Consider market conditions and personal risk tolerance")

    # Monitor mode
    if args.monitor:
        print("\n🔄 Starting continuous monitoring...")
        try:
            await engine.monitor_active_bets(check_interval=60)  # Check every minute
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped")

    # Export if requested
    if args.export:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        export_path = f"C:/EQ12/logs/hedge_recommendation_{timestamp}.json"

        export_data = {
            "original_bet": asdict(original_bet),
            "recommendation": asdict(recommendation),
            "analysis_summary": {
                "primary_strategy": primary.strategy.value,
                "guaranteed_profit": primary.guaranteed_profit,
                "expected_value": primary.expected_value,
                "confidence": primary.confidence,
                "urgency": recommendation.urgency_score,
            },
        }

        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"\n💾 Recommendation exported to: {export_path}")


if __name__ == "__main__":
    asyncio.run(main())
