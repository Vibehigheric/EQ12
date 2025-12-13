#!/usr/bin/env python3
"""
EQ12 Advanced NCAA Week 7 Parlay Generator with Expert Mathematics
Comprehensive parlay generation using odds conversion, Kelly Criterion, and AI analysis
"""

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime

from eq12_betting_mathematics import EQ12BettingMathematics, OddsFormat
from eq12_complete_parlay_analyzer import (
    BetType,
    CompleteParlaySlip,
    DetailedParlayLeg,
    EQ12CompleteParlayDisplaySystem,
)
from eq12_unicode_handler import safe_print


@dataclass
class NCAAGame:
    """NCAA game with comprehensive betting data."""

    game_id: str
    home_team: str
    away_team: str
    conference: str
    week: int
    game_time: datetime

    # Moneyline odds (decimal format)
    home_ml_odds: float
    away_ml_odds: float

    # Spread odds
    home_spread: float
    home_spread_odds: float
    away_spread_odds: float

    # Total (Over/Under)
    total_points: float
    over_odds: float
    under_odds: float

    # Advanced metrics
    home_team_rating: float = 75.0
    away_team_rating: float = 75.0
    weather_factor: float = 1.0
    injury_factor: float = 1.0
    public_betting_percentage: float = 50.0
    sharp_money_indicator: bool = False


