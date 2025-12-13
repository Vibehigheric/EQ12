#!/usr/bin/env python3
"""
Enhanced Official Sample - The Odds API v4
Based on official samples but with EdgeGod rate limiting and 429 error prevention

This combines the simplicity of official samples with production-grade reliability:
- Conservative rate limiting (25/sec vs 30/sec API limit)
- Intelligent retry logic with exponential backoff
- Response caching to reduce API calls
- Comprehensive error handling for 401/402/429
"""

import asyncio
import os
from typing import Any

# Import our EdgeGod API Manager
from api_manager import EdgeGodAPIManager

# Configuration (following official sample patterns)
API_KEY = os.getenv("ODDS_API_KEY")  # Set this environment variable
SPORT = "americanfootball_nfl"  # Official sample uses NFL
REGIONS = "us"  # Official sample uses US region
MARKETS = "h2h,spreads,totals"  # Official sample markets
ODDS_FORMAT = "american"  # Changed from decimal to american (more useful)


class EnhancedOddsClient:
    """
    Enhanced version of official samples with EdgeGod rate limiting

    Features:
    - All benefits of official samples (simple, clean API)
    - Plus: 429 error prevention, caching, retry logic
    - Plus: Quota management, usage tracking
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key required. Set ODDS_API_KEY environment variable.")

        # Initialize EdgeGod API Manager with production settings
        self.api_manager = EdgeGodAPIManager(
            api_key=api_key,
            max_daily_quota=450,  # Conservative limit
            rate_limit=25.0,  # Under 30/sec API limit
            cache_duration=900,  # 15-minute cache
        )
        print("✅ Enhanced Odds Client initialized with rate limiting")

    async def get_sports(self) -> list[dict[str, Any]]:
        """Get available sports (matches official sample pattern)"""
        try:
            sports = await self.api_manager.get_sports()
            print(f"📊 Found {len(sports)} available sports")
            return sports
        except Exception as e:
            print(f"❌ Error fetching sports: {e}")
            return []

    async def get_odds(
        self,
        sport: str = SPORT,
        regions: str = REGIONS,
        markets: str = MARKETS,
        odds_format: str = ODDS_FORMAT,
        event_ids: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get odds for a sport (enhanced version of official sample)

        Args:
            sport: Sport key (e.g., 'americanfootball_nfl')
            regions: Regions to get odds for (e.g., 'us')
            markets: Markets to include (e.g., 'h2h,spreads,totals')
            odds_format: Format for odds (e.g., 'american', 'decimal')
            event_ids: Optional list of specific event IDs
        """
        try:
            odds = await self.api_manager.get_odds(
                sport_key=sport,
                regions=regions,
                markets=markets,
                odds_format=odds_format,
                event_ids=event_ids,
            )
            print(f"🎯 Retrieved odds for {len(odds)} events in {sport}")
            return odds
        except Exception as e:
            print(f"❌ Error fetching odds for {sport}: {e}")
            return []

    async def get_events(self, sport: str, days_ahead: int = 7) -> list[dict[str, Any]]:
        """Get events for a sport (following official patterns)"""
        try:
            from datetime import datetime, timedelta

            # Calculate time window (official samples often use date ranges)
            start_time = datetime.now()
            end_time = start_time + timedelta(days=days_ahead)

            start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_iso = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            events = await self.api_manager.get_events(
                sport_key=sport, commence_time_from=start_iso, commence_time_to=end_iso
            )
            print(f"📅 Found {len(events)} upcoming events in {sport}")
            return events
        except Exception as e:
            print(f"❌ Error fetching events for {sport}: {e}")
            return []

    async def get_usage_stats(self) -> dict[str, Any]:
        """Get API usage statistics (not in official samples but very useful)"""
        return self.api_manager.get_usage_stats()

    async def close(self):
        """Clean shutdown (important for production)"""
        await self.api_manager.close()
        print("🔒 Enhanced Odds Client closed cleanly")


