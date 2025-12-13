#!/usr/bin/env python3
"""
EQ12 Database Migration and Schema Upgrade Tool

This script fixes the database schema issues identified in the EQ12 Sports Betting System:
- Missing 'clv' (Closing Line Value) column in bets table
- Missing 'edge_id' foreign key in bets table
- Ensures all tables have proper indexes and constraints

Author: EQ12 System
Created: 2025-10-04
"""

import logging
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/database_migration.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class EQ12DatabaseMigrator:
    """Database schema migration and upgrade tool"""

    def __init__(self, db_path: str = "data/sports_betting.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def backup_database(self) -> str:
        """Create a backup of the current database"""
        if not self.db_path.exists():
            logger.info("No existing database to backup")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.db_path}.backup_{timestamp}"

        try:
            # Copy database file
            import shutil

            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            return ""

    def check_schema_version(self) -> int:
        """Check current schema version"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute(
                "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
            )
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else 0
        except sqlite3.OperationalError:
            # schema_version table doesn't exist
            return 0

    def update_schema_version(self, version: int):
        """Update schema version tracking"""
        conn = sqlite3.connect(str(self.db_path))

        # Create schema_version table if it doesn't exist
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """
        )

        # Insert new version
        conn.execute(
            """
            INSERT INTO schema_version (version, description)
            VALUES (?, ?)
        """,
            (version, f"EQ12 Schema Migration v{version}"),
        )

        conn.commit()
        conn.close()
        logger.info(f"Schema updated to version {version}")

    def migration_v1_add_missing_columns(self):
        """Migration 1: Add missing CLV and edge_id columns to bets table"""
        logger.info("Running Migration v1: Adding missing columns to bets table")

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(bets)")
        columns = [column[1] for column in cursor.fetchall()]

        try:
            # Add edge_id column if missing
            if "edge_id" not in columns:
                cursor.execute("ALTER TABLE bets ADD COLUMN edge_id INTEGER")
                logger.info("Added edge_id column to bets table")

            # Add clv column if missing
            if "clv" not in columns:
                cursor.execute("ALTER TABLE bets ADD COLUMN clv REAL")
                logger.info("Added clv column to bets table")

            # Create index on edge_id for performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_bets_edge_id ON bets(edge_id)
            """
            )

            conn.commit()
            logger.info("Migration v1 completed successfully")

        except Exception as e:
            logger.error(f"Migration v1 failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def migration_v2_create_missing_tables(self):
        """Migration 2: Ensure all required tables exist with proper schema"""
        logger.info("Running Migration v2: Creating missing tables")

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            # Create all tables with complete schema
            table_definitions = [
                """
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sport TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    game_time TIMESTAMP NOT NULL,
                    season INTEGER,
                    week INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS odds_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    bookmaker TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    odds_data JSON NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games (id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS team_ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_name TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    elo_rating REAL DEFAULT 1500,
                    power_rating REAL,
                    season INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(team_name, sport, season)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS betting_edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    market_type TEXT NOT NULL,
                    bookmaker TEXT NOT NULL,
                    edge_percentage REAL NOT NULL,
                    recommended_stake REAL,
                    confidence_level REAL,
                    analysis_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games (id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    edge_id INTEGER,
                    bet_type TEXT NOT NULL,
                    stake REAL NOT NULL,
                    odds REAL NOT NULL,
                    potential_payout REAL,
                    bet_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    result TEXT,
                    profit_loss REAL,
                    clv REAL,
                    bookmaker TEXT,
                    notes TEXT,
                    FOREIGN KEY (game_id) REFERENCES games (id),
                    FOREIGN KEY (edge_id) REFERENCES betting_edges (id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS injury_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_name TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    injury_status TEXT NOT NULL,
                    injury_description TEXT,
                    impact_rating INTEGER CHECK(impact_rating BETWEEN 1 AND 10),
                    report_date DATE NOT NULL,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS twitter_sentiment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_name TEXT NOT NULL,
                    game_id INTEGER,
                    sentiment_score REAL CHECK(sentiment_score BETWEEN -1.0 AND 1.0),
                    tweet_volume INTEGER DEFAULT 0,
                    analysis_data JSON,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games (id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS bankroll_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    change_amount REAL,
                    change_reason TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_date DATE NOT NULL,
                    total_bets INTEGER DEFAULT 0,
                    winning_bets INTEGER DEFAULT 0,
                    total_profit REAL DEFAULT 0,
                    avg_clv REAL DEFAULT 0,
                    roi REAL DEFAULT 0,
                    bankroll_value REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(metric_date)
                )
                """,
            ]

            for table_sql in table_definitions:
                cursor.execute(table_sql)

            # Create useful indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_games_sport_time ON games(sport, game_time)",
                "CREATE INDEX IF NOT EXISTS idx_odds_game_bookmaker ON odds_snapshots(game_id, bookmaker)",
                "CREATE INDEX IF NOT EXISTS idx_edges_game_confidence ON betting_edges(game_id, confidence_level DESC)",
                "CREATE INDEX IF NOT EXISTS idx_bets_time ON bets(bet_time)",
                "CREATE INDEX IF NOT EXISTS idx_bets_result ON bets(result)",
                "CREATE INDEX IF NOT EXISTS idx_injuries_team_date ON injury_reports(team_name, report_date)",
                "CREATE INDEX IF NOT EXISTS idx_sentiment_team_time ON twitter_sentiment(team_name, timestamp)",
            ]

            for index_sql in indexes:
                cursor.execute(index_sql)

            conn.commit()
            logger.info("Migration v2 completed successfully")

        except Exception as e:
            logger.error(f"Migration v2 failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def migration_v3_data_validation(self):
        """Migration 3: Validate and fix data inconsistencies"""
        logger.info("Running Migration v3: Data validation and cleanup")

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            # Set default CLV values for existing bets without CLV
            cursor.execute(
                """
                UPDATE bets
                SET clv = 0.0
                WHERE clv IS NULL
            """
            )

            # Initialize bankroll if empty
            cursor.execute("SELECT COUNT(*) FROM bankroll_history")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO bankroll_history (amount, change_reason)
                    VALUES (1000.0, 'Initial bankroll setup')
                """
                )
                logger.info("Initialized bankroll with $1000")

            conn.commit()
            logger.info("Migration v3 completed successfully")

        except Exception as e:
            logger.error(f"Migration v3 failed: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def run_full_migration(self):
        """Run complete database migration"""
        logger.info("Starting EQ12 Database Migration")

        # Create backup
        backup_path = self.backup_database()

        try:
            current_version = self.check_schema_version()
            logger.info(f"Current schema version: {current_version}")

            # Always ensure tables exist first (Migration v2)
            if current_version < 2:
                self.migration_v2_create_missing_tables()
                self.update_schema_version(2)

            # Then add missing columns (Migration v1)
            if current_version < 1:
                self.migration_v1_add_missing_columns()
                self.update_schema_version(1)

            # Finally validate data (Migration v3)
            if current_version < 3:
                self.migration_v3_data_validation()
                self.update_schema_version(3)

            logger.info("Database migration completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            if backup_path and os.path.exists(backup_path):
                logger.info(f"Database backup available at: {backup_path}")
            return False

    def validate_schema(self) -> bool:
        """Validate that all required tables and columns exist"""
        logger.info("Validating database schema")

        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Check required tables exist
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN (
                    'games', 'odds_snapshots', 'team_ratings',
                    'betting_edges', 'bets', 'injury_reports',
                    'twitter_sentiment', 'bankroll_history', 'performance_metrics'
                )
            """
            )

            existing_tables = [row[0] for row in cursor.fetchall()]
            required_tables = [
                "games",
                "odds_snapshots",
                "team_ratings",
                "betting_edges",
                "bets",
                "injury_reports",
                "twitter_sentiment",
                "bankroll_history",
                "performance_metrics",
            ]

            missing_tables = set(required_tables) - set(existing_tables)
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False

            # Check bets table has required columns
            cursor.execute("PRAGMA table_info(bets)")
            bet_columns = [column[1] for column in cursor.fetchall()]

            required_bet_columns = ["edge_id", "clv"]
            missing_columns = set(required_bet_columns) - set(bet_columns)

            if missing_columns:
                logger.error(f"Missing columns in bets table: {missing_columns}")
                return False

            conn.close()
            logger.info("Schema validation passed!")
            return True

        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False


def main():
    """Main migration function"""
    print("EQ12 Database Migration Tool")
    print("============================")

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    migrator = EQ12DatabaseMigrator()

    # Run migration
    success = migrator.run_full_migration()

    if success:
        # Validate the result
        if migrator.validate_schema():
            print("\n✅ Database migration completed successfully!")
            print("✅ Schema validation passed!")
            sys.exit(0)
        else:
            print("\n❌ Migration completed but schema validation failed!")
            sys.exit(1)
    else:
        print("\n❌ Database migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
