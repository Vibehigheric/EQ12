import sqlite3
from pathlib import Path

db_path = Path("data/sports_betting.db")
if not db_path.exists():
    print("Database file does not exist")
else:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Existing tables: {tables}")

    if "bets" in tables:
        cursor = conn.execute("PRAGMA table_info(bets)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Bets table columns: {columns}")

    conn.close()
