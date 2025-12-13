#!/usr/bin/env python3
"""Get detailed financial summary"""

import sqlite3
from pathlib import Path

def get_financial_summary():
    """Get comprehensive financial summary"""
    data_dir = Path("C:/EQ12_BROKEN_20251122_210342/data")
    
    print("\n" + "=" * 70)
    print("💎 EQ12 FINANCIAL ASSETS & AVAILABLE FUNDS SUMMARY")
    print("=" * 70)
    
    # Get revenue snapshots - LATEST DATA
    try:
        conn = sqlite3.connect(data_dir / "business_intelligence.db")
        cursor = conn.cursor()
        
        # Get latest revenue snapshots
        cursor.execute("""
            SELECT stream_name, daily_revenue, monthly_revenue, timestamp 
            FROM revenue_snapshots 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        
        print("\n📊 LATEST REVENUE SNAPSHOTS (Top Streams):")
        print("-" * 70)
        
        total_daily = 0
        total_monthly = 0
        
        for row in cursor.fetchall():
            stream_name, daily, monthly, ts = row
            total_daily += daily
            total_monthly += monthly
            print(f"  {stream_name[:40]:40} | Daily: ${daily:>12,.2f} | Monthly: ${monthly:>15,.2f}")
            print(f"    └─ Last updated: {ts}")
        
        print("-" * 70)
        print(f"  TOTAL DAILY REVENUE:    ${total_daily:,.2f}")
        print(f"  TOTAL MONTHLY REVENUE:  ${total_monthly:,.2f}")
        print(f"  ANNUALIZED REVENUE:     ${total_monthly * 12:,.2f}")
        
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")
    
    # Get copywriting revenue
    try:
        conn = sqlite3.connect(data_dir / "copywriting_empire.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT stream_name, monthly_target, current_revenue, status
            FROM revenue_streams
            ORDER BY monthly_target DESC
        """)
        
        print("\n💰 COPYWRITING REVENUE STREAMS (Targets):")
        print("-" * 70)
        
        total_target = 0
        total_current = 0
        
        rows = cursor.fetchall()
        for stream_name, target, current, status in rows:
            total_target += target
            total_current += current
            pct = (current / target * 100) if target > 0 else 0
            status_icon = "✅" if status == "deployed" else "⏳"
            print(f"  {status_icon} {stream_name[:35]:35} | Target: ${target:>8,.0f} | Current: ${current:>10,.2f} ({pct:>5.1f}%)")
        
        print("-" * 70)
        print(f"  TOTAL TARGET:  ${total_target:,.2f}")
        print(f"  TOTAL CURRENT: ${total_current:,.2f}")
        
        conn.close()
    except Exception as e:
        print(f"  Error: {e}")
    
    # Check for payment processor accounts
    print("\n🔐 PAYMENT PROCESSOR INTEGRATIONS:")
    print("-" * 70)
    
    try:
        # Look for config files
        config_path = Path("C:/EQ12_BROKEN_20251122_210342/config")
        gumroad_configs = list(config_path.glob("*gumroad*.json"))
        
        if gumroad_configs:
            print(f"  ✅ Gumroad: {len(gumroad_configs)} config file(s) found")
            for cfg in gumroad_configs:
                print(f"     └─ {cfg.name}")
        
        # Check for other payment processors
        stripe_cfg = list(config_path.glob("*stripe*"))
        paypal_cfg = list(config_path.glob("*paypal*"))
        
        if stripe_cfg:
            print(f"  ✅ Stripe: {len(stripe_cfg)} config(s)")
        if paypal_cfg:
            print(f"  ✅ PayPal: {len(paypal_cfg)} config(s)")
        
    except Exception as e:
        pass
    
    # Summary
    print("\n" + "=" * 70)
    print("💡 NEXT STEPS TO CLAIM FUNDS:")
    print("=" * 70)
    print("""
1. GUMROAD MARKETPLACE
   - Products created and listed on Gumroad
   - Check dashboard: https://gumroad.com/dashboard
   - Earnings are in "Creator Account" balance
   - Withdraw via bank account or PayPal
   
2. BETTING/SPORTS REVENUE  
   - Active parlay tracking system running
   - Database shows historical data
   - Bankroll manager available for tracking
   
3. COPYWRITING EMPIRE
   - 12 revenue streams configured
   - Targets: Premium courses, done-for-you services, coaching
   - Current revenue: $0 (awaiting first sales)
   
4. RECOMMENDED ACTIONS:
   - Run: python EQ12_2025_MASTER_ORCHESTRATOR.py --mode all
   - Monitor dashboard: reports/revenue_dashboard.html
   - Check Gumroad account for active sales
   - Set up payment processor webhooks
   - Verify bank/PayPal connection for payouts
""")
    
    print("=" * 70)

if __name__ == "__main__":
    get_financial_summary()
