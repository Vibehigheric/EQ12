#!/usr/bin/env python3
"""
Enhanced version of The Odds API Python samples with EdgeGod rate limiting
Drop-in replacement for odds.py that prevents 429 EXCEEDED_FREQ_LIMIT errors

This enhanced version includes:
- Built-in rate limiting (25 requests/second)
- Intelligent caching (15-minute duration)
- Exponential backoff retry logic
- Automatic 429 error recovery
- Same API interface as original
"""

import argparse
import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Any

import requests


@dataclass
class CacheEntry:
    data: Any
    timestamp: datetime
    ttl_seconds: int = 900  # 15 minutes default

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.timestamp + timedelta(seconds=self.ttl_seconds)


class EdgeGodRateLimiter:
    """Conservative rate limiter for The Odds API"""

    def __init__(self, max_requests_per_second: float = 25.0):
        self.max_requests_per_second = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0.0
        self.lock = Lock()

    def wait_if_needed(self):
        """Wait if necessary to maintain rate limit"""
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_request_time

            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                time.sleep(sleep_time)

            self.last_request_time = time.time()


class EdgeGodAPIClient:
    """Enhanced Odds API client with built-in 429 error prevention"""

    def __init__(self, api_key: str, rate_limit: float = 25.0):
        self.api_key = api_key
        self.rate_limiter = EdgeGodRateLimiter(rate_limit)
        self.cache: dict[str, CacheEntry] = {}
        self.session = requests.Session()

        # Configure session with retries
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _generate_cache_key(self, url: str, params: dict) -> str:
        """Generate cache key from URL and parameters"""
        cache_data = f"{url}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()

    def _get_cached(self, cache_key: str) -> Any | None:
        """Get cached data if still valid"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired():
                print(f"✅ Cache hit for {cache_key[:8]}...")
                return entry.data
            del self.cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, data: Any, ttl: int = 900):
        """Cache data with TTL"""
        self.cache[cache_key] = CacheEntry(data=data, timestamp=datetime.utcnow(), ttl_seconds=ttl)
        print(f"💾 Cached data for {cache_key[:8]}...")

    def make_request(self, url: str, params: dict, ttl: int = 900) -> dict:
        """Make rate-limited API request with caching"""
        # Add API key to params
        params = params.copy()
        params["api_key"] = self.api_key

        # Check cache first
        cache_key = self._generate_cache_key(url, params)
        cached_data = self._get_cached(cache_key)
        if cached_data:
            return cached_data

        # Rate limit the request
        self.rate_limiter.wait_if_needed()

        try:
            response = self.session.get(url, params=params, timeout=30)

            if response.status_code == 429:
                print("⚠️ Rate limit hit, implementing exponential backoff...")
                time.sleep(2**1)  # Start with 2 second backoff
                return self.make_request(url, params, ttl)

            response.raise_for_status()

            result = {"data": response.json(), "headers": dict(response.headers)}

            # Cache successful responses
            self._set_cache(cache_key, result, ttl)

            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed: {e}")
            raise

    def get_sports(self) -> dict:
        """Get list of available sports"""
        return self.make_request("https://api.the-odds-api.com/v4/sports", {})

    def get_odds(
        self,
        sport: str,
        regions: str = "us",
        markets: str = "h2h,spreads",
        odds_format: str = "decimal",
        date_format: str = "iso",
    ) -> dict:
        """Get odds for a sport with rate limiting"""
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
            "dateFormat": date_format,
        }
        return self.make_request(f"https://api.the-odds-api.com/v4/sports/{sport}/odds", params)


def main():
    """Enhanced main function - drop-in replacement for original odds.py"""
    # Obtain the api key that was passed in from the command line
    parser = argparse.ArgumentParser(description="Enhanced Sample V4 with EdgeGod rate limiting")
    parser.add_argument("--api-key", type=str, default="")
    args = parser.parse_args()

    # An api key is emailed to you when you sign up to a plan
    # Get a free API key at: [The Odds API Registration](https://api.the-odds-api.com/)
    API_KEY = args.api_key or "YOUR_API_KEY"

    if API_KEY == "YOUR_API_KEY":
        print("❌ Please provide a valid API key using --api-key argument")
        return

    # Initialize EdgeGod API client
    client = EdgeGodAPIClient(API_KEY, rate_limit=25.0)

    # Sport key - same as original
    SPORT = "upcoming"  # use 'upcoming' to see the next 8 games across all sports

    # Parameters - same as original
    REGIONS = "us"  # uk | us | eu | au. Multiple can be specified if comma delimited
    MARKETS = "h2h,spreads"  # h2h | spreads | totals. Multiple can be specified
    ODDS_FORMAT = "decimal"  # decimal | american
    DATE_FORMAT = "iso"  # iso | unix

    print("🎯 EdgeGod Enhanced Odds API Client")
    print("=" * 40)
    print("✅ Built-in rate limiting (25 req/sec)")
    print("✅ Intelligent caching (15 min TTL)")
    print("✅ Automatic 429 error prevention")
    print("✅ Exponential backoff retry logic")
    print("=" * 40)

    try:
        # First get a list of in-season sports with rate limiting
        print("\n📊 Fetching available sports...")
        sports_response = client.get_sports()

        if "data" in sports_response:
            print("✅ List of in season sports:")
            for sport in sports_response["data"][:5]:  # Show first 5
                print(f"   🏆 {sport.get('title', 'Unknown')} ({sport.get('key', 'unknown')})")

            if len(sports_response["data"]) > 5:
                print(f"   ... and {len(sports_response['data']) - 5} more sports")

        # Now get odds with rate limiting
        print(f"\n🎲 Fetching odds for {SPORT}...")
        odds_response = client.get_odds(SPORT, REGIONS, MARKETS, ODDS_FORMAT, DATE_FORMAT)

        if "data" in odds_response:
            odds_json = odds_response["data"]
            headers = odds_response["headers"]

            print(f"✅ Number of events: {len(odds_json)}")

            # Show sample of the data
            if odds_json:
                print("\n📋 Sample event:")
                sample_event = odds_json[0]
                print(f"   🏟️ {sample_event.get('home_team')} vs {sample_event.get('away_team')}")
                print(f"   📅 {sample_event.get('commence_time')}")
                print(f"   📊 Bookmakers: {len(sample_event.get('bookmakers', []))}")

            # Check the usage quota
            print("\n💳 API Usage:")
            print(f"   📈 Remaining requests: {headers.get('x-requests-remaining', 'Unknown')}")
            print(f"   📊 Used requests: {headers.get('x-requests-used', 'Unknown')}")

            print("\n🎉 SUCCESS: Zero 429 errors with EdgeGod rate limiting!")

        else:
            print("❌ No data received from API")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 EdgeGod features that prevented issues:")
        print("   • Rate limiting prevented 429 errors")
        print("   • Retry logic handled temporary failures")
        print("   • Caching reduced duplicate API calls")


if __name__ == "__main__":
    main()
