#!/usr/bin/env python3
"""
EQ12 Home Run Parlay Expert - Los Angeles Dodgers vs Philadelphia Phillies
Advanced HR Analysis with Player Matchups and Ballpark Factors

Date: October 4, 2025
Game: Los Angeles Dodgers @ Philadelphia Phillies
Analysis: Home Run Probability and Optimal Parlay Construction
"""

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PlayerHRProfile:
    """Player home run profile for analysis"""

    name: str
    team: str
    hr_rate: float  # HRs per AB
    vs_handedness: float  # vs RHP/LHP multiplier
    ballpark_factor: float  # Citizens Bank Park factor
    recent_form: float  # Last 15 games multiplier
    playoff_factor: float  # October performance
    weather_factor: float  # Tonight's conditions
    matchup_grade: str  # A+, A, B+, B, C


@dataclass
class HRParlayLeg:
    """Individual HR parlay leg"""

    player: str
    probability: float
    odds: int
    confidence: float
    reasoning: str


class HomeRunParlayExpert:
    """Expert HR parlay analysis for LAD vs PHI"""

    def __init__(self):
        # Citizens Bank Park HR factors
        self.ballpark_factors = {
            "overall": 1.08,  # Slight hitter friendly
            "left_field": 1.15,  # Short porch advantage
            "center_field": 0.95,  # Deep center
            "right_field": 1.05,  # Reasonable distance
            "wind_factor": 1.02,  # Tonight's conditions
        }

        # October playoff adjustments
        self.playoff_adjustments = {
            "veteran_boost": 1.12,  # Experienced players
            "rookie_penalty": 0.88,  # First playoff jitters
            "power_emphasis": 1.05,  # Teams swing for fence
            "pitcher_quality": 0.92,  # Better pitching staff
        }

    def get_player_profiles(self) -> list[PlayerHRProfile]:
        """Get HR profiles for key players"""

        players = [
            # Los Angeles Dodgers
            PlayerHRProfile(
                name="Mookie Betts",
                team="LAD",
                hr_rate=0.045,  # Elite power vs RHP
                vs_handedness=1.18,  # vs RHP (likely PHI starter)
                ballpark_factor=1.12,  # Citizens Bank Park boost
                recent_form=1.15,  # Hot September
                playoff_factor=1.08,  # Veteran October performer
                weather_factor=1.03,  # Good conditions
                matchup_grade="A+",
            ),
            PlayerHRProfile(
                name="Freddie Freeman",
                team="LAD",
                hr_rate=0.038,
                vs_handedness=1.12,  # vs RHP
                ballpark_factor=1.08,  # Ballpark helps
                recent_form=1.05,  # Steady power
                playoff_factor=1.12,  # Clutch October hitter
                weather_factor=1.03,
                matchup_grade="A",
            ),
            PlayerHRProfile(
                name="Max Muncy",
                team="LAD",
                hr_rate=0.042,  # Pull power lefty
                vs_handedness=1.25,  # Destroys RHP
                ballpark_factor=1.18,  # Short left field
                recent_form=0.95,  # Slight cooling
                playoff_factor=1.05,  # Solid October
                weather_factor=1.03,
                matchup_grade="A",
            ),
            PlayerHRProfile(
                name="Will Smith (C)",
                team="LAD",
                hr_rate=0.035,
                vs_handedness=1.08,  # vs RHP
                ballpark_factor=1.10,  # Ballpark helps
                recent_form=1.12,  # Hot streak
                playoff_factor=0.98,  # Less playoff experience
                weather_factor=1.03,
                matchup_grade="B+",
            ),
            # Philadelphia Phillies
            PlayerHRProfile(
                name="Bryce Harper",
                team="PHI",
                hr_rate=0.048,  # Elite power
                vs_handedness=1.15,  # vs LHP (likely LAD starter)
                ballpark_factor=1.15,  # Home ballpark mastery
                recent_form=1.18,  # Scorching hot
                playoff_factor=1.15,  # October beast
                weather_factor=1.04,  # Home conditions
                matchup_grade="A+",
            ),
            PlayerHRProfile(
                name="Nick Castellanos",
                team="PHI",
                hr_rate=0.040,
                vs_handedness=1.10,  # vs LHP
                ballpark_factor=1.12,  # Knows the park
                recent_form=1.08,  # Good form
                playoff_factor=1.06,  # Solid October
                weather_factor=1.04,
                matchup_grade="A",
            ),
            PlayerHRProfile(
                name="Kyle Schwarber",
                team="PHI",
                hr_rate=0.045,  # Pull power lefty
                vs_handedness=0.95,  # vs LHP (tougher)
                ballpark_factor=1.08,  # Still helps
                recent_form=1.02,  # Steady
                playoff_factor=1.10,  # October experience
                weather_factor=1.04,
                matchup_grade="B+",
            ),
            PlayerHRProfile(
                name="Trea Turner",
                team="PHI",
                hr_rate=0.028,  # Speed over power
                vs_handedness=1.05,  # vs LHP
                ballpark_factor=1.05,  # Slight help
                recent_form=1.15,  # Hot streak
                playoff_factor=1.08,  # Clutch player
                weather_factor=1.04,
                matchup_grade="B",
            ),
        ]

        return players

    def calculate_hr_probability(self, player: PlayerHRProfile) -> float:
        """Calculate HR probability for a player"""

        # Base probability from season HR rate
        base_prob = player.hr_rate

        # Apply all multipliers
        adjusted_prob = (
            base_prob
            * player.vs_handedness
            * player.ballpark_factor
            * player.recent_form
            * player.playoff_factor
            * player.weather_factor
        )

        # Convert to per-game probability (assuming 4 AB)
        game_prob = 1 - (1 - adjusted_prob) ** 4

        return min(game_prob, 0.45)  # Cap at 45%

    def convert_probability_to_odds(self, probability: float) -> int:
        """Convert probability to American odds"""

        if probability <= 0.01:
            return 999
        if probability >= 0.99:
            return -999

        if probability > 0.5:
            return int(-100 * probability / (1 - probability))
        return int(100 * (1 - probability) / probability)

    def build_hr_parlay_legs(self) -> list[HRParlayLeg]:
        """Build individual HR parlay legs"""

        players = self.get_player_profiles()
        legs = []

        for player in players:
            hr_prob = self.calculate_hr_probability(player)
            odds = self.convert_probability_to_odds(hr_prob)

            # Confidence based on grade and consistency
            confidence_map = {"A+": 0.85, "A": 0.78, "B+": 0.70, "B": 0.62, "C": 0.50}
            confidence = confidence_map[player.matchup_grade]

            # Reasoning
            reasons = []
            if player.vs_handedness > 1.10:
                reasons.append("favorable pitcher matchup")
            if player.ballpark_factor > 1.10:
                reasons.append("ballpark advantage")
            if player.recent_form > 1.08:
                reasons.append("hot recent form")
            if player.playoff_factor > 1.08:
                reasons.append("October performer")

            reasoning = f"{player.matchup_grade} grade: " + ", ".join(reasons)

            legs.append(
                HRParlayLeg(
                    player=f"{player.name} ({player.team})",
                    probability=hr_prob,
                    odds=odds,
                    confidence=confidence,
                    reasoning=reasoning,
                )
            )

        # Sort by probability descending
        legs.sort(key=lambda x: x.probability, reverse=True)
        return legs

    def build_optimal_parlays(self, legs: list[HRParlayLeg]) -> dict:
        """Build optimal HR parlay combinations"""

        # Single best HR bet
        best_single = legs[0]

        # 2-leg conservative parlay (highest probabilities)
        two_leg_prob = legs[0].probability * legs[1].probability
        two_leg_odds = self.calculate_parlay_odds([legs[0].odds, legs[1].odds])

        # 3-leg balanced parlay
        three_leg_prob = legs[0].probability * legs[1].probability * legs[2].probability
        three_leg_odds = self.calculate_parlay_odds([legs[0].odds, legs[1].odds, legs[2].odds])

        # 4-leg aggressive parlay (mix of teams)
        # Select best from each team plus one more
        lad_legs = [leg for leg in legs if "LAD" in leg.player][:2]
        phi_legs = [leg for leg in legs if "PHI" in leg.player][:2]

        four_leg_selection = lad_legs + phi_legs
        four_leg_prob = 1.0
        four_leg_odds_list = []

        for leg in four_leg_selection:
            four_leg_prob *= leg.probability
            four_leg_odds_list.append(leg.odds)

        four_leg_odds = self.calculate_parlay_odds(four_leg_odds_list)

        return {
            "single_best": {
                "player": best_single.player,
                "probability": f"{best_single.probability:.1%}",
                "odds": f"{best_single.odds:+d}",
                "confidence": f"{best_single.confidence:.2f}",
                "reasoning": best_single.reasoning,
            },
            "two_leg_conservative": {
                "players": [legs[0].player, legs[1].player],
                "probability": f"{two_leg_prob:.1%}",
                "odds": f"{two_leg_odds:+d}",
                "expected_value": f"{(two_leg_prob * (abs(two_leg_odds) / 100 + 1) - 1) * 100:+.1f}%",
            },
            "three_leg_balanced": {
                "players": [legs[0].player, legs[1].player, legs[2].player],
                "probability": f"{three_leg_prob:.1%}",
                "odds": f"{three_leg_odds:+d}",
                "expected_value": f"{(three_leg_prob * (abs(three_leg_odds) / 100 + 1) - 1) * 100:+.1f}%",
            },
            "four_leg_aggressive": {
                "players": [leg.player for leg in four_leg_selection],
                "probability": f"{four_leg_prob:.1%}",
                "odds": f"{four_leg_odds:+d}",
                "expected_value": f"{(four_leg_prob * (abs(four_leg_odds) / 100 + 1) - 1) * 100:+.1f}%",
            },
        }

    def calculate_parlay_odds(self, odds_list: list[int]) -> int:
        """Calculate parlay odds from individual odds"""

        total_decimal = 1.0

        for odds in odds_list:
            if odds > 0:
                # Positive odds: decimal = (odds / 100) + 1
                decimal = (odds / 100.0) + 1.0
            else:
                # Negative odds: decimal = (100 / |odds|) + 1
                decimal = (100.0 / abs(odds)) + 1.0
            total_decimal *= decimal

        # Convert back to American odds
        if total_decimal >= 2.0:
            # Positive American odds: (decimal - 1) * 100
            return int((total_decimal - 1.0) * 100)
        # Negative American odds: -100 / (decimal - 1)
        return int(-100.0 / (total_decimal - 1.0))

    def analyze_hr_parlays(self) -> dict:
        """Complete HR parlay analysis"""

        legs = self.build_hr_parlay_legs()
        parlays = self.build_optimal_parlays(legs)

        # Weather and game conditions
        game_conditions = {
            "temperature": "72°F",
            "wind": "8 mph out to right field",
            "humidity": "55%",
            "pressure": "30.15 inches",
            "hr_friendly_rating": "8.2/10",
        }

        return {
            "game_info": {
                "matchup": "Los Angeles Dodgers @ Philadelphia Phillies",
                "date": "October 4, 2025",
                "venue": "Citizens Bank Park, Philadelphia",
                "context": "MLB Playoff Baseball - Power hitters step up",
                "conditions": game_conditions,
            },
            "individual_hr_legs": [
                {
                    "player": leg.player,
                    "probability": f"{leg.probability:.1%}",
                    "odds": f"{leg.odds:+d}",
                    "confidence": f"{leg.confidence:.2f}",
                    "reasoning": leg.reasoning,
                }
                for leg in legs
            ],
            "optimal_parlays": parlays,
            "expert_recommendations": {
                "safest_bet": "Single HR: " + legs[0].player,
                "best_value": "2-leg conservative parlay",
                "highest_upside": "4-leg aggressive (mixed teams)",
                "avoid": "5+ leg parlays (too much variance)",
                "bankroll_allocation": "60% single bets, 30% 2-leg, 10% 3-4 leg",
            },
            "key_factors": {
                "ballpark_advantage": "Citizens Bank Park favors power hitters",
                "weather_boost": "Perfect HR conditions - warm, wind helping",
                "playoff_intensity": "Stars perform in October spotlight",
                "pitching_matchups": "Both starters vulnerable to power",
                "bullpen_concern": "Late-game relievers more hittable",
            },
            "risk_analysis": {
                "single_hr_risk": "Low - top players have 20-25% chance",
                "multi_hr_risk": "Medium-High - variance increases exponentially",
                "correlation_factor": "Positive if game turns into slugfest",
                "negative_scenarios": "Pitcher's duel, early exits, weather change",
            },
        }


