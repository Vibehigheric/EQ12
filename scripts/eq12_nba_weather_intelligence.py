#!/usr/bin/env python3
"""
EQ12 NBA Weather Intelligence Integration
Combines NBA team/venue intelligence with weather data for enhanced betting analysis
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from typing import Any

import requests

# Configure enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "C:/EQ12/logs/nba_weather_intelligence.log",
            encoding="utf-8"),
        logging.StreamHandler(
            sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EQ12NBAWeatherIntelligence:
    """
    EQ12 NBA Weather Intelligence System
    Combines NBA venue intelligence with weather data for enhanced betting analysis
    """

    def __init__(self, api_key: str | None = None):
        """Initialize NBA Weather Intelligence System"""
        self.api_key = api_key or os.getenv(
            "NBA_API_KEY", "8716c77c5ce79d828b73eccc10819a10")

        # NBA Arena Database with precise coordinates and characteristics
        self.nba_arenas = {
            "Atlanta Hawks": {
                "arena": "State Farm Arena",
                "city": "Atlanta",
                "state": "GA",
                "coordinates": {"lat": 33.7573, "lon": -84.3963},
                "capacity": 20000,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Boston Celtics": {
                "arena": "TD Garden",
                "city": "Boston",
                "state": "MA",
                "coordinates": {"lat": 42.3662, "lon": -71.0621},
                "capacity": 19156,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Brooklyn Nets": {
                "arena": "Barclays Center",
                "city": "Brooklyn",
                "state": "NY",
                "coordinates": {"lat": 40.6826, "lon": -73.9754},
                "capacity": 17732,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Charlotte Hornets": {
                "arena": "Spectrum Center",
                "city": "Charlotte",
                "state": "NC",
                "coordinates": {"lat": 35.2251, "lon": -80.8392},
                "capacity": 19077,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Chicago Bulls": {
                "arena": "United Center",
                "city": "Chicago",
                "state": "IL",
                "coordinates": {"lat": 41.8807, "lon": -87.6742},
                "capacity": 20917,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "travel",
            },
            "Cleveland Cavaliers": {
                "arena": "Rocket Mortgage FieldHouse",
                "city": "Cleveland",
                "state": "OH",
                "coordinates": {"lat": 41.4965, "lon": -81.6882},
                "capacity": 19432,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "travel",
            },
            "Dallas Mavericks": {
                "arena": "American Airlines Center",
                "city": "Dallas",
                "state": "TX",
                "coordinates": {"lat": 32.7905, "lon": -96.8103},
                "capacity": 19200,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Denver Nuggets": {
                "arena": "Ball Arena",
                "city": "Denver",
                "state": "CO",
                "coordinates": {"lat": 39.7487, "lon": -105.0077},
                "capacity": 19520,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "altitude_weather",
            },
            "Detroit Pistons": {
                "arena": "Little Caesars Arena",
                "city": "Detroit",
                "state": "MI",
                "coordinates": {"lat": 42.3411, "lon": -83.0553},
                "capacity": 20332,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "travel",
            },
            "Golden State Warriors": {
                "arena": "Chase Center",
                "city": "San Francisco",
                "state": "CA",
                "coordinates": {"lat": 37.7680, "lon": -122.3897},
                "capacity": 18064,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "fog_wind",
            },
            "Houston Rockets": {
                "arena": "Toyota Center",
                "city": "Houston",
                "state": "TX",
                "coordinates": {"lat": 29.6808, "lon": -95.3621},
                "capacity": 18055,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "humidity",
            },
            "Indiana Pacers": {
                "arena": "Gainbridge Fieldhouse",
                "city": "Indianapolis",
                "state": "IN",
                "coordinates": {"lat": 39.7640, "lon": -86.1555},
                "capacity": 17923,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "LA Clippers": {
                "arena": "Crypto.com Arena",  # Shared with Lakers
                "city": "Los Angeles",
                "state": "CA",
                "coordinates": {"lat": 34.0430, "lon": -118.2673},
                "capacity": 19068,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Los Angeles Lakers": {
                "arena": "Crypto.com Arena",
                "city": "Los Angeles",
                "state": "CA",
                "coordinates": {"lat": 34.0430, "lon": -118.2673},
                "capacity": 19068,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Memphis Grizzlies": {
                "arena": "FedExForum",
                "city": "Memphis",
                "state": "TN",
                "coordinates": {"lat": 35.1382, "lon": -90.0505},
                "capacity": 17794,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Miami Heat": {
                "arena": "Kaseya Center",
                "city": "Miami",
                "state": "FL",
                "coordinates": {"lat": 25.7814, "lon": -80.1870},
                "capacity": 19600,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "hurricane_season",
            },
            "Milwaukee Bucks": {
                "arena": "Fiserv Forum",
                "city": "Milwaukee",
                "state": "WI",
                "coordinates": {"lat": 43.0448, "lon": -87.9073},
                "capacity": 17500,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "severe_weather",
            },
            "Minnesota Timberwolves": {
                "arena": "Target Center",
                "city": "Minneapolis",
                "state": "MN",
                "coordinates": {"lat": 44.9795, "lon": -93.2760},
                "capacity": 19356,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "blizzard_risk",
            },
            "New Orleans Pelicans": {
                "arena": "Smoothie King Center",
                "city": "New Orleans",
                "state": "LA",
                "coordinates": {"lat": 29.9490, "lon": -90.0821},
                "capacity": 16867,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "hurricane_season",
            },
            "New York Knicks": {
                "arena": "Madison Square Garden",
                "city": "New York",
                "state": "NY",
                "coordinates": {"lat": 40.7505, "lon": -73.9934},
                "capacity": 20789,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "blizzard_risk",
            },
            "Oklahoma City Thunder": {
                "arena": "Paycom Center",
                "city": "Oklahoma City",
                "state": "OK",
                "coordinates": {"lat": 35.4634, "lon": -97.5151},
                "capacity": 18203,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "tornado_season",
            },
            "Orlando Magic": {
                "arena": "Amway Center",
                "city": "Orlando",
                "state": "FL",
                "coordinates": {"lat": 28.5392, "lon": -81.3839},
                "capacity": 18846,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "hurricane_season",
            },
            "Philadelphia 76ers": {
                "arena": "Wells Fargo Center",
                "city": "Philadelphia",
                "state": "PA",
                "coordinates": {"lat": 39.9012, "lon": -75.1720},
                "capacity": 20478,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "snow_ice",
            },
            "Phoenix Suns": {
                "arena": "Footprint Center",
                "city": "Phoenix",
                "state": "AZ",
                "coordinates": {"lat": 33.4457, "lon": -112.0712},
                "capacity": 18055,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "dust_storms",
            },
            "Portland Trail Blazers": {
                "arena": "Moda Center",
                "city": "Portland",
                "state": "OR",
                "coordinates": {"lat": 45.5316, "lon": -122.6668},
                "capacity": 19393,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "rain_wind",
            },
            "Sacramento Kings": {
                "arena": "Golden 1 Center",
                "city": "Sacramento",
                "state": "CA",
                "coordinates": {"lat": 38.5816, "lon": -121.4999},
                "capacity": 17608,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "San Antonio Spurs": {
                "arena": "Frost Bank Center",
                "city": "San Antonio",
                "state": "TX",
                "coordinates": {"lat": 29.4270, "lon": -98.4375},
                "capacity": 18418,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "minimal",
            },
            "Toronto Raptors": {
                "arena": "Scotiabank Arena",
                "city": "Toronto",
                "state": "ON",
                "coordinates": {"lat": 43.6434, "lon": -79.3791},
                "capacity": 19800,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "blizzard_risk",
            },
            "Utah Jazz": {
                "arena": "Delta Center",
                "city": "Salt Lake City",
                "state": "UT",
                "coordinates": {"lat": 40.7683, "lon": -111.9011},
                "capacity": 18306,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "altitude_snow",
            },
            "Washington Wizards": {
                "arena": "Capital One Arena",
                "city": "Washington",
                "state": "DC",
                "coordinates": {"lat": 38.8982, "lon": -77.0209},
                "capacity": 20356,
                "roo": "enclosed",
                "climate_controlled": True,
                "weather_impact": "snow_ice",
            },
        }

        # Weather impact categories for NBA betting intelligence
        self.weather_impact_analysis = {
            "minimal": {
                "factor": 1.0,
                "description": "Weather has negligible impact on game",
            },
            "travel": {
                "factor": 1.1,
                "description": "Weather may impact team travel to venue",
            },
            "altitude_weather": {
                "factor": 1.15,
                "description": "High altitude + weather affects visiting teams",
            },
            "fog_wind": {
                "factor": 1.05,
                "description": "Bay area weather may impact fan attendance",
            },
            "humidity": {
                "factor": 1.05,
                "description": "High humidity may affect player performance",
            },
            "hurricane_season": {
                "factor": 1.2,
                "description": "Hurricane season may impact games/travel",
            },
            "severe_weather": {
                "factor": 1.15,
                "description": "Severe weather may impact attendance/travel",
            },
            "blizzard_risk": {
                "factor": 1.2,
                "description": "Blizzard risk may significantly impact games",
            },
            "tornado_season": {
                "factor": 1.1,
                "description": "Tornado season may impact scheduling",
            },
            "snow_ice": {
                "factor": 1.15,
                "description": "Snow/ice may impact travel and attendance",
            },
            "dust_storms": {
                "factor": 1.05,
                "description": "Dust storms may impact visibility/travel",
            },
            "rain_wind": {
                "factor": 1.05,
                "description": "Rain/wind may impact fan attendance",
            },
            "altitude_snow": {
                "factor": 1.2,
                "description": "High altitude + snow affects visiting teams",
            },
        }

        self.session = requests.Session()
        logger.info("NBA Weather Intelligence System initialized")
        logger.info(
            f"Database loaded: {len(self.nba_arenas)} NBA arenas with weather intelligence")

    def get_arena_weather_forecast(self, team_name: str) -> dict[str, Any]:
        """Get weather forecast for NBA team's home arena"""
        if team_name not in self.nba_arenas:
            logger.warning(f"Team not found in database: {team_name}")
            return {"success": False, "error": "Team not found"}

        arena_data = self.nba_arenas[team_name]
        coordinates = arena_data["coordinates"]

        try:
            # Use National Weather Service API for US locations
            if arena_data["state"] != "ON":  # Not Toronto
                # Get NWS point data
                nws_url = (
                    f"https://api.weather.gov/points/{coordinates['lat']},{coordinates['lon']}"
                )
                response = self.session.get(nws_url, timeout=10)

                if response.status_code == 200:
                    point_data = response.json()
                    forecast_url = point_data["properties"]["forecast"]

                    # Get detailed forecast
                    forecast_response = self.session.get(forecast_url, timeout=10)
                    if forecast_response.status_code == 200:
                        forecast_data = forecast_response.json()

                        # Extract relevant periods (next 3 days)
                        periods = forecast_data["properties"]["periods"][:6]

                        weather_analysis = {"success": True,
                                            "team": team_name,
                                            "arena": arena_data["arena"],
                                            "location": f"{arena_data['city']}, {arena_data['state']}",
                                            "coordinates": coordinates,
                                            "forecast_periods": periods,
                                            "weather_impact": arena_data["weather_impact"],
                                            "impact_analysis": self.weather_impact_analysis[arena_data["weather_impact"]],
                                            "betting_intelligence": self._analyze_weather_betting_impact(periods,
                                                                                                         arena_data),
                                            }

                        logger.info(
                            f"Weather forecast retrieved for {team_name} at {
                                arena_data['arena']}")
                        return weather_analysis

            else:
                # For Toronto, use a different approach or mock data
                logger.info(
                    f"International venue {team_name} - using weather intelligence database")
                return {
                    "success": True,
                    "team": team_name,
                    "arena": arena_data["arena"],
                    "location": f"{arena_data['city']}, {arena_data['state']}",
                    "coordinates": coordinates,
                    "weather_impact": arena_data["weather_impact"],
                    "impact_analysis": self.weather_impact_analysis[arena_data["weather_impact"]],
                    "international_venue": True,
                }

        except Exception as e:
            logger.error(f"Weather forecast error for {team_name}: {e}")

        return {"success": False, "error": "Weather data unavailable"}

    def _analyze_weather_betting_impact(
        self, forecast_periods: list[dict], arena_data: dict
    ) -> dict[str, Any]:
        """Analyze weather forecast for betting intelligence"""
        betting_analysis = {
            "risk_level": "LOW",
            "confidence_factor": 1.0,
            "key_factors": [],
            "recommendations": [],
        }

        try:
            # Analyze next 24-48 hours for immediate impact
            for period in forecast_periods[:4]:
                detailed_forecast = period.get("detailedForecast", "").lower()

                # Check for severe weather indicators
                severe_indicators = [
                    "storm",
                    "blizzard",
                    "hurricane",
                    "tornado",
                    "severe",
                    "warning",
                    "advisory",
                ]
                for indicator in severe_indicators:
                    if indicator in detailed_forecast:
                        betting_analysis["risk_level"] = "HIGH"
                        betting_analysis["confidence_factor"] = 1.3
                        betting_analysis["key_factors"].append(
                            f"Severe weather: {indicator}")

                # Check for travel-impacting weather
                travel_indicators = ["snow", "ice", "freezing", "heavy rain", "wind"]
                for indicator in travel_indicators:
                    if indicator in detailed_forecast:
                        if betting_analysis["risk_level"] == "LOW":
                            betting_analysis["risk_level"] = "MEDIUM"
                            betting_analysis["confidence_factor"] = 1.15
                        betting_analysis["key_factors"].append(
                            f"Travel impact: {indicator}")

            # Generate betting recommendations
            if betting_analysis["risk_level"] == "HIGH":
                betting_analysis["recommendations"].append(
                    "High weather risk - consider postponement odds"
                )
                betting_analysis["recommendations"].append(
                    "Monitor team travel reports closely")

            elif betting_analysis["risk_level"] == "MEDIUM":
                betting_analysis["recommendations"].append(
                    "Weather may impact attendance - consider under bets"
                )
                betting_analysis["recommendations"].append(
                    "Visiting team may face travel challenges"
                )

            else:
                betting_analysis["recommendations"].append(
                    "Weather impact minimal - standard betting approach"
                )

        except Exception as e:
            logger.warning(f"Weather betting analysis error: {e}")

        return betting_analysis

    def analyze_matchup_weather_intelligence(
        self, home_team: str, away_team: str
    ) -> dict[str, Any]:
        """Analyze weather intelligence for a specific NBA matchup"""
        logger.info(f"Analyzing weather intelligence: {away_team} @ {home_team}")

        # Get home team arena weather
        home_weather = self.get_arena_weather_forecast(home_team)

        # Get away team home conditions (for comparison)
        away_home_weather = self.get_arena_weather_forecast(away_team)

        matchup_analysis = {
            "matchup": f"{away_team} @ {home_team}",
            "home_weather": home_weather,
            "away_team_conditions": away_home_weather,
            "comparative_analysis": None,
            "betting_edge": None,
        }

        if home_weather.get("success") and away_home_weather.get("success"):
            # Compare climate conditions
            home_impact = home_weather.get("impact_analysis", {}).get("factor", 1.0)
            away_impact = away_home_weather.get(
                "impact_analysis", {}).get(
                "factor", 1.0)

            comparative_analysis = {
                "home_advantage_factor": home_impact,
                "visitor_adaptation_factor": away_impact,
                "weather_differential": home_impact - away_impact,
                "analysis": self._generate_comparative_weather_analysis(
                    home_weather, away_home_weather
                ),
            }

            matchup_analysis["comparative_analysis"] = comparative_analysis

            # Generate betting edge analysis
            betting_edge = {
                "recommended_side": "HOME" if home_impact < away_impact else "AWAY",
                "edge_strength": abs(
                    home_impact -
                    away_impact),
                "confidence": (
                    "HIGH" if abs(
                        home_impact -
                        away_impact) > 0.1 else "MEDIUM"),
            }

            matchup_analysis["betting_edge"] = betting_edge

        return matchup_analysis

    def _generate_comparative_weather_analysis(
            self, home_weather: dict, away_weather: dict) -> str:
        """Generate comparative weather analysis text"""
        home_impact = home_weather.get("weather_impact", "minimal")
        away_impact = away_weather.get("weather_impact", "minimal")

        home_arena = home_weather.get("arena", "Unknown Arena")
        away_arena = away_weather.get("arena", "Unknown Arena")

        if home_impact == away_impact:
            return f"Similar weather conditions at both {home_arena} and {away_arena} - minimal differential impact"

        home_factor = self.weather_impact_analysis[home_impact]["factor"]
        away_factor = self.weather_impact_analysis[away_impact]["factor"]

        if home_factor > away_factor:
            return f"Home venue has higher weather impact factor ({home_factor} vs {away_factor}) - visiting team may have advantage"
        else:
            return "Visiting team faces greater weather adaptation challenge - home team advantage likely"

    def generate_daily_nba_weather_report(self) -> dict[str, Any]:
        """Generate comprehensive daily NBA weather intelligence report"""
        logger.info("Generating daily NBA weather intelligence report...")

        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now(UTC).isoformat(),
            "total_teams": len(self.nba_arenas),
            "weather_alerts": [],
            "high_impact_venues": [],
            "betting_opportunities": [],
            "system_status": "operational",
        }

        # Analyze all NBA venues for weather impacts
        high_impact_count = 0
        weather_alerts = 0

        for team_name, arena_data in self.nba_arenas.items():
            try:
                weather_forecast = self.get_arena_weather_forecast(team_name)

                if weather_forecast.get("success"):
                    impact_factor = self.weather_impact_analysis[arena_data["weather_impact"]][
                        "factor"
                    ]

                    # Check for high-impact weather
                    if impact_factor > 1.1:
                        high_impact_count += 1
                        report["high_impact_venues"].append(
                            {
                                "team": team_name,
                                "arena": arena_data["arena"],
                                "impact_factor": impact_factor,
                                "weather_type": arena_data["weather_impact"],
                            }
                        )

                    # Check for weather betting opportunities
                    if weather_forecast.get("betting_intelligence"):
                        betting_intel = weather_forecast["betting_intelligence"]
                        if betting_intel["risk_level"] in ["MEDIUM", "HIGH"]:
                            report["betting_opportunities"].append(
                                {
                                    "team": team_name,
                                    "risk_level": betting_intel["risk_level"],
                                    "confidence_factor": betting_intel["confidence_factor"],
                                    "recommendations": betting_intel["recommendations"],
                                })

                    # Check for weather alerts
                    if weather_forecast.get("forecast_periods"):
                        for period in weather_forecast["forecast_periods"][:2]:
                            detailed_forecast = period.get(
                                "detailedForecast", "").lower()
                            if any(
                                word in detailed_forecast
                                for word in ["storm", "severe", "warning", "advisory"]
                            ):
                                weather_alerts += 1
                                report["weather_alerts"].append(
                                    {
                                        "team": team_name,
                                        "arena": arena_data["arena"],
                                        "alert": period.get("name", "Unknown"),
                                        "forecast": detailed_forecast,
                                    }
                                )
                                break

            except Exception as e:
                logger.warning(f"Error analyzing {team_name}: {e}")
                continue

            # Rate limiting
            time.sleep(0.1)

        report["high_impact_count"] = high_impact_count
        report["weather_alerts_count"] = weather_alerts
        report["betting_opportunities_count"] = len(report["betting_opportunities"])

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"C:/EQ12/logs/nba_weather_intelligence_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Daily NBA weather intelligence report saved: {report_file}")
        return report


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 NBA Weather Intelligence System")
    parser.add_argument("--api-key", help="NBA API key (stored for future use)")
    parser.add_argument(
        "--team-weather",
        help="Get weather forecast for specific NBA team")
    parser.add_argument(
        "--matchup",
        nargs=2,
        metavar=("AWAY", "HOME"),
        help="Analyze matchup weather intelligence",
    )
    parser.add_argument(
        "--daily-report",
        action="store_true",
        help="Generate daily weather intelligence report",
    )
    parser.add_argument(
        "--list-teams",
        action="store_true",
        help="List all NBA teams in database")
    parser.add_argument(
        "--weather-alerts",
        action="store_true",
        help="Check for weather alerts across NBA venues",
    )

    args = parser.parse_args()

    # Initialize NBA Weather Intelligence
    nba_weather = EQ12NBAWeatherIntelligence(api_key=args.api_key)

    print("EQ12 NBA WEATHER INTELLIGENCE SYSTEM")
    print("=" * 80)

    if args.team_weather:
        print(f"Getting weather forecast for {args.team_weather}...")
        result = nba_weather.get_arena_weather_forecast(args.team_weather)

        if result["success"]:
            print(f"Weather Intelligence for {result['team']}:")
            print(f"   Arena: {result['arena']}")
            print(f"   Location: {result['location']}")
            print(f"   Weather Impact: {result['weather_impact'].upper()}")

            impact = result["impact_analysis"]
            print(f"   Impact Factor: {impact['factor']}")
            print(f"   Analysis: {impact['description']}")

            if result.get("betting_intelligence"):
                betting = result["betting_intelligence"]
                print(f"   Betting Risk: {betting['risk_level']}")
                print(f"   Confidence Factor: {betting['confidence_factor']}")
                for rec in betting["recommendations"]:
                    print(f"   Recommendation: {rec}")
        else:
            print(f"Error: {result['error']}")

    elif args.matchup:
        away_team, home_team = args.matchup
        print(f"Analyzing matchup weather intelligence: {away_team} @ {home_team}...")

        result = nba_weather.analyze_matchup_weather_intelligence(home_team, away_team)
        print(f"Matchup Analysis: {result['matchup']}")

        if result.get("comparative_analysis"):
            comp = result["comparative_analysis"]
            print(f"   Weather Differential: {comp['weather_differential']:.3f}")
            print(f"   Analysis: {comp['analysis']}")

        if result.get("betting_edge"):
            edge = result["betting_edge"]
            print(f"   Recommended Side: {edge['recommended_side']}")
            print(f"   Edge Strength: {edge['edge_strength']:.3f}")
            print(f"   Confidence: {edge['confidence']}")

    elif args.daily_report:
        print("Generating daily NBA weather intelligence report...")
        result = nba_weather.generate_daily_nba_weather_report()

        print("Daily NBA Weather Intelligence Report:")
        print(f"   Date: {result['date']}")
        print(f"   Total Teams Analyzed: {result['total_teams']}")
        print(f"   High-Impact Venues: {result['high_impact_count']}")
        print(f"   Weather Alerts: {result['weather_alerts_count']}")
        print(f"   Betting Opportunities: {result['betting_opportunities_count']}")

        if result["weather_alerts"]:
            print("\n   Active Weather Alerts:")
            for alert in result["weather_alerts"][:5]:
                print(f"      {alert['team']}: {alert['alert']}")

    elif args.list_teams:
        print("NBA Teams in Weather Intelligence Database:")
        for team_name, arena_data in nba_weather.nba_arenas.items():
            impact_factor = nba_weather.weather_impact_analysis[arena_data["weather_impact"]][
                "factor"
            ]
            print(
                f"   {
                    team_name:25} | {
                    arena_data['arena']:25} | Impact: {impact_factor}")

    elif args.weather_alerts:
        print("Checking weather alerts across NBA venues...")
        # Quick check for high-impact weather conditions
        alert_count = 0
        for team_name in list(nba_weather.nba_arenas.keys())[:10]:  # Sample 10 teams
            result = nba_weather.get_arena_weather_forecast(team_name)
            if result.get("success") and result.get("betting_intelligence"):
                if result["betting_intelligence"]["risk_level"] != "LOW":
                    alert_count += 1
                    print(
                        f"   {team_name}: {
                            result['betting_intelligence']['risk_level']} weather risk")

        if alert_count == 0:
            print("   No significant weather alerts detected")

    else:
        # Default: run daily report
        print("Running default NBA weather intelligence analysis...")
        result = nba_weather.generate_daily_nba_weather_report()

        print("\nNBA Weather Intelligence Summary:")
        print(f"   System Status: {result['system_status'].upper()}")
        print(f"   Teams Monitored: {result['total_teams']}")
        print(f"   High-Impact Venues: {result['high_impact_count']}")
        print(f"   Active Weather Alerts: {result['weather_alerts_count']}")
        print(f"   Betting Opportunities: {result['betting_opportunities_count']}")

        if result["betting_opportunities"]:
            print("\n   Top Betting Opportunities:")
            for opp in result["betting_opportunities"][:3]:
                print(
                    f"      {
                        opp['team']}: {
                        opp['risk_level']} risk (factor: {
                        opp['confidence_factor']})")

    print("\n✅ EQ12 NBA Weather Intelligence Complete!")


if __name__ == "__main__":
    main()