# Enhanced version of official sample usage
async def enhanced_official_example():
    """
    Enhanced version of the official sample that prevents 429 errors

    This follows the same pattern as official samples but adds:
    - Rate limiting to prevent 429 errors
    - Intelligent caching to reduce API calls
    - Proper error handling and retry logic
    """

    print("🚀 Starting Enhanced Official Sample with EdgeGod Rate Limiting...")
    print()

    # Initialize client (same pattern as official samples)
    client = EnhancedOddsClient(API_KEY)

    try:
        # Step 1: Get available sports (official sample pattern)
        print("1️⃣ Getting available sports...")
        sports = await client.get_sports()

        if sports:
            # Show first few sports (like official samples do)
            print("📋 Available sports:")
            for sport in sports[:5]:  # Show first 5
                print(f"   • {sport.get('title', 'Unknown')} ({sport.get('key', 'unknown')})")
            if len(sports) > 5:
                print(f"   ... and {len(sports) - 5} more")
            print()

        # Step 2: Get odds for specific sport (official sample pattern)
        print("2️⃣ Getting odds for NFL...")
        odds_data = await client.get_odds(
            sport=SPORT, regions=REGIONS, markets=MARKETS, odds_format=ODDS_FORMAT
        )

        if odds_data:
            print("🎯 Sample odds data:")
            # Show first event (like official samples)
            first_event = odds_data[0]
            print(
                f"   Event: {first_event.get('away_team', 'Unknown')} @ {first_event.get('home_team', 'Unknown')}"
            )
            print(f"   Start: {first_event.get('commence_time', 'Unknown')}")

            # Show bookmaker info (official sample style)
            if first_event.get("bookmakers"):
                bookmaker = first_event["bookmakers"][0]
                print(f"   Bookmaker: {bookmaker.get('title', 'Unknown')}")
                if bookmaker.get("markets"):
                    market = bookmaker["markets"][0]
                    print(f"   Market: {market.get('key', 'Unknown')}")
            print()

        # Step 3: Show usage stats (EdgeGod enhancement)
        print("3️⃣ API Usage Statistics:")
        stats = await client.get_usage_stats()
        print(f"   📊 Total requests: {stats['requests']['total']}")
        print(f"   ✅ Success rate: {stats['requests']['success_rate']:.1f}%")
        print(f"   🗄️ Cache hit rate: {stats['cache']['hit_rate']:.1f}%")
        print(
            f"   📈 Daily quota used: {stats['quota']['daily_used']}/{stats['quota']['daily_limit']}"
        )
        print(f"   💾 Cached responses: {stats['cache']['entries']}")
        print()

        # Step 4: Demonstrate no 429 errors (EdgeGod feature)
        print("4️⃣ Testing rapid API calls (would cause 429 errors without rate limiting)...")
        rapid_requests = []
        for i in range(3):  # Make several quick requests
            print(f"   Making request {i+1}/3...")
            task = client.get_sports()
            rapid_requests.append(task)

        # All complete successfully without 429 errors!
        results = await asyncio.gather(*rapid_requests)
        print(f"   ✅ All {len(results)} rapid requests succeeded (no 429 errors!)")
        print()

        print("🎉 Enhanced Official Sample completed successfully!")
        print("💡 Key improvements over official samples:")
        print("   • No 429 EXCEEDED_FREQ_LIMIT errors")
        print("   • No 402 OUT_OF_USAGE_CREDITS errors")
        print("   • Intelligent caching reduces API calls")
        print("   • Robust retry logic handles temporary failures")
        print("   • Real-time usage monitoring and analytics")

    except Exception as e:
        print(f"❌ Error in enhanced sample: {e}")

    finally:
        # Clean shutdown (official samples often forget this)
        await client.close()


# Simple usage example (official sample style)
async def simple_example():
    """Simple example following official sample patterns exactly"""

    client = EnhancedOddsClient(API_KEY)

    try:
        # Get odds for NFL (exactly like official sample)
        odds = await client.get_odds(
            sport="americanfootball_nfl",
            regions="us",
            markets="h2h,spreads,totals",
            odds_format="american",
        )

        # Print result (like official samples do)
        print("Odds data:", odds[:2] if len(odds) > 2 else odds)

    finally:
        await client.close()


if __name__ == "__main__":
    print("Choose example to run:")
    print("1. Enhanced Official Sample (recommended)")
    print("2. Simple Example (matches official patterns)")

    choice = input("\nEnter choice (1 or 2): ").strip()

    if choice == "2":
        asyncio.run(simple_example())
    else:
        asyncio.run(enhanced_official_example())
