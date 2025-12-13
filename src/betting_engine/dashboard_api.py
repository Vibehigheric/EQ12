import json
import sqlite3
import sys
import os
from datetime import datetime

# Add parent directory to path to allow imports if run directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from betting_engine.database import get_connection
# from betting_engine.analytics import generate_report 

def export_dashboard_data(output_path="dashboard_data.json"):
    """
    Exports all critical betting data to a JSON file for the VB.NET Dashboard.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    data = {
        "generated_at": str(datetime.now()),
        "stats": {},
        "recent_bets": [],
        "alerts": []
    }

    # 1. Stats
    try:
        cursor.execute("SELECT SUM(profit), COUNT(*), AVG(clv) FROM bets WHERE status != 'PENDING'")
        row = cursor.fetchone()
        if row:
            data["stats"]["total_profit"] = row[0] if row[0] else 0.0
            data["stats"]["total_bets"] = row[1]
            data["stats"]["avg_clv"] = row[2] if row[2] else 0.0
    except Exception as e:
        print(f"Error fetching stats: {e}")

    # 2. Recent Bets
    try:
        cursor.execute("SELECT id, date_placed, selection, market, odds_decimal, stake, status, profit FROM bets ORDER BY id DESC LIMIT 10")
        bets = cursor.fetchall()
        for bet in bets:
            data["recent_bets"].append({
                "id": bet[0],
                "date": bet[1],
                "selection": bet[2],
                "market": bet[3],
                "odds": bet[4],
                "stake": bet[5],
                "status": bet[6],
                "profit": bet[7]
            })
    except Exception as e:
        print(f"Error fetching bets: {e}")

    # 3. Alerts (Mock - would come from Scanner)
    data["alerts"].append({"type": "INFO", "message": "Dashboard Data Updated"})

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"Dashboard data exported to {output_path}")
    conn.close()

if __name__ == "__main__":
    from datetime import datetime
    export_dashboard_data()
