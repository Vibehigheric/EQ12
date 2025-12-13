"""
EdgeGod API Manager - Comprehensive rate limiting and quota management for The Odds API

This module provides intelligent API management to prevent 429 (rate limited) and
402 (quota exceeded) errors while maximizing API efficiency through caching and
smart request distribution.

Key Features:
- Conservative rate limiting (25 calls/second vs API limit of 30)
- Daily and hourly quota management with intelligent distribution
- Response caching with configurable TTL (default 15 minutes)
- Exponential backoff retry logic for failed requests
- Comprehensive usage statistics and monitoring
- Automatic quota tracking from API response headers

Author: EdgeGod Expert System
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import logging
import os
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIUsageStats:
    """Track API usage statistics"""

    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.cached_responses = 0
        self.rate_limited_requests = 0
        self.quota_exceeded_requests = 0
        self.quota_remaining = None
        self.total_quota_used = None

    def add_request(
        self,
        success: bool = True,
        cached: bool = False,
        rate_limited: bool = False,
        quota_exceeded: bool = False,
    ):
        """Add a request to statistics"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        if cached:
            self.cached_responses += 1
        if rate_limited:
            self.rate_limited_requests += 1
        if quota_exceeded:
            self.quota_exceeded_requests += 1


class EdgeGodAPIManager:
    """
    Comprehensive API manager for The Odds API with intelligent rate limiting,
    quota management, caching, and error handling.
    """

    def __init__(
        self,
        api_key: str,
        max_daily_quota: int = 450,
        rate_limit: float = 25.0,
        cache_duration: int = 900,
    ):
        """
        Initialize the API manager

        Args:
            api_key: The Odds API key
            max_daily_quota: Maximum daily API calls (default 450, conservative)
            rate_limit: Calls per second limit (default 25, under API limit of 30)
            cache_duration: Cache duration in seconds (default 900 = 15 minutes)
        """
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        self.rate_limit = rate_limit
        self.max_daily_quota = max_daily_quota
        self.cache_duration = cache_duration

        # Rate limiting
        self.request_times = deque()
        self.min_interval = 1.0 / rate_limit

        # Quota management
        self.daily_usage = 0
        self.hourly_usage = 0
        self.hourly_limit = max_daily_quota // 24  # Distribute daily quota across hours
        self.last_reset_hour = datetime.now().hour
        self.last_reset_date = datetime.now().date()

        # Caching
        self.cache = {}

        # Statistics
        self.stats = APIUsageStats()

        # HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)

        # Retry configuration
        self.max_retries = 3
        self.base_delay = 2.0
        self.max_delay = 30.0

        logger.info(
            f"EdgeGod API Manager initialized - Rate limit: {rate_limit}/sec, Daily quota: {max_daily_quota}"
        )

    def _get_cache_key(self, endpoint: str, params: dict[str, Any]) -> str:
        """Generate cache key for request"""
        # Remove API key from params for cache key
        cache_params = {k: v for k, v in params.items() if k != "apiKey"}
        param_str = json.dumps(cache_params, sort_keys=True)
        return hashlib.md5(f"{endpoint}:{param_str}".encode()).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Any | None:
        """Get cached response if valid"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                self.stats.add_request(success=True, cached=True)
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_data
            # Remove expired cache entry
            del self.cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: Any):
        """Cache successful response"""
        self.cache[cache_key] = (response, time.time())
        logger.debug(f"Cached response for key: {cache_key}")

    async def _wait_for_rate_limit(self):
        """Wait to respect rate limit"""
        now = time.time()

        # Clean old timestamps
        while self.request_times and now - self.request_times[0] > 1.0:
            self.request_times.popleft()

        # Check if we need to wait
        if len(self.request_times) >= self.rate_limit:
            sleep_time = 1.0 - (now - self.request_times[0])
            if sleep_time > 0:
                logger.debug(f"Rate limit wait: {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                now = time.time()

        # Add current request timestamp
        self.request_times.append(now)

    def _check_quota_limits(self):
        """Check and enforce quota limits"""
        now = datetime.now()

        # Reset daily quota if new day
        if now.date() != self.last_reset_date:
            self.daily_usage = 0
            self.hourly_usage = 0
            self.last_reset_date = now.date()
            self.last_reset_hour = now.hour
            logger.info("Daily quota reset")

        # Reset hourly quota if new hour
        if now.hour != self.last_reset_hour:
            self.hourly_usage = 0
            self.last_reset_hour = now.hour
            logger.info("Hourly quota reset")

        # Check limits
        if self.daily_usage >= self.max_daily_quota:
            raise Exception(f"Daily quota exceeded: {self.daily_usage}/{self.max_daily_quota}")

        if self.hourly_usage >= self.hourly_limit:
            minutes_to_wait = 60 - now.minute
            logger.warning(f"Hourly limit reached, waiting {minutes_to_wait} minutes")
            raise Exception(f"Hourly quota exceeded, wait {minutes_to_wait} minutes")

    def _update_quota_from_headers(self, headers: dict[str, str]):
        """Update quota information from API response headers"""
        if "x-requests-remaining" in headers:
            self.stats.quota_remaining = int(headers["x-requests-remaining"])
        if "x-requests-used" in headers:
            self.stats.total_quota_used = int(headers["x-requests-used"])
        if "x-requests-last" in headers:
            last_cost = int(headers["x-requests-last"])
            logger.debug(f"API call cost: {last_cost} credits")

    async def _make_request_with_retries(self, endpoint: str, params: dict[str, Any]) -> Any:
        """Make API request with retries and exponential backoff"""
        url = f"{self.base_url}/{endpoint}"
        params = {**params, "apiKey": self.api_key}

        for attempt in range(self.max_retries):
            try:
                # Check quota limits
                self._check_quota_limits()

                # Wait for rate limit
                await self._wait_for_rate_limit()

                # Make request
                response = await self.client.get(url, params=params)

                # Update quota info
                self._update_quota_from_headers(dict(response.headers))

                # Increment usage counters
                self.daily_usage += 1
                self.hourly_usage += 1

                if response.status_code == 200:
                    result = response.json()
                    self.stats.add_request(success=True)
                    return result

                if response.status_code == 429:
                    # Rate limited
                    self.stats.add_request(success=False, rate_limited=True)
                    retry_after = float(response.headers.get("Retry-After", 3.0))
                    logger.warning(
                        f"Rate limited (429), waiting {retry_after}s (attempt {attempt + 1})"
                    )
                    await asyncio.sleep(retry_after)
                    continue

                if response.status_code == 402:
                    # Quota exceeded
                    self.stats.add_request(success=False, quota_exceeded=True)
                    error_msg = "Usage quota exceeded - upgrade plan or wait for reset"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                if response.status_code == 401:
                    # Invalid API key
                    error_msg = "Invalid API key (401)"
                    logger.error(error_msg)
                    raise Exception(error_msg)

                # Other error
                error_text = response.text
                logger.error(f"API error {response.status_code}: {error_text}")

                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2**attempt), self.max_delay)
                    await asyncio.sleep(delay)
                    continue
                response.raise_for_status()

            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = min(self.base_delay * (2**attempt), self.max_delay)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}), retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.stats.add_request(success=False)
                    raise

        raise Exception(f"Request failed after {self.max_retries} attempts")

    async def make_api_call(
        self, endpoint: str, params: dict[str, Any] = None, use_cache: bool = True
    ) -> Any:
        """Main method to make API calls with full management"""
        if params is None:
            params = {}

        cache_key = self._get_cache_key(endpoint, params)

        # Check cache first
        if use_cache:
            cached_response = self._get_cached_response(cache_key)
            if cached_response is not None:
                return cached_response

        # Make the request
        try:
            response = await self._make_request_with_retries(endpoint, params)

            # Cache successful response
            if use_cache:
                self._cache_response(cache_key, response)

            return response

        except Exception as e:
            logger.error(f"API call failed for {endpoint}: {e}")
            raise

    async def get_sports(self, all_sports: bool = False) -> list[dict[str, Any]]:
        """Get available sports"""
        params = {}
        if all_sports:
            params["all"] = "true"

        return await self.make_api_call("sports", params)

    async def get_events(
        self,
        sport_key: str,
        commence_time_from: str = None,
        commence_time_to: str = None,
    ) -> list[dict[str, Any]]:
        """Get events for a sport"""
        params = {}
        if commence_time_from:
            params["commenceTimeFrom"] = commence_time_from
        if commence_time_to:
            params["commenceTimeTo"] = commence_time_to
        params["dateFormat"] = "iso"

        return await self.make_api_call(f"sports/{sport_key}/events", params)

    async def get_odds(
        self,
        sport_key: str,
        regions: str = "us",
        markets: str = "h2h",
        odds_format: str = "american",
        event_ids: list[str] = None,
    ) -> list[dict[str, Any]]:
        """Get odds for events"""
        params = {
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
            "dateFormat": "iso",
        }

        if event_ids:
            # Process in batches to avoid large requests
            batch_size = 20  # Conservative batch size
            all_odds = []

            for i in range(0, len(event_ids), batch_size):
                batch_ids = event_ids[i : i + batch_size]
                params["eventIds"] = ",".join(batch_ids)

                try:
                    batch_odds = await self.make_api_call(f"sports/{sport_key}/odds", params)
                    all_odds.extend(batch_odds)

                    # Small delay between batches
                    if i + batch_size < len(event_ids):
                        await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Failed to fetch odds for batch {i//batch_size + 1}: {e}")
                    continue

            return all_odds
        return await self.make_api_call(f"sports/{sport_key}/odds", params)

    def get_usage_stats(self) -> dict[str, Any]:
        """Get comprehensive usage statistics"""
        return {
            "requests": {
                "total": self.stats.total_requests,
                "successful": self.stats.successful_requests,
                "failed": self.stats.failed_requests,
                "cached": self.stats.cached_responses,
                "success_rate": self.stats.successful_requests
                / max(1, self.stats.total_requests)
                * 100,
            },
            "errors": {
                "rate_limited": self.stats.rate_limited_requests,
                "quota_exceeded": self.stats.quota_exceeded_requests,
            },
            "quota": {
                "daily_used": self.daily_usage,
                "daily_limit": self.max_daily_quota,
                "daily_remaining": self.max_daily_quota - self.daily_usage,
                "hourly_used": self.hourly_usage,
                "hourly_limit": self.hourly_limit,
                "api_quota_remaining": self.stats.quota_remaining,
                "api_quota_used": self.stats.total_quota_used,
            },
            "cache": {
                "entries": len(self.cache),
                "hit_rate": self.stats.cached_responses / max(1, self.stats.total_requests) * 100,
            },
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform API health check"""
        try:
            start_time = time.time()
            sports = await self.get_sports()
            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "sports_available": len(sports),
                "usage_stats": self.get_usage_stats(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "usage_stats": self.get_usage_stats(),
            }

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    def save_usage_report(self, filename: str = None):
        """Save usage statistics to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_usage_report_{timestamp}.json"

        logs_dir = Path(os.environ.get("EQ12_LOGS", "./logs"))
        logs_dir.mkdir(exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "usage_stats": self.get_usage_stats(),
            "configuration": {
                "daily_quota_limit": self.max_daily_quota,
                "rate_limit": self.rate_limit,
                "hourly_limit": self.hourly_limit,
                "cache_duration_seconds": self.cache_duration,
            },
        }

        report_path = logs_dir / filename
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Usage report saved to {report_path}")
        return report_path


# Example usage and testing
async def main():
    """Example usage of the API manager"""
    api_key = os.environ.get("ODDS_API_KEY", "")
    if not api_key:
        print("Please set ODDS_API_KEY environment variable")
        return

    # Initialize API manager
    api_manager = EdgeGodAPIManager(api_key, max_daily_quota=450)

    try:
        # Health check
        health = await api_manager.health_check()
        print(f"API Health: {health['status']}")

        # Get sports (cached for 15 minutes)
        sports = await api_manager.get_sports()
        print(f"Available sports: {len(sports)}")

        # Get MLB events for today
        if sports:
            today = datetime.now().strftime("%Y-%m-%d")
            events = await api_manager.get_events(
                "baseball_mlb", f"{today}T00:00:00Z", f"{today}T23:59:59Z"
            )
            print(f"MLB events today: {len(events)}")

            # Get odds for first few events
            if events:
                event_ids = [event["id"] for event in events[:5]]
                odds = await api_manager.get_odds("baseball_mlb", event_ids=event_ids)
                print(f"Odds retrieved for {len(odds)} events")

        # Print usage stats
        stats = api_manager.get_usage_stats()
        print("\nAPI Usage Stats:")
        print(f"  Total requests: {stats['requests']['total']}")
        print(f"  Success rate: {stats['requests']['success_rate']:.1f}%")
        print(f"  Daily quota used: {stats['quota']['daily_used']}/{stats['quota']['daily_limit']}")
        print(f"  Cache hit rate: {stats['cache']['hit_rate']:.1f}%")

        # Save usage report
        api_manager.save_usage_report()

    except Exception as e:
        print(f"Error: {e}")

    finally:
        await api_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
