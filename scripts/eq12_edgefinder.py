#!/usr/bin/env python3
"""
EQ12 EdgeFinder Service
Production daemon to pull DK/FD/MGM markets, normalize odds, compute EV/Kelly.

This is the core service that ties together all EQ12 components:
- Odds fetching from The Odds API
- AI-powered normalization via Responses API
- Mathematical EV/Kelly calculations
- Parlay construction with multiple strategies
- Telegram alerting for profitable opportunities
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict
from datetime import timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from eq12_parlay_builder import Parlay, ParlayBuilder
from eq12_timezone import (
    filter_upcoming_games,
    parse_commence_time,
    utc_now,
)

# Import our EQ12 components
from eq12_math import (
    expected_value_percentage,
    kelly_fraction,
)
from eq12_responses_client import create_eq12_responses_client

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/edgefinder.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class EdgeFinderConfig:
    """Configuration for EdgeFinder service."""

    def __init__(self):
        # Load environment variables
        load_dotenv()

        # API Keys
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # EQ12 Settings
        self.allowed_books = ["draftkings", "fanduel", "betmgm"]
        self.target_sports = ["americanfootball_nfl"]
        self.min_ev_threshold = 0.025  # 2.5% minimum edge
        self.kelly_multiplier = 0.5  # Half-Kelly sizing
        self.max_legs_per_parlay = 6
        self.correlation_penalty = 0.15
        self.bankroll = 1000.0

        # Service Settings
        self.polling_interval = 45  # seconds between polls
        self.steaming_interval = 15  # seconds for steaming window
        self.alert_threshold = 0.04  # 4% EV for alerts
        self.max_alerts_per_hour = 5

        # Validate required keys
        missing_keys = []
        for key, value in [
            ("ODDS_API_KEY", self.odds_api_key),
            ("OPENAI_API_KEY", self.openai_api_key),
        ]:
            if not value:
                missing_keys.append(key)

        if missing_keys:
            raise ValueError(f"Missing required environment variables: {missing_keys}")


class EdgeFinderService:
    """
    Production EdgeFinder service for automated parlay discovery.
    Combines odds fetching, AI normalization, and parlay construction.
    """

    def __init__(self, config: EdgeFinderConfig):
        self.config = config
        self.running = False
        self.alert_count_reset = utc_now()
        self.alert_count = 0

        # Initialize components
        self.parlay_builder = ParlayBuilder(bankroll=config.bankroll)

        try:
            self.ai_client = create_eq12_responses_client(config.openai_api_key)
            logger.info("🤖 AI client initialized")
        except Exception as e:
            logger.warning(f"⚠️ AI client failed to initialize: {e}")
            self.ai_client = None

        # State tracking
        self.last_poll_time = None
        self.legs_database = []  # In-memory storage (could be DB)
        self.recent_alerts = []

        logger.info("🔍 EdgeFinder service initialized")

    async def start_daemon(self):
        """Start the EdgeFinder daemon with continuous monitoring."""
        logger.info("🚀 Starting EdgeFinder daemon")
        self.running = True

        try:
            while self.running:
                cycle_start = time.time()

                # Main processing cycle
                await self.process_cycle()

                # Calculate sleep time to maintain interval
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, self.config.polling_interval - cycle_duration)

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(
                        f"⚠️ Cycle took {
                            cycle_duration:.1f}s, no sleep time")

        except KeyboardInterrupt:
            logger.info("👋 Daemon stopped by user")
        except Exception as e:
            logger.error(f"❌ Daemon error: {e}")
        finally:
            self.running = False
            logger.info("🛑 EdgeFinder daemon stopped")

    async def process_cycle(self):
        """Process one complete cycle of odds fetching and analysis."""
        try:
            # Step 1: Fetch fresh odds
            raw_games = await self.fetch_odds_for_sports()
            if not raw_games:
                logger.info("📭 No games available")
                return

            # Step 2: Filter to upcoming games only
            upcoming_games = filter_upcoming_games(raw_games, "commence_time")
            logger.info(f"🎯 Found {len(upcoming_games)} upcoming games")

            # Step 3: Process each game for legs
            all_legs = []
            for game in upcoming_games:
                legs = await self.process_game_for_legs(game)
                all_legs.extend(legs)

            # Step 4: Update legs database
            self.legs_database = all_legs
            logger.info(f"💾 Updated database with {len(all_legs)} legs")

            # Step 5: Build parlays using multiple strategies
            if all_legs:
                await self.build_and_analyze_parlays(all_legs)

            # Step 6: Clean up old data
            self.cleanup_old_data()

            self.last_poll_time = utc_now()

        except Exception as e:
            logger.error(f"❌ Process cycle error: {e}")

    async def fetch_odds_for_sports(self) -> list[dict]:
        """Fetch odds from The Odds API for configured sports."""
        all_games = []

        for sport in self.config.target_sports:
            try:
                games = await self.fetch_sport_odds(sport)
                all_games.extend(games)
                logger.info(f"📥 Fetched {len(games)} games for {sport}")

            except Exception as e:
                logger.error(f"❌ Error fetching {sport}: {e}")

        return all_games

    async def fetch_sport_odds(self, sport: str) -> list[dict]:
        """Fetch odds for a specific sport."""
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
        params = {
            "apiKey": self.config.odds_api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "bookmakers": ",".join(self.config.allowed_books),
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        return response.json()

    async def process_game_for_legs(self, game: dict) -> list[dict]:
        """Process individual game to extract betting legs."""
        legs = []

        try:
            game_id = self.generate_game_id(game)
            commence_time = game.get("commence_time")

            # Process each bookmaker
            for bookmaker in game.get("bookmakers", []):
                book_name = bookmaker.get("title", "").lower()

                # Filter to allowed books
                if not any(
                        allowed in book_name for allowed in self.config.allowed_books):
                    continue

                # Process each market
                for market in bookmaker.get("markets", []):
                    market_legs = self.process_market_outcomes(
                        game_id, book_name, market, commence_time
                    )
                    legs.extend(market_legs)

        except Exception as e:
            logger.warning(f"⚠️ Error processing game {game.get('id', 'unknown')}: {e}")

        return legs

    def process_market_outcomes(
        self, game_id: str, book: str, market: dict, commence_time: str
    ) -> list[dict]:
        """Process market outcomes into betting legs."""
        legs = []
        market_key = market.get("key")

        # Map API market names to our format
        market_mapping = {"h2h": "moneyline", "spreads": "spread", "totals": "total"}

        market_name = market_mapping.get(market_key)
        if not market_name:
            return legs

        for outcome in market.get("outcomes", []):
            try:
                # Extract outcome data
                selection = outcome.get("name", "")
                odds = outcome.get("price")
                point = outcome.get("point")  # For spreads/totals

                if not selection or odds is None:
                    continue

                # Generate model probability (placeholder - integrate your model here)
                model_prob = self.estimate_model_probability(
                    game_id, market_name, selection, odds, point
                )

                # Calculate EV and Kelly
                ev = expected_value_percentage(model_prob, odds)
                kelly = kelly_fraction(
                    model_prob,
                    odds,
                    kelly_cut=self.config.kelly_multiplier,
                    max_kelly=0.025,
                )

                leg = {
                    "game_id": game_id,
                    "book": self.normalize_book_name(book),
                    "market": market_name,
                    "selection": selection,
                    "odds": odds,
                    "point": point,
                    "model_prob": model_prob,
                    "ev": ev,
                    "kelly": kelly,
                    "commence_time": commence_time,
                    "last_update": utc_now().isoformat(),
                    "hook_flag": point is not None and abs(point % 1) == 0.5,
                }

                legs.append(leg)

            except Exception as e:
                logger.warning(f"⚠️ Error processing outcome: {e}")

        return legs

    def estimate_model_probability(
        self, game_id: str, market: str, selection: str, odds: int, point: float | None
    ) -> float:
        """
        Estimate model probability for outcome.
        PLACEHOLDER - integrate your actual model here.
        """
        # Simple placeholder logic - replace with your model
        from eq12_math import implied_prob_from_american

        # Start with implied probability
        implied = implied_prob_from_american(odds)

        # Add some simple adjustments (placeholder logic)
        if market == "moneyline":
            # Slight favorite bias adjustment
            if odds < 0:  # Favorite
                return min(0.95, implied * 1.05)
            else:  # Underdog
                return max(0.05, implied * 0.98)

        elif market == "spread":
            # Slight home field advantage (very crude)
            if "home" in selection.lower():
                return min(0.95, implied * 1.02)
            return max(0.05, implied * 0.98)

        elif market == "total":
            # Weather/pace adjustments would go here
            return implied

        return implied

    def generate_game_id(self, game: dict) -> str:
        """Generate standardized game ID."""
        try:
            commence_time = parse_commence_time(game["commence_time"])
            date_str = commence_time.strftime("%Y%m%d")

            away_team = game["away_team"].lower().replace(" ", "_")
            home_team = game["home_team"].lower().replace(" ", "_")

            return f"nfl_{date_str}_{away_team}_{home_team}"

        except Exception:
            # Fallback
            return f"game_{int(time.time())}"

    def normalize_book_name(self, book: str) -> str:
        """Normalize book names to standard format."""
        book_lower = book.lower()

        if "draft" in book_lower:
            return "draftkings"
        elif "fan" in book_lower:
            return "fanduel"
        elif "mgm" in book_lower or "betmgm" in book_lower:
            return "betmgm"

        return book_lower

    async def build_and_analyze_parlays(self, legs: list[dict]):
        """Build parlays and send alerts for profitable opportunities."""
        # Filter legs with positive EV
        positive_ev_legs = [leg for leg in legs if leg["ev"] > 0]

        if len(positive_ev_legs) < 2:
            logger.info("📊 Insufficient positive EV legs for parlays")
            return

        # Build parlays with all strategies
        strategies = ["balanced", "conservative", "yolo", "spreads_only"]
        parlays = self.parlay_builder.build_all_strategies(positive_ev_legs, strategies)

        logger.info(
            f"🎰 Built {
                len(parlays)} parlays across {
                len(strategies)} strategies")

        # Analyze and alert on profitable parlays
        for parlay in parlays:
            await self.analyze_parlay_for_alerts(parlay)

        # Log to file for tracking
        await self.log_parlays_to_file(parlays)

    async def analyze_parlay_for_alerts(self, parlay: Parlay):
        """Analyze parlay and send alerts if thresholds met."""
        # Check if EV meets alert threshold
        ev_percentage = parlay.expected_value_dollars / parlay.stake_dollars

        if ev_percentage < self.config.alert_threshold:
            return

        # Check alert rate limiting
        if self.alert_count >= self.config.max_alerts_per_hour:
            # Reset counter if hour has passed
            if utc_now() - self.alert_count_reset > timedelta(hours=1):
                self.alert_count = 0
                self.alert_count_reset = utc_now()
            else:
                return

        # Generate and send alert
        await self.send_parlay_alert(parlay)
        self.alert_count += 1

    async def send_parlay_alert(self, parlay: Parlay):
        """Send Telegram alert for profitable parlay."""
        try:
            # Generate alert copy using AI if available
            if self.ai_client:
                alert_text = self.ai_client.generate_alert_copy(asdict(parlay))
            else:
                alert_text = self.generate_basic_alert(parlay)

            # Send to Telegram (if configured)
            if self.config.telegram_token and self.config.telegram_chat_id:
                await self.send_telegram_message(alert_text)

            # Log alert
            logger.info(f"🚨 ALERT SENT: {alert_text[:100]}...")

        except Exception as e:
            logger.error(f"❌ Alert sending failed: {e}")

    def generate_basic_alert(self, parlay: Parlay) -> str:
        """Generate basic alert text without AI."""
        ev_pct = (parlay.expected_value_dollars / parlay.stake_dollars) * 100

        return (
            f"🔥 {len(parlay.legs)}-leg {parlay.strategy} parlay @ "
            f"{parlay.combined_odds:+d} odds. "
            f"{ev_pct:.1f}% EV, ${parlay.expected_value_dollars:+.2f} expected profit. "
            f"Stake ${parlay.stake_dollars:.0f} • Risk: {parlay.risk_level}"
        )

    async def send_telegram_message(self, message: str):
        """Send message to Telegram."""
        try:
            url = f"https://api.telegram.org/bot{
                self.config.telegram_token}/sendMessage"
            data = {
                "chat_id": self.config.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML",
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

        except Exception as e:
            logger.error(f"❌ Telegram send failed: {e}")

    async def log_parlays_to_file(self, parlays: list[Parlay]):
        """Log parlays to file for tracking."""
        try:
            log_dir = Path("C:/EQ12/logs")
            log_dir.mkdir(exist_ok=True)

            timestamp = utc_now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"parlays_{timestamp}.json"

            parlay_data = {
                "timestamp": utc_now().isoformat(),
                "parlays": [asdict(parlay) for parlay in parlays],
                "legs_analyzed": len(self.legs_database),
                "config": {
                    "bankroll": self.config.bankroll,
                    "min_ev": self.config.min_ev_threshold,
                    "max_legs": self.config.max_legs_per_parlay,
                },
            }

            with open(log_file, "w") as f:
                json.dump(parlay_data, f, indent=2)

            logger.info(f"📁 Logged {len(parlays)} parlays to {log_file.name}")

        except Exception as e:
            logger.error(f"❌ Logging failed: {e}")

    def cleanup_old_data(self):
        """Clean up old legs and alerts."""
        cutoff_time = utc_now() - timedelta(hours=6)

        # Remove old legs
        original_count = len(self.legs_database)
        self.legs_database = [
            leg
            for leg in self.legs_database
            if parse_commence_time(leg.get("commence_time", "")) > cutoff_time
        ]

        removed = original_count - len(self.legs_database)
        if removed > 0:
            logger.info(f"🗑️ Cleaned up {removed} old legs")

    def stop(self):
        """Stop the daemon."""
        logger.info("🛑 Stop signal received")
        self.running = False


async def main():
    """Main entry point for EdgeFinder service."""
    print("🔍 EQ12 EdgeFinder Service")
    print("=" * 50)

    try:
        # Load configuration
        config = EdgeFinderConfig()

        # Create and start service
        service = EdgeFinderService(config)
        await service.start_daemon()

    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except Exception as e:
        print(f"❌ Service failed: {e}")
        logger.error(f"Service failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