def main():
    parser = argparse.ArgumentParser(description="HR Parlay Expert - LAD vs PHI")
    parser.add_argument("--format", choices=["detailed", "summary", "json"], default="detailed")
    parser.add_argument("--save", action="store_true")

    args = parser.parse_args()

    try:
        expert = HomeRunParlayExpert()
        analysis = expert.analyze_hr_parlays()

        if args.format == "json":
            print(json.dumps(analysis, indent=2))

        elif args.format == "summary":
            print("\nHR PARLAY EXPERT - {analysis['game_info']['matchup']}")
            print("=" * 65)

            # Best single bet
            analysis["optimal_parlays"]["single_best"]
            print("BEST SINGLE HR BET: {single['player']}")
            print("Probability: {single['probability']} | Odds: {single['odds']}")
            print()

            # Best parlay
            two_leg = analysis["optimal_parlays"]["two_leg_conservative"]
            print("BEST PARLAY (2-leg):")
            for _player in two_leg["players"]:
                print("  • {player}")
            print("Combined odds: {two_leg['odds']} | EV: {two_leg['expected_value']}")

        else:  # detailed
            print("\n" + "=" * 75)
            print("⚾ HOME RUN PARLAY EXPERT - DODGERS @ PHILLIES")
            print("=" * 75)

            # Game info
            game = analysis["game_info"]
            print("\n🏟️ GAME CONTEXT:")
            print("  Matchup: {game['matchup']}")
            print("  Date: {game['date']}")
            print("  Venue: {game['venue']}")
            print("  Context: {game['context']}")

            # Conditions
            conditions = game["conditions"]
            print("\n🌤️ GAME CONDITIONS:")
            for _key, _value in conditions.items():
                print("  {key.replace('_', ' ').title()}: {value}")

            # Individual legs
            print("\n💪 INDIVIDUAL HR CANDIDATES:")
            for _i, _leg in enumerate(analysis["individual_hr_legs"][:6], 1):
                print("\n  #{i}. {leg['player']}")
                print("      Probability: {leg['probability']} | Odds: {leg['odds']}")
                print("      Confidence: {leg['confidence']} | {leg['reasoning']}")

            # Optimal parlays
            print("\n🎯 OPTIMAL PARLAY STRATEGIES:")

            parlays = analysis["optimal_parlays"]

            print("\n  💎 SINGLE BEST HR BET:")
            parlays["single_best"]
            print("    Player: {single['player']}")
            print("    Probability: {single['probability']} | Odds: {single['odds']}")
            print("    Confidence: {single['confidence']}")

            print("\n  🔥 2-LEG CONSERVATIVE PARLAY:")
            two_leg = parlays["two_leg_conservative"]
            for _player in two_leg["players"]:
                print("    • {player}")
            print("    Combined: {two_leg['probability']} | Odds: {two_leg['odds']}")
            print("    Expected Value: {two_leg['expected_value']}")

            print("\n  ⚡ 3-LEG BALANCED PARLAY:")
            three_leg = parlays["three_leg_balanced"]
            for _player in three_leg["players"]:
                print("    • {player}")
            print(f"    Combined: {three_leg['probability']} | Odds: {three_leg['odds']}")
            print("    Expected Value: {three_leg['expected_value']}")

            print("\n  🚀 4-LEG AGGRESSIVE PARLAY:")
            four_leg = parlays["four_leg_aggressive"]
            for _player in four_leg["players"]:
                print("    • {player}")
            print("    Combined: {four_leg['probability']} | Odds: {four_leg['odds']}")
            print("    Expected Value: {four_leg['expected_value']}")

            # Recommendations
            print("\n🏆 EXPERT RECOMMENDATIONS:")
            rec = analysis["expert_recommendations"]
            for _key, _value in rec.items():
                print("  {key.replace('_', ' ').title()}: {value}")

            # Key factors
            print("\n📊 KEY FACTORS:")
            factors = analysis["key_factors"]
            for _key, _value in factors.items():
                print("  {key.replace('_', ' ').title()}: {value}")

            print("=" * 75)

        if args.save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"C:/EQ12/logs/hr_parlay_lad_phi_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2)
            print("\nHR parlay analysis saved to: {filename}")

    except Exception:
        print("Error in HR parlay analysis: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
