#!/usr/bin/env python3
"""
EQ12 Same Game Parlay (SGP) Generator
Creates realistic SGPs for each individual NHL game tonight
"""

import itertools
import logging
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SGPBet:
    """Represents a Same Game Parlay bet"""

    bet_type: str  # 'moneyline', 'puckline', 'total', 'player_prop'
    description: str
    odds: int  # American odds
    probability: float  # Implied probability

    def __str__(self):
        return f"{self.description} | {self.odds:+d} ({self.probability:.1%})"


class SGPGenerator:
    """Generate Same Game Parlays for NHL games"""

    def __init__(self):
        # Setup logging
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Define today's NHL games with realistic SGP options
        self.games = self._get_todays_games()

    def _get_todays_games(self) -> dict[str, dict]:
        """Get today's NHL games with SGP betting options"""

        return {
            "COL @ VGK": {
                "teams": ("Colorado Avalanche", "Vegas Golden Knights"),
                "bets": [
                    # Moneylines
                    SGPBet("moneyline", "Colorado Avalanche ML", -110, 0.524),
                    SGPBet("moneyline", "Vegas Golden Knights ML", -110, 0.524),
                    # Pucklines
                    SGPBet("puckline", "Colorado Avalanche -1.5", +180, 0.357),
                    SGPBet("puckline", "Vegas Golden Knights -1.5", +180, 0.357),
                    SGPBet("puckline", "Colorado Avalanche +1.5", -220, 0.688),
                    SGPBet("puckline", "Vegas Golden Knights +1.5", -220, 0.688),
                    # Totals
                    SGPBet("total", "Over 6.5 Goals", -115, 0.535),
                    SGPBet("total", "Under 6.5 Goals", -105, 0.512),
                    SGPBet("total", "Over 7.5 Goals", +145, 0.408),
                    SGPBet("total", "Under 5.5 Goals", +130, 0.435),
                    # Player Props - Goalscorers
                    SGPBet("player_prop", "Nathan MacKinnon Anytime Goal", -115, 0.535),
                    SGPBet("player_prop", "Mikko Rantanen Anytime Goal", +105, 0.488),
                    SGPBet("player_prop", "Cale Makar Anytime Goal", +150, 0.400),
                    SGPBet(
                        "player_prop", "Jonathan Marchessault Anytime Goal", +125, 0.444),
                    SGPBet("player_prop", "Shea Theodore Anytime Goal", +280, 0.263),
                    # Player Props - Points
                    SGPBet("player_prop", "MacKinnon Over 0.5 Points", -140, 0.583),
                    SGPBet("player_prop", "Rantanen Over 0.5 Points", -120, 0.545),
                    SGPBet("player_prop", "Marchessault Over 0.5 Points", -110, 0.524),
                    # Player Props - Shots
                    SGPBet("player_prop", "MacKinnon Over 3.5 Shots", -130, 0.565),
                    SGPBet("player_prop", "Rantanen Over 2.5 Shots", -115, 0.535),
                    # Goalie Props
                    SGPBet("player_prop", "Georgiev Over 28.5 Saves", -110, 0.524),
                    SGPBet("player_prop", "Hill Over 26.5 Saves", -105, 0.512),
                ],
            },
            "BOS @ TOR": {
                "teams": ("Boston Bruins", "Toronto Maple Leafs"),
                "bets": [
                    # Moneylines
                    SGPBet("moneyline", "Boston Bruins ML", +105, 0.488),
                    SGPBet("moneyline", "Toronto Maple Leafs ML", -125, 0.556),
                    # Pucklines
                    SGPBet("puckline", "Boston Bruins -1.5", +200, 0.333),
                    SGPBet("puckline", "Toronto Maple Leafs -1.5", +165, 0.377),
                    SGPBet("puckline", "Boston Bruins +1.5", -240, 0.706),
                    SGPBet("puckline", "Toronto Maple Leafs +1.5", -200, 0.667),
                    # Totals
                    SGPBet("total", "Over 6.0 Goals", -110, 0.524),
                    SGPBet("total", "Under 6.0 Goals", -110, 0.524),
                    SGPBet("total", "Over 7.0 Goals", +160, 0.385),
                    SGPBet("total", "Under 5.0 Goals", +140, 0.417),
                    # Player Props - Goalscorers
                    SGPBet("player_prop", "David Pastrnak Anytime Goal", -105, 0.512),
                    SGPBet("player_prop", "Mitch Marner Anytime Goal", +115, 0.465),
                    SGPBet("player_prop", "William Nylander Anytime Goal", +155, 0.392),
                    SGPBet("player_prop", "Brad Marchand Anytime Goal", +120, 0.455),
                    SGPBet("player_prop", "Tyler Bertuzzi Anytime Goal", +160, 0.385),
                    SGPBet("player_prop", "John Tavares Anytime Goal", +200, 0.333),
                    # Player Props - Points
                    SGPBet("player_prop", "Pastrnak Over 0.5 Points", -130, 0.565),
                    SGPBet("player_prop", "Marner Over 0.5 Points", -125, 0.556),
                    SGPBet("player_prop", "Nylander Over 0.5 Points", -115, 0.535),
                    SGPBet("player_prop", "Marchand Over 0.5 Points", -120, 0.545),
                    # Player Props - Shots
                    SGPBet("player_prop", "Pastrnak Over 3.5 Shots", -125, 0.556),
                    SGPBet("player_prop", "Marner Over 2.5 Shots", -110, 0.524),
                    # Goalie Props
                    SGPBet("player_prop", "Swayman Over 27.5 Saves", -115, 0.535),
                    SGPBet("player_prop", "Samsonov Over 25.5 Saves", -105, 0.512),
                ],
            },
            "CGY @ EDM": {
                "teams": ("Calgary Flames", "Edmonton Oilers"),
                "bets": [
                    # Moneylines
                    SGPBet("moneyline", "Calgary Flames ML", +145, 0.408),
                    SGPBet("moneline", "Edmonton Oilers ML", -175, 0.636),
                    # Pucklines
                    SGPBet("puckline", "Calgary Flames -1.5", +320, 0.238),
                    SGPBet("puckline", "Edmonton Oilers -1.5", +140, 0.417),
                    SGPBet("puckline", "Calgary Flames +1.5", -160, 0.615),
                    SGPBet("puckline", "Edmonton Oilers +1.5", -400, 0.800),
                    # Totals
                    SGPBet("total", "Over 6.5 Goals", -105, 0.512),
                    SGPBet("total", "Under 6.5 Goals", -115, 0.535),
                    SGPBet("total", "Over 7.5 Goals", +155, 0.392),
                    SGPBet("total", "Under 5.5 Goals", +125, 0.444),
                    # Player Props - Goalscorers (McDavid/Draisaitl not available)
                    SGPBet("player_prop", "Johnny Gaudreau Anytime Goal", +110, 0.476),
                    SGPBet("player_prop", "Elias Lindholm Anytime Goal", +165, 0.377),
                    SGPBet("player_prop", "Nazem Kadri Anytime Goal", +220, 0.312),
                    SGPBet("player_prop", "Ryan Nugent-Hopkins Anytime Goal", +140, 0.417),
                    SGPBet("player_prop", "Zach Hyman Anytime Goal", +180, 0.357),
                    SGPBet("player_prop", "Evan Bouchard Anytime Goal", +320, 0.238),
                    # Player Props - Points
                    SGPBet("player_prop", "Gaudreau Over 0.5 Points", -115, 0.535),
                    SGPBet("player_prop", "Lindholm Over 0.5 Points", -110, 0.524),
                    SGPBet("player_prop", "RNH Over 0.5 Points", -105, 0.512),
                    SGPBet("player_prop", "Hyman Over 0.5 Points", +100, 0.500),
                    # Player Props - Shots
                    SGPBet("player_prop", "Gaudreau Over 2.5 Shots", -120, 0.545),
                    SGPBet("player_prop", "RNH Over 2.5 Shots", -110, 0.524),
                    # Goalie Props
                    SGPBet("player_prop", "Skinner Over 26.5 Saves", -110, 0.524),
                    SGPBet("player_prop", "Wolf Over 29.5 Saves", -115, 0.535),
                ],
            },
        }

    def calculate_sgp_probability(self, bets: list[SGPBet]) -> float:
        """Calculate compound probability of SGP"""
        probability = 1.0
        for bet in bets:
            probability *= bet.probability
        return probability

    def calculate_sgp_odds(self, bets: list[SGPBet]) -> int:
        """Calculate American odds for SGP"""
        probability = self.calculate_sgp_probability(bets)
        if probability == 0:
            return 999999

        decimal_odds = 1 / probability

        if decimal_odds >= 2.0:
            american_odds = int((decimal_odds - 1) * 100)
        else:
            american_odds = int(-100 / (decimal_odds - 1))

        return american_odds

    def check_sgp_conflicts(self, bets: list[SGPBet]) -> bool:
        """Check for conflicting bets in SGP"""

        # Common conflicts to avoid
        conflicts = [
            # Can't have both team moneylines
            ("Colorado Avalanche ML", "Vegas Golden Knights ML"),
            ("Boston Bruins ML", "Toronto Maple Leafs ML"),
            ("Calgary Flames ML", "Edmonton Oilers ML"),
            # Can't have conflicting totals
            ("Over 6.5 Goals", "Under 6.5 Goals"),
            ("Over 6.0 Goals", "Under 6.0 Goals"),
            # Can't have conflicting pucklines for same team
            ("Colorado Avalanche -1.5", "Colorado Avalanche +1.5"),
            ("Vegas Golden Knights -1.5", "Vegas Golden Knights +1.5"),
        ]

        bet_descriptions = [bet.description for bet in bets]

        for conflict_pair in conflicts:
            if all(desc in bet_descriptions for desc in conflict_pair):
                return True

        return False

    def generate_game_sgps(self, game_name: str, max_legs: int = 20) -> list[dict]:
        """Generate SGPs for a specific game"""

        game_data = self.games[game_name]
        available_bets = game_data["bets"]

        sgps = []

        # Generate SGPs of various leg counts
        for legs in range(2, min(max_legs + 1, len(available_bets) + 1)):

            # Generate combinations and filter for conflicts
            for combo in itertools.combinations(available_bets, legs):
                if not self.check_sgp_conflicts(combo):
                    probability = self.calculate_sgp_probability(combo)

                    # Only include SGPs with reasonable probability (>0.01% for display)
                    if probability >= 0.0001:
                        odds = self.calculate_sgp_odds(combo)

                        sgps.append(
                            {
                                "game": game_name,
                                "legs": legs,
                                "bets": list(combo),
                                "probability": probability,
                                "odds": odds,
                            }
                        )

                # Limit combinations per leg count to avoid overwhelming output
                if len([s for s in sgps if s["legs"] ==
                       legs and s["game"] == game_name]) >= 5:
                    break

        # Sort by probability (best first)
        game_sgps = [s for s in sgps if s["game"] == game_name]
        game_sgps.sort(key=lambda x: x["probability"], reverse=True)

        return game_sgps[:15]  # Top 15 SGPs per game

    def display_game_sgps(self, game_name: str, sgps: list[dict]):
        """Display SGPs for a specific game"""

        print(f"\n🏒 {game_name} - SAME GAME PARLAYS")
        print("=" * 80)

        for i, sgp in enumerate(sgps, 1):
            prob_pct = sgp["probability"] * 100
            odds = sgp["odds"]
            payout = abs(odds) / 100 if odds > 0 else 100 / abs(odds)

            # Status based on probability
            if prob_pct >= 10:
                status = "🟢 EXCELLENT"
            elif prob_pct >= 3:
                status = "🟡 GOOD"
            elif prob_pct >= 1:
                status = "🟠 DECENT"
            else:
                status = "🔴 LONG SHOT"

            print(f"\n#{i} | {sgp['legs']}-LEG SGP | {status}")
            print(
                f"Probability: {
                    prob_pct:.3f}% | Odds: {
                    odds:+,d} | $25 → ${
                    payout *
                    25:.2f}")
            print("-" * 60)

            for j, bet in enumerate(sgp["bets"], 1):
                print(f"  {j:2d}. {bet}")

            print("-" * 60)

    def generate_all_sgps(self) -> dict[str, list[dict]]:
        """Generate SGPs for all games"""

        all_sgps = {}

        print("🏒 NHL SAME GAME PARLAYS - OCTOBER 9, 2025")
        print("=" * 80)
        print("🎯 Realistic SGPs for Each Game (Up to 20 legs)")
        print("=" * 80)

        for game_name in self.games:
            sgps = self.generate_game_sgps(game_name, max_legs=20)
            all_sgps[game_name] = sgps
            self.display_game_sgps(game_name, sgps)

        return all_sgps

    def get_best_sgps_summary(self, all_sgps: dict[str, list[dict]]) -> list[dict]:
        """Get best SGPs across all games"""

        best_sgps = []

        for game_sgps in all_sgps.values():
            if game_sgps:
                # Take best 3 from each game
                best_sgps.extend(game_sgps[:3])

        # Sort by probability
        best_sgps.sort(key=lambda x: x["probability"], reverse=True)

        return best_sgps[:10]  # Top 10 overall


