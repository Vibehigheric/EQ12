#!/usr/bin/env python3
"""Extract actual financial data from databases"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def extract_financial_data():
    """Extract all financial/revenue data"""
    data_dir = Path("C:/EQ12_BROKEN_20251122_210342/data")
    
    print("🔍 SEARCHING FOR AVAILABLE FUNDS AND EARNINGS\n")
    print("=" * 60)
    
    # Check betting_learning.db for parlay history
    try:
        conn = sqlite3.connect(data_dir / "betting_learning.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parlay_history LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            cursor.execute("PRAGMA table_info(parlay_history)")
            columns = [col[1] for col in cursor.fetchall()]
            print("\n💰 PARLAY HISTORY:")
            print(f"Columns: {columns}")
            for row in rows:
                print(f"  {row}")
        conn.close()
    except Exception as e:
        print(f"❌ betting_learning.db: {e}")
    
    # Check copywriting_empire.db for revenue
    try:
        conn = sqlite3.connect(data_dir / "copywriting_empire.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM revenue_streams LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            cursor.execute("PRAGMA table_info(revenue_streams)")
            columns = [col[1] for col in cursor.fetchall()]
            print("\n📊 COPYWRITING REVENUE STREAMS:")
            print(f"Columns: {columns}")
            for row in rows:
                print(f"  {row}")
        
        # Check empire_performance
        cursor.execute("SELECT COUNT(*) FROM empire_performance")
        count = cursor.fetchone()[0]
        if count > 0:
            cursor.execute("SELECT * FROM empire_performance LIMIT 3")
            rows = cursor.fetchall()
            cursor.execute("PRAGMA table_info(empire_performance)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"\n📈 EMPIRE PERFORMANCE ({count} records):")
            print(f"Columns: {columns}")
            for row in rows:
                print(f"  {row}")
        
        conn.close()
    except Exception as e:
        print(f"❌ copywriting_empire.db: {e}")
    
    # Check business_intelligence.db for snapshots
    try:
        conn = sqlite3.connect(data_dir / "business_intelligence.db")
        cursor = conn.cursor()
        
        # Revenue snapshots
        cursor.execute("SELECT COUNT(*) FROM revenue_snapshots")
        count = cursor.fetchone()[0]
        print(f"\n💵 REVENUE SNAPSHOTS: {count} records")
        
        if count > 0:
            cursor.execute("SELECT * FROM revenue_snapshots ORDER BY rowid DESC LIMIT 3")
            rows = cursor.fetchall()
            cursor.execute("PRAGMA table_info(revenue_snapshots)")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns: {columns}")
            for row in rows:
                print(f"  {row}")
        
        # Business metrics
        cursor.execute("SELECT COUNT(*) FROM business_metrics")
        count = cursor.fetchone()[0]
        print(f"\n📊 BUSINESS METRICS: {count} records")
        
        if count > 0:
            cursor.execute("SELECT DISTINCT substr(timestamp, 1, 10) as date FROM business_metrics ORDER BY date DESC LIMIT 5")
            dates = cursor.fetchall()
            print(f"Most recent dates: {[d[0] for d in dates]}")
        
        conn.close()
    except Exception as e:
        print(f"❌ business_intelligence.db: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    extract_financial_data()
