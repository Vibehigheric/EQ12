#!/usr/bin/env python3
"""
Gumroad Marketplace Integration - Sync sales and earnings
Fetches latest Gumroad sales data and updates local database
"""

import os
import sqlite3
import json
from datetime import datetime
import requests
import argparse
from pathlib import Path

class GumroadSync:
    def __init__(self):
        self.gumroad_token = os.getenv("GUMROAD_API_TOKEN")
        self.base_url = "https://api.gumroad.com/v2"
        self.db_path = Path("data/business_intelligence.db")
        
    def fetch_sales(self):
        """Fetch latest sales from Gumroad API"""
        try:
            headers = {"Authorization": f"Bearer {self.gumroad_token}"}
            response = requests.get(
                f"{self.base_url}/me/sales",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get("sales", [])
            else:
                print(f"❌ API Error: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error fetching Gumroad sales: {e}")
            return []
    
    def update_database(self, sales):
        """Update local database with sales data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for sale in sales:
                cursor.execute("""
                    INSERT OR REPLACE INTO revenue_snapshots 
                    (stream_name, daily_revenue, monthly_revenue, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (
                    f"gumroad_{sale.get('product_name', 'unknown')}",
                    float(sale.get('price', 0)) / 100,  # Convert cents to dollars
                    float(sale.get('price', 0)) / 100 * 30,  # Rough monthly estimate
                    datetime.utcnow().isoformat()
                ))
            
            conn.commit()
            conn.close()
            print(f"✅ Updated {len(sales)} sales records in database")
            
        except Exception as e:
            print(f"❌ Error updating database: {e}")
    
    def get_earnings_summary(self):
        """Get total earnings from Gumroad"""
        try:
            headers = {"Authorization": f"Bearer {self.gumroad_token}"}
            response = requests.get(
                f"{self.base_url}/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json().get("user", {})
                earnings = user.get("total_payout_cents", 0) / 100
                print(f"💰 Total Gumroad Earnings: ${earnings:,.2f}")
                return earnings
            else:
                print("❌ Could not fetch earnings summary")
                return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 0
    
    def sync(self):
        """Run full sync operation"""
        print("🔄 Syncing Gumroad data...")
        
        if not self.gumroad_token:
            print("⚠️  GUMROAD_API_TOKEN not set. Set environment variable:")
            print("   setx GUMROAD_API_TOKEN \"your_token_here\"")
            return
        
        sales = self.fetch_sales()
        if sales:
            self.update_database(sales)
        
        self.get_earnings_summary()
        print("✅ Gumroad sync complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gumroad Marketplace Sync")
    parser.add_argument("--update", action="store_true", help="Update database with sales")
    parser.add_argument("--earnings", action="store_true", help="Show earnings summary")
    
    args = parser.parse_args()
    
    syncer = GumroadSync()
    
    if args.earnings:
        syncer.get_earnings_summary()
    else:
        syncer.sync()
