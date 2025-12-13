#!/usr/bin/env python3
"""
EQ12 Analytics Report Generator
Comprehensive revenue and performance analytics across all income streams
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class EQ12AnalyticsEngine:
    """Main analytics engine for EQ12 revenue intelligence"""
    
    def __init__(self, workspace_root: str = "C:\\EQ12_BROKEN_20251122_210342"):
        self.workspace = Path(workspace_root)
        self.databases = self._discover_databases()
        
    def _discover_databases(self) -> Dict[str, Path]:
        """Discover all SQLite databases in workspace"""
        dbs = {}
        for db_file in self.workspace.rglob("*.db"):
            dbs[db_file.stem] = db_file
        return dbs
    
    def get_revenue_summary(self) -> Dict:
        """Get comprehensive revenue summary across all streams"""
        summary = {
            "total_daily": 0.0,
            "total_monthly": 0.0,
            "total_annualized": 0.0,
            "streams": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Try business_intelligence.db first
        if "business_intelligence" in self.databases:
            try:
                conn = sqlite3.connect(self.databases["business_intelligence"])
                cursor = conn.cursor()
                
                # Check for revenue_snapshots table
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='revenue_snapshots'
                """)
                
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT 
                            source,
                            SUM(daily_revenue) as daily,
                            COUNT(*) as records
                        FROM revenue_snapshots
                        WHERE timestamp >= datetime('now', '-30 days')
                        GROUP BY source
                        ORDER BY daily DESC
                    """)
                    
                    for row in cursor.fetchall():
                        stream = {
                            "source": row[0],
                            "daily_revenue": float(row[1]) if row[1] else 0.0,
                            "monthly_revenue": float(row[1] * 30) if row[1] else 0.0,
                            "records": row[2]
                        }
                        summary["streams"].append(stream)
                        summary["total_daily"] += stream["daily_revenue"]
                        
                conn.close()
            except Exception as e:
                print(f"Warning: Could not read business_intelligence.db: {e}")
        
        # Calculate totals
        summary["total_monthly"] = summary["total_daily"] * 30
        summary["total_annualized"] = summary["total_monthly"] * 12
        
        return summary
    
    def get_bankroll_status(self) -> Dict:
        """Get current bankroll status from betting databases"""
        status = {
            "current_balance": 0.0,
            "peak_balance": 0.0,
            "total_deposits": 0.0,
            "total_withdrawals": 0.0,
            "roi": 0.0
        }
        
        # Check eq12_betting.db
        if "eq12_betting" in self.databases:
            try:
                conn = sqlite3.connect(self.databases["eq12_betting"])
                cursor = conn.cursor()
                
                # Try to find bankroll table
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    AND name LIKE '%bankroll%'
                """)
                
                tables = cursor.fetchall()
                if tables:
                    table_name = tables[0][0]
                    cursor.execute(f"""
                        SELECT 
                            balance,
                            timestamp
                        FROM {table_name}
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """)
                    
                    row = cursor.fetchone()
                    if row:
                        status["current_balance"] = float(row[0]) if row[0] else 0.0
                        
                conn.close()
            except Exception as e:
                print(f"Warning: Could not read eq12_betting.db: {e}")
        
        return status
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics"""
        metrics = {
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "avg_roi": 0.0,
            "total_bets": 0
        }
        
        # Check eq12_bets.db
        if "eq12_bets" in self.databases:
            try:
                conn = sqlite3.connect(self.databases["eq12_bets"])
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table'
                    LIMIT 5
                """)
                
                tables = [row[0] for row in cursor.fetchall()]
                
                # Try to find bet records
                for table in tables:
                    try:
                        cursor.execute(f"""
                            SELECT COUNT(*) as total,
                                   SUM(CASE WHEN result='win' THEN 1 ELSE 0 END) as wins
                            FROM {table}
                            WHERE result IS NOT NULL
                        """)
                        
                        row = cursor.fetchone()
                        if row and row[0]:
                            metrics["total_bets"] = row[0]
                            metrics["win_rate"] = (row[1] / row[0]) if row[0] > 0 else 0.0
                            break
                    except:
                        continue
                        
                conn.close()
            except Exception as e:
                print(f"Warning: Could not read eq12_bets.db: {e}")
        
        return metrics
    
    def get_database_inventory(self) -> List[Dict]:
        """Get inventory of all databases"""
        inventory = []
        
        for name, path in self.databases.items():
            try:
                size_mb = path.stat().st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(path.stat().st_mtime)
                
                # Count tables
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                conn.close()
                
                inventory.append({
                    "name": name,
                    "path": str(path),
                    "size_mb": round(size_mb, 2),
                    "tables": table_count,
                    "modified": modified.isoformat()
                })
            except Exception as e:
                print(f"Warning: Could not inventory {name}: {e}")
        
        return sorted(inventory, key=lambda x: x["size_mb"], reverse=True)
    
    def generate_full_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "revenue_summary": self.get_revenue_summary(),
            "bankroll_status": self.get_bankroll_status(),
            "performance_metrics": self.get_performance_metrics(),
            "database_inventory": self.get_database_inventory()
        }


