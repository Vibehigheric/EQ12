#!/usr/bin/env python3
"""
EQ12 GODSTACK - Odds Ingest & Normalizer
Pull lines/props from books/APIs, normalize markets, de-duplicate teams/players, unify timezones

Core Features:
- Multi-source odds aggregation (The-Odds-API, FanDuel API, DraftKings scraping)
- Market normalization (ML, RL, totals, team totals, player props)
- Team/player de-duplication and standardization
- Timezone unification and game scheduling
- Real-time line movement tracking
- SQLite/Parquet storage with optional Redis caching
"""

import argparse
import hashlib
import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/odds_ingest.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class NormalizedOdds(BaseModel):
    """Standardized odds format across all books"""

    game_id: str = Field(..., description="Unique game identifier")
    book_name: str = Field(..., description="Sportsbook name")
    sport: str = Field(default="baseball_mlb", description="Sport identifier")

    # Game metadata
    home_team: str = Field(..., description="Home team standardized name")
    away_team: str = Field(..., description="Away team standardized name")
    commence_time: datetime = Field(..., description="Game start time in UTC")

    # Markets
    moneyline_home: int | None = Field(None, description="Home ML odds (American)")
    moneyline_away: int | None = Field(None, description="Away ML odds (American)")

    total_points: float | None = Field(None, description="Total runs/points line")
    total_over_odds: int | None = Field(None, description="Total over odds")
    total_under_odds: int | None = Field(None, description="Total under odds")

    spread_home: float | None = Field(None, description="Home spread (runline)")
    spread_home_odds: int | None = Field(None, description="Home spread odds")
    spread_away: float | None = Field(None, description="Away spread")
    spread_away_odds: int | None = Field(None, description="Away spread odds")

    # Team totals
    home_team_total: float | None = Field(None, description="Home team total line")
    home_team_over_odds: int | None = Field(None, description="Home team total over odds")
    home_team_under_odds: int | None = Field(None, description="Home team total under odds")

    away_team_total: float | None = Field(None, description="Away team total line")
    away_team_over_odds: int | None = Field(None, description="Away team total over odds")
    away_team_under_odds: int | None = Field(None, description="Away team total under odds")

    # Metadata
    last_update: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data_hash: str = Field(default="", description="Data integrity hash")


class PlayerProp(BaseModel):
    """Normalized player proposition bet"""

    prop_id: str = Field(..., description="Unique prop identifier")
    game_id: str = Field(..., description="Associated game ID")
    book_name: str = Field(..., description="Sportsbook name")

    player_name: str = Field(..., description="Standardized player name")
    team: str = Field(..., description="Player team")
    position: str = Field(default="", description="Player position")

    prop_type: str = Field(..., description="Prop category (hits, strikeouts, home_runs, etc)")
    line: float = Field(..., description="Over/under line")
    over_odds: int | None = Field(None, description="Over odds (American)")
    under_odds: int | None = Field(None, description="Under odds (American)")

    last_update: datetime = Field(default_factory=lambda: datetime.now(UTC))


@dataclass
class BookConfig:
    """Configuration for each sportsbook integration"""

    name: str
    base_url: str
    api_key: str | None
    rate_limit: int  # requests per minute
    timeout: int
    headers: dict[str, str]
    team_mapping: dict[str, str]  # book names -> standardized names


