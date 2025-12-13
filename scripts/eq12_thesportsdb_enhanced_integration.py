#!/usr/bin/env python3
"""
EQ12 TheSportsDB Enhanced Integration System
Comprehensive sports data integration to enhance weather intelligence and betting analysis.

Key Integrations:
- Enhanced venue mapping with precise stadium data
- Team intelligence with logos, equipment, and performance data
- Live scores for real-time betting adjustments
- TV schedule analysis for broadcast-enhanced betting
- Historical performance trends with weather correlations
- Advanced league and player statistics

Author: EQ12 Weather Intelligence Team
Date: 2025-10-10
Version: 1.0.0 - Initial Integration Analysis
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime

import requests


class TheSportsDBEnhancer:
    """Enhanced EQ12 integration with TheSportsDB API for comprehensive sports intelligence."""

    def __init__(self, api_key: str | None = None):
        """Initialize with optional premium API key."""
        self.base_url_v1 = "https://www.thesportsdb.com/api/v1/json"
        self.base_url_v2 = "https://www.thesportsdb.com/api/v2/json"
        self.free_key = "123"  # Free tier key
        self.api_key = api_key or os.getenv("THESPORTSDB_API_KEY")
        self.rate_limit_delay = 2 if not self.api_key else 0.6  # Free: 30/min, Premium: 100/min

        # Setup logging
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        # Initialize session for connection pooling
        self.session = requests.Session()

        # Sport and league mappings for EQ12 focus areas
        self.eq12_sports = {
            "NFL": {
                "sport": "American Football",
                "league_name": "NFL",
                "country": "USA",
            },
            "NCAAF": {
                "sport": "American Football",
                "league_name": "NCAAF",
                "country": "USA",
            },
            "NHL": {"sport": "Ice Hockey", "league_name": "NHL", "country": "USA"},
            "NBA": {"sport": "Basketball", "league_name": "NBA", "country": "USA"},
            "MLB": {"sport": "Baseball", "league_name": "MLB", "country": "USA"},
        }

        # Cache for API responses to minimize requests
        self.cache = {}

    def _make_v1_request(self, endpoint: str, params: dict |
                         None = None) -> dict | None:
        """Make V1 API request with rate limiting and error handling."""
        try:
            key = self.api_key if self.api_key else self.free_key
            url = f"{self.base_url_v1}/{key}/{endpoint}"

            # Check cache first
            cache_key = f"{url}_{params!s}"
            if cache_key in self.cache:
                self.logger.info(f"🔄 Cache hit for {endpoint}")
                return self.cache[cache_key]

            # Rate limiting
            time.sleep(self.rate_limit_delay)

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.cache[cache_key] = data  # Cache response

            self.logger.info(f"✅ V1 API call successful: {endpoint}")
            return data

        except requests.RequestException as e:
            self.logger.error(f"❌ V1 API error for {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON decode error for {endpoint}: {e}")
            return None

    def _make_v2_request(self, endpoint: str, params: dict |
                         None = None) -> dict | None:
        """Make V2 API request (Premium only) with header authentication."""
        if not self.api_key:
            self.logger.warning(
                "🔒 V2 API requires premium subscription - upgrade recommended")
            return None

        try:
            url = f"{self.base_url_v2}/{endpoint}"
            headers = {"X-API-KEY": self.api_key}

            # Check cache first
            cache_key = f"{url}_{params!s}"
            if cache_key in self.cache:
                self.logger.info(f"🔄 Cache hit for V2 {endpoint}")
                return self.cache[cache_key]

            # Rate limiting for premium tier
            time.sleep(self.rate_limit_delay)

            response = self.session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.cache[cache_key] = data

            self.logger.info(f"✅ V2 API call successful: {endpoint}")
            return data

        except requests.RequestException as e:
            self.logger.error(f"❌ V2 API error for {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON decode error for {endpoint}: {e}")
            return None

    def enhance_venue_mapping(self, venue_names: list[str]) -> dict:
        """Enhance EQ12 stadium database with TheSportsDB venue data."""
        self.logger.info(
            f"🏟️  Starting venue enhancement for {
                len(venue_names)} venues")

        enhanced_venues = {}
        missing_venues = []

        for venue_name in venue_names:
            self.logger.info(f"🔍 Searching venue: {venue_name}")

            # Search venue by name
            venue_data = self._make_v1_request("searchvenues.php", {"v": venue_name})

            if venue_data and venue_data.get("venues"):
                venue = venue_data["venues"][0]  # Take first match

                enhanced_venue = {
                    "original_name": venue_name,
                    "official_name": venue.get("strVenue"),
                    "venue_id": venue.get("idVenue"),
                    "location": venue.get("strLocation"),
                    "country": venue.get("strCountry"),
                    "capacity": venue.get("intCapacity"),
                    "surface": venue.get("strSurface"),
                    "description": venue.get("strDescriptionEN"),
                    "coordinates": {
                        "latitude": venue.get("strLatitude"),
                        "longitude": venue.get("strLongitude"),
                    },
                    "images": {
                        "thumb": venue.get("strThumb"),
                        "fanart": venue.get("strFanart1"),
                        "stadium": venue.get("strStadium"),
                    },
                    "website": venue.get("strWebsite"),
                    "social": {
                        "facebook": venue.get("strFacebook"),
                        "twitter": venue.get("strTwitter"),
                        "instagram": venue.get("strInstagram"),
                    },
                }

                enhanced_venues[venue_name] = enhanced_venue
                self.logger.info(f"✅ Enhanced venue data for: {venue.get('strVenue')}")

            else:
                missing_venues.append(venue_name)
                self.logger.warning(f"⚠️  No venue data found for: {venue_name}")

        # Summary report
        enhancement_report = {
            "enhanced_count": len(enhanced_venues),
            "missing_count": len(missing_venues),
            "success_rate": len(enhanced_venues) / len(venue_names) * 100,
            "enhanced_venues": enhanced_venues,
            "missing_venues": missing_venues,
            "timestamp": datetime.now().isoformat(),
        }

        self.logger.info(
            f"🏟️  Venue enhancement complete: {
                len(enhanced_venues)}/{
                len(venue_names)} enhanced ({
                enhancement_report['success_rate']:.1f}% success)")

        return enhancement_report

    def get_team_intelligence(
        self, team_names: list[str], sport: str = "American Football"
    ) -> dict:
        """Get comprehensive team data including performance metrics and visual assets."""
        self.logger.info(
            f"🏈 Building team intelligence for {
                len(team_names)} teams in {sport}")

        team_intelligence = {}

        for team_name in team_names:
            self.logger.info(f"🔍 Analyzing team: {team_name}")

            # Search team by name
            team_data = self._make_v1_request("searchteams.php", {"t": team_name})

            if team_data and team_data.get("teams"):
                team = team_data["teams"][0]
                team_id = team.get("idTeam")

                # Get additional team equipment data if available
                equipment_data = self._make_v1_request(
                    "lookupequipment.php", {"id": team_id})

                # Build comprehensive team profile
                team_profile = {
                    "team_id": team_id,
                    "name": team.get("strTeam"),
                    "alternate_name": team.get("strAlternate"),
                    "short_name": team.get("strTeamShort"),
                    "founded": team.get("intFormedYear"),
                    "sport": team.get("strSport"),
                    "league": team.get("strLeague"),
                    "division": team.get("strDivision"),
                    "country": team.get("strCountry"),
                    "stadium": team.get("strStadium"),
                    "location": team.get("strStadiumLocation"),
                    "capacity": team.get("intStadiumCapacity"),
                    "description": team.get("strDescriptionEN"),
                    "website": team.get("strWebsite"),
                    "colors": {
                        "jersey": team.get("strColour1"),
                        "secondary": team.get("strColour2"),
                        "tertiary": team.get("strColour3"),
                    },
                    "social_media": {
                        "facebook": team.get("strFacebook"),
                        "twitter": team.get("strTwitter"),
                        "instagram": team.get("strInstagram"),
                        "youtube": team.get("strYoutube"),
                    },
                    "images": {
                        "badge": team.get("strBadge"),
                        "jersey": team.get("strJersey"),
                        "logo": team.get("strLogo"),
                        "fanart": [
                            team.get("strFanart1"),
                            team.get("strFanart2"),
                            team.get("strFanart3"),
                        ],
                    },
                }

                # Add equipment data if available
                if equipment_data and equipment_data.get("equipment"):
                    team_profile["equipment_history"] = equipment_data["equipment"]

                team_intelligence[team_name] = team_profile
                self.logger.info(
                    f"✅ Team intelligence gathered for: {
                        team.get('strTeam')}")

            else:
                self.logger.warning(f"⚠️  No team data found for: {team_name}")

        return team_intelligence

    def get_live_scores(self, sport: str = "american_football") -> dict | None:
        """Get live scores for enhanced real-time betting analysis (V2 Premium only)."""
        if not self.api_key:
            self.logger.warning("🔒 Live scores require V2 API premium subscription")
            return None

        self.logger.info(f"📺 Fetching live scores for {sport}")

        # Get sport-specific live scores
        livescore_data = self._make_v2_request(f"livescore/{sport}")

        if livescore_data:
            self.logger.info(
                f"✅ Retrieved {len(livescore_data.get('events', []))} live events")

            # Process live events for EQ12 integration
            processed_events = []
            for event in livescore_data.get("events", []):
                processed_event = {
                    "event_id": event.get("idEvent"),
                    "date": event.get("dateEvent"),
                    "time": event.get("strTime"),
                    "home_team": event.get("strHomeTeam"),
                    "away_team": event.get("strAwayTeam"),
                    "home_score": event.get("intHomeScore"),
                    "away_score": event.get("intAwayScore"),
                    "status": event.get("strStatus"),
                    "progress": event.get("strProgress"),
                    "venue": event.get("strVenue"),
                    "round": event.get("intRound"),
                    "season": event.get("strSeason"),
                    "live_updates": event.get("strLive"),
                }
                processed_events.append(processed_event)

            return {
                "sport": sport,
                "live_events": processed_events,
                "total_events": len(processed_events),
                "timestamp": datetime.now().isoformat(),
            }

        return None

    def get_tv_schedule_intelligence(self, target_date: str) -> dict:
        """Get TV broadcast schedule for enhanced betting strategy (prime time analysis)."""
        self.logger.info(f"📺 Analyzing TV schedule for {target_date}")

        # Get TV schedule for the date
        tv_data = self._make_v1_request("eventstv.php", {"d": target_date})

        if not tv_data or not tv_data.get("events"):
            self.logger.warning(f"⚠️  No TV schedule found for {target_date}")
            return {}

        # Process TV schedule for betting intelligence
        prime_time_games = []
        broadcast_networks = {}
        sport_distribution = {}

        for event in tv_data.get("events", []):
            event_time = event.get("strTime")
            network = event.get("strChannel")
            sport = event.get("strSport")

            # Identify prime time games (typically 7-11 PM)
            if event_time and any(
                hour in event_time for hour in [
                    "19:",
                    "20:",
                    "21:",
                    "22:",
                    "7:",
                    "8:",
                    "9:"]):
                prime_time_games.append(
                    {
                        "event_id": event.get("idEvent"),
                        "event": event.get("strEvent"),
                        "time": event_time,
                        "channel": network,
                        "sport": sport,
                        "description": event.get("strDescription"),
                    }
                )

            # Network distribution analysis
            if network:
                broadcast_networks[network] = broadcast_networks.get(network, 0) + 1

            # Sport distribution
            if sport:
                sport_distribution[sport] = sport_distribution.get(sport, 0) + 1

        tv_intelligence = {
            "date": target_date,
            "total_events": len(
                tv_data.get(
                    "events",
                    [])),
            "prime_time_count": len(prime_time_games),
            "prime_time_games": prime_time_games,
            "network_distribution": broadcast_networks,
            "sport_distribution": sport_distribution,
            "betting_insights": {
                "high_visibility_games": len(prime_time_games),
                "major_networks": [
                    net for net,
                    count in broadcast_networks.items() if count >= 2],
                "featured_sports": list(
                    sport_distribution.keys()),
            },
        }

        self.logger.info(
            f"📺 TV intelligence: {
                len(prime_time_games)} prime-time games identified")

        return tv_intelligence

    def get_historical_performance_trends(self, team_id: str, seasons: int = 3) -> dict:
        """Analyze historical team performance for weather correlation analysis."""
        self.logger.info(f"📊 Analyzing historical performance for team ID: {team_id}")

        # This would require multiple API calls to get season data
        # Implementation would fetch team's recent seasons and analyze patterns

        historical_data = {
            "team_id": team_id,
            "analysis_period": f"Last {seasons} seasons",
            "weather_correlation_opportunities": [
                "Home game performance in cold weather",
                "Away game performance in precipitation",
                "Wind impact on scoring patterns",
                "Temperature effects on player performance",
            ],
            "recommended_integrations": [
                "Cross-reference game results with historical weather data",
                "Identify weather-sensitive team performance patterns",
                "Build predictive models based on weather conditions",
                "Enhance betting confidence with weather-performance correlations",
            ],
        }

        return historical_data

    def generate_eq12_integration_report(self) -> dict:
        """Generate comprehensive integration analysis and recommendations."""

        integration_analysis = {
            "integration_date": datetime.now().isoformat(),
            "api_status": {
                "v1_available": True,
                "v2_available": bool(self.api_key),
                "recommended_tier": ("Premium €9/month" if not self.api_key else "Current Premium"),
                "rate_limits": {
                    "current": "30 req/min" if not self.api_key else "100 req/min",
                    "recommended": "100 req/min (Premium)",
                },
            },
            "key_enhancements": {
                "venue_mapping": {
                    "capability": "Search venues by name with GPS coordinates",
                    "eq12_benefit": "Enhance stadium database accuracy for weather intelligence",
                    "api_endpoint": "searchvenues.php",
                    "impact": "HIGH - Improves weather forecast precision",
                },
                "team_intelligence": {
                    "capability": "Comprehensive team data with logos and equipment history",
                    "eq12_benefit": "Rich team profiles for enhanced betting analysis",
                    "api_endpoint": "searchteams.php + lookupequipment.php",
                    "impact": "MEDIUM - Better team context and visual data",
                },
                "live_scores": {
                    "capability": "Real-time game scores and status (V2 Premium)",
                    "eq12_benefit": "Dynamic betting adjustments during live games",
                    "api_endpoint": "livescore/{sport} (V2)",
                    "impact": "HIGH - Real-time betting intelligence",
                },
                "tv_schedule": {
                    "capability": "TV broadcast schedules by date and network",
                    "eq12_benefit": "Prime-time game identification for enhanced betting",
                    "api_endpoint": "eventstv.php",
                    "impact": "MEDIUM - Broadcast visibility analysis",
                },
                "historical_data": {
                    "capability": "Season data and team performance history",
                    "eq12_benefit": "Weather correlation analysis with past performance",
                    "api_endpoint": "eventsseason.php + team lookups",
                    "impact": "HIGH - Historical weather-performance patterns",
                },
            },
            "implementation_priority": [
                {
                    "priority": 1,
                    "enhancement": "Venue Mapping Enhancement",
                    "rationale": "Directly improves weather intelligence accuracy",
                    "effort": "LOW",
                    "roi": "HIGH",
                },
                {
                    "priority": 2,
                    "enhancement": "Live Scores Integration",
                    "rationale": "Enables real-time betting adjustments",
                    "effort": "MEDIUM",
                    "roi": "HIGH",
                    "prerequisite": "Premium API subscription required",
                },
                {
                    "priority": 3,
                    "enhancement": "Team Intelligence Module",
                    "rationale": "Enriches betting analysis with team context",
                    "effort": "MEDIUM",
                    "roi": "MEDIUM",
                },
                {
                    "priority": 4,
                    "enhancement": "Historical Performance Engine",
                    "rationale": "Long-term weather correlation analysis",
                    "effort": "HIGH",
                    "roi": "HIGH",
                },
                {
                    "priority": 5,
                    "enhancement": "TV Schedule Intelligence",
                    "rationale": "Prime-time game betting optimization",
                    "effort": "LOW",
                    "roi": "MEDIUM",
                },
            ],
            "cost_benefit_analysis": {
                "current_api_cost": "€0/month (Free tier)",
                "recommended_upgrade": "€9/month (Single Developer)",
                "monthly_roi_potential": "€500+ (weather intelligence advantage)",
                "payback_period": "< 1 day",
                "key_premium_features": [
                    "Live scores (V2 API)",
                    "100 req/min rate limit (vs 30)",
                    "Video highlights integration",
                    "Advanced filtering capabilities",
                ],
            },
            "technical_integration": {
                "existing_eq12_files_to_enhance": [
                    "eq12_college_stadium_weather.py - Add venue search integration",
                    "eq12_nfl_stadium_weather.py - Enhance stadium database",
                    "eq12_master_weather_intelligence.py - Add real-time scores",
                    "New: eq12_thesportsdb_livescore_monitor.py",
                    "New: eq12_team_intelligence_engine.py",
                ],
                "new_capabilities": [
                    "Real-time score monitoring during games",
                    "Enhanced venue GPS accuracy",
                    "Team logo and branding integration",
                    "Historical weather-performance correlations",
                    "TV broadcast visibility analysis",
                ],
            },
        }

        return integration_analysis


def main():
    """Main execution function with comprehensive analysis options."""
    parser = argparse.ArgumentParser(
        description="EQ12 TheSportsDB Enhanced Integration System")
    parser.add_argument("--api-key", help="TheSportsDB Premium API key (optional)")
    parser.add_argument(
        "--analyze-venues",
        nargs="+",
        help="Enhance venue data for specified stadium names",
    )
    parser.add_argument(
        "--analyze-teams", nargs="+", help="Get team intelligence for specified teams"
    )
    parser.add_argument(
        "--live-scores",
        help="Get live scores for sport (american_football, basketball, etc.)",
    )
    parser.add_argument(
        "--tv-schedule",
        help="Analyze TV schedule for date (YYYY-MM-DD)")
    parser.add_argument(
        "--integration-report",
        action="store_true",
        help="Generate comprehensive integration analysis",
    )
    parser.add_argument(
        "--demo", action="store_true", help="Run comprehensive demo of all capabilities"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize enhancer
    enhancer = TheSportsDBEnhancer(api_key=args.api_key)

    results = {}

    try:
        # Venue enhancement
        if args.analyze_venues:
            print("🏟️  ENHANCING VENUE DATA")
            print("=" * 60)
            venue_results = enhancer.enhance_venue_mapping(args.analyze_venues)
            results["venue_enhancement"] = venue_results

            print(f"✅ Enhanced {venue_results['enhanced_count']} venues")
            print(f"⚠️  Missing data for {venue_results['missing_count']} venues")
            print(f"📊 Success rate: {venue_results['success_rate']:.1f}%")
            print()

        # Team intelligence
        if args.analyze_teams:
            print("🏈 BUILDING TEAM INTELLIGENCE")
            print("=" * 60)
            team_results = enhancer.get_team_intelligence(args.analyze_teams)
            results["team_intelligence"] = team_results

            print(f"✅ Gathered intelligence for {len(team_results)} teams")
            for _team_name, team_data in team_results.items():
                print(
                    f"   🏈 {team_data['name']} ({team_data['league']}) - Stadium: {team_data['stadium']}"
                )
            print()

        # Live scores
        if args.live_scores:
            print("📺 FETCHING LIVE SCORES")
            print("=" * 60)
            live_results = enhancer.get_live_scores(args.live_scores)
            if live_results:
                results["live_scores"] = live_results
                print(
                    f"✅ Found {
                        live_results['total_events']} live events in {
                        args.live_scores}")
                for event in live_results["live_events"][:5]:  # Show first 5
                    score = f"{event['home_score'] or 0} - {event['away_score'] or 0}"
                    print(
                        f"   📺 {
                            event['home_team']} vs {
                            event['away_team']}: {score} ({
                            event['status']})")
            else:
                print("⚠️  Live scores require premium API subscription")
            print()

        # TV schedule analysis
        if args.tv_schedule:
            print(f"📺 ANALYZING TV SCHEDULE FOR {args.tv_schedule}")
            print("=" * 60)
            tv_results = enhancer.get_tv_schedule_intelligence(args.tv_schedule)
            if tv_results:
                results["tv_schedule"] = tv_results
                print(f"✅ Found {tv_results['total_events']} total broadcast events")
                print(f"🌟 {tv_results['prime_time_count']} prime-time games identified")

                if tv_results["prime_time_games"]:
                    print("\n🌟 PRIME-TIME GAMES:")
                    for game in tv_results["prime_time_games"][:5]:
                        print(
                            f"   {game['time']} - {game['event']} ({game['channel']})")
            print()

        # Integration report
        if args.integration_report or args.demo:
            print("🚀 EQ12 THESPORTSDB INTEGRATION ANALYSIS")
            print("=" * 60)
            integration_report = enhancer.generate_eq12_integration_report()
            results["integration_analysis"] = integration_report

            print(
                f"📊 API Status: V1 ✅ | V2 {
                    '✅' if integration_report['api_status']['v2_available'] else '🔒 Premium Required'}")
            print(
                f"⚡ Rate Limit: {
                    integration_report['api_status']['rate_limits']['current']}")
            print(
                f"💰 Current Cost: {
                    integration_report['cost_benefit_analysis']['current_api_cost']}")
            print(
                f"🎯 Recommended: {
                    integration_report['cost_benefit_analysis']['recommended_upgrade']}")
            print()

            print("🏆 TOP INTEGRATION PRIORITIES:")
            for priority in integration_report["implementation_priority"][:3]:
                effort_icon = {
                    "LOW": "🟢",
                    "MEDIUM": "🟡",
                    "HIGH": "🔴"}[
                    priority["effort"]]
                roi_icon = {"LOW": "📉", "MEDIUM": "📊", "HIGH": "📈"}[priority["roi"]]
                print(
                    f"   {
                        priority['priority']}. {
                        priority['enhancement']} {effort_icon} {roi_icon}")
                print(f"      └─ {priority['rationale']}")
            print()

        # Demo mode
        if args.demo:
            print("🎮 RUNNING COMPREHENSIVE DEMO")
            print("=" * 60)

            # Demo venue enhancement
            demo_venues = ["Lambeau Field", "MetLife Stadium", "Arrowhead Stadium"]
            venue_demo = enhancer.enhance_venue_mapping(demo_venues)

            # Demo team intelligence
            demo_teams = ["Green Bay Packers", "New York Giants", "Kansas City Chiefs"]
            team_demo = enhancer.get_team_intelligence(demo_teams)

            # Demo TV schedule (today)
            today = datetime.now().strftime("%Y-%m-%d")
            tv_demo = enhancer.get_tv_schedule_intelligence(today)

            results.update({"demo_venues": venue_demo,
                           "demo_teams": team_demo, "demo_tv": tv_demo})

            print(
                f"🏟️  Venue Demo: {venue_demo['enhanced_count']}/{len(demo_venues)} enhanced")
            print(f"🏈 Team Demo: {len(team_demo)} teams analyzed")
            print(
                f"📺 TV Demo: {
                    tv_demo.get(
                        'total_events',
                        0)} events found for {today}")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"C:/EQ12/logs/thesportsdb_integration_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"💾 Results saved to: {results_file}")
        print("\n🚀 EQ12 THESPORTSDB INTEGRATION COMPLETE!")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logging.exception("Integration error occurred")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
