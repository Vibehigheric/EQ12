#!/usr/bin/env python3
"""
EQ12 Sports Parlay Analyzer - Demo Mode
Demonstrates parlay analysis with mock data when no API key is available.
"""

import logging
from datetime import datetime, timedelta

# Mock game data for demonstration
MOCK_NHL_GAMES = [
    {
        "id": "demo_nhl_001",
        "sport_key": "icehockey_nhl",
        "commence_time": datetime.now().isoformat() + "Z",
        "home_team": "Toronto Maple Leafs",
        "away_team": "Boston Bruins",
        "bookmakers": [
            {
                "key": "draftkings",
                "title": "DraftKings",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Toronto Maple Leafs", "price": -125},
                            {"name": "Boston Bruins", "price": +105},
                        ],
                    },
                    {
                        "key": "spreads",
                        "outcomes": [
                            {
                                "name": "Toronto Maple Leafs",
                                "price": -110,
                                "point": -1.5,
                            },
                            {"name": "Boston Bruins", "price": -110, "point": +1.5},
                        ],
                    },
                    {
                        "key": "totals",
                        "outcomes": [
                            {"name": "Over", "price": -110, "point": 6.5},
                            {"name": "Under", "price": -110, "point": 6.5},
                        ],
                    },
                ],
            }
        ],
    },
    {
        "id": "demo_nhl_002",
        "sport_key": "icehockey_nhl",
        "commence_time": (datetime.now() + timedelta(hours=2)).isoformat() + "Z",
        "home_team": "New York Rangers",
        "away_team": "Philadelphia Flyers",
        "bookmakers": [
            {
                "key": "fanduel",
                "title": "FanDuel",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "New York Rangers", "price": -140},
                            {"name": "Philadelphia Flyers", "price": +115},
                        ],
                    },
                    {
                        "key": "spreads",
                        "outcomes": [
                            {"name": "New York Rangers", "price": -105, "point": -1.5},
                            {
                                "name": "Philadelphia Flyers",
                                "price": -115,
                                "point": +1.5,
                            },
                        ],
                    },
                    {
                        "key": "totals",
                        "outcomes": [
                            {"name": "Over", "price": +100, "point": 5.5},
                            {"name": "Under", "price": -120, "point": 5.5},
                        ],
                    },
                ],
            }
        ],
    },
]

MOCK_NBA_GAMES = [
    {
        "id": "demo_nba_001",
        "sport_key": "basketball_nba_preseason_sg",
        "commence_time": (datetime.now() + timedelta(hours=4)).isoformat() + "Z",
        "home_team": "Los Angeles Lakers",
        "away_team": "Los Angeles Clippers",
        "bookmakers": [
            {
                "key": "betmgm",
                "title": "BetMGM",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Los Angeles Lakers", "price": +110},
                            {"name": "Los Angeles Clippers", "price": -130},
                        ],
                    },
                    {
                        "key": "spreads",
                        "outcomes": [
                            {
                                "name": "Los Angeles Lakers",
                                "price": -110,
                                "point": +2.5,
                            },
                            {
                                "name": "Los Angeles Clippers",
                                "price": -110,
                                "point": -2.5,
                            },
                        ],
                    },
                    {
                        "key": "totals",
                        "outcomes": [
                            {"name": "Over", "price": -105, "point": 215.5},
                            {"name": "Under", "price": -115, "point": 215.5},
                        ],
                    },
                ],
            }
        ],
    }
]


def run_demo_analysis():
    """Run demonstration analysis with mock data"""
    print("\n" + "=" * 60)
    print("🏒🏀 EQ12 SPORTS PARLAY ANALYZER - DEMO MODE")
    print("=" * 60)
    print("📢 Running with mock data - no API key required")
    print("   For live data, set ODDS_API_KEY environment variable")
    print("=" * 60)

    from eq12_sports_parlay_analyzer import SportsParlay

    # Create analyzer with demo flag
    class DemoSportsParlay(SportsParlay):
        def __init__(self):
            # Initialize without API key for demo
            self.today = datetime.now().strftime("%Y-%m-%d")
            self.sports = {
                "nhl": "icehockey_nhl",
                "nba_preseason": "basketball_nba_preseason_sg",
            }
            logging.info(f"Demo mode initialized for {self.today}")

        def fetch_games_for_sport(self, sport_key: str):
            """Return mock games for demo"""
            if sport_key == "icehockey_nhl":
                return MOCK_NHL_GAMES
            elif sport_key in ["basketball_nba_preseason_sg", "basketball_nba"]:
                return MOCK_NBA_GAMES
            return []

        def run_analysis(self):
            """Run demo analysis with mock data"""
            logging.info("Starting demo sports parlay analysis...")

            results = {
                "date": self.today,
                "demo_mode": True,
                "sports_analyzed": [],
                "games_found": {},
                "game_analyses": [],
                "parlay_suggestions": [],
                "summary": {},
            }

            # Analyze mock data
            for sport_name, sport_key in self.sports.items():
                games = self.fetch_games_for_sport(sport_key)
                results["games_found"][sport_name] = len(games)
                results["sports_analyzed"].append(sport_name)

                # Analyze each game
                for game in games:
                    analysis = self.analyze_game_value(game)
                    results["game_analyses"].append(analysis)

            # Create parlay suggestions
            if results["game_analyses"]:
                results["parlay_suggestions"] = self.create_parlay_suggestions(
                    results["game_analyses"]
                )

            # Generate summary
            total_games = sum(results["games_found"].values())
            high_confidence_games = len(
                [g for g in results["game_analyses"] if g["confidence"] >= 60]
            )

            results["summary"] = {
                "total_games_analyzed": total_games,
                "high_confidence_games": high_confidence_games,
                "parlay_suggestions_generated": len(
                    results["parlay_suggestions"]),
                "sports_with_games": [
                    sport for sport,
                    count in results["games_found"].items() if count > 0],
            }

            return results

    # Run demo analysis
    try:
        analyzer = DemoSportsParlay()
        results = analyzer.run_analysis()

        # Import and use the print function from the main script
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "main_analyzer", "eq12_sports_parlay_analyzer.py"
        )
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)

        main_module.print_results(results)

        print("\n🎯 DEMO COMPLETE!")
        print("   To run with live data:")
        print("   1. Get API key from https://the-odds-api.com")
        print("   2. Set environment variable: $env:ODDS_API_KEY = 'your_key'")
        print("   3. Run: python eq12_sports_parlay_analyzer.py")

    except ImportError as e:
        print(f"❌ Error: Could not import main analyzer: {e}")
        print("   Make sure eq12_sports_parlay_analyzer.py is in the same directory")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    run_demo_analysis()
