"""
EQ12 Real-Time Odds Ingestion System
High-frequency odds collection with caching, validation, and rate limiting
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

import os

logger = logging.getLogger(__name__)


class OddsIngestor:
    """
    Real-time odds ingestion with intelligent caching and validation

    Features:
    - Multiple sportsbook API integration
    - Intelligent caching to minimize API calls
    - Real-time change detection
    - Rate limiting and quota management
    - Data validation and sanitization
    """

    def __init__(self):
        self.api_key = os.getenv("ODDS_API_KEY")
        self.base_url = "https://api.the-odds-api.com/v4"

        # Cache configuration
        self.cache_dir = "data/odds_cache"
        self.cache_duration = 300  # 5 minutes default cache
        self.high_frequency_cache = 60  # 1 minute for live games

        # Rate limiting
        self.requests_per_hour = 500
        self.request_log = []

        # Supported sports and markets
        self.supported_sports = [
            "americanfootball_nfl",
            "basketball_nba",
            "baseball_mlb",
            "icehockey_nhl",
        ]

        self.supported_markets = [
            "h2h",  # moneyline
            "spreads",
            "totals",
            "player_props",
        ]

        # Initialize cache directory
        os.makedirs(self.cache_dir, exist_ok=True)

        logger.info("OddsIngestor initialized")
        if self.api_key:
            logger.info("Odds API key configured")
        else:
            logger.warning("No Odds API key found - using cached data only")

    def ingest_live_odds(
        self,
        sport: str = "americanfootball_nfl",
        markets: list[str] | None = None,
        bookmakers: list[str] | None = None,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Ingest live odds with intelligent caching

        Args:
            sport: Sport key (e.g., 'americanfootball_nfl')
            markets: List of markets to fetch
            bookmakers: Specific bookmakers to include
            force_refresh: Bypass cache and fetch fresh data

        Returns:
            Processed odds data with metadata
        """
        if not markets:
            markets = ["h2h", "spreads", "totals"]

        if not bookmakers:
            bookmakers = ["draftkings", "fanduel", "betmgm"]

        # Check cache first
        cache_key = self._generate_cache_key(sport, markets, bookmakers)

        if not force_refresh:
            cached_data = self._get_cached_odds(cache_key)
            if cached_data:
                logger.info("Using cached odds data")
                return cached_data

        # Rate limiting check
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded - using cached data")
            cached_data = self._get_cached_odds(cache_key, ignore_expiry=True)
            if cached_data:
                return cached_data
            else:
                return {"error": "Rate limit exceeded and no cached data available"}

        # Fetch fresh data
        try:
            raw_odds = self._fetch_odds_from_api(sport, markets, bookmakers)

            if raw_odds:
                # Process and validate odds
                processed_odds = self._process_odds_data(raw_odds, sport, markets)

                # Cache the results
                self._cache_odds_data(cache_key, processed_odds)

                # Log ingestion
                self._log_ingestion(sport, markets, len(processed_odds.get("games", [])))

                return processed_odds
            else:
                return {"error": "No odds data received from API"}

        except Exception as e:
            logger.error(f"Odds ingestion failed: {e}")

            # Try to return cached data as fallback
            cached_data = self._get_cached_odds(cache_key, ignore_expiry=True)
            if cached_data:
                logger.info("Using stale cached data due to API error")
                return cached_data

            return {"error": f"Ingestion failed: {e}"}

    def _generate_cache_key(self, sport: str, markets: list[str], bookmakers: list[str]) -> str:
        """Generate unique cache key for request parameters"""
        key_data = f"{sport}_{'-'.join(sorted(markets))}_{'-'.join(sorted(bookmakers))}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_cached_odds(
        self, cache_key: str, ignore_expiry: bool = False
    ) -> dict[str, Any] | None:
        """Get cached odds if available and not expired"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        if not os.path.exists(cache_file):
            return None

        try:
            with open(cache_file, encoding="utf-8") as f:
                cached_data = json.load(f)

            # Check expiry
            if not ignore_expiry:
                cache_time = datetime.fromisoformat(cached_data["cached_at"])

                # Determine cache duration based on data type
                duration = self.cache_duration
                if cached_data.get("is_live"):
                    duration = self.high_frequency_cache

                if datetime.now(UTC) - cache_time > timedelta(seconds=duration):
                    return None

            return cached_data

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Invalid cache file {cache_key}: {e}")
            return None

    def _cache_odds_data(self, cache_key: str, odds_data: dict[str, Any]):
        """Cache odds data with timestamp"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")

        # Add cache metadata
        cached_data = odds_data.copy()
        cached_data["cached_at"] = datetime.now(UTC).isoformat()
        cached_data["cache_key"] = cache_key

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cached_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.warning(f"Failed to cache odds data: {e}")

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        if not self.api_key:
            return False

        now = time.time()

        # Remove old requests (older than 1 hour)
        self.request_log = [req_time for req_time in self.request_log if now - req_time < 3600]

        # Check if we can make another request
        return len(self.request_log) < self.requests_per_hour

    def _log_request(self):
        """Log a new API request for rate limiting"""
        self.request_log.append(time.time())

    def _fetch_odds_from_api(
        self, sport: str, markets: list[str], bookmakers: list[str]
    ) -> list[dict[str, Any]] | None:
        """Fetch odds data from The Odds API"""
        if not self.api_key or not httpx:
            logger.warning("API key or httpx not available")
            return None

        self._log_request()

        # Build API URL
        url = f"{self.base_url}/sports/{sport}/odds"

        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": ",".join(markets),
            "bookmakers": ",".join(bookmakers),
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        try:
            with httpx.Client(timeout=30) as client:
                response = client.get(url, params=params)
                response.raise_for_status()

                odds_data = response.json()
                logger.info(f"Fetched {len(odds_data)} games from Odds API")

                return odds_data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("Odds API rate limit exceeded")
            elif e.response.status_code == 401:
                logger.error("Invalid Odds API key")
            else:
                logger.error(f"Odds API HTTP error: {e.response.status_code}")
            return None

        except Exception as e:
            logger.error(f"Odds API request failed: {e}")
            return None

    def _process_odds_data(
        self, raw_odds: list[dict], sport: str, markets: list[str]
    ) -> dict[str, Any]:
        """Process and validate raw odds data"""
        processed_games = []
        live_games = 0

        for game_data in raw_odds:
            try:
                processed_game = self._process_single_game(game_data, sport)
                if processed_game:
                    processed_games.append(processed_game)

                    # Check if game is live
                    commence_time = datetime.fromisoformat(game_data["commence_time"])
                    if commence_time <= datetime.now(UTC):
                        live_games += 1

            except Exception as e:
                logger.warning(f"Failed to process game: {e}")
                continue

        return {
            "sport": sport,
            "markets": markets,
            "games": processed_games,
            "total_games": len(processed_games),
            "live_games": live_games,
            "is_live": live_games > 0,
            "ingested_at": datetime.now(UTC).isoformat(),
            "data_quality": self._assess_data_quality(processed_games),
        }

    def _process_single_game(self, game_data: dict, sport: str) -> dict[str, Any] | None:
        """Process a single game's odds data"""
        try:
            processed_game = {
                "id": game_data["id"],
                "sport": sport,
                "commence_time": game_data["commence_time"],
                "home_team": game_data["home_team"],
                "away_team": game_data["away_team"],
                "bookmakers": [],
            }

            # Process bookmaker odds
            for bookmaker in game_data.get("bookmakers", []):
                processed_bookmaker = self._process_bookmaker_odds(bookmaker)
                if processed_bookmaker:
                    processed_game["bookmakers"].append(processed_bookmaker)

            # Validate game has usable odds
            if not processed_game["bookmakers"]:
                return None

            # Add derived information
            processed_game["best_odds"] = self._find_best_odds(processed_game["bookmakers"])
            processed_game["market_summary"] = self._summarize_markets(processed_game["bookmakers"])

            return processed_game

        except KeyError as e:
            logger.warning(f"Missing required field in game data: {e}")
            return None

    def _process_bookmaker_odds(self, bookmaker_data: dict) -> dict[str, Any] | None:
        """Process odds for a single bookmaker"""
        try:
            processed_bookmaker = {
                "key": bookmaker_data["key"],
                "title": bookmaker_data["title"],
                "last_update": bookmaker_data["last_update"],
                "markets": {},
            }

            # Process each market
            for market in bookmaker_data.get("markets", []):
                market_key = market["key"]
                processed_bookmaker["markets"][market_key] = {
                    "last_update": market["last_update"],
                    "outcomes": [],
                }

                # Process outcomes
                for outcome in market.get("outcomes", []):
                    processed_outcome = {"name": outcome["name"], "price": outcome["price"]}

                    # Add point for spread/totals
                    if "point" in outcome:
                        processed_outcome["point"] = outcome["point"]

                    processed_bookmaker["markets"][market_key]["outcomes"].append(processed_outcome)

            return processed_bookmaker

        except KeyError as e:
            logger.warning(f"Missing required field in bookmaker data: {e}")
            return None

    def _find_best_odds(self, bookmakers: list[dict]) -> dict[str, Any]:
        """Find best odds across all bookmakers"""
        best_odds = {}

        for bookmaker in bookmakers:
            for market_key, market_data in bookmaker["markets"].items():
                if market_key not in best_odds:
                    best_odds[market_key] = {}

                for outcome in market_data["outcomes"]:
                    outcome_name = outcome["name"]
                    price = outcome["price"]

                    # For American odds, higher positive or lower negative is better
                    if outcome_name not in best_odds[market_key]:
                        best_odds[market_key][outcome_name] = {
                            "price": price,
                            "bookmaker": bookmaker["key"],
                        }
                    else:
                        current_best = best_odds[market_key][outcome_name]["price"]
                        if self._is_better_odds(price, current_best):
                            best_odds[market_key][outcome_name] = {
                                "price": price,
                                "bookmaker": bookmaker["key"],
                            }

        return best_odds

    def _is_better_odds(self, new_price: int, current_price: int) -> bool:
        """Determine if new odds are better than current"""
        # For positive odds, higher is better
        if new_price > 0 and current_price > 0:
            return new_price > current_price

        # For negative odds, closer to 0 (higher absolute value) is worse
        if new_price < 0 and current_price < 0:
            return new_price > current_price

        # Positive odds are generally better than negative
        if new_price > 0 and current_price < 0:
            return True

        if new_price < 0 and current_price > 0:
            return False

        return False

    def _summarize_markets(self, bookmakers: list[dict]) -> dict[str, Any]:
        """Summarize available markets"""
        markets_summary = {}

        for bookmaker in bookmakers:
            for market_key in bookmaker["markets"]:
                if market_key not in markets_summary:
                    markets_summary[market_key] = {"bookmaker_count": 0, "bookmakers": []}

                markets_summary[market_key]["bookmaker_count"] += 1
                markets_summary[market_key]["bookmakers"].append(bookmaker["key"])

        return markets_summary

    def _assess_data_quality(self, games: list[dict]) -> dict[str, Any]:
        """Assess quality of ingested data"""
        if not games:
            return {"quality_score": 0, "issues": ["No games data"]}

        total_games = len(games)
        games_with_odds = sum(1 for game in games if game.get("bookmakers"))
        games_with_multiple_books = sum(1 for game in games if len(game.get("bookmakers", [])) > 1)

        quality_score = (games_with_odds / total_games) * 100

        return {
            "quality_score": round(quality_score, 1),
            "total_games": total_games,
            "games_with_odds": games_with_odds,
            "games_with_multiple_books": games_with_multiple_books,
            "avg_bookmakers_per_game": round(
                sum(len(game.get("bookmakers", [])) for game in games) / total_games, 1
            ),
        }

    def _log_ingestion(self, sport: str, markets: list[str], game_count: int):
        """Log ingestion activity"""
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "sport": sport,
            "markets": markets,
            "games_ingested": game_count,
            "requests_used": len(self.request_log),
            "requests_remaining": self.requests_per_hour - len(self.request_log),
        }

        log_file = os.path.join("logs", "odds_ingestion.jsonl")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to log ingestion: {e}")

    def get_ingestion_stats(self, days: int = 1) -> dict[str, Any]:
        """Get ingestion statistics"""
        log_file = os.path.join("logs", "odds_ingestion.jsonl")

        if not os.path.exists(log_file):
            return {"error": "No ingestion log found"}

        try:
            cutoff_date = datetime.now(UTC) - timedelta(days=days)

            total_ingestions = 0
            total_games = 0
            sports_breakdown = {}

            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry["timestamp"])

                        if entry_time >= cutoff_date:
                            total_ingestions += 1
                            total_games += entry.get("games_ingested", 0)

                            sport = entry.get("sport", "unknown")
                            sports_breakdown[sport] = sports_breakdown.get(sport, 0) + 1

                    except (json.JSONDecodeError, KeyError, ValueError):
                        continue

            return {
                "period_days": days,
                "total_ingestions": total_ingestions,
                "total_games_processed": total_games,
                "avg_games_per_ingestion": round(total_games / max(total_ingestions, 1), 1),
                "sports_breakdown": sports_breakdown,
                "current_cache_files": len(os.listdir(self.cache_dir)),
                "rate_limit_status": {
                    "requests_used": len(self.request_log),
                    "requests_remaining": self.requests_per_hour - len(self.request_log),
                },
            }

        except Exception as e:
            return {"error": f"Failed to analyze ingestion stats: {e}"}

    def cleanup_cache(self, max_age_hours: int = 24):
        """Clean up old cache files"""
        if not os.path.exists(self.cache_dir):
            return

        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_files = 0

        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)

            try:
                if os.path.getctime(file_path) < cutoff_time:
                    os.remove(file_path)
                    cleaned_files += 1
            except Exception as e:
                logger.warning(f"Failed to clean cache file {filename}: {e}")

        logger.info(f"Cleaned {cleaned_files} old cache files")


def test_odds_ingestor():
    """Test odds ingestion system"""
    try:
        ingestor = OddsIngestor()

        print("🏈 Testing Odds Ingestor...")

        # Test with cached data (should work without API key)
        result = ingestor.ingest_live_odds(
            sport="americanfootball_nfl",
            markets=["h2h", "spreads"],
            bookmakers=["draftkings", "fanduel"],
        )

        print(f"📊 Ingestion Result: {result}")

        # Test stats
        stats = ingestor.get_ingestion_stats()
        print(f"📈 Stats: {stats}")

        return "error" not in result or "No odds data" in str(result)

    except Exception as e:
        print(f"❌ Odds ingestor test failed: {e}")
        return False


if __name__ == "__main__":
    test_odds_ingestor()
