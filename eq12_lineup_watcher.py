#!/usr/bin/env python3
"""
EQ12 MLB Playoffs Lineup & Pitching Watcher
==========================================
Real-time monitoring for playoff edges:
- LINEUP_CONFIRMED, PITCHER_CHANGE, LATE_SCRATCH events
- ROOF_STATUS, WIND_ALERT for weather-sensitive props
- Auto prop voiding and bullpen leverage adjustments
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import aiohttp
import websockets


class EventType(Enum):
    LINEUP_CONFIRMED = "LINEUP_CONFIRMED"
    PITCHER_CHANGE = "PITCHER_CHANGE"
    LATE_SCRATCH = "LATE_SCRATCH"
    ROOF_STATUS = "ROOF_STATUS"
    WIND_ALERT = "WIND_ALERT"
    BULLPEN_LEVERAGE = "BULLPEN_LEVERAGE"


@dataclass
class LineupEvent:
    event_type: EventType
    game_pk: str
    timestamp: datetime
    team: str
    details: dict[str, Any]
    action_required: list[str]  # What SGPs/props need adjustment
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL


class MLBPlayoffWatcher:
    """Real-time playoff lineup and pitching intelligence"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()

        # API endpoints
        self.mlb_base = "https://statsapi.mlb.com/api/v1"
        self.weather_api = "https://api.weather.gov"  # Real-time weather

        # Event tracking
        self.active_games = {}
        self.lineup_states = {}
        self.event_log = []
        self.alert_thresholds = {
            "wind_speed_mph": 12,
            "precipitation_chance": 30,
            "pitcher_change_hours": 2.0,
            "scratch_urgency_minutes": 120,
        }

        # Dashboard connection
        self.dashboard_ws = None

    def setup_logging(self):
        """Setup logging for playoff operations"""
        log_dir = r"C:\EQ12\logs"
        os.makedirs(log_dir, exist_ok=True)

        # Main log
        log_file = os.path.join(
            log_dir, f"mlb_playoff_watcher_{datetime.now().strftime('%Y%m%d')}.log"
        )

        # Events log (JSONL format)
        self.events_log_file = os.path.join(log_dir, "lineup_events.jsonl")

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )

    async def get_playoff_games(self) -> list[dict]:
        """Get today's playoff games"""
        async with aiohttp.ClientSession() as session:
            date = datetime.now().strftime("%Y-%m-%d")

            params = {
                "date": date,
                "sportId": 1,  # MLB
                "gameTypes": "P,F,D,L,W",  # Playoff game types
                "hydrate": "team,linescore,probablePitcher,weather",
            }

            try:
                async with session.get(f"{self.mlb_base}/schedule", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        games = []

                        for date_entry in data.get("dates", []):
                            for game in date_entry.get("games", []):
                                # Only playoff games
                                if game.get("gameType") in ["P", "F", "D", "L", "W"]:
                                    games.append(game)

                        self.logger.info(f"🏆 Found {len(games)} playoff games today")
                        return games
                    self.logger.error(f"Failed to fetch playoff schedule: {response.status}")
                    return []

            except Exception as e:
                self.logger.error(f"Error fetching playoff games: {e}")
                return []

    async def monitor_lineup_changes(self, game_pk: str):
        """Monitor single game for lineup/pitcher changes"""
        last_lineup_hash = None
        last_pitcher_hash = None

        while True:
            try:
                # Get live feed
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.mlb_base}/game/{game_pk}/feed/live") as response:
                        if response.status != 200:
                            await asyncio.sleep(30)
                            continue

                        feed_data = await response.json()

                # Check lineup changes
                await self._check_lineup_changes(game_pk, feed_data, last_lineup_hash)

                # Check pitcher changes
                await self._check_pitcher_changes(game_pk, feed_data, last_pitcher_hash)

                # Check weather alerts
                await self._check_weather_alerts(game_pk, feed_data)

                # Update hashes
                current_lineup = self._extract_lineup_hash(feed_data)
                current_pitcher = self._extract_pitcher_hash(feed_data)

                if current_lineup != last_lineup_hash:
                    last_lineup_hash = current_lineup

                if current_pitcher != last_pitcher_hash:
                    last_pitcher_hash = current_pitcher

                # Smart polling based on game state
                game_time = feed_data.get("gameData", {}).get("datetime", {}).get("dateTime")
                if game_time:
                    game_dt = datetime.fromisoformat(game_time.replace("Z", "+00:00"))
                    time_to_game = (game_dt - datetime.now(UTC)).total_seconds() / 3600

                    if time_to_game > 3:
                        await asyncio.sleep(300)  # 5 minutes
                    elif time_to_game > 1:
                        await asyncio.sleep(60)  # 1 minute
                    elif time_to_game > 0:
                        await asyncio.sleep(15)  # 15 seconds
                    else:
                        await asyncio.sleep(30)  # During game
                else:
                    await asyncio.sleep(60)  # Default

            except Exception as e:
                self.logger.error(f"Error monitoring game {game_pk}: {e}")
                await asyncio.sleep(60)

    async def _check_lineup_changes(self, game_pk: str, feed_data: dict, last_hash: str):
        """Check for lineup confirmations or late scratches"""
        try:
            teams = feed_data.get("liveData", {}).get("boxscore", {}).get("teams", {})

            for side in ["home", "away"]:
                team_data = teams.get(side, {})
                if not team_data:
                    continue

                team_name = team_data.get("team", {}).get("name", "")
                batters = team_data.get("batters", [])

                # Count confirmed batters (with batting order)
                confirmed_batters = 0
                for batter_id in batters:
                    batter_info = (
                        feed_data.get("liveData", {})
                        .get("boxscore", {})
                        .get("players", {})
                        .get(f"ID{batter_id}", {})
                    )
                    if (
                        batter_info.get("battingOrder")
                        and 101 <= batter_info.get("battingOrder") <= 109
                    ):
                        confirmed_batters += 1

                # Lineup confirmed event
                if confirmed_batters == 9:
                    event = LineupEvent(
                        event_type=EventType.LINEUP_CONFIRMED,
                        game_pk=game_pk,
                        timestamp=datetime.now(UTC),
                        team=team_name,
                        details={
                            "confirmed_batters": confirmed_batters,
                            "batting_orders": [
                                101,
                                102,
                                103,
                                104,
                                105,
                                106,
                                107,
                                108,
                                109,
                            ],
                            "lineup_finalized": True,
                        },
                        action_required=[
                            "Finalize batter props for confirmed lineup",
                            "Lock team total adjustments",
                            "Enable SGP building for this team",
                        ],
                        severity="MEDIUM",
                    )

                    await self._emit_event(event)

        except Exception as e:
            self.logger.error(f"Error checking lineup changes: {e}")

    async def _check_pitcher_changes(self, game_pk: str, feed_data: dict, last_hash: str):
        """Check for starting pitcher changes"""
        try:
            # Get probable vs actual starters
            probable_pitchers = feed_data.get("gameData", {}).get("probablePitchers", {})
            actual_pitchers = feed_data.get("liveData", {}).get("boxscore", {}).get("teams", {})

            for side in ["home", "away"]:
                probable_sp = probable_pitchers.get(side, {})
                actual_team = actual_pitchers.get(side, {})

                if not probable_sp or not actual_team:
                    continue

                probable_name = probable_sp.get("fullName", "")

                # Get actual starting pitcher from pitchers list
                pitchers = actual_team.get("pitchers", [])
                if pitchers:
                    actual_sp_id = pitchers[0]  # First pitcher is starter
                    actual_sp_info = (
                        feed_data.get("liveData", {})
                        .get("boxscore", {})
                        .get("players", {})
                        .get(f"ID{actual_sp_id}", {})
                    )
                    actual_name = actual_sp_info.get("person", {}).get("fullName", "")

                    # Pitcher change detected
                    if probable_name and actual_name and probable_name != actual_name:
                        team_name = actual_team.get("team", {}).get("name", "")

                        event = LineupEvent(
                            event_type=EventType.PITCHER_CHANGE,
                            game_pk=game_pk,
                            timestamp=datetime.now(UTC),
                            team=team_name,
                            details={
                                "original_pitcher": probable_name,
                                "new_pitcher": actual_name,
                                "change_reason": "TBD - check injury reports",
                                "pitcher_id": actual_sp_id,
                            },
                            action_required=[
                                f"VOID all {probable_name} strikeout props",
                                f"Reprice game total with {actual_name}",
                                "Update bullpen leverage (starter change)",
                                "Rebuild affected SGPs immediately",
                            ],
                            severity="HIGH",
                        )

                        await self._emit_event(event)

        except Exception as e:
            self.logger.error(f"Error checking pitcher changes: {e}")

    async def _check_weather_alerts(self, game_pk: str, feed_data: dict):
        """Monitor weather conditions for prop adjustments"""
        try:
            weather = feed_data.get("gameData", {}).get("weather", {})
            venue = feed_data.get("gameData", {}).get("venue", {})

            if not weather:
                return

            temp = weather.get("temp")
            wind_speed = weather.get("wind", "").split()[0] if weather.get("wind") else "0"
            wind_direction = weather.get("wind", "")
            weather.get("condition", "")

            try:
                wind_speed_num = float(wind_speed)
            except (ValueError, TypeError):
                wind_speed_num = 0

            # Wind alert for HR/TB props
            if wind_speed_num >= self.alert_thresholds["wind_speed_mph"]:
                event = LineupEvent(
                    event_type=EventType.WIND_ALERT,
                    game_pk=game_pk,
                    timestamp=datetime.now(UTC),
                    team="Both Teams",
                    details={
                        "wind_speed": wind_speed_num,
                        "wind_direction": wind_direction,
                        "temperature": temp,
                        "venue": venue.get("name", ""),
                        "roof_type": venue.get("roofType", "Open"),
                    },
                    action_required=[
                        f"Adjust HR props for {wind_speed_num} mph wind",
                        "Total Bases lines need wind factor",
                        f"Game total may be affected ({wind_direction})",
                        "Power stack risk assessment needed",
                    ],
                    severity="MEDIUM" if wind_speed_num < 18 else "HIGH",
                )

                await self._emit_event(event)

            # Roof status for indoor/outdoor variance
            roof_type = venue.get("roofType", "Open")
            if "Dome" in roof_type or "Retractable" in roof_type:
                event = LineupEvent(
                    event_type=EventType.ROOF_STATUS,
                    game_pk=game_pk,
                    timestamp=datetime.now(UTC),
                    team="Both Teams",
                    details={
                        "roof_type": roof_type,
                        "venue": venue.get("name", ""),
                        "weather_controlled": True,
                        "temperature": temp,
                    },
                    action_required=[
                        "Apply indoor park factors to HR props",
                        "Stable conditions favor consistent totals",
                        "Wind eliminated - standard prop lines",
                    ],
                    severity="LOW",
                )

                await self._emit_event(event)

        except Exception as e:
            self.logger.error(f"Error checking weather alerts: {e}")

    def _extract_lineup_hash(self, feed_data: dict) -> str:
        """Create hash of current lineup state"""
        try:
            teams = feed_data.get("liveData", {}).get("boxscore", {}).get("teams", {})
            lineup_data = {}

            for side in ["home", "away"]:
                team_data = teams.get(side, {})
                batters = team_data.get("batters", [])

                team_lineup = []
                for batter_id in batters:
                    batter_info = (
                        feed_data.get("liveData", {})
                        .get("boxscore", {})
                        .get("players", {})
                        .get(f"ID{batter_id}", {})
                    )
                    batting_order = batter_info.get("battingOrder")
                    name = batter_info.get("person", {}).get("fullName", "")

                    if batting_order and name:
                        team_lineup.append(f"{batting_order}:{name}")

                lineup_data[side] = sorted(team_lineup)

            return str(hash(str(lineup_data)))

        except Exception:
            return ""

    def _extract_pitcher_hash(self, feed_data: dict) -> str:
        """Create hash of current pitcher assignments"""
        try:
            probable = feed_data.get("gameData", {}).get("probablePitchers", {})
            actual = feed_data.get("liveData", {}).get("boxscore", {}).get("teams", {})

            pitcher_data = {}
            for side in ["home", "away"]:
                prob_sp = probable.get(side, {}).get("fullName", "")

                actual_pitchers = actual.get(side, {}).get("pitchers", [])
                actual_sp = ""
                if actual_pitchers:
                    sp_id = actual_pitchers[0]
                    sp_info = (
                        feed_data.get("liveData", {})
                        .get("boxscore", {})
                        .get("players", {})
                        .get(f"ID{sp_id}", {})
                    )
                    actual_sp = sp_info.get("person", {}).get("fullName", "")

                pitcher_data[side] = {"probable": prob_sp, "actual": actual_sp}

            return str(hash(str(pitcher_data)))

        except Exception:
            return ""

    async def _emit_event(self, event: LineupEvent):
        """Emit event to logs and dashboard"""
        try:
            # Log to JSONL file
            event_json = json.dumps({**asdict(event), "timestamp": event.timestamp.isoformat()})

            with open(self.events_log_file, "a") as f:
                f.write(event_json + "\n")

            # Add to memory log
            self.event_log.append(event)

            # Log to console
            severity_emoji = {"LOW": "ℹ️", "MEDIUM": "⚠️", "HIGH": "🚨", "CRITICAL": "🔥"}

            emoji = severity_emoji.get(event.severity, "📊")
            self.logger.info(
                f"{emoji} {event.event_type.value}: {event.team} - {len(event.action_required)} actions required"
            )

            for action in event.action_required:
                self.logger.info(f"  → {action}")

            # Send to dashboard WebSocket (if connected)
            if self.dashboard_ws:
                await self._send_to_dashboard(event)

        except Exception as e:
            self.logger.error(f"Error emitting event: {e}")

    async def _send_to_dashboard(self, event: LineupEvent):
        """Send event to dashboard WebSocket"""
        try:
            dashboard_msg = {
                "type": "lineup_event",
                "data": {**asdict(event), "timestamp": event.timestamp.isoformat()},
            }

            await self.dashboard_ws.send(json.dumps(dashboard_msg))

        except Exception as e:
            self.logger.warning(f"Could not send to dashboard: {e}")

    async def connect_dashboard(self, ws_url: str = "ws://localhost:3000/ws"):
        """Connect to dashboard WebSocket"""
        try:
            self.dashboard_ws = await websockets.connect(ws_url)
            self.logger.info(f"✅ Connected to dashboard at {ws_url}")

        except Exception as e:
            self.logger.warning(f"Could not connect to dashboard: {e}")

    async def run_playoff_monitoring(self):
        """Main monitoring loop for playoffs"""
        self.logger.info("🏆 Starting MLB Playoff Lineup & Pitching Watcher")

        # Connect to dashboard
        await self.connect_dashboard()

        # Get playoff games
        playoff_games = await self.get_playoff_games()

        if not playoff_games:
            self.logger.warning("No playoff games found for today")
            return

        # Start monitoring tasks
        tasks = []
        for game in playoff_games:
            game_pk = game["gamePk"]
            home_team = game["teams"]["home"]["team"]["name"]
            away_team = game["teams"]["away"]["team"]["name"]

            self.logger.info(f"🔍 Starting monitoring: {away_team} @ {home_team} (Game {game_pk})")

            task = asyncio.create_task(self.monitor_lineup_changes(game_pk))
            tasks.append(task)

        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            self.logger.info("🛑 Monitoring stopped by user")
        finally:
            if self.dashboard_ws:
                await self.dashboard_ws.close()


async def main():
    """Run playoff watcher"""
    watcher = MLBPlayoffWatcher()
    await watcher.run_playoff_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
