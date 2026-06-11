"""
EQ12 Stacked NHL SGP Builder
Create one mega SGP combining multiple NHL games on one slip
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import requests


class EQ12StackedNHLSGP:
    """Build stacked SGPs combining multiple NHL games."""

    def __init__(self):
        """Initialize stacked SGP builder."""

        # EQ12 production API key
        self.api_key = "ODDS_API_KEY_PLACEHOLDER"
        self.base_url = "https://api.the-odds-api.com/v4"

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.logger.info("🎰 EQ12 Stacked NHL SGP Builder initialized")

    def fetch_target_games(self):
        """Fetch the 3 target NHL games."""

        try:
            url = f"{self.base_url}/sports/icehockey_nhl/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "dateFormat": "iso",
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            games = response.json()

            target_games = []
            today = datetime.now().date()
            tomorrow = datetime.fromordinal(today.toordinal() + 1).date()

            for game in games:
                try:
                    game_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
                    game_date = game_time.date()

                    # Add enhanced game info
                    game["local_time"] = game_time.strftime("%I:%M %p ET")
                    game["matchup"] = f"{game['away_team']} @ {game['home_team']}"

                    # Check for our 3 target games
                    is_target = False

                    # Game 1: Chicago @ Florida (today)
                    if (
                        game_date == today
                        and "Chicago Blackhawks" in [game["away_team"], game["home_team"]]
                        and "Florida Panthers" in [game["away_team"], game["home_team"]]
                    ):
                        game["game_label"] = "Game 1: CHI @ FLA"
                        is_target = True

                    # Game 2: Pittsburgh @ NYR (12:10 AM)
                    elif (
                        game_date == tomorrow
                        and "Pittsburgh Penguins" in [game["away_team"], game["home_team"]]
                        and "New York Rangers" in [game["away_team"], game["home_team"]]
                    ):
                        game["game_label"] = "Game 2: PIT @ NYR"
                        is_target = True

                    # Game 3: Colorado @ LA Kings (2:50 AM)
                    elif (
                        game_date == tomorrow
                        and "Colorado Avalanche" in [game["away_team"], game["home_team"]]
                        and "Los Angeles Kings" in [game["away_team"], game["home_team"]]
                    ):
                        game["game_label"] = "Game 3: COL @ LAK"
                        is_target = True

                    if is_target:
                        target_games.append(game)

                except Exception as e:
                    self.logger.error(f"Error processing game: {e}")
                    continue

            self.logger.info(f"Found {len(target_games)} target games for stacked SGP")
            return sorted(target_games, key=lambda x: x["commence_time"])

        except Exception as e:
            self.logger.error(f"Failed to fetch target games: {e}")
            return []

    def calculate_american_odds_probability(self, odds):
        """Convert American odds to probability."""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)

    def combine_probabilities(self, probabilities):
        """Combine independent probabilities."""
        combined = 1.0
        for prob in probabilities:
            combined *= prob
        return combined

    def probability_to_american_odds(self, probability):
        """Convert probability back to American odds."""
        if probability >= 0.5:
            return int(-100 * probability / (1 - probability))
        else:
            return int(100 * (1 - probability) / probability)

    def extract_best_picks(self, game):
        """Extract the best picks from each game."""

        markets = {}
        for bookmaker in game.get("bookmakers", []):
            if bookmaker["key"] == "fanduel":
                for market in bookmaker["markets"]:
                    markets[market["key"]] = market["outcomes"]
                break

        if not markets:
            return None

        picks = []

        # Get teams
        home_team = game["home_team"]
        away_team = game["away_team"]

        try:
            # Pick 1: Favorite ML
            h2h = markets.get("h2h", [])
            home_ml = next((o for o in h2h if o["name"] == home_team), None)
            away_ml = next((o for o in h2h if o["name"] == away_team), None)

            if home_ml and away_ml:
                if home_ml["price"] < away_ml["price"]:  # Home is favorite
                    picks.append(
                        {
                            "pick": f"{home_team} ML",
                            "odds": home_ml["price"],
                            "probability": self.calculate_american_odds_probability(
                                home_ml["price"]
                            ),
                        }
                    )
                else:  # Away is favorite
                    picks.append(
                        {
                            "pick": f"{away_team} ML",
                            "odds": away_ml["price"],
                            "probability": self.calculate_american_odds_probability(
                                away_ml["price"]
                            ),
                        }
                    )

            # Pick 2: Favorite Puckline
            spreads = markets.get("spreads", [])
            if spreads:
                # Find the favorite puckline
                for spread in spreads:
                    if spread["point"] < 0:  # This team is getting points (underdog)
                        continue
                    else:
                        picks.append(
                            {
                                "pick": f"{spread['name']} {spread['point']:+.1f}",
                                "odds": spread["price"],
                                "probability": self.calculate_american_odds_probability(
                                    spread["price"]
                                ),
                            }
                        )
                        break

            # Pick 3: Over/Under (pick Over for action)
            totals = markets.get("totals", [])
            over_pick = next((o for o in totals if o["name"] == "Over"), None)
            if over_pick:
                picks.append(
                    {
                        "pick": f"Over {over_pick['point']}",
                        "odds": over_pick["price"],
                        "probability": self.calculate_american_odds_probability(over_pick["price"]),
                    }
                )

        except Exception as e:
            self.logger.error(f"Error extracting picks for {game['matchup']}: {e}")

        return picks

    def build_stacked_sgp(self, games):
        """Build the stacked SGP combining all games."""

        all_picks = []
        game_sections = []

        for game in games:
            picks = self.extract_best_picks(game)
            if not picks:
                continue

            game_sections.append(
                {
                    "game": game["matchup"],
                    "time": game["local_time"],
                    "label": game["game_label"],
                    "picks": picks,
                }
            )

            all_picks.extend(picks)

        if not all_picks:
            return None

        # Find and remove lowest confidence (lowest probability) leg
        lowest_prob_pick = min(all_picks, key=lambda x: x["probability"])

        self.logger.info(
            f"🔍 Removing lowest confidence leg: {lowest_prob_pick['pick']} ({lowest_prob_pick['probability']:.1%} chance)"
        )

        # Remove the lowest confidence pick from all_picks
        all_picks = [pick for pick in all_picks if pick != lowest_prob_pick]

        # Also remove from game_sections for display
        for section in game_sections:
            section["picks"] = [pick for pick in section["picks"] if pick != lowest_prob_pick]

        # Calculate combined probability and odds with remaining picks
        probabilities = [pick["probability"] for pick in all_picks]
        combined_prob = self.combine_probabilities(probabilities)
        combined_odds = self.probability_to_american_odds(combined_prob)

        # Calculate potential payouts
        stake = 45  # Standard EQ12 stake
        if combined_odds > 0:
            payout = stake + (stake * combined_odds / 100)
        else:
            payout = stake + (stake * 100 / abs(combined_odds))

        roi = payout / stake
        expected_value = (combined_prob * payout - stake) / stake * 100

        return {
            "type": "Optimized Stacked SGP",
            "total_legs": len(all_picks),
            "games": len(game_sections),
            "game_sections": game_sections,
            "combined_odds": combined_odds,
            "combined_probability": combined_prob,
            "stake": stake,
            "payout": payout,
            "roi": roi,
            "expected_value": expected_value,
            "all_picks": all_picks,
            "removed_leg": {
                "pick": lowest_prob_pick["pick"],
                "odds": lowest_prob_pick["odds"],
                "probability": lowest_prob_pick["probability"],
                "reason": "Lowest confidence leg removed to optimize win probability",
            },
        }

    def display_stacked_sgp(self, sgp):
        """Display the stacked SGP in a formatted way."""

        print(f"\n🎰 STACKED NHL SGP - {sgp['games']} GAMES, {sgp['total_legs']} LEGS")
        print("=" * 70)

        # Game breakdown
        for i, section in enumerate(sgp["game_sections"], 1):
            print(f"\n🏒 {section['label']} - {section['game']} ({section['time']})")
            for j, pick in enumerate(section["picks"], 1):
                print(
                    f"   Leg {len([p for s in sgp['game_sections'][: i - 1] for p in s['picks']]) + j}: {pick['pick']} ({pick['odds']:+d})"
                )

        # Combined results
        print("\n🎯 STACKED SGP SUMMARY")
        print("=" * 40)
        print(f"Total Legs: {sgp['total_legs']}")
        print(f"Combined Odds: {sgp['combined_odds']:+d}")
        print(f"Win Probability: {sgp['combined_probability']:.1%}")
        print(f"Stake: ${sgp['stake']}")
        print(f"Potential Payout: ${sgp['payout']:.0f}")
        print(f"ROI: {sgp['roi']:.1f}x")
        print(f"Expected Value: {sgp['expected_value']:+.1f}%")

        # Show removed leg
        if "removed_leg" in sgp:
            print("\n❌ REMOVED LEG (Lowest Confidence):")
            print(f"   {sgp['removed_leg']['pick']} ({sgp['removed_leg']['odds']:+d})")
            print(f"   Win Probability: {sgp['removed_leg']['probability']:.1%}")
            print(f"   Reason: {sgp['removed_leg']['reason']}")

        # Risk assessment
        if sgp["roi"] >= 100:
            print(f"\n🚀 LOTTERY TICKET STATUS: {sgp['roi']:.0f}x ROI!")
        elif sgp["roi"] >= 50:
            print(f"\n🎲 HIGH RISK/REWARD: {sgp['roi']:.0f}x ROI")
        else:
            print(f"\n⚖️ MODERATE RISK: {sgp['roi']:.1f}x ROI")

        return sgp


def main():
    """Build stacked SGP for the 3 target NHL games."""

    print("🎰 EQ12 STACKED NHL SGP BUILDER")
    print("=" * 50)
    print("Combining CHI@FLA + PIT@NYR + COL@LAK into ONE MEGA SLIP")

    try:
        builder = EQ12StackedNHLSGP()

        # Fetch target games
        print("\n🔄 Fetching 3 target games...")
        games = builder.fetch_target_games()

        if len(games) != 3:
            print(f"❌ Expected 3 games, found {len(games)}")
            return

        # Build stacked SGP
        print("\n🏗️ Building stacked SGP...")
        stacked_sgp = builder.build_stacked_sgp(games)

        if not stacked_sgp:
            print("❌ Failed to build stacked SGP")
            return

        # Display results
        builder.display_stacked_sgp(stacked_sgp)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        log_file = Path("C:/EQ12/logs") / f"stacked_nhl_sgp_{timestamp}.json"

        with open(log_file, "w") as f:
            json.dump(stacked_sgp, f, indent=2, default=str)

        print(f"\n💾 Stacked SGP saved: {log_file}")

        # Strategy recommendation
        print("\n💡 STRATEGY COMPARISON:")
        print("Individual SGPs: 3 bets x $45 = $135 total, multiple win chances")
        print(f"Stacked SGP: 1 bet x $45 = $45 total, {stacked_sgp['roi']:.0f}x lottery ticket")
        print("\nRecommendation: Consider both approaches for diversification")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
