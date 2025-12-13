"""
EQ12 Parlay Optimizer
Advanced parlay optimization with EQ12-specific rules and edge detection

This module implements the core EQ12 betting strategy:
1. No ML + Spread same game conflicts
2. HR props = Over only (edge detection)
3. TB/Hits player marking with star system
4. Auto-lock EV+ parlays (>5% edge)
5. Multi-sport moonshot builders (10-20 legs)
6. Correlation-aware parlay construction
"""

import itertools
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

import numpy as np
import pandas as pd

try:
    from eq12_backtester.core.engine import Bet, BetOutcome, MarketType, Parlay
except ImportError:
    from core.engine import Bet, MarketType
try:
    from eq12_backtester.simulators.sport_simulators import (
        SimulationInput,
        SimulatorFactory,
    )
except ImportError:
    from simulators.sport_simulators import SimulatorFactory

logger = logging.getLogger(__name__)


class ParlayType(Enum):
    """Types of parlays in EQ12 system"""

    SAME_GAME = "same_game"
    MULTI_GAME = "multi_game"
    MULTI_SPORT = "multi_sport"
    MOONSHOT = "moonshot"  # 10+ legs
    LOCK_PARLAY = "lock"  # High confidence EV+ parlay


@dataclass
class ParlayRule:
    """EQ12 parlay construction rule"""

    rule_name: str
    applies_to: list[MarketType]
    restriction_type: str  # 'forbidden', 'required', 'conditional'
    condition: str | None = None
    penalty_score: float = 0.0


@dataclass
class PlayerRating:
    """EQ12 player rating system"""

    player_name: str
    sport: str
    ratings: dict[str, float]  # stat_type -> rating (0-5 stars)
    confidence: float = 0.5
    recent_form: float = 1.0  # Multiplier for recent performance

    def get_star_rating(self, stat_type: str) -> int:
        """Convert rating to star system (1-5 stars)"""
        rating = self.ratings.get(stat_type, 2.5)
        return min(5, max(1, int(rating + 0.5)))


@dataclass
class ParlayCandidate:
    """Potential parlay with scoring"""

    legs: list[Bet]
    parlay_type: ParlayType
    combined_odds: float
    expected_value: float
    confidence_score: float
    rule_violations: list[str] = field(default_factory=list)
    correlation_adjustment: float = 1.0

    @property
    def leg_count(self) -> int:
        return len(self.legs)

    @property
    def is_valid(self) -> bool:
        return len(self.rule_violations) == 0

    @property
    def quality_score(self) -> float:
        """Overall parlay quality score"""
        base_score = self.expected_value * self.confidence_score
        violation_penalty = len(self.rule_violations) * -10.0
        correlation_bonus = (self.correlation_adjustment - 1.0) * 5.0

        return base_score + violation_penalty + correlation_bonus


