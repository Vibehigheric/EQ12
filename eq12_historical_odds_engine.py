#!/usr/bin/env python3
"""
EQ12 Historical Odds Data Engine
Enhanced sports betting analysis using The Odds API v4 historical data endpoints

This module integrates with The Odds API historical endpoints to:
- Fetch historical event odds and outcomes
- Analyze line movement patterns over time
- Build predictive models based on historical data
- Enhance parlay generation with historical context
- Track betting performance and validation

Author: EQ12 System
Date: October 4, 2025
Version: 1.0.0
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import requests

# Import EQ12 rate limiting system
try:
    from eq12_rate_limit import (
        get_limiter_stats,
        get_with_limit,
        post_with_limit,
        sync_limiter,
    )

    RATE_LIMITING_AVAILABLE = True
    print("✅ EQ12 Rate limiting enabled for historical odds engine")
except ImportError:
    RATE_LIMITING_AVAILABLE = False
    print("⚠️ Rate limiting not available - using basic requests")

# Import today-only guard system

# Import NBA data integration
try:
    from eq12_nba_data_integration import NBADataIntegration

    NBA_INTEGRATION_AVAILABLE = True
except ImportError:
    NBA_INTEGRATION_AVAILABLE = False
    print("⚠️ NBA Integration not available for historical odds engine")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\historical_odds_engine.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SportKey(Enum):
    """Sport keys for The Odds API"""

    NFL = "americanfootball_nfl"
    NCAA_FOOTBALL = "americanfootball_ncaaf"
    NBA = "basketball_nba"
    NCAA_BASKETBALL = "basketball_ncaab"
    NHL = "icehockey_nhl"
    MLB = "baseball_mlb"
    SOCCER_EPL = "soccer_epl"
    TENNIS = "tennis_atp"


class MarketKey(Enum):
    """Market keys for betting types"""

    H2H = "h2h"  # Head to head / Moneyline
    SPREADS = "spreads"  # Point spreads
    TOTALS = "totals"  # Over/under
    PLAYER_PROPS = "player_points"
    ALTERNATE_SPREADS = "alternate_spreads"


@dataclass
class HistoricalOddsConfig:
    """Configuration for historical odds requests"""

    api_key: str
    base_url: str = "https://api.the-odds-api.com/v4"
    regions: list[str] = None
    markets: list[str] = None
    odds_format: str = "american"
    date_format: str = "iso"

    def __post_init__(self):
        if self.regions is None:
            self.regions = ["us", "us2"]
        if self.markets is None:
            self.markets = ["h2h", "spreads", "totals"]


@dataclass
class HistoricalEvent:
    """Historical event data structure"""

    event_id: str
    sport_key: str
    sport_title: str
    commence_time: str
    home_team: str
    away_team: str
    completed: bool = False
    final_score: dict[str, str] | None = None


@dataclass
class HistoricalOdds:
    """Historical odds data structure"""

    timestamp: str
    previous_timestamp: str | None
    next_timestamp: str | None
    event: HistoricalEvent
    bookmakers: list[dict[str, Any]]


@dataclass
class LineMovementAnalysis:
    """Analysis of line movement over time"""

    event_id: str
    market: str
    opening_line: float
    closing_line: float
    line_movement: float
    movement_percentage: float
    consensus_direction: str
    sharp_money_indicator: bool


class EQ12HistoricalOddsEngine:
    """Main class for historical odds data integration"""

    def __init__(self, config: HistoricalOddsConfig):
        self.config = config
        self.db_path = Path("C:\\EQ12\\data\\historical_odds.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms between requests

    def _init_database(self):
        """Initialize SQLite database for historical data storage"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Historical events table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS historical_events (
                        event_id TEXT PRIMARY KEY,
                        sport_key TEXT NOT NULL,
                        sport_title TEXT NOT NULL,
                        commence_time TEXT NOT NULL,
                        home_team TEXT NOT NULL,
                        away_team TEXT NOT NULL,
                        completed BOOLEAN DEFAULT FALSE,
                        final_score TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Historical odds table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS historical_odds (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        bookmaker TEXT NOT NULL,
                        market TEXT NOT NULL,
                        outcome_name TEXT NOT NULL,
                        price REAL NOT NULL,
                        point REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (event_id) REFERENCES historical_events (event_id)
                    )
                """
                )

                # Line movement analysis table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS line_movements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_id TEXT NOT NULL,
                        market TEXT NOT NULL,
                        opening_line REAL NOT NULL,
                        closing_line REAL NOT NULL,
                        line_movement REAL NOT NULL,
                        movement_percentage REAL NOT NULL,
                        consensus_direction TEXT NOT NULL,
                        sharp_money_indicator BOOLEAN DEFAULT FALSE,
                        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (event_id) REFERENCES historical_events (event_id)
                    )
                """
                )

                # Create indices for better performance
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_event_sport ON historical_events(sport_key)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_odds_event ON historical_odds(event_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_odds_timestamp ON historical_odds(timestamp)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_movement_event ON line_movements(event_id)"
                )

                conn.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _make_api_request(self, endpoint: str, params: dict[str, Any]) -> dict[str, Any] | None:
        """Make API request with error handling and rate limiting"""
        self._rate_limit()

        url = f"{self.config.base_url}{endpoint}"
        params["apiKey"] = self.config.api_key

        try:
            if RATE_LIMITING_AVAILABLE:
                response = get_with_limit(url, params=params, timeout=30)
            else:
                response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            # Check quota headers
            remaining = response.headers.get("x-requests-remaining", "unknown")
            used = response.headers.get("x-requests-used", "unknown")
            last_cost = response.headers.get("x-requests-last", "unknown")

            logger.info(
                f"API Request: {endpoint} | Quota - Remaining: {remaining}, Used: {used}, Last Cost: {last_cost}"
            )

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error for {endpoint}: {e}")
            return None

    def get_historical_events(
        self,
        sport: SportKey,
        date: datetime,
        commence_time_from: datetime | None = None,
        commence_time_to: datetime | None = None,
    ) -> list[HistoricalEvent]:
        """
        Fetch historical events for a given sport and date

        Args:
            sport: Sport key
            date: Historical date to query
            commence_time_from: Optional filter for game start time
            commence_time_to: Optional filter for game end time

        Returns:
            List of historical events
        """
        endpoint = f"/historical/sports/{sport.value}/events"

        params = {
            "date": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "dateFormat": self.config.date_format,
        }

        if commence_time_from:
            params["commenceTimeFrom"] = commence_time_from.strftime("%Y-%m-%dT%H:%M:%SZ")
        if commence_time_to:
            params["commenceTimeTo"] = commence_time_to.strftime("%Y-%m-%dT%H:%M:%SZ")

        response_data = self._make_api_request(endpoint, params)
        if not response_data:
            return []

        events = []
        for event_data in response_data.get("data", []):
            event = HistoricalEvent(
                event_id=event_data["id"],
                sport_key=event_data["sport_key"],
                sport_title=event_data["sport_title"],
                commence_time=event_data["commence_time"],
                home_team=event_data["home_team"],
                away_team=event_data["away_team"],
            )
            events.append(event)

        # Store events in database
        self._store_events(events)

        return events

    def get_historical_event_odds(
        self,
        sport: SportKey,
        event_id: str,
        date: datetime,
        regions: list[str] | None = None,
        markets: list[str] | None = None,
    ) -> HistoricalOdds | None:
        """
        Fetch historical odds for a specific event at a given timestamp

        Args:
            sport: Sport key
            event_id: Unique event identifier
            date: Historical timestamp
            regions: List of bookmaker regions
            markets: List of betting markets

        Returns:
            Historical odds data or None
        """
        endpoint = f"/historical/sports/{sport.value}/events/{event_id}/odds"

        params = {
            "date": date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "regions": ",".join(regions or self.config.regions),
            "markets": ",".join(markets or self.config.markets),
            "dateFormat": self.config.date_format,
            "oddsFormat": self.config.odds_format,
        }

        response_data = self._make_api_request(endpoint, params)
        if not response_data:
            return None

        # Parse response data
        event_data = response_data["data"]
        event = HistoricalEvent(
            event_id=event_data["id"],
            sport_key=event_data["sport_key"],
            sport_title=event_data["sport_title"],
            commence_time=event_data["commence_time"],
            home_team=event_data["home_team"],
            away_team=event_data["away_team"],
        )

        historical_odds = HistoricalOdds(
            timestamp=response_data["timestamp"],
            previous_timestamp=response_data.get("previous_timestamp"),
            next_timestamp=response_data.get("next_timestamp"),
            event=event,
            bookmakers=event_data.get("bookmakers", []),
        )

        # Store odds in database
        self._store_historical_odds(historical_odds)

        return historical_odds

    def analyze_line_movement(
        self,
        sport: SportKey,
        event_id: str,
        start_date: datetime,
        end_date: datetime,
        market: str = "h2h",
    ) -> LineMovementAnalysis | None:
        """
        Analyze line movement for an event over a time period

        Args:
            sport: Sport key
            event_id: Event identifier
            start_date: Analysis start date
            end_date: Analysis end date
            market: Betting market to analyze

        Returns:
            Line movement analysis
        """
        # Fetch historical odds at multiple timestamps
        timestamps = self._generate_timestamps(start_date, end_date, hours=6)  # Every 6 hours

        odds_history = []
        for timestamp in timestamps:
            odds_data = self.get_historical_event_odds(sport, event_id, timestamp, markets=[market])
            if odds_data:
                odds_history.append(odds_data)

        if len(odds_history) < 2:
            logger.warning(f"Insufficient historical data for line movement analysis: {event_id}")
            return None

        # Analyze line movement
        opening_odds = odds_history[0]
        closing_odds = odds_history[-1]

        # Extract consensus line from multiple bookmakers
        opening_line = self._get_consensus_line(opening_odds.bookmakers, market)
        closing_line = self._get_consensus_line(closing_odds.bookmakers, market)

        if opening_line is None or closing_line is None:
            return None

        line_movement = closing_line - opening_line
        movement_percentage = (line_movement / abs(opening_line)) * 100 if opening_line != 0 else 0

        # Determine consensus direction and sharp money indicators
        consensus_direction = (
            "up" if line_movement > 0 else "down" if line_movement < 0 else "stable"
        )
        sharp_money_indicator = abs(movement_percentage) > 5  # Significant movement threshold

        analysis = LineMovementAnalysis(
            event_id=event_id,
            market=market,
            opening_line=opening_line,
            closing_line=closing_line,
            line_movement=line_movement,
            movement_percentage=movement_percentage,
            consensus_direction=consensus_direction,
            sharp_money_indicator=sharp_money_indicator,
        )

        # Store analysis
        self._store_line_movement(analysis)

        return analysis

    def _generate_timestamps(
        self, start_date: datetime, end_date: datetime, hours: int = 6
    ) -> list[datetime]:
        """Generate timestamps for historical data collection"""
        timestamps = []
        current = start_date
        interval = timedelta(hours=hours)

        while current <= end_date:
            timestamps.append(current)
            current += interval

        return timestamps

    def _get_consensus_line(self, bookmakers: list[dict], market: str) -> float | None:
        """Calculate consensus line from multiple bookmakers"""
        lines = []

        for bookmaker in bookmakers:
            for market_data in bookmaker.get("markets", []):
                if market_data["key"] == market:
                    for outcome in market_data.get("outcomes", []):
                        if outcome.get("point") is not None:  # For spreads/totals
                            lines.append(outcome["point"])
                        elif market == "h2h":  # For moneyline
                            lines.append(outcome["price"])

        return sum(lines) / len(lines) if lines else None

    def _store_events(self, events: list[HistoricalEvent]):
        """Store historical events in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                for event in events:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO historical_events
                        (event_id, sport_key, sport_title, commence_time, home_team, away_team)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """,
                        (
                            event.event_id,
                            event.sport_key,
                            event.sport_title,
                            event.commence_time,
                            event.home_team,
                            event.away_team,
                        ),
                    )

                conn.commit()
                logger.info(f"Stored {len(events)} historical events")

        except Exception as e:
            logger.error(f"Error storing events: {e}")

    def _store_historical_odds(self, historical_odds: HistoricalOdds):
        """Store historical odds data in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Store event first
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO historical_events
                    (event_id, sport_key, sport_title, commence_time, home_team, away_team)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        historical_odds.event.event_id,
                        historical_odds.event.sport_key,
                        historical_odds.event.sport_title,
                        historical_odds.event.commence_time,
                        historical_odds.event.home_team,
                        historical_odds.event.away_team,
                    ),
                )

                # Store odds data
                for bookmaker in historical_odds.bookmakers:
                    bookmaker_key = bookmaker["key"]

                    for market in bookmaker.get("markets", []):
                        market_key = market["key"]

                        for outcome in market.get("outcomes", []):
                            cursor.execute(
                                """
                                INSERT INTO historical_odds
                                (event_id, timestamp, bookmaker, market, outcome_name, price, point)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    historical_odds.event.event_id,
                                    historical_odds.timestamp,
                                    bookmaker_key,
                                    market_key,
                                    outcome["name"],
                                    outcome["price"],
                                    outcome.get("point"),
                                ),
                            )

                conn.commit()
                logger.info(f"Stored historical odds for event {historical_odds.event.event_id}")

        except Exception as e:
            logger.error(f"Error storing historical odds: {e}")

    def _store_line_movement(self, analysis: LineMovementAnalysis):
        """Store line movement analysis in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO line_movements
                    (event_id, market, opening_line, closing_line, line_movement,
                     movement_percentage, consensus_direction, sharp_money_indicator)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        analysis.event_id,
                        analysis.market,
                        analysis.opening_line,
                        analysis.closing_line,
                        analysis.line_movement,
                        analysis.movement_percentage,
                        analysis.consensus_direction,
                        analysis.sharp_money_indicator,
                    ),
                )

                conn.commit()
                logger.info(f"Stored line movement analysis for {analysis.event_id}")

        except Exception as e:
            logger.error(f"Error storing line movement: {e}")

    def get_similar_historical_patterns(
        self, current_event: dict, lookback_days: int = 30
    ) -> list[dict]:
        """
        Find similar historical betting patterns for enhanced prediction

        Args:
            current_event: Current event data
            lookback_days: Days to look back for historical patterns

        Returns:
            List of similar historical patterns
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Query for similar events (same teams, similar lines, etc.)
                end_date = datetime.now(UTC)
                start_date = end_date - timedelta(days=lookback_days)

                query = """
                    SELECT he.*, lm.opening_line, lm.closing_line, lm.line_movement, lm.sharp_money_indicator
                    FROM historical_events he
                    LEFT JOIN line_movements lm ON he.event_id = lm.event_id
                    WHERE he.sport_key = ?
                    AND (he.home_team = ? OR he.away_team = ? OR he.home_team = ? OR he.away_team = ?)
                    AND he.commence_time >= ? AND he.commence_time <= ?
                    ORDER BY he.commence_time DESC
                """

                cursor.execute(
                    query,
                    (
                        current_event.get("sport_key"),
                        current_event.get("home_team"),
                        current_event.get("home_team"),
                        current_event.get("away_team"),
                        current_event.get("away_team"),
                        start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    ),
                )

                results = cursor.fetchall()

                patterns = []
                for row in results:
                    pattern = {
                        "event_id": row[0],
                        "sport_key": row[1],
                        "home_team": row[4],
                        "away_team": row[5],
                        "commence_time": row[3],
                        "opening_line": row[8],
                        "closing_line": row[9],
                        "line_movement": row[10],
                        "sharp_money_indicator": row[11],
                    }
                    patterns.append(pattern)

                return patterns

        except Exception as e:
            logger.error(f"Error finding historical patterns: {e}")
            return []

    def generate_historical_report(self, sport: SportKey, days_back: int = 7) -> dict[str, Any]:
        """Generate comprehensive historical analysis report"""
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=days_back)

        report = {
            "report_date": end_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "analysis_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            "sport": sport.value,
            "summary": {},
            "line_movements": [],
            "sharp_money_patterns": [],
            "performance_metrics": {},
        }

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get summary statistics
                cursor.execute(
                    """
                    SELECT COUNT(*) as total_events,
                           AVG(ABS(line_movement)) as avg_movement,
                           COUNT(CASE WHEN sharp_money_indicator = 1 THEN 1 END) as sharp_money_games
                    FROM historical_events he
                    JOIN line_movements lm ON he.event_id = lm.event_id
                    WHERE he.sport_key = ?
                    AND he.commence_time >= ? AND he.commence_time <= ?
                """,
                    (
                        sport.value,
                        start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    ),
                )

                summary = cursor.fetchone()
                if summary:
                    report["summary"] = {
                        "total_events": summary[0],
                        "average_line_movement": round(summary[1] or 0, 2),
                        "sharp_money_games": summary[2],
                        "sharp_money_percentage": round(
                            (summary[2] / summary[0] * 100) if summary[0] > 0 else 0, 1
                        ),
                    }

                # Get significant line movements
                cursor.execute(
                    """
                    SELECT he.home_team, he.away_team, lm.market, lm.opening_line,
                           lm.closing_line, lm.line_movement, lm.movement_percentage
                    FROM historical_events he
                    JOIN line_movements lm ON he.event_id = lm.event_id
                    WHERE he.sport_key = ?
                    AND he.commence_time >= ? AND he.commence_time <= ?
                    AND ABS(lm.movement_percentage) > 5
                    ORDER BY ABS(lm.movement_percentage) DESC
                    LIMIT 10
                """,
                    (
                        sport.value,
                        start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    ),
                )

                movements = cursor.fetchall()
                for movement in movements:
                    report["line_movements"].append(
                        {
                            "matchup": f"{movement[1]} @ {movement[0]}",
                            "market": movement[2],
                            "opening_line": movement[3],
                            "closing_line": movement[4],
                            "movement": movement[5],
                            "movement_percentage": round(movement[6], 1),
                        }
                    )

        except Exception as e:
            logger.error(f"Error generating historical report: {e}")

        return report


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 Historical Odds Data Engine")
    parser.add_argument(
        "--action",
        choices=["fetch_events", "analyze_movement", "generate_report", "test_api"],
        default="generate_report",
        help="Action to perform",
    )
    parser.add_argument(
        "--sport",
        choices=[sport.value for sport in SportKey],
        default=SportKey.NFL.value,
        help="Sport to analyze",
    )
    parser.add_argument("--days", type=int, default=7, help="Number of days to analyze")
    parser.add_argument("--date", help="YYYY-MM-DD (default: today America/New_York)")
    parser.add_argument("--after", help="HH:MM 24h cutoff (optional)")
    parser.add_argument("--event-id", help="Specific event ID for analysis")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get API key from environment
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        logger.error("ODDS_API_KEY environment variable not found!")
        sys.exit(1)

    # Initialize engine
    config = HistoricalOddsConfig(api_key=api_key)
    engine = EQ12HistoricalOddsEngine(config)

    try:
        sport_enum = SportKey(args.sport)

        if args.action == "fetch_events":
            logger.info(f"Fetching historical events for {sport_enum.value}")
            date = datetime.now(UTC) - timedelta(days=1)  # Yesterday
            events = engine.get_historical_events(sport_enum, date)
            logger.info(f"Fetched {len(events)} events")

        elif args.action == "analyze_movement":
            if not args.event_id:
                logger.error("Event ID required for movement analysis")
                sys.exit(1)

            logger.info(f"Analyzing line movement for event {args.event_id}")
            start_date = datetime.now(UTC) - timedelta(days=args.days)
            end_date = datetime.now(UTC)

            analysis = engine.analyze_line_movement(sport_enum, args.event_id, start_date, end_date)
            if analysis:
                logger.info(f"Line Movement Analysis: {asdict(analysis)}")
            else:
                logger.warning("No movement analysis available")

        elif args.action == "generate_report":
            logger.info(f"Generating historical report for {sport_enum.value}")
            report = engine.generate_historical_report(sport_enum, args.days)

            # Save report
            report_file = f"C:\\EQ12\\logs\\historical_report_{sport_enum.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"Report saved to: {report_file}")
            print(json.dumps(report, indent=2))

        elif args.action == "test_api":
            logger.info("Testing API connection...")
            # Test with a simple sports list call (doesn't count against quota)
            response = engine._make_api_request("/sports", {})
            if response:
                logger.info("API connection successful!")
                logger.info(f"Available sports: {len(response)} found")
            else:
                logger.error("API connection failed!")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
