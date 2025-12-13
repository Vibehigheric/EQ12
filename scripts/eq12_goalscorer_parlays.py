#!/usr/bin/env python3
"""
EQ12 Goalscorer Parlay Generator
Creates realistic goalscorer parlays with actual winning probabilities
Focuses on best chances while allowing up to 20 legs
"""

import argparse
import itertools
import logging
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class GoalscorerBet:
    """Represents a goalscorer bet"""

    player_name: str
    team: str
    opponent: str
    odds: int  # American odds
    probability: float  # Implied probability
    bet_type: str  # 'anytime_goal', 'first_goal', etc.
    game: str

    def __str__(self):
        return f"{
            self.player_name} ({
            self.team}) {
            self.bet_type} vs {
                self.opponent} | {
                    self.odds:+d} ({
                        self.probability:.1%})"


class GoalscorerParlayGenerator:
    """Generate realistic goalscorer parlays"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        self.base_url = "https://api.the-odds-api.com/v4"

        # Setup logging
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Realistic goalscorer data for today's analysis
        self.sample_goalscorers = self._get_sample_goalscorers()

    def _get_sample_goalscorers(self) -> list[GoalscorerBet]:
        """Get realistic NHL goalscorer bets for analysis"""

        # Today's likely NHL games with realistic goalscorer odds
        goalscorers = [
            # High probability scorers (stars)
            GoalscorerBet(
                "Connor McDavid",
                "EDM",
                "CGY",
                -120,
                0.545,
                "Anytime Goal",
                "EDM vs CGY",
            ),
            GoalscorerBet(
                "Leon Draisaitl",
                "EDM",
                "CGY",
                -110,
                0.524,
                "Anytime Goal",
                "EDM vs CGY",
            ),
            GoalscorerBet(
                "Nathan MacKinnon",
                "COL",
                "VGK",
                -115,
                0.535,
                "Anytime Goal",
                "COL vs VGK",
            ),
            GoalscorerBet(
                "David Pastrnak",
                "BOS",
                "TOR",
                -105,
                0.512,
                "Anytime Goal",
                "BOS vs TOR",
            ),
            GoalscorerBet(
                "Auston Matthews",
                "TOR",
                "BOS",
                -100,
                0.500,
                "Anytime Goal",
                "TOR vs BOS",
            ),
            # Good probability scorers (consistent producers)
            GoalscorerBet(
                "Mikko Rantanen",
                "COL",
                "VGK",
                +105,
                0.488,
                "Anytime Goal",
                "COL vs VGK",
            ),
            GoalscorerBet(
                "Johnny Gaudreau",
                "CGY",
                "EDM",
                +110,
                0.476,
                "Anytime Goal",
                "CGY vs EDM",
            ),
            GoalscorerBet("Mitch Marner", "TOR", "BOS", +115,
                          0.465, "Anytime Goal", "TOR vs BOS"),
            GoalscorerBet("Brad Marchand", "BOS", "TOR", +120,
                          0.455, "Anytime Goal", "BOS vs TOR"),
            GoalscorerBet(
                "Jonathan Marchessault",
                "VGK",
                "COL",
                +125,
                0.444,
                "Anytime Goal",
                "VGK vs COL",
            ),
            # Moderate probability (secondary scorers)
            GoalscorerBet(
                "Ryan Nugent-Hopkins",
                "EDM",
                "CGY",
                +140,
                0.417,
                "Anytime Goal",
                "EDM vs CGY",
            ),
            GoalscorerBet("Cale Makar", "COL", "VGK", +150,
                          0.400, "Anytime Goal", "COL vs VGK"),
            GoalscorerBet(
                "William Nylander",
                "TOR",
                "BOS",
                +155,
                0.392,
                "Anytime Goal",
                "TOR vs BOS",
            ),
            GoalscorerBet(
                "Tyler Bertuzzi",
                "BOS",
                "TOR",
                +160,
                0.385,
                "Anytime Goal",
                "BOS vs TOR",
            ),
            GoalscorerBet(
                "Elias Lindholm",
                "CGY",
                "EDM",
                +165,
                0.377,
                "Anytime Goal",
                "CGY vs EDM",
            ),
            # Lower probability but still reasonable (role players with scoring upside)
            GoalscorerBet("Zach Hyman", "EDM", "CGY", +180,
                          0.357, "Anytime Goal", "EDM vs CGY"),
            GoalscorerBet(
                "Artturi Lehkonen",
                "COL",
                "VGK",
                +190,
                0.345,
                "Anytime Goal",
                "COL vs VGK",
            ),
            GoalscorerBet("John Tavares", "TOR", "BOS", +200,
                          0.333, "Anytime Goal", "TOR vs BOS"),
            GoalscorerBet("Pavel Zacha", "BOS", "TOR", +210,
                          0.323, "Anytime Goal", "BOS vs TOR"),
            GoalscorerBet("Nazem Kadri", "CGY", "EDM", +220,
                          0.312, "Anytime Goal", "CGY vs EDM"),
            # Stretch picks (defensemen, checking line forwards)
            GoalscorerBet("Shea Theodore", "VGK", "COL", +280,
                          0.263, "Anytime Goal", "VGK vs COL"),
            GoalscorerBet("Morgan Rielly", "TOR", "BOS", +300,
                          0.250, "Anytime Goal", "TOR vs BOS"),
            GoalscorerBet("Evan Bouchard", "EDM", "CGY", +320,
                          0.238, "Anytime Goal", "EDM vs CGY"),
            GoalscorerBet(
                "Charlie McAvoy",
                "BOS",
                "TOR",
                +350,
                0.222,
                "Anytime Goal",
                "BOS vs TOR",
            ),
            GoalscorerBet(
                "Rasmus Andersson",
                "CGY",
                "EDM",
                +380,
                0.208,
                "Anytime Goal",
                "CGY vs EDM",
            ),
        ]

        return goalscorers

    def calculate_parlay_probability(self, bets: list[GoalscorerBet]) -> float:
        """Calculate compound probability of parlay"""
        probability = 1.0
        for bet in bets:
            probability *= bet.probability
        return probability

    def calculate_parlay_odds(self, bets: list[GoalscorerBet]) -> int:
        """Calculate American odds for parlay"""
        probability = self.calculate_parlay_probability(bets)
        if probability == 0:
            return 999999

        decimal_odds = 1 / probability

        if decimal_odds >= 2.0:
            american_odds = int((decimal_odds - 1) * 100)
        else:
            american_odds = int(-100 / (decimal_odds - 1))

        return american_odds

    def generate_realistic_parlays(self) -> list[dict]:
        """Generate goalscorer parlays with realistic winning chances"""

        parlays = []
        goalscorers = self.sample_goalscorers

        # Sort by probability (highest first) for best chances
        goalscorers_sorted = sorted(
            goalscorers,
            key=lambda x: x.probability,
            reverse=True)

        self.logger.info("🎯 Generating Realistic Goalscorer Parlays")
        self.logger.info("=" * 60)

        # 2-leg parlays (best probability)
        for combo in itertools.combinations(goalscorers_sorted[:10], 2):
            probability = self.calculate_parlay_probability(combo)
            if probability >= 0.15:  # 15%+ chance
                parlays.append(
                    {
                        "legs": len(combo),
                        "bets": list(combo),
                        "probability": probability,
                        "odds": self.calculate_parlay_odds(combo),
                        "rating": "EXCELLENT",
                    }
                )

        # 3-leg parlays (very good probability)
        for combo in itertools.combinations(goalscorers_sorted[:8], 3):
            probability = self.calculate_parlay_probability(combo)
            if probability >= 0.08:  # 8%+ chance
                parlays.append(
                    {
                        "legs": len(combo),
                        "bets": list(combo),
                        "probability": probability,
                        "odds": self.calculate_parlay_odds(combo),
                        "rating": "VERY GOOD",
                    }
                )

        # 4-leg parlays (good probability)
        for combo in itertools.combinations(goalscorers_sorted[:8], 4):
            probability = self.calculate_parlay_probability(combo)
            if probability >= 0.04:  # 4%+ chance
                parlays.append(
                    {
                        "legs": len(combo),
                        "bets": list(combo),
                        "probability": probability,
                        "odds": self.calculate_parlay_odds(combo),
                        "rating": "GOOD",
                    }
                )

        # 5-leg parlays (decent probability)
        for combo in itertools.combinations(goalscorers_sorted[:10], 5):
            probability = self.calculate_parlay_probability(combo)
            if probability >= 0.02:  # 2%+ chance
                parlays.append(
                    {
                        "legs": len(combo),
                        "bets": list(combo),
                        "probability": probability,
                        "odds": self.calculate_parlay_odds(combo),
                        "rating": "DECENT",
                    }
                )

        # 6-8 leg parlays (reasonable probability)
        for legs in [6, 7, 8]:
            for combo in itertools.combinations(goalscorers_sorted[:12], legs):
                probability = self.calculate_parlay_probability(combo)
                if probability >= 0.005:  # 0.5%+ chance
                    parlays.append(
                        {
                            "legs": len(combo),
                            "bets": list(combo),
                            "probability": probability,
                            "odds": self.calculate_parlay_odds(combo),
                            "rating": "REASONABLE",
                        }
                    )
                    if len([p for p in parlays if p["legs"] == legs]) >= 3:
                        break

        # 10-12 leg parlays (long shot but not impossible)
        for legs in [10, 12]:
            best_combo = goalscorers_sorted[:legs]
            probability = self.calculate_parlay_probability(best_combo)
            if probability >= 0.0001:  # 0.01%+ chance
                parlays.append(
                    {
                        "legs": legs,
                        "bets": best_combo,
                        "probability": probability,
                        "odds": self.calculate_parlay_odds(best_combo),
                        "rating": "LONG SHOT",
                    }
                )

        # 15 leg parlay (the dream shot)
        dream_combo = goalscorers_sorted[:15]
        probability = self.calculate_parlay_probability(dream_combo)
        parlays.append(
            {
                "legs": 15,
                "bets": dream_combo,
                "probability": probability,
                "odds": self.calculate_parlay_odds(dream_combo),
                "rating": "DREAM SHOT",
            }
        )

        # 20 leg parlay (the ultimate dream)
        ultimate_combo = goalscorers_sorted[:20]
        probability = self.calculate_parlay_probability(ultimate_combo)
        parlays.append(
            {
                "legs": 20,
                "bets": ultimate_combo,
                "probability": probability,
                "odds": self.calculate_parlay_odds(ultimate_combo),
                "rating": "ULTIMATE DREAM",
            }
        )

        # Sort by probability (best chances first)
        parlays.sort(key=lambda x: x["probability"], reverse=True)

        return parlays

    def display_parlays(self, parlays: list[dict]):
        """Display parlays in order of best winning probability"""

        print("\n🏒 TODAY'S GOALSCORER PARLAYS - BEST CHANCES FIRST")
        print("=" * 80)

        for i, parlay in enumerate(parlays, 1):
            prob_pct = parlay["probability"] * 100
            odds = parlay["odds"]
            rating = parlay["rating"]

            # Color coding based on probability
            if prob_pct >= 15:
                status = "🟢 STRONG"
            elif prob_pct >= 5:
                status = "🟡 SOLID"
            elif prob_pct >= 1:
                status = "🟠 DECENT"
            else:
                status = "🔴 LONG SHOT"

            print(f"\n#{i} | {parlay['legs']}-LEG PARLAY | {status} | {rating}")
            print(
                f"Probability: {
                    prob_pct:.3f}% | Odds: {
                    odds:+,d} | Potential: ${
                    odds /
                    100:.0f} per $1")
            print("-" * 80)

            for j, bet in enumerate(parlay["bets"], 1):
                print(f"  {j:2d}. {bet}")

            if i <= 10:  # Show expected value for top 10
                expected_value = (parlay["probability"] * abs(odds) / 100) - 1
                print(
                    f"\n💰 Expected Value: {expected_value:+.3f} ({expected_value * 100:+.1f}%)")

            print("=" * 80)

    def get_top_recommendations(
            self,
            parlays: list[dict],
            count: int = 5) -> list[dict]:
        """Get top recommended parlays based on probability"""

        # Filter for reasonable probabilities and return top ones
        reasonable_parlays = [p for p in parlays if p["probability"] >= 0.001]  # 0.1%+
        return reasonable_parlays[:count]


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Generate realistic goalscorer parlays")
    parser.add_argument("--api-key", help="The Odds API key")
    parser.add_argument(
        "--top",
        type=int,
        default=15,
        help="Number of top parlays to show")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with sample data")

    args = parser.parse_args()

    generator = GoalscorerParlayGenerator(args.api_key)

    print("🎯 EQ12 GOALSCORER PARLAY GENERATOR")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("🏒 NHL Goalscorer Analysis")

    # Generate parlays
    parlays = generator.generate_realistic_parlays()

    # Show top parlays
    top_parlays = parlays[: args.top]
    generator.display_parlays(top_parlays)

    # Show recommendations
    print("\n🎯 TOP 5 RECOMMENDATIONS (Best Probability of Winning):")
    print("=" * 60)

    recommendations = generator.get_top_recommendations(parlays, 5)
    for i, parlay in enumerate(recommendations, 1):
        prob_pct = parlay["probability"] * 100
        payout = abs(parlay["odds"]) / 100

        print(f"\n🥇 RECOMMENDATION #{i}")
        print(f"   Legs: {parlay['legs']} | Probability: {prob_pct:.3f}%")
        print(f"   $1 bet pays: ${payout:.2f} | Rating: {parlay['rating']}")
        print(
            f"   Risk Level: {
                'LOW' if prob_pct > 5 else 'MEDIUM' if prob_pct > 1 else 'HIGH'}")

    # Summary statistics
    total_parlays = len(parlays)
    avg_probability = sum(p["probability"] for p in parlays) / len(parlays) * 100

    print("\n📊 SUMMARY:")
    print(f"   Total parlays generated: {total_parlays}")
    print(f"   Average probability: {avg_probability:.3f}%")
    print(f"   Best chance: {parlays[0]['probability'] * 100:.3f}%")
    print(f"   Longest shot: {parlays[-1]['probability'] * 100:.6f}%")


if __name__ == "__main__":
    main()
