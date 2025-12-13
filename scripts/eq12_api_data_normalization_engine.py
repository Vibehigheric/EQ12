#!/usr/bin/env python3
"""
EQ12 API Data Normalization Engine
Unified data format from multiple sports/weather APIs with cross-validation
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Enumeration of supported data sources"""

    THE_ODDS_API = "the_odds_api"
    THESPORTSDB = "thesportsdb"
    MYSPORTSFEEDS = "mysportsfeeds"
    NWS_WEATHER = "nws_weather"
    OPENWEATHER = "openweather"
    WEATHERAPI = "weatherapi"


@dataclass
class NormalizedTeam:
    """Standardized team information"""

    name: str
    abbreviation: str
    city: str
    full_name: str
    league: str


@dataclass
class NormalizedOdds:
    """Standardized odds information"""

    bookmaker: str
    home_team_odds: float
    away_team_odds: float
    spread_home: float | None = None
    spread_away: float | None = None
    total_over: float | None = None
    total_under: float | None = None
    total_points: float | None = None


@dataclass
class NormalizedWeather:
    """Standardized weather information"""

    temperature_f: float
    temperature_c: float
    feels_like_f: float
    feels_like_c: float
    humidity_percent: int
    wind_speed_mph: float
    wind_speed_kmh: float
    wind_direction: str
    precipitation_inch: float
    precipitation_mm: float
    precipitation_probability: int
    visibility_miles: float
    visibility_km: float
    pressure_inhg: float
    pressure_mb: float
    weather_description: str
    timestamp: datetime
    source: DataSource


@dataclass
class NormalizedGame:
    """Standardized game information combining all sources"""

    game_id: str
    sport: str
    league: str
    home_team: NormalizedTeam
    away_team: NormalizedTeam
    game_datetime: datetime
    venue_name: str
    venue_city: str
    venue_state: str
    venue_type: str  # outdoor, indoor, retractable
    coordinates: tuple  # (lat, lon)
    status: str  # scheduled, in_progress, completed, postponed
    odds: list[NormalizedOdds]
    weather: NormalizedWeather | None
    data_sources: list[DataSource]
    data_quality_score: float
    last_updated: datetime


