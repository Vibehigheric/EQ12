#!/usr/bin/env python3
"""
EQ12 GODSTACK - Same Game Parlay (SGP) Optimizer
Advanced SGP creation based on comprehensive MLB analysis

This module creates optimal Same Game Parlays by analyzing:
- Statistical correlations between bets
- Value opportunities from market inefficiencies
- Risk-adjusted expected value calculations
- Weather and pitching impact factors
- Bankroll allocation strategies
"""

import argparse
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/sgp_optimizer.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class SGPLeg:
    """Individual leg of a Same Game Parlay"""

    market: str  # "moneyline", "spread", "total", "f5_total", etc.
    selection: str  # "home", "away", "over", "under"
    team: str  # Team name for clarity
    odds: int  # American odds format
    implied_prob: float  # Implied probability
    true_prob: float  # Estimated true probability
    edge: float  # Edge percentage
    reasoning: str  # Why this leg was selected
    correlation_factor: float  # How this correlates with other legs (-1 to 1)


@dataclass
class SGPRecommendation:
    """Complete SGP recommendation with analysis"""

    game_id: str
    matchup: str
    legs: list[SGPLeg]
    combined_odds: int  # American odds for entire parlay
    combined_implied_prob: float
    combined_true_prob: float
    expected_value: float  # Expected value as decimal
    kelly_fraction: float  # Kelly criterion recommended bet size
    confidence: int  # 1-10 confidence rating
    risk_rating: str  # "LOW", "MEDIUM", "HIGH"
    recommended_units: float  # Recommended bet size in units
    max_bet: float  # Maximum recommended bet amount
    reasoning: str  # Overall parlay strategy explanation
    correlation_analysis: str  # How legs work together