class EQ12ParlayOptimizer:
    """
    Advanced parlay optimizer implementing EQ12 betting strategy

    Core Features:
    - Rule-based parlay construction
    - EV optimization with Kelly sizing
    - Multi-sport correlation analysis
    - Player star rating integration
    - Automated moonshot generation
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = eq12_root

        # EQ12 parlay rules (hardcoded strategy)
        self.parlay_rules = self._initialize_eq12_rules()

        # Player rating system
        self.player_ratings = self._load_player_ratings()

        # Simulators for EV calculation
        self.simulators = {
            "MLB": SimulatorFactory.get_simulator("MLB"),
            "NFL": SimulatorFactory.get_simulator("NFL"),
            "NBA": SimulatorFactory.get_simulator("NBA"),
        }

        # Parlay limits and thresholds
        self.config = {
            "min_ev_percent": 5.0,  # Minimum EV for auto-lock
            "max_legs_same_game": 4,  # Max legs per same game parlay
            "max_legs_moonshot": 20,  # Max legs for moonshot parlays
            "min_confidence": 0.6,  # Minimum confidence threshold
            "star_threshold": 3,  # Min stars for TB/Hits selection
            "correlation_threshold": 0.3,  # Min correlation for same-game adjustment
        }

        logger.info("EQ12 Parlay Optimizer initialized")

    def _initialize_eq12_rules(self) -> list[ParlayRule]:
        """Initialize EQ12-specific parlay rules"""
        return [
            # Rule 1: No ML + Spread same game
            ParlayRule(
                rule_name="no_ml_spread_same_game",
                applies_to=[
                    MarketType.MLB_MONEYLINE,
                    MarketType.MLB_SPREAD,
                    MarketType.NFL_MONEYLINE,
                    MarketType.NFL_SPREAD,
                    MarketType.NBA_MONEYLINE,
                    MarketType.NBA_SPREAD,
                ],
                restriction_type="forbidden",
                condition="same_game_ml_and_spread",
                penalty_score=100.0,
            ),
            # Rule 2: HR = Over only (EQ12 edge detection)
            ParlayRule(
                rule_name="hr_over_only",
                applies_to=[MarketType.MLB_HR],
                restriction_type="required",
                condition="must_be_over",
                penalty_score=50.0,
            ),
            # Rule 3: TB/Hits require 3+ stars
            ParlayRule(
                rule_name="tb_hits_star_requirement",
                applies_to=[MarketType.MLB_TB, MarketType.MLB_HITS],
                restriction_type="conditional",
                condition="min_3_stars",
                penalty_score=25.0,
            ),
            # Rule 4: Max 3 HR legs per parlay
            ParlayRule(
                rule_name="max_hr_legs",
                applies_to=[MarketType.MLB_HR],
                restriction_type="conditional",
                condition="max_3_per_parlay",
                penalty_score=15.0,
            ),
            # Rule 5: Auto-lock EV+ > 5%
            ParlayRule(
                rule_name="auto_lock_high_ev",
                applies_to=[],  # Applies to all
                restriction_type="conditional",
                condition="ev_above_5_percent",
                penalty_score=0.0,
            ),
        ]

    def _load_player_ratings(self) -> dict[str, PlayerRating]:
        """Load EQ12 player rating system"""
        # In production, this would load from database/CSV
        return {
            "Aaron Judge": PlayerRating(
                player_name="Aaron Judge",
                sport="MLB",
                ratings={
                    "hr": 5.0,  # 5-star HR hitter
                    "tb": 4.5,  # 4.5-star TB producer
                    "hits": 3.5,  # 3.5-star hit rate
                    "k": 2.0,  # High strikeout rate
                },
                confidence=0.9,
                recent_form=1.15,  # Hot streak
            ),
            "Mookie Betts": PlayerRating(
                player_name="Mookie Betts",
                sport="MLB",
                ratings={
                    "hr": 4.0,
                    "tb": 4.8,  # Excellent TB producer
                    "hits": 4.2,  # Great contact hitter
                    "k": 4.0,  # Low strikeout rate
                },
                confidence=0.85,
                recent_form=1.05,
            ),
            "Josh Allen": PlayerRating(
                player_name="Josh Allen",
                sport="NFL",
                ratings={
                    "passing_tds": 4.5,
                    "rushing_tds": 4.0,
                    "passing_yards": 4.2,
                    "interceptions": 2.5,
                },
                confidence=0.88,
            ),
            # More players would be loaded from data
        }

    def optimize_parlay(
        self,
        available_bets: list[Bet],
        parlay_type: ParlayType = ParlayType.MULTI_GAME,
        target_legs: int | None = None,
    ) -> list[ParlayCandidate]:
        """
        Optimize parlay construction based on EQ12 rules

        Args:
            available_bets: Pool of bets to choose from
            parlay_type: Type of parlay to construct
            target_legs: Target number of legs (None for optimization)

        Returns:
            List of optimized parlay candidates, sorted by quality score
        """
        logger.info(f"Optimizing {parlay_type.value} parlay from {len(available_bets)} bets")

        # Filter bets based on EQ12 rules
        eligible_bets = self._filter_bets_by_rules(available_bets)

        # Generate parlay combinations
        if target_legs:
            leg_ranges = [target_legs]
        else:
            if parlay_type == ParlayType.MOONSHOT:
                leg_ranges = range(10, min(21, len(eligible_bets) + 1))
            else:
                leg_ranges = range(2, min(8, len(eligible_bets) + 1))

        parlay_candidates = []

        for num_legs in leg_ranges:
            # Generate combinations
            combinations = itertools.combinations(eligible_bets, num_legs)

            for combo in combinations:
                candidate = self._evaluate_parlay_combination(list(combo), parlay_type)
                if candidate and candidate.is_valid:
                    parlay_candidates.append(candidate)

                # Limit combinations to prevent explosion
                if len(parlay_candidates) > 1000:
                    break

        # Sort by quality score
        parlay_candidates.sort(key=lambda x: x.quality_score, reverse=True)

        logger.info(f"Generated {len(parlay_candidates)} valid parlay candidates")
        return parlay_candidates[:50]  # Return top 50

    def _filter_bets_by_rules(self, bets: list[Bet]) -> list[Bet]:
        """Filter bets based on EQ12 rules"""
        eligible_bets = []

        for bet in bets:
            is_eligible = True

            # Apply HR over-only rule
            if bet.market_type == MarketType.MLB_HR and "Under" in bet.selection:
                is_eligible = False
                continue

            # Apply TB/Hits star requirement
            if bet.market_type in [MarketType.MLB_TB, MarketType.MLB_HITS]:
                player_name = self._extract_player_name(bet.selection)
                if player_name:
                    rating = self.player_ratings.get(player_name)
                    if rating:
                        stat_type = "tb" if bet.market_type == MarketType.MLB_TB else "hits"
                        stars = rating.get_star_rating(stat_type)
                        if stars < self.config["star_threshold"]:
                            is_eligible = False
                            continue

            if is_eligible:
                eligible_bets.append(bet)

        logger.info(f"Filtered {len(bets)} bets down to {len(eligible_bets)} eligible bets")
        return eligible_bets

    def _evaluate_parlay_combination(
        self, legs: list[Bet], parlay_type: ParlayType
    ) -> ParlayCandidate | None:
        """Evaluate a specific parlay combination"""

        # Check rule violations
        violations = self._check_rule_violations(legs, parlay_type)

        # Calculate combined odds
        combined_decimal_odds = 1.0
        for leg in legs:
            combined_decimal_odds *= leg.decimal_odds

        # Convert to American odds
        if combined_decimal_odds >= 2.0:
            combined_odds = (combined_decimal_odds - 1) * 100
        else:
            combined_odds = -100 / (combined_decimal_odds - 1)

        # Calculate expected value
        expected_value = self._calculate_parlay_ev(legs)

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(legs)

        # Calculate correlation adjustment
        correlation_adj = self._calculate_correlation_adjustment(legs)

        candidate = ParlayCandidate(
            legs=legs,
            parlay_type=parlay_type,
            combined_odds=combined_odds,
            expected_value=expected_value,
            confidence_score=confidence_score,
            rule_violations=violations,
            correlation_adjustment=correlation_adj,
        )

        return candidate

    def _check_rule_violations(self, legs: list[Bet], parlay_type: ParlayType) -> list[str]:
        """Check for EQ12 rule violations"""
        violations = []

        # Group legs by game/sport for analysis
        games_map = defaultdict(list)
        for leg in legs:
            game_key = f"{leg.sport}_{getattr(leg, 'game_id', 'unknown')}"
            games_map[game_key].append(leg)

        # Rule 1: No ML + Spread same game
        for game_legs in games_map.values():
            ml_legs = [l for l in game_legs if "MONEYLINE" in l.market_type.value]
            spread_legs = [l for l in game_legs if "SPREAD" in l.market_type.value]

            if ml_legs and spread_legs:
                violations.append("ml_and_spread_same_game")

        # Rule 2: Max 3 HR legs
        hr_legs = [l for l in legs if l.market_type == MarketType.MLB_HR]
        if len(hr_legs) > 3:
            violations.append("too_many_hr_legs")

        # Rule 3: TB/Hits star requirements (already filtered in _filter_bets_by_rules)

        # Rule 4: Same game parlay limits
        if parlay_type == ParlayType.SAME_GAME:
            if len(legs) > self.config["max_legs_same_game"]:
                violations.append("too_many_same_game_legs")

        return violations

    def _calculate_parlay_ev(self, legs: list[Bet]) -> float:
        """Calculate expected value of parlay"""
        # Simplified EV calculation
        # In production, this would use sophisticated models

        total_stake = 100.0  # Assume $100 parlay

        # Calculate true probability using simulators
        true_prob = 1.0
        for leg in legs:
            # Get simulator
            simulator = self.simulators.get(leg.sport)
            if simulator:
                # For now, use implied probability with adjustment
                leg_true_prob = leg.implied_probability * 1.05  # Slight edge assumption
            else:
                leg_true_prob = leg.implied_probability

            true_prob *= leg_true_prob

        # Calculate expected payout
        combined_decimal_odds = 1.0
        for leg in legs:
            combined_decimal_odds *= leg.decimal_odds

        expected_return = true_prob * (total_stake * combined_decimal_odds)
        expected_value = expected_return - total_stake

        return expected_value

    def _calculate_confidence_score(self, legs: list[Bet]) -> float:
        """Calculate confidence score for parlay"""
        if not legs:
            return 0.0

        # Base confidence from individual legs
        leg_confidences = []
        for leg in legs:
            # Use player ratings if available
            player_name = self._extract_player_name(leg.selection)
            if player_name and player_name in self.player_ratings:
                rating = self.player_ratings[player_name]
                confidence = rating.confidence * rating.recent_form
            else:
                # Default confidence based on odds
                if abs(leg.odds) < 150:  # Heavy favorite/strong bet
                    confidence = 0.7
                elif abs(leg.odds) < 300:
                    confidence = 0.6
                else:
                    confidence = 0.4

            leg_confidences.append(confidence)

        # Combined confidence (geometric mean with decay)
        if len(leg_confidences) == 1:
            return leg_confidences[0]

        # Confidence decreases with more legs
        avg_confidence = np.mean(leg_confidences)
        decay_factor = 0.95 ** (len(legs) - 1)

        return avg_confidence * decay_factor

    def _calculate_correlation_adjustment(self, legs: list[Bet]) -> float:
        """Calculate correlation adjustment for parlay"""
        # Simplified correlation model
        # In production, would use sophisticated correlation matrices

        if len(legs) < 2:
            return 1.0

        # Check for same-game correlations
        same_game_pairs = 0
        total_pairs = len(legs) * (len(legs) - 1) / 2

        for i in range(len(legs)):
            for j in range(i + 1, len(legs)):
                leg1, leg2 = legs[i], legs[j]

                # Same sport and potentially same game
                if leg1.sport == leg2.sport:
                    # Check for correlated markets
                    if (
                        leg1.market_type == MarketType.MLB_HR
                        and leg2.market_type == MarketType.MLB_TB
                    ) or (
                        leg1.market_type == MarketType.MLB_TB
                        and leg2.market_type == MarketType.MLB_HITS
                    ):
                        same_game_pairs += 1

        # Positive correlation increases parlay value
        correlation_strength = same_game_pairs / total_pairs if total_pairs > 0 else 0
        adjustment = 1.0 + (correlation_strength * 0.15)  # Max 15% boost

        return adjustment

    def _extract_player_name(self, selection: str) -> str | None:
        """Extract player name from bet selection text"""
        # Simple extraction - in production would be more sophisticated
        if "Over" in selection:
            return selection.split(" Over ")[0]
        if "Under" in selection:
            return selection.split(" Under ")[0]
        # Try to extract first part before market indicator
        parts = selection.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[1]}"

        return None

    def generate_moonshot_parlays(
        self, available_bets: list[Bet], count: int = 5
    ) -> list[ParlayCandidate]:
        """Generate high-odds moonshot parlays (10+ legs)"""
        logger.info(f"Generating {count} moonshot parlays")

        # Filter to highest confidence bets for moonshots
        high_confidence_bets = []
        for bet in available_bets:
            player_name = self._extract_player_name(bet.selection)
            if player_name and player_name in self.player_ratings:
                rating = self.player_ratings[player_name]
                if rating.confidence >= 0.7:  # High confidence only
                    high_confidence_bets.append(bet)

        if len(high_confidence_bets) < 10:
            logger.warning("Insufficient high-confidence bets for moonshots")
            return []

        moonshots = self.optimize_parlay(
            high_confidence_bets, ParlayType.MOONSHOT, target_legs=None
        )

        return moonshots[:count]

    def get_auto_lock_parlays(self, available_bets: list[Bet]) -> list[ParlayCandidate]:
        """Get parlays that meet auto-lock criteria (>5% EV)"""
        all_parlays = self.optimize_parlay(available_bets)

        auto_locks = [
            p
            for p in all_parlays
            if p.expected_value > (self.config["min_ev_percent"] * 0.01 * 100)  # $5 EV on $100 bet
        ]

        logger.info(f"Found {len(auto_locks)} auto-lock parlays")
        return auto_locks

    def export_parlay_recommendations(
        self, parlays: list[ParlayCandidate], filename: str | None = None
    ) -> str:
        """Export parlay recommendations to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eq12_parlay_recommendations_{timestamp}.csv"

        # Convert to DataFrame
        parlay_data = []
        for i, parlay in enumerate(parlays):
            legs_text = " | ".join([f"{leg.selection} ({leg.odds:+g})" for leg in parlay.legs])

            parlay_data.append(
                {
                    "rank": i + 1,
                    "parlay_type": parlay.parlay_type.value,
                    "legs": parlay.leg_count,
                    "combined_odds": f"{parlay.combined_odds:+g}",
                    "expected_value": f"${parlay.expected_value:.2f}",
                    "confidence": f"{parlay.confidence_score:.2f}",
                    "quality_score": f"{parlay.quality_score:.2f}",
                    "violations": (
                        "; ".join(parlay.rule_violations) if parlay.rule_violations else "None"
                    ),
                    "selections": legs_text,
                }
            )

        df = pd.DataFrame(parlay_data)

        # Save to reports directory
        from pathlib import Path

        reports_dir = Path(self.eq12_root) / "eq12_backtester" / "reports"
        reports_dir.mkdir(exist_ok=True)

        filepath = reports_dir / filename
        df.to_csv(filepath, index=False)

        logger.info(f"Exported {len(parlays)} parlay recommendations to {filepath}")
        return str(filepath)