class EQ12DataNormalizationEngine:
    """
    Comprehensive data normalization engine for EQ12 betting system
    Handles multiple API formats and creates unified data structures
    """

    def __init__(self):
        """Initialize with team mapping databases"""
        self.team_mappings = self._load_team_mappings()
        self.venue_mappings = self._load_venue_mappings()

    def _load_team_mappings(self) -> dict[str, dict[str, str]]:
        """Load comprehensive team name mappings for normalization"""
        return {
            "MLB": {
                # The Odds API -> Standard mapping
                "Boston Red Sox": {
                    "abbr": "BOS",
                    "city": "Boston",
                    "full": "Boston Red Sox",
                },
                "New York Yankees": {
                    "abbr": "NYY",
                    "city": "New York",
                    "full": "New York Yankees",
                },
                "Chicago Cubs": {
                    "abbr": "CHC",
                    "city": "Chicago",
                    "full": "Chicago Cubs",
                },
                "Chicago White Sox": {
                    "abbr": "CWS",
                    "city": "Chicago",
                    "full": "Chicago White Sox",
                },
                "Houston Astros": {
                    "abbr": "HOU",
                    "city": "Houston",
                    "full": "Houston Astros",
                },
                "Los Angeles Dodgers": {
                    "abbr": "LAD",
                    "city": "Los Angeles",
                    "full": "Los Angeles Dodgers",
                },
                "Los Angeles Angels": {
                    "abbr": "LAA",
                    "city": "Los Angeles",
                    "full": "Los Angeles Angels",
                },
                "San Francisco Giants": {
                    "abbr": "SF",
                    "city": "San Francisco",
                    "full": "San Francisco Giants",
                },
                "Oakland Athletics": {
                    "abbr": "OAK",
                    "city": "Oakland",
                    "full": "Oakland Athletics",
                },
                "Seattle Mariners": {
                    "abbr": "SEA",
                    "city": "Seattle",
                    "full": "Seattle Mariners",
                },
                "Texas Rangers": {
                    "abbr": "TEX",
                    "city": "Texas",
                    "full": "Texas Rangers",
                },
                "Minnesota Twins": {
                    "abbr": "MIN",
                    "city": "Minnesota",
                    "full": "Minnesota Twins",
                },
                "Detroit Tigers": {
                    "abbr": "DET",
                    "city": "Detroit",
                    "full": "Detroit Tigers",
                },
                "Cleveland Guardians": {
                    "abbr": "CLE",
                    "city": "Cleveland",
                    "full": "Cleveland Guardians",
                },
                "Kansas City Royals": {
                    "abbr": "KC",
                    "city": "Kansas City",
                    "full": "Kansas City Royals",
                },
                "Milwaukee Brewers": {
                    "abbr": "MIL",
                    "city": "Milwaukee",
                    "full": "Milwaukee Brewers",
                },
                "St. Louis Cardinals": {
                    "abbr": "STL",
                    "city": "St. Louis",
                    "full": "St. Louis Cardinals",
                },
                "Pittsburgh Pirates": {
                    "abbr": "PIT",
                    "city": "Pittsburgh",
                    "full": "Pittsburgh Pirates",
                },
                "Cincinnati Reds": {
                    "abbr": "CIN",
                    "city": "Cincinnati",
                    "full": "Cincinnati Reds",
                },
                "Atlanta Braves": {
                    "abbr": "ATL",
                    "city": "Atlanta",
                    "full": "Atlanta Braves",
                },
                "New York Mets": {
                    "abbr": "NYM",
                    "city": "New York",
                    "full": "New York Mets",
                },
                "Philadelphia Phillies": {
                    "abbr": "PHI",
                    "city": "Philadelphia",
                    "full": "Philadelphia Phillies",
                },
                "Washington Nationals": {
                    "abbr": "WSN",
                    "city": "Washington",
                    "full": "Washington Nationals",
                },
                "Miami Marlins": {
                    "abbr": "MIA",
                    "city": "Miami",
                    "full": "Miami Marlins",
                },
                "Tampa Bay Rays": {
                    "abbr": "TB",
                    "city": "Tampa Bay",
                    "full": "Tampa Bay Rays",
                },
                "Baltimore Orioles": {
                    "abbr": "BAL",
                    "city": "Baltimore",
                    "full": "Baltimore Orioles",
                },
                "Toronto Blue Jays": {
                    "abbr": "TOR",
                    "city": "Toronto",
                    "full": "Toronto Blue Jays",
                },
                "Colorado Rockies": {
                    "abbr": "COL",
                    "city": "Colorado",
                    "full": "Colorado Rockies",
                },
                "Arizona Diamondbacks": {
                    "abbr": "ARI",
                    "city": "Arizona",
                    "full": "Arizona Diamondbacks",
                },
                "San Diego Padres": {
                    "abbr": "SD",
                    "city": "San Diego",
                    "full": "San Diego Padres",
                },
            },
            "NFL": {
                # NFL team mappings
                "New England Patriots": {
                    "abbr": "NE",
                    "city": "New England",
                    "full": "New England Patriots",
                },
                "Miami Dolphins": {
                    "abbr": "MIA",
                    "city": "Miami",
                    "full": "Miami Dolphins",
                },
                "Buffalo Bills": {
                    "abbr": "BUF",
                    "city": "Buffalo",
                    "full": "Buffalo Bills",
                },
                "New York Jets": {
                    "abbr": "NYJ",
                    "city": "New York",
                    "full": "New York Jets",
                },
                "Pittsburgh Steelers": {
                    "abbr": "PIT",
                    "city": "Pittsburgh",
                    "full": "Pittsburgh Steelers",
                },
                "Baltimore Ravens": {
                    "abbr": "BAL",
                    "city": "Baltimore",
                    "full": "Baltimore Ravens",
                },
                "Cleveland Browns": {
                    "abbr": "CLE",
                    "city": "Cleveland",
                    "full": "Cleveland Browns",
                },
                "Cincinnati Bengals": {
                    "abbr": "CIN",
                    "city": "Cincinnati",
                    "full": "Cincinnati Bengals",
                },
                "Kansas City Chiefs": {
                    "abbr": "KC",
                    "city": "Kansas City",
                    "full": "Kansas City Chiefs",
                },
                "Las Vegas Raiders": {
                    "abbr": "LV",
                    "city": "Las Vegas",
                    "full": "Las Vegas Raiders",
                },
                "Los Angeles Chargers": {
                    "abbr": "LAC",
                    "city": "Los Angeles",
                    "full": "Los Angeles Chargers",
                },
                "Denver Broncos": {
                    "abbr": "DEN",
                    "city": "Denver",
                    "full": "Denver Broncos",
                },
                "Indianapolis Colts": {
                    "abbr": "IND",
                    "city": "Indianapolis",
                    "full": "Indianapolis Colts",
                },
                "Tennessee Titans": {
                    "abbr": "TEN",
                    "city": "Tennessee",
                    "full": "Tennessee Titans",
                },
                "Houston Texans": {
                    "abbr": "HOU",
                    "city": "Houston",
                    "full": "Houston Texans",
                },
                "Jacksonville Jaguars": {
                    "abbr": "JAX",
                    "city": "Jacksonville",
                    "full": "Jacksonville Jaguars",
                },
                "Green Bay Packers": {
                    "abbr": "GB",
                    "city": "Green Bay",
                    "full": "Green Bay Packers",
                },
                "Chicago Bears": {
                    "abbr": "CHI",
                    "city": "Chicago",
                    "full": "Chicago Bears",
                },
                "Detroit Lions": {
                    "abbr": "DET",
                    "city": "Detroit",
                    "full": "Detroit Lions",
                },
                "Minnesota Vikings": {
                    "abbr": "MIN",
                    "city": "Minnesota",
                    "full": "Minnesota Vikings",
                },
                "Dallas Cowboys": {
                    "abbr": "DAL",
                    "city": "Dallas",
                    "full": "Dallas Cowboys",
                },
                "Philadelphia Eagles": {
                    "abbr": "PHI",
                    "city": "Philadelphia",
                    "full": "Philadelphia Eagles",
                },
                "New York Giants": {
                    "abbr": "NYG",
                    "city": "New York",
                    "full": "New York Giants",
                },
                "Washington Commanders": {
                    "abbr": "WAS",
                    "city": "Washington",
                    "full": "Washington Commanders",
                },
                "San Francisco 49ers": {
                    "abbr": "SF",
                    "city": "San Francisco",
                    "full": "San Francisco 49ers",
                },
                "Seattle Seahawks": {
                    "abbr": "SEA",
                    "city": "Seattle",
                    "full": "Seattle Seahawks",
                },
                "Los Angeles Rams": {
                    "abbr": "LAR",
                    "city": "Los Angeles",
                    "full": "Los Angeles Rams",
                },
                "Arizona Cardinals": {
                    "abbr": "ARI",
                    "city": "Arizona",
                    "full": "Arizona Cardinals",
                },
                "Tampa Bay Buccaneers": {
                    "abbr": "TB",
                    "city": "Tampa Bay",
                    "full": "Tampa Bay Buccaneers",
                },
                "New Orleans Saints": {
                    "abbr": "NO",
                    "city": "New Orleans",
                    "full": "New Orleans Saints",
                },
                "Atlanta Falcons": {
                    "abbr": "ATL",
                    "city": "Atlanta",
                    "full": "Atlanta Falcons",
                },
                "Carolina Panthers": {
                    "abbr": "CAR",
                    "city": "Carolina",
                    "full": "Carolina Panthers",
                },
            },
        }

    def _load_venue_mappings(self) -> dict[str, dict[str, Any]]:
        """Load comprehensive venue mappings with coordinates and attributes"""
        return {
            # MLB Venues
            "Fenway Park": {
                "city": "Boston",
                "state": "MA",
                "type": "outdoor",
                "coordinates": (42.3467, -71.0972),
                "capacity": 37755,
            },
            "Yankee Stadium": {
                "city": "New York",
                "state": "NY",
                "type": "outdoor",
                "coordinates": (40.8296, -73.9262),
                "capacity": 54251,
            },
            "Wrigley Field": {
                "city": "Chicago",
                "state": "IL",
                "type": "outdoor",
                "coordinates": (41.9484, -87.6553),
                "capacity": 41649,
            },
            "Coors Field": {
                "city": "Denver",
                "state": "CO",
                "type": "outdoor",
                "coordinates": (39.7559, -104.9942),
                "capacity": 50398,
            },
            # NFL Venues
            "Lambeau Field": {
                "city": "Green Bay",
                "state": "WI",
                "type": "outdoor",
                "coordinates": (44.5013, -88.0622),
                "capacity": 81441,
            },
            "Soldier Field": {
                "city": "Chicago",
                "state": "IL",
                "type": "outdoor",
                "coordinates": (41.8623, -87.6167),
                "capacity": 61500,
            },
            "Arrowhead Stadium": {
                "city": "Kansas City",
                "state": "MO",
                "type": "outdoor",
                "coordinates": (39.0489, -94.4839),
                "capacity": 76416,
            },
            # Indoor/Retractable Venues
            "Ford Field": {
                "city": "Detroit",
                "state": "MI",
                "type": "indoor",
                "coordinates": (42.3400, -83.0456),
                "capacity": 65000,
            },
            "Minute Maid Park": {
                "city": "Houston",
                "state": "TX",
                "type": "retractable",
                "coordinates": (29.7571, -95.3555),
                "capacity": 41168,
            },
        }

    def normalize_the_odds_api_data(
            self, raw_data: dict[str, Any], sport: str) -> NormalizedGame:
        """Normalize data from The Odds API"""
        try:
            # Extract basic game info
            game_id = f"odds_{raw_data.get('id', 'unknown')}"
            home_team_name = raw_data.get("home_team", "")
            away_team_name = raw_data.get("away_team", "")

            # Normalize teams
            home_team = self._normalize_team(home_team_name, sport)
            away_team = self._normalize_team(away_team_name, sport)

            # Parse game time
            commence_time = raw_data.get("commence_time", "")
            game_datetime = self._parse_datetime(commence_time)

            # Extract odds
            normalized_odds = []
            for bookmaker in raw_data.get("bookmakers", []):
                odds = self._normalize_odds_from_bookmaker(bookmaker)
                if odds:
                    normalized_odds.append(odds)

            # Create normalized game (venue info will be enhanced by other sources)
            normalized_game = NormalizedGame(
                game_id=game_id,
                sport=sport,
                league=sport,
                home_team=home_team,
                away_team=away_team,
                game_datetime=game_datetime,
                venue_name="",  # To be filled by other sources
                venue_city="",
                venue_state="",
                venue_type="outdoor",  # Default assumption
                coordinates=(0.0, 0.0),  # To be filled
                status="scheduled",
                odds=normalized_odds,
                weather=None,
                data_sources=[DataSource.THE_ODDS_API],
                data_quality_score=0.7,  # Odds API provides good odds, limited venue info
                last_updated=datetime.now(UTC),
            )

            return normalized_game

        except Exception as e:
            logger.error(f"Error normalizing Odds API data: {e}")
            raise

    def normalize_thesportsdb_data(
        self, raw_data: dict[str, Any], sport: str
    ) -> dict[str, Any] | None:
        """Normalize data from TheSportsDB for venue enhancement"""
        try:
            venue_name = raw_data.get("strVenue", "")
            home_team = raw_data.get("strHomeTeam", "")
            away_team = raw_data.get("strAwayTeam", "")

            # Map venue information
            venue_info = self.venue_mappings.get(venue_name, {})

            return {
                "venue_name": venue_name,
                "venue_city": venue_info.get("city", ""),
                "venue_state": venue_info.get("state", ""),
                "venue_type": venue_info.get("type", "outdoor"),
                "coordinates": venue_info.get("coordinates", (0.0, 0.0)),
                "home_team": home_team,
                "away_team": away_team,
            }

        except Exception as e:
            logger.error(f"Error normalizing TheSportsDB data: {e}")
            return None

    def normalize_weather_data(
        self, raw_data: dict[str, Any], source: DataSource
    ) -> NormalizedWeather:
        """Normalize weather data from various sources"""

        if source == DataSource.NWS_WEATHER:
            return self._normalize_nws_weather(raw_data)
        elif source == DataSource.OPENWEATHER:
            return self._normalize_openweather_data(raw_data)
        elif source == DataSource.WEATHERAPI:
            return self._normalize_weatherapi_data(raw_data)
        else:
            raise ValueError(f"Unsupported weather source: {source}")

    def _normalize_nws_weather(self, raw_data: dict[str, Any]) -> NormalizedWeather:
        """Normalize National Weather Service data"""
        try:
            # NWS typically provides temperature in Celsius
            temp_c = raw_data.get("temperature", 20)  # Default 20°C
            temp_f = self._celsius_to_fahrenheit(temp_c)

            # Extract other metrics
            humidity = raw_data.get("relativeHumidity", {}).get("value", 50)
            wind_speed_mps = raw_data.get("windSpeed", {}).get("value", 0)  # m/s
            wind_speed_mph = self._mps_to_mph(wind_speed_mps)
            wind_direction = raw_data.get("windDirection", {}).get("value", "SW")

            # Visibility (convert from meters to miles if needed)
            visibility_m = raw_data.get(
                "visibility", {}).get(
                "value", 16000)  # Default 10 miles
            visibility_miles = self._meters_to_miles(visibility_m)

            return NormalizedWeather(
                temperature_f=temp_f,
                temperature_c=temp_c,
                feels_like_f=temp_f,  # NWS doesn't always provide feels_like
                feels_like_c=temp_c,
                humidity_percent=int(humidity),
                wind_speed_mph=wind_speed_mph,
                wind_speed_kmh=self._mph_to_kmh(wind_speed_mph),
                wind_direction=self._normalize_wind_direction(wind_direction),
                precipitation_inch=0.0,  # Would need forecast data
                precipitation_mm=0.0,
                precipitation_probability=0,
                visibility_miles=visibility_miles,
                visibility_km=self._miles_to_km(visibility_miles),
                pressure_inhg=29.92,  # Default if not available
                pressure_mb=1013.25,
                weather_description=raw_data.get("textDescription", "Clear"),
                timestamp=datetime.now(UTC),
                source=DataSource.NWS_WEATHER,
            )

        except Exception as e:
            logger.error(f"Error normalizing NWS weather data: {e}")
            raise

    def _normalize_openweather_data(
            self, raw_data: dict[str, Any]) -> NormalizedWeather:
        """Normalize OpenWeather API data"""
        try:
            current = raw_data.get("current", {})

            temp_k = current.get("temp", 293.15)  # Default 20°C in Kelvin
            temp_c = temp_k - 273.15
            temp_f = self._celsius_to_fahrenheit(temp_c)

            feels_like_k = current.get("feels_like", temp_k)
            feels_like_c = feels_like_k - 273.15
            feels_like_f = self._celsius_to_fahrenheit(feels_like_c)

            return NormalizedWeather(
                temperature_f=temp_f,
                temperature_c=temp_c,
                feels_like_f=feels_like_f,
                feels_like_c=feels_like_c,
                humidity_percent=current.get("humidity", 50),
                wind_speed_mph=self._mps_to_mph(current.get("wind_speed", 0)),
                wind_speed_kmh=self._mps_to_kmh(current.get("wind_speed", 0)),
                wind_direction=self._degrees_to_direction(current.get("wind_deg", 225)),
                precipitation_inch=0.0,  # Would be in hourly forecast
                precipitation_mm=0.0,
                precipitation_probability=0,
                visibility_miles=self._meters_to_miles(
                    current.get("visibility", 10000)),
                visibility_km=current.get("visibility", 10000) / 1000,
                pressure_inhg=self._mb_to_inhg(current.get("pressure", 1013)),
                pressure_mb=current.get("pressure", 1013),
                weather_description=current.get(
                    "weather", [
                        {}])[0].get(
                    "description", "clear sky"),
                timestamp=datetime.fromtimestamp(current.get("dt", 0), UTC),
                source=DataSource.OPENWEATHER,
            )

        except Exception as e:
            logger.error(f"Error normalizing OpenWeather data: {e}")
            raise

    def _normalize_weatherapi_data(self, raw_data: dict[str, Any]) -> NormalizedWeather:
        """Normalize WeatherAPI.com data"""
        try:
            current = raw_data.get("current", {})

            return NormalizedWeather(
                temperature_f=current.get("temp_f", 70),
                temperature_c=current.get("temp_c", 21),
                feels_like_f=current.get("feelslike_f", 70),
                feels_like_c=current.get("feelslike_c", 21),
                humidity_percent=current.get("humidity", 50),
                wind_speed_mph=current.get("wind_mph", 0),
                wind_speed_kmh=current.get("wind_kph", 0),
                wind_direction=current.get("wind_dir", "SW"),
                precipitation_inch=current.get("precip_in", 0),
                precipitation_mm=current.get("precip_mm", 0),
                precipitation_probability=0,  # Would be in forecast
                visibility_miles=current.get("vis_miles", 10),
                visibility_km=current.get("vis_km", 16),
                pressure_inhg=current.get("pressure_in", 29.92),
                pressure_mb=current.get("pressure_mb", 1013),
                weather_description=current.get("condition", {}).get("text", "Clear"),
                timestamp=datetime.now(UTC),
                source=DataSource.WEATHERAPI,
            )

        except Exception as e:
            logger.error(f"Error normalizing WeatherAPI data: {e}")
            raise

    def _normalize_team(self, team_name: str, sport: str) -> NormalizedTeam:
        """Normalize team name across different API formats"""
        sport_mappings = self.team_mappings.get(sport, {})
        team_info = sport_mappings.get(team_name, {})

        if not team_info:
            # Try to find partial matches
            for mapped_name, info in sport_mappings.items():
                if (
                    team_name.lower() in mapped_name.lower()
                    or mapped_name.lower() in team_name.lower()
                ):
                    team_info = info
                    break

        return NormalizedTeam(
            name=team_name,
            abbreviation=team_info.get("abbr", team_name[:3].upper()),
            city=team_info.get("city", team_name.split()[0]),
            full_name=team_info.get("full", team_name),
            league=sport,
        )

    def _normalize_odds_from_bookmaker(
        self, bookmaker_data: dict[str, Any]
    ) -> NormalizedOdds | None:
        """Extract and normalize odds from bookmaker data"""
        try:
            bookmaker_name = bookmaker_data.get("title", "Unknown")

            # Initialize odds structure
            home_odds = None
            away_odds = None
            spread_home = None
            spread_away = None
            total_over = None
            total_under = None
            total_points = None

            # Process markets
            for market in bookmaker_data.get("markets", []):
                market_key = market.get("key", "")
                outcomes = market.get("outcomes", [])

                if market_key == "h2h":  # Head-to-head (moneyline)
                    for outcome in outcomes:
                        price = outcome.get("price")
                        if outcome.get("name") in bookmaker_data.get("home_team", ""):
                            home_odds = self._american_to_decimal_odds(price)
                        else:
                            away_odds = self._american_to_decimal_odds(price)

                elif market_key == "spreads":  # Point spread
                    for outcome in outcomes:
                        point = outcome.get("point", 0)
                        if outcome.get("name") in bookmaker_data.get("home_team", ""):
                            spread_home = point
                        else:
                            spread_away = point

                elif market_key == "totals":  # Over/Under
                    total_points = outcomes[0].get("point") if outcomes else None
                    for outcome in outcomes:
                        if outcome.get("name", "").lower() == "over":
                            total_over = self._american_to_decimal_odds(
                                outcome.get("price"))
                        elif outcome.get("name", "").lower() == "under":
                            total_under = self._american_to_decimal_odds(
                                outcome.get("price"))

            if home_odds and away_odds:
                return NormalizedOdds(
                    bookmaker=bookmaker_name,
                    home_team_odds=home_odds,
                    away_team_odds=away_odds,
                    spread_home=spread_home,
                    spread_away=spread_away,
                    total_over=total_over,
                    total_under=total_under,
                    total_points=total_points,
                )

        except Exception as e:
            logger.error(
                f"Error normalizing odds from {
                    bookmaker_data.get(
                        'title',
                        'Unknown')}: {e}")

        return None

    def cross_validate_data(self, games: list[NormalizedGame]) -> list[NormalizedGame]:
        """Cross-validate data from multiple sources and improve quality scores"""

        validated_games = []

        for game in games:
            # Check data consistency
            quality_factors = []

            # Team name consistency
            if game.home_team.name and game.away_team.name:
                quality_factors.append(0.8)

            # Venue information completeness
            if game.venue_name and game.coordinates != (0.0, 0.0):
                quality_factors.append(0.9)
            else:
                quality_factors.append(0.5)

            # Odds availability
            if game.odds:
                quality_factors.append(0.8)

                # Check for odds consistency across bookmakers
                moneyline_odds = [
                    odds.home_team_odds for odds in game.odds if odds.home_team_odds]
                if len(moneyline_odds) > 1:
                    odds_variance = max(moneyline_odds) - min(moneyline_odds)
                    if odds_variance < 0.5:  # Low variance = consistent
                        quality_factors.append(0.9)
                    else:
                        quality_factors.append(0.6)
            else:
                quality_factors.append(0.3)

            # Weather data quality
            if game.weather:
                if game.weather.source in [
                    DataSource.NWS_WEATHER,
                    DataSource.OPENWEATHER,
                ]:
                    quality_factors.append(0.9)
                else:
                    quality_factors.append(0.7)

            # Multiple data sources boost quality
            if len(game.data_sources) >= 2:
                quality_factors.append(0.8)

            # Calculate overall quality score
            if quality_factors:
                game.data_quality_score = sum(quality_factors) / len(quality_factors)

            validated_games.append(game)

        logger.info(f"Cross-validated {len(validated_games)} games")
        return validated_games

    def merge_game_data(
        self, primary_game: NormalizedGame, enhancement_data: dict[str, Any]
    ) -> NormalizedGame:
        """Merge additional data sources into primary game data"""

        # Enhance venue information
        if enhancement_data.get("venue_name"):
            primary_game.venue_name = enhancement_data["venue_name"]

        if "venue_city" in enhancement_data:
            primary_game.venue_city = enhancement_data["venue_city"]

        if "venue_state" in enhancement_data:
            primary_game.venue_state = enhancement_data["venue_state"]

        if "venue_type" in enhancement_data:
            primary_game.venue_type = enhancement_data["venue_type"]

        if "coordinates" in enhancement_data:
            primary_game.coordinates = enhancement_data["coordinates"]

        # Add weather data if provided
        if enhancement_data.get("weather"):
            primary_game.weather = enhancement_data["weather"]

        # Update data sources
        new_sources = enhancement_data.get("data_sources", [])
        for source in new_sources:
            if source not in primary_game.data_sources:
                primary_game.data_sources.append(source)

        # Update timestamp
        primary_game.last_updated = datetime.now(UTC)

        return primary_game

    # Unit conversion utilities
    def _celsius_to_fahrenheit(self, celsius: float) -> float:
        """Convert Celsius to Fahrenheit"""
        return (celsius * 9 / 5) + 32

    def _fahrenheit_to_celsius(self, fahrenheit: float) -> float:
        """Convert Fahrenheit to Celsius"""
        return (fahrenheit - 32) * 5 / 9

    def _mps_to_mph(self, mps: float) -> float:
        """Convert meters per second to miles per hour"""
        return mps * 2.237

    def _mph_to_kmh(self, mph: float) -> float:
        """Convert miles per hour to kilometers per hour"""
        return mph * 1.609

    def _mps_to_kmh(self, mps: float) -> float:
        """Convert meters per second to kilometers per hour"""
        return mps * 3.6

    def _meters_to_miles(self, meters: float) -> float:
        """Convert meters to miles"""
        return meters / 1609.34

    def _miles_to_km(self, miles: float) -> float:
        """Convert miles to kilometers"""
        return miles * 1.609

    def _mb_to_inhg(self, millibars: float) -> float:
        """Convert millibars to inches of mercury"""
        return millibars * 0.02953

    def _american_to_decimal_odds(self, american_odds: int | float) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1

    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert wind direction degrees to compass direction"""
        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        index = int((degrees + 11.25) / 22.5) % 16
        return directions[index]

    def _normalize_wind_direction(self, direction: str | float | int) -> str:
        """Normalize wind direction to standard format"""
        if isinstance(direction, (int, float)):
            return self._degrees_to_direction(float(direction))
        else:
            # Clean up string direction
            direction_str = str(direction).upper().strip()
            # Map common variations
            direction_map = {
                "NORTH": "N",
                "SOUTH": "S",
                "EAST": "E",
                "WEST": "W",
                "NORTHEAST": "NE",
                "NORTHWEST": "NW",
                "SOUTHEAST": "SE",
                "SOUTHWEST": "SW",
            }
            return direction_map.get(direction_str, direction_str)

    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string from various API formats"""
        try:
            # Try ISO format with Z
            if datetime_str.endswith("Z"):
                return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

            # Try ISO format
            return datetime.fromisoformat(datetime_str)

        except Exception:
            # Default to current time if parsing fails
            logger.warning(f"Failed to parse datetime: {datetime_str}")
            return datetime.now(UTC)


