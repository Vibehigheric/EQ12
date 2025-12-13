#!/usr/bin/env python3
"""
EQ12 Enhanced NBA Intelligence System
Multi-API NBA betting intelligence with comprehensive provider support
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime, timedelta
from typing import Any

import requests

# Configure enhanced logging with unicode support
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/nba_enhanced.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


class EQ12EnhancedNBAIntelligence:
    """
    EQ12 Enhanced NBA Intelligence System
    Multi-provider NBA data integration for premium betting intelligence
    """

    def __init__(self, api_key: str | None = None):
        """Initialize Enhanced NBA Intelligence with multi-provider support"""
        self.api_key = api_key or os.getenv(
            "NBA_API_KEY", "8716c77c5ce79d828b73eccc10819a10")

        # Multiple NBA API providers to test
        self.providers = {
            "rapidapi_basketball": {
                "base_url": "https://api-basketball.p.rapidapi.com",
                "headers": {
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": "api-basketball.p.rapidapi.com",
                },
            },
            "rapidapi_nba": {
                "base_url": "https://api-nba-v1.p.rapidapi.com",
                "headers": {
                    "X-RapidAPI-Key": self.api_key,
                    "X-RapidAPI-Host": "api-nba-v1.p.rapidapi.com",
                },
            },
            "sportsdata_nba": {
                "base_url": "https://api.sportsdata.io/v3/nba",
                "headers": {"Ocp-Apim-Subscription-Key": self.api_key},
            },
            "balldontlie": {
                "base_url": "https://www.balldontlie.io/api/v1",
                "headers": {"Authorization": self.api_key},
            },
            "nba_official": {
                "base_url": "https://stats.nba.com/stats",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            },
        }

        self.session = requests.Session()
        self.active_providers = []
        self.best_provider = None

        logger.info("Enhanced NBA Intelligence System initialized")
        logger.info(f"API Key configured: {self.api_key[:8]}...")

    def discover_active_providers(self) -> dict[str, Any]:
        """Discover which NBA API providers are accessible with the given key"""
        logger.info("Discovering active NBA API providers...")

        discovery_results = {
            "active_providers": [],
            "provider_status": {},
            "best_provider": None,
            "total_tested": len(self.providers),
        }

        for provider_name, config in self.providers.items():
            logger.info(f"Testing provider: {provider_name}")

            try:
                # Test different endpoints for each provider
                test_endpoints = {
                    "rapidapi_basketball": "/status",
                    "rapidapi_nba": "/teams",
                    "sportsdata_nba": "/scores/json/GamesByDate/2024-10-10",
                    "balldontlie": "/teams",
                    "nba_official": "/teamstats",
                }

                endpoint = test_endpoints.get(provider_name, "/status")
                url = f"{config['base_url']}{endpoint}"

                response = self.session.get(url, headers=config["headers"], timeout=10)

                status = {
                    "accessible": False,
                    "status_code": response.status_code,
                    "response_size": len(response.content),
                    "error": None,
                }

                if response.status_code == 200:
                    status["accessible"] = True
                    discovery_results["active_providers"].append(provider_name)
                    logger.info(f"Provider {provider_name}: ACTIVE")

                    if not discovery_results["best_provider"]:
                        discovery_results["best_provider"] = provider_name

                elif response.status_code == 403:
                    status["error"] = "Access forbidden - check API key/subscription"
                    logger.warning(f"Provider {provider_name}: ACCESS DENIED (403)")

                elif response.status_code == 401:
                    status["error"] = "Unauthorized - invalid API key"
                    logger.warning(f"Provider {provider_name}: UNAUTHORIZED (401)")

                else:
                    status["error"] = f"HTTP {response.status_code}"
                    logger.warning(
                        f"Provider {provider_name}: ERROR ({
                            response.status_code})")

                discovery_results["provider_status"][provider_name] = status

            except Exception as e:
                error_status = {
                    "accessible": False,
                    "status_code": None,
                    "response_size": 0,
                    "error": str(e),
                }
                discovery_results["provider_status"][provider_name] = error_status
                logger.warning(f"Provider {provider_name}: CONNECTION ERROR - {e}")

            # Small delay between tests
            time.sleep(0.5)

        self.active_providers = discovery_results["active_providers"]
        self.best_provider = discovery_results["best_provider"]

        logger.info(
            f"Discovery complete: {len(self.active_providers)}/{len(self.providers)} providers active"
        )
        return discovery_results

    def get_nba_teams_multi_provider(self) -> dict[str, Any]:
        """Get NBA teams using best available provider"""
        logger.info("Fetching NBA teams from available providers...")

        if not self.active_providers:
            self.discover_active_providers()

        if not self.active_providers:
            return {"success": False, "error": "No active NBA API providers found"}

        # Try each active provider until we get data
        for provider in self.active_providers:
            try:
                config = self.providers[provider]

                if provider == "rapidapi_basketball":
                    url = f"{config['base_url']}/teams"
                    params = {"league": "12", "season": "2024-2025"}  # NBA league ID

                elif provider == "rapidapi_nba":
                    url = f"{config['base_url']}/teams"
                    params = {}

                elif provider == "sportsdata_nba":
                    url = f"{config['base_url']}/scores/json/teams"
                    params = {}

                elif provider == "balldontlie":
                    url = f"{config['base_url']}/teams"
                    params = {}

                else:
                    continue

                response = self.session.get(
                    url, headers=config["headers"], params=params, timeout=15
                )

                if response.status_code == 200:
                    data = response.json()

                    # Normalize response format
                    teams = []
                    if provider.startswith("rapidapi"):
                        teams = data.get("response", data.get("data", []))
                    else:
                        teams = data if isinstance(
                            data, list) else data.get(
                            "teams", [])

                    logger.info(
                        f"Successfully retrieved {
                            len(teams)} NBA teams from {provider}")
                    return {
                        "success": True,
                        "teams": teams,
                        "provider": provider,
                        "total_teams": len(teams),
                    }

            except Exception as e:
                logger.warning(f"Provider {provider} failed for teams: {e}")
                continue

        return {"success": False, "error": "All providers failed for teams data"}

    def get_nba_games_today(self) -> dict[str, Any]:
        """Get today's NBA games from available providers"""
        logger.info("Fetching today's NBA games...")

        if not self.active_providers:
            self.discover_active_providers()

        if not self.active_providers:
            return {"success": False, "error": "No active NBA API providers found"}

        today = datetime.now().strftime("%Y-%m-%d")

        for provider in self.active_providers:
            try:
                config = self.providers[provider]

                if provider == "rapidapi_basketball":
                    url = f"{config['base_url']}/games"
                    params = {"league": "12", "season": "2024-2025", "date": today}

                elif provider == "rapidapi_nba":
                    url = f"{config['base_url']}/games"
                    params = {"date": today}

                elif provider == "sportsdata_nba":
                    url = f"{config['base_url']}/scores/json/GamesByDate/{today}"
                    params = {}

                elif provider == "balldontlie":
                    url = f"{config['base_url']}/games"
                    params = {"dates[]": today}

                else:
                    continue

                response = self.session.get(
                    url, headers=config["headers"], params=params, timeout=15
                )

                if response.status_code == 200:
                    data = response.json()

                    # Normalize response format
                    games = []
                    if provider.startswith("rapidapi"):
                        games = data.get("response", data.get("data", []))
                    else:
                        games = data if isinstance(
                            data, list) else data.get(
                            "games", [])

                    # Identify live games
                    live_games = []
                    for game in games:
                        game_status = self._extract_game_status(game, provider)
                        if game_status and game_status.get("is_live", False):
                            live_games.append(game)

                    logger.info(
                        f"Found {
                            len(games)} games today, {
                            len(live_games)} live from {provider}")
                    return {
                        "success": True,
                        "games": games,
                        "live_games": live_games,
                        "provider": provider,
                        "date": today,
                        "total_games": len(games),
                        "live_count": len(live_games),
                    }

            except Exception as e:
                logger.warning(f"Provider {provider} failed for games: {e}")
                continue

        return {"success": False, "error": "All providers failed for games data"}

    def _extract_game_status(self, game: dict, provider: str) -> dict[str, Any]:
        """Extract normalized game status from different providers"""
        try:
            if provider == "rapidapi_basketball":
                status = game.get("status", {})
                return {
                    "is_live": status.get("short") in [
                        "1H", "2H", "3H", "4H", "OT", "HT"], "status_text": status.get(
                        "long", "Unknown"), "period": status.get(
                        "short", "Unknown"), }

            elif provider == "rapidapi_nba":
                status = game.get("status", {})
                return {
                    "is_live": status.get("halftime", False)
                    or status.get("short") in ["Q1", "Q2", "Q3", "Q4", "OT"],
                    "status_text": status.get("long", "Unknown"),
                    "period": status.get("short", "Unknown"),
                }

            elif provider == "sportsdata_nba":
                status = game.get("Status", "Unknown")
                return {
                    "is_live": status
                    in [
                        "InProgress",
                        "1st",
                        "2nd",
                        "3rd",
                        "4th",
                        "Overtime",
                        "Halftime",
                    ],
                    "status_text": status,
                    "period": game.get("Period", "Unknown"),
                }

            elif provider == "balldontlie":
                status = game.get("status", "Unknown")
                return {
                    "is_live": status in ["Live", "In Progress"],
                    "status_text": status,
                    "period": game.get("period", "Unknown"),
                }

        except Exception as e:
            logger.warning(f"Error extracting game status: {e}")

        return {"is_live": False, "status_text": "Unknown", "period": "Unknown"}

    def generate_comprehensive_nba_report(self) -> dict[str, Any]:
        """Generate comprehensive NBA intelligence report"""
        logger.info("Generating comprehensive NBA intelligence report...")

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "api_discovery": None,
            "teams_data": None,
            "games_data": None,
            "betting_intelligence": {
                "live_opportunities": [],
                "high_value_games": [],
                "recommendations": [],
            },
            "system_status": "unknown",
        }

        # Discover available APIs
        discovery = self.discover_active_providers()
        report["api_discovery"] = discovery

        if discovery["active_providers"]:
            logger.info(f"Using {len(discovery['active_providers'])} active providers")

            # Get teams data
            teams_result = self.get_nba_teams_multi_provider()
            report["teams_data"] = teams_result

            # Get games data
            games_result = self.get_nba_games_today()
            report["games_data"] = games_result

            # Generate betting intelligence
            if games_result.get("success"):
                report["betting_intelligence"] = self._analyze_betting_opportunities(
                    games_result)

            report["system_status"] = "operational"
        else:
            logger.warning("No active NBA API providers found")
            report["system_status"] = "no_api_access"

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"C:/EQ12/logs/nba_comprehensive_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"Comprehensive NBA report saved: {report_file}")
        return report

    def _analyze_betting_opportunities(self, games_data: dict) -> dict[str, Any]:
        """Analyze games for betting opportunities"""
        opportunities = {
            "live_opportunities": [],
            "high_value_games": [],
            "recommendations": [],
        }

        if not games_data.get("success"):
            return opportunities

        games = games_data.get("games", [])
        live_games = games_data.get("live_games", [])

        # Analyze live games for immediate opportunities
        for game in live_games:
            opportunity = {
                "game_id": game.get("id", "unknown"),
                "teams": self._extract_team_names(game, games_data["provider"]),
                "status": self._extract_game_status(game, games_data["provider"]),
                "value_rating": "HIGH",  # Live games always high value
                "reason": "Live game with dynamic odds",
            }
            opportunities["live_opportunities"].append(opportunity)

        # Identify high-value upcoming games
        for game in games[:5]:  # Top 5 games for analysis
            if not self._extract_game_status(
                    game, games_data["provider"]).get("is_live"):
                teams = self._extract_team_names(game, games_data["provider"])
                if teams:
                    opportunity = {
                        "game_id": game.get("id", "unknown"),
                        "teams": teams,
                        "value_rating": "MEDIUM",
                        "reason": "Prime time matchup with betting potential",
                    }
                    opportunities["high_value_games"].append(opportunity)

        # Generate recommendations
        if live_games:
            opportunities["recommendations"].append(
                f"Monitor {len(live_games)} live games for in-play betting opportunities"
            )

        if games:
            opportunities["recommendations"].append(
                f"Analyze {len(games)} games scheduled today for pre-game value"
            )

        return opportunities

    def _extract_team_names(self, game: dict, provider: str) -> str:
        """Extract team names from different provider formats"""
        try:
            if provider == "rapidapi_basketball":
                teams = game.get("teams", {})
                away = teams.get("away", {}).get("name", "Unknown")
                home = teams.get("home", {}).get("name", "Unknown")
                return f"{away} @ {home}"

            elif provider == "rapidapi_nba":
                teams = game.get("teams", {})
                away = teams.get("visitors", {}).get("name", "Unknown")
                home = teams.get("home", {}).get("name", "Unknown")
                return f"{away} @ {home}"

            elif provider == "sportsdata_nba":
                away = game.get("AwayTeam", "Unknown")
                home = game.get("HomeTeam", "Unknown")
                return f"{away} @ {home}"

            elif provider == "balldontlie":
                away = game.get("visitor_team", {}).get("full_name", "Unknown")
                home = game.get("home_team", {}).get("full_name", "Unknown")
                return f"{away} @ {home}"

        except Exception as e:
            logger.warning(f"Error extracting team names: {e}")

        return "Unknown Teams"


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="EQ12 Enhanced NBA Intelligence System")
    parser.add_argument("--api-key", help="NBA API key")
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Discover available API providers")
    parser.add_argument("--teams", action="store_true", help="Get NBA teams")
    parser.add_argument("--games", action="store_true", help="Get today's games")
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate comprehensive report")
    parser.add_argument("--monitor", type=int, help="Monitor games for N minutes")

    args = parser.parse_args()

    # Initialize Enhanced NBA Intelligence
    nba_system = EQ12EnhancedNBAIntelligence(api_key=args.api_key)

    print("EQ12 ENHANCED NBA INTELLIGENCE SYSTEM")
    print("=" * 80)

    if args.discover:
        print("Discovering NBA API providers...")
        result = nba_system.discover_active_providers()
        print("\nAPI Discovery Results:")
        print(
            f"   Active Providers: {len(result['active_providers'])}/{result['total_tested']}")
        print(f"   Best Provider: {result['best_provider'] or 'None'}")

        for provider, status in result["provider_status"].items():
            status_icon = "✅" if status["accessible"] else "❌"
            error_info = f" - {status['error']}" if status["error"] else ""
            print(
                f"   {status_icon} {provider}: HTTP {
                    status['status_code']}{error_info}")

    elif args.teams:
        print("Fetching NBA teams...")
        result = nba_system.get_nba_teams_multi_provider()
        if result["success"]:
            print(
                f"✅ Found {
                    result['total_teams']} NBA teams using {
                    result['provider']}")
        else:
            print(f"❌ Error: {result['error']}")

    elif args.games:
        print("Fetching today's NBA games...")
        result = nba_system.get_nba_games_today()
        if result["success"]:
            print(
                f"🏀 Found {
                    result['total_games']} games today, {
                    result['live_count']} live")
            print(f"   Provider: {result['provider']}")
        else:
            print(f"❌ Error: {result['error']}")

    elif args.report:
        print("Generating comprehensive NBA intelligence report...")
        result = nba_system.generate_comprehensive_nba_report()
        print("\nNBA Intelligence Summary:")
        print(f"   System Status: {result['system_status'].upper()}")

        if result["api_discovery"]:
            active_count = len(result["api_discovery"]["active_providers"])
            total_count = result["api_discovery"]["total_tested"]
            print(f"   API Providers: {active_count}/{total_count} active")

        if result["teams_data"] and result["teams_data"]["success"]:
            print(f"   NBA Teams: {result['teams_data']['total_teams']} loaded")

        if result["games_data"] and result["games_data"]["success"]:
            games_count = result["games_data"]["total_games"]
            live_count = result["games_data"]["live_count"]
            print(f"   Games Today: {games_count} scheduled, {live_count} live")

        betting_ops = len(result["betting_intelligence"]["live_opportunities"])
        high_value = len(result["betting_intelligence"]["high_value_games"])
        print(f"   Betting Opportunities: {betting_ops} live, {high_value} high-value")

    elif args.monitor:
        print(f"Starting {args.monitor}-minute NBA monitoring...")
        end_time = datetime.now() + timedelta(minutes=args.monitor)

        while datetime.now() < end_time:
            result = nba_system.get_nba_games_today()
            if result["success"]:
                live_count = result["live_count"]
                total_count = result["total_games"]
                print(
                    f"🔄 {
                        datetime.now().strftime('%H:%M:%S')} - {live_count}/{total_count} games live")
            else:
                print(f"⚠️ Monitoring error: {result['error']}")

            time.sleep(60)  # Check every minute

    else:
        # Default: run comprehensive report
        print("Running default NBA intelligence analysis...")
        result = nba_system.generate_comprehensive_nba_report()

        print("\nNBA Intelligence Dashboard:")
        print(f"   System Status: {result['system_status'].upper()}")

        if result["api_discovery"]:
            active_providers = result["api_discovery"]["active_providers"]
            print(
                f"   Active Providers: {
                    ', '.join(active_providers) if active_providers else 'None'}")

        if result["betting_intelligence"]:
            live_ops = len(result["betting_intelligence"]["live_opportunities"])
            recommendations = len(result["betting_intelligence"]["recommendations"])
            print(f"   Live Opportunities: {live_ops}")
            print(f"   Recommendations: {recommendations}")

    print("\n✅ EQ12 Enhanced NBA Intelligence Complete!")


if __name__ == "__main__":
    main()
