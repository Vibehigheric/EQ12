#!/usr/bin/env python3
"""
EQ12 Weather-Enhanced Sports Betting Analysis System
Automatically applies weather analysis to EVERY outdoor MLB, NFL, and College Football game
Integrates with existing weather systems and multi-API sports data
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Import EQ12 existing systems
try:
    from eq12_dual_weather_strategy import EQ12DualWeatherStrategy
    from eq12_multi_sports_api_client import EQ12MultiSportsAPIClient, GameData
    from eq12_nws_weather_client import EQ12NWSWeatherClient
    from eq12_weather_client import EQ12WeatherClient
except ImportError as e:
    logging.warning(f"Some EQ12 modules not found: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WeatherEnhancedBetting:
    """Complete betting analysis with weather integration"""

    game_data: GameData
    weather_analysis: dict[str, Any]
    betting_recommendation: dict[str, Any]
    confidence_score: float
    weather_impact_score: float


class EQ12WeatherEnhancedBettingSystem:
    """
    Production system that automatically applies weather analysis
    to every outdoor MLB, NFL, and College Football game
    """

    def __init__(self):
        """Initialize with all EQ12 systems"""
        self.sports_client = EQ12MultiSportsAPIClient()

        # Initialize weather systems
        try:
            self.dual_weather = EQ12DualWeatherStrategy()
            self.nws_client = EQ12NWSWeatherClient()
            self.openweather_client = EQ12WeatherClient()
            self.weather_available = True
        except Exception as e:
            logger.warning(f"Weather systems not available: {e}")
            self.weather_available = False

        # Betting analysis configuration
        self.weather_impact_thresholds = {
            "MLB": {
                "wind_critical": 15,  # mph - affects home runs
                "temp_hot": 85,  # °F - favors offense
                "temp_cold": 45,  # °F - favors pitching
                "precipitation": 0.1,  # inches - game delay risk
                "humidity_high": 75,  # % - affects ball movement
            },
            "NFL": {
                "wind_critical": 20,  # mph - affects passing/kicking
                "temp_cold": 32,  # °F - affects ball handling
                "precipitation": 0.2,  # inches - affects field conditions
                "snow_accumulation": 1,  # inches - major game changer
                "visibility_low": 0.5,  # miles - affects passing
            },
            "NCAAF": {
                "wind_critical": 18,  # mph - similar to NFL
                "temp_cold": 35,  # °F - college players less adapted
                "precipitation": 0.15,  # inches - field condition critical
                "temperature_swing": 20,  # °F - adaptation challenges
            },
        }

        # Venue coordinates for weather analysis
        self.venue_coordinates = self._load_extended_venue_database()

    def _load_extended_venue_database(self) -> dict[str, dict[str, Any]]:
        """Extended venue database with precise coordinates for weather analysis"""
        return {
            # MLB Stadiums (Major League Baseball)
            "Fenway Park": {
                "lat": 42.3467,
                "lon": -71.0972,
                "city": "Boston",
                "type": "outdoor",
                "elevation": 20,
            },
            "Yankee Stadium": {
                "lat": 40.8296,
                "lon": -73.9262,
                "city": "New York",
                "type": "outdoor",
                "elevation": 55,
            },
            "Wrigley Field": {
                "lat": 41.9484,
                "lon": -87.6553,
                "city": "Chicago",
                "type": "outdoor",
                "elevation": 595,
            },
            "Coors Field": {
                "lat": 39.7559,
                "lon": -104.9942,
                "city": "Denver",
                "type": "outdoor",
                "elevation": 5200,
            },
            "Kauffman Stadium": {
                "lat": 39.0517,
                "lon": -94.4803,
                "city": "Kansas City",
                "type": "outdoor",
                "elevation": 750,
            },
            "Busch Stadium": {
                "lat": 38.6226,
                "lon": -90.1928,
                "city": "St. Louis",
                "type": "outdoor",
                "elevation": 465,
            },
            "Progressive Field": {
                "lat": 41.4962,
                "lon": -81.6852,
                "city": "Cleveland",
                "type": "outdoor",
                "elevation": 660,
            },
            "Comerica Park": {
                "lat": 42.3391,
                "lon": -83.0485,
                "city": "Detroit",
                "type": "outdoor",
                "elevation": 585,
            },
            "Target Field": {
                "lat": 44.9817,
                "lon": -93.2777,
                "city": "Minneapolis",
                "type": "outdoor",
                "elevation": 815,
            },
            "Guaranteed Rate Field": {
                "lat": 41.8300,
                "lon": -87.6338,
                "city": "Chicago",
                "type": "outdoor",
                "elevation": 595,
            },
            # NFL Stadiums (National Football League)
            "Lambeau Field": {
                "lat": 44.5013,
                "lon": -88.0622,
                "city": "Green Bay",
                "type": "outdoor",
                "elevation": 640,
            },
            "Soldier Field": {
                "lat": 41.8623,
                "lon": -87.6167,
                "city": "Chicago",
                "type": "outdoor",
                "elevation": 590,
            },
            "Arrowhead Stadium": {
                "lat": 39.0489,
                "lon": -94.4839,
                "city": "Kansas City",
                "type": "outdoor",
                "elevation": 909,
            },
            "Mile High Stadium": {
                "lat": 39.7439,
                "lon": -105.0200,
                "city": "Denver",
                "type": "outdoor",
                "elevation": 5280,
            },
            "Buffalo Bills Stadium": {
                "lat": 42.7738,
                "lon": -78.7870,
                "city": "Buffalo",
                "type": "outdoor",
                "elevation": 630,
            },
            "FirstEnergy Stadium": {
                "lat": 41.5061,
                "lon": -81.6995,
                "city": "Cleveland",
                "type": "outdoor",
                "elevation": 570,
            },
            "Heinz Field": {
                "lat": 40.4468,
                "lon": -80.0158,
                "city": "Pittsburgh",
                "type": "outdoor",
                "elevation": 710,
            },
            "M&T Bank Stadium": {
                "lat": 39.2780,
                "lon": -76.6227,
                "city": "Baltimore",
                "type": "outdoor",
                "elevation": 60,
            },
            "Lincoln Financial Field": {
                "lat": 39.9008,
                "lon": -75.1675,
                "city": "Philadelphia",
                "type": "outdoor",
                "elevation": 50,
            },
            "MetLife Stadium": {
                "lat": 40.8135,
                "lon": -74.0745,
                "city": "East Rutherford",
                "type": "outdoor",
                "elevation": 10,
            },
            # Major College Football Stadiums
            "Michigan Stadium": {
                "lat": 42.2658,
                "lon": -83.7486,
                "city": "Ann Arbor",
                "type": "outdoor",
                "elevation": 881,
            },
            "Ohio Stadium": {
                "lat": 40.0017,
                "lon": -83.0197,
                "city": "Columbus",
                "type": "outdoor",
                "elevation": 760,
            },
            "Beaver Stadium": {
                "lat": 40.8120,
                "lon": -77.8560,
                "city": "University Park",
                "type": "outdoor",
                "elevation": 1150,
            },
            "Tiger Stadium": {
                "lat": 30.4118,
                "lon": -91.1838,
                "city": "Baton Rouge",
                "type": "outdoor",
                "elevation": 55,
            },
            "Neyland Stadium": {
                "lat": 35.9550,
                "lon": -83.9253,
                "city": "Knoxville",
                "type": "outdoor",
                "elevation": 905,
            },
            "Camp Randall Stadium": {
                "lat": 43.0702,
                "lon": -89.4124,
                "city": "Madison",
                "type": "outdoor",
                "elevation": 869,
            },
            "Memorial Stadium": {
                "lat": 40.8202,
                "lon": -96.7056,
                "city": "Lincoln",
                "type": "outdoor",
                "elevation": 1170,
            },
            "Kyle Field": {
                "lat": 30.6103,
                "lon": -96.3401,
                "city": "College Station",
                "type": "outdoor",
                "elevation": 320,
            },
            # Indoor Stadiums (minimal weather impact)
            "Ford Field": {
                "lat": 42.3400,
                "lon": -83.0456,
                "city": "Detroit",
                "type": "indoor",
                "elevation": 585,
            },
            "U.S. Bank Stadium": {
                "lat": 44.9737,
                "lon": -93.2581,
                "city": "Minneapolis",
                "type": "indoor",
                "elevation": 815,
            },
            "Mercedes-Benz Superdome": {
                "lat": 29.9511,
                "lon": -90.0812,
                "city": "New Orleans",
                "type": "indoor",
                "elevation": 3,
            },
            "State Farm Stadium": {
                "lat": 33.5276,
                "lon": -112.2625,
                "city": "Glendale",
                "type": "retractable",
                "elevation": 1135,
            },
            # Retractable Roof (weather consideration varies)
            "Minute Maid Park": {
                "lat": 29.7571,
                "lon": -95.3555,
                "city": "Houston",
                "type": "retractable",
                "elevation": 22,
            },
            "Rogers Centre": {
                "lat": 43.6414,
                "lon": -79.3894,
                "city": "Toronto",
                "type": "retractable",
                "elevation": 300,
            },
            "T-Mobile Park": {
                "lat": 47.5914,
                "lon": -122.3326,
                "city": "Seattle",
                "type": "retractable",
                "elevation": 134,
            },
        }

    async def analyze_all_outdoor_games(
        self, sports: list[str] | None = None
    ) -> list[WeatherEnhancedBetting]:
        """
        Main function: Analyze ALL outdoor games with weather integration
        Focus: MLB, NFL, College Football
        """
        if sports is None:
            sports = ["MLB", "NFL", "NCAAF"]

        logger.info("🌦️ Starting comprehensive weather-enhanced betting analysis...")

        # Get all games from multi-API system
        all_games = self.sports_client.get_comprehensive_analysis(sports)

        # Filter for outdoor games requiring weather analysis
        outdoor_games = self.sports_client.get_weather_required_games(all_games)

        logger.info(f"Found {len(outdoor_games)} outdoor games requiring weather analysis")

        # Analyze each outdoor game with weather
        enhanced_analyses = []

        for game in outdoor_games:
            try:
                analysis = await self.analyze_game_with_weather(game)
                enhanced_analyses.append(analysis)
                logger.info(f"✅ Analyzed: {game.away_team} @ {game.home_team}")

            except Exception as e:
                logger.error(f"❌ Failed to analyze {game.away_team} @ {game.home_team}: {e}")
                continue

        logger.info(f"🎯 Completed weather analysis for {len(enhanced_analyses)} games")
        return enhanced_analyses

    async def analyze_game_with_weather(self, game: GameData) -> WeatherEnhancedBetting:
        """
        Analyze individual game with comprehensive weather integration
        """
        # Get venue coordinates
        venue_info = self.venue_coordinates.get(game.venue, {})

        if not venue_info:
            logger.warning(f"No coordinates found for venue: {game.venue}")
            # Use mock coordinates for testing
            venue_info = {
                "lat": 40.0,
                "lon": -80.0,
                "city": "Unknown",
                "type": "outdoor",
            }

        # Get weather analysis
        weather_analysis = {}
        if self.weather_available:
            try:
                # Use dual weather strategy for comprehensive analysis
                weather_data = await self.get_game_weather_analysis(
                    venue_info["lat"], venue_info["lon"], game.game_time
                )
                weather_analysis = weather_data

            except Exception as e:
                logger.warning(f"Weather analysis failed for {game.venue}: {e}")
                weather_analysis = self._get_mock_weather_data()
        else:
            weather_analysis = self._get_mock_weather_data()

        # Calculate weather impact score
        weather_impact_score = self.calculate_weather_impact(game.sport, weather_analysis)

        # Generate betting recommendation
        betting_recommendation = self.generate_betting_recommendation(
            game, weather_analysis, weather_impact_score
        )

        # Calculate overall confidence
        confidence_score = self.calculate_confidence_score(
            game, weather_analysis, weather_impact_score
        )

        return WeatherEnhancedBetting(
            game_data=game,
            weather_analysis=weather_analysis,
            betting_recommendation=betting_recommendation,
            confidence_score=confidence_score,
            weather_impact_score=weather_impact_score,
        )

    async def get_game_weather_analysis(
        self, lat: float, lon: float, game_time: datetime
    ) -> dict[str, Any]:
        """
        Get comprehensive weather analysis using EQ12 dual weather strategy
        """
        if not self.weather_available:
            return self._get_mock_weather_data()

        try:
            # Use dual weather strategy (NWS + OpenWeather)
            analysis = self.dual_weather.analyze_location_comprehensive(lat, lon)

            # Add specific game-time forecast

            # Extract relevant weather metrics
            current = analysis.get("current_conditions", {})
            forecast = analysis.get("forecast_data", {})

            return {
                "temperature": current.get("temperature", 70),
                "feels_like": current.get("feels_like", 70),
                "humidity": current.get("humidity", 50),
                "wind_speed": current.get("wind_speed", 5),
                "wind_direction": current.get("wind_direction", "SW"),
                "precipitation_probability": forecast.get("precipitation_prob", 0),
                "precipitation_amount": forecast.get("precipitation_amount", 0),
                "visibility": current.get("visibility", 10),
                "pressure": current.get("pressure", 30.0),
                "weather_description": current.get("description", "Clear"),
                "alerts": analysis.get("alerts", []),
                "air_quality": analysis.get("air_quality", {}),
                "source": "EQ12_Dual_Weather_Strategy",
            }

        except Exception as e:
            logger.error(f"Dual weather strategy failed: {e}")
            return self._get_mock_weather_data()

    def calculate_weather_impact(self, sport: str, weather_data: dict[str, Any]) -> float:
        """
        Calculate weather impact score (0-10) based on sport-specific thresholds
        """
        if sport not in self.weather_impact_thresholds:
            return 5.0  # Neutral impact

        thresholds = self.weather_impact_thresholds[sport]
        impact_score = 5.0  # Start neutral

        # Temperature impact
        temp = weather_data.get("temperature", 70)
        if sport == "MLB":
            if temp > thresholds["temp_hot"]:
                impact_score += min((temp - thresholds["temp_hot"]) / 10, 2.0)  # Offense boost
            elif temp < thresholds["temp_cold"]:
                impact_score -= min((thresholds["temp_cold"] - temp) / 10, 2.0)  # Pitching boost

        elif sport in ["NFL", "NCAAF"] and temp < thresholds["temp_cold"]:
            impact_score += min((thresholds["temp_cold"] - temp) / 10, 3.0)  # Cold weather impact

        # Wind impact
        wind_speed = weather_data.get("wind_speed", 0)
        if wind_speed > thresholds["wind_critical"]:
            impact_score += min((wind_speed - thresholds["wind_critical"]) / 5, 2.5)

        # Precipitation impact
        precip_prob = weather_data.get("precipitation_probability", 0)
        precip_amount = weather_data.get("precipitation_amount", 0)

        if precip_prob > 50 or precip_amount > thresholds.get("precipitation", 0.1):
            impact_score += min(precip_prob / 25, 2.0)

        # Cap the score between 0-10
        return max(0, min(10, impact_score))

    def generate_betting_recommendation(
        self, game: GameData, weather_data: dict[str, Any], weather_impact: float
    ) -> dict[str, Any]:
        """
        Generate specific betting recommendations based on weather analysis
        """
        recommendations = {
            "primary_bet": "",
            "reasoning": "",
            "confidence": "medium",
            "specific_bets": [],
            "avoid_bets": [],
            "weather_factor": weather_impact,
        }

        sport = game.sport
        temp = weather_data.get("temperature", 70)
        wind = weather_data.get("wind_speed", 5)
        precip_prob = weather_data.get("precipitation_probability", 0)

        if sport == "MLB":
            # Baseball-specific recommendations
            if wind > 15:
                if weather_data.get("wind_direction", "").startswith(
                    ("S", "SW")
                ):  # Wind blowing out
                    recommendations["primary_bet"] = "Over (Total Runs)"
                    recommendations["reasoning"] = (
                        f"Strong wind ({wind} mph) blowing out favors home runs"
                    )
                    recommendations["specific_bets"].append("Over team totals")
                    recommendations["specific_bets"].append("Home run props (if available)")
                else:  # Wind blowing in
                    recommendations["primary_bet"] = "Under (Total Runs)"
                    recommendations["reasoning"] = (
                        f"Wind ({wind} mph) blowing in suppresses offense"
                    )
                    recommendations["avoid_bets"].append("Over bets")

            elif temp > 85:
                recommendations["primary_bet"] = "Over (Total Runs)"
                recommendations["reasoning"] = (
                    f"Hot weather ({temp}°F) helps ball carry, favors hitters"
                )
                recommendations["specific_bets"].append("Over team totals")

            elif temp < 45:
                recommendations["primary_bet"] = "Under (Total Runs)"
                recommendations["reasoning"] = (
                    f"Cold weather ({temp}°F) favors pitching, ball doesn't carry"
                )
                recommendations["avoid_bets"].append("Home run props")

        elif sport in ["NFL", "NCAAF"]:
            # Football-specific recommendations
            if wind > 20:
                recommendations["primary_bet"] = "Under (Total Points)"
                recommendations["reasoning"] = (
                    f"Strong wind ({wind} mph) affects passing and kicking"
                )
                recommendations["specific_bets"].append("Under team totals")
                recommendations["avoid_bets"].append("Long field goal props")
                recommendations["avoid_bets"].append("High passing yards props")

            elif temp < 32 and precip_prob > 50:
                recommendations["primary_bet"] = "Under (Total Points)"
                recommendations["reasoning"] = (
                    f"Cold ({temp}°F) + precipitation risk = sloppy conditions"
                )
                recommendations["specific_bets"].append("More rushing attempts props")
                recommendations["avoid_bets"].append("High passing totals")

            elif temp < 20:
                recommendations["primary_bet"] = "Under (Total Points)"
                recommendations["reasoning"] = (
                    f"Extreme cold ({temp}°F) affects ball handling and kicking"
                )
                recommendations["specific_bets"].append("More turnovers props (if available)")

        # Set confidence based on weather impact strength
        if weather_impact >= 7:
            recommendations["confidence"] = "high"
        elif weather_impact <= 3:
            recommendations["confidence"] = "low"
        else:
            recommendations["confidence"] = "medium"

        return recommendations

    def calculate_confidence_score(
        self, game: GameData, weather_data: dict[str, Any], weather_impact: float
    ) -> float:
        """
        Calculate overall confidence score (0-1) for the analysis
        """
        confidence_factors = []

        # Weather data quality
        if weather_data.get("source") == "EQ12_Dual_Weather_Strategy":
            confidence_factors.append(0.9)  # High quality dual-source data
        else:
            confidence_factors.append(0.6)  # Mock or single-source data

        # Odds data availability
        if game.odds and game.odds.get("bookmakers"):
            confidence_factors.append(0.8)
        else:
            confidence_factors.append(0.4)

        # Venue data quality
        venue_info = self.venue_coordinates.get(game.venue, {})
        if venue_info and venue_info.get("type") == "outdoor":
            confidence_factors.append(0.9)  # Clear outdoor venue
        else:
            confidence_factors.append(0.5)  # Unknown venue type

        # Weather impact clarity
        if weather_impact >= 7 or weather_impact <= 3:
            confidence_factors.append(0.8)  # Clear impact direction
        else:
            confidence_factors.append(0.6)  # Moderate impact

        # Calculate weighted average
        return sum(confidence_factors) / len(confidence_factors)

    def _get_mock_weather_data(self) -> dict[str, Any]:
        """Mock weather data for testing"""
        return {
            "temperature": 72,
            "feels_like": 75,
            "humidity": 55,
            "wind_speed": 8,
            "wind_direction": "SW",
            "precipitation_probability": 10,
            "precipitation_amount": 0,
            "visibility": 10,
            "pressure": 30.1,
            "weather_description": "Partly Cloudy",
            "alerts": [],
            "air_quality": {"aqi": 50},
            "source": "mock_data",
        }

    def save_analysis_report(self, analyses: list[WeatherEnhancedBetting]) -> str:
        """Save comprehensive analysis report"""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_games_analyzed": len(analyses),
            "weather_impact_distribution": self._calculate_impact_distribution(analyses),
            "high_confidence_bets": [
                {
                    "game": f"{a.game_data.away_team} @ {a.game_data.home_team}",
                    "sport": a.game_data.sport,
                    "venue": a.game_data.venue,
                    "weather_impact": a.weather_impact_score,
                    "confidence": a.confidence_score,
                    "recommendation": a.betting_recommendation["primary_bet"],
                    "reasoning": a.betting_recommendation["reasoning"],
                }
                for a in analyses
                if a.confidence_score > 0.7
            ],
            "weather_alerts": [
                {
                    "game": f"{a.game_data.away_team} @ {a.game_data.home_team}",
                    "alerts": a.weather_analysis.get("alerts", []),
                }
                for a in analyses
                if a.weather_analysis.get("alerts")
            ],
        }

        # Save to logs directory
        report_file = f"C:\\\\EQ12\\logs\\weather_enhanced_betting_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, "w") as f:
                json.dump(report_data, f, indent=2, default=str)
            logger.info(f"📊 Analysis report saved: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return ""

    def _calculate_impact_distribution(
        self, analyses: list[WeatherEnhancedBetting]
    ) -> dict[str, int]:
        """Calculate distribution of weather impact scores"""
        distribution = {"low": 0, "medium": 0, "high": 0, "extreme": 0}

        for analysis in analyses:
            impact = analysis.weather_impact_score
            if impact <= 3:
                distribution["low"] += 1
            elif impact <= 6:
                distribution["medium"] += 1
            elif impact <= 8:
                distribution["high"] += 1
            else:
                distribution["extreme"] += 1

        return distribution


async def main():
    """Test the weather-enhanced betting system"""
    print("🌦️⚾🏈 EQ12 WEATHER-ENHANCED BETTING ANALYSIS SYSTEM")
    print("=" * 70)
    print("Automatic weather analysis for EVERY outdoor MLB, NFL, and College Football game")

    # Initialize system
    system = EQ12WeatherEnhancedBettingSystem()

    print("\n🎯 ANALYZING ALL OUTDOOR GAMES...")
    print("Sports: MLB, NFL, College Football")
    print("Weather Sources: NWS (FREE) + OpenWeather (Enhanced)")

    # Run comprehensive analysis
    analyses = await system.analyze_all_outdoor_games(["MLB", "NFL", "NCAAF"])

    # Display results
    print("\n📊 ANALYSIS COMPLETE!")
    print(f"Total games analyzed: {len(analyses)}")

    # Show weather impact distribution
    impact_dist = system._calculate_impact_distribution(analyses)
    print("\n🌤️ WEATHER IMPACT DISTRIBUTION:")
    print(f"   Low Impact (0-3):    {impact_dist['low']} games")
    print(f"   Medium Impact (3-6): {impact_dist['medium']} games")
    print(f"   High Impact (6-8):   {impact_dist['high']} games")
    print(f"   Extreme Impact (8+): {impact_dist['extreme']} games")

    # Show high-confidence recommendations
    high_confidence = [a for a in analyses if a.confidence_score > 0.7]
    print(f"\n🎯 HIGH-CONFIDENCE BETTING OPPORTUNITIES: {len(high_confidence)}")

    for i, analysis in enumerate(high_confidence[:5], 1):  # Show top 5
        game = analysis.game_data
        weather = analysis.weather_analysis
        bet_rec = analysis.betting_recommendation

        print(f"\n{i}. {game.away_team} @ {game.home_team} ({game.sport})")
        print(f"   Venue: {game.venue}")
        print(f"   Weather Impact: {analysis.weather_impact_score:.1f}/10")
        print(f"   Confidence: {analysis.confidence_score:.1f}")
        print(f"   Temperature: {weather.get('temperature', 'N/A')}°F")
        print(f"   Wind: {weather.get('wind_speed', 'N/A')} mph")
        print(f"   💰 Recommendation: {bet_rec['primary_bet']}")
        print(f"   📝 Reasoning: {bet_rec['reasoning']}")

    # Show weather alerts
    weather_alerts = [a for a in analyses if a.weather_analysis.get("alerts")]
    if weather_alerts:
        print(f"\n⚠️ WEATHER ALERTS: {len(weather_alerts)} games")
        for alert_analysis in weather_alerts[:3]:
            game = alert_analysis.game_data
            alerts = alert_analysis.weather_analysis["alerts"]
            print(f"   {game.away_team} @ {game.home_team}: {len(alerts)} active alerts")

    # Save comprehensive report
    report_file = system.save_analysis_report(analyses)
    if report_file:
        print(f"\n📁 Detailed report saved: {report_file}")

    print("\n🚀 WEATHER-ENHANCED BETTING SYSTEM OPERATIONAL!")
    print("Every outdoor game now includes comprehensive weather analysis!")


if __name__ == "__main__":
    asyncio.run(main())
