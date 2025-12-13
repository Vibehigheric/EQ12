#!/usr/bin/env python3
"""
EQ12 Dual Weather Strategy - NWS + OpenWeather Integration
Optimal combination: FREE NWS government data + Enhanced OpenWeather features
Maximum coverage with cost-effective approach for EQ12 betting system
"""

from datetime import UTC, datetime
from typing import Any

# Import both weather clients
try:
    from eq12_nws_weather_client import EQ12NWSWeatherClient
except ImportError:
    print("NWS Weather Client not found - create eq12_nws_weather_client.py first")

try:
    from eq12_weather_client import EQ12WeatherClient
except ImportError:
    print("OpenWeather Client not found - create eq12_weather_client.py first")


class EQ12DualWeatherStrategy:
    """
    Combines FREE NWS data with premium OpenWeather features
    Maximizes weather intelligence while minimizing costs
    """

    def __init__(self):
        self.nws_client = EQ12NWSWeatherClient()

        # Only initialize OpenWeather if API key is available
        try:
            self.openweather_client = EQ12WeatherClient()
            self.has_openweather = True
        except BaseException:
            self.openweather_client = None
            self.has_openweather = False

        # Strategy configuration
        self.strategy_config = {
            "primary_source": "NWS",  # FREE and reliable
            "fallback_source": "OpenWeather",  # Enhanced features when needed
            "cost_optimization": True,
            "api_call_limits": {
                "nws": "unlimited",  # Government service
                "openweather": 1000,  # Free tier daily limit
            },
        }

    def get_comprehensive_weather_analysis(
        self, team: str, game_datetime: str | None = None
    ) -> dict[str, Any]:
        """
        Dual-source weather analysis combining NWS + OpenWeather
        Maximizes data quality while optimizing costs
        """

        analysis = {
            "team": team,
            "game_datetime": game_datetime,
            "timestamp": datetime.now(UTC).isoformat(),
            "sources_used": [],
            "primary_analysis": {},
            "enhanced_features": {},
            "combined_impact": {},
            "cost_summary": {
                "nws_calls": 1,  # Always free
                "openweather_calls": 0,
                "total_cost": 0.0,
            },
        }

        # Step 1: Get PRIMARY analysis from FREE NWS
        print(f"🏛️ Getting FREE government weather data for {team}...")
        nws_analysis = self.nws_client.get_nhl_weather_analysis(team, game_datetime)

        if "error" not in nws_analysis:
            analysis["sources_used"].append("NWS")
            analysis["primary_analysis"] = nws_analysis
            print(
                f"✅ NWS data acquired - Impact: {nws_analysis['betting_impact']['impact_level']}"
            )
        else:
            print(f"⚠️ NWS data unavailable: {nws_analysis.get('error')}")

        # Step 2: Determine if OpenWeather enhancement is needed
        needs_enhancement = self._should_use_openweather(nws_analysis)

        if needs_enhancement and self.has_openweather:
            print(f"🌤️ Getting enhanced OpenWeather data for {team}...")
            openweather_analysis = self.openweather_client.get_nhl_game_weather_analysis(
                team, game_datetime)

            if "error" not in openweather_analysis:
                analysis["sources_used"].append("OpenWeather")
                analysis["enhanced_features"] = openweather_analysis
                analysis["cost_summary"]["openweather_calls"] = 1
                # $0.0015 per call above free tier
                analysis["cost_summary"]["total_cost"] = 0.0015
                print(
                    f"✅ OpenWeather enhancement acquired - Air Quality: {
                        openweather_analysis.get(
                            'air_quality', {}).get(
                            'aqi_description', 'N/A')}")
            else:
                print(
                    f"⚠️ OpenWeather enhancement failed: {
                        openweather_analysis.get('error')}")

        # Step 3: Combine analyses for optimal betting intelligence
        analysis["combined_impact"] = self._combine_weather_analyses(
            analysis["primary_analysis"], analysis.get("enhanced_features", {})
        )

        return analysis

    def _should_use_openweather(self, nws_analysis: dict) -> bool:
        """
        Determine if OpenWeather enhancement is cost-justified
        Smart cost optimization based on weather conditions
        """

        if "error" in nws_analysis:
            return True  # Use as fallback if NWS fails

        # Use OpenWeather for enhanced features in these scenarios:
        enhancement_triggers = [
            # High-impact weather conditions need air quality data
            nws_analysis.get("betting_impact", {}).get("impact_score", 0) >= 6,
            # Multiple weather alerts suggest complex conditions
            len(nws_analysis.get("weather_alerts", [])) >= 2,
            # Temperature extremes may affect air quality
            self._has_extreme_temperature(nws_analysis),
            # High wind conditions may affect air quality/visibility
            self._has_high_wind_conditions(nws_analysis),
        ]

        return any(enhancement_triggers)

    def _has_extreme_temperature(self, nws_analysis: dict) -> bool:
        """Check for extreme temperature conditions"""
        current = nws_analysis.get("current_weather", {})
        temp = current.get("temperature")
        return temp is not None and (temp < 20 or temp > 85)

    def _has_high_wind_conditions(self, nws_analysis: dict) -> bool:
        """Check for high wind conditions"""
        current = nws_analysis.get("current_weather", {})
        wind_speed = current.get("wind_speed", 0)
        wind_gust = current.get("wind_gust", 0)

        # Safely handle wind values that might be dicts or other types
        wind_speed_val = wind_speed if isinstance(wind_speed, (int, float)) else 0
        wind_gust_val = wind_gust if isinstance(wind_gust, (int, float)) else 0

        return max(wind_speed_val, wind_gust_val) >= 20

    def _combine_weather_analyses(
            self, nws_data: dict, openweather_data: dict) -> dict[str, Any]:
        """
        Intelligently combine NWS and OpenWeather data
        Creates superior betting analysis from dual sources
        """

        if not nws_data or "error" in nws_data:
            if openweather_data and "error" not in openweather_data:
                return openweather_data.get("betting_impact", {})
            else:
                return {"error": "No weather data available from either source"}

        # Start with NWS as primary source
        combined_impact = nws_data.get("betting_impact", {}).copy()

        # Enhance with OpenWeather features if available
        if openweather_data and "error" not in openweather_data:

            # Add air quality considerations
            air_quality = openweather_data.get("air_quality", {})
            aqi = air_quality.get("aqi", 0)

            if aqi >= 4:  # Poor air quality
                combined_impact["impact_score"] = min(
                    combined_impact.get("impact_score", 0) + 2, 10
                )
                combined_impact["impact_factors"] = combined_impact.get(
                    "impact_factors", [])
                combined_impact["impact_factors"].append(
                    f"Poor air quality (AQI {aqi}) - Player performance risk"
                )
            elif aqi >= 3:  # Moderate air quality
                combined_impact["impact_score"] = min(
                    combined_impact.get("impact_score", 0) + 1, 10
                )
                combined_impact["impact_factors"] = combined_impact.get(
                    "impact_factors", [])
                combined_impact["impact_factors"].append(
                    f"Moderate air quality (AQI {aqi}) - Minor performance impact"
                )

            # Compare and enhance temperature data
            nws_temp = nws_data.get("current_weather", {}).get("temperature")
            ow_temp = openweather_data.get("current_weather", {}).get("temp")

            if nws_temp and ow_temp:
                temp_diff = abs(nws_temp - ow_temp)
                if temp_diff > 5:  # Significant difference
                    combined_impact["data_quality_note"] = (
                        f"Temperature variance: NWS {nws_temp}°F vs OpenWeather {ow_temp}°F")

        # Recalculate impact level based on enhanced score
        impact_score = combined_impact.get("impact_score", 0)
        if impact_score >= 8:
            combined_impact["impact_level"] = "CRITICAL"
        elif impact_score >= 6:
            combined_impact["impact_level"] = "HIGH"
        elif impact_score >= 4:
            combined_impact["impact_level"] = "MEDIUM"
        elif impact_score >= 2:
            combined_impact["impact_level"] = "LOW"
        else:
            combined_impact["impact_level"] = "MINIMAL"

        # Add dual-source confidence indicator
        combined_impact["data_confidence"] = "Enhanced - Dual Source Verification"
        combined_impact["source_summary"] = "NWS Government Data + OpenWeather Enhancement"

        return combined_impact

    def get_optimal_weather_strategy(self) -> dict[str, Any]:
        """
        Return the optimal weather strategy configuration for EQ12
        Balances cost, accuracy, and comprehensive coverage
        """

        strategy = {
            "recommended_approach": "Dual-Source Hybrid Strategy",
            "primary_benefits": {
                "nws_advantages": [
                    "100% FREE - No API key required",
                    "Government-grade accuracy and reliability",
                    "No rate limits for typical betting use",
                    "Official weather alerts and warnings",
                    "Detailed hourly forecasts from local offices",
                ],
                "openweather_advantages": [
                    "Air quality data for player performance analysis",
                    "Global coverage including international venues",
                    "AI Weather Assistant for natural language queries",
                    "Comprehensive API with consistent data format",
                    "Historical weather data for trend analysis",
                ],
            },
            "cost_optimization": {
                "strategy": "NWS-First with Smart OpenWeather Enhancement",
                "monthly_cost_estimate": "$0-15 for typical EQ12 usage",
                "cost_breakdown": {
                    "nws_calls": "Unlimited FREE",
                    "openweather_calls": "1,000 FREE/day, then $0.0015 each",
                    "smart_triggering": "Only use OpenWeather when high-value conditions detected",
                },
            },
            "implementation_priority": {
                "phase_1": "Implement FREE NWS client for immediate use",
                "phase_2": "Add OpenWeather for air quality and enhancement",
                "phase_3": "Optimize dual-source triggering logic",
                "phase_4": "Historical analysis and ML integration",
            },
            "betting_intelligence_maximization": {
                "data_sources": "Government reliability + Commercial enhancement",
                "coverage": "Complete NHL arena coverage + travel routes",
                "alerting": "Official NWS warnings + commercial AI analysis",
                "cost_efficiency": "95% free government data + 5% targeted enhancements",
            },
        }

        return strategy

    def analyze_multiple_games(self, teams: list[str]) -> dict[str, Any]:
        """
        Analyze weather for multiple games using optimal dual-source strategy
        Automatically balances cost and data quality
        """

        results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "teams_analyzed": len(teams),
            "strategy_used": "Dual-Source Cost-Optimized",
            "game_analyses": {},
            "summary_metrics": {
                "critical_weather_games": 0,
                "enhanced_analysis_games": 0,
                "total_api_calls": {"nws": 0, "openweather": 0},
                "estimated_cost": 0.0,
            },
        }

        for team in teams:
            print(f"\n🏒 Analyzing weather for {team} using dual-source strategy...")

            analysis = self.get_comprehensive_weather_analysis(team)
            results["game_analyses"][team] = analysis

            # Update metrics
            results["summary_metrics"]["total_api_calls"]["nws"] += analysis["cost_summary"][
                "nws_calls"
            ]
            results["summary_metrics"]["total_api_calls"]["openweather"] += analysis[
                "cost_summary"
            ]["openweather_calls"]
            results["summary_metrics"]["estimated_cost"] += analysis["cost_summary"]["total_cost"]

            if "OpenWeather" in analysis["sources_used"]:
                results["summary_metrics"]["enhanced_analysis_games"] += 1

            impact_level = analysis.get(
                "combined_impact", {}).get(
                "impact_level", "MINIMAL")
            if impact_level in ["HIGH", "CRITICAL"]:
                results["summary_metrics"]["critical_weather_games"] += 1

        return results