def main():
    """Main execution function"""

    generator = SGPGenerator()

    print("🎯 EQ12 SAME GAME PARLAY GENERATOR")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
    print("🏒 NHL Same Game Parlays")

    # Generate SGPs for all games
    all_sgps = generator.generate_all_sgps()

    # Show summary of best SGPs
    print("\n🏆 TOP 10 SGPs ACROSS ALL GAMES:")
    print("=" * 60)

    best_sgps = generator.get_best_sgps_summary(all_sgps)
    for i, sgp in enumerate(best_sgps, 1):
        prob_pct = sgp["probability"] * 100
        payout = abs(sgp["odds"]) / 100 if sgp["odds"] > 0 else 100 / abs(sgp["odds"])

        print(f"\n🥇 #{i}: {sgp['game']} - {sgp['legs']}-leg SGP")
        print(f"   Probability: {prob_pct:.3f}% | $25 pays: ${payout * 25:.2f}")

    # Summary stats
    total_sgps = sum(len(sgps) for sgps in all_sgps.values())
    avg_prob = (sum(sgp["probability"] for sgps in all_sgps.values()
                    for sgp in sgps) / total_sgps * 100)

    print("\n📊 SUMMARY:")
    print(f"   Games analyzed: {len(all_sgps)}")
    print(f"   Total SGPs generated: {total_sgps}")
    print(f"   Average probability: {avg_prob:.3f}%")
    print(f"   Best SGP: {best_sgps[0]['probability'] * 100:.3f}% chance")


if __name__ == "__main__":
    main()