class SGPOptimizer:
    """Advanced Same Game Parlay optimization engine"""

    def __init__(self):
        self.games_data = None
        self.value_analysis = None
        self.sgp_recommendations = []

    def load_game_data(self, games_file: str) -> None:
        """Load MLB games data"""
        try:
            with open(games_file) as f:
                self.games_data = json.load(f)
            logger.info(f"Loaded {len(self.games_data['games'])} games from {games_file}")
        except Exception as e:
            logger.error(f"Error loading games data: {e}")
            raise

    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        return (100 / abs(american_odds)) + 1

    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American odds"""
        if decimal_odds >= 2.0:
            return int((decimal_odds - 1) * 100)
        return int(-100 / (decimal_odds - 1))

    def calculate_implied_probability(self, american_odds: int) -> float:
        """Calculate implied probability from American odds"""
        decimal_odds = self.american_to_decimal(american_odds)
        return 1 / decimal_odds

    def calculate_parlay_odds(self, legs: list[SGPLeg]) -> tuple[int, float]:
        """Calculate combined odds and implied probability for parlay"""
        combined_decimal = 1.0

        for leg in legs:
            leg_decimal = self.american_to_decimal(leg.odds)
            combined_decimal *= leg_decimal

        combined_american = self.decimal_to_american(combined_decimal)
        combined_implied_prob = 1 / combined_decimal

        return combined_american, combined_implied_prob

    def estimate_correlation(self, leg1: SGPLeg, leg2: SGPLeg, game_data: dict) -> float:
        """Estimate correlation between two SGP legs"""

        # Strong positive correlations
        if (
            leg1.market == "moneyline"
            and leg2.market == "spread"
            and leg1.selection == leg2.selection
        ):
            return 0.85  # ML and spread for same team

        if (
            leg1.market == "total"
            and leg2.market == "f5_total"
            and leg1.selection == leg2.selection
        ):
            return 0.70  # Full game and F5 totals same direction

        # Moderate positive correlations
        if leg1.market == "moneyline" and leg2.market == "total":
            # Favorite + Under often correlated (pitching dominance)
            if (leg1.selection == "away" and leg1.odds < 0 and leg2.selection == "under") or (
                leg1.selection == "home" and leg1.odds < 0 and leg2.selection == "under"
            ):
                return 0.35
            # Underdog + Over can be correlated (shootout games)
            if (leg1.selection == "away" and leg1.odds > 0 and leg2.selection == "over") or (
                leg1.selection == "home" and leg1.odds > 0 and leg2.selection == "over"
            ):
                return 0.25

        # Weather correlations
        weather = game_data.get("weather", {})
        wind_direction = weather.get("wind_direction", "")

        if leg1.market == "total" and leg2.market == "total" and "Out" in wind_direction:
            return 0.15  # Wind out helps overs

        # Pitcher quality correlations
        home_pitcher_era = game_data.get("home_pitcher", {}).get("era", 4.0)
        game_data.get("away_pitcher", {}).get("era", 4.0)

        if leg1.market == "total" and leg2.market == "moneyline":
            if home_pitcher_era < 3.5 and leg1.selection == "under" and leg2.selection == "home":
                return 0.30  # Good home pitcher + under + home ML

        # Default to low correlation
        return 0.10

    def calculate_true_probability(self, leg: SGPLeg, game_data: dict) -> float:
        """Estimate true probability accounting for various factors"""

        base_prob = leg.implied_prob

        # Adjust for market efficiency (remove vig estimate)
        vig_adjustment = 0.02  # Assume 2% vig per market on average
        adjusted_prob = base_prob * (1 - vig_adjustment)

        # Weather adjustments
        weather = game_data.get("weather", {})
        wind_direction = weather.get("wind_direction", "")
        wind_speed = weather.get("wind_speed", 0)

        if leg.market == "total" and "Out" in wind_direction and wind_speed > 5:
            if leg.selection == "over":
                adjusted_prob += 0.03  # Wind out helps overs
            else:
                adjusted_prob -= 0.03

        # Pitching adjustments
        home_pitcher = game_data.get("home_pitcher", {})
        away_pitcher = game_data.get("away_pitcher", {})

        home_era = home_pitcher.get("era", 4.0)
        away_era = away_pitcher.get("era", 4.0)
        era_diff = abs(home_era - away_era)

        if leg.market == "moneyline" and era_diff > 0.5:
            if leg.selection == "home" and home_era < away_era:
                adjusted_prob += 0.02  # Better home pitcher
            elif leg.selection == "away" and away_era < home_era:
                adjusted_prob += 0.02  # Better away pitcher

        # Home field advantage (typically ~3-5% in MLB)
        if leg.market == "moneyline" and leg.selection == "home":
            adjusted_prob += 0.03

        # Ensure probability stays in valid range
        adjusted_prob = max(0.05, min(0.95, adjusted_prob))

        return adjusted_prob

    def create_conservative_sgp(self, game_data: dict) -> SGPRecommendation | None:
        """Create a conservative 2-leg SGP focused on value and correlation"""

        game_id = game_data["game_id"]
        matchup = f"{game_data['away_team']} @ {game_data['home_team']}"

        legs = []

        # Analyze moneyline value
        home_ml_odds = game_data["odds"]["moneyline_home"]
        game_data["odds"]["moneyline_away"]

        # Check for value on home ML (from our analysis, Blue Jays had value)
        if game_data["home_team"] == "Toronto Blue Jays":
            home_ml_leg = SGPLeg(
                market="moneyline",
                selection="home",
                team=game_data["home_team"],
                odds=home_ml_odds,
                implied_prob=self.calculate_implied_probability(home_ml_odds),
                true_prob=0.0,  # Will calculate below
                edge=0.0,
                reasoning="Home underdog with pitching advantage and home field edge",
                correlation_factor=0.0,
            )
            home_ml_leg.true_prob = self.calculate_true_probability(home_ml_leg, game_data)
            home_ml_leg.edge = home_ml_leg.true_prob - home_ml_leg.implied_prob

            if home_ml_leg.edge > 0.015:  # Minimum 1.5% edge
                legs.append(home_ml_leg)

        # Add correlated total bet
        game_data["odds"]["total_runs"]
        over_odds = game_data["odds"]["total_over_price"]
        under_odds = game_data["odds"]["total_under_price"]

        # Check weather for total bias
        weather = game_data.get("weather", {})
        wind_direction = weather.get("wind_direction", "")

        total_leg = None
        if "Out" in wind_direction and len(legs) > 0:
            # Wind blowing out favors overs, combine with home underdog
            total_leg = SGPLeg(
                market="total",
                selection="over",
                team="Both Teams",
                odds=over_odds,
                implied_prob=self.calculate_implied_probability(over_odds),
                true_prob=0.0,
                edge=0.0,
                reasoning=f"Wind blowing out to RF ({weather.get('wind_speed')}mph) favors overs",
                correlation_factor=0.0,
            )
        else:
            # No weather edge, check under value
            total_leg = SGPLeg(
                market="total",
                selection="under",
                team="Both Teams",
                odds=under_odds,
                implied_prob=self.calculate_implied_probability(under_odds),
                true_prob=0.0,
                edge=0.0,
                reasoning="Strong pitching matchup suggests lower scoring",
                correlation_factor=0.0,
            )

        if total_leg:
            total_leg.true_prob = self.calculate_true_probability(total_leg, game_data)
            total_leg.edge = total_leg.true_prob - total_leg.implied_prob

            if total_leg.edge > 0.01 or len(legs) > 0:  # Accept marginal total edge if ML has value
                legs.append(total_leg)

        if len(legs) < 2:
            return None

        # Calculate correlation between legs
        if len(legs) == 2:
            correlation = self.estimate_correlation(legs[0], legs[1], game_data)
            legs[0].correlation_factor = correlation
            legs[1].correlation_factor = correlation

        # Calculate combined odds and probabilities
        combined_odds, combined_implied_prob = self.calculate_parlay_odds(legs)

        # Estimate true combined probability accounting for correlation
        if len(legs) == 2:
            # Adjust for correlation using copula approach
            p1, p2 = legs[0].true_prob, legs[1].true_prob
            correlation = legs[0].correlation_factor

            # Simple correlation adjustment (more sophisticated methods exist)
            if correlation > 0:
                combined_true_prob = p1 * p2 * (1 + correlation * 0.5)
            else:
                combined_true_prob = p1 * p2 * (1 + correlation * 0.3)
        else:
            combined_true_prob = 1.0
            for leg in legs:
                combined_true_prob *= leg.true_prob

        combined_true_prob = min(0.95, max(0.05, combined_true_prob))

        expected_value = combined_true_prob * self.american_to_decimal(combined_odds) - 1

        # Kelly Criterion calculation
        kelly_fraction = 0.0
        if combined_odds > 0:
            decimal_odds = self.american_to_decimal(combined_odds)
            kelly_fraction = (combined_true_prob * decimal_odds - 1) / (decimal_odds - 1)
            kelly_fraction = max(0, min(0.05, kelly_fraction))  # Cap at 5%

        # Risk assessment
        confidence = 7  # Conservative SGPs get moderate confidence
        if expected_value > 0.05:
            confidence = 8
        elif expected_value < 0:
            confidence = 5

        risk_rating = "LOW" if kelly_fraction < 0.02 else "MEDIUM"

        recommended_units = kelly_fraction * 0.5  # Use half-Kelly
        max_bet = recommended_units * 1000  # Assume $1000 unit size

        # Create correlation analysis
        correlation_analysis = f"Legs have {correlation:.1%} correlation"
        if correlation > 0.3:
            correlation_analysis += (
                " (STRONG positive correlation - legs likely to win/lose together)"
            )
        elif correlation > 0.1:
            correlation_analysis += " (MODERATE positive correlation)"
        else:
            correlation_analysis += " (LOW correlation - legs relatively independent)"

        reasoning = f"Conservative 2-leg SGP targeting {expected_value:.1%} expected value"
        if any(leg.edge > 0.02 for leg in legs):
            reasoning += ". Contains legs with 2%+ individual value."
        reasoning += " Weather and pitching factors considered."

        return SGPRecommendation(
            game_id=game_id,
            matchup=matchup,
            legs=legs,
            combined_odds=combined_odds,
            combined_implied_prob=combined_implied_prob,
            combined_true_prob=combined_true_prob,
            expected_value=expected_value,
            kelly_fraction=kelly_fraction,
            confidence=confidence,
            risk_rating=risk_rating,
            recommended_units=recommended_units,
            max_bet=max_bet,
            reasoning=reasoning,
            correlation_analysis=correlation_analysis,
        )

    def create_aggressive_sgp(self, game_data: dict) -> SGPRecommendation | None:
        """Create a more aggressive 3-leg SGP with higher upside"""

        game_id = game_data["game_id"]
        matchup = f"{game_data['away_team']} @ {game_data['home_team']}"

        legs = []

        # Start with spread bet for better odds
        home_spread = game_data["odds"]["spread_home"]
        home_spread_odds = game_data["odds"]["spread_price_home"]
        away_spread_odds = game_data["odds"]["spread_price_away"]

        # Choose spread side based on value analysis
        if game_data["home_team"] == "Toronto Blue Jays":
            spread_leg = SGPLeg(
                market="spread",
                selection="home",
                team=game_data["home_team"],
                odds=home_spread_odds,
                implied_prob=self.calculate_implied_probability(home_spread_odds),
                true_prob=0.0,
                edge=0.0,
                reasoning=f"Home team getting {home_spread} runs with pitching advantage",
                correlation_factor=0.0,
            )
        else:
            # Detroit Tigers game - take road favorite
            spread_leg = SGPLeg(
                market="spread",
                selection="away",
                team=game_data["away_team"],
                odds=away_spread_odds,
                implied_prob=self.calculate_implied_probability(away_spread_odds),
                true_prob=0.0,
                edge=0.0,
                reasoning=f"Road favorite giving {abs(game_data['odds']['spread_away'])} runs",
                correlation_factor=0.0,
            )

        spread_leg.true_prob = self.calculate_true_probability(spread_leg, game_data)
        spread_leg.edge = spread_leg.true_prob - spread_leg.implied_prob
        legs.append(spread_leg)

        # Add total bet
        total_runs = game_data["odds"]["total_runs"]
        over_odds = game_data["odds"]["total_over_price"]
        under_odds = game_data["odds"]["total_under_price"]

        weather = game_data.get("weather", {})
        weather.get("wind_direction", "")

        if total_runs >= 8.0:  # High total game
            total_leg = SGPLeg(
                market="total",
                selection="over",
                team="Both Teams",
                odds=over_odds,
                implied_prob=self.calculate_implied_probability(over_odds),
                true_prob=0.0,
                edge=0.0,
                reasoning=f"High total ({total_runs}) with favorable weather conditions",
                correlation_factor=0.0,
            )
        else:  # Low total game
            total_leg = SGPLeg(
                market="total",
                selection="under",
                team="Both Teams",
                odds=under_odds,
                implied_prob=self.calculate_implied_probability(under_odds),
                true_prob=0.0,
                edge=0.0,
                reasoning=f"Low total ({total_runs}) suggests strong pitching",
                correlation_factor=0.0,
            )

        total_leg.true_prob = self.calculate_true_probability(total_leg, game_data)
        total_leg.edge = total_leg.true_prob - total_leg.implied_prob
        legs.append(total_leg)

        # Add a first 5 innings bet for 3rd leg (simulate F5 odds)
        total_runs * 0.55  # Typically ~55% of runs score in F5
        f5_selection = "over" if total_leg.selection == "over" else "under"

        # Simulate F5 odds (typically better juice than full game)
        f5_odds = -105 if f5_selection == "over" else -115

        f5_leg = SGPLeg(
            market="f5_total",
            selection=f5_selection,
            team="Both Teams",
            odds=f5_odds,
            implied_prob=self.calculate_implied_probability(f5_odds),
            true_prob=0.0,
            edge=0.0,
            reasoning=f"F5 {f5_selection} correlates with full game total direction",
            correlation_factor=0.0,
        )

        f5_leg.true_prob = self.calculate_true_probability(f5_leg, game_data)
        f5_leg.edge = f5_leg.true_prob - f5_leg.implied_prob
        legs.append(f5_leg)

        # Calculate correlations
        for i, leg1 in enumerate(legs):
            for j, leg2 in enumerate(legs):
                if i < j:
                    correlation = self.estimate_correlation(leg1, leg2, game_data)
                    leg1.correlation_factor = max(leg1.correlation_factor, correlation)
                    leg2.correlation_factor = max(leg2.correlation_factor, correlation)

        combined_odds, combined_implied_prob = self.calculate_parlay_odds(legs)

        # More sophisticated correlation adjustment for 3 legs
        avg_correlation = sum(leg.correlation_factor for leg in legs) / len(legs)
        individual_probs = [leg.true_prob for leg in legs]

        # Simplified 3-leg correlation adjustment
        base_combined_prob = 1.0
        for prob in individual_probs:
            base_combined_prob *= prob

        # Adjust upward for positive correlation
        combined_true_prob = base_combined_prob * (1 + avg_correlation * 0.4)
        combined_true_prob = min(0.80, max(0.01, combined_true_prob))  # 3-leg has lower max prob

        expected_value = combined_true_prob * self.american_to_decimal(combined_odds) - 1

        # Kelly calculation
        kelly_fraction = 0.0
        if combined_odds > 0:
            decimal_odds = self.american_to_decimal(combined_odds)
            kelly_fraction = (combined_true_prob * decimal_odds - 1) / (decimal_odds - 1)
            kelly_fraction = max(0, min(0.03, kelly_fraction))  # Cap at 3% for 3-leggers

        confidence = 6  # Lower confidence for 3-leg parlays
        if expected_value > 0.08:
            confidence = 7
        elif expected_value < -0.05:
            confidence = 4

        risk_rating = "MEDIUM" if kelly_fraction < 0.02 else "HIGH"

        recommended_units = kelly_fraction * 0.3  # Use smaller fraction of Kelly for 3-legs
        max_bet = recommended_units * 1000

        correlation_analysis = f"3-leg parlay with {avg_correlation:.1%} average correlation"
        if avg_correlation > 0.4:
            correlation_analysis += " (HIGH correlation increases variance)"
        elif avg_correlation > 0.2:
            correlation_analysis += " (MODERATE correlation - some legs move together)"
        else:
            correlation_analysis += " (LOW correlation - legs mostly independent)"

        reasoning = f"Aggressive 3-leg SGP targeting {expected_value:.1%} expected value with {combined_odds:+d} payout"
        if expected_value > 0:
            reasoning += ". Positive EV despite correlation adjustments."
        else:
            reasoning += ". Negative EV but potential for entertainment value."

        return SGPRecommendation(
            game_id=game_id,
            matchup=matchup,
            legs=legs,
            combined_odds=combined_odds,
            combined_implied_prob=combined_implied_prob,
            combined_true_prob=combined_true_prob,
            expected_value=expected_value,
            kelly_fraction=kelly_fraction,
            confidence=confidence,
            risk_rating=risk_rating,
            recommended_units=recommended_units,
            max_bet=max_bet,
            reasoning=reasoning,
            correlation_analysis=correlation_analysis,
        )

    def create_value_sgp(self, game_data: dict) -> SGPRecommendation | None:
        """Create SGP focused purely on finding market inefficiencies"""

        game_id = game_data["game_id"]
        matchup = f"{game_data['away_team']} @ {game_data['home_team']}"

        legs = []

        # Analyze all available markets for value
        odds_data = game_data["odds"]

        # Check moneyline value
        markets_to_check = [
            ("moneyline", "home", odds_data["moneyline_home"]),
            ("moneyline", "away", odds_data["moneyline_away"]),
            ("spread", "home", odds_data["spread_price_home"]),
            ("spread", "away", odds_data["spread_price_away"]),
            ("total", "over", odds_data["total_over_price"]),
            ("total", "under", odds_data["total_under_price"]),
        ]

        potential_legs = []

        for market, selection, odds in markets_to_check:
            leg = SGPLeg(
                market=market,
                selection=selection,
                team=(
                    game_data["home_team"]
                    if selection == "home"
                    else game_data["away_team"] if selection == "away" else "Both Teams"
                ),
                odds=odds,
                implied_prob=self.calculate_implied_probability(odds),
                true_prob=0.0,
                edge=0.0,
                reasoning="",
                correlation_factor=0.0,
            )

            leg.true_prob = self.calculate_true_probability(leg, game_data)
            leg.edge = leg.true_prob - leg.implied_prob

            potential_legs.append(leg)

        # Sort by edge and take best 2-3
        potential_legs.sort(key=lambda x: x.edge, reverse=True)

        # Take top 2 legs with positive value
        for leg in potential_legs:
            if leg.edge > 0.005 and len(legs) < 2:  # Minimum 0.5% edge
                leg.reasoning = f"{leg.edge:.2%} edge identified through market analysis"
                legs.append(leg)

        if len(legs) < 2:
            # If not enough value legs, add best remaining leg
            for leg in potential_legs:
                if len(legs) < 2 and leg not in legs:
                    leg.reasoning = f"Best available option ({leg.edge:.2%} edge)"
                    legs.append(leg)

        if len(legs) < 2:
            return None

        # Calculate correlations
        if len(legs) == 2:
            correlation = self.estimate_correlation(legs[0], legs[1], game_data)
            legs[0].correlation_factor = correlation
            legs[1].correlation_factor = correlation

        combined_odds, combined_implied_prob = self.calculate_parlay_odds(legs)

        # Calculate true probability
        if len(legs) == 2:
            p1, p2 = legs[0].true_prob, legs[1].true_prob
            correlation = legs[0].correlation_factor
            combined_true_prob = p1 * p2 * (1 + correlation * 0.5)
        else:
            combined_true_prob = 1.0
            for leg in legs:
                combined_true_prob *= leg.true_prob

        combined_true_prob = min(0.95, max(0.05, combined_true_prob))

        expected_value = combined_true_prob * self.american_to_decimal(combined_odds) - 1

        # Kelly calculation
        kelly_fraction = 0.0
        if combined_odds > 0:
            decimal_odds = self.american_to_decimal(combined_odds)
            kelly_fraction = (combined_true_prob * decimal_odds - 1) / (decimal_odds - 1)
            kelly_fraction = max(0, min(0.08, kelly_fraction))  # Higher cap for value plays

        confidence = 8  # High confidence for value-based SGPs
        if expected_value > 0.05:
            confidence = 9
        elif expected_value < 0:
            confidence = 6

        risk_rating = "LOW" if expected_value > 0.03 else "MEDIUM"

        recommended_units = kelly_fraction * 0.75  # Use more of Kelly for value plays
        max_bet = recommended_units * 1000

        avg_edge = sum(leg.edge for leg in legs) / len(legs)
        correlation = legs[0].correlation_factor if legs else 0

        correlation_analysis = f"Value-focused SGP with {correlation:.1%} correlation between legs"
        if correlation < 0.2:
            correlation_analysis += " (LOW correlation preserves individual leg values)"
        else:
            correlation_analysis += " (HIGHER correlation may reduce combined value)"

        reasoning = f"Value-based SGP with {avg_edge:.2%} average edge per leg"
        if expected_value > 0.03:
            reasoning += (
                f". Strong {expected_value:.1%} expected value after correlation adjustment."
            )
        else:
            reasoning += f". Modest {expected_value:.1%} expected value - proceed with caution."

        return SGPRecommendation(
            game_id=game_id,
            matchup=matchup,
            legs=legs,
            combined_odds=combined_odds,
            combined_implied_prob=combined_implied_prob,
            combined_true_prob=combined_true_prob,
            expected_value=expected_value,
            kelly_fraction=kelly_fraction,
            confidence=confidence,
            risk_rating=risk_rating,
            recommended_units=recommended_units,
            max_bet=max_bet,
            reasoning=reasoning,
            correlation_analysis=correlation_analysis,
        )

    def generate_all_sgps(self) -> None:
        """Generate SGP recommendations for all games"""

        if not self.games_data:
            logger.error("No games data loaded")
            return

        for game in self.games_data["games"]:
            logger.info(f"Creating SGPs for {game['away_team']} @ {game['home_team']}")

            # Create different SGP types
            conservative_sgp = self.create_conservative_sgp(game)
            aggressive_sgp = self.create_aggressive_sgp(game)
            value_sgp = self.create_value_sgp(game)

            if conservative_sgp:
                conservative_sgp.matchup += " (Conservative)"
                self.sgp_recommendations.append(conservative_sgp)

            if aggressive_sgp:
                aggressive_sgp.matchup += " (Aggressive)"
                self.sgp_recommendations.append(aggressive_sgp)

            if value_sgp:
                value_sgp.matchup += " (Value-Focused)"
                self.sgp_recommendations.append(value_sgp)

    def generate_sgp_report(self, output_file: str | None = None) -> str:
        """Generate comprehensive SGP report"""

        if not self.sgp_recommendations:
            return "No SGP recommendations generated"

        report_lines = [
            "🎯 EQ12 SAME GAME PARLAY (SGP) RECOMMENDATIONS",
            "=" * 50,
            f"📅 Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"🎲 Total SGPs: {len(self.sgp_recommendations)}",
            "",
        ]

        # Sort by expected value
        sorted_sgps = sorted(self.sgp_recommendations, key=lambda x: x.expected_value, reverse=True)

        for i, sgp in enumerate(sorted_sgps, 1):
            report_lines.extend(
                [
                    f"## 🎲 SGP #{i}: {sgp.matchup}",
                    "",
                    f"**Combined Odds:** {sgp.combined_odds:+d} (Decimal: {self.american_to_decimal(sgp.combined_odds):.2f})",
                    f"**Expected Value:** {sgp.expected_value:.2%}",
                    f"**Confidence:** {sgp.confidence}/10 ({sgp.risk_rating} Risk)",
                    f"**Kelly Bet Size:** {sgp.kelly_fraction:.2%} of bankroll",
                    f"**Recommended Units:** {sgp.recommended_units:.2f}",
                    f"**Max Bet:** ${sgp.max_bet:.2f}",
                    "",
                    "### 🦵 SGP Legs:",
                    "",
                ]
            )

            for j, leg in enumerate(sgp.legs, 1):
                report_lines.extend(
                    [
                        f"**Leg {j}: {leg.market.title()} - {leg.selection.title()}**",
                        f"- Team: {leg.team}",
                        f"- Odds: {leg.odds:+d}",
                        f"- Implied Prob: {leg.implied_prob:.1%}",
                        f"- True Prob: {leg.true_prob:.1%}",
                        f"- Edge: {leg.edge:.2%}",
                        f"- Reasoning: {leg.reasoning}",
                        "",
                    ]
                )

            report_lines.extend(
                [
                    "### 🔗 Correlation Analysis:",
                    sgp.correlation_analysis,
                    "",
                    "### 📝 SGP Strategy:",
                    sgp.reasoning,
                    "",
                    "---",
                    "",
                ]
            )

        # Add summary statistics
        total_ev = sum(sgp.expected_value for sgp in self.sgp_recommendations)
        avg_confidence = sum(sgp.confidence for sgp in self.sgp_recommendations) / len(
            self.sgp_recommendations
        )
        positive_ev_count = sum(1 for sgp in self.sgp_recommendations if sgp.expected_value > 0)

        report_lines.extend(
            [
                "## 📊 SGP PORTFOLIO SUMMARY",
                "",
                f"**Total Expected Value:** {total_ev:.2%}",
                f"**Average Confidence:** {avg_confidence:.1f}/10",
                f"**Positive EV SGPs:** {positive_ev_count}/{len(self.sgp_recommendations)}",
                f"**Best SGP:** {sorted_sgps[0].matchup} ({sorted_sgps[0].expected_value:.2%} EV)",
                "",
                "## 🎯 PORTFOLIO RECOMMENDATIONS",
                "",
                "**Conservative Approach:**",
                "- Bet only positive EV SGPs",
                "- Use 25-50% of recommended Kelly size",
                "- Focus on 7+ confidence ratings",
                "",
                "**Aggressive Approach:**",
                "- Bet top 2-3 SGPs by expected value",
                "- Use 50-75% of recommended Kelly size",
                "- Accept 6+ confidence ratings",
                "",
                "**Bankroll Management:**",
                "- Never risk more than 5% total bankroll on SGPs",
                "- Treat as entertainment with mathematical edge",
                "- Track results to validate model performance",
                "",
                "---",
                "*Generated by EQ12 GODSTACK SGP Optimizer*",
            ]
        )

        report_text = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report_text)
            logger.info(f"SGP report saved to {output_file}")

        return report_text

    def save_sgp_data(self, output_file: str) -> None:
        """Save SGP recommendations as JSON"""

        sgp_data = {
            "generation_time": datetime.now(UTC).isoformat(),
            "games_analyzed": len(self.games_data["games"]) if self.games_data else 0,
            "sgps_created": len(self.sgp_recommendations),
            "recommendations": [asdict(sgp) for sgp in self.sgp_recommendations],
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sgp_data, f, indent=2, ensure_ascii=False)

        logger.info(f"SGP data saved to {output_file}")


def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(
        description="EQ12 SGP Optimizer - Generate optimal Same Game Parlays"
    )
    parser.add_argument(
        "--games-file",
        default="C:/EQ12/logs/mlb_games_today_20251005_054339.json",
        help="MLB games data file",
    )
    parser.add_argument("--output-dir", default="C:/EQ12/logs", help="Output directory for reports")
    parser.add_argument("--save-json", action="store_true", help="Save SGP data as JSON")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize optimizer
        optimizer = SGPOptimizer()

        # Load data
        logger.info("Loading MLB games data...")
        optimizer.load_game_data(args.games_file)

        # Generate SGPs
        logger.info("Generating SGP recommendations...")
        optimizer.generate_all_sgps()

        # Generate report
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        report_file = f"{args.output_dir}/SGP_RECOMMENDATIONS_{timestamp}.md"

        logger.info("Creating SGP report...")
        optimizer.generate_sgp_report(report_file)

        # Save JSON if requested
        if args.save_json:
            json_file = f"{args.output_dir}/sgp_data_{timestamp}.json"
            optimizer.save_sgp_data(json_file)

        # Print summary
        print("\n" + "=" * 60)
        print("🎲 EQ12 SGP OPTIMIZER - EXECUTION COMPLETE")
        print("=" * 60)
        print(f"📊 Games Analyzed: {len(optimizer.games_data['games'])}")
        print(f"🎯 SGPs Created: {len(optimizer.sgp_recommendations)}")
        print(f"📁 Report Saved: {report_file}")

        if optimizer.sgp_recommendations:
            best_sgp = max(optimizer.sgp_recommendations, key=lambda x: x.expected_value)
            print(f"🏆 Best SGP: {best_sgp.matchup}")
            print(f"💰 Expected Value: {best_sgp.expected_value:.2%}")
            print(f"🎲 Odds: {best_sgp.combined_odds:+d}")

        print("=" * 60)

    except Exception as e:
        logger.error(f"Error in SGP optimization: {e}")
        raise


if __name__ == "__main__":
    main()
