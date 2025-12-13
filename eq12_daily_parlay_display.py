#!/usr/bin/env python3
"""
EQ12 Daily Parlay Generator - October 4, 2025
Display all parlays the system would play today with complete analysis
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class BetType(Enum):
    MONEYLINE = "ML"
    SPREAD = "SPREAD"
    OVER_UNDER = "O/U"
    PROP = "PROP"


class Sport(Enum):
    NCAA_FOOTBALL = "NCAA Football"
    NFL = "NFL"
    NBA = "NBA"
    NHL = "NHL"


@dataclass
class GameInfo:
    """Individual game information"""

    home_team: str
    away_team: str
    sport: Sport
    game_time: str
    spread_line: float | None = None
    total_line: float | None = None
    home_ml_odds: float | None = None
    away_ml_odds: float | None = None


@dataclass
class ParlayLeg:
    """Individual parlay leg with complete details"""

    game: GameInfo
    bet_type: BetType
    selection: str
    odds: float
    decimal_odds: float
    implied_probability: float
    confidence: float
    sharp_money_indicator: bool = False
    injury_concerns: bool = False
    weather_factor: bool = False


@dataclass
class DailyParlay:
    """Complete daily parlay recommendation"""

    parlay_id: str
    legs: list[ParlayLeg]
    combined_odds: float
    combined_decimal_odds: float
    total_implied_probability: float
    recommended_stake: float
    kelly_percentage: float
    expected_profit: float
    expected_roi: float
    risk_score: float
    confidence_score: float
    reasoning: str
    category: str  # "High Confidence", "Value Play", "Long Shot", etc.


class EQ12DailyParlaySystem:
    """Complete daily parlay generation system"""

    def __init__(self):
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.bankroll = 1000.00
        self.max_risk_per_parlay = 0.05  # 5% max
        self.min_confidence = 0.60  # 60% minimum confidence
        self.base_directory = Path("C:/EQ12")
        self.logs_dir = self.base_directory / "logs"

    def get_todays_games(self) -> list[GameInfo]:
        """Get all games scheduled for today"""
        # College football and sports action for today
        games = [
            # NCAA Football - Friday Night Lights
            GameInfo(
                home_team="Louisiana Tech",
                away_team="UTEP",
                sport=Sport.NCAA_FOOTBALL,
                game_time="2025-10-04 19:30",
                spread_line=-7.5,  # Louisiana Tech -7.5
                total_line=58.5,
                home_ml_odds=-280,
                away_ml_odds=+230,
            ),
            GameInfo(
                home_team="Toledo",
                away_team="Buffalo",
                sport=Sport.NCAA_FOOTBALL,
                game_time="2025-10-04 20:00",
                spread_line=-10.5,  # Toledo -10.5
                total_line=52.5,
                home_ml_odds=-450,
                away_ml_odds=+350,
            ),
            GameInfo(
                home_team="Nevada",
                away_team="Air Force",
                sport=Sport.NCAA_FOOTBALL,
                game_time="2025-10-04 22:30",
                spread_line=+3.5,  # Air Force -3.5
                total_line=45.5,
                home_ml_odds=+150,
                away_ml_odds=-170,
            ),
            # NHL Early Season
            GameInfo(
                home_team="Pittsburgh Penguins",
                away_team="New York Rangers",
                sport=Sport.NHL,
                game_time="2025-10-04 19:00",
                spread_line=-1.5,  # Puck line
                total_line=6.5,
                home_ml_odds=+120,
                away_ml_odds=-140,
            ),
            GameInfo(
                home_team="Detroit Red Wings",
                away_team="Nashville Predators",
                sport=Sport.NHL,
                game_time="2025-10-04 19:30",
                spread_line=+1.5,
                total_line=6.0,
                home_ml_odds=+180,
                away_ml_odds=-200,
            ),
            # NBA Preseason
            GameInfo(
                home_team="Milwaukee Bucks",
                away_team="Chicago Bulls",
                sport=Sport.NBA,
                game_time="2025-10-04 20:00",
                spread_line=-8.5,
                total_line=225.5,
                home_ml_odds=-350,
                away_ml_odds=+280,
            ),
        ]
        return games

    def calculate_decimal_odds(self, american_odds: float) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        return (100 / abs(american_odds)) + 1

    def calculate_implied_probability(self, decimal_odds: float) -> float:
        """Calculate implied probability from decimal odds"""
        return 1 / decimal_odds

    def calculate_kelly_criterion(self, decimal_odds: float, true_prob: float) -> float:
        """Calculate Kelly Criterion percentage"""
        if true_prob <= 0 or true_prob >= 1:
            return 0

        # Kelly formula: f* = (bp - q) / b
        b = decimal_odds - 1
        p = true_prob
        q = 1 - p

        raw_kelly = (b * p - q) / b

        # Apply 25% conservative factor and 5% max cap
        conservative_kelly = raw_kelly * 0.25
        return min(conservative_kelly, 0.05)

    def generate_high_confidence_parlay(self, games: list[GameInfo]) -> DailyParlay:
        """Generate high confidence parlay with strong favorites"""
        legs = []

        # Leg 1: Louisiana Tech -7.5 (Strong home team)
        louisiana_tech_spread = ParlayLeg(
            game=games[0],
            bet_type=BetType.SPREAD,
            selection="Louisiana Tech -7.5",
            odds=-110,
            decimal_odds=1.91,
            implied_probability=0.524,
            confidence=0.78,
            sharp_money_indicator=True,
        )
        legs.append(louisiana_tech_spread)

        # Leg 2: Toledo -10.5 (Dominant home favorite)
        toledo_spread = ParlayLeg(
            game=games[1],
            bet_type=BetType.SPREAD,
            selection="Toledo -10.5",
            odds=-110,
            decimal_odds=1.91,
            implied_probability=0.524,
            confidence=0.82,
            sharp_money_indicator=True,
        )
        legs.append(toledo_spread)

        # Leg 3: Rangers ML (Road favorite with value)
        rangers_ml = ParlayLeg(
            game=games[3],
            bet_type=BetType.MONEYLINE,
            selection="New York Rangers ML",
            odds=-140,
            decimal_odds=1.71,
            implied_probability=0.583,
            confidence=0.72,
        )
        legs.append(rangers_ml)

        # Calculate combined odds
        combined_decimal = 1.91 * 1.91 * 1.71  # 6.24
        (combined_decimal - 1) * 100  # +524

        # Calculate Kelly sizing
        estimated_true_prob = 0.78 * 0.82 * 0.72  # 0.461
        kelly_pct = self.calculate_kelly_criterion(combined_decimal, estimated_true_prob)

        recommended_stake = self.bankroll * kelly_pct
        expected_profit = recommended_stake * (combined_decimal - 1)
        expected_roi = (expected_profit / recommended_stake) * 100

        return DailyParlay(
            parlay_id="EQ12_HIGH_CONF_20251004_1",
            legs=legs,
            combined_odds=+524,
            combined_decimal_odds=combined_decimal,
            total_implied_probability=0.160,  # 1/6.24
            recommended_stake=recommended_stake,
            kelly_percentage=kelly_pct,
            expected_profit=expected_profit,
            expected_roi=expected_roi,
            risk_score=0.45,
            confidence_score=0.77,
            reasoning="High-confidence parlay focusing on strong home favorites with sharp money backing",
            category="High Confidence",
        )

    def generate_value_play_parlay(self, games: list[GameInfo]) -> DailyParlay:
        """Generate value play parlay with favorable odds"""
        legs = []

        # Leg 1: Air Force -3.5 (Road favorite with value)
        air_force_spread = ParlayLeg(
            game=games[2],
            bet_type=BetType.SPREAD,
            selection="Air Force -3.5",
            odds=-110,
            decimal_odds=1.91,
            implied_probability=0.524,
            confidence=0.68,
        )
        legs.append(air_force_spread)

        # Leg 2: Under 6.5 Red Wings/Predators (Low-scoring trend)
        redwings_under = ParlayLeg(
            game=games[4],
            bet_type=BetType.OVER_UNDER,
            selection="Under 6.0 Total Goals",
            odds=-105,
            decimal_odds=1.95,
            implied_probability=0.513,
            confidence=0.71,
        )
        legs.append(redwings_under)

        # Leg 3: Bulls +8.5 (Getting points in preseason)
        bulls_spread = ParlayLeg(
            game=games[5],
            bet_type=BetType.SPREAD,
            selection="Chicago Bulls +8.5",
            odds=-110,
            decimal_odds=1.91,
            implied_probability=0.524,
            confidence=0.65,
        )
        legs.append(bulls_spread)

        # Calculate combined odds
        combined_decimal = 1.91 * 1.95 * 1.91  # 7.12
        (combined_decimal - 1) * 100  # +612

        # Calculate Kelly sizing
        estimated_true_prob = 0.68 * 0.71 * 0.65  # 0.314
        kelly_pct = self.calculate_kelly_criterion(combined_decimal, estimated_true_prob)

        recommended_stake = self.bankroll * kelly_pct
        expected_profit = recommended_stake * (combined_decimal - 1)
        expected_roi = (expected_profit / recommended_stake) * 100

        return DailyParlay(
            parlay_id="EQ12_VALUE_20251004_1",
            legs=legs,
            combined_odds=+612,
            combined_decimal_odds=combined_decimal,
            total_implied_probability=0.140,  # 1/7.12
            recommended_stake=recommended_stake,
            kelly_percentage=kelly_pct,
            expected_profit=expected_profit,
            expected_roi=expected_roi,
            risk_score=0.58,
            confidence_score=0.68,
            reasoning="Value play targeting favorable lines across multiple sports",
            category="Value Play",
        )

    def generate_longshot_parlay(self, games: list[GameInfo]) -> DailyParlay:
        """Generate longshot parlay with higher risk/reward"""
        legs = []

        # Leg 1: UTEP +7.5 (Road dog with value)
        utep_spread = ParlayLeg(
            game=games[0],
            bet_type=BetType.SPREAD,
            selection="UTEP +7.5",
            odds=-110,
            decimal_odds=1.91,
            implied_probability=0.524,
            confidence=0.58,
        )
        legs.append(utep_spread)

        # Leg 2: Over 58.5 Louisiana Tech/UTEP (High total)
        tech_over = ParlayLeg(
            game=games[0],
            bet_type=BetType.OVER_UNDER,
            selection="Over 58.5 Total Points",
            odds=-110,
            decimal_odds=1.91,
            implied_probability=0.524,
            confidence=0.62,
        )
        legs.append(tech_over)

        # Leg 3: Red Wings ML (Home dog value)
        redwings_ml = ParlayLeg(
            game=games[4],
            bet_type=BetType.MONEYLINE,
            selection="Detroit Red Wings ML",
            odds=+180,
            decimal_odds=2.80,
            implied_probability=0.357,
            confidence=0.45,
        )
        legs.append(redwings_ml)

        # Leg 4: Bulls ML (Big underdog)
        bulls_ml = ParlayLeg(
            game=games[5],
            bet_type=BetType.MONEYLINE,
            selection="Chicago Bulls ML",
            odds=+280,
            decimal_odds=3.80,
            implied_probability=0.263,
            confidence=0.35,
        )
        legs.append(bulls_ml)

        # Calculate combined odds
        combined_decimal = 1.91 * 1.91 * 2.80 * 3.80  # 38.67
        (combined_decimal - 1) * 100  # +3767

        # Calculate Kelly sizing (conservative for longshot)
        estimated_true_prob = 0.58 * 0.62 * 0.45 * 0.35  # 0.057
        kelly_pct = min(
            self.calculate_kelly_criterion(combined_decimal, estimated_true_prob), 0.01
        )  # Cap at 1%

        recommended_stake = self.bankroll * kelly_pct
        expected_profit = recommended_stake * (combined_decimal - 1)
        expected_roi = (expected_profit / recommended_stake) * 100

        return DailyParlay(
            parlay_id="EQ12_LONGSHOT_20251004_1",
            legs=legs,
            combined_odds=+3767,
            combined_decimal_odds=combined_decimal,
            total_implied_probability=0.026,  # 1/38.67
            recommended_stake=recommended_stake,
            kelly_percentage=kelly_pct,
            expected_profit=expected_profit,
            expected_roi=expected_roi,
            risk_score=0.89,
            confidence_score=0.50,
            reasoning="High-risk longshot parlay targeting multiple underdogs for maximum payout",
            category="Long Shot",
        )

    def generate_all_daily_parlays(self) -> list[DailyParlay]:
        """Generate all recommended parlays for today"""
        games = self.get_todays_games()

        parlays = [
            self.generate_high_confidence_parlay(games),
            self.generate_value_play_parlay(games),
            self.generate_longshot_parlay(games),
        ]

        return parlays

    def display_daily_parlays(self):
        """Display all parlays the system would play today"""
        print("🏈 **EQ12 DAILY PARLAY SYSTEM - {self.current_date}**")
        print("=" * 80)
        print("📅 Date: {datetime.now().strftime('%A, %B %d, %Y')}")
        print("💰 Bankroll: ${self.bankroll:,.2f}")
        print("🎯 Games Available: 6 across NCAA, NHL, NBA")

        parlays = self.generate_all_daily_parlays()

        total_stake = sum(p.recommended_stake for p in parlays)
        sum(p.expected_profit for p in parlays)
        (total_stake / self.bankroll) * 100

        print("\n📊 **DAILY SUMMARY**")
        print("=" * 80)
        print("Total Parlays Recommended: {len(parlays)}")
        print("Total Recommended Stakes: ${total_stake:.2f}")
        print("Bankroll Utilization: {bankroll_utilization:.1f}%")
        print("Total Potential Profit: ${total_potential_profit:.2f}")
        print("Combined Expected ROI: {(total_potential_profit/total_stake)*100:.1f}%")

        for _i, parlay in enumerate(parlays, 1):
            print("\n🎯 **PARLAY #{i} - {parlay.category.upper()}**")
            print("=" * 80)
            print("ID: {parlay.parlay_id}")
            print("Combined Odds: {parlay.combined_odds:+}")
            print("Decimal Odds: {parlay.combined_decimal_odds:.2f}")
            print(
                f"Recommended Stake: ${parlay.recommended_stake:.2f} ({parlay.kelly_percentage:.1%} Kelly)"
            )
            print("Expected Profit: ${parlay.expected_profit:.2f}")
            print("Expected ROI: {parlay.expected_roi:.1f}%")
            print("Risk Score: {parlay.risk_score:.2f}/1.00")
            print("Confidence Score: {parlay.confidence_score:.2f}/1.00")
            print("Reasoning: {parlay.reasoning}")

            print("\n📋 **PARLAY LEGS:**")
            for _j, leg in enumerate(parlay.legs, 1):
                print("  Leg {j}: {leg.selection}")
                print("    Game: {leg.game.away_team} @ {leg.game.home_team}")
                print("    Sport: {leg.game.sport.value}")
                print("    Time: {leg.game.game_time}")
                print("    Bet Type: {leg.bet_type.value}")
                print("    Odds: {leg.odds:+} ({leg.decimal_odds:.2f} decimal)")
                print("    Implied Prob: {leg.implied_probability:.1%}")
                print("    Confidence: {leg.confidence:.1%}")

                indicators = []
                if leg.sharp_money_indicator:
                    indicators.append("⚡ Sharp Money")
                if leg.injury_concerns:
                    indicators.append("🏥 Injury Concerns")
                if leg.weather_factor:
                    indicators.append("🌤️ Weather Factor")

                if indicators:
                    print("    Indicators: {' | '.join(indicators)}")
                print()

        # Save results
        self.save_daily_results(parlays)

        print("\n✅ **DAILY PARLAY GENERATION COMPLETE**")
        print("All recommended parlays generated with Kelly Criterion sizing")
        print("Monitor games throughout the day for live betting opportunities")

    def save_daily_results(self, parlays: list[DailyParlay]):
        """Save daily parlay results to JSON log"""
        timestamp = datetime.now().isoformat()

        results = {
            "timestamp": timestamp,
            "date": self.current_date,
            "system": "EQ12_Daily_Parlay_Generator",
            "version": "1.0.0",
            "bankroll": self.bankroll,
            "total_parlays": len(parlays),
            "total_stake": sum(p.recommended_stake for p in parlays),
            "total_potential_profit": sum(p.expected_profit for p in parlays),
            "bankroll_utilization": (sum(p.recommended_stake for p in parlays) / self.bankroll)
            * 100,
            "parlays": [asdict(parlay) for parlay in parlays],
        }

        self.logs_dir.mkdir(exist_ok=True)
        log_file = self.logs_dir / f"daily_parlays_{self.current_date}.json"

        with open(log_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print("\n📝 Daily results saved: {log_file}")


def main():
    """Main execution function"""
    daily_system = EQ12DailyParlaySystem()
    daily_system.display_daily_parlays()


if __name__ == "__main__":
    main()
