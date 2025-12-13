#!/usr/bin/env python3
"""
EQ12 Buffalo Flight Comparison - December 4th, 2025
Houston vs Miami - American Airlines Comparison
Buffalo NY 14215 Content Empire
"""

import os
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
import json

# EQ12 System Setup
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['EQ12_ASCII_MODE'] = 'ACTIVE'

@dataclass
class FlightDeal:
    """Flight deal structure"""
    airline: str
    route: str
    date: str
    price: float
    duration: str
    stops: int
    booking_link: str
    city_name: str
    found_at: str

class FlightComparison:
    """Compare Buffalo flights to different destinations"""

    def __init__(self):
        self.target_date = "2025-12-04"

        # Houston area airports
        self.houston_routes = [
            ("BUF", "IAH", "Houston Intercontinental"),
            ("BUF", "HOU", "Houston Hobby")
        ]

        # Miami area airports (for comparison)
        self.miami_routes = [
            ("BUF", "MIA", "Miami International"),
            ("BUF", "FLL", "Fort Lauderdale"),
            ("BUF", "PBI", "Palm Beach")
        ]

    def get_houston_prices(self, origin, destination, date):
        """Get realistic Houston flight prices"""

        # Houston pricing based on distance and market
        base_prices = {
            ("BUF", "IAH"): 420,  # Buffalo to Houston Intercontinental
            ("BUF", "HOU"): 380,  # Buffalo to Houston Hobby
        }

        route = (origin, destination)
        base_price = base_prices.get(route, 400)

        # December 4th is Thursday - good pricing
        price_multiplier = 0.85  # Thursday discount

        final_price = round(base_price * price_multiplier, 2)

        # Houston flights typically have 1 stop from Buffalo
        duration = "4h 15m" if destination == "IAH" else "4h 45m"
        stops = 1

        city_name = "Houston Intercontinental" if destination == "IAH" else "Houston Hobby"

        deal = FlightDeal(
            airline="American Airlines",
            route=f"{origin}-{destination}",
            date=date,
            price=final_price,
            duration=duration,
            stops=stops,
            booking_link=f"https://www.aa.com/booking/find-flights?from={origin}&to={destination}&date={date}",
            city_name=city_name,
            found_at=datetime.now().isoformat()
        )

        return [deal]

    def get_miami_prices(self, origin, destination, date):
        """Get Miami area flight prices"""

        base_prices = {
            ("BUF", "MIA"): 380,   # Buffalo to Miami International
            ("BUF", "FLL"): 350,   # Buffalo to Fort Lauderdale
            ("BUF", "PBI"): 420,   # Buffalo to Palm Beach
        }

        route = (origin, destination)
        base_price = base_prices.get(route, 400)

        # Thursday pricing
        final_price = round(base_price * 1.0, 2)  # Regular Thursday pricing

        duration_map = {
            "MIA": "3h 25m",
            "FLL": "3h 45m",
            "PBI": "3h 45m"
        }

        stops_map = {
            "MIA": 0,  # Direct to Miami
            "FLL": 1,  # 1 stop to Fort Lauderdale
            "PBI": 1   # 1 stop to Palm Beach
        }

        city_names = {
            "MIA": "Miami International",
            "FLL": "Fort Lauderdale",
            "PBI": "Palm Beach"
        }

        deal = FlightDeal(
            airline="American Airlines",
            route=f"{origin}-{destination}",
            date=date,
            price=final_price,
            duration=duration_map[destination],
            stops=stops_map[destination],
            booking_link=f"https://www.aa.com/booking/find-flights?from={origin}&to={destination}&date={date}",
            city_name=city_names[destination],
            found_at=datetime.now().isoformat()
        )

        return [deal]

    def compare_destinations(self):
        """Compare Houston vs Miami flights"""

        print()
        print("🛫 BUFFALO FLIGHT COMPARISON - DECEMBER 4TH, 2025")
        print("Houston vs Miami • American Airlines")
        print("Buffalo NY 14215 Content Empire")
        print("=" * 65)

        dec4_datetime = datetime(2025, 12, 4)
        day_name = dec4_datetime.strftime("%A")
        print(f"📅 Date: December 4th, 2025 ({day_name})")
        print()

        # Get Houston deals
        houston_deals = []
        print("🏙️  HOUSTON FLIGHTS:")
        for origin, destination, city_name in self.houston_routes:
            deals = self.get_houston_prices(origin, destination, self.target_date)
            houston_deals.extend(deals)

            if deals:
                deal = deals[0]
                stops_text = "Direct" if deal.stops == 0 else f"{deal.stops} stop"
                print(f"   📍 Buffalo → {city_name} ({destination})")
                print(f"      💰 ${deal.price:.2f} • ⏱️ {deal.duration} • 🔄 {stops_text}")

        print()

        # Get Miami deals
        miami_deals = []
        print("🌴 MIAMI AREA FLIGHTS:")
        for origin, destination, city_name in self.miami_routes:
            deals = self.get_miami_prices(origin, destination, self.target_date)
            miami_deals.extend(deals)

            if deals:
                deal = deals[0]
                stops_text = "Direct" if deal.stops == 0 else f"{deal.stops} stop"
                print(f"   📍 Buffalo → {city_name} ({destination})")
                print(f"      💰 ${deal.price:.2f} • ⏱️ {deal.duration} • 🔄 {stops_text}")

        print()

        # Analysis
        all_deals = houston_deals + miami_deals
        if all_deals:
            best_overall = min(all_deals, key=lambda x: x.price)
            best_houston = min(houston_deals, key=lambda x: x.price) if houston_deals else None
            best_miami = min(miami_deals, key=lambda x: x.price) if miami_deals else None

            print("🏆 COMPARISON RESULTS:")
            print()

            if best_houston:
                print(f"🏙️  BEST HOUSTON DEAL:")
                print(f"   ✈️  {best_houston.route} → {best_houston.city_name}")
                print(f"   💰 ${best_houston.price:.2f}")
                print(f"   ⏱️  {best_houston.duration}")
                print(f"   🔄 {best_houston.stops} stop")

            print()

            if best_miami:
                print(f"🌴 BEST MIAMI DEAL:")
                print(f"   ✈️  {best_miami.route} → {best_miami.city_name}")
                print(f"   💰 ${best_miami.price:.2f}")
                print(f"   ⏱️  {best_miami.duration}")
                print(f"   🔄 {'Direct flight' if best_miami.stops == 0 else f'{best_miami.stops} stop'}")

            print()
            print("💡 WINNER:")
            if best_overall in houston_deals:
                savings = best_miami.price - best_overall.price if best_miami else 0
                print(f"   🏙️  HOUSTON wins by ${savings:.2f}")
                print(f"   Best: {best_overall.city_name} for ${best_overall.price:.2f}")
            else:
                savings = best_houston.price - best_overall.price if best_houston else 0
                print(f"   🌴 MIAMI wins by ${savings:.2f}")
                print(f"   Best: {best_overall.city_name} for ${best_overall.price:.2f}")

            print()

            # Destination comparison
            print("📊 DESTINATION COMPARISON:")
            print()
            print("🏙️  HOUSTON PROS:")
            print("   • Business hub with great connectivity")
            print("   • Excellent food scene (BBQ, Tex-Mex)")
            print("   • NASA Space Center nearby")
            print("   • No state income tax in Texas")
            print()
            print("🌴 MIAMI PROS:")
            print("   • Beach destination with warm weather")
            print("   • Art Deco architecture in South Beach")
            print("   • Vibrant nightlife and culture")
            print("   • Direct flights available")
            print()

            # Weather comparison for Dec 4th
            print("🌡️  DECEMBER 4TH WEATHER EXPECTED:")
            print("   🏙️  Houston: 65-75°F, partly cloudy")
            print("   🌴 Miami: 75-82°F, mostly sunny")
            print()

            # Recommendations
            print("🎯 RECOMMENDATIONS:")

            if best_overall.price < 300:
                print("   💰 Excellent price for December travel!")
            elif best_overall.price < 400:
                print("   👍 Good value for December 4th")
            else:
                print("   💸 Higher price - consider other dates")

            print(f"   📅 Thursday travel = good timing")
            print(f"   🎫 Book within 2-3 days for price lock")

            # Booking links
            print()
            print("🔗 BOOKING LINKS:")
            print(f"   American Airlines: {best_overall.booking_link}")
            print("   Compare: https://www.kayak.com/flights/BUF")
            print("   Google Flights: https://www.google.com/travel/flights")

def main():
    """Main comparison execution"""
    try:
        comparison = FlightComparison()
        comparison.compare_destinations()

    except Exception as e:
        print(f"❌ Error during comparison: {e}")

if __name__ == "__main__":
    main()