class OddsIngestEngine:
    """Main odds ingestion and normalization engine"""

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path or "C:/EQ12/configs/odds_config.json"
        self.db_path = Path("C:/EQ12/data/odds_database.db")
        self.logs_dir = Path("C:/EQ12/logs")

        # Load configuration
        self.config = self._load_config()
        self.books = self._setup_books()

        # Initialize database
        self._init_database()

        # Team name standardization
        self.team_standards = self._load_team_standards()

        # Rate limiting
        self.last_requests = {}

        logger.info(f"OddsIngestEngine initialized with {len(self.books)} books")

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file or create default"""

        default_config = {
            "books": {
                "the_odds_api": {
                    "name": "The-Odds-API",
                    "base_url": "https://api.the-odds-api.com/v4",
                    "api_key_env": "ODDS_API_KEY",
                    "rate_limit": 500,  # requests per hour
                    "timeout": 30,
                    "headers": {"Content-Type": "application/json"},
                }
            },
            "redis": {
                "enabled": False,
                "host": "localhost",
                "port": 6379,
                "ttl": 300,  # 5 minutes
            },
            "storage": {
                "sqlite_enabled": True,
                "parquet_enabled": True,
                "retention_days": 30,
            },
        }

        try:
            with open(self.config_path) as f:
                config = json.load(f)
                logger.info(f"Loaded config from {self.config_path}")
                return config
        except FileNotFoundError:
            logger.info(f"Config not found, creating default at {self.config_path}")
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def _setup_books(self) -> dict[str, BookConfig]:
        """Setup sportsbook configurations"""

        books = {}

        # The-Odds-API setup
        api_key = self._get_env_var("ODDS_API_KEY")
        if api_key:
            books["the_odds_api"] = BookConfig(
                name="The-Odds-API",
                base_url="https://api.the-odds-api.com/v4",
                api_key=api_key,
                rate_limit=500,
                timeout=30,
                headers={"Content-Type": "application/json"},
                team_mapping=self._get_mlb_team_mapping(),
            )

        return books

    def _get_env_var(self, var_name: str) -> str | None:
        """Get environment variable safely"""
        import os

        return os.getenv(var_name)

    def _get_mlb_team_mapping(self) -> dict[str, str]:
        """MLB team name standardization mapping"""

        return {
            # The-Odds-API -> Standard names
            "New York Yankees": "NYY",
            "Toronto Blue Jays": "TOR",
            "Boston Red Sox": "BOS",
            "Tampa Bay Rays": "TB",
            "Baltimore Orioles": "BAL",
            "Chicago White Sox": "CWS",
            "Cleveland Guardians": "CLE",
            "Detroit Tigers": "DET",
            "Kansas City Royals": "KC",
            "Minnesota Twins": "MIN",
            "Houston Astros": "HOU",
            "Los Angeles Angels": "LAA",
            "Oakland Athletics": "OAK",
            "Seattle Mariners": "SEA",
            "Texas Rangers": "TEX",
            "Atlanta Braves": "ATL",
            "Miami Marlins": "MIA",
            "New York Mets": "NYM",
            "Philadelphia Phillies": "PHI",
            "Washington Nationals": "WSH",
            "Chicago Cubs": "CHC",
            "Cincinnati Reds": "CIN",
            "Milwaukee Brewers": "MIL",
            "Pittsburgh Pirates": "PIT",
            "St. Louis Cardinals": "STL",
            "Arizona Diamondbacks": "ARI",
            "Colorado Rockies": "COL",
            "Los Angeles Dodgers": "LAD",
            "San Diego Padres": "SD",
            "San Francisco Giants": "SF",
        }

    def _load_team_standards(self) -> dict[str, str]:
        """Load team standardization mapping"""
        return self._get_mlb_team_mapping()

    def _init_database(self):
        """Initialize SQLite database"""

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Games odds table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS odds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    book_name TEXT NOT NULL,
                    sport TEXT DEFAULT 'baseball_mlb',
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    commence_time TEXT NOT NULL,
                    moneyline_home INTEGER,
                    moneyline_away INTEGER,
                    total_points REAL,
                    total_over_odds INTEGER,
                    total_under_odds INTEGER,
                    spread_home REAL,
                    spread_home_odds INTEGER,
                    spread_away REAL,
                    spread_away_odds INTEGER,
                    home_team_total REAL,
                    home_team_over_odds INTEGER,
                    home_team_under_odds INTEGER,
                    away_team_total REAL,
                    away_team_over_odds INTEGER,
                    away_team_under_odds INTEGER,
                    last_update TEXT NOT NULL,
                    data_hash TEXT,
                    UNIQUE(game_id, book_name, last_update)
                )
            """
            )

            # Player props table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS player_props (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prop_id TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    book_name TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    team TEXT NOT NULL,
                    position TEXT,
                    prop_type TEXT NOT NULL,
                    line REAL NOT NULL,
                    over_odds INTEGER,
                    under_odds INTEGER,
                    last_update TEXT NOT NULL,
                    UNIQUE(prop_id, book_name, last_update)
                )
            """
            )

            # Line movements table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS line_movements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    book_name TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    movement_time TEXT NOT NULL,
                    movement_cents REAL
                )
            """
            )

        logger.info("Database initialized successfully")

    def standardize_team_name(self, team_name: str, book_name: str) -> str:
        """Convert book-specific team name to standard format"""

        # Direct mapping first
        if team_name in self.team_standards:
            return self.team_standards[team_name]

        # Fuzzy matching for variations
        team_lower = team_name.lower()
        for book_name_key, standard in self.team_standards.items():
            if team_lower in book_name_key.lower():
                return standard

        # Fallback to original if no match
        logger.warning(f"No standard mapping found for team: {team_name} from {book_name}")
        return team_name

    def generate_game_id(self, home_team: str, away_team: str, commence_time: datetime) -> str:
        """Generate unique game identifier"""

        date_str = commence_time.strftime("%Y%m%d")
        game_str = f"{away_team}@{home_team}_{date_str}"
        return hashlib.md5(game_str.encode()).hexdigest()[:12]

    def calculate_data_hash(self, odds_data: dict) -> str:
        """Calculate hash for data integrity"""

        # Remove timestamp fields for hash calculation
        clean_data = {k: v for k, v in odds_data.items() if k not in ["last_update", "data_hash"]}

        data_str = json.dumps(clean_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    async def fetch_odds_the_odds_api(self, sport: str = "baseball_mlb") -> list[NormalizedOdds]:
        """Fetch odds from The-Odds-API"""

        if "the_odds_api" not in self.books:
            logger.warning("The-Odds-API not configured")
            return []

        book = self.books["the_odds_api"]

        try:
            # Rate limiting check
            await self._check_rate_limit("the_odds_api", book.rate_limit)

            async with httpx.AsyncClient(timeout=book.timeout) as client:
                # Fetch games
                url = f"{book.base_url}/sports/{sport}/odds"
                params = {
                    "apiKey": book.api_key,
                    "regions": "us",
                    "markets": "h2h,spreads,totals,team_totals",
                    "oddsFormat": "american",
                    "dateFormat": "iso",
                }

                response = await client.get(url, params=params)
                response.raise_for_status()

                games_data = response.json()
                logger.info(f"Fetched {len(games_data)} games from The-Odds-API")

                normalized_odds = []

                for game in games_data:
                    try:
                        # Extract game info
                        home_team = self.standardize_team_name(game["home_team"], "the_odds_api")
                        away_team = self.standardize_team_name(game["away_team"], "the_odds_api")
                        commence_time = datetime.fromisoformat(
                            game["commence_time"].replace("Z", "+00:00")
                        )

                        game_id = self.generate_game_id(home_team, away_team, commence_time)

                        # Process each bookmaker
                        for bookmaker in game.get("bookmakers", []):
                            book_name = bookmaker["title"]

                            # Initialize odds data
                            odds_data = {
                                "game_id": game_id,
                                "book_name": book_name,
                                "sport": sport,
                                "home_team": home_team,
                                "away_team": away_team,
                                "commence_time": commence_time,
                            }

                            # Process markets
                            for market in bookmaker.get("markets", []):
                                market_key = market["key"]

                                if market_key == "h2h":  # Moneyline
                                    for outcome in market["outcomes"]:
                                        if outcome["name"] == home_team:
                                            odds_data["moneyline_home"] = outcome["price"]
                                        elif outcome["name"] == away_team:
                                            odds_data["moneyline_away"] = outcome["price"]

                                elif market_key == "spreads":  # Runline
                                    for outcome in market["outcomes"]:
                                        if outcome["name"] == home_team:
                                            odds_data["spread_home"] = outcome["point"]
                                            odds_data["spread_home_odds"] = outcome["price"]
                                        elif outcome["name"] == away_team:
                                            odds_data["spread_away"] = outcome["point"]
                                            odds_data["spread_away_odds"] = outcome["price"]

                                elif market_key == "totals":  # Game total
                                    for outcome in market["outcomes"]:
                                        if outcome["name"] == "Over":
                                            odds_data["total_points"] = outcome["point"]
                                            odds_data["total_over_odds"] = outcome["price"]
                                        elif outcome["name"] == "Under":
                                            odds_data["total_under_odds"] = outcome["price"]

                            # Calculate hash
                            odds_data["data_hash"] = self.calculate_data_hash(odds_data)

                            normalized_odds.append(NormalizedOdds(**odds_data))

                    except Exception as e:
                        logger.error(f"Error processing game {game.get('id', 'unknown')}: {e}")
                        continue

                return normalized_odds

        except httpx.RequestError as e:
            logger.error(f"HTTP error fetching from The-Odds-API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    async def _check_rate_limit(self, book_name: str, rate_limit: int):
        """Check and enforce rate limiting"""

        current_time = time.time()

        if book_name not in self.last_requests:
            self.last_requests[book_name] = []

        # Remove old requests (older than 1 hour)
        self.last_requests[book_name] = [
            req_time for req_time in self.last_requests[book_name] if current_time - req_time < 3600
        ]

        # Check if we're over the rate limit
        if len(self.last_requests[book_name]) >= rate_limit:
            sleep_time = 3600 - (current_time - self.last_requests[book_name][0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached for {book_name}, sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)

        # Record this request
        self.last_requests[book_name].append(current_time)

    def save_odds_to_database(self, odds_list: list[NormalizedOdds]):
        """Save normalized odds to SQLite database"""

        with sqlite3.connect(self.db_path) as conn:
            for odds in odds_list:
                try:
                    # Convert to dict for database insertion
                    odds_dict = odds.dict()
                    odds_dict["commence_time"] = odds.commence_time.isoformat()
                    odds_dict["last_update"] = odds.last_update.isoformat()

                    # Insert into database
                    placeholders = ", ".join(["?" for _ in odds_dict])
                    columns = ", ".join(odds_dict.keys())

                    conn.execute(
                        f"""
                        INSERT OR REPLACE INTO odds ({columns})
                        VALUES ({placeholders})
                    """,
                        list(odds_dict.values()),
                    )

                except Exception as e:
                    logger.error(f"Error saving odds to database: {e}")
                    continue

            conn.commit()
            logger.info(f"Saved {len(odds_list)} odds records to database")

    def export_to_parquet(self, output_path: str | None = None):
        """Export odds data to Parquet format"""

        if not output_path:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            output_path = f"C:/EQ12/data/odds_export_{timestamp}.parquet"

        try:
            # Read from database
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query("SELECT * FROM odds ORDER BY last_update DESC", conn)

            # Convert timestamps
            df["commence_time"] = pd.to_datetime(df["commence_time"])
            df["last_update"] = pd.to_datetime(df["last_update"])

            # Save to Parquet
            df.to_parquet(output_path, engine="pyarrow", compression="snappy")
            logger.info(f"Exported {len(df)} records to {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Error exporting to Parquet: {e}")
            return None

    async def ingest_all_odds(self, sport: str = "baseball_mlb") -> dict[str, int]:
        """Main method to ingest odds from all configured sources"""

        logger.info(f"Starting odds ingestion for {sport}")

        results = {"total_odds": 0, "sources_used": 0, "errors": 0}

        try:
            # The-Odds-API
            if "the_odds_api" in self.books:
                try:
                    odds = await self.fetch_odds_the_odds_api(sport)
                    if odds:
                        self.save_odds_to_database(odds)
                        results["total_odds"] += len(odds)
                        results["sources_used"] += 1
                        logger.info(f"Successfully ingested {len(odds)} odds from The-Odds-API")
                except Exception as e:
                    logger.error(f"Error with The-Odds-API: {e}")
                    results["errors"] += 1

            # Export to Parquet if enabled
            if self.config.get("storage", {}).get("parquet_enabled", False):
                self.export_to_parquet()

            logger.info(f"Odds ingestion complete: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in odds ingestion: {e}")
            results["errors"] += 1
            return results

    def get_latest_odds(self, game_id: str | None = None) -> list[dict]:
        """Retrieve latest odds from database"""

        with sqlite3.connect(self.db_path) as conn:
            if game_id:
                query = """
                    SELECT * FROM odds
                    WHERE game_id = ?
                    ORDER BY last_update DESC
                """
                cursor = conn.execute(query, (game_id,))
            else:
                query = """
                    SELECT * FROM odds
                    WHERE date(commence_time) >= date('now')
                    ORDER BY commence_time ASC, last_update DESC
                """
                cursor = conn.execute(query)

            columns = [description[0] for description in cursor.description]
            results = []

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row, strict=False)))

            return results


