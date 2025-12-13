import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'bets.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database with the required schema."""
    conn = get_connection()
    cursor = conn.cursor()

    # Bets Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_placed TEXT NOT NULL,
        sport TEXT NOT NULL,
        league TEXT,
        market TEXT NOT NULL,
        selection TEXT NOT NULL,
        odds_decimal REAL NOT NULL,
        stake REAL NOT NULL,
        sportsbook TEXT NOT NULL,
        implied_prob REAL,
        expected_edge REAL,
        true_probability REAL, -- New: True probability from model
        reasoning TEXT,
        model_name TEXT,
        tag TEXT,
        
        -- Metadata (JSON) for Sport Specifics (Pitcher, Weather, Injuries)
        metadata TEXT, 

        -- Settlement Columns
        status TEXT DEFAULT 'PENDING', -- PENDING, WON, LOST, PUSH, VOID
        profit REAL DEFAULT 0.0,
        closing_odds REAL,
        clv REAL,
        date_settled TEXT
    )
    ''')

    # Performance Metrics Table (Snapshot for weekly reviews)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance_snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_generated TEXT NOT NULL,
        total_bets INTEGER,
        total_profit REAL,
        roi REAL,
        win_rate REAL,
        clv_avg REAL,
        notes TEXT
    )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
