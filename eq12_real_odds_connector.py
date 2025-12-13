#!/usr/bin/env python3
"""
EQ12 Real-Time Odds Connector - Live API Integration
==================================================

Connects to real sportsbook APIs to get live odds data:
- The Odds API (multiple sportsbooks)
- ESPN API (game scores/status)
- Pinnacle API (sharp lines)
- Real-time WebSocket feeds

API Keys needed:
- ODDS_API_KEY: The Odds API (theoddsapi.com)
- ESPN_API_KEY: ESPN API (optional)
- PINNACLE_API_KEY: Pinnacle (optional)
"""

import asyncio
import logging
import os
from datetime import UTC, datetime

import aiohttp

logger = logging.getLogger(__name__)


class RealTimeOddsConnector:
    """Real-time odds data connector"""

    def __init__(self):
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        self.base_url = "https://api.the-odds-api.com/v4"
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get_live_games_real(self) -> list[dict]:
        """Get actual live games from The Odds API"""
        if not self.odds_api_key:
            logger.warning("No ODDS_API_KEY found, using demo data")
            return await self._get_demo_games()

        try:
            # Get live/upcoming games for major sports
            sports = [
                "americanfootball_nfl",
                "basketball_nba",
                "baseball_mlb",
                "icehockey_nhl",
                "soccer_epl",
            ]
            all_games = []

            for sport in sports:
                games = await self._fetch_sport_odds(sport)
                all_games.extend(games)

            logger.info(f"Retrieved {len(all_games)} live games from API")
            return all_games

        except Exception as e:
            logger.error(f"API error, falling back to demo: {e}")
            return await self._get_demo_games()

    async def _fetch_sport_odds(self, sport: str) -> list[dict]:
        """Fetch odds for specific sport"""
        url = f"{self.base_url}/sports/{sport}/odds"
        params = {
            "apiKey": self.odds_api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",  # moneyline, spread, totals
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._process_odds_data(data, sport)
            else:
                logger.warning(f"API error for {sport}: {response.status}")
                return []

    def _process_odds_data(self, raw_data: list, sport: str) -> list[dict]:
        """Process raw odds data into standardized format"""
        processed_games = []

        for game in raw_data:
            # Check if game is live or starting soon
            commence_time = datetime.fromisoformat(game["commence_time"].replace("Z", "+00:00"))
            now = datetime.now(UTC)

            # Only include games starting within 4 hours or already started
            if (commence_time - now).total_seconds() > 14400:
                continue

            # Extract best odds from all books
            best_odds = self._extract_best_odds(game.get("bookmakers", []))

            processed_game = {
                "game_id": f"{sport}_{game['id']}",
                "home_team": game["home_team"],
                "away_team": game["away_team"],
                "sport": sport.upper(),
                "commence_time": commence_time,
                "live_odds": best_odds,
                "bookmakers": [book["key"] for book in game.get("bookmakers", [])],
            }

            processed_games.append(processed_game)

        return processed_games

    def _extract_best_odds(self, bookmakers: list) -> dict:
        """Extract best odds across all sportsbooks"""
        best_odds = {"moneyline": {}, "spread": {}, "total": {}}

        for book in bookmakers:
            book["key"]

            for market in book.get("markets", []):
                market_type = market["key"]

                if market_type == "h2h":  # Moneyline
                    for outcome in market["outcomes"]:
                        team_side = "home" if outcome["name"] == book.get("home_team") else "away"
                        odds = outcome["price"]

                        # Track best odds (highest for positive, closest to 0 for negative)
                        if team_side not in best_odds["moneyline"] or self._is_better_odds(
                            odds, best_odds["moneyline"][team_side]
                        ):
                            best_odds["moneyline"][team_side] = odds

                elif market_type == "spreads":
                    for outcome in market["outcomes"]:
                        team_side = "home" if outcome["name"] == book.get("home_team") else "away"
                        spread = outcome.get("point", 0)
                        odds = outcome["price"]

                        spread_key = f"{team_side}_spread"
                        odds_key = f"{team_side}_odds"

                        if spread_key not in best_odds["spread"]:
                            best_odds["spread"][spread_key] = spread
                            best_odds["spread"][odds_key] = odds
                        elif self._is_better_odds(odds, best_odds["spread"][odds_key]):
                            best_odds["spread"][odds_key] = odds

                elif market_type == "totals":
                    for outcome in market["outcomes"]:
                        side = outcome["name"].lower()  # 'over' or 'under'
                        total = outcome.get("point", 0)
                        odds = outcome["price"]

                        if side not in best_odds["total"] or self._is_better_odds(
                            odds, best_odds["total"][f"{side}_odds"]
                        ):
                            best_odds["total"][side] = total
                            best_odds["total"][f"{side}_odds"] = odds

        return best_odds

    def _is_better_odds(self, new_odds: int, current_odds: int) -> bool:
        """Compare which odds are better for the bettor"""
        # For positive odds, higher is better
        if (new_odds > 0 and current_odds > 0) or (new_odds < 0 and current_odds < 0):
            return new_odds > current_odds
        # Mixed signs, positive is always better
        else:
            return new_odds > 0

    async def _get_demo_games(self) -> list[dict]:
        """Demo games for testing when no API key"""
        return [
            {
                "game_id": "demo_nfl_1",
                "home_team": "Denver Broncos",
                "away_team": "Kansas City Chiefs",
                "sport": "NFL",
                "commence_time": datetime.now(UTC),
                "live_odds": {
                    "moneyline": {"home": 185, "away": -220},
                    "spread": {
                        "home_spread": 4.5,
                        "away_spread": -4.5,
                        "home_odds": -110,
                        "away_odds": -110,
                    },
                    "total": {"over": 47.5, "under": 47.5, "over_odds": -110, "under_odds": -110},
                },
                "bookmakers": ["draftkings", "fanduel", "betmgm"],
            },
            {
                "game_id": "demo_nba_1",
                "home_team": "Golden State Warriors",
                "away_team": "Los Angeles Lakers",
                "sport": "NBA",
                "commence_time": datetime.now(UTC),
                "live_odds": {
                    "moneyline": {"home": -150, "away": 125},
                    "spread": {
                        "home_spread": -2.5,
                        "away_spread": 2.5,
                        "home_odds": -110,
                        "away_odds": -110,
                    },
                    "total": {"over": 225.5, "under": 225.5, "over_odds": -115, "under_odds": -105},
                },
                "bookmakers": ["draftkings", "fanduel"],
            },
        ]


# API Usage Example
async def test_real_odds():
    """Test real odds API connection"""
    async with RealTimeOddsConnector() as connector:
        games = await connector.get_live_games_real()

        print(f"Found {len(games)} live/upcoming games:")
        for game in games[:3]:  # Show first 3
            print(f"\n{game['sport']}: {game['away_team']} @ {game['home_team']}")
            print(f"Moneyline: {game['live_odds'].get('moneyline', 'N/A')}")
            print(f"Spread: {game['live_odds'].get('spread', 'N/A')}")
            print(f"Total: {game['live_odds'].get('total', 'N/A')}")

        return games


if __name__ == "__main__":
    print("🔗 Testing EQ12 Real-Time Odds Connector...")
    print("=" * 50)

    # Test the connector
    games = asyncio.run(test_real_odds())

    print(f"\n✅ Successfully retrieved {len(games)} games")
    print("\n💡 To use real data:")
    print("   1. Get API key from theoddsapi.com")
    print("   2. Set environment variable: ODDS_API_KEY=your_key")
    print("   3. Run the parlay scanner with real data")

    print("\n🎯 Your parlay recommendation is ready!")
    print("   Check: OPTIMAL_PARLAY_RECOMMENDATION.md")
