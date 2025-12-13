#!/usr/bin/env python3
"""
EQ12 NBA CALENDAR INTEGRATION - October 4, 2025
Integrates NBA key dates, Emirates NBA Cup schedule, and season events
into EQ12 governance and automation systems

Key Features:
- NBA regular season schedule integration
- Emirates NBA Cup group play and playoff tracking
- Key dates automation and alerts
- Governance calendar synchronization
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

# Import NBA data integration
from eq12_nba_data_integration import NBADataIntegration, NBAKeyDate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EQ12CalendarEvent:
    """EQ12 calendar event with NBA integration"""

    event_id: str
    title: str
    date: datetime
    category: str
    description: str
    priority: str  # "high", "medium", "low"
    automation_triggers: list[str]  # EQ12 systems to trigger
    betting_relevance: bool = False
    source: str = "NBA.com"


class NBACalendarIntegration:
    """NBA calendar integration for EQ12 systems"""

    def __init__(self):
        self.nba_integration = NBADataIntegration()
        self.base_directory = Path("C:/EQ12")
        self.configs_dir = self.base_directory / "configs"
        self.logs_dir = self.base_directory / "logs"

        # Dunk Score tracking
        self.dunk_score_thresholds = {
            "legendary": 120.0,  # Legendary dunk worthy of special alerts
            "elite": 110.0,  # Elite dunk for high-priority tracking
            "highlight": 100.0,  # Highlight-worthy dunk for betting props
            "notable": 85.0,  # Notable dunk for general tracking
        }

        # Ensure directories exist
        self.configs_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # Calendar file paths
        self.calendar_file = self.configs_dir / "nba_calendar_2025_26.json"
        self.automation_config = self.configs_dir / "nba_automation_triggers.json"

    def fetch_and_integrate_nba_calendar(self) -> list[EQ12CalendarEvent]:
        """Fetch NBA key dates and convert to EQ12 calendar events"""
        logger.info("🏀 Fetching NBA calendar for EQ12 integration")

        try:
            # Get NBA key dates
            nba_key_dates = self.nba_integration.fetch_nba_key_dates()
            eq12_events = []

            for nba_date in nba_key_dates:
                # Convert to EQ12 calendar event
                eq12_event = self._convert_nba_date_to_eq12_event(nba_date)
                eq12_events.append(eq12_event)

            # Add dunk score calendar events
            dunk_score_events = self.create_dunk_score_calendar_events()
            eq12_events.extend(dunk_score_events)

            logger.info(
                f"✅ Integrated {len(eq12_events)} NBA events ({len(dunk_score_events)} dunk score) into EQ12 calendar"
            )
            return eq12_events

        except Exception as e:
            logger.error(f"❌ Error integrating NBA calendar: {e}")
            return []

    def _convert_nba_date_to_eq12_event(self, nba_date: NBAKeyDate) -> EQ12CalendarEvent:
        """Convert NBA key date to EQ12 calendar event with automation triggers"""

        # Determine priority based on event type
        priority = self._get_event_priority(nba_date)

        # Determine automation triggers
        automation_triggers = self._get_automation_triggers(nba_date)

        # Determine betting relevance
        betting_relevance = self._has_betting_relevance(nba_date)

        return EQ12CalendarEvent(
            event_id=f"nba_{nba_date.date.strftime('%Y%m%d')}_{nba_date.category}",
            title=nba_date.event,
            date=nba_date.date,
            category=nba_date.category,
            description=nba_date.description,
            priority=priority,
            automation_triggers=automation_triggers,
            betting_relevance=betting_relevance,
            source="NBA.com",
        )

    def _get_event_priority(self, nba_date: NBAKeyDate) -> str:
        """Determine event priority for EQ12 systems"""
        if nba_date.category in ["nba_cup", "playoffs", "all_star"]:
            return "high"
        if nba_date.category == "regular_season":
            if (
                "opens" in nba_date.event.lower()
                or "ends" in nba_date.event.lower()
                or (
                    "christmas" in nba_date.event.lower()
                    or "trade deadline" in nba_date.event.lower()
                )
            ):
                return "high"
            return "medium"
        if nba_date.category == "preseason":
            return "low"
        return "medium"

    def _get_automation_triggers(self, nba_date: NBAKeyDate) -> list[str]:
        """Determine which EQ12 systems should be triggered for this event"""
        triggers = []

        # Always trigger governance notifications
        triggers.append("eq12_governance_assistant")

        # Betting-related triggers
        if self._has_betting_relevance(nba_date):
            triggers.extend(
                [
                    "eq12_mega_parlay_builder",
                    "eq12_historical_odds_engine",
                    "eq12_enhanced_daily_parlay_system",
                ]
            )

        # Season milestones
        if "opens" in nba_date.event.lower() or "begins" in nba_date.event.lower():
            triggers.extend(["eq12_automation_bridge", "eq12_godstack_orchestrator"])

        # NBA Cup specific
        if nba_date.category == "nba_cup":
            triggers.append("eq12_nba_cup_tracker")  # Future system

        # Trade deadline
        if "trade deadline" in nba_date.event.lower():
            triggers.append("eq12_roster_analytics")  # Future system

        return triggers

    def _has_betting_relevance(self, nba_date: NBAKeyDate) -> bool:
        """Determine if event has betting relevance"""
        betting_keywords = [
            "opens",
            "begins",
            "cup",
            "championship",
            "playoffs",
            "christmas",
            "all-star",
            "trade deadline",
        ]

        event_text = nba_date.event.lower()
        return any(keyword in event_text for keyword in betting_keywords)

    def create_dunk_score_calendar_events(self) -> list[EQ12CalendarEvent]:
        """Generate calendar events for dunk score milestones and tracking"""
        events = []

        try:
            # Get current dunk score leaders
            dunk_scores = self.nba_integration.fetch_nba_dunk_scores(20)
            dunk_news = self.nba_integration.fetch_dunk_score_news()

            # Create milestone tracking events
            for threshold_name, threshold_value in self.dunk_score_thresholds.items():
                matching_dunks = [d for d in dunk_scores if d.dunk_score >= threshold_value]

                if matching_dunks:
                    event = EQ12CalendarEvent(
                        event_id=f"dunk_score_{threshold_name}_milestone",
                        title=f"NBA Dunk Score {threshold_name.title()} Milestone ({threshold_value}+)",
                        date=datetime.now() + timedelta(days=1),  # Daily check
                        category="dunk_score_tracking",
                        description=f"Monitor for {threshold_name} dunks ({threshold_value}+): {len(matching_dunks)} achieved",
                        priority=("high" if threshold_name in ["legendary", "elite"] else "medium"),
                        automation_triggers=[
                            "eq12_mega_parlay_builder",
                            "eq12_nba_game_monitor",
                            "eq12_dunk_score_alerts",  # Future system
                        ],
                        betting_relevance=True,
                        source="NBA Dunk Score Integration",
                    )
                    events.append(event)

            # Create player-specific dunk tracking events
            top_dunkers = {}
            for dunk in dunk_scores[:10]:  # Top 10 dunk scores
                player = dunk.player_name
                if player not in top_dunkers or dunk.dunk_score > top_dunkers[player]["best_score"]:
                    top_dunkers[player] = {
                        "team": dunk.team,
                        "best_score": dunk.dunk_score,
                        "opponent": dunk.opponent,
                        "game_date": dunk.game_date,
                    }

            for player, stats in top_dunkers.items():
                if stats["best_score"] >= self.dunk_score_thresholds["notable"]:
                    event = EQ12CalendarEvent(
                        event_id=f"dunk_tracker_{player.lower().replace(' ', '_')}",
                        title=f"{player} Dunk Score Tracking ({stats['team']})",
                        date=datetime.now() + timedelta(days=7),  # Weekly review
                        category="player_dunk_tracking",
                        description=f"Best score: {stats['best_score']:.1f} vs {stats['opponent']}. Track for betting opportunities.",
                        priority="medium" if stats["best_score"] >= 100 else "low",
                        automation_triggers=[
                            "eq12_mega_parlay_builder",
                            "eq12_player_props_optimizer",  # Future system
                        ],
                        betting_relevance=True,
                        source="NBA Dunk Score Player Tracking",
                    )
                    events.append(event)

            # Create dunk score news monitoring events
            if dunk_news:
                event = EQ12CalendarEvent(
                    event_id="dunk_score_news_update",
                    title="NBA Dunk Score News & Analysis Update",
                    date=datetime.now() + timedelta(days=3),  # Every 3 days
                    category="dunk_score_news",
                    description=f"Latest updates: {len(dunk_news)} news sources monitored including methodology changes",
                    priority="low",
                    automation_triggers=[
                        "eq12_nba_data_integration",
                        "eq12_news_aggregator",  # Future system
                    ],
                    betting_relevance=False,
                    source="NBA Dunk Score News Monitoring",
                )
                events.append(event)

            logger.info(f"Created {len(events)} dunk score calendar events")

        except Exception as e:
            logger.error(f"Error creating dunk score calendar events: {e}")

        return events

    def save_calendar_to_configs(self, events: list[EQ12CalendarEvent]) -> str:
        """Save NBA calendar to EQ12 configs directory"""
        calendar_data = {
            "generated_at": datetime.now().isoformat(),
            "source": "NBA.com Integration",
            "season": "2025-26",
            "events_count": len(events),
            "events": [asdict(event) for event in events],
        }

        # Convert datetime objects to ISO strings for JSON serialization
        for event_data in calendar_data["events"]:
            if isinstance(event_data["date"], datetime):
                event_data["date"] = event_data["date"].isoformat()

        with open(self.calendar_file, "w") as f:
            json.dump(calendar_data, f, indent=2, default=str)

        logger.info(f"💾 Saved NBA calendar to {self.calendar_file}")
        return str(self.calendar_file)

    def generate_automation_config(self, events: list[EQ12CalendarEvent]) -> str:
        """Generate automation configuration for EQ12 systems"""
        automation_config = {
            "generated_at": datetime.now().isoformat(),
            "description": "NBA automation triggers for EQ12 systems",
            "triggers": {},
            "schedules": [],
        }

        # Group events by trigger system
        for event in events:
            for trigger in event.automation_triggers:
                if trigger not in automation_config["triggers"]:
                    automation_config["triggers"][trigger] = []

                automation_config["triggers"][trigger].append(
                    {
                        "event_id": event.event_id,
                        "title": event.title,
                        "date": (
                            event.date.isoformat()
                            if isinstance(event.date, datetime)
                            else event.date
                        ),
                        "priority": event.priority,
                        "betting_relevance": event.betting_relevance,
                    }
                )

        # Add scheduled automation tasks
        automation_config["schedules"] = [
            {
                "task": "nba_daily_games_check",
                "system": "eq12_mega_parlay_builder",
                "frequency": "daily",
                "time": "14:00",  # 2 PM daily check
                "description": "Check for NBA games starting after 3 PM",
            },
            {
                "task": "nba_cup_monitoring",
                "system": "eq12_governance_assistant",
                "frequency": "weekly",
                "day": "friday",
                "time": "10:00",
                "description": "Monitor Emirates NBA Cup progress and betting opportunities",
            },
            {
                "task": "nba_stats_update",
                "system": "eq12_historical_odds_engine",
                "frequency": "daily",
                "time": "08:00",
                "description": "Update NBA player stats and team analytics",
            },
            {
                "task": "dunk_score_monitoring",
                "system": "eq12_nba_data_integration",
                "frequency": "daily",
                "time": "12:00",
                "description": "Monitor NBA dunk scores for betting opportunities and milestone alerts",
            },
            {
                "task": "dunk_score_leaderboard_update",
                "system": "eq12_mega_parlay_builder",
                "frequency": "hourly",
                "description": "Update dunk score leaderboard for prop betting optimization",
            },
        ]

        with open(self.automation_config, "w") as f:
            json.dump(automation_config, f, indent=2)

        logger.info(f"⚙️ Generated automation config at {self.automation_config}")
        return str(self.automation_config)

    def get_upcoming_nba_events(self, days: int = 30) -> list[EQ12CalendarEvent]:
        """Get upcoming NBA events in the next N days"""
        try:
            # Load calendar from file
            if not self.calendar_file.exists():
                logger.warning("NBA calendar not found, generating fresh calendar")
                events = self.fetch_and_integrate_nba_calendar()
                self.save_calendar_to_configs(events)
            else:
                with open(self.calendar_file) as f:
                    calendar_data = json.load(f)

                events = []
                for event_data in calendar_data["events"]:
                    event_data["date"] = datetime.fromisoformat(event_data["date"])
                    events.append(EQ12CalendarEvent(**event_data))

            # Filter to upcoming events
            now = datetime.now()
            future_date = now + timedelta(days=days)

            upcoming = [event for event in events if now <= event.date <= future_date]

            return sorted(upcoming, key=lambda x: x.date)

        except Exception as e:
            logger.error(f"Error getting upcoming NBA events: {e}")
            return []

    def get_todays_nba_events(self) -> list[EQ12CalendarEvent]:
        """Get today's NBA events"""
        return self.get_upcoming_nba_events(days=1)

    def create_governance_alerts(self, events: list[EQ12CalendarEvent]) -> dict:
        """Create governance alerts for high-priority NBA events"""
        alerts = {
            "generated_at": datetime.now().isoformat(),
            "high_priority_events": [],
            "betting_opportunities": [],
            "automation_reminders": [],
        }

        for event in events:
            if event.priority == "high":
                alerts["high_priority_events"].append(
                    {
                        "title": event.title,
                        "date": (
                            event.date.isoformat()
                            if isinstance(event.date, datetime)
                            else event.date
                        ),
                        "description": event.description,
                        "automation_triggers": event.automation_triggers,
                    }
                )

            if event.betting_relevance:
                alerts["betting_opportunities"].append(
                    {
                        "title": event.title,
                        "date": (
                            event.date.isoformat()
                            if isinstance(event.date, datetime)
                            else event.date
                        ),
                        "category": event.category,
                    }
                )

        # Save alerts
        alerts_file = (
            self.logs_dir / f"nba_governance_alerts_{datetime.now().strftime('%Y%m%d')}.json"
        )
        with open(alerts_file, "w") as f:
            json.dump(alerts, f, indent=2)

        logger.info(f"🚨 Generated governance alerts at {alerts_file}")
        return alerts

    def sync_with_eq12_governance(self) -> bool:
        """Sync NBA calendar with EQ12 governance systems"""
        try:
            logger.info("🔄 Syncing NBA calendar with EQ12 governance")

            # Fetch and save calendar
            events = self.fetch_and_integrate_nba_calendar()
            self.save_calendar_to_configs(events)

            # Generate automation config
            self.generate_automation_config(events)

            # Get upcoming events for alerts
            upcoming_events = self.get_upcoming_nba_events(days=14)  # Next 2 weeks

            # Create governance alerts
            self.create_governance_alerts(upcoming_events)

            logger.info("✅ NBA calendar sync with EQ12 governance complete")
            return True

        except Exception as e:
            logger.error(f"❌ Error syncing NBA calendar with governance: {e}")
            return False


