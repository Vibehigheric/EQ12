#!/usr/bin/env python3
"""
Analytics Report Generator - Aggregate all revenue metrics
Generates comprehensive reports across all revenue streams
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
import argparse

class AnalyticsReporter:
    def __init__(self):
        self.db_path = Path("data/business_intelligence.db")
    
    def get_monthly_revenue(self):
        """Calculate total monthly revenue across all streams"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT SUM(monthly_revenue) as total
                FROM revenue_snapshots
                WHERE timestamp >= datetime('now', '-30 days')
            """)
            
            result = cursor.fetchone()
            total = result[0] if result[0] else 0
            conn.close()
            return total
        except Exception as e:
            print(f"Error: {e}")
            return 0
    
    def get_roi(self):
        """Calculate return on investment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get betting history
            cursor.execute("""
                SELECT SUM(amount) as total_staked FROM bankroll
                WHERE type='bet'
            """)
            
            staked = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT SUM(profit) as total_profit FROM bankroll
                WHERE type='settlement'
            """)
            
            profit = cursor.fetchone()[0] or 0
            conn.close()
            
            if staked == 0:
                return 0
            
            roi = (profit / staked) * 100
            return roi
        except Exception as e:
            print(f"Error: {e}")
            return 0
    
    def get_sharpe_ratio(self):
        """Calculate Sharpe ratio for sports betting"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT profit FROM bankroll
                WHERE type='settlement'
                ORDER BY timestamp DESC
                LIMIT 30
            """)
            
            returns = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            if len(returns) < 2:
                return 0
            
            import statistics
            mean_return = statistics.mean(returns)
            std_dev = statistics.stdev(returns) if len(returns) > 1 else 1
            
            # Annualize if based on daily returns
            sharpe = (mean_return / std_dev) * (252 ** 0.5) if std_dev > 0 else 0
            return sharpe
        except Exception as e:
            return 0
    
    def generate_report(self, metric="all"):
        """Generate analytics report"""
        print("\n" + "=" * 70)
        print("📊 EQ12 ANALYTICS REPORT")
        print("=" * 70)
        
        if metric in ["monthly_revenue", "all"]:
            revenue = self.get_monthly_revenue()
            print(f"\n💰 Monthly Revenue: ${revenue:,.2f}")
            print(f"   Annualized: ${revenue * 12:,.2f}")
        
        if metric in ["roi", "all"]:
            roi = self.get_roi()
            print(f"\n📈 Return on Investment (ROI): {roi:+.2f}%")
        
        if metric in ["sharpe", "all"]:
            sharpe = self.get_sharpe_ratio()
            print(f"\n📊 Sharpe Ratio: {sharpe:.2f}")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analytics Report Generator")
    parser.add_argument("--metric", choices=["monthly_revenue", "roi", "sharpe", "all"], 
                        default="all", help="Specific metric to report")
    
    args = parser.parse_args()
    
    reporter = AnalyticsReporter()
    reporter.generate_report(args.metric)
