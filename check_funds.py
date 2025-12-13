#!/usr/bin/env python3
"""Check available funds and earnings from databases"""

import sqlite3
import json
from pathlib import Path

def check_db(db_path):
    """Check database for financial info"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n=== {db_path.name} ===")
            for table in tables:
                table_name = table[0]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  {table_name}: {count} records")
                    
                    # Show columns
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    col_names = [col[1] for col in columns]
                    if any(k in col_names for k in ['balance', 'earnings', 'revenue', 'amount', 'profit']):
                        print(f"    Columns: {', '.join(col_names)}")
                except Exception as e:
                    pass
        
        conn.close()
    except Exception as e:
        pass

# Check key databases
data_dir = Path("C:/EQ12_BROKEN_20251122_210342/data")
key_dbs = [
    "betting_history.db",
    "betting_learning.db", 
    "copywriting_empire.db",
    "business_intelligence.db",
    "coral_ethereum_intelligence.db",
    "ai_cache.db",
]

for db_name in key_dbs:
    db_path = data_dir / db_name
    if db_path.exists():
        check_db(db_path)

print("\n✅ Database scan complete")