class EQ12AdvancedNCAAParlayGenerator:
    """Advanced NCAA parlay generator with expert mathematics integration."""

    def __init__(self):
        self.math_engine = EQ12BettingMathematics()
        self.parlay_system = EQ12CompleteParlayDisplaySystem()
        self.games_data = []
        self.bankroll = 1000.0  # Default bankroll for Kelly calculations

    def load_ncaa_week7_games(self) -> None:
        """Load comprehensive NCAA Week 7 games with realistic data."""
        # ACC Conference Games
        acc_games = [
            NCAAGame(
                game_id="ACC_001_W7",
                home_team="North Carolina Tar Heels",
                away_team="Clemson Tigers",
                conference="ACC",
                week=7,
                game_time=datetime(2025, 10, 4, 16, 0),
                home_ml_odds=2.85,  # +185 ML
                away_ml_odds=1.42,  # -238 ML
                home_spread=6.5,
                home_spread_odds=1.91,
                away_spread_odds=1.91,
                total_points=58.5,
                over_odds=1.87,
                under_odds=1.95,
                home_team_rating=78.5,
                away_team_rating=85.2,
                public_betting_percentage=68.0,
                sharp_money_indicator=True,
            ),
            NCAAGame(
                game_id="ACC_002_W7",
                home_team="Pittsburgh Panthers",
                away_team="Boston College Eagles",
                conference="ACC",
                week=7,
                game_time=datetime(2025, 10, 4, 16, 0),
                home_ml_odds=1.62,  # -162 ML
                away_ml_odds=2.38,  # +138 ML
                home_spread=-3.0,
                home_spread_odds=1.91,
                away_spread_odds=1.91,
                total_points=45.5,
                over_odds=1.91,
                under_odds=1.91,
                home_team_rating=80.1,
                away_team_rating=76.3,
                public_betting_percentage=58.5,
            ),
            NCAAGame(
                game_id="ACC_003_W7",
                home_team="Louisville Cardinals",
                away_team="Virginia Cavaliers",
                conference="ACC",
                week=7,
                game_time=datetime(2025, 10, 4, 19, 30),
                home_ml_odds=1.67,  # -149 ML
                away_ml_odds=2.25,  # +125 ML
                home_spread=-2.5,
                home_spread_odds=1.91,
                away_spread_odds=1.91,
                total_points=52.5,
                over_odds=1.95,
                under_odds=1.87,
                home_team_rating=77.8,
                away_team_rating=75.2,
            ),
        ]

        # SEC Conference Games
        sec_games = [
            NCAAGame(
                game_id="SEC_001_W7",
                home_team="Alabama Crimson Tide",
                away_team="Tennessee Volunteers",
                conference="SEC",
                week=7,
                game_time=datetime(2025, 10, 4, 15, 30),
                home_ml_odds=1.80,  # -125 ML
                away_ml_odds=2.05,  # +105 ML
                home_spread=-1.5,
                home_spread_odds=1.91,
                away_spread_odds=1.91,
                total_points=62.5,
                over_odds=1.91,
                under_odds=1.91,
                home_team_rating=89.5,
                away_team_rating=88.2,
                public_betting_percentage=72.0,
                sharp_money_indicator=True,
            ),
            NCAAGame(
                game_id="SEC_002_W7",
                home_team="Georgia Bulldogs",
                away_team="Auburn Tigers",
                conference="SEC",
                week=7,
                game_time=datetime(2025, 10, 4, 19, 0),
                home_ml_odds=1.45,  # -222 ML
                away_ml_odds=2.75,  # +175 ML
                home_spread=-5.5,
                home_spread_odds=1.91,
                away_spread_odds=1.91,
                total_points=55.5,
                over_odds=1.87,
                under_odds=1.95,
                home_team_rating=91.2,
                away_team_rating=79.8,
            ),
        ]

        # Big 12 Conference Games
        big12_games = [
            NCAAGame(
                game_id="B12_001_W7",
                home_team="Texas Longhorns",
                away_team="Oklahoma Sooners",
                conference="Big 12",
                week=7,
                game_time=datetime(2025, 10, 4, 12, 0),
                home_ml_odds=1.75,  # -133 ML
                away_ml_odds=2.10,  # +110 ML
                home_spread=-2.0,
                home_spread_odds=1.91,
                away_spread_odds=1.91,
                total_points=65.5,
                over_odds=1.95,
                under_odds=1.87,
                home_team_rating=87.5,
                away_team_rating=86.1,
                public_betting_percentage=65.0,
            )
        ]

        self.games_data = acc_games + sec_games + big12_games

    def calculate_true_probabilities(self, game: NCAAGame) -> dict[str, float]:
        """Calculate true probabilities using advanced modeling."""
        # Base probability from team ratings
        rating_diff = game.home_team_rating - game.away_team_rating

        # Home field advantage (typically 2-3 points in college football)
        home_advantage = 2.8
        adjusted_rating_diff = rating_diff + home_advantage

        # Convert rating difference to win probability using logistic function
        # Each point of rating difference ≈ 3% win probability change
        base_home_prob = 0.5 + (adjusted_rating_diff * 0.03)

        # Adjust for weather and injuries
        weather_adj = (game.weather_factor - 1.0) * 0.1
        injury_adj = (game.injury_factor - 1.0) * 0.15

        home_win_prob = max(0.1, min(0.9, base_home_prob + weather_adj + injury_adj))
        away_win_prob = 1.0 - home_win_prob

        # Spread probabilities (assuming normal distribution around spread)
        spread_prob = 0.52 if game.home_spread < 0 else 0.48

        # Total probabilities (slight under bias in college football)
        total_prob = 0.48  # Slight under bias

        return {
            "home_ml": home_win_prob,
            "away_ml": away_win_prob,
            "home_spread": spread_prob,
            "away_spread": 1.0 - spread_prob,
            "over": total_prob,
            "under": 1.0 - total_prob,
        }

    def create_optimal_parlay_leg(
        self, game: NCAAGame, bet_type: BetType, bankroll_fraction: float = 0.02
    ) -> DetailedParlayLeg:
        """Create an optimized parlay leg with Kelly sizing."""
        true_probs = self.calculate_true_probabilities(game)

        # Select odds and probability based on bet type
        if bet_type == BetType.MONEYLINE:
            # Choose the side with better value
            home_conversion = self.math_engine.convert_odds(
                game.home_ml_odds, OddsFormat.DECIMAL, true_probs["home_ml"]
            )
            away_conversion = self.math_engine.convert_odds(
                game.away_ml_odds, OddsFormat.DECIMAL, true_probs["away_ml"]
            )

            if home_conversion.kelly_fraction > away_conversion.kelly_fraction:
                odds = game.home_ml_odds
                pick_team = game.home_team
                true_prob = true_probs["home_ml"]
                conversion = home_conversion
            else:
                odds = game.away_ml_odds
                pick_team = game.away_team
                true_prob = true_probs["away_ml"]
                conversion = away_conversion

            pick_description = f"{pick_team} MONEYLINE"

        elif bet_type == BetType.SPREAD:
            # Always take the side with positive expected value
            home_conversion = self.math_engine.convert_odds(
                game.home_spread_odds, OddsFormat.DECIMAL, true_probs["home_spread"]
            )
            away_conversion = self.math_engine.convert_odds(
                game.away_spread_odds, OddsFormat.DECIMAL, true_probs["away_spread"]
            )

            if home_conversion.edge > away_conversion.edge:
                odds = game.home_spread_odds
                pick_team = game.home_team
                true_prob = true_probs["home_spread"]
                conversion = home_conversion
                spread_line = game.home_spread
            else:
                odds = game.away_spread_odds
                pick_team = game.away_team
                true_prob = true_probs["away_spread"]
                conversion = away_conversion
                spread_line = -game.home_spread

            pick_description = f"{pick_team} SPREAD {spread_line:+.1f}"

        elif bet_type == BetType.OVER_UNDER:
            over_conversion = self.math_engine.convert_odds(
                game.over_odds, OddsFormat.DECIMAL, true_probs["over"]
            )
            under_conversion = self.math_engine.convert_odds(
                game.under_odds, OddsFormat.DECIMAL, true_probs["under"]
            )

            if over_conversion.edge > under_conversion.edge:
                odds = game.over_odds
                pick_description = f"OVER {game.total_points}"
                true_prob = true_probs["over"]
                conversion = over_conversion
            else:
                odds = game.under_odds
                pick_description = f"UNDER {game.total_points}"
                true_prob = true_probs["under"]
                conversion = under_conversion

        # Extract selection and line from pick description
        if bet_type == BetType.MONEYLINE:
            selection = pick_team
            line = None
        elif bet_type == BetType.SPREAD:
            selection = pick_team
            line = spread_line
        else:  # OVER_UNDER
            selection = "OVER" if "OVER" in pick_description else "UNDER"
            line = game.total_points

        # Create the leg with all calculations
        return DetailedParlayLeg(
            game_id=game.game_id,
            sport="NCAAF",
            conference=game.conference,
            matchup=f"{game.away_team} @ {game.home_team}",
            home_team=game.home_team,
            away_team=game.away_team,
            bet_type=bet_type,
            selection=selection,
            line=line,
            odds=odds,
            confidence=true_prob,
            edge_percentage=conversion.edge * 100 if conversion.edge else 0,
            kelly_percentage=conversion.kelly_fraction,
            sentiment=0.6 + random.uniform(-0.2, 0.2),
            steam_detected=game.sharp_money_indicator,
            bookmaker="EQ12 Optimal",
            market="h2h" if bet_type == BetType.MONEYLINE else "spread",
            start_time=game.game_time.isoformat() + "Z",
            is_top25=game.home_team_rating > 85 or game.away_team_rating > 85,
        )

    def generate_conference_parlays(
        self, conference: str, parlay_types: list[str]
    ) -> list[CompleteParlaySlip]:
        """Generate optimized parlays for a specific conference."""
        conference_games = [g for g in self.games_data if g.conference == conference]
        parlays = []

        for parlay_type in parlay_types:
            if parlay_type == "MONEYLINE_VALUE":
                # High-value moneyline parlay
                legs = []
                for game in conference_games[:4]:  # Max 4 legs for value parlays
                    leg = self.create_optimal_parlay_leg(game, BetType.MONEYLINE)
                    if leg.edge_percentage > 2.0:  # Only positive edge bets
                        legs.append(leg)

                if len(legs) >= 2:
                    parlay = self._create_parlay_slip(legs, conference, parlay_type)
                    parlays.append(parlay)

            elif parlay_type == "SPREAD_SYSTEM":
                # Spread-based system parlay
                legs = []
                for game in conference_games:
                    leg = self.create_optimal_parlay_leg(game, BetType.SPREAD)
                    if leg.kelly_percentage > 0.01:  # Kelly suggests betting
                        legs.append(leg)

                if len(legs) >= 3:
                    parlay = self._create_parlay_slip(legs[:5], conference, parlay_type)
                    parlays.append(parlay)

            elif parlay_type == "TOTAL_SHARP":
                # Over/Under sharp money parlay
                legs = []
                for game in conference_games:
                    if game.sharp_money_indicator:  # Only sharp money games
                        leg = self.create_optimal_parlay_leg(game, BetType.OVER_UNDER)
                        legs.append(leg)

                if len(legs) >= 2:
                    parlay = self._create_parlay_slip(legs, conference, parlay_type)
                    parlays.append(parlay)

        return parlays

    def _create_parlay_slip(
        self, legs: list[DetailedParlayLeg], conference: str, parlay_type: str
    ) -> CompleteParlaySlip:
        """Create a complete parlay slip with advanced calculations."""
        # Calculate combined odds using betting mathematics
        individual_odds = [leg.odds for leg in legs]
        combined_odds = self.math_engine.calculate_parlay_odds(individual_odds)

        # Calculate true probability
        individual_probs = [leg.confidence for leg in legs]
        true_prob = self.math_engine.calculate_parlay_probability(individual_probs)

        # Calculate expected value and Kelly sizing
        parlay_conversion = self.math_engine.convert_odds(
            combined_odds, OddsFormat.DECIMAL, true_prob
        )

        # Calculate metrics
        expected_roi = (parlay_conversion.edge * 100) if parlay_conversion.edge else 0
        kelly_stake = (
            (parlay_conversion.kelly_fraction * self.bankroll)
            if parlay_conversion.kelly_fraction
            else 0
        )
        risk_score = min(0.95, 0.3 + (len(legs) * 0.1))  # Higher risk with more legs

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parlay_id = f"{conference}_{parlay_type}_Week7_{timestamp}"

        return CompleteParlaySlip(
            parlay_id=parlay_id,
            conference=conference,
            parlay_type=parlay_type,
            week=7,
            generated_at=datetime.now().isoformat(),
            legs=legs,
            combined_odds=combined_odds,
            win_probability=true_prob,
            expected_roi=expected_roi,
            recommended_stake=kelly_stake,
            total_edge=sum(leg.edge_percentage for leg in legs),
            risk_score=risk_score,
        )