def main():
    """Main function for NBA calendar integration"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 NBA Calendar Integration")
    parser.add_argument(
        "--sync", help="Sync NBA calendar with EQ12 governance", action="store_true"
    )
    parser.add_argument("--upcoming", type=int, default=14, help="Days ahead to check for events")
    parser.add_argument("--alerts", help="Generate governance alerts", action="store_true")
    parser.add_argument("--verbose", help="Verbose logging", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize NBA calendar integration
    calendar_integration = NBACalendarIntegration()

    if args.sync:
        success = calendar_integration.sync_with_eq12_governance()
        if success:
            print("✅ NBA calendar sync completed successfully")
        else:
            print("❌ NBA calendar sync failed")
            return 1

    # Show upcoming events
    upcoming_events = calendar_integration.get_upcoming_nba_events(days=args.upcoming)

    print(f"\n🏀 UPCOMING NBA EVENTS (Next {args.upcoming} days):")
    for event in upcoming_events:
        priority_emoji = (
            "🔴" if event.priority == "high" else "🟡" if event.priority == "medium" else "🟢"
        )
        betting_emoji = "💰" if event.betting_relevance else ""

        print(f"  {priority_emoji}{betting_emoji} {event.title}")
        print(f"     📅 {event.date.strftime('%Y-%m-%d')} | Category: {event.category}")
        print(f"     📝 {event.description}")
        if event.automation_triggers:
            print(
                f"     ⚙️ Triggers: {', '.join(event.automation_triggers[:3])}{'...' if len(event.automation_triggers) > 3 else ''}"
            )
        print()

    if args.alerts and upcoming_events:
        alerts = calendar_integration.create_governance_alerts(upcoming_events)
        print(f"🚨 Generated {len(alerts['high_priority_events'])} high-priority alerts")
        print(f"💰 Found {len(alerts['betting_opportunities'])} betting opportunities")

    print(f"\n📊 Total events found: {len(upcoming_events)}")
    return 0


if __name__ == "__main__":
    exit(main())
