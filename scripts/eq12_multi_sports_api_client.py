#!/usr/bin/env python3
"""
EQ12 Multi-API Sports Betting Intelligence System
Combines multiple free APIs for comprehensive MLB, NFL, and College Football analysis
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class GameData:
    """Standardized game data structure"""

    game_id: str
    home_team: str
    away_team: str
    sport: str
    league: str
    game_time: datetime
    venue: str
    venue_type: str  # 'outdoor', 'indoor', 'retractable'
    weather_required: bool
    odds: dict[str, Any]
    stats: dict[str, Any]
    weather_data: dict[str, Any] | None = None


class EQ12MultiSportsAPIClient:
    """
    Comprehensive sports betting intelligence combining multiple free APIs
    Focus: MLB, NFL, College Football with weather analysis
    """

    def __init__(self):
        """Initialize with API keys from environment"""
        # API Keys (some are free, some require registration)
        self.odds_api_key = os.environ.get("ODDS_API_KEY")  # The Odds API
        self.mysportsfeeds_key = os.environ.get(
            "MYSPORTSFEEDS_API_KEY")  # MySportsFeeds

        # Base URLs for free APIs
        self.thesportsdb_base = "https://www.thesportsdb.com/api/v1/json"
        self.odds_api_base = "https://api.the-odds-api.com/v4"
        self.mysportsfeeds_base = "https://api.mysportsfeeds.com/v2.1/pull"

        # Sports configuration - Focus on outdoor games needing weather
        self.sports_config = {
            "MLB": {
                "outdoor_percentage": 85,  # Most MLB stadiums are outdoor
                "weather_critical": True,
                "season_months": [3, 4, 5, 6, 7, 8, 9, 10],
                "thesportsdb_id": "4424",
                "odds_api_key": "baseball_mlb",
            },
            "NFL": {
                "outdoor_percentage": 70,  # Mix of outdoor/indoor/retractable
                "weather_critical": True,
                "season_months": [8, 9, 10, 11, 12, 1],
                "thesportsdb_id": "4391",
                "odds_api_key": "americanfootball_nfl",
            },
            "NCAAF": {
                "outdoor_percentage": 90,  # Most college stadiums outdoor
                "weather_critical": True,
                "season_months": [8, 9, 10, 11, 12],
                "thesportsdb_id": "4387",
                "odds_api_key": "americanfootball_ncaaf",
            },
        }

        # Stadium database for weather requirements
        self.venue_database = self._load_venue_database()

    def _load_venue_database(self) -> dict[str, dict[str, Any]]:
        """Load stadium/venue database with weather requirements"""
        return {
            # MLB - Major outdoor stadiums
            "Fenway Park": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "Boston",
                "lat": 42.3467,
                "lon": -71.0972,
            },
            "Yankee Stadium": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "New York",
                "lat": 40.8296,
                "lon": -73.9262,
            },
            "Wrigley Field": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "Chicago",
                "lat": 41.9484,
                "lon": -87.6553,
            },
            "Coors Field": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "Denver",
                "lat": 39.7559,
                "lon": -104.9942,
            },
            "Kauffman Stadium": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "Kansas City",
                "lat": 39.0517,
                "lon": -94.4803,
            },
            # MLB - Indoor/Retractable (weather less critical)
            "Minute Maid Park": {
                "type": "retractable",
                "weather_critical": False,
                "city": "Houston",
                "lat": 29.7571,
                "lon": -95.3555,
            },
            "Tropicana Field": {
                "type": "indoor",
                "weather_critical": False,
                "city": "St. Petersburg",
                "lat": 27.7683,
                "lon": -82.6534,
            },
            "Rogers Centre": {
                "type": "retractable",
                "weather_critical": False,
                "city": "Toronto",
                "lat": 43.6414,
                "lon": -79.3894,
            },
            # NFL - Major outdoor stadiums
            "Lambeau Field": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "Green Bay",
                "lat": 44.5013,
                "lon": -88.0622,
            },
            "Soldier Field": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "Chicago",
                "lat": 41.8623,
                "lon": -87.6167,
            },
            "Arrowhead Stadium": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "Kansas City",
                "lat": 39.0489,
                "lon": -94.4839,
            },
            "Mile High Stadium": {
                "type": "outdoor",
                "weather_critical": True,
                "city": "Denver",
                "lat": 39.7439,
                "lon": -105.0200,
            },
            # NFL - Indoor stadiums
            "Mercedes-Benz Superdome": {
                "type": "indoor",
                "weather_critical": False,
                "city": "New Orleans",
                "lat": 29.9511,
                "lon": -90.0812,
            },
            "Ford Field": {
                "type": "indoor",
                "weather_critical": False,
                "city": "Detroit",
                "lat": 42.3400,
                "lon": -83.0456,
            },
            "U.S. Bank Stadium": {
                "type": "indoor",
                "weather_critical": False,
                "city": "Minneapolis",
                "lat": 44.9737,
                "lon": -93.2581,
            },
        }

    def get_odds_data(self, sport: str, region: str = "us") -> list[dict[str, Any]]:
        """
        Get current odds from The Odds API
        Free tier: 500 requests/month
        """
        if not self.odds_api_key:
            logger.warning("ODDS_API_KEY not set - using mock data")
            return self._get_mock_odds_data(sport)

        sport_key = self.sports_config[sport]["odds_api_key"]
        url = f"{self.odds_api_base}/sports/{sport_key}/odds"

        params = {
            "apiKey": self.odds_api_key,
            "regions": region,
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            odds_data = response.json()
            logger.info(f"Retrieved {len(odds_data)} {sport} games with odds")
            return odds_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching odds for {sport}: {e}")
            return self._get_mock_odds_data(sport)

    def get_thesportsdb_data(self, sport: str) -> list[dict[str, Any]]:
        """
        Get team and league data from TheSportsDB (completely free)
        """
        league_id = self.sports_config[sport]["thesportsdb_id"]

        # Get current season events
        url = f"{self.thesportsdb_base}/3/eventsseason.php"
        params = {"id": league_id, "s": "2024-2025"}  # Current season

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            events = data.get("events", []) if data else []

            # Handle None case
            if events is None:
                events = []

            logger.info(f"Retrieved {len(events)} {sport} events from TheSportsDB")
            return events

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching TheSportsDB data for {sport}: {e}")
            return []

    def get_mysportsfeeds_data(
        self, sport: str, season: str = "2024-regular"
    ) -> list[dict[str, Any]]:
        """
        Get detailed stats from MySportsFeeds
        Free tier: 500 requests/month
        """
        if not self.mysportsfeeds_key:
            logger.warning("MYSPORTSFEEDS_API_KEY not set - using mock data")
            return self._get_mock_stats_data(sport)

        # Map sports to MySportsFeeds format
        sport_mapping = {"MLB": "mlb", "NFL": "nfl", "NCAA": "ncaa-fb"}

        sport_key = sport_mapping.get(sport)
        if not sport_key:
            logger.error(f"Unsupported sport for MySportsFeeds: {sport}")
            return []

        url = f"{self.mysportsfeeds_base}/{sport_key}/{season}/games.json"

        try:
            response = requests.get(
                url,
                auth=(
                    self.mysportsfeeds_key,
                    "MYSPORTSFEEDS"),
                timeout=10)
            response.raise_for_status()

            data = response.json()
            games = data.get("games", [])

            logger.info(f"Retrieved {len(games)} {sport} games from MySportsFeeds")
            return games

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching MySportsFeeds data for {sport}: {e}")
            return self._get_mock_stats_data(sport)

    def normalize_game_data(
        self,
        sport: str,
        odds_data: list[dict],
        thesportsdb_data: list[dict],
        mysportsfeeds_data: list[dict],
    ) -> list[GameData]:
        """
        Normalize data from multiple APIs into standardized GameData objects
        """
        normalized_games = []

        # Process odds data as primary source (most current)
        for odds_game in odds_data:
            try:
                game_data = self._create_game_from_odds(sport, odds_game)

                # Enhance with venue data from TheSportsDB
                self._enhance_with_thesportsdb(game_data, thesportsdb_data)

                # Enhance with detailed stats from MySportsFeeds
                self._enhance_with_mysportsfeeds(game_data, mysportsfeeds_data)

                # Determine if weather analysis is required
                game_data.weather_required = self._requires_weather_analysis(game_data)

                normalized_games.append(game_data)

            except Exception as e:
                logger.warning(f"Error normalizing game data: {e}")
                continue

        logger.info(f"Normalized {len(normalized_games)} {sport} games")
        return normalized_games

    def _create_game_from_odds(self, sport: str, odds_game: dict) -> GameData:
        """Create GameData object from odds API data"""
        return GameData(
            game_id=f"{sport}_{odds_game.get('id', 'unknown')}",
            home_team=odds_game.get("home_team", ""),
            away_team=odds_game.get("away_team", ""),
            sport=sport,
            league=sport,
            game_time=datetime.fromisoformat(
                odds_game.get("commence_time", "").replace("Z", "+00:00")
            ),
            venue="",  # Will be enhanced
            venue_type="unknown",  # Will be enhanced
            weather_required=False,  # Will be determined
            odds=self._extract_odds_data(odds_game),
            stats={},  # Will be enhanced
        )

    def _extract_odds_data(self, odds_game: dict) -> dict[str, Any]:
        """Extract and structure odds data"""
        odds_data = {"bookmakers": [], "best_odds": {}, "line_movement": {}}

        for bookmaker in odds_game.get("bookmakers", []):
            bookie_data = {"name": bookmaker.get("title", ""), "markets": {}}

            for market in bookmaker.get("markets", []):
                market_key = market.get("key", "")
                bookie_data["markets"][market_key] = {
                    "outcomes": market.get("outcomes", [])}

            odds_data["bookmakers"].append(bookie_data)

        return odds_data

    def _enhance_with_thesportsdb(
            self,
            game_data: GameData,
            thesportsdb_data: list[dict]):
        """Enhance game data with venue information from TheSportsDB"""
        for event in thesportsdb_data:
            if (
                event.get("strHomeTeam") == game_data.home_team
                or event.get("strAwayTeam") == game_data.away_team
            ):

                venue = event.get("strVenue", "")
                game_data.venue = venue

                # Determine venue type from database
                venue_info = self.venue_database.get(venue, {})
                game_data.venue_type = venue_info.get(
                    "type", "outdoor")  # Default outdoor

                break

    def _enhance_with_mysportsfeeds(
            self,
            game_data: GameData,
            mysportsfeeds_data: list[dict]):
        """Enhance game data with detailed statistics"""
        # Add team stats, player stats, historical performance
        game_data.stats.update(
            {
                "team_stats": {},
                "player_stats": {},
                "historical_h2h": {},
                "recent_form": {},
            }
        )

    def _requires_weather_analysis(self, game_data: GameData) -> bool:
        """
        Determine if a game requires weather analysis
        Focus on outdoor venues for MLB, NFL, and College Football
        """
        if game_data.sport not in ["MLB", "NFL", "NCAAF"]:
            return False

        # Indoor games don't need weather analysis
        if game_data.venue_type == "indoor":
            return False

        # Retractable roof stadiums - weather is less critical but still relevant
        if game_data.venue_type == "retractable":
            return True  # Light weather analysis

        # Outdoor games always need weather analysis
        if game_data.venue_type == "outdoor":
            return True

        # Default: if unknown venue type, assume outdoor for these sports
        return True

    def get_comprehensive_analysis(
        self, sports: list[str] | None = None
    ) -> dict[str, list[GameData]]:
        """
        Get comprehensive multi-API analysis for specified sports
        Default: MLB, NFL, NCAAF (all outdoor sports needing weather)
        """
        if sports is None:
            sports = ["MLB", "NFL", "NCAAF"]

        all_games = {}

        for sport in sports:
            logger.info(f"Fetching comprehensive data for {sport}...")

            # Get data from all APIs
            odds_data = self.get_odds_data(sport)
            thesportsdb_data = self.get_thesportsdb_data(sport)
            mysportsfeeds_data = self.get_mysportsfeeds_data(sport)

            # Normalize and combine data
            normalized_games = self.normalize_game_data(
                sport, odds_data, thesportsdb_data, mysportsfeeds_data
            )

            all_games[sport] = normalized_games

            # Rate limiting - be respectful to free APIs
            time.sleep(1)

        return all_games

    def get_weather_required_games(
            self, all_games: dict[str, list[GameData]]) -> list[GameData]:
        """
        Filter games that require weather analysis (outdoor venues)
        """
        weather_games = []

        for _sport, games in all_games.items():
            for game in games:
                if game.weather_required:
                    weather_games.append(game)

        logger.info(f"Found {len(weather_games)} games requiring weather analysis")
        return weather_games

    def _get_mock_odds_data(self, sport: str) -> list[dict[str, Any]]:
        """Mock odds data for testing without API key"""
        return [{"id": f"mock_{sport}_game_1",
                 "sport_key": sport.lower(),
                 "commence_time": (datetime.now() + timedelta(hours=2)).isoformat() + "Z",
                 "home_team": ("Boston Red Sox" if sport == "MLB" else "New England Patriots"),
                 "away_team": "New York Yankees" if sport == "MLB" else "Miami Dolphins",
                 "bookmakers": [{"title": "DraftKings",
                                 "markets": [{"key": "h2h",
                                              "outcomes": [{"name": "Boston Red Sox",
                                                            "price": -110},
                                                           {"name": "New York Yankees",
                                                            "price": 120},
                                                           ],
                                              }],
                                 }],
                 }]

    def _get_mock_stats_data(self, sport: str) -> list[dict[str, Any]]:
        """Mock stats data for testing without API key"""
        return [
            {
                "schedule": {
                    "homeTeam": {"abbreviation": "BOS"},
                    "awayTeam": {"abbreviation": "NYY"},
                    "venue": {"name": "Fenway Park"},
                    "startTime": (datetime.now() + timedelta(hours=2)).isoformat(),
                }
            }
        ]


def main():
    """Test the multi-API sports client"""
    print("🏈🏀⚾ EQ12 MULTI-API SPORTS BETTING INTELLIGENCE")
    print("=" * 60)

    # Initialize client
    client = EQ12MultiSportsAPIClient()

    print("\n📊 FETCHING COMPREHENSIVE SPORTS DATA...")
    print("Sources: The Odds API + TheSportsDB + MySportsFeeds")
    print("Focus: MLB, NFL, College Football")

    # Get comprehensive analysis
    all_games = client.get_comprehensive_analysis(["MLB", "NFL", "NCAAF"])

    # Display results
    total_games = 0
    weather_games_count = 0

    for sport, games in all_games.items():
        print(f"\n🎯 {sport} ANALYSIS:")
        print(f"   Total Games: {len(games)}")

        weather_required = [g for g in games if g.weather_required]
        weather_games_count += len(weather_required)
        total_games += len(games)

        print(f"   Weather Analysis Required: {len(weather_required)}")
        print(f"   Indoor/Covered Games: {len(games) - len(weather_required)}")

        # Show sample games
        for i, game in enumerate(games[:3]):  # Show first 3 games
            print(f"\n   Game {i + 1}: {game.away_team} @ {game.home_team}")
            print(f"   Venue: {game.venue} ({game.venue_type})")
            print(f"   Weather Required: {'Yes' if game.weather_required else 'No'}")
            print(f"   Odds Available: {'Yes' if game.odds['bookmakers'] else 'No'}")

    print("\n🌤️ WEATHER ANALYSIS SUMMARY:")
    print(f"   Total Games Analyzed: {total_games}")
    print(f"   Games Requiring Weather: {weather_games_count}")
    print(f"   Weather Coverage: {weather_games_count / total_games * 100:.1f}%")

    # Get weather-required games for detailed analysis
    weather_games = client.get_weather_required_games(all_games)

    print("\n🎯 OUTDOOR GAMES NEEDING WEATHER ANALYSIS:")
    for game in weather_games[:5]:  # Show first 5
        venue_info = client.venue_database.get(game.venue, {})
        print(f"   {game.away_team} @ {game.home_team}")
        print(f"   Venue: {game.venue} ({game.venue_type})")
        if venue_info:
            print(f"   Location: {venue_info.get('city', 'Unknown')}")
            print(
                f"   Coordinates: {venue_info.get('lat', 'N/A')}, {venue_info.get('lon', 'N/A')}")
        print()

    print("🚀 NEXT STEP: Integrate with EQ12 weather system for complete analysis!")

    # Save analysis to logs
    log_file = f"C:\\\\EQ12\\logs\\multi_api_sports_analysis_{
        datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    analysis_data = {
        "timestamp": datetime.now().isoformat(),
        "total_games": total_games,
        "weather_games": weather_games_count,
        "sports_analyzed": list(all_games.keys()),
        "weather_required_games": [
            {
                "sport": game.sport,
                "teams": f"{game.away_team} @ {game.home_team}",
                "venue": game.venue,
                "venue_type": game.venue_type,
                "game_time": game.game_time.isoformat(),
            }
            for game in weather_games
        ],
    }

    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, "w") as f:
            json.dump(analysis_data, f, indent=2)
        print(f"\n📁 Analysis saved: {log_file}")
    except Exception as e:
        logger.error(f"Failed to save analysis: {e}")


if __name__ == "__main__":
    main()