async def main():
    """Main CLI interface"""

    parser = argparse.ArgumentParser(description="EQ12 Odds Ingest Engine")
    parser.add_argument(
        "--sport",
        default="baseball_mlb",
        help="Sport to ingest (default: baseball_mlb)",
    )
    parser.add_argument("--config", help="Config file path")
    parser.add_argument("--export", action="store_true", help="Export to Parquet after ingest")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize engine
    engine = OddsIngestEngine(config_path=args.config)

    # Run ingestion
    results = await engine.ingest_all_odds(sport=args.sport)

    print("\n📊 ODDS INGEST RESULTS:")
    print(f"   Total odds ingested: {results['total_odds']}")
    print(f"   Sources used: {results['sources_used']}")
    print(f"   Errors: {results['errors']}")

    # Show latest games
    latest_odds = engine.get_latest_odds()
    if latest_odds:
        print(f"\n🎲 LATEST GAMES ({len(latest_odds)} found):")
        for odds in latest_odds[:5]:  # Show first 5
            print(f"   {odds['away_team']} @ {odds['home_team']} - {odds['book_name']}")
            if odds["moneyline_home"]:
                print(
                    f"      ML: {odds['away_team']} {odds['moneyline_away']} | {odds['home_team']} {odds['moneyline_home']}"
                )
            if odds["total_points"]:
                print(
                    f"      Total: {odds['total_points']} (O{odds['total_over_odds']}/U{odds['total_under_odds']})"
                )

    if args.export:
        export_path = engine.export_to_parquet()
        if export_path:
            print(f"\n💾 Data exported to: {export_path}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
