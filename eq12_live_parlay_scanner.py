#!/usr/bin/env python3
"""
EQ12 Live Parlay Scanner - $8 to $80 Parlay Optimizer
===================================================

Scans all live games to find optimal parlay combinations for:
- Stake: $8
- Target: $80 (10x ROI)
- Required odds: +1150 minimum
- Max risk: Moderate correlation allowed
- Sports: NFL, NBA, MLB, NHL, Soccer

Real-time parlay discovery with EV calculations and risk scoring.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime

import numpy as np

# Import EQ12 math library
try:
    from eq12_math import (
        calculate_ev,
        calculate_parlay_ev,
        detect_sgp_correlations,
        independent_parlay_probability,
        kelly_criterion,
    )
except ImportError:
    # Fallback for standalone execution
    import sys

    sys.path.append("eq12_math")
    from odds import calculate_ev
    from parlay import independent_parlay_probability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/eq12_live_parlay_scanner.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class LiveGame:
    """Live game data structure"""

    game_id: str
    home_team: str
    away_team: str
    sport: str
    league: str
    start_time: datetime
    current_period: str
    time_remaining: str
    home_score: int
    away_score: int
    live_odds: dict[str, dict[str, float]]
    momentum_score: float = 0.0


@dataclass
class ParlayLeg:
    """Individual parlay leg"""

    game_id: str
    selection: str
    market_type: str
    odds: float
    probability: float
    ev_percent: float
    sportsbook: str


@dataclass
class OptimalParlay:
    """Optimal parlay recommendation"""

    legs: list[ParlayLeg]
    total_odds: float
    joint_probability: float
    expected_value: float
    roi_multiple: float
    stake_amount: float
    potential_payout: float
    risk_score: float
    confidence: float
    reasoning: str


class LiveOddsProvider:
    """Mock live odds provider - replace with real API"""

    def __init__(self):
        self.api_key = os.getenv("ODDS_API_KEY", "demo_key")

    async def get_live_games(self) -> list[LiveGame]:
        """Get all current live games"""
        # Mock data - replace with real API calls
        live_games = [
            LiveGame(
                game_id="nfl_kc_den_20251006",
                home_team="Denver Broncos",
                away_team="Kansas City Chiefs",
                sport="NFL",
                league="NFL",
                start_time=datetime.now(UTC),
                current_period="Q2",
                time_remaining="8:42",
                home_score=14,
                away_score=21,
                live_odds={
                    "moneyline": {"home": 185, "away": -220},
                    "spread": {"home": 4.5, "away": -4.5, "home_odds": -110, "away_odds": -110},
                    "total": {"over": 47.5, "under": 47.5, "over_odds": -110, "under_odds": -110},
                },
                momentum_score=0.75,  # Chiefs momentum
            ),
            LiveGame(
                game_id="nba_lal_gsw_20251006",
                home_team="Golden State Warriors",
                away_team="Los Angeles Lakers",
                sport="NBA",
                league="NBA",
                start_time=datetime.now(UTC),
                current_period="Q1",
                time_remaining="4:22",
                home_score=28,
                away_score=24,
                live_odds={
                    "moneyline": {"home": -150, "away": 125},
                    "spread": {"home": -2.5, "away": 2.5, "home_odds": -110, "away_odds": -110},
                    "total": {"over": 225.5, "under": 225.5, "over_odds": -115, "under_odds": -105},
                },
                momentum_score=0.60,  # Warriors slight momentum
            ),
            LiveGame(
                game_id="mlb_lad_sd_20251006",
                home_team="San Diego Padres",
                away_team="Los Angeles Dodgers",
                sport="MLB",
                league="MLB",
                start_time=datetime.now(UTC),
                current_period="7th",
                time_remaining="Top 7th",
                home_score=3,
                away_score=5,
                live_odds={
                    "moneyline": {"home": 220, "away": -260},
                    "spread": {"home": 1.5, "away": -1.5, "home_odds": -120, "away_odds": 100},
                    "total": {"over": 8.5, "under": 8.5, "over_odds": -105, "under_odds": -115},
                },
                momentum_score=0.85,  # Dodgers strong momentum
            ),
            LiveGame(
                game_id="nhl_bos_tor_20251006",
                home_team="Toronto Maple Leafs",
                away_team="Boston Bruins",
                sport="NHL",
                league="NHL",
                start_time=datetime.now(UTC),
                current_period="2nd",
                time_remaining="12:15",
                home_score=2,
                away_score=1,
                live_odds={
                    "moneyline": {"home": -135, "away": 115},
                    "spread": {"home": -0.5, "away": 0.5, "home_odds": -110, "away_odds": -110},
                    "total": {"over": 6.5, "under": 6.5, "over_odds": -110, "under_odds": -110},
                },
                momentum_score=0.65,  # Leafs momentum
            ),
        ]

        logger.info(f"Retrieved {len(live_games)} live games")
        return live_games


class ParlayOptimizer:
    """Optimize parlay combinations for target ROI"""

    def __init__(self, target_stake: float = 8.0, target_roi: float = 10.0):
        self.target_stake = target_stake
        self.target_roi = target_roi
        self.target_payout = target_stake * target_roi  # $80
        self.min_odds = target_roi * 100 + 100  # +1000 American odds minimum

    def american_to_decimal(self, american_odds: float) -> float:
        """Convert American odds to decimal"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1

    def calculate_leg_probability(self, decimal_odds: float) -> float:
        """Estimate true probability with vig removal"""
        implied_prob = 1 / decimal_odds
        # Simple vig removal (assume 5% vig)
        return implied_prob * 1.05

    def generate_parlay_legs(self, games: list[LiveGame]) -> list[ParlayLeg]:
        """Generate all possible parlay legs from live games"""
        legs = []

        for game in games:
            game_legs = []

            # Moneyline legs
            if "moneyline" in game.live_odds:
                ml_odds = game.live_odds["moneyline"]

                # Home ML
                home_decimal = self.american_to_decimal(ml_odds["home"])
                home_prob = self.calculate_leg_probability(home_decimal)
                home_ev = calculate_ev(home_prob, home_decimal)

                game_legs.append(
                    ParlayLeg(
                        game_id=game.game_id,
                        selection=f"{game.home_team} ML",
                        market_type="moneyline",
                        odds=home_decimal,
                        probability=home_prob,
                        ev_percent=home_ev * 100,
                        sportsbook="live_feed",
                    )
                )

                # Away ML
                away_decimal = self.american_to_decimal(ml_odds["away"])
                away_prob = self.calculate_leg_probability(away_decimal)
                away_ev = calculate_ev(away_prob, away_decimal)

                game_legs.append(
                    ParlayLeg(
                        game_id=game.game_id,
                        selection=f"{game.away_team} ML",
                        market_type="moneyline",
                        odds=away_decimal,
                        probability=away_prob,
                        ev_percent=away_ev * 100,
                        sportsbook="live_feed",
                    )
                )

            # Spread legs (only add if EV > 0%)
            if "spread" in game.live_odds:
                spread_odds = game.live_odds["spread"]

                # Home spread
                home_spread_decimal = self.american_to_decimal(spread_odds.get("home_odds", -110))
                home_spread_prob = self.calculate_leg_probability(home_spread_decimal)
                home_spread_ev = calculate_ev(home_spread_prob, home_spread_decimal)

                if home_spread_ev > 0:
                    game_legs.append(
                        ParlayLeg(
                            game_id=game.game_id,
                            selection=f"{game.home_team} {spread_odds['home']:+}",
                            market_type="spread",
                            odds=home_spread_decimal,
                            probability=home_spread_prob,
                            ev_percent=home_spread_ev * 100,
                            sportsbook="live_feed",
                        )
                    )

            # Total legs (only add if EV > 0%)
            if "total" in game.live_odds:
                total_odds = game.live_odds["total"]

                # Over
                over_decimal = self.american_to_decimal(total_odds.get("over_odds", -110))
                over_prob = self.calculate_leg_probability(over_decimal)
                over_ev = calculate_ev(over_prob, over_decimal)

                if over_ev > 0:
                    game_legs.append(
                        ParlayLeg(
                            game_id=game.game_id,
                            selection=f"Over {total_odds['over']}",
                            market_type="total",
                            odds=over_decimal,
                            probability=over_prob,
                            ev_percent=over_ev * 100,
                            sportsbook="live_feed",
                        )
                    )

            # Only add legs with positive EV for this game
            positive_ev_legs = [leg for leg in game_legs if leg.ev_percent > 0.5]
            legs.extend(positive_ev_legs)

        logger.info(f"Generated {len(legs)} positive EV legs from {len(games)} games")
        return legs

    def find_optimal_parlays(self, legs: list[ParlayLeg], max_legs: int = 4) -> list[OptimalParlay]:
        """Find optimal parlay combinations for target ROI"""
        optimal_parlays = []

        # Try 2-leg combinations
        for i in range(len(legs)):
            for j in range(i + 1, len(legs)):
                parlay = self._evaluate_parlay([legs[i], legs[j]])
                if parlay and parlay.roi_multiple >= 8.0:  # At least 8x ROI
                    optimal_parlays.append(parlay)

        # Try 3-leg combinations (most promising 2-leg combos)
        optimal_parlays.sort(key=lambda x: x.expected_value, reverse=True)
        top_2leg_legs = set()
        for parlay in optimal_parlays[:10]:  # Top 10 2-leg parlays
            for leg in parlay.legs:
                top_2leg_legs.add((leg.game_id, leg.selection))

        top_legs = [leg for leg in legs if (leg.game_id, leg.selection) in top_2leg_legs]

        for i in range(len(top_legs)):
            for j in range(i + 1, len(top_legs)):
                for k in range(j + 1, len(top_legs)):
                    parlay = self._evaluate_parlay([top_legs[i], top_legs[j], top_legs[k]])
                    if parlay and parlay.roi_multiple >= 9.0:  # Higher bar for 3-leg
                        optimal_parlays.append(parlay)

        # Try 4-leg combinations (only best legs)
        best_legs = sorted(legs, key=lambda x: x.ev_percent, reverse=True)[:8]

        for i in range(len(best_legs)):
            for j in range(i + 1, len(best_legs)):
                for k in range(j + 1, len(best_legs)):
                    for l in range(k + 1, len(best_legs)):
                        parlay = self._evaluate_parlay(
                            [best_legs[i], best_legs[j], best_legs[k], best_legs[l]]
                        )
                        if parlay and parlay.roi_multiple >= 10.0:  # Target ROI for 4-leg
                            optimal_parlays.append(parlay)

        # Sort by EV and return top candidates
        optimal_parlays.sort(key=lambda x: (x.roi_multiple, x.expected_value), reverse=True)

        logger.info(f"Found {len(optimal_parlays)} optimal parlay opportunities")
        return optimal_parlays[:10]  # Return top 10

    def _evaluate_parlay(self, legs: list[ParlayLeg]) -> OptimalParlay | None:
        """Evaluate a specific parlay combination"""
        if len(legs) < 2:
            return None

        # Check for same-game conflicts
        if self._has_same_game_conflicts(legs):
            return None

        # Calculate parlay odds
        total_odds = 1.0
        for leg in legs:
            total_odds *= leg.odds

        # Check if meets minimum odds requirement
        if total_odds < (self.target_roi * 0.8):  # 80% of target as threshold
            return None

        # Calculate joint probability
        probabilities = [leg.probability for leg in legs]
        joint_prob = independent_parlay_probability(probabilities)

        # Calculate expected value
        potential_payout = self.target_stake * (total_odds - 1)
        expected_value = joint_prob * potential_payout - (1 - joint_prob) * self.target_stake
        ev_percent = (expected_value / self.target_stake) * 100

        # Risk scoring
        risk_score = self._calculate_risk_score(legs, joint_prob)

        # Confidence scoring
        confidence = self._calculate_confidence(legs, risk_score, ev_percent)

        # ROI multiple
        roi_multiple = potential_payout / self.target_stake

        # Generate reasoning
        reasoning = self._generate_reasoning(legs, total_odds, joint_prob, ev_percent)

        return OptimalParlay(
            legs=legs,
            total_odds=total_odds,
            joint_probability=joint_prob,
            expected_value=expected_value,
            roi_multiple=roi_multiple,
            stake_amount=self.target_stake,
            potential_payout=potential_payout + self.target_stake,
            risk_score=risk_score,
            confidence=confidence,
            reasoning=reasoning,
        )

    def _has_same_game_conflicts(self, legs: list[ParlayLeg]) -> bool:
        """Check for conflicting bets in same game"""
        game_markets = {}

        for leg in legs:
            if leg.game_id not in game_markets:
                game_markets[leg.game_id] = []
            game_markets[leg.game_id].append(leg.market_type)

        # Check for multiple legs from same game
        for _game_id, markets in game_markets.items():
            if len(markets) > 1:
                # Allow some combinations, forbid others
                if "moneyline" in markets and ("spread" in markets or "total" in markets):
                    return True  # Too correlated

        return False

    def _calculate_risk_score(self, legs: list[ParlayLeg], joint_prob: float) -> float:
        """Calculate risk score (0-100, lower is better)"""
        base_risk = (1 - joint_prob) * 100  # Base probability risk

        # Add complexity risk
        complexity_risk = len(legs) * 5  # 5 points per leg

        # Add correlation risk
        correlation_risk = 0
        games = {leg.game_id for leg in legs}
        if len(games) < len(legs):  # Same game parlay
            correlation_risk = 20

        # Add low EV risk
        avg_ev = np.mean([leg.ev_percent for leg in legs])
        if avg_ev < 2.0:
            correlation_risk += 10

        total_risk = min(base_risk + complexity_risk + correlation_risk, 100)
        return total_risk

    def _calculate_confidence(
        self, legs: list[ParlayLeg], risk_score: float, ev_percent: float
    ) -> float:
        """Calculate confidence score (0-100, higher is better)"""
        # Base confidence from EV
        ev_confidence = min(ev_percent * 2, 40)  # Cap at 40

        # Leg quality confidence
        avg_leg_ev = np.mean([leg.ev_percent for leg in legs])
        leg_confidence = min(avg_leg_ev * 5, 30)  # Cap at 30

        # Risk adjustment
        risk_adjustment = (100 - risk_score) * 0.3  # Max 30 from risk

        total_confidence = min(ev_confidence + leg_confidence + risk_adjustment, 100)
        return total_confidence

    def _generate_reasoning(
        self, legs: list[ParlayLeg], total_odds: float, joint_prob: float, ev_percent: float
    ) -> str:
        """Generate human-readable reasoning for parlay"""
        leg_count = len(legs)
        american_odds = (
            int((total_odds - 1) * 100) if total_odds >= 2 else int(-100 / (total_odds - 1))
        )

        reasoning = (
            f"{leg_count}-leg parlay ({american_odds:+}) with {joint_prob:.1%} hit probability. "
        )

        high_ev_legs = [leg for leg in legs if leg.ev_percent > 3.0]
        if high_ev_legs:
            reasoning += f"Strong value on {len(high_ev_legs)} legs. "

        if ev_percent > 5.0:
            reasoning += f"Excellent {ev_percent:.1f}% expected value. "
        elif ev_percent > 0:
            reasoning += f"Positive {ev_percent:.1f}% expected value. "

        # Mention best leg
        best_leg = max(legs, key=lambda x: x.ev_percent)
        reasoning += f"Anchor: {best_leg.selection} ({best_leg.ev_percent:.1f}% EV)."

        return reasoning


