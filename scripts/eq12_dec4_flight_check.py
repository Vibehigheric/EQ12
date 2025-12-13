#!/usr/bin/env python3
"""
EQ12 December 4th, 2025 Flight Check
Buffalo NY 14215 Content Empire - American Airlines Specific Date
"""

import os
import sys
from datetime import datetime

# EQ12 System Setup
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['EQ12_ASCII_MODE'] = 'ACTIVE'

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from eq12_buffalo_miami_quick_search import QuickFlightFinder

def check_december_4th():
    """Check flights specifically for December 4th, 2025"""

    print()
    print("🗓️  DECEMBER 4TH, 2025 - BUFFALO TO MIAMI")
    print("American Airlines Flight Search")
    print("Buffalo NY 14215 Content Empire")
    print("=" * 55)

    # Create finder instance
    finder = QuickFlightFinder()

    # December 4th, 2025 analysis
    target_date = "2025-12-04"
    dec4_datetime = datetime(2025, 12, 4)
    day_name = dec4_datetime.strftime("%A")

    print(f"📅 Date: December 4th, 2025 ({day_name})")
    print(f"🎯 Routes: Buffalo → Miami/Fort Lauderdale/Palm Beach")
    print()

    # Get prices for all routes
    routes_info = [
        ("BUF", "MIA", "Miami International"),
        ("BUF", "FLL", "Fort Lauderdale"),
        ("BUF", "PBI", "Palm Beach")
    ]

    dec4_deals = []

    for origin, destination, city_name in routes_info:
        deals = finder.get_aa_sample_prices(origin, destination, target_date)
        dec4_deals.extend(deals)

        if deals:
            deal = deals[0]
            stops_text = "Direct" if deal.stops == 0 else f"{deal.stops} stop"
            print(f"📍 Buffalo → {city_name} ({destination})")
            print(f"   💰 ${deal.price:.2f} • ⏱️ {deal.duration} • 🔄 {stops_text}")
            print()

    # Find best deal
    if dec4_deals:
        best_deal = min(dec4_deals, key=lambda x: x.price)

        print("🏆 BEST DEAL FOR DECEMBER 4TH:")
        print(f"   ✈️  {best_deal.route}")
        print(f"   💰 ${best_deal.price:.2f}")
        print(f"   ⏱️  {best_deal.duration}")
        print(f"   🔄 {'Direct flight' if best_deal.stops == 0 else f'{best_deal.stops} stop'}")
        print()

        print("🔗 BOOKING LINKS:")
        print(f"   American Airlines: {best_deal.booking_link}")
        print("   Alternative: https://www.kayak.com/flights/BUF-MIA/2025-12-04")
        print()

        # Day analysis
        print("📊 DECEMBER 4TH ANALYSIS:")
        print(f"   • {day_name} is typically a good day to fly")

        if day_name in ["Tuesday", "Wednesday", "Thursday"]:
            print("   • ✅ Midweek flights often have lower prices")
            print("   • ✅ Less crowded airports and flights")
        elif day_name in ["Friday", "Saturday"]:
            print("   • ⚠️  Weekend travel may cost more")
            print("   • ⚠️  Busier airports expected")
        else:
            print("   • 📊 Monday travel - moderate pricing")

        print("   • Early December = Good timing before holiday rush")
        print("   • Consider booking soon - prices change daily")

        print()
        print("🎯 RECOMMENDATIONS:")
        print("   1. December 4th is excellent timing (before holiday peak)")
        print("   2. Book within next few days for best price lock")
        print("   3. Check baggage fees and seat selection")
        print("   4. Consider travel insurance for winter travel")

    else:
        print("❌ No deals found for December 4th")

if __name__ == "__main__":
    check_december_4th()