if __name__ == "__main__":
    # Test the parlay optimizer
    print("🎯 EQ12 Parlay Optimizer Test")

    optimizer = EQ12ParlayOptimizer()

    # Create test bets
    test_bets = [
        Bet(
            bet_id="hr1",
            sport="MLB",
            market_type=MarketType.MLB_HR,
            selection="Aaron Judge Over 0.5 HR",
            odds=150,
            stake=50,
        ),
        Bet(
            bet_id="tb1",
            sport="MLB",
            market_type=MarketType.MLB_TB,
            selection="Mookie Betts Over 1.5 TB",
            odds=120,
            stake=50,
        ),
        Bet(
            bet_id="hits1",
            sport="MLB",
            market_type=MarketType.MLB_HITS,
            selection="Mookie Betts Over 0.5 Hits",
            odds=130,
            stake=50,
        ),
        Bet(
            bet_id="nfl1",
            sport="NFL",
            market_type=MarketType.NFL_PROPS,
            selection="Josh Allen Over 1.5 Passing TDs",
            odds=110,
            stake=50,
        ),
    ]

    # Optimize parlays
    parlays = optimizer.optimize_parlay(test_bets, ParlayType.MULTI_SPORT)

    print(f"\nGenerated {len(parlays)} parlay candidates:")
    for i, parlay in enumerate(parlays[:3]):  # Show top 3
        print(f"\nParlay {i + 1}:")
        print(f"  Legs: {parlay.leg_count}")
        print(f"  Combined Odds: {parlay.combined_odds:+g}")
        print(f"  Expected Value: ${parlay.expected_value:.2f}")
        print(f"  Quality Score: {parlay.quality_score:.2f}")
        print("  Selections:")
        for leg in parlay.legs:
            print(f"    - {leg.selection} ({leg.odds:+g})")

    # Test auto-lock detection
    auto_locks = optimizer.get_auto_lock_parlays(test_bets)
    print(f"\nAuto-lock parlays: {len(auto_locks)}")

    logger.info("EQ12 Parlay Optimizer test completed!")