class EQ12LiveParlayScanner:
    """Main live parlay scanning engine"""

    def __init__(self):
        self.odds_provider = LiveOddsProvider()
        self.parlay_optimizer = ParlayOptimizer(target_stake=8.0, target_roi=10.0)
        self.scan_interval = 30  # seconds
        self.running = False

    async def start_scanning(self):
        """Start continuous parlay scanning"""
        logger.info("🎯 EQ12 Live Parlay Scanner Started")
        logger.info("Target: $8 → $80 (10x ROI)")
        logger.info(f"Scanning every {self.scan_interval} seconds")

        self.running = True

        while self.running:
            try:
                await self._scan_cycle()
                await asyncio.sleep(self.scan_interval)
            except KeyboardInterrupt:
                logger.info("Scan interrupted by user")
                break
            except Exception as e:
                logger.error(f"Scan cycle error: {e}")
                await asyncio.sleep(5)  # Short delay on error

    async def _scan_cycle(self):
        """Single scan cycle"""
        logger.info("🔍 Starting scan cycle...")

        # Get live games
        games = await self.odds_provider.get_live_games()
        if not games:
            logger.warning("No live games found")
            return

        # Generate parlay legs
        legs = self.parlay_optimizer.generate_parlay_legs(games)
        if not legs:
            logger.warning("No positive EV legs found")
            return

        # Find optimal parlays
        optimal_parlays = self.parlay_optimizer.find_optimal_parlays(legs)

        if optimal_parlays:
            logger.info(f"🎉 Found {len(optimal_parlays)} optimal parlays!")

            # Display top 3 parlays
            for i, parlay in enumerate(optimal_parlays[:3]):
                self._display_parlay(i + 1, parlay)

            # Save to file for further analysis
            self._save_parlays(optimal_parlays)
        else:
            logger.info("📊 No parlays meeting 10x ROI criteria found")

    def _display_parlay(self, rank: int, parlay: OptimalParlay):
        """Display parlay information"""
        print(f"\n🏆 OPTIMAL PARLAY #{rank}")
        print(f"{'=' * 50}")
        print(f"💰 Stake: ${parlay.stake_amount:.0f}")
        print(f"🎯 Payout: ${parlay.potential_payout:.0f}")
        print(f"📈 ROI: {parlay.roi_multiple:.1f}x")
        print(f"🎲 Odds: +{int((parlay.total_odds - 1) * 100)}")
        print(f"📊 Hit Probability: {parlay.joint_probability:.1%}")
        print(f"💡 Expected Value: {parlay.expected_value:.1f}% ")
        print(f"⚠️  Risk Score: {parlay.risk_score:.0f}/100")
        print(f"✅ Confidence: {parlay.confidence:.0f}/100")
        print("\n📝 LEGS:")
        for i, leg in enumerate(parlay.legs, 1):
            print(f"  {i}. {leg.selection} @ {leg.odds:.2f} ({leg.ev_percent:.1f}% EV)")
        print(f"\n💭 Reasoning: {parlay.reasoning}")
        print(f"{'=' * 50}")

    def _save_parlays(self, parlays: list[OptimalParlay]):
        """Save parlays to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/eq12_optimal_parlays_{timestamp}.json"

        parlay_data = []
        for parlay in parlays:
            parlay_dict = {
                "timestamp": datetime.now().isoformat(),
                "stake": parlay.stake_amount,
                "potential_payout": parlay.potential_payout,
                "roi_multiple": parlay.roi_multiple,
                "total_odds": parlay.total_odds,
                "joint_probability": parlay.joint_probability,
                "expected_value": parlay.expected_value,
                "risk_score": parlay.risk_score,
                "confidence": parlay.confidence,
                "reasoning": parlay.reasoning,
                "legs": [
                    {
                        "selection": leg.selection,
                        "odds": leg.odds,
                        "probability": leg.probability,
                        "ev_percent": leg.ev_percent,
                        "market_type": leg.market_type,
                        "game_id": leg.game_id,
                    }
                    for leg in parlay.legs
                ],
            }
            parlay_data.append(parlay_dict)

        os.makedirs("logs", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(parlay_data, f, indent=2)

        logger.info(f"💾 Saved {len(parlays)} parlays to {filename}")

    async def scan_once(self):
        """Perform a single scan and return results"""
        await self._scan_cycle()

    def stop_scanning(self):
        """Stop continuous scanning"""
        self.running = False
        logger.info("🛑 Parlay scanner stopped")


async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Live Parlay Scanner")
    parser.add_argument("--once", action="store_true", help="Run scan once and exit")
    parser.add_argument("--stake", type=float, default=8.0, help="Bet stake amount")
    parser.add_argument("--roi", type=float, default=10.0, help="Target ROI multiple")
    args = parser.parse_args()

    # Initialize scanner
    scanner = EQ12LiveParlayScanner()
    scanner.parlay_optimizer.target_stake = args.stake
    scanner.parlay_optimizer.target_roi = args.roi
    scanner.parlay_optimizer.target_payout = args.stake * args.roi

    if args.once:
        logger.info("🔍 Running single parlay scan...")
        await scanner.scan_once()
    else:
        logger.info("🔄 Starting continuous parlay scanning...")
        await scanner.start_scanning()


if __name__ == "__main__":
    asyncio.run(main())
