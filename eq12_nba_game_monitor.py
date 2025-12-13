#!/usr/bin/env python3
"""
EQ12 NBA GAME STATE MONITOR - October 4, 2025
Real-time NBA game monitoring for live scores, betting lines, and parlay adjustments
Integrates with NBA.com live data and EQ12 parlay systems

Features:
- Live score tracking and game state monitoring
- Real-time betting line movement detection
- Automated parlay adjustment recommendations
- In-game betting opportunity alerts
- Performance analytics and trend detection
"""

import json
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

# Import NBA integration and EQ12 systems
from eq12_nba_data_integration import NBADataIntegration, NBAGame

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GameState(Enum):
    """NBA game states for monitoring"""

    SCHEDULED = "scheduled"
    PREGAME = "pregame"  # 30 minutes before tipoff
    LIVE = "live"  # Game in progress
    HALFTIME = "halftime"
    TIMEOUT = "timeout"
    FINAL = "final"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class BettingAlert(Enum):
    """Types of betting alerts"""

    LINE_MOVEMENT = "line_movement"
    LIVE_OPPORTUNITY = "live_opportunity"
    PARLAY_RISK = "parlay_risk"
    VALUE_BET = "value_bet"
    GAME_FLOW = "game_flow"


@dataclass
class LiveGameData:
    """Live NBA game data structure"""

    game_id: str
    home_team: str
    away_team: str
    game_state: GameState
    home_score: int = 0
    away_score: int = 0
    period: int = 1
    time_remaining: str = "12:00"
    last_updated: datetime = None

    # Betting data
    live_spread: float | None = None
    live_total: float | None = None
    live_home_ml: int | None = None
    live_away_ml: int | None = None

    # Analytics
    pace: float | None = None  # Possessions per 48 minutes
    lead_changes: int = 0
    largest_lead: int = 0
    momentum_indicator: str = "neutral"  # "home", "away", "neutral"


@dataclass
class BettingAlertData:
    """Betting alert data structure"""

    alert_id: str
    alert_type: BettingAlert
    game_id: str
    timestamp: datetime
    priority: str  # "high", "medium", "low"
    message: str
    data: dict
    action_required: bool = False


