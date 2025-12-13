"""
EQ12 Betting Intelligence Orchestrator
Core automation system for MLB playoff betting intelligence

Features:
- Lineup Lock Watcher
- Injury & Status Sentinel
- Weather & Park Factor Engine
- SGP Builder with DraftKings rules
- Circuit breaker integration
- Real-time odds monitoring
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class BettingAlert:
    """Betting intelligence alert structure"""

    type: str
    priority: str  # high, medium, low
    message: str
    data: dict[str, Any]
    timestamp: str
    game_id: str | None = None


class CircuitBreaker:
    """Circuit breaker for external API calls"""

    def __init__(self, failure_threshold: int = 5, timeout_duration: int = 300):
        """TODO: Add docstring for __init__"""

        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration
        self.state_file = Path("logs/circuit_breaker/state.json")
        self.state = self.load_state()

    def load_state(self) -> dict:
        """Load circuit breaker state from disk"""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception:
                pass
        return {
            "status": "healthy",
            "offline": False,
            "until": None,
            "failure_count": 0,
            "last_failure": None,
        }

    def save_state(self):
        """Save circuit breaker state to disk"""
        self.state_file.parent.mkdir(exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def is_available(self) -> bool:
        """Check if circuit breaker allows requests"""
        if not self.state.get("offline"):
            return True

        until_str = self.state.get("until")
        if until_str:
            until_time = datetime.fromisoformat(until_str.replace("Z", "+00:00"))
            if datetime.now() > until_time:
                # Reset circuit breaker
                self.state.update(
                    {
                        "offline": False,
                        "until": None,
                        "failure_count": 0,
                        "status": "healthy",
                    }
                )
                self.save_state()
                return True
        return False

    def record_failure(self):
        """Record a failure and potentially trip circuit breaker"""
        self.state["failure_count"] += 1
        self.state["last_failure"] = datetime.now().isoformat()

        if self.state["failure_count"] >= self.failure_threshold:
            # Trip circuit breaker
            until_time = datetime.now() + timedelta(seconds=self.timeout_duration)
            self.state.update(
                {
                    "offline": True,
                    "until": until_time.isoformat() + "Z",
                    "status": "tripped",
                }
            )
            logging.warning(f"Circuit breaker tripped until {until_time}")

        self.save_state()

    def record_success(self):
        """Record successful operation"""
        if self.state["failure_count"] > 0:
            self.state["failure_count"] = max(0, self.state["failure_count"] - 1)
            if self.state["failure_count"] == 0:
                self.state["status"] = "healthy"
            self.save_state()


class LineupWatcher:
    """Monitors MLB lineup announcements"""

    def __init__(self, circuit_breaker: CircuitBreaker):
        """TODO: Add docstring for __init__"""

        self.cb = circuit_breaker
        self.api_key = os.getenv("ODDS_API_KEY")
        self.lineup_cache = {}

    async def check_lineups(self) -> list[BettingAlert]:
        """Check for lineup updates"""
        alerts = []

        if not self.cb.is_available():
            return alerts

        try:
            # Mock lineup check - replace with real API
            games = await self._fetch_todays_games()

            for game in games:
                lineup_status = await self._check_game_lineup(game)
                if lineup_status.get(
                        "confirmed") and game["id"] not in self.lineup_cache:
                    alert = BettingAlert(
                        type="lineup_confirmed",
                        priority="high",
                        message=f"Lineup confirmed: {
                            game['home_team']} vs {
                            game['away_team']}",
                        data=lineup_status,
                        timestamp=datetime.now().isoformat(),
                        game_id=game["id"],
                    )
                    alerts.append(alert)
                    self.lineup_cache[game["id"]] = lineup_status

            self.cb.record_success()

        except Exception as e:
            logging.error(f"Lineup watcher error: {e}")
            self.cb.record_failure()

        return alerts

    async def _fetch_todays_games(self) -> list[dict]:
        """Fetch today's MLB games"""
        # Mock data - replace with real API call
        return [
            {
                "id": "game_001",
                "home_team": "Yankees",
                "away_team": "Dodgers",
                "start_time": "19:00",
            }
        ]

    async def _check_game_lineup(self, game: dict) -> dict:
        """Check specific game lineup status"""
        # Mock lineup data - replace with real API
        return {
            "confirmed": True,
            "home_lineup": ["Judge", "Stanton", "Torres"],
            "away_lineup": ["Betts", "Freeman", "Turner"],
            "home_pitcher": "Cole",
            "away_pitcher": "Kershaw",
        }


