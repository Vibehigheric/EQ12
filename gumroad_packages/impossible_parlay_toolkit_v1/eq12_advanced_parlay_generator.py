#!/usr/bin/env python3
"""
EQ12 Advanced Parlay Generator
Generates 6, 10, 15, and 20-leg parlays including Same Game Parlays (SGP)
for NHL games using The Odds API
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import combinations
from random import seed, shuffle
from typing import Any

import requests

# Set up logging
log_dir = "C:\\EQ12\\logs" if os.name == "nt" else "/workspaces/EQ12/logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"advanced_parlay_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class Bet:
    """Represents a single bet"""

    game_id: str
    home_team: str
    away_team: str
    market: str  # 'h2h', 'spreads', 'totals'
    selection: str  # team name or 'Over'/'Under'
    odds: int
    line: float | None = None  # for spreads/totals

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
            return f"{self.selection} ML"
        elif self.market == "spreads":
            sign = "+" if self.line >= 0 else ""
            return f"{self.selection} {sign}{self.line}"
        elif self.market == "totals":
            return f"{self.selection} {self.line}"
        return f"{self.selection}"


@dataclass
class SameGameParlay:
    """Represents a Same Game Parlay (multiple bets from one game)"""

    game_id: str
    home_team: str
    away_team: str
    bets: list[Bet]

    @property
    def combined_odds(self) -> float:
        """Calculate combined odds for the SGP"""
        combined_prob = 1.0
        for bet in self.bets:
            combined_prob *= bet.implied_probability
        # Convert back to American odds
        if combined_prob >= 0.5:
            return int(-100 * combined_prob / (1 - combined_prob))
        else:
            return int(100 * (1 - combined_prob) / combined_prob)

    @property
    def description(self) -> str:
        """Human readable SGP description"""
        game = f"{self.away_team} @ {self.home_team}"
        bets_desc = " + ".join([bet.description for bet in self.bets])
        return f"SGP: {game} ({bets_desc})"


@dataclass
class ParlaySlip:
    """Represents a complete parlay slip"""

    legs: list[Any]  # Can be Bet or SameGameParlay objects
    parlay_type: str  # '6-leg', '10-leg', etc.

    @property
    def total_odds(self) -> int:
        """Calculate total parlay odds"""
        combined_prob = 1.0
        for leg in self.legs:
            if isinstance(leg, Bet):
                combined_prob *= leg.implied_probability
            elif isinstance(leg, SameGameParlay):
                sgp_prob = 1.0
                for bet in leg.bets:
                    sgp_prob *= bet.implied_probability
                combined_prob *= sgp_prob

        # Convert to American odds
        if combined_prob >= 0.5:
            return int(-100 * combined_prob / (1 - combined_prob))
        else:
            return int(100 * (1 - combined_prob) / combined_prob)

    @property
    def expected_probability(self) -> float:
        """Expected probability of parlay hitting"""
        combined_prob = 1.0
        for leg in self.legs:
            if isinstance(leg, Bet):
                combined_prob *= leg.implied_probability
            elif isinstance(leg, SameGameParlay):
                sgp_prob = 1.0
                for bet in leg.bets:
                    sgp_prob *= bet.implied_probability
                combined_prob *= sgp_prob
        return combined_prob


class AdvancedParlayGenerator:
    """Advanced parlay generator with SGP support"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("ODDS_API_KEY")
        if not self.api_key:
            logger.warning("No API key provided - using demo mode")

        self.base_url = "https://api.the-odds-api.com/v4"
        self.sports = ["icehockey_nhl"]
        self.markets = ["h2h", "spreads", "totals"]
        self.games_data = {}

        # Set random seed for reproducible parlay generation
        seed(42)

        logger.info(
            f"Initialized AdvancedParlayGenerator for {datetime.now().strftime('%Y-%m-%d')}"
        )

    def fetch_games(self) -> dict[str, list[dict]]:
        """Fetch games and odds for all sports and markets"""
        if not self.api_key:
            return self._get_demo_data()

        all_games = {}

        for sport in self.sports:
            logger.info(f"Fetching games for {sport}...")

            # Get basic games
            games_url = f"{self.base_url}/sports/{sport}/odds"
            params = {
                "apiKey": self.api_key,
                "regions": "us",
                "markets": ",".join(self.markets),
                "oddsFormat": "american",
                "dateFormat": "iso",
            }

            try:
                response = requests.get(games_url, params=params, timeout=10)
                response.raise_for_status()
                games = response.json()

                if games:
                    all_games[sport] = games
                    logger.info(f"Found {len(games)} games for {sport}")
                else:
                    logger.warning(f"No games found for {sport}")

            except requests.RequestException as e:
                logger.error(f"Error fetching {sport} data: {e}")

        self.games_data = all_games
        return all_games

    def _get_demo_data(self) -> dict[str, list[dict]]:
        """Generate demo data when no API key is available"""
        logger.info("Using demo data (no API key provided)")

        demo_games = {
            "icehockey_nhl": [
                {
                    "id": "demo_chi_bos",
                    "home_team": "Boston Bruins",
                    "away_team": "Chicago Blackhawks",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "markets": [
                                {
                                    "key": "h2h",
                                    "outcomes": [
                                        {"name": "Boston Bruins", "price": -165},
                                        {"name": "Chicago Blackhawks", "price": +140},
                                    ],
                                },
                                {
                                    "key": "spreads",
                                    "outcomes": [
                                        {"name": "Boston Bruins", "price": +154, "point": -1.5},
                                        {
                                            "name": "Chicago Blackhawks",
                                            "price": -190,
                                            "point": +1.5,
                                        },
                                    ],
                                },
                                {
                                    "key": "totals",
                                    "outcomes": [
                                        {"name": "Over", "price": -110, "point": 6.0},
                                        {"name": "Under", "price": -110, "point": 6.0},
                                    ],
                                },
                            ],
                        }
                    ],
                }
                # Add 6 more demo games to simulate tonight's 7 NHL games
            ]
            + [
                {
                    "id": f"demo_game_{i}",
                    "home_team": f"Home Team {i}",
                    "away_team": f"Away Team {i}",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "markets": [
                                {
                                    "key": "h2h",
                                    "outcomes": [
                                        {"name": f"Home Team {i}", "price": -120},
                                        {"name": f"Away Team {i}", "price": +100},
                                    ],
                                },
                                {
                                    "key": "spreads",
                                    "outcomes": [
                                        {"name": f"Home Team {i}", "price": +140, "point": -1.5},
                                        {"name": f"Away Team {i}", "price": -170, "point": +1.5},
                                    ],
                                },
                                {
                                    "key": "totals",
                                    "outcomes": [
                                        {"name": "Over", "price": -105, "point": 5.5 + i * 0.5},
                                        {"name": "Under", "price": -115, "point": 5.5 + i * 0.5},
                                    ],
                                },
                            ],
                        }
                    ],
                }
                for i in range(2, 8)
            ]
        }

        self.games_data = demo_games
        return demo_games

    def extract_all_bets(self) -> list[Bet]:
        """Extract all individual bets from games data"""
        all_bets = []

        for _sport, games in self.games_data.items():
            for game in games:
                game_id = game["id"]
                home_team = game["home_team"]
                away_team = game["away_team"]

                # Use first bookmaker's odds
                if game.get("bookmakers"):
                    bookmaker = game["bookmakers"][0]

                    for market_data in bookmaker.get("markets", []):
                        market = market_data["key"]

                        for outcome in market_data.get("outcomes", []):
                            bet = Bet(
                                game_id=game_id,
                                home_team=home_team,
                                away_team=away_team,
                                market=market,
                                selection=outcome["name"],
                                odds=outcome["price"],
                                line=outcome.get("point"),
                            )
                            all_bets.append(bet)

        logger.info(
            f"Extracted {len(all_bets)} total bets from {len(self.games_data.get('icehockey_nhl', []))} games"
        )
        return all_bets

    def create_same_game_parlays(self) -> list[SameGameParlay]:
        """Create Same Game Parlays (multiple bets from one game)"""
        sgps = []

        for _sport, games in self.games_data.items():
            for game in games:
                game_id = game["id"]
                home_team = game["home_team"]
                away_team = game["away_team"]

                if not game.get("bookmakers"):
                    continue

                bookmaker = game["bookmakers"][0]
                game_bets = []

                # Extract all bets for this game
                for market_data in bookmaker.get("markets", []):
                    market = market_data["key"]

                    for outcome in market_data.get("outcomes", []):
                        bet = Bet(
                            game_id=game_id,
                            home_team=home_team,
                            away_team=away_team,
                            market=market,
                            selection=outcome["name"],
                            odds=outcome["price"],
                            line=outcome.get("point"),
                        )
                        game_bets.append(bet)

                # Create SGP combinations (2-3 bets per game)
                if len(game_bets) >= 2:
                    # 2-leg SGPs
                    for bet_combo in combinations(game_bets, 2):
                        # Avoid conflicting bets (e.g., both teams ML)
                        if self._is_valid_sgp_combo(bet_combo):
                            sgp = SameGameParlay(
                                game_id=game_id,
                                home_team=home_team,
                                away_team=away_team,
                                bets=list(bet_combo),
                            )
                            sgps.append(sgp)

                    # 3-leg SGPs (if we have enough different markets)
                    if len(game_bets) >= 3:
                        for bet_combo in combinations(game_bets, 3):
                            if self._is_valid_sgp_combo(bet_combo):
                                sgp = SameGameParlay(
                                    game_id=game_id,
                                    home_team=home_team,
                                    away_team=away_team,
                                    bets=list(bet_combo),
                                )
                                sgps.append(sgp)

        logger.info(f"Created {len(sgps)} Same Game Parlays")
        return sgps

    def _is_valid_sgp_combo(self, bets: tuple[Bet, ...]) -> bool:
        """Check if bet combination is valid for SGP (no conflicting bets)"""
        markets = [bet.market for bet in bets]
        selections = [bet.selection for bet in bets]

        # Can't have both teams' moneyline
        if markets.count("h2h") > 1:
            return False

        # Can't have both teams' spread
        if markets.count("spreads") > 1:
            return False

        # Can't have both Over and Under
        return not ("Over" in selections and "Under" in selections)

    def generate_parlay_slips(self, target_legs: list[int]) -> dict[int, list[ParlaySlip]]:
        """Generate parlay slips with specified number of legs"""
        all_bets = self.extract_all_bets()
        sgps = self.create_same_game_parlays()

        # Filter to get best bets from each category
        # Prioritize reasonable odds and avoid extreme longshots
        filtered_bets = [
            bet for bet in all_bets if -300 <= bet.odds <= 300 and bet.implied_probability > 0.2
        ]

        # Limit SGPs to best combinations (highest probability)
        sgps.sort(key=lambda x: sum(bet.implied_probability for bet in x.bets), reverse=True)
        filtered_sgps = sgps[:50]  # Keep top 50 SGPs

        # Combine individual bets and SGPs as potential legs (limited set)
        all_legs = filtered_bets[:100] + filtered_sgps  # Limit total legs to manageable number

        logger.info(
            f"Using {len(all_legs)} potential legs ({len(filtered_bets)} bets + {len(filtered_sgps)} SGPs)"
        )

        parlay_slips = {}

        for leg_count in target_legs:
            logger.info(f"Generating {leg_count}-leg parlays...")
            slips = []

            # Use iterative approach instead of generating all combinations at once
            attempts = 0
            max_attempts = 5000 if leg_count >= 15 else 1000

            while len(slips) < 10 and attempts < max_attempts:
                attempts += 1

                # Randomly select legs for this parlay
                shuffle(all_legs)
                potential_legs = []
                games_used = set()
                conflicting_bets = set()

                # Build parlay leg by leg, avoiding conflicts
                for leg in all_legs:
                    if len(potential_legs) >= leg_count:
                        break

                    # Check if this leg conflicts with existing legs
                    if isinstance(leg, Bet):
                        # For longer parlays, allow multiple markets per game but avoid direct conflicts
                        conflict_key = f"{leg.game_id}_{leg.market}_{leg.selection}"
                        game_market_key = f"{leg.game_id}_{leg.market}"

                        # Check for direct conflicts (same market different selection)
                        is_conflict = False
                        for existing_leg in potential_legs:
                            if isinstance(existing_leg, Bet) and (
                                existing_leg.game_id == leg.game_id
                                and existing_leg.market == leg.market
                                and existing_leg.selection != leg.selection
                            ):
                                is_conflict = True
                                break

                        # For longer parlays, be more flexible with game usage
                        if leg_count >= 15:
                            # Allow multiple bets per game for 15+ leg parlays
                            if not is_conflict and conflict_key not in conflicting_bets:
                                potential_legs.append(leg)
                                conflicting_bets.add(conflict_key)
                        else:
                            # Stricter rules for shorter parlays
                            if game_market_key not in games_used and not is_conflict:
                                potential_legs.append(leg)
                                games_used.add(game_market_key)

                    elif isinstance(leg, SameGameParlay):
                        # For SGPs, only allow one per game regardless of parlay length
                        if leg.game_id not in games_used:
                            potential_legs.append(leg)
                            games_used.add(leg.game_id)

                # Create slip if we have enough legs
                if len(potential_legs) == leg_count:
                    slip = ParlaySlip(legs=potential_legs, parlay_type=f"{leg_count}-leg")

                    # Adjust probability threshold based on parlay length
                    min_prob = 0.0001 if leg_count >= 15 else 0.001
                    if slip.expected_probability > min_prob:
                        slips.append(slip)

            # Sort by expected probability (most likely to hit first)
            slips.sort(key=lambda x: x.expected_probability, reverse=True)
            parlay_slips[leg_count] = slips[:5]  # Keep top 5 for each leg count

            logger.info(f"Generated {len(slips)} valid {leg_count}-leg parlays")

        return parlay_slips

    def _is_valid_parlay_combo(self, legs: tuple[Any, ...]) -> bool:
        """Check if parlay combination is valid (no conflicting bets across legs)"""
        games_used = set()

        for leg in legs:
            if isinstance(leg, Bet):
                # For individual bets, track game and market
                key = f"{leg.game_id}_{leg.market}"
                if key in games_used:
                    # Already have a bet on this game/market
                    return False
                games_used.add(key)

            elif isinstance(leg, SameGameParlay):
                # For SGPs, just track the game
                if leg.game_id in games_used:
                    return False
                games_used.add(leg.game_id)

        return True

    def format_parlay_output(self, parlay_slips: dict[int, list[ParlaySlip]]) -> str:
        """Format parlay slips for display"""
        output = []
        output.append("🏒 EQ12 ADVANCED NHL PARLAY GENERATOR")
        output.append("=" * 60)
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")

        total_games = len(self.games_data.get("icehockey_nhl", []))
        output.append("📊 ANALYSIS SUMMARY:")
        output.append(f"   • NHL Games Tonight: {total_games}")
        output.append(f"   • Parlay Types: {', '.join(f'{k}-leg' for k in parlay_slips)}")
        output.append("")

        for leg_count, slips in parlay_slips.items():
            output.append(f"💰 {leg_count}-LEG PARLAYS ({len(slips)} slips)")
            output.append("-" * 40)

            for i, slip in enumerate(slips, 1):
                prob_pct = slip.expected_probability * 100
                output.append(
                    f"\n   SLIP #{i} (Odds: {slip.total_odds:+d}, Probability: {prob_pct:.1f}%)"
                )

                for j, leg in enumerate(slip.legs, 1):
                    if isinstance(leg, Bet):
                        game = f"{leg.away_team} @ {leg.home_team}"
                        output.append(f"   LEG {j}: {game}")
                        output.append(f"            {leg.description} ({leg.odds:+d})")

                    elif isinstance(leg, SameGameParlay):
                        output.append(f"   LEG {j}: {leg.description}")
                        output.append(f"            Combined odds: {leg.combined_odds:+d}")

            output.append("")

        output.append("💡 DISCLAIMER: These parlays are for entertainment purposes only.")
        output.append("   Please gamble responsibly and within your means.")
        output.append("   Same Game Parlays (SGPs) have correlated outcomes - bet accordingly.")

        return "\n".join(output)

    def save_analysis(self, parlay_slips: dict[int, list[ParlaySlip]]) -> str:
        """Save parlay analysis to JSON file"""
        timestamp = datetime.now(UTC).isoformat()

        # Convert to serializable format
        analysis_data = {
            "timestamp": timestamp,
            "games_analyzed": len(self.games_data.get("icehockey_nhl", [])),
            "parlay_slips": {},
        }

        for leg_count, slips in parlay_slips.items():
            slip_data = []
            for slip in slips:
                legs_data = []
                for leg in slip.legs:
                    if isinstance(leg, Bet):
                        legs_data.append(
                            {
                                "type": "single_bet",
                                "game": f"{leg.away_team} @ {leg.home_team}",
                                "market": leg.market,
                                "selection": leg.selection,
                                "odds": leg.odds,
                                "line": leg.line,
                            }
                        )
                    elif isinstance(leg, SameGameParlay):
                        sgp_bets = []
                        for bet in leg.bets:
                            sgp_bets.append(
                                {
                                    "market": bet.market,
                                    "selection": bet.selection,
                                    "odds": bet.odds,
                                    "line": bet.line,
                                }
                            )
                        legs_data.append(
                            {
                                "type": "same_game_parlay",
                                "game": f"{leg.away_team} @ {leg.home_team}",
                                "bets": sgp_bets,
                                "combined_odds": leg.combined_odds,
                            }
                        )

                slip_data.append(
                    {
                        "legs": legs_data,
                        "total_odds": slip.total_odds,
                        "probability": slip.expected_probability,
                    }
                )

            analysis_data["parlay_slips"][str(leg_count)] = slip_data

        # Save to file
        filename = f"advanced_parlay_analysis_{datetime.now().strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(log_dir, filename)

        with open(filepath, "w") as f:
            json.dump(analysis_data, f, indent=2)

        logger.info(f"Advanced parlay analysis saved to {filepath}")
        return filepath

    def run_analysis(self, target_legs: list[int] | None = None) -> None:
        """Run complete advanced parlay analysis"""
        if target_legs is None:
            target_legs = [6, 10, 15, 20]
        logger.info("Starting advanced parlay analysis...")

        # Fetch games data
        games_data = self.fetch_games()
        if not games_data:
            logger.error("No games data available")
            return

        # Generate parlay slips
        parlay_slips = self.generate_parlay_slips(target_legs)

        # Display results
        output = self.format_parlay_output(parlay_slips)
        print(output)

        # Save analysis
        self.save_analysis(parlay_slips)

        logger.info("Advanced parlay analysis completed successfully")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Advanced Parlay Generator")
    parser.add_argument("--api-key", help="The Odds API key")
    parser.add_argument(
        "--legs",
        nargs="+",
        type=int,
        default=[6, 10, 15, 20],
        help="Number of legs for parlays (default: 6 10 15 20)",
    )
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")

    args = parser.parse_args()

    # Use demo mode if requested or no API key available
    api_key = None if args.demo else (args.api_key or os.getenv("ODDS_API_KEY"))

    generator = AdvancedParlayGenerator(api_key=api_key)
    generator.run_analysis(target_legs=args.legs)


if __name__ == "__main__":
    main()