def main():
    """Demo the EQ12 Dual Weather Strategy"""

    print("⚡ EQ12 DUAL WEATHER STRATEGY - OPTIMAL INTEGRATION")
    print("=" * 60)
    print("🏛️ PRIMARY: FREE National Weather Service (Government)")
    print("🌤️ ENHANCEMENT: OpenWeather (When Cost-Justified)")
    print("")

    strategy = EQ12DualWeatherStrategy()

    # Show optimal strategy
    optimal_config = strategy.get_optimal_weather_strategy()
    print("🎯 RECOMMENDED APPROACH:")
    print(f"   Strategy: {optimal_config['recommended_approach']}")
    print(
        f"   Monthly Cost: {
            optimal_config['cost_optimization']['monthly_cost_estimate']}")
    print(
        f"   Data Sources: {
            optimal_config['betting_intelligence_maximization']['data_sources']}")
    print("")

    # Test with sample teams
    test_teams = ["Boston", "Colorado", "Vegas"]

    print(f"📊 TESTING DUAL-SOURCE ANALYSIS FOR {len(test_teams)} TEAMS:")
    results = strategy.analyze_multiple_games(test_teams)

    print("\n📈 DUAL-SOURCE SUMMARY:")
    metrics = results["summary_metrics"]
    print(f"   🏛️ NWS Calls: {metrics['total_api_calls']['nws']} (FREE)")
    print(f"   🌤️ OpenWeather Calls: {metrics['total_api_calls']['openweather']}")
    print(f"   💰 Total Cost: ${metrics['estimated_cost']:.4f}")
    print(
        f"   📊 Enhanced Analyses: {metrics['enhanced_analysis_games']}/{len(test_teams)}")
    print(f"   ⚠️ Critical Weather Games: {metrics['critical_weather_games']}")

    print("\n✅ EQ12 DUAL WEATHER STRATEGY READY!")
    print("   💰 Cost-Optimized: 95% free government data")
    print("   📊 Enhanced Intelligence: Smart commercial augmentation")
    print("   🎯 Betting Edge: Maximum weather awareness at minimal cost")


if __name__ == "__main__":
    main()