class InjurySentinel:
    """Monitors player injury updates and status changes"""

    def __init__(self, circuit_breaker: CircuitBreaker):
        """TODO: Add docstring for __init__"""

        self.cb = circuit_breaker
        self.injury_cache = {}

    async def check_injuries(self) -> list[BettingAlert]:
        """Check for injury updates"""
        alerts = []

        if not self.cb.is_available():
            return alerts

        try:
            injury_updates = await self._fetch_injury_updates()

            for update in injury_updates:
                if (
                    update["player_id"] not in self.injury_cache
                    or self.injury_cache[update["player_id"]]["status"] != update["status"]
                ):
                    alert = BettingAlert(
                        type="injury_update",
                        priority=self._get_injury_priority(update),
                        message=f"Injury Update: {update['player_name']} - {update['status']}",
                        data=update,
                        timestamp=datetime.now().isoformat(),
                    )
                    alerts.append(alert)
                    self.injury_cache[update["player_id"]] = update

            self.cb.record_success()

        except Exception as e:
            logging.error(f"Injury sentinel error: {e}")
            self.cb.record_failure()

        return alerts

    def _get_injury_priority(self, update: dict) -> str:
        """Determine alert priority based on injury severity"""
        status = update.get("status", "").lower()
        if status in ["out", "scratched"]:
            return "high"
        if status in ["questionable", "day-to-day"]:
            return "medium"
        return "low"

    async def _fetch_injury_updates(self) -> list[dict]:
        """Fetch latest injury updates"""
        # Mock data - replace with real injury API
        return [
            {
                "player_id": "judge_aaron",
                "player_name": "Aaron Judge",
                "team": "Yankees",
                "status": "Active",
                "injury_type": None,
            }
        ]


class WeatherEngine:
    """Monitors weather conditions and park factors"""

    def __init__(self, circuit_breaker: CircuitBreaker):
        """TODO: Add docstring for __init__"""

        self.cb = circuit_breaker
        self.weather_cache = {}

    async def check_weather(self) -> list[BettingAlert]:
        """Check weather conditions for games"""
        alerts = []

        if not self.cb.is_available():
            return alerts

        try:
            weather_data = await self._fetch_weather_data()

            for stadium, conditions in weather_data.items():
                # Calculate Run Environment Index (REI)
                rei = self._calculate_rei(conditions)

                if abs(
                    rei -
                    conditions.get(
                        "baseline_rei",
                        1.0)) > 0.15:  # 15% deviation
                    alert = BettingAlert(
                        type="weather_impact",
                        priority="medium",
                        message=f"Weather Impact at {stadium}: REI {
                            rei:.2f}",
                        data={
                            "stadium": stadium,
                            "conditions": conditions,
                            "rei": rei,
                            "recommendation": self._get_weather_recommendation(
                                conditions,
                                rei),
                        },
                        timestamp=datetime.now().isoformat(),
                    )
                    alerts.append(alert)

            self.cb.record_success()

        except Exception as e:
            logging.error(f"Weather engine error: {e}")
            self.cb.record_failure()

        return alerts

    def _calculate_rei(self, conditions: dict) -> float:
        """Calculate Run Environment Index based on weather"""
        base_rei = 1.0

        # Wind factor
        wind_speed = conditions.get("wind_speed_mph", 0)
        wind_direction = conditions.get("wind_direction", "calm")

        if wind_direction in ["out_to_c", "out_to_l", "out_to_rf"]:
            rei_adjustment = min(wind_speed * 0.02, 0.3)  # Max 30% boost
        elif wind_direction in ["in_from_c", "in_from_l", "in_from_rf"]:
            rei_adjustment = -min(wind_speed * 0.02, 0.25)  # Max 25% reduction
        else:
            rei_adjustment = 0

        # Temperature factor
        temp_f = conditions.get("temperature_f", 70)
        if temp_f > 80:
            rei_adjustment += (temp_f - 80) * 0.005  # Warmer = more runs
        elif temp_f < 50:
            rei_adjustment -= (50 - temp_f) * 0.008  # Colder = fewer runs

        return max(0.5, base_rei + rei_adjustment)  # Minimum REI of 0.5

    def _get_weather_recommendation(self, conditions: dict, rei: float) -> str:
        """Generate betting recommendation based on weather"""
        if rei > 1.15:
            return "Favor overs and HR props"
        if rei < 0.85:
            return "Favor unders and K props"
        return "Neutral weather impact"

    async def _fetch_weather_data(self) -> dict:
        """Fetch weather data for MLB stadiums"""
        # Mock weather data - replace with real weather API
        return {
            "Yankee Stadium": {
                "temperature_f": 72,
                "wind_speed_mph": 8,
                "wind_direction": "out_to_rf",
                "humidity": 45,
                "baseline_rei": 1.0,
            }
        }