def main():
    parser = argparse.ArgumentParser(description="EQ12 Analytics Report Generator")
    parser.add_argument(
        "--metric",
        choices=["revenue", "bankroll", "performance", "inventory", "all"],
        default="all",
        help="Metric to report"
    )
    parser.add_argument(
        "--workspace",
        default="C:\\EQ12_BROKEN_20251122_210342",
        help="Workspace root path"
    )
    parser.add_argument(
        "--output",
        help="Output JSON file path"
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format"
    )
    
    args = parser.parse_args()
    
    engine = EQ12AnalyticsEngine(args.workspace)
    
    # Generate requested metric
    if args.metric == "revenue":
        data = engine.get_revenue_summary()
    elif args.metric == "bankroll":
        data = engine.get_bankroll_status()
    elif args.metric == "performance":
        data = engine.get_performance_metrics()
    elif args.metric == "inventory":
        data = engine.get_database_inventory()
    else:  # all
        data = engine.generate_full_report()
    
    # Output
    if args.format == "json":
        output = json.dumps(data, indent=2)
        print(output)
    else:
        # Text format
        if args.metric == "all" or args.metric == "revenue":
            rev = data if args.metric == "revenue" else data.get("revenue_summary", {})
            print("\n" + "="*70)
            print("📊 REVENUE SUMMARY")
            print("="*70)
            print(f"Daily Revenue:    ${rev.get('total_daily', 0):,.2f}")
            print(f"Monthly Revenue:  ${rev.get('total_monthly', 0):,.2f}")
            print(f"Annualized:       ${rev.get('total_annualized', 0):,.2f}")
            print(f"\nActive Streams:   {len(rev.get('streams', []))}")
            
        if args.metric == "all" or args.metric == "bankroll":
            bank = data if args.metric == "bankroll" else data.get("bankroll_status", {})
            print("\n" + "="*70)
            print("💰 BANKROLL STATUS")
            print("="*70)
            print(f"Current Balance:  ${bank.get('current_balance', 0):,.2f}")
            print(f"ROI:              {bank.get('roi', 0)*100:.2f}%")
            
        if args.metric == "all" or args.metric == "inventory":
            inv = data if args.metric == "inventory" else data.get("database_inventory", [])
            print("\n" + "="*70)
            print("📁 DATABASE INVENTORY")
            print("="*70)
            print(f"Total Databases:  {len(inv)}")
            for db in inv[:10]:  # Top 10
                print(f"  • {db['name']:30s} {db['size_mb']:>8.2f} MB  ({db['tables']} tables)")
    
    # Save to file if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n✅ Report saved to: {output_path}")


if __name__ == "__main__":
    main()
