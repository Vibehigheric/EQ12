#!/usr/bin/env python3
"""
EQ12 American Airlines Flight Hunter - Buffalo to Miami December 2025
Buffalo NY 14215 Content Empire - Advanced Flight Search & Deal Detection

Multi-source flight search with price tracking, deal alerts, and booking automation.
Supports American Airlines direct and codeshare flights to Miami area airports.
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Import required modules with error handling
try:
    import aiohttp
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install aiohttp requests beautifulsoup4 pandas selenium")
    sys.exit(1)

# EQ12 System Configuration
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['EQ12_ASCII_MODE'] = 'ACTIVE'

@dataclass
class FlightDeal:
    """Flight deal data structure for EQ12 system"""
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_date: str
    departure_time: str
    arrival_date: str
    arrival_time: str
    duration: str
    stops: int
    price: float
    currency: str
    booking_class: str
    aircraft_type: str
    source: str
    deal_score: float
    availability: str
    last_updated: str
    deep_link: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class FlightSearchEngine:
    """Advanced flight search engine for American Airlines Buffalo-Miami routes"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        # Buffalo and Miami area airports
        self.origin_airports = ['BUF']  # Buffalo Niagara International
        self.destination_airports = [
            'MIA',  # Miami International (Primary)
            'FLL',  # Fort Lauderdale-Hollywood
            'PBI',  # Palm Beach International
            'FXE',  # Fort Lauderdale Executive
            'OPF',  # Miami-Opa-Locka Executive
            'TMB'   # Miami-Kendall-Tamiami Executive
        ]

        # December 2025 search parameters
        self.search_dates = self._generate_december_dates()

        # Flight sources and APIs
        self.sources = {
            'american_airlines': 'https://www.aa.com',
            'kayak': 'https://www.kayak.com',
            'expedia': 'https://www.expedia.com',
            'google_flights': 'https://www.google.com/travel/flights',
            'momondo': 'https://www.momondo.com',
            'skyscanner': 'https://www.skyscanner.com'
        }

        self.deals = []

    def _setup_logging(self) -> logging.Logger:
        """Setup EQ12 compliant logging"""
        logger = logging.getLogger('eq12_flight_search')
        logger.setLevel(logging.INFO)

        # Create logs directory if not exists
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # JSON log handler
        log_file = os.path.join(log_dir, f'eq12_flight_search_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        handler = logging.FileHandler(log_file, encoding='ascii')

        # ASCII-safe formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def _generate_december_dates(self) -> List[str]:
        """Generate all December 2025 dates for searching"""
        dates = []
        start_date = datetime(2025, 12, 1)

        for day in range(31):
            current_date = start_date + timedelta(days=day)
            dates.append(current_date.strftime('%Y-%m-%d'))

        return dates

    def _create_webdriver(self) -> webdriver.Chrome:
        """Create Selenium WebDriver with optimized settings"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Disable images for faster loading
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create WebDriver: {e}")
            raise

    async def search_american_airlines(self, origin: str, destination: str, date: str) -> List[FlightDeal]:
        """Search American Airlines website directly"""
        self.logger.info(f"Searching American Airlines: {origin} -> {destination} on {date}")

        deals = []
        driver = None

        try:
            driver = self._create_webdriver()

            # Build AA search URL
            search_url = (
                f"https://www.aa.com/booking/find-flights?"
                f"tripType=OneWay&"
                f"from={origin}&"
                f"to={destination}&"
                f"departDate={date}&"
                f"passengers=1&"
                f"cabinType=economy"
            )

            driver.get(search_url)

            # Wait for results to load
            wait = WebDriverWait(driver, 20)

            try:
                # Wait for flight results container
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='flight-results']")))

                # Extract flight information
                flight_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='flight-option']")

                for flight_elem in flight_elements[:10]:  # Top 10 flights
                    try:
                        # Extract flight details
                        flight_number = self._safe_extract_text(flight_elem, "[data-testid='flight-number']")
                        departure_time = self._safe_extract_text(flight_elem, "[data-testid='departure-time']")
                        arrival_time = self._safe_extract_text(flight_elem, "[data-testid='arrival-time']")
                        duration = self._safe_extract_text(flight_elem, "[data-testid='duration']")
                        stops = self._extract_stops(flight_elem)
                        price_text = self._safe_extract_text(flight_elem, "[data-testid='price']")
                        aircraft = self._safe_extract_text(flight_elem, "[data-testid='aircraft']")

                        # Parse price
                        price = self._parse_price(price_text)

                        if price and flight_number:
                            deal = FlightDeal(
                                airline='American Airlines',
                                flight_number=flight_number,
                                departure_airport=origin,
                                arrival_airport=destination,
                                departure_date=date,
                                departure_time=departure_time,
                                arrival_date=date,
                                arrival_time=arrival_time,
                                duration=duration,
                                stops=stops,
                                price=price,
                                currency='USD',
                                booking_class='Economy',
                                aircraft_type=aircraft,
                                source='American Airlines',
                                deal_score=self._calculate_deal_score(price, stops, duration),
                                availability='Available',
                                last_updated=datetime.now().isoformat(),
                                deep_link=search_url
                            )

                            deals.append(deal)
                            self.logger.info(f"Found AA flight: {flight_number} - ${price}")

                    except Exception as e:
                        self.logger.warning(f"Error extracting flight details: {e}")
                        continue

            except TimeoutException:
                self.logger.warning(f"Timeout waiting for AA results: {origin} -> {destination} on {date}")

        except Exception as e:
            self.logger.error(f"Error searching American Airlines: {e}")

        finally:
            if driver:
                driver.quit()

        return deals

    async def search_kayak(self, origin: str, destination: str, date: str) -> List[FlightDeal]:
        """Search Kayak for American Airlines flights"""
        self.logger.info(f"Searching Kayak: {origin} -> {destination} on {date}")

        deals = []
        driver = None

        try:
            driver = self._create_webdriver()

            # Build Kayak search URL
            search_url = (
                f"https://www.kayak.com/flights/{origin}-{destination}/{date}?"
                f"sort=price_a&"
                f"airlines=AA"  # American Airlines filter
            )

            driver.get(search_url)

            # Wait for results
            wait = WebDriverWait(driver, 25)

            try:
                # Wait for flight results
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-resultid]")))

                # Extract flight results
                flight_elements = driver.find_elements(By.CSS_SELECTOR, "[data-resultid]")

                for flight_elem in flight_elements[:15]:  # Top 15 flights
                    try:
                        # Check if it's American Airlines
                        airline_elem = flight_elem.find_element(By.CSS_SELECTOR, ".airline-logo, .airline-name")
                        if 'american' not in airline_elem.get_attribute('alt').lower():
                            continue

                        # Extract details
                        times = flight_elem.find_elements(By.CSS_SELECTOR, ".time")
                        departure_time = times[0].text if len(times) > 0 else ""
                        arrival_time = times[1].text if len(times) > 1 else ""

                        duration_elem = flight_elem.find_element(By.CSS_SELECTOR, ".duration")
                        duration = duration_elem.text

                        stops_elem = flight_elem.find_element(By.CSS_SELECTOR, ".stops")
                        stops = 0 if 'nonstop' in stops_elem.text.lower() else 1

                        price_elem = flight_elem.find_element(By.CSS_SELECTOR, ".price")
                        price = self._parse_price(price_elem.text)

                        if price:
                            deal = FlightDeal(
                                airline='American Airlines',
                                flight_number='AA-TBD',  # Kayak doesn't always show flight numbers
                                departure_airport=origin,
                                arrival_airport=destination,
                                departure_date=date,
                                departure_time=departure_time,
                                arrival_date=date,
                                arrival_time=arrival_time,
                                duration=duration,
                                stops=stops,
                                price=price,
                                currency='USD',
                                booking_class='Economy',
                                aircraft_type='TBD',
                                source='Kayak',
                                deal_score=self._calculate_deal_score(price, stops, duration),
                                availability='Available',
                                last_updated=datetime.now().isoformat(),
                                deep_link=search_url
                            )

                            deals.append(deal)
                            self.logger.info(f"Found Kayak flight: ${price}")

                    except (NoSuchElementException, Exception) as e:
                        continue

            except TimeoutException:
                self.logger.warning(f"Timeout waiting for Kayak results: {origin} -> {destination}")

        except Exception as e:
            self.logger.error(f"Error searching Kayak: {e}")

        finally:
            if driver:
                driver.quit()

        return deals

    def _safe_extract_text(self, parent_element, selector: str) -> str:
        """Safely extract text from an element"""
        try:
            element = parent_element.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except (NoSuchElementException, Exception):
            return ""

    def _extract_stops(self, flight_element) -> int:
        """Extract number of stops from flight element"""
        try:
            stops_text = self._safe_extract_text(flight_element, "[data-testid='stops'], .stops")
            if 'nonstop' in stops_text.lower() or 'direct' in stops_text.lower():
                return 0
            elif '1 stop' in stops_text.lower():
                return 1
            elif '2 stop' in stops_text.lower():
                return 2
            else:
                return 0
        except:
            return 0

    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price from text string"""
        if not price_text:
            return None

        # Remove currency symbols and extract numeric value
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if price_match:
            try:
                return float(price_match.group())
            except ValueError:
                return None
        return None

    def _calculate_deal_score(self, price: float, stops: int, duration: str) -> float:
        """Calculate deal score (higher = better deal)"""
        base_score = 100

        # Price factor (lower price = higher score)
        if price < 200:
            price_score = 50
        elif price < 300:
            price_score = 40
        elif price < 400:
            price_score = 30
        elif price < 500:
            price_score = 20
        else:
            price_score = 10

        # Stops penalty
        stops_score = max(0, 30 - (stops * 15))

        # Duration factor (extract hours)
        duration_score = 20
        if duration:
            duration_match = re.search(r'(\d+)h', duration)
            if duration_match:
                hours = int(duration_match.group(1))
                if hours <= 3:
                    duration_score = 20
                elif hours <= 5:
                    duration_score = 15
                elif hours <= 8:
                    duration_score = 10
                else:
                    duration_score = 5

        return price_score + stops_score + duration_score

    async def search_all_sources(self) -> List[FlightDeal]:
        """Search all sources for the best American Airlines deals"""
        self.logger.info("Starting comprehensive American Airlines flight search...")

        all_deals = []

        for origin in self.origin_airports:
            for destination in self.destination_airports:
                for date in self.search_dates[:10]:  # Search first 10 days of December
                    try:
                        # Search American Airlines directly
                        aa_deals = await self.search_american_airlines(origin, destination, date)
                        all_deals.extend(aa_deals)

                        # Search Kayak
                        kayak_deals = await self.search_kayak(origin, destination, date)
                        all_deals.extend(kayak_deals)

                        # Add delay to avoid being blocked
                        await asyncio.sleep(2)

                    except Exception as e:
                        self.logger.error(f"Error searching {origin}->{destination} on {date}: {e}")
                        continue

        self.deals = all_deals
        return all_deals

    def analyze_deals(self) -> Dict[str, Any]:
        """Analyze and rank flight deals"""
        if not self.deals:
            return {"error": "No deals found"}

        # Sort by deal score (highest first)
        sorted_deals = sorted(self.deals, key=lambda x: x.deal_score, reverse=True)

        # Calculate statistics
        prices = [deal.price for deal in self.deals if deal.price]

        analysis = {
            "total_deals_found": len(self.deals),
            "best_deal": sorted_deals[0].to_dict() if sorted_deals else None,
            "average_price": sum(prices) / len(prices) if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "direct_flights": [deal.to_dict() for deal in sorted_deals if deal.stops == 0],
            "cheapest_flights": sorted(self.deals, key=lambda x: x.price or float('inf'))[:5],
            "airports_searched": {
                "origins": self.origin_airports,
                "destinations": self.destination_airports
            },
            "search_dates": self.search_dates[:10],
            "last_updated": datetime.now().isoformat()
        }

        return analysis

    def save_results(self, analysis: Dict[str, Any]) -> str:
        """Save search results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eq12_american_airlines_buffalo_miami_dec2025_{timestamp}.json"
        filepath = os.path.join("logs", filename)

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Save results
        with open(filepath, 'w', encoding='ascii', errors='replace') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=True)

        self.logger.info(f"Results saved to: {filepath}")
        return filepath

    def print_best_deals(self, analysis: Dict[str, Any], top_n: int = 10):
        """Print the best deals to console"""
        print("\n" + "="*80)
        print("🛫 EQ12 AMERICAN AIRLINES FLIGHT SEARCH RESULTS")
        print("Buffalo (BUF) -> Miami/South Florida - December 2025")
        print("Buffalo NY 14215 Content Empire - Flight Intelligence")
        print("="*80)

        if analysis.get("error"):
            print(f"❌ Error: {analysis['error']}")
            return

        print(f"\n📊 SEARCH SUMMARY:")
        print(f"Total deals found: {analysis['total_deals_found']}")
        print(f"Average price: ${analysis['average_price']:.2f}")
        print(f"Price range: ${analysis['min_price']:.2f} - ${analysis['max_price']:.2f}")
        print(f"Direct flights available: {len(analysis['direct_flights'])}")

        if analysis.get("best_deal"):
            best = analysis["best_deal"]
            print(f"\n🏆 BEST OVERALL DEAL:")
            print(f"Flight: {best['airline']} {best['flight_number']}")
            print(f"Route: {best['departure_airport']} -> {best['arrival_airport']}")
            print(f"Date: {best['departure_date']}")
            print(f"Time: {best['departure_time']} - {best['arrival_time']}")
            print(f"Duration: {best['duration']}")
            print(f"Stops: {best['stops']}")
            print(f"Price: ${best['price']:.2f}")
            print(f"Deal Score: {best['deal_score']:.1f}/100")
            print(f"Source: {best['source']}")

        if analysis.get("cheapest_flights"):
            print(f"\n💰 TOP {min(5, len(analysis['cheapest_flights']))} CHEAPEST FLIGHTS:")
            for i, deal in enumerate(analysis["cheapest_flights"][:5], 1):
                deal_dict = deal.to_dict() if hasattr(deal, 'to_dict') else deal
                print(f"\n{i}. ${deal_dict['price']:.2f} - {deal_dict['airline']} {deal_dict['flight_number']}")
                print(f"   {deal_dict['departure_airport']} -> {deal_dict['arrival_airport']} on {deal_dict['departure_date']}")
                print(f"   {deal_dict['departure_time']} - {deal_dict['arrival_time']} ({deal_dict['duration']})")
                print(f"   Stops: {deal_dict['stops']} | Score: {deal_dict['deal_score']:.1f} | Source: {deal_dict['source']}")

        if analysis.get("direct_flights"):
            print(f"\n✈️  DIRECT FLIGHTS AVAILABLE: {len(analysis['direct_flights'])}")
            for i, deal in enumerate(analysis["direct_flights"][:3], 1):
                print(f"\n{i}. ${deal['price']:.2f} - {deal['airline']} {deal['flight_number']}")
                print(f"   {deal['departure_airport']} -> {deal['arrival_airport']} on {deal['departure_date']}")
                print(f"   {deal['departure_time']} - {deal['arrival_time']} ({deal['duration']})")

        print(f"\n📍 Airports searched:")
        print(f"Origins: {', '.join(analysis['airports_searched']['origins'])}")
        print(f"Destinations: {', '.join(analysis['airports_searched']['destinations'])}")
        print(f"\n⏰ Last updated: {analysis['last_updated']}")
        print("="*80)

async def main():
    """Main execution function"""
    print("🚀 EQ12 American Airlines Flight Search Starting...")
    print("Buffalo NY 14215 Content Empire - Flight Intelligence System")
    print("Searching for the best American Airlines deals to Miami area...")

    try:
        # Initialize search engine
        search_engine = FlightSearchEngine()

        # Search all sources
        deals = await search_engine.search_all_sources()

        if deals:
            # Analyze results
            analysis = search_engine.analyze_deals()

            # Print results
            search_engine.print_best_deals(analysis)

            # Save results
            filepath = search_engine.save_results(analysis)
            print(f"\n📁 Full results saved to: {filepath}")

        else:
            print("❌ No American Airlines flights found. Check your internet connection and try again.")

    except KeyboardInterrupt:
        print("\n⏹️ Search interrupted by user")
    except Exception as e:
        print(f"❌ Error during flight search: {e}")
        logging.exception("Flight search error")

if __name__ == "__main__":
    # Set up EQ12 environment
    sys.dont_write_bytecode = True

    # Run the flight search
    asyncio.run(main())