class SGPBuilder:
    """Same Game Parlay builder with DraftKings rules awareness"""

    def __init__(self):
        """TODO: Add docstring for __init__"""

        self.dk_rules = self._load_dk_rules()

    def _load_dk_rules(self) -> dict:
        """Load DraftKings SGP correlation rules"""
        # Mock DK rules - replace with actual rule engine
        return {
            "allowed_correlations": [
                ["player_hr", "team_total_over"],
                ["pitcher_ks", "team_total_under"],
                ["player_hits", "player_rbi"],
            ],
            "forbidden_correlations": [
                ["pitcher_ks_over", "same_team_hits_over"],
                ["team_total_over", "opposing_pitcher_ks_over"],
            ],
            "max_legs": 5,
            "min_legs": 2,
        }

    async def build_sgp(self, game_data: dict) -> dict:
        """Build optimal SGP for given game"""
        # Mock SGP building logic
        return {
            "legs": [
                {
                    "type": "player_hr",
                    "player": "Aaron Judge",
                    "line": 0.5,
                    "pick": "over",
                },
                {"type": "team_total", "team": "Yankees", "line": 5.5, "pick": "over"},
                {
                    "type": "pitcher_ks",
                    "pitcher": "Gerrit Cole",
                    "line": 7.5,
                    "pick": "over",
                },
            ],
            "expected_odds": 650,
            "confidence": 0.68,
            "kelly_stake": 0.02,
        }


class BettingIntelligenceOrchestrator:
    """Main orchestrator for betting intelligence system"""

    def __init__(self):
        """TODO: Add docstring for __init__"""

        self.setup_logging()
        self.circuit_breaker = CircuitBreaker()
        self.lineup_watcher = LineupWatcher(self.circuit_breaker)
        self.injury_sentinel = InjurySentinel(self.circuit_breaker)
        self.weather_engine = WeatherEngine(self.circuit_breaker)
        self.sgp_builder = SGPBuilder()
        self.alerts = []

    def setup_logging(self):
        """Configure logging for the orchestrator"""
        log_dir = Path("logs/betting")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    log_dir /
                    f"betting_intelligence_{
                        datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler(),
            ],
        )

    async def run_intelligence_cycle(self):
        """Run one complete intelligence gathering cycle"""
        logging.info("Starting betting intelligence cycle")

        # Gather intelligence from all sources
        tasks = [
            self.lineup_watcher.check_lineups(),
            self.injury_sentinel.check_injuries(),
            self.weather_engine.check_weather(),
        ]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, list):
                    self.alerts.extend(result)
                elif isinstance(result, Exception):
                    logging.error(f"Intelligence cycle error: {result}")

            # Process high-priority alerts
            high_priority_alerts = [a for a in self.alerts if a.priority == "high"]
            if high_priority_alerts:
                await self.process_high_priority_alerts(high_priority_alerts)

            logging.info(
                f"Intelligence cycle complete. Generated {len(self.alerts)} alerts")

        except Exception as e:
            logging.error(f"Intelligence cycle failed: {e}")

    async def process_high_priority_alerts(self, alerts: list[BettingAlert]):
        """Process high-priority alerts immediately"""
        for alert in alerts:
            logging.warning(f"HIGH PRIORITY: {alert.message}")
            await self.save_alert(alert)
            # Here you would trigger notifications, automatic actions, etc.

    async def save_alert(self, alert: BettingAlert):
        """Save alert to disk for audit trail"""
        alerts_dir = Path("logs/betting/alerts")
        alerts_dir.mkdir(exist_ok=True)

        alert_file = (
            alerts_dir /
            f"alert_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}_{
                alert.type}.json")
        alert_file.write_text(json.dumps(asdict(alert), indent=2))

    async def run_continuous(self, interval_seconds: int = 300):
        """Run intelligence system continuously"""
        logging.info(
            f"Starting continuous betting intelligence (interval: {interval_seconds}s)")

        while True:
            try:
                await self.run_intelligence_cycle()

                # Clean old alerts (keep last 1000)
                if len(self.alerts) > 1000:
                    self.alerts = self.alerts[-1000:]

                await asyncio.sleep(interval_seconds)

            except KeyboardInterrupt:
                logging.info("Stopping betting intelligence system")
                break
            except Exception as e:
                logging.error(f"Continuous run error: {e}")
                await asyncio.sleep(60)  # Wait before retry


async def main():
    """Main entry point"""
    orchestrator = BettingIntelligenceOrchestrator()

    # Run one cycle for testing
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--test":
        await orchestrator.run_intelligence_cycle()
        print(f"Test complete. Generated {len(orchestrator.alerts)} alerts")
        return

    # Run continuous monitoring
    await orchestrator.run_continuous(interval_seconds=300)  # 5-minute cycles


if __name__ == "__main__":
    asyncio.run(main())