class NBAGameMonitor:
    """Real-time NBA game monitoring system"""

    def __init__(self):
        self.nba_integration = NBADataIntegration()
        self.base_directory = Path("C:/EQ12")
        self.logs_dir = self.base_directory / "logs"
        self.monitoring_active = False
        self.monitored_games: dict[str, LiveGameData] = {}
        self.alert_callbacks: list[Callable] = []
        self.update_interval = 30  # seconds

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)

        # Alert thresholds
        self.alert_thresholds = {
            "significant_line_movement": 2.0,  # Point movement threshold
            "total_movement": 5.0,  # Total line movement threshold
            "live_value_threshold": 0.05,  # 5% edge for live betting
            "momentum_shift_threshold": 10,  # Points for momentum detection
        }

        # Dunk Score monitoring thresholds
        self.dunk_score_thresholds = {
            "legendary_dunk": 120.0,
            "elite_dunk": 110.0,
            "highlight_dunk": 100.0,
            "notable_dunk": 85.0,
        }

        # Track dunk events during games
        self.game_dunk_tracking: dict[str, list[dict]] = {}

    def add_alert_callback(self, callback: Callable):
        """Add callback function for betting alerts"""
        self.alert_callbacks.append(callback)

    def start_monitoring(self, games: list[NBAGame] | None = None):
        """Start monitoring NBA games"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        logger.info("🏀 Starting NBA game monitoring")
        self.monitoring_active = True

        # Get games to monitor
        if not games:
            games = self.nba_integration.get_todays_games()

        # Initialize game data
        for game in games:
            live_data = LiveGameData(
                game_id=game.game_id,
                home_team=game.home_team,
                away_team=game.away_team,
                game_state=GameState.SCHEDULED,
                last_updated=datetime.now(),
            )
            self.monitored_games[game.game_id] = live_data

        logger.info(f"📊 Monitoring {len(self.monitored_games)} NBA games")

        # Start monitoring loop in background thread
        monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitoring_thread.start()

    def monitor_dunk_scores(self, game_data: LiveGameData):
        """Monitor and alert on significant dunk scores during live games"""
        try:
            # Simulate dunk score detection (in production: real-time NBA data)
            if game_data.game_state == GameState.LIVE and random.random() < 0.15:
                # Get current dunk score leaders for context
                current_leaders = self.nba_integration.fetch_nba_dunk_scores(5)

                # Simulate a dunk occurring
                dunk_event = self._simulate_live_dunk(game_data, current_leaders)

                if dunk_event:
                    # Track dunk in game history
                    if game_data.game_id not in self.game_dunk_tracking:
                        self.game_dunk_tracking[game_data.game_id] = []

                    self.game_dunk_tracking[game_data.game_id].append(dunk_event)

                    # Generate alerts for significant dunks
                    if dunk_event["dunk_score"] >= self.dunk_score_thresholds["notable_dunk"]:
                        self._generate_dunk_alert(game_data, dunk_event)

        except Exception as e:
            logger.error(f"Error monitoring dunk scores: {e}")

    def _simulate_live_dunk(self, game_data: LiveGameData, current_leaders) -> dict:
        """Simulate a live dunk event with realistic dunk score"""
        import random

        # Generate realistic dunk score components
        jump_score = random.uniform(60, 95)
        power_score = random.uniform(55, 98)
        style_score = random.uniform(45, 100)
        contest_score = random.uniform(0, 100)

        # Calculate composite dunk score
        dunk_score = (jump_score + power_score + style_score + contest_score) / 4

        # Add randomness for spectacular dunks
        if random.random() < 0.1:  # 10% chance of spectacular dunk
            dunk_score += random.uniform(10, 25)

        return {
            "timestamp": datetime.now().isoformat(),
            "player": random.choice(["Anthony Edwards", "Nikola Jokic", "Jamal Murray"]),
            "team": random.choice([game_data.home_team, game_data.away_team]),
            "dunk_score": round(dunk_score, 1),
            "jump_score": round(jump_score, 1),
            "power_score": round(power_score, 1),
            "style_score": round(style_score, 1),
            "contest_score": round(contest_score, 1),
            "game_period": game_data.period,
            "dunk_type": random.choice(["poster", "alley-oop", "breakaway", "windmill"]),
        }

    def _generate_dunk_alert(self, game_data: LiveGameData, dunk_event: dict):
        """Generate betting alert for significant dunk scores"""
        dunk_score = dunk_event["dunk_score"]

        if dunk_score >= self.dunk_score_thresholds["legendary_dunk"]:
            alert_type = "LEGENDARY DUNK"
            priority = "critical"
        elif dunk_score >= self.dunk_score_thresholds["elite_dunk"]:
            alert_type = "ELITE DUNK"
            priority = "high"
        elif dunk_score >= self.dunk_score_thresholds["highlight_dunk"]:
            alert_type = "HIGHLIGHT DUNK"
            priority = "medium"
        else:
            alert_type = "NOTABLE DUNK"
            priority = "low"

        alert = BettingAlert(
            alert_id=f"{game_data.game_id}_dunk_{int(time.time())}",
            game_id=game_data.game_id,
            alert_type=alert_type,
            priority=priority,
            timestamp=datetime.now(),
            message=f"{alert_type}: {dunk_event['player']} - Score: {dunk_score}",
            betting_data={
                "dunk_score": dunk_score,
                "player": dunk_event["player"],
                "team": dunk_event["team"],
                "dunk_type": dunk_event["dunk_type"],
            },
        )

        # Send alert to all callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

        logger.info(f"🚨 {alert_type}: {dunk_event['player']} - {dunk_score}")

    def stop_monitoring(self):
        """Stop monitoring NBA games"""
        logger.info("⏹️ Stopping NBA game monitoring")
        self.monitoring_active = False

    def _monitoring_loop(self):
        """Main monitoring loop (runs in background thread)"""
        while self.monitoring_active:
            try:
                self._update_all_games()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Short delay before retrying

    def _update_all_games(self):
        """Update all monitored games"""
        for game_id, game_data in self.monitored_games.items():
            try:
                self._update_game_data(game_data)
            except Exception as e:
                logger.error(f"Error updating game {game_id}: {e}")

    def _update_game_data(self, game_data: LiveGameData):
        """Update individual game data and check for alerts"""
        # Simulate live data updates (in production, this would fetch from NBA API)
        previous_data = asdict(game_data)

        # Update game state based on current time and game schedule
        self._update_game_state(game_data)

        # Update live scores (simulated for demo)
        if game_data.game_state == GameState.LIVE:
            self._simulate_live_score_update(game_data)

        # Update betting lines (simulated)
        self._simulate_betting_line_updates(game_data)

        # Check for alerts
        self._check_for_alerts(game_data, previous_data)

        game_data.last_updated = datetime.now()

    def _update_game_state(self, game_data: LiveGameData):
        """Update game state based on current time"""
        now = datetime.now()

        # For demo purposes, simulate game progression based on time
        # In production, this would come from NBA API

        if game_data.game_state == GameState.SCHEDULED:
            # Check if game should be starting (for demo, start games after 3 PM)
            if now.hour >= 15:  # 3 PM
                game_data.game_state = GameState.PREGAME

        elif game_data.game_state == GameState.PREGAME:
            # Start game after a few minutes in pregame
            if now.minute % 10 == 0:  # Demo: start every 10 minutes
                game_data.game_state = GameState.LIVE
                game_data.period = 1
                game_data.time_remaining = "12:00"

    def _simulate_live_score_update(self, game_data: LiveGameData):
        """Simulate live score updates (replace with real NBA API in production)"""
        import random

        # Randomly update scores to simulate live action
        if random.random() < 0.3:  # 30% chance of scoring
            if random.random() < 0.5:
                game_data.home_score += random.choice([1, 2, 3])  # 1, 2, or 3 points
            else:
                game_data.away_score += random.choice([1, 2, 3])

        # Update time remaining (simplified)
        if game_data.time_remaining and ":" in game_data.time_remaining:
            minutes, seconds = map(int, game_data.time_remaining.split(":"))
            total_seconds = minutes * 60 + seconds - 30  # Subtract 30 seconds per update

            if total_seconds <= 0:
                if game_data.period < 4:
                    game_data.period += 1
                    game_data.time_remaining = "12:00"
                else:
                    game_data.game_state = GameState.FINAL
                    game_data.time_remaining = "00:00"
            else:
                new_minutes = total_seconds // 60
                new_seconds = total_seconds % 60
                game_data.time_remaining = f"{new_minutes}:{new_seconds:02d}"

    def _simulate_betting_line_updates(self, game_data: LiveGameData):
        """Simulate betting line movements (replace with real sportsbook APIs)"""
        import random

        # Simulate line movements based on score differential
        if game_data.game_state == GameState.LIVE:
            score_diff = game_data.home_score - game_data.away_score

            # Adjust spread based on score differential
            if game_data.live_spread is None:
                game_data.live_spread = -3.5  # Starting spread

            # Simulate line movement
            if abs(score_diff) > 10:  # Significant lead
                movement = random.uniform(-1.5, 1.5)
                game_data.live_spread += movement

            # Simulate total line adjustment
            if game_data.live_total is None:
                game_data.live_total = 218.5

            # Adjust total based on pace
            total_score = game_data.home_score + game_data.away_score
            if total_score > 0 and game_data.period > 0:
                projected_total = (total_score / game_data.period) * 4
                if abs(projected_total - game_data.live_total) > 10:
                    adjustment = random.uniform(-2.5, 2.5)
                    game_data.live_total += adjustment

    def _check_for_alerts(self, game_data: LiveGameData, previous_data: dict):
        """Check for betting alerts based on game updates"""
        alerts = []

        # Check for significant line movements
        if (
            game_data.live_spread
            and previous_data.get("live_spread")
            and abs(game_data.live_spread - previous_data["live_spread"])
            >= self.alert_thresholds["significant_line_movement"]
        ):
            alert = BettingAlertData(
                alert_id=f"{game_data.game_id}_line_movement_{int(time.time())}",
                alert_type=BettingAlert.LINE_MOVEMENT,
                game_id=game_data.game_id,
                timestamp=datetime.now(),
                priority="high",
                message=f"Significant spread movement in {game_data.away_team} @ {game_data.home_team}: {previous_data['live_spread']} → {game_data.live_spread}",
                data={
                    "old_spread": previous_data["live_spread"],
                    "new_spread": game_data.live_spread,
                    "movement": game_data.live_spread - previous_data["live_spread"],
                },
                action_required=True,
            )
            alerts.append(alert)

        # Check for live betting opportunities
        if game_data.game_state == GameState.LIVE:
            score_diff = abs(game_data.home_score - game_data.away_score)
            if score_diff > 15 and game_data.period <= 3:  # Large lead, game not over
                alert = BettingAlertData(
                    alert_id=f"{game_data.game_id}_live_opp_{int(time.time())}",
                    alert_type=BettingAlert.LIVE_OPPORTUNITY,
                    game_id=game_data.game_id,
                    timestamp=datetime.now(),
                    priority="medium",
                    message=f"Live betting opportunity in {game_data.away_team} @ {game_data.home_team}: Large lead ({score_diff} points) in period {game_data.period}",
                    data={
                        "score_differential": score_diff,
                        "period": game_data.period,
                        "home_score": game_data.home_score,
                        "away_score": game_data.away_score,
                    },
                )
                alerts.append(alert)

        # Trigger alerts
        for alert in alerts:
            self._trigger_alert(alert)

    def _trigger_alert(self, alert: BettingAlertData):
        """Trigger betting alert and call callbacks"""
        logger.info(f"🚨 BETTING ALERT: {alert.message}")

        # Save alert to log file
        alert_log = self.logs_dir / f"nba_betting_alerts_{datetime.now().strftime('%Y%m%d')}.json"

        alert_data = asdict(alert)
        alert_data["timestamp"] = alert.timestamp.isoformat()

        # Append to daily alert log
        alerts_list = []
        if alert_log.exists():
            with open(alert_log) as f:
                try:
                    alerts_list = json.load(f)
                except json.JSONDecodeError:
                    alerts_list = []

        alerts_list.append(alert_data)

        with open(alert_log, "w") as f:
            json.dump(alerts_list, f, indent=2)

        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def get_monitored_games_status(self) -> dict:
        """Get status of all monitored games"""
        status = {
            "monitoring_active": self.monitoring_active,
            "games_count": len(self.monitored_games),
            "last_updated": datetime.now().isoformat(),
            "games": [],
        }

        for game_data in self.monitored_games.values():
            game_status = {
                "game_id": game_data.game_id,
                "matchup": f"{game_data.away_team} @ {game_data.home_team}",
                "state": game_data.game_state.value,
                "score": f"{game_data.away_score} - {game_data.home_score}",
                "period": game_data.period,
                "time_remaining": game_data.time_remaining,
                "live_spread": game_data.live_spread,
                "live_total": game_data.live_total,
            }
            status["games"].append(game_status)

        return status

    def get_live_betting_recommendations(self) -> list[dict]:
        """Generate live betting recommendations based on current game states"""
        recommendations = []

        for game_data in self.monitored_games.values():
            if game_data.game_state == GameState.LIVE:
                rec = self._analyze_live_betting_opportunity(game_data)
                if rec:
                    recommendations.append(rec)

        return recommendations

    def _analyze_live_betting_opportunity(self, game_data: LiveGameData) -> dict | None:
        """Analyze individual game for live betting opportunities"""
        score_diff = game_data.home_score - game_data.away_score
        game_data.home_score + game_data.away_score

        recommendations = []

        # Analyze spread opportunities
        if game_data.live_spread and abs(score_diff) != abs(game_data.live_spread):
            spread_value = abs(score_diff) - abs(game_data.live_spread)
            if abs(spread_value) > 3:  # Significant difference
                recommendation = {
                    "game": f"{game_data.away_team} @ {game_data.home_team}",
                    "bet_type": "spread",
                    "recommendation": "home" if spread_value > 0 else "away",
                    "live_line": game_data.live_spread,
                    "current_diff": score_diff,
                    "value": abs(spread_value),
                    "period": game_data.period,
                    "confidence": min(90, 60 + abs(spread_value) * 5),  # Cap at 90%
                }
                recommendations.append(recommendation)

        if recommendations:
            return {"game_id": game_data.game_id, "recommendations": recommendations}

        return None


def example_alert_callback(alert: BettingAlertData):
    """Example callback function for betting alerts"""
    print(f"📱 ALERT CALLBACK: {alert.alert_type.value.upper()}")
    print(f"   Game: {alert.game_id}")
    print(f"   Message: {alert.message}")
    print(f"   Priority: {alert.priority}")
    print(f"   Action Required: {alert.action_required}")
    print()


def main():
    """Main function for NBA game monitoring"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 NBA Game State Monitor")
    parser.add_argument("--monitor", help="Start monitoring today's games", action="store_true")
    parser.add_argument("--status", help="Show monitoring status", action="store_true")
    parser.add_argument(
        "--recommendations",
        help="Get live betting recommendations",
        action="store_true",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=300,
        help="Monitoring duration in seconds (default: 300)",
    )
    parser.add_argument("--verbose", help="Verbose logging", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize NBA game monitor
    monitor = NBAGameMonitor()

    # Add example callback
    monitor.add_alert_callback(example_alert_callback)

    if args.monitor:
        print("🏀 Starting NBA game monitoring...")

        # Get ONLY the target games we want to monitor
        target_games = monitor.nba_integration.get_target_games_only()

        if not target_games:
            print("⚠️ Target NBA games not found for today")
            print("   Looking for:")
            print("   • Orlando Magic @ Miami Heat")
            print("   • Minnesota Timberwolves @ Denver Nuggets")
            return 1

        print(f"🎯 Monitoring {len(target_games)} TARGET NBA games:")
        for game in target_games:
            print(f"   🏀 {game.away_team} @ {game.home_team}")
            print(f"      ⏰ {game.game_time.strftime('%H:%M')} ET")
            if hasattr(game, "spread_line") and game.spread_line:
                print(f"      💰 Spread: {game.spread_line}, O/U: {game.total_line}")

        # Use target games for monitoring
        today_games = target_games

        # Start monitoring
        monitor.start_monitoring(today_games)

        try:
            print(f"⏱️ Monitoring for {args.duration} seconds... (Ctrl+C to stop)")
            time.sleep(args.duration)
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring interrupted by user")
        finally:
            monitor.stop_monitoring()

    if args.status:
        status = monitor.get_monitored_games_status()
        print("\n📊 NBA MONITORING STATUS:")
        print(f"   Active: {'✅' if status['monitoring_active'] else '❌'}")
        print(f"   Games: {status['games_count']}")

        if status["games"]:
            print("\n🏀 MONITORED GAMES:")
            for game in status["games"]:
                state_emoji = {"live": "🔴", "final": "✅", "scheduled": "🟡"}.get(
                    game["state"], "⚪"
                )
                print(f"   {state_emoji} {game['matchup']}")
                print(
                    f"     Score: {game['score']} | Period: {game['period']} | Time: {game['time_remaining']}"
                )
                if game["live_spread"]:
                    print(
                        f"     Live Spread: {game['live_spread']} | Live Total: {game['live_total']}"
                    )

    if args.recommendations:
        recommendations = monitor.get_live_betting_recommendations()
        print("\n💡 LIVE BETTING RECOMMENDATIONS:")

        if not recommendations:
            print("   No live betting opportunities found")
        else:
            for game_rec in recommendations:
                print(f"\n🏀 {game_rec['game_id']}")
                for rec in game_rec["recommendations"]:
                    confidence_emoji = (
                        "🟢" if rec["confidence"] > 75 else "🟡" if rec["confidence"] > 60 else "🔴"
                    )
                    print(
                        f"   {confidence_emoji} {rec['bet_type'].upper()}: Bet {rec['recommendation']}"
                    )
                    print(
                        f"     Live Line: {rec['live_line']} | Current Diff: {rec['current_diff']}"
                    )
                    print(f"     Value: {rec['value']} | Confidence: {rec['confidence']}%")

    return 0


if __name__ == "__main__":
    exit(main())
