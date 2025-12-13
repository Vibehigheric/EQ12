"""
EQ12 Backtester Data Layer
Comprehensive data loading and API integration for all sports and markets

This module handles:
1. CSV/Excel loading for prop sheets (MLB HR, TB, K, etc.)
2. API integrations (OddsAPI, ESPN, DraftKings historicals)
3. Hardcoded sport mappings and team normalization
4. Data caching and storage for EQ12 stack
"""

import json
import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import requests

logger = logging.getLogger(__name__)


@dataclass
class GameResult:
    """Standardized game result structure"""

    game_id: str
    sport: str
    date: datetime
    home_team: str
    away_team: str
    home_score: int | None = None
    away_score: int | None = None
    status: str = "completed"
    additional_stats: dict[str, Any] | None = None


@dataclass
class PlayerStat:
    """Player performance statistics"""

    player_name: str
    team: str
    sport: str
    date: datetime
    stats: dict[str, float]  # HR, TB, Hits, K, etc.


class EQ12DataLoader:
    """
    Master data loader for EQ12 backtesting system

    Handles all data sources used in the profit maximization loop:
    - Sports betting data (odds, results)
    - Trading data (OHLCV, indicators)
    - Affiliate funnel data (CTR, conversions)
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = Path(eq12_root)
        self.data_dir = self.eq12_root / "eq12_backtester" / "data"
        self.cache_dir = self.data_dir / "cache"
        self.db_path = self.data_dir / "eq12_backtester.db"

        # Create directories
        self.data_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

        # Initialize database
        self._init_database()

        # API configurations
        self.api_configs = {
            "odds_api": {
                "base_url": "https://api.the-odds-api.com/v4",
                "key": os.getenv("ODDS_API_KEY", ""),
                "rate_limit": 500,  # requests per month for free tier
            },
            "espn_api": {
                "base_url": "http://site.api.espn.com/apis/site/v2/sports",
                "rate_limit": None,  # No official limit
            },
        }

        # Team name mappings for normalization
        self.team_mappings = self._load_team_mappings()

        logger.info("EQ12 Data Loader initialized")

    def _init_database(self):
        """Initialize SQLite database for caching"""
        with sqlite3.connect(self.db_path) as conn:
            # Games table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    game_id TEXT PRIMARY KEY,
                    sport TEXT,
                    date TEXT,
                    home_team TEXT,
                    away_team TEXT,
                    home_score INTEGER,
                    away_score INTEGER,
                    status TEXT,
                    raw_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Player stats table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS player_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT,
                    team TEXT,
                    sport TEXT,
                    date TEXT,
                    stat_type TEXT,
                    stat_value REAL,
                    game_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Odds history table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS odds_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT,
                    market_type TEXT,
                    selection TEXT,
                    odds REAL,
                    timestamp TIMESTAMP,
                    bookmaker TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.commit()

    def _load_team_mappings(self) -> dict[str, dict[str, str]]:
        """Load team name mappings for normalization"""
        return {
            "MLB": {
                # Common variations -> standard name
                "NYY": "New York Yankees",
                "NY Yankees": "New York Yankees",
                "Yankees": "New York Yankees",
                "LAD": "Los Angeles Dodgers",
                "LA Dodgers": "Los Angeles Dodgers",
                "Dodgers": "Los Angeles Dodgers",
                "BOS": "Boston Red Sox",
                "Red Sox": "Boston Red Sox",
                "HOU": "Houston Astros",
                "Astros": "Houston Astros",
                # Add more mappings as needed
            },
            "NFL": {
                "KC": "Kansas City Chiefs",
                "Chiefs": "Kansas City Chiefs",
                "BUF": "Buffalo Bills",
                "Bills": "Buffalo Bills",
                "TB": "Tampa Bay Buccaneers",
                "Bucs": "Tampa Bay Buccaneers",
                "Buccaneers": "Tampa Bay Buccaneers",
                # Add more mappings
            },
            "NBA": {
                "LAL": "Los Angeles Lakers",
                "Lakers": "Los Angeles Lakers",
                "GSW": "Golden State Warriors",
                "Warriors": "Golden State Warriors",
                # Add more mappings
            },
        }

    def normalize_team_name(self, team_name: str, sport: str) -> str:
        """Normalize team names across different data sources"""
        sport_mappings = self.team_mappings.get(sport.upper(), {})
        return sport_mappings.get(team_name, team_name)

    def load_csv_data(self, file_path: str | Path, data_type: str = "bets") -> pd.DataFrame:
        """
        Load CSV data (prop sheets, historical bets, etc.)

        Args:
            file_path: Path to CSV file
            data_type: Type of data (bets, games, stats, etc.)
        """
        try:
            df = pd.read_csv(file_path)

            # Standardize column names
            df.columns = df.columns.str.lower().str.replace(" ", "_")

            # Parse dates if present
            date_cols = ["date", "game_date", "timestamp"]
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")

            # Normalize team names if present
            team_cols = ["team", "home_team", "away_team", "opponent"]
            sport = df.get("sport", pd.Series(["MLB"])).iloc[0] if len(df) > 0 else "MLB"

            for col in team_cols:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: self.normalize_team_name(str(x), sport))

            logger.info(f"Loaded {len(df)} rows from {file_path}")
            return df

        except Exception as e:
            logger.error(f"Error loading CSV {file_path}: {e}")
            return pd.DataFrame()

    def load_excel_data(self, file_path: str | Path, sheet_name: str | None = None) -> pd.DataFrame:
        """Load Excel data (prop sheets with multiple tabs)"""
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                # Load first sheet
                df = pd.read_excel(file_path)

            # Apply same normalization as CSV
            df.columns = df.columns.str.lower().str.replace(" ", "_")

            logger.info(f"Loaded {len(df)} rows from Excel: {file_path}")
            return df

        except Exception as e:
            logger.error(f"Error loading Excel {file_path}: {e}")
            return pd.DataFrame()

    def get_odds_api_data(
        self,
        sport: str,
        market: str = "h2h",
        regions: str = "us",
        date_from: str | None = None,
    ) -> list[dict]:
        """
        Fetch data from The Odds API

        Args:
            sport: Sport key (baseball_mlb, americanfootball_nfl, etc.)
            market: Market type (h2h, spreads, totals, player_props)
            regions: Regions (us, uk, au)
            date_from: ISO date string for historical data
        """
        if not self.api_configs["odds_api"]["key"]:
            logger.warning("ODDS_API_KEY not set - skipping API call")
            return []

        # Check cache first
        cache_key = f"odds_{sport}_{market}_{date_from or 'current'}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return cached_data

        try:
            base_url = self.api_configs["odds_api"]["base_url"]
            endpoint = f"{base_url}/sports/{sport}/odds"

            params = {
                "apiKey": self.api_configs["odds_api"]["key"],
                "regions": regions,
                "markets": market,
                "dateFormat": "iso",
            }

            if date_from:
                params["date_from"] = date_from

            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Cache the response
            self._cache_data(cache_key, data, expiry_hours=1)

            logger.info(f"Fetched {len(data)} games from Odds API: {sport}/{market}")
            return data

        except Exception as e:
            logger.error(f"Error fetching Odds API data: {e}")
            return []

    def get_espn_scores(self, sport: str, date: str | None = None) -> list[GameResult]:
        """
        Fetch game scores from ESPN API

        Args:
            sport: Sport (baseball, football, basketball)
            date: Date in YYYYMMDD format, defaults to today
        """
        if not date:
            date = datetime.now().strftime("%Y%m%d")

        # Check cache
        cache_key = f"espn_scores_{sport}_{date}"
        cached_data = self._get_cached_data(cache_key)
        if cached_data:
            return [GameResult(**game) for game in cached_data]

        try:
            # Map sport names
            sport_mapping = {
                "MLB": "baseball/mlb",
                "NFL": "football/nfl",
                "NBA": "basketball/nba",
            }

            espn_sport = sport_mapping.get(sport.upper(), sport.lower())
            base_url = self.api_configs["espn_api"]["base_url"]
            url = f"{base_url}/{espn_sport}/scoreboard"

            params = {"dates": date}
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            games = []

            for event in data.get("events", []):
                game = GameResult(
                    game_id=event.get("id", ""),
                    sport=sport.upper(),
                    date=datetime.strptime(event.get("date", ""), "%Y-%m-%dT%H:%M:%SZ"),
                    home_team=self.normalize_team_name(
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[0]
                        .get("team", {})
                        .get("displayName", ""),
                        sport,
                    ),
                    away_team=self.normalize_team_name(
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[1]
                        .get("team", {})
                        .get("displayName", ""),
                        sport,
                    ),
                    home_score=int(
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[0]
                        .get("score", 0)
                    ),
                    away_score=int(
                        event.get("competitions", [{}])[0]
                        .get("competitors", [{}])[1]
                        .get("score", 0)
                    ),
                    status=event.get("status", {}).get("type", {}).get("name", "unknown"),
                )
                games.append(game)

            # Cache results
            self._cache_data(cache_key, [game.__dict__ for game in games], expiry_hours=24)

            # Store in database
            self._store_games_in_db(games)

            logger.info(f"Fetched {len(games)} games from ESPN: {sport} {date}")
            return games

        except Exception as e:
            logger.error(f"Error fetching ESPN scores: {e}")
            return []

    def get_mlb_player_stats(self, date: str | None = None) -> list[PlayerStat]:
        """
        Fetch MLB player statistics for a specific date

        This would integrate with your existing sports result parser
        """
        # This would call your existing sports_result_parser functionality
        # For now, return empty list - integrate with actual parser

        logger.info("MLB player stats integration point - connect to sports_result_parser")
        return []

    def load_prop_sheets(self, sheet_type: str = "MLB_HR") -> pd.DataFrame:
        """
        Load EQ12 prop sheets from standard locations

        Args:
            sheet_type: Type of prop sheet (MLB_HR, MLB_TB, NFL_TD, etc.)
        """
        # Look for prop sheets in common locations
        possible_paths = [
            self.data_dir / f"{sheet_type.lower()}_props.csv",
            self.eq12_root / "data" / f"{sheet_type.lower()}_props.csv",
            self.eq12_root / f"{sheet_type}_props.xlsx",
        ]

        for path in possible_paths:
            if path.exists():
                if path.suffix == ".csv":
                    return self.load_csv_data(path, "props")
                if path.suffix in [".xlsx", ".xls"]:
                    return self.load_excel_data(path)

        logger.warning(f"No prop sheet found for {sheet_type}")
        return pd.DataFrame()

    def _get_cached_data(self, cache_key: str) -> Any | None:
        """Get data from cache if not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                cached = json.load(f)

            # Check expiry
            datetime.fromisoformat(cached["timestamp"])
            expiry_time = datetime.fromisoformat(cached["expiry"])

            if datetime.now() < expiry_time:
                return cached["data"]
            # Expired - remove file
            cache_file.unlink()
            return None

        except Exception as e:
            logger.error(f"Error reading cache {cache_key}: {e}")
            return None

    def _cache_data(self, cache_key: str, data: Any, expiry_hours: int = 24):
        """Cache data with expiry"""
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            cached_data = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "expiry": (datetime.now() + timedelta(hours=expiry_hours)).isoformat(),
            }

            with open(cache_file, "w") as f:
                json.dump(cached_data, f, default=str)

        except Exception as e:
            logger.error(f"Error caching data {cache_key}: {e}")

    def _store_games_in_db(self, games: list[GameResult]):
        """Store game results in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                for game in games:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO games
                        (game_id, sport, date, home_team, away_team, home_score, away_score, status, raw_data)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            game.game_id,
                            game.sport,
                            game.date.isoformat(),
                            game.home_team,
                            game.away_team,
                            game.home_score,
                            game.away_score,
                            game.status,
                            json.dumps(game.__dict__, default=str),
                        ),
                    )
                conn.commit()

        except Exception as e:
            logger.error(f"Error storing games in database: {e}")

    def query_historical_games(
        self, sport: str, start_date: datetime, end_date: datetime
    ) -> list[GameResult]:
        """Query historical games from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT * FROM games
                    WHERE sport = ? AND date BETWEEN ? AND ?
                    ORDER BY date DESC
                """,
                    (sport, start_date.isoformat(), end_date.isoformat()),
                )

                games = []
                for row in cursor.fetchall():
                    game = GameResult(
                        game_id=row[0],
                        sport=row[1],
                        date=datetime.fromisoformat(row[2]),
                        home_team=row[3],
                        away_team=row[4],
                        home_score=row[5],
                        away_score=row[6],
                        status=row[7],
                    )
                    games.append(game)

                return games

        except Exception as e:
            logger.error(f"Error querying historical games: {e}")
            return []

    def get_data_summary(self) -> dict[str, Any]:
        """Get summary of available data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Count games by sport
                cursor = conn.execute(
                    """
                    SELECT sport, COUNT(*) as game_count
                    FROM games
                    GROUP BY sport
                """
                )
                games_by_sport = dict(cursor.fetchall())

                # Get date ranges
                cursor = conn.execute(
                    """
                    SELECT MIN(date) as earliest, MAX(date) as latest
                    FROM games
                """
                )
                date_range = cursor.fetchone()

                return {
                    "games_by_sport": games_by_sport,
                    "date_range": {
                        "earliest": date_range[0] if date_range[0] else None,
                        "latest": date_range[1] if date_range[1] else None,
                    },
                    "cache_files": len(list(self.cache_dir.glob("*.json"))),
                    "database_size_mb": (
                        self.db_path.stat().st_size / 1024 / 1024 if self.db_path.exists() else 0
                    ),
                }

        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}


# Integration helper functions
def load_eq12_prop_data(prop_type: str = "MLB_HR") -> pd.DataFrame:
    """Quick function to load EQ12 prop data"""
    loader = EQ12DataLoader()
    return loader.load_prop_sheets(prop_type)


def get_recent_scores(sport: str = "MLB", days_back: int = 7) -> list[GameResult]:
    """Quick function to get recent game scores"""
    loader = EQ12DataLoader()
    games = []

    for i in range(days_back):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
        daily_games = loader.get_espn_scores(sport, date)
        games.extend(daily_games)

    return games


if __name__ == "__main__":
    # Test the data loader
    loader = EQ12DataLoader()

    print("🎯 EQ12 Data Loader Test")

    # Test ESPN scores
    mlb_games = loader.get_espn_scores("MLB")
    print(f"MLB Games Today: {len(mlb_games)}")

    # Test data summary
    summary = loader.get_data_summary()
    print(f"Data Summary: {summary}")

    logger.info("EQ12 Data Loader test completed!")