async def main():
    """Run comprehensive NCAA Week 7 parlay generation."""
    safe_print("🏈 EQ12 Advanced NCAA Week 7 Parlay Generator")
    safe_print("=" * 60)

    # Initialize generator
    generator = EQ12AdvancedNCAAParlayGenerator()

    # Load games data
    safe_print("📊 Loading NCAA Week 7 games...")
    generator.load_ncaa_week7_games()
    safe_print("   Loaded {len(generator.games_data)} games")

    # Test betting mathematics
    safe_print("\n🧮 Testing Betting Mathematics...")
    test_odds = generator.math_engine.convert_odds(2.50, OddsFormat.DECIMAL, 0.45)
    safe_print(f"   Decimal 2.50 → ML: {test_odds.moneyline:+d}, Edge: {test_odds.edge:.3f}")

    # Generate parlays for each conference
    all_parlays = []
    conferences = ["ACC", "SEC", "Big 12"]
    parlay_types = ["MONEYLINE_VALUE", "SPREAD_SYSTEM", "TOTAL_SHARP"]

    for conference in conferences:
        safe_print("\n🏟️ Generating {conference} parlays...")
        conference_parlays = generator.generate_conference_parlays(conference, parlay_types)
        all_parlays.extend(conference_parlays)
        safe_print("   Generated {len(conference_parlays)} optimized parlays")

    # Display all parlays using the complete system
    safe_print("\n🎯 Analyzing {len(all_parlays)} NCAA Week 7 Parlays...")
    safe_print("=" * 60)

    analyzer = EQ12CompleteParlayDisplaySystem()

    for i, parlay in enumerate(all_parlays, 1):
        safe_print(f"\n==================== SLIP {i}/{len(all_parlays)} ====================")
        analyzer.display_complete_parlay_slip(parlay)

        # AI Analysis
        try:
            analysis = await analyzer.ai_analyze_parlay(parlay, "pre_game_validation")
            safe_print("\n🤖 **AI ANALYSIS FOR SLIP {i}**")
            safe_print("🎯 AI Confidence: {analysis.get('confidence_score', 0):.1f}%")
            safe_print(f"💡 Boolean Authorization: {analysis.get('boolean_authorized', False)}")
            safe_print(f"📝 AI Analysis: {analysis.get('ai_analysis', 'Analysis unavailable')}")
        except Exception:
            safe_print("⚠️ AI Analysis unavailable: {str(e)}")

    # Summary statistics
    sum(p.expected_roi for p in all_parlays)
    sum(p.risk_score for p in all_parlays) / len(all_parlays)
    total_recommended_stake = sum(p.recommended_stake for p in all_parlays)

    safe_print("\n📊 **NCAA WEEK 7 SUMMARY**")
    safe_print("   Total Parlays: {len(all_parlays)}")
    safe_print("   Combined Expected ROI: {total_expected_roi:.1f}%")
    safe_print("   Average Risk Score: {avg_risk_score:.2f}")
    safe_print("   Total Recommended Stakes: ${total_recommended_stake:.2f}")
    safe_print(
        f"   Bankroll Utilization: {(total_recommended_stake / generator.bankroll) * 100:.1f}%"
    )

    safe_print("\n✅ EQ12 Advanced NCAA Week 7 Analysis Complete!")


if __name__ == "__main__":
    asyncio.run(main())
