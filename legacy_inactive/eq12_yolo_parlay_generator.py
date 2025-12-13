#!/usr/bin/env python3
"""
EQ12 YOLO Parlay Generator
Creates massive 15 and 20-leg parlays by being more aggressive with bet combinations
Includes multiple bets per game and SGP combinations
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from random import choice, seed, shuffle

import requests

# Set up logging
log_dir = "C:\\\\EQ12\\logs" if os.name == "nt" else "/workspaces/EQ12/logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"yolo_parlay_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class YoloBet:
    """Represents a YOLO bet for massive parlays"""

    game: str
    market: str
    selection: str
    odds: int
    line: float = None

    @property
    def implied_probability(self) -> float:
        """Calculate implied probability from American odds"""
        if self.odds > 0:
            return 100 / (self.odds + 100)
        else:
            return abs(self.odds) / (abs(self.odds) + 100)

    @property
    def description(self) -> str:
        """Human readable bet description"""
        if self.market == "h2h":
            return f"{self.selection} ML ({self.odds:+d})"
        elif self.market == "spreads":
            sign = "+" if self.line >= 0 else ""
            return f"{self.selection} {sign}{self.line} ({self.odds:+d})"
        elif self.market == "totals":
            return f"{self.selection} {self.line} ({self.odds:+d})"
        return f"{self.selection} ({self.odds:+d})"


class YoloParlayGenerator:
    """Generate massive YOLO parlays for degens"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        self.base_url = "https://api.the-odds-api.com/v4"
        seed(42)  # Reproducible chaos
        logger.info("YOLO Parlay Generator initialized - Maximum degeneracy mode activated!")

    def fetch_all_bets(self) -> list[YoloBet]:
        """Fetch ALL possible bets from NHL games"""
        if not self.api_key:
            return self._get_yolo_demo_bets()

        all_bets = []

        # Get NHL games with all markets
        games_url = f"{self.base_url}/sports/icehockey_nhl/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        try:
            response = requests.get(games_url, params=params, timeout=10)
            response.raise_for_status()
            games = response.json()

            for game in games:
                game_key = f"{game['away_team']} @ {game['home_team']}"

                if game.get("bookmakers"):
                    bookmaker = game["bookmakers"][0]

                    for market_data in bookmaker.get("markets", []):
                        market = market_data["key"]

                        for outcome in market_data.get("outcomes", []):
                            bet = YoloBet(
                                game=game_key,
                                market=market,
                                selection=outcome["name"],
                                odds=outcome["price"],
                                line=outcome.get("point"),
                            )
                            all_bets.append(bet)

            logger.info(f"Fetched {len(all_bets)} YOLO bets from {len(games)} NHL games")

        except Exception as e:
            logger.error(f"Error fetching live data: {e}")
            return self._get_yolo_demo_bets()

        return all_bets

    def _get_yolo_demo_bets(self) -> list[YoloBet]:
        """Generate demo YOLO bets"""
        logger.info("Using demo YOLO bets - prepare for maximum chaos!")

        games = [
            "Chicago Blackhawks @ Boston Bruins",
            "New York Rangers @ Buffalo Sabres",
            "New Jersey Devils @ Carolina Hurricanes",
            "Montreal Canadiens @ Detroit Red Wings",
            "Philadelphia Flyers @ Florida Panthers",
            "New York Islanders @ Pittsburgh Penguins",
            "Ottawa Senators @ Tampa Bay Lightning",
            "Minnesota Wild @ St Louis Blues",
            "Columbus Blue Jackets @ Nashville Predators",
            "Dallas Stars @ Winnipeg Jets",
            "Calgary Flames @ Vancouver Canucks",
            "Utah Hockey Club @ Colorado Avalanche",
            "Anaheim Ducks @ Seattle Kraken",
            "Vegas Golden Knights @ San Jose Sharks",
        ]

        demo_bets = []

        for game in games:
            away_team, home_team = game.split(" @ ")

            # Moneylines
            demo_bets.extend(
                [
                    YoloBet(game, "h2h", home_team, choice([-180, -150, -120, +110])),
                    YoloBet(game, "h2h", away_team, choice([+150, +130, +110, -110])),
                ]
            )

            # Spreads
            spread = choice([1.5, 2.5])
            demo_bets.extend(
                [
                    YoloBet(game, "spreads", home_team, choice([+140, +160]), -spread),
                    YoloBet(game, "spreads", away_team, choice([-180, -200]), +spread),
                ]
            )

            # Totals
            total = choice([5.5, 6.0, 6.5])
            demo_bets.extend(
                [
                    YoloBet(game, "totals", "Over", choice([-110, +100]), total),
                    YoloBet(game, "totals", "Under", choice([-110, +100]), total),
                ]
            )

        return demo_bets

    def generate_yolo_parlays(self, target_legs: list[int]) -> dict[str, list[dict]]:
        """Generate absolutely insane parlays"""
        all_bets = self.fetch_all_bets()
        results = {}

        for leg_count in target_legs:
            logger.info(f"Generating YOLO {leg_count}-leg parlays...")
            parlays = []

            # Generate 10 different YOLO parlays for each leg count
            for _i in range(10):
                shuffle(all_bets)

                # Just take the first N bets - YOLO mode doesn't care about conflicts
                parlay_bets = []

                for bet in all_bets:
                    if len(parlay_bets) >= leg_count:
                        break

                    # Only avoid the most obvious conflicts (same selection twice)
                    bet_key = f"{bet.game}_{bet.market}_{bet.selection}"

                    duplicate = False
                    for existing_bet in parlay_bets:
                        existing_key = (
                            f"{existing_bet.game}_{existing_bet.market}_{existing_bet.selection}"
                        )
                        if bet_key == existing_key:
                            duplicate = True
                            break

                    if not duplicate:
                        parlay_bets.append(bet)

                if len(parlay_bets) == leg_count:
                    # Calculate parlay odds
                    total_prob = 1.0
                    for bet in parlay_bets:
                        total_prob *= bet.implied_probability

                    # Convert to American odds
                    if total_prob >= 0.5:
                        total_odds = int(-100 * total_prob / (1 - total_prob))
                    else:
                        total_odds = int(100 * (1 - total_prob) / total_prob)

                    parlay = {
                        "legs": parlay_bets,
                        "total_odds": total_odds,
                        "probability_pct": total_prob * 100,
                    }
                    parlays.append(parlay)

            # Sort by best odds (highest payout)
            parlays.sort(key=lambda x: x["total_odds"], reverse=True)
            results[f"{leg_count}-leg"] = parlays

        return results

    def format_yolo_output(self, parlays: dict[str, list[dict]]) -> str:
        """Format YOLO parlay output"""
        lines = []
        lines.append("🎰🔥 EQ12 YOLO PARLAY GENERATOR - MAXIMUM DEGENERACY MODE 🔥🎰")
        lines.append("=" * 70)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("⚠️  WARNING: These parlays are ABSOLUTELY INSANE!")
        lines.append("⚠️  FOR ENTERTAINMENT ONLY - DO NOT ACTUALLY BET THESE!")
        lines.append("")

        for parlay_type, parlay_list in parlays.items():
            lines.append(f"💸 {parlay_type.upper()} YOLO PARLAYS")
            lines.append("-" * 50)

            for i, parlay in enumerate(parlay_list, 1):
                prob_pct = parlay["probability_pct"]
                odds = parlay["total_odds"]

                lines.append(f"\n   🎲 YOLO SLIP #{i}")
                lines.append(f"   💰 Total Odds: {odds:+,d}")
                lines.append(f"   🎯 Probability: {prob_pct:.6f}%")
                lines.append("   💀 This is basically impossible but YOLO!")
                lines.append("")

                for j, bet in enumerate(parlay["legs"], 1):
                    lines.append(f"   LEG {j:2d}: {bet.game}")
                    lines.append(f"           {bet.description}")

                lines.append("")

            lines.append("")

        lines.append("🚨 MASSIVE DISCLAIMER 🚨")
        lines.append("These parlays are MATHEMATICALLY INSANE and for entertainment only!")
        lines.append("The probability of hitting a 20-leg parlay is essentially ZERO.")
        lines.append("Please gamble responsibly. This is just for fun!")
        lines.append("If you actually bet these, you will lose your money. Guaranteed.")

        return "\n".join(lines)

    def save_yolo_analysis(self, parlays: dict[str, list[dict]]) -> str:
        """Save YOLO analysis to file"""
        timestamp = datetime.now(UTC).isoformat()

        # Convert to JSON-serializable format
        json_data = {
            "timestamp": timestamp,
            "yolo_mode": True,
            "warning": "These parlays are insane and for entertainment only",
            "parlays": {},
        }

        for parlay_type, parlay_list in parlays.items():
            json_parlays = []
            for parlay in parlay_list:
                json_legs = []
                for bet in parlay["legs"]:
                    json_legs.append(
                        {
                            "game": bet.game,
                            "market": bet.market,
                            "selection": bet.selection,
                            "odds": bet.odds,
                            "line": bet.line,
                            "description": bet.description,
                        }
                    )

                json_parlays.append(
                    {
                        "legs": json_legs,
                        "total_odds": parlay["total_odds"],
                        "probability_pct": parlay["probability_pct"],
                    }
                )

            json_data["parlays"][parlay_type] = json_parlays

        filename = f"yolo_parlay_analysis_{datetime.now().strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(log_dir, filename)

        with open(filepath, "w") as f:
            json.dump(json_data, f, indent=2)

        logger.info(f"YOLO parlay analysis saved to {filepath}")
        return filepath

    def run_yolo_analysis(self, target_legs: list[int] | None = None) -> None:
        """Run the full YOLO parlay analysis"""
        if target_legs is None:
            target_legs = [6, 10, 15, 20]
        logger.info("Starting YOLO parlay analysis - MAXIMUM CHAOS MODE!")

        parlays = self.generate_yolo_parlays(target_legs)
        output = self.format_yolo_output(parlays)

        print(output)

        self.save_yolo_analysis(parlays)

        logger.info("YOLO parlay analysis complete - May the odds be never in your favor!")


def main():
    """Main YOLO function"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 YOLO Parlay Generator - Maximum Degeneracy")
    parser.add_argument(
        "--legs",
        nargs="+",
        type=int,
        default=[6, 10, 15, 20],
        help="Leg counts for YOLO parlays",
    )
    parser.add_argument("--demo", action="store_true", help="Use demo data")

    args = parser.parse_args()

    api_key = None if args.demo else os.getenv("ODDS_API_KEY")

    generator = YoloParlayGenerator(api_key=api_key)
    generator.run_yolo_analysis(target_legs=args.legs)


if __name__ == "__main__":
    main()
