"""
EQ12 Sports Data Pull for Specific Dates

Pull NHL and college football games for 10/11/2025, NFL games for 10/12/2025.
Comprehensive analysis with weather data for outdoor games.
"""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"C:\\\\EQ12\\logs\\\\sports_data_pull_{
                datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12SpecificDateSportsPull:
    """Pull sports data for specific dates using EQ12 multi-API system"""

    def __init__(self):
        # API Keys from environment
        self.odds_api_key = os.getenv(
            "ODDS_API_KEY", "8eb822610b7753d45f76dcac8230a7d1")
        self.openweather_api_key = os.getenv("OPENWEATHER_API_KEY")

        # API Base URLs
        self.odds_api_base = "https://api.the-odds-api.com/v4"
        self.thesportsdb_base = "https://www.thesportsdb.com/api/v1/json/3"
        self.mysportsfeeds_base = "https://api.mysportsfeeds.com/v2.1"
        self.nws_base = "https://api.weather.gov"

        # Target dates
        self.target_dates = {"nhl_college_fb": "2025-10-11", "nfl": "2025-10-12"}

        # Sport configurations
        self.sports_config = {
            "nhl": {
                "odds_api_key": "icehockey_nhl",
                "thesportsdb_id": "4424",
                "outdoor": False,
                "weather_critical": False,
            },
            "college_football": {
                "odds_api_key": "americanfootball_ncaaf",
                "thesportsdb_id": "4391",
                "outdoor": True,
                "weather_critical": True,
            },
            "nfl": {
                "odds_api_key": "americanfootball_nfl",
                "thesportsdb_id": "4391",
                "outdoor": True,
                "weather_critical": True,
            },
        }

        # Results storage
        self.results = {
            "pull_timestamp": datetime.now(UTC).isoformat(),
            "target_dates": self.target_dates,
            "games_found": {},
            "weather_analysis": {},
            "betting_opportunities": {},
            "api_usage": {},
        }

    def get_odds_data(self, sport: str, date_filter: str |
                      None = None) -> list[dict[str, Any]]:
        """Get odds data from The Odds API"""

        if not self.odds_api_key:
            logger.warning(f"ODDS_API_KEY not set - using mock data for {sport}")
            return self._get_mock_odds_data(sport)

        sport_key = self.sports_config[sport]["odds_api_key"]
        url = f"{self.odds_api_base}/sports/{sport_key}/odds"

        params = {
            "apiKey": self.odds_api_key,
            "regions": "us,uk,eu",  # Multi-region for arbitrage
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()

            odds_data = response.json()

            # Filter by date if specified
            if date_filter:
                filtered_games = []
                for game in odds_data:
                    game_date = game.get("commence_time", "")[:10]  # Get YYYY-MM-DD
                    if game_date == date_filter:
                        filtered_games.append(game)
                odds_data = filtered_games

            logger.info(
                f"Retrieved {
                    len(odds_data)} {sport} games for {
                    date_filter or 'all dates'}")

            # Track API usage
            self.results["api_usage"][f"odds_api_{sport}"] = {
                "requests_made": 1,
                "games_returned": len(odds_data),
                "date_filter": date_filter,
            }

            return odds_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching odds for {sport}: {e}")
            return self._get_mock_odds_data(sport)

    def get_thesportsdb_data(
            self, sport: str, season: str = "2024-2025") -> list[dict[str, Any]]:
        """Get supplementary data from TheSportsDB"""

        league_id = self.sports_config[sport]["thesportsdb_id"]
        url = f"{self.thesportsdb_base}/eventsseason.php"

        params = {"id": league_id, "s": season}

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            events = data.get("events", []) if data else []

            # Handle None case
            if events is None:
                events = []

            logger.info(f"Retrieved {len(events)} {sport} events from TheSportsDB")

            self.results["api_usage"][f"thesportsdb_{sport}"] = {
                "requests_made": 1,
                "events_returned": len(events),
            }

            return events

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching TheSportsDB data for {sport}: {e}")
            return []

    def analyze_weather_for_game(self, game_info: dict[str, Any]) -> dict[str, Any]:
        """Analyze weather for outdoor games"""

        # Extract game location (simplified for demo)
        home_team = game_info.get("home_team", "")
        game_info.get("away_team", "")

        # Stadium locations (sample - would need complete database)
        stadium_locations = {
            "Green Bay Packers": {"lat": 44.5013, "lon": -88.0622, "city": "Green Bay"},
            "Chicago Bears": {"lat": 41.8623, "lon": -87.6167, "city": "Chicago"},
            "Kansas City Chiefs": {
                "lat": 39.0489,
                "lon": -94.4839,
                "city": "Kansas City",
            },
            "Denver Broncos": {"lat": 39.7439, "lon": -105.0200, "city": "Denver"},
            "Buffalo Bills": {"lat": 42.7738, "lon": -78.7870, "city": "Buffalo"},
            "New England Patriots": {
                "lat": 42.0909,
                "lon": -71.2643,
                "city": "Foxborough",
            },
            "Pittsburgh Steelers": {
                "lat": 40.4468,
                "lon": -80.0158,
                "city": "Pittsburgh",
            },
            "Cleveland Browns": {"lat": 41.5061, "lon": -81.6995, "city": "Cleveland"},
        }

        location = stadium_locations.get(home_team)
        if not location:
            return {"weather_available": False, "reason": "Location not in database"}

        # Get weather data from NWS (free) or OpenWeather
        try:
            weather_data = self._get_nws_weather(location["lat"], location["lon"])

            weather_analysis = {
                "weather_available": True,
                "location": location,
                "conditions": weather_data,
                "betting_impact": self._assess_weather_impact(weather_data),
                "recommendation": self._generate_weather_recommendation(weather_data),
            }

            return weather_analysis

        except Exception as e:
            logger.warning(f"Could not get weather for {location['city']}: {e}")
            return {"weather_available": False, "error": str(e)}

    def _get_nws_weather(self, lat: float, lon: float) -> dict[str, Any]:
        """Get weather from National Weather Service (free)"""

        try:
            # Get NWS grid point
            points_url = f"{self.nws_base}/points/{lat},{lon}"
            points_response = requests.get(points_url, timeout=10)
            points_response.raise_for_status()

            points_data = points_response.json()
            forecast_url = points_data["properties"]["forecast"]

            # Get forecast
            forecast_response = requests.get(forecast_url, timeout=10)
            forecast_response.raise_for_status()

            forecast_data = forecast_response.json()
            periods = forecast_data["properties"]["periods"]

            # Return first period (today's forecast)
            if periods:
                return {
                    "temperature": periods[0].get("temperature"),
                    "temperature_unit": periods[0].get("temperatureUnit"),
                    "wind_speed": periods[0].get("windSpeed"),
                    "wind_direction": periods[0].get("windDirection"),
                    "short_forecast": periods[0].get("shortForecast"),
                    "detailed_forecast": periods[0].get("detailedForecast"),
                    "source": "NWS (Free)",
                }

            return {"error": "No forecast periods available"}

        except Exception as e:
            logger.warning(f"NWS weather failed: {e}")
            return {"error": f"NWS unavailable: {e}"}

    def _assess_weather_impact(self, weather_data: dict[str, Any]) -> dict[str, Any]:
        """Assess weather impact on game outcomes"""

        if "error" in weather_data:
            return {"impact_level": "unknown", "reason": "Weather data unavailable"}

        temp = weather_data.get("temperature", 70)
        wind_speed = weather_data.get("wind_speed", "0 mph")
        conditions = weather_data.get("short_forecast", "").lower()

        # Extract wind speed number
        wind_mph = 0
        if "mph" in wind_speed:
            try:
                wind_mph = int(wind_speed.split()[0])
            except BaseException:
                wind_mph = 0

        # Impact assessment
        impact_factors = []
        impact_level = "low"

        if temp < 32:
            impact_factors.append("Freezing temperature affects ball handling")
            impact_level = "high"
        elif temp < 45:
            impact_factors.append("Cold temperature may affect passing accuracy")
            impact_level = "medium"

        if wind_mph > 20:
            impact_factors.append("High winds significantly affect passing/kicking")
            impact_level = "high"
        elif wind_mph > 15:
            impact_factors.append("Moderate winds may affect long passes")
            impact_level = "medium"

        if any(word in conditions for word in ["rain", "snow", "storm"]):
            impact_factors.append("Precipitation affects ball handling and footing")
            impact_level = "high"

        return {
            "impact_level": impact_level,
            "factors": impact_factors,
            "temperature": temp,
            "wind_speed_mph": wind_mph,
            "conditions": conditions,
        }

    def _generate_weather_recommendation(self, weather_data: dict[str, Any]) -> str:
        """Generate betting recommendation based on weather"""

        impact = self._assess_weather_impact(weather_data)

        if impact["impact_level"] == "high":
            return "Consider UNDER bets due to adverse weather conditions"
        elif impact["impact_level"] == "medium":
            return "Weather may favor ground game - monitor team rushing stats"
        else:
            return "Weather conditions favorable - minimal impact expected"

    def _get_mock_odds_data(self, sport: str) -> list[dict[str, Any]]:
        """Generate mock data when API unavailable"""

        mock_data = {
            "nhl": [
                {
                    "id": "mock_nhl_1",
                    "sport_key": "icehockey_nhl",
                    "sport_title": "NHL",
                    "commence_time": "2025-10-11T19:00:00Z",
                    "home_team": "Boston Bruins",
                    "away_team": "New York Rangers",
                    "bookmakers": [
                        {
                            "key": "draftkings",
                            "title": "DraftKings",
                            "markets": [
                                {
                                    "key": "h2h",
                                    "outcomes": [
                                        {"name": "Boston Bruins", "price": -120},
                                        {"name": "New York Rangers", "price": +105},
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
            "college_football": [
                {
                    "id": "mock_cfb_1",
                    "sport_key": "americanfootball_ncaaf",
                    "sport_title": "NCAAF",
                    "commence_time": "2025-10-11T17:00:00Z",
                    "home_team": "Alabama Crimson Tide",
                    "away_team": "Georgia Bulldogs",
                    "bookmakers": [
                        {
                            "key": "fanduel",
                            "title": "FanDuel",
                            "markets": [
                                {
                                    "key": "h2h",
                                    "outcomes": [
                                        {"name": "Alabama Crimson Tide", "price": -150},
                                        {"name": "Georgia Bulldogs", "price": +125},
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
            "nfl": [
                {
                    "id": "mock_nfl_1",
                    "sport_key": "americanfootball_nfl",
                    "sport_title": "NFL",
                    "commence_time": "2025-10-12T13:00:00Z",
                    "home_team": "Green Bay Packers",
                    "away_team": "Chicago Bears",
                    "bookmakers": [
                        {
                            "key": "betmgm",
                            "title": "BetMGM",
                            "markets": [
                                {
                                    "key": "h2h",
                                    "outcomes": [
                                        {"name": "Green Bay Packers", "price": -180},
                                        {"name": "Chicago Bears", "price": +155},
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        return mock_data.get(sport, [])

    def pull_all_target_games(self) -> dict[str, Any]:
        """Pull all games for target dates"""

        logger.info("Starting comprehensive sports data pull for target dates")

        # NHL games for 10/11/2025
        logger.info("Pulling NHL games for 2025-10-11...")
        nhl_games = self.get_odds_data("nhl", "2025-10-11")
        self.results["games_found"]["nhl_2025_10_11"] = nhl_games

        # College Football games for 10/11/2025
        logger.info("Pulling College Football games for 2025-10-11...")
        cfb_games = self.get_odds_data("college_football", "2025-10-11")
        self.results["games_found"]["college_football_2025_10_11"] = cfb_games

        # NFL games for 10/12/2025
        logger.info("Pulling NFL games for 2025-10-12...")
        nfl_games = self.get_odds_data("nfl", "2025-10-12")
        self.results["games_found"]["nfl_2025_10_12"] = nfl_games

        # Get supplementary data from TheSportsDB
        logger.info("Getting supplementary data from TheSportsDB...")
        self.get_thesportsdb_data("nhl")
        self.get_thesportsdb_data("college_football")
        self.get_thesportsdb_data("nfl")

        # Weather analysis for outdoor games
        logger.info("Analyzing weather for outdoor games...")

        # Analyze weather for college football games
        cfb_weather = {}
        for game in cfb_games:
            game_id = game.get("id", "unknown")
            weather_analysis = self.analyze_weather_for_game(game)
            cfb_weather[game_id] = weather_analysis

        # Analyze weather for NFL games
        nfl_weather = {}
        for game in nfl_games:
            game_id = game.get("id", "unknown")
            weather_analysis = self.analyze_weather_for_game(game)
            nfl_weather[game_id] = weather_analysis

        self.results["weather_analysis"] = {
            "college_football": cfb_weather,
            "nfl": nfl_weather,
            "nhl": "Indoor sport - weather not applicable",
        }

        # Generate betting opportunities summary
        self._analyze_betting_opportunities()

        return self.results

    def _analyze_betting_opportunities(self):
        """Analyze potential betting opportunities from collected data"""

        opportunities = {
            "arbitrage_potential": [],
            "weather_influenced_bets": [],
            "high_value_games": [],
            "summary": {},
        }

        total_games = 0
        total_bookmakers = 0

        # Analyze each sport's games
        for sport_key, games in self.results["games_found"].items():
            sport_opportunities = []

            for game in games:
                game_analysis = {
                    "game_id": game.get("id"),
                    "matchup": f"{game.get('away_team')} @ {game.get('home_team')}",
                    "commence_time": game.get("commence_time"),
                    "bookmaker_count": len(game.get("bookmakers", [])),
                    "markets_available": [],
                    "arbitrage_potential": False,
                }

                # Check bookmakers and markets
                bookmakers = game.get("bookmakers", [])
                total_bookmakers += len(bookmakers)

                if len(bookmakers) >= 2:
                    game_analysis["arbitrage_potential"] = True
                    opportunities["arbitrage_potential"].append(game_analysis)

                # Check for weather influence (outdoor games)
                if "football" in sport_key:
                    game_id = game.get("id")
                    weather_data = (
                        self.results["weather_analysis"] .get(
                            sport_key.split("_")[0] +
                            "_" +
                            sport_key.split("_")[1],
                            {}) .get(
                            game_id,
                            {}))

                    if weather_data.get("weather_available") and weather_data.get(
                        "betting_impact", {}
                    ).get("impact_level") in ["medium", "high"]:
                        opportunities["weather_influenced_bets"].append(
                            {
                                **game_analysis,
                                "weather_impact": weather_data["betting_impact"],
                                "recommendation": weather_data.get(
                                    "recommendation",
                                    ""),
                            })

                sport_opportunities.append(game_analysis)
                total_games += 1

        opportunities["summary"] = {
            "total_games_found": total_games,
            "total_bookmakers": total_bookmakers,
            "arbitrage_opportunities": len(opportunities["arbitrage_potential"]),
            "weather_influenced_games": len(opportunities["weather_influenced_bets"]),
            "api_calls_made": len(self.results["api_usage"]),
        }

        self.results["betting_opportunities"] = opportunities

    def save_results(self) -> str:
        """Save results to JSON file"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"C:\\\\EQ12\\\\data\\\\sports_pull_{timestamp}.json"

        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, "w") as f:
                json.dump(self.results, f, indent=2, default=str)

            logger.info(f"Results saved to: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Could not save results: {e}")
            return ""

    def print_summary(self):
        """Print formatted summary of results"""

        print("\n" + "=" * 80)
        print("🏈🏒 EQ12 SPORTS DATA PULL RESULTS")
        print("=" * 80)

        print("\n📅 TARGET DATES:")
        print(f"   NHL & College Football: {self.target_dates['nhl_college_fb']}")
        print(f"   NFL: {self.target_dates['nfl']}")

        print("\n📊 GAMES FOUND:")
        for sport_date, games in self.results["games_found"].items():
            sport_name = sport_date.replace("_", " ").title()
            print(f"   {sport_name}: {len(games)} games")

        print("\n🌦️ WEATHER ANALYSIS:")
        weather_data = self.results["weather_analysis"]
        for sport, analysis in weather_data.items():
            if isinstance(analysis, dict):
                weather_games = len(
                    [
                        g
                        for g in analysis.values()
                        if isinstance(g, dict) and g.get("weather_available")
                    ]
                )
                print(
                    f"   {
                        sport.replace(
                            '_',
                            ' ').title()}: {weather_games} games with weather data")
            else:
                print(f"   {sport.upper()}: {analysis}")

        print("\n💰 BETTING OPPORTUNITIES:")
        opportunities = self.results["betting_opportunities"]
        summary = opportunities["summary"]

        print(f"   Total Games: {summary['total_games_found']}")
        print(f"   Bookmaker Connections: {summary['total_bookmakers']}")
        print(f"   Arbitrage Potential: {summary['arbitrage_opportunities']} games")
        print(f"   Weather-Influenced: {summary['weather_influenced_games']} games")

        print("\n🔧 API USAGE:")
        for api_call, usage in self.results["api_usage"].items():
            print(f"   {api_call}: {usage['requests_made']} requests")

        print("\n🎯 TOP OPPORTUNITIES:")

        # Show arbitrage opportunities
        arbitrage_ops = opportunities["arbitrage_potential"][:3]
        for i, opp in enumerate(arbitrage_ops, 1):
            print(f"   {i}. {opp['matchup']} ({opp['bookmaker_count']} bookmakers)")

        # Show weather-influenced games
        weather_ops = opportunities["weather_influenced_bets"][:3]
        if weather_ops:
            print("\n🌦️ WEATHER-INFLUENCED GAMES:")
            for i, game in enumerate(weather_ops, 1):
                impact = game["weather_impact"]["impact_level"]
                print(f"   {i}. {game['matchup']} - {impact.title()} weather impact")
                print(f"      Recommendation: {game['recommendation']}")

        print("\n" + "=" * 80)
        print("🎉 EQ12 Sports Data Pull Complete!")
        print("Ready for betting analysis and arbitrage detection!")
        print("=" * 80)


def main():
    """Main function to run sports data pull"""

    print("🏈🏒 EQ12 Sports Data Pull Starting...")
    print("Target: NHL & College Football (10/11/2025), NFL (10/12/2025)")

    # Create puller
    puller = EQ12SpecificDateSportsPull()

    # Pull all target games
    puller.pull_all_target_games()

    # Print summary
    puller.print_summary()

    # Save results
    filename = puller.save_results()
    if filename:
        print(f"\n📋 Detailed results saved: {filename}")

    print("\n🚀 Next Steps:")
    print("1. Review arbitrage opportunities")
    print("2. Analyze weather-influenced games")
    print("3. Execute betting strategy")
    print("4. Monitor odds changes")


if __name__ == "__main__":
    main()
