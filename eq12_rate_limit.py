#!/usr/bin/env python3
"""
EQ12 Rate Limiting Module - Comprehensive Throttling System
Prevents API rate limit hits with soft throttling, burst handling, and Retry-After compliance
"""

import asyncio
import json
import logging
import os
import random
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import requests


class EQ12Config:
    """Configuration manager for EQ12 rate limiting settings"""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file or environment variables"""
        config_path = Path("C:/EQ12/configs/rate_limit_config.json")

        # Default configuration
        default_config = {
            "API_THROTTLE": {
                "max_rpm": 30,
                "burst": 5,
                "concurrency": 2,
                "min_interval_ms": 250,
                "soft_remaining_floor": 200,
                "jitter_ms": [50, 150],
                "backoff_base_s": 1.0,
                "backoff_max_s": 8.0,
                "enable_proactive_throttle": True,
                "enable_burst_detection": True,
            }
        }

        # Try to load from config file
        try:
            if config_path.exists():
                with open(config_path) as f:
                    file_config = json.load(f)
                    default_config.update(file_config)
        except Exception as e:
            logging.warning(f"Failed to load config from {config_path}: {e}")

        # Override with environment variables
        env_overrides = {
            "max_rpm": int(os.getenv("EQ12_MAX_RPM", default_config["API_THROTTLE"]["max_rpm"])),
            "burst": int(os.getenv("EQ12_BURST", default_config["API_THROTTLE"]["burst"])),
            "concurrency": int(
                os.getenv("EQ12_CONCURRENCY", default_config["API_THROTTLE"]["concurrency"])
            ),
            "min_interval_ms": int(
                os.getenv(
                    "EQ12_MIN_INTERVAL_MS",
                    default_config["API_THROTTLE"]["min_interval_ms"],
                )
            ),
            "soft_remaining_floor": int(
                os.getenv(
                    "EQ12_SOFT_REMAINING_FLOOR",
                    default_config["API_THROTTLE"]["soft_remaining_floor"],
                )
            ),
            "backoff_base_s": float(
                os.getenv(
                    "EQ12_BACKOFF_BASE_S",
                    default_config["API_THROTTLE"]["backoff_base_s"],
                )
            ),
            "backoff_max_s": float(
                os.getenv(
                    "EQ12_BACKOFF_MAX_S",
                    default_config["API_THROTTLE"]["backoff_max_s"],
                )
            ),
        }

        for key, value in env_overrides.items():
            default_config["API_THROTTLE"][key] = value

        return default_config

    def get_throttle_config(self) -> dict:
        """Get throttling configuration"""
        return self.config["API_THROTTLE"]


class SoftLimiter:
    """Synchronous soft rate limiter with burst handling and proactive throttling"""

    def __init__(
        self,
        max_rpm=30,
        burst=5,
        min_interval_ms=250,
        concurrency=2,
        jitter_ms=(50, 150),
        backoff_base_s=1.0,
        backoff_max_s=8.0,
        soft_remaining_floor=200,
        enable_proactive_throttle=True,
    ):
        self.max_rps = max(0.1, max_rpm / 60.0)
        self.min_interval = max(min_interval_ms / 1000.0, 1.0 / self.max_rps)
        self.burst = max(1, burst)
        self.sema = threading.Semaphore(concurrency)
        self.lock = threading.Lock()
        self.tokens = self.burst
        self.last = 0.0
        self.jitter_ms = jitter_ms
        self.backoff_base = backoff_base_s
        self.backoff_max = backoff_max_s
        self.soft_remaining_floor = soft_remaining_floor
        self.enable_proactive_throttle = enable_proactive_throttle

        # Statistics tracking
        self.stats = {
            "requests_made": 0,
            "throttles_applied": 0,
            "backoffs_triggered": 0,
            "proactive_throttles": 0,
            "last_reset": time.time(),
        }

        logging.info(
            f"🚦 EQ12 SoftLimiter initialized: {max_rpm} RPM, burst={burst}, concurrency={concurrency}"
        )

    def wait(self, cost: int = 1):
        """Wait for permission to make a request"""
        self.sema.acquire()

        with self.lock:
            now = time.monotonic()
            # Refill burst bucket over time
            elapsed = now - self.last if self.last else 0.0
            self.tokens = min(self.burst, self.tokens + elapsed * self.max_rps)
            self.last = now

            if self.tokens < cost:
                # Need to wait to accumulate enough tokens
                need = (cost - self.tokens) / self.max_rps
                time.sleep(need)
                self.tokens = 0.0
                self.stats["throttles_applied"] += 1
            else:
                self.tokens -= cost

        # Apply minimum spacing and jitter
        jitter_delay = random.uniform(self.jitter_ms[0], self.jitter_ms[1]) / 1000.0
        time.sleep(self.min_interval + jitter_delay)

    def release(self):
        """Release the semaphore"""
        self.sema.release()
        self.stats["requests_made"] += 1

    def backoff(self, attempt: int, retry_after: str | None = None):
        """Apply exponential backoff with jitter"""
        if retry_after:
            try:
                delay = float(retry_after)
                logging.warning(f"⏳ Respecting Retry-After: {delay}s")
            except (ValueError, TypeError):
                delay = self.backoff_base * (2 ** (attempt - 1))
        else:
            delay = self.backoff_base * (2 ** (attempt - 1))

        delay = min(self.backoff_max, delay)
        jitter = random.uniform(0, 0.25)
        total_delay = delay + jitter

        logging.warning(f"⏸️ Rate limit backoff: {total_delay:.2f}s (attempt {attempt})")
        time.sleep(total_delay)
        self.stats["backoffs_triggered"] += 1

    def check_quota_headers(self, headers: dict) -> bool:
        """Check quota headers and apply proactive throttling if needed"""
        if not self.enable_proactive_throttle:
            return False

        # Check common quota header patterns
        quota_headers = [
            "x-requests-remaining",
            "x-ratelimit-remaining",
            "ratelimit-remaining",
            "x-quota-remaining",
        ]

        for header in quota_headers:
            remaining = headers.get(header)
            if remaining is not None:
                try:
                    remaining_count = float(remaining)
                    if remaining_count < self.soft_remaining_floor:
                        throttle_delay = 1.0 + (self.soft_remaining_floor - remaining_count) * 0.01
                        logging.warning(
                            f"🔄 Proactive throttle: {remaining_count} requests remaining, sleeping {throttle_delay:.2f}s"
                        )
                        time.sleep(throttle_delay)
                        self.stats["proactive_throttles"] += 1
                        return True
                except (ValueError, TypeError):
                    continue

        return False

    def get_stats(self) -> dict:
        """Get performance statistics"""
        now = time.time()
        elapsed = now - self.stats["last_reset"]
        rpm = (self.stats["requests_made"] / elapsed) * 60 if elapsed > 0 else 0

        return {
            **self.stats,
            "current_rpm": rpm,
            "elapsed_seconds": elapsed,
            "efficiency": 1
            - (self.stats["throttles_applied"] / max(1, self.stats["requests_made"])),
        }


class AsyncSoftLimiter:
    """Asynchronous soft rate limiter for aiohttp and async operations"""

    def __init__(
        self,
        max_rpm=30,
        burst=5,
        min_interval_ms=250,
        concurrency=2,
        jitter_ms=(50, 150),
        soft_remaining_floor=200,
    ):
        self._sema = asyncio.Semaphore(concurrency)
        self._min_interval = max(min_interval_ms / 1000.0, 1.0 / (max_rpm / 60.0))
        self._jitter = jitter_ms
        self._tokens = burst
        self._burst = burst
        self._max_rps = max_rpm / 60.0
        self._last = 0.0
        self._lock = asyncio.Lock()
        self._soft_remaining_floor = soft_remaining_floor

        # Statistics
        self._stats = {
            "requests_made": 0,
            "throttles_applied": 0,
            "proactive_throttles": 0,
        }

        logging.info(f"🚦 EQ12 AsyncSoftLimiter initialized: {max_rpm} RPM, burst={burst}")

    @asynccontextmanager
    async def slot(self, cost: int = 1):
        """Async context manager for rate-limited requests"""
        await self._sema.acquire()
        try:
            async with self._lock:
                now = time.monotonic()
                elapsed = now - self._last if self._last else 0.0
                self._tokens = min(self._burst, self._tokens + elapsed * self._max_rps)
                self._last = now

                if self._tokens < cost:
                    need = (cost - self._tokens) / self._max_rps
                    await asyncio.sleep(need)
                    self._tokens = 0.0
                    self._stats["throttles_applied"] += 1
                else:
                    self._tokens -= cost

            # Apply jitter
            jitter_delay = random.uniform(*self._jitter) / 1000.0
            await asyncio.sleep(self._min_interval + jitter_delay)
            yield
        finally:
            self._sema.release()
            self._stats["requests_made"] += 1

    async def check_quota_headers_async(self, headers: dict) -> bool:
        """Async version of quota header checking"""
        quota_headers = [
            "x-requests-remaining",
            "x-ratelimit-remaining",
            "ratelimit-remaining",
            "x-quota-remaining",
        ]

        for header in quota_headers:
            remaining = headers.get(header)
            if remaining is not None:
                try:
                    remaining_count = float(remaining)
                    if remaining_count < self._soft_remaining_floor:
                        throttle_delay = 1.0 + (self._soft_remaining_floor - remaining_count) * 0.01
                        logging.warning(
                            f"🔄 Async proactive throttle: {remaining_count} remaining, sleeping {throttle_delay:.2f}s"
                        )
                        await asyncio.sleep(throttle_delay)
                        self._stats["proactive_throttles"] += 1
                        return True
                except (ValueError, TypeError):
                    continue
        return False


# Global limiter instances
_config = EQ12Config()
_throttle_config = _config.get_throttle_config()

sync_limiter = SoftLimiter(
    max_rpm=_throttle_config["max_rpm"],
    burst=_throttle_config["burst"],
    min_interval_ms=_throttle_config["min_interval_ms"],
    concurrency=_throttle_config["concurrency"],
    jitter_ms=tuple(_throttle_config["jitter_ms"]),
    backoff_base_s=_throttle_config["backoff_base_s"],
    backoff_max_s=_throttle_config["backoff_max_s"],
    soft_remaining_floor=_throttle_config["soft_remaining_floor"],
)

async_limiter = AsyncSoftLimiter(
    max_rpm=_throttle_config["max_rpm"],
    burst=_throttle_config["burst"],
    min_interval_ms=_throttle_config["min_interval_ms"],
    concurrency=_throttle_config["concurrency"],
    jitter_ms=tuple(_throttle_config["jitter_ms"]),
    soft_remaining_floor=_throttle_config["soft_remaining_floor"],
)


def get_with_limit(url: str, cost: int = 1, max_attempts: int = 3, **kwargs) -> requests.Response:
    """
    Rate-limited requests.get() with automatic retry and quota awareness

    Args:
        url: URL to fetch
        cost: API cost (default 1, some endpoints may cost more)
        max_attempts: Maximum retry attempts
        **kwargs: Additional arguments for requests.get()

    Returns:
        requests.Response object
    """
    attempt = 1

    while attempt <= max_attempts:
        sync_limiter.wait(cost)

        try:
            # Set reasonable defaults
            kwargs.setdefault("timeout", 15)

            response = requests.get(url, **kwargs)

            # Check for rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                sync_limiter.backoff(attempt, retry_after)
                attempt += 1
                continue

            # Check quota headers for proactive throttling
            sync_limiter.check_quota_headers(response.headers)

            # Log successful request
            if response.status_code >= 400:
                logging.warning(f"⚠️ HTTP {response.status_code} for {url}")

            return response

        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Request failed for {url}: {e}")
            if attempt >= max_attempts:
                raise
            sync_limiter.backoff(attempt)
            attempt += 1

        finally:
            sync_limiter.release()

    raise requests.exceptions.RetryError(f"Failed after {max_attempts} attempts: {url}")


def post_with_limit(url: str, cost: int = 1, max_attempts: int = 3, **kwargs) -> requests.Response:
    """Rate-limited requests.post() with automatic retry"""
    attempt = 1

    while attempt <= max_attempts:
        sync_limiter.wait(cost)

        try:
            kwargs.setdefault("timeout", 15)
            response = requests.post(url, **kwargs)

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                sync_limiter.backoff(attempt, retry_after)
                attempt += 1
                continue

            sync_limiter.check_quota_headers(response.headers)
            return response

        except requests.exceptions.RequestException as e:
            logging.error(f"❌ POST failed for {url}: {e}")
            if attempt >= max_attempts:
                raise
            sync_limiter.backoff(attempt)
            attempt += 1

        finally:
            sync_limiter.release()

    raise requests.exceptions.RetryError(f"POST failed after {max_attempts} attempts: {url}")


async def aiohttp_get_with_limit(session, url: str, cost: int = 1, max_attempts: int = 3, **kwargs):
    """
    Rate-limited aiohttp GET with automatic retry

    Args:
        session: aiohttp.ClientSession
        url: URL to fetch
        cost: API cost
        max_attempts: Maximum retry attempts
        **kwargs: Additional arguments for session.get()

    Returns:
        aiohttp.ClientResponse
    """
    attempt = 1

    while attempt <= max_attempts:
        async with async_limiter.slot(cost):
            try:
                kwargs.setdefault("timeout", 15)
                async with session.get(url, **kwargs) as response:
                    if response.status == 429:
                        retry_after = response.headers.get("Retry-After")
                        if retry_after:
                            await asyncio.sleep(float(retry_after))
                        else:
                            await asyncio.sleep(2 ** (attempt - 1))
                        attempt += 1
                        continue

                    await async_limiter.check_quota_headers_async(dict(response.headers))
                    return response

            except Exception as e:
                logging.error(f"❌ Async request failed for {url}: {e}")
                if attempt >= max_attempts:
                    raise
                await asyncio.sleep(2 ** (attempt - 1))
                attempt += 1

    raise Exception(f"Async request failed after {max_attempts} attempts: {url}")


def get_limiter_stats() -> dict:
    """Get performance statistics from both limiters"""
    return {
        "sync_limiter": sync_limiter.get_stats(),
        "async_limiter": {
            "requests_made": async_limiter._stats["requests_made"],
            "throttles_applied": async_limiter._stats["throttles_applied"],
            "proactive_throttles": async_limiter._stats["proactive_throttles"],
        },
    }


def reset_limiter_stats():
    """Reset performance statistics"""
    sync_limiter.stats = {
        "requests_made": 0,
        "throttles_applied": 0,
        "backoffs_triggered": 0,
        "proactive_throttles": 0,
        "last_reset": time.time(),
    }

    async_limiter._stats = {
        "requests_made": 0,
        "throttles_applied": 0,
        "proactive_throttles": 0,
    }

    logging.info("📊 Rate limiter statistics reset")


# Configuration file creation helper
def create_default_config():
    """Create default rate limiting configuration file"""
    config_dir = Path("C:/EQ12/configs")
    config_dir.mkdir(parents=True, exist_ok=True)

    config_path = config_dir / "rate_limit_config.json"

    default_config = {
        "API_THROTTLE": {
            "max_rpm": 30,
            "burst": 5,
            "concurrency": 2,
            "min_interval_ms": 250,
            "soft_remaining_floor": 200,
            "jitter_ms": [50, 150],
            "backoff_base_s": 1.0,
            "backoff_max_s": 8.0,
            "enable_proactive_throttle": True,
            "enable_burst_detection": True,
        },
        "API_ENDPOINTS": {
            "odds_api": {
                "base_url": "https://api.the-odds-api.com",
                "max_rpm": 60,
                "cost_per_request": 1,
            },
            "nba_api": {
                "base_url": "https://api.nba.com",
                "max_rpm": 120,
                "cost_per_request": 1,
            },
        },
    }

    try:
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        logging.info(f"✅ Created default rate limiting config: {config_path}")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to create config file: {e}")
        return False


if __name__ == "__main__":
    # Test the rate limiter
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Rate Limiter Test")
    parser.add_argument("--test-sync", action="store_true", help="Test synchronous limiter")
    parser.add_argument("--test-async", action="store_true", help="Test asynchronous limiter")
    parser.add_argument("--create-config", action="store_true", help="Create default config file")
    parser.add_argument("--requests", type=int, default=10, help="Number of test requests")

    args = parser.parse_args()

    if args.create_config:
        create_default_config()

    if args.test_sync:
        print("🧪 Testing synchronous rate limiter...")
        start_time = time.time()

        for _i in range(args.requests):
            try:
                response = get_with_limit("https://httpbin.org/delay/0.1")
                print("✅ Request {i+1}: HTTP {response.status_code}")
            except Exception:
                print("❌ Request {i+1} failed: {e}")

        duration = time.time() - start_time
        stats = get_limiter_stats()

        print("\n📊 Test Results:")
        print("Duration: {duration:.2f}s")
        print("RPM: {stats['sync_limiter']['current_rpm']:.1f}")
        print("Efficiency: {stats['sync_limiter']['efficiency']:.2%}")
        print("Throttles: {stats['sync_limiter']['throttles_applied']}")

    if args.test_async:
        import aiohttp

        async def test_async_limiter():
            print("🧪 Testing asynchronous rate limiter...")
            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                tasks = []
                for _i in range(args.requests):
                    task = aiohttp_get_with_limit(session, "https://httpbin.org/delay/0.1")
                    tasks.append(task)

                results = await asyncio.gather(*tasks, return_exceptions=True)

                for _i, result in enumerate(results):
                    if isinstance(result, Exception):
                        print("❌ Request {i+1} failed: {result}")
                    else:
                        print("✅ Request {i+1}: HTTP {result.status}")

            time.time() - start_time
            get_limiter_stats()

            print("\n📊 Async Test Results:")
            print("Duration: {duration:.2f}s")
            print("Requests: {stats['async_limiter']['requests_made']}")
            print("Throttles: {stats['async_limiter']['throttles_applied']}")

        asyncio.run(test_async_limiter())