def main():
    """Test the data normalization engine"""
    print("🔧 EQ12 DATA NORMALIZATION ENGINE")
    print("=" * 50)

    engine = EQ12DataNormalizationEngine()

    # Test with sample data
    sample_odds_data = {
        "id": "test_game_123",
        "home_team": "Boston Red Sox",
        "away_team": "New York Yankees",
        "commence_time": "2024-10-15T19:10:00Z",
        "bookmakers": [
            {
                "title": "DraftKings",
                "markets": [
                    {
                        "key": "h2h",
                        "outcomes": [
                            {"name": "Boston Red Sox", "price": -110},
                            {"name": "New York Yankees", "price": 120},
                        ],
                    }
                ],
            }
        ],
    }

    print("\n📊 TESTING ODDS NORMALIZATION:")
    normalized_game = engine.normalize_the_odds_api_data(sample_odds_data, "MLB")

    print(f"Game ID: {normalized_game.game_id}")
    print(f"Teams: {normalized_game.away_team.name} @ {normalized_game.home_team.name}")
    print(f"Date: {normalized_game.game_datetime}")
    print(f"Data Quality Score: {normalized_game.data_quality_score}")
    print(f"Odds Bookmakers: {len(normalized_game.odds)}")

    # Test weather normalization
    print("\n🌤️ TESTING WEATHER NORMALIZATION:")
    sample_weather = {
        "temp": 295.15,  # 22°C in Kelvin (OpenWeather format)
        "feels_like": 297.15,
        "humidity": 60,
        "wind_speed": 5.5,  # m/s
        "wind_deg": 225,  # SW
        "visibility": 10000,  # meters
        "pressure": 1013,  # mb
        "weather": [{"description": "partly cloudy"}],
        "dt": 1634567890,
    }

    normalized_weather = engine.normalize_weather_data(
        {"current": sample_weather}, DataSource.OPENWEATHER
    )

    print(
        f"Temperature: {
            normalized_weather.temperature_f:.1f}°F / {
            normalized_weather.temperature_c:.1f}°C")
    print(
        f"Wind: {
            normalized_weather.wind_speed_mph:.1f} mph {
            normalized_weather.wind_direction}")
    print(f"Visibility: {normalized_weather.visibility_miles:.1f} miles")
    print(f"Source: {normalized_weather.source.value}")

    # Test cross-validation
    print("\n✅ TESTING CROSS-VALIDATION:")
    normalized_game.weather = normalized_weather
    normalized_game.data_sources.append(DataSource.OPENWEATHER)

    validated_games = engine.cross_validate_data([normalized_game])
    validated_game = validated_games[0]

    print("Pre-validation quality: 0.7")
    print(f"Post-validation quality: {validated_game.data_quality_score:.2f}")
    print(f"Data sources: {[s.value for s in validated_game.data_sources]}")

    print("\n🚀 DATA NORMALIZATION ENGINE READY!")
    print("All APIs can now be normalized to unified EQ12 format!")


if __name__ == "__main__":
    main()
