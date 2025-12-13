#!/usr/bin/env python3
"""
EQ12 Automated Odds Ingest Pipeline
Professional-grade odds polling with UTC normalization and EV calculation.

This is the foundation of the automation stack - runs every 1-2 minutes to:
1. Poll DK/FD/MGM odds from The Odds API
2. Normalize all times to UTC (fixes offset-naive errors)
3. Calculate EV and correlation metrics
4. Persist to structured logs for consumption by schedulers
5. Trigger parlay builders on EV spikes
"""

from eq12_math import (
    expected_value_percentage,
    implied_prob_from_american,
    kelly_fraction,
)
from eq12_timezone import parse_commence_time, utc_now
import asyncio
import json
import logging
import os
import sys
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

import aiofiles
import aiohttp

# Add EQ12 modules to path
sys.path.insert(0, str(Path(__file__).parent))


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/odds_ingest.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


@dataclass
class OddsLeg:
    """Normalized odds leg for EQ12 processing."""

    book: str
    game_id: str
    market: str  # moneyline, spread, total
    selection: str
    odds: int  # American format
    point: float | None = None  # For spreads/totals
    model_prob: float = 0.0
    ev: float = 0.0
    kelly: float = 0.0
    hook_flag: bool = False
    commence_time_utc: str = ""
    last_update_utc: str = ""

    def __post_init__(self):
        """Calculate derived fields after initialization."""
        if self.model_prob > 0:
            self.ev = expected_value_percentage(self.model_prob, self.odds)
            self.kelly = kelly_fraction(self.model_prob, self.odds, kelly_cut=0.5)

        # Check if it's a hook (half-point spread/total)
        if self.point is not None:
            self.hook_flag = abs(self.point % 1) == 0.5

        # Set timestamps
        if not self.last_update_utc:
            self.last_update_utc = utc_now().isoformat()


class EQ12OddsIngestor:
    """
    Production odds ingestion service for EQ12.
    Handles polling, normalization, and EV calculation.
    """

    def __init__(self):
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        if not self.odds_api_key:
            raise ValueError("ODDS_API_KEY environment variable not set")

        # EQ12 Configuration - Expert Sports Betting Focus
        self.allowed_books = ["draftkings", "fanduel", "betmgm"]
        self.target_sports = ["americanfootball_nfl"]  # Focus on NFL
        self.markets = ["h2h", "spreads", "totals"]

        # Paths
        self.logs_dir = Path("C:/EQ12/logs")
        self.logs_dir.mkdir(exist_ok=True)

        # State tracking
        self.last_poll_time = None
        self.polling_interval = 90  # 90 seconds = 1.5 minutes (expert frequency)
        self.session = None

        logger.info("🔄 EQ12 Odds Ingestor initialized")
        logger.info(f"   Books: {', '.join(self.allowed_books)}")
        logger.info(f"   Polling interval: {self.polling_interval}s")

    async def start_continuous_polling(self):
        """Start continuous odds polling with expert timing."""
        logger.info("🚀 Starting continuous odds polling")

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            self.session = session

            while True:
                try:
                    poll_start = datetime.now()

                    # Main polling cycle
                    await self.poll_and_process_odds()

                    # Calculate next poll time
                    poll_duration = (datetime.now() - poll_start).total_seconds()
                    sleep_time = max(0, self.polling_interval - poll_duration)

                    logger.info(
                        f"⏱️ Poll completed in {
                            poll_duration:.1f}s, sleeping {
                            sleep_time:.0f}s")

                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)

                except KeyboardInterrupt:
                    logger.info("👋 Polling stopped by user")
                    break
                except Exception as e:
                    logger.error(f"❌ Polling cycle failed: {e}")
                    logger.error(traceback.format_exc())
                    await asyncio.sleep(30)  # Recovery delay

    async def poll_and_process_odds(self):
        """Execute one complete polling and processing cycle."""
        all_legs = []

        for sport in self.target_sports:
            try:
                # Fetch raw odds
                raw_games = await self.fetch_sport_odds(sport)
                logger.info(f"📥 Fetched {len(raw_games)} games for {sport}")

                # Process each game
                for game in raw_games:
                    legs = self.process_game_to_legs(game)
                    all_legs.extend(legs)

            except Exception as e:
                logger.error(f"❌ Failed to process {sport}: {e}")

        if all_legs:
            # Filter to upcoming games only (expert timing)
            upcoming_legs = self.filter_upcoming_games(all_legs)
            logger.info(f"🎯 Found {len(upcoming_legs)} upcoming legs")

            # Apply model probabilities and calculate EV
            enriched_legs = await self.enrich_with_model_probs(upcoming_legs)

            # Persist to structured logs
            await self.persist_legs(enriched_legs)

            # Check for EV spikes that should trigger builders
            await self.check_ev_spikes(enriched_legs)

        self.last_poll_time = utc_now()

    async def fetch_sport_odds(self, sport: str) -> list[dict]:
        """Fetch odds for a specific sport from The Odds API."""
        url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
        params = {
            "apiKey": self.odds_api_key,
            "regions": "us",
            "markets": ",".join(self.markets),
            "oddsFormat": "american",
            "bookmakers": ",".join(self.allowed_books),  # DK/FD/MGM only
            "dateFormat": "iso",  # Get ISO timestamps
        }

        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"Odds API error: {response.status}")

            return await response.json()

    def process_game_to_legs(self, game: dict) -> list[OddsLeg]:
        """Convert API game data to normalized EQ12 legs."""
        legs = []

        try:
            # Generate standardized game ID
            game_id = self.generate_game_id(game)
            commence_time_utc = self.normalize_commence_time(
                game.get("commence_time", ""))

            # Process each bookmaker
            for bookmaker in game.get("bookmakers", []):
                book_name = self.normalize_book_name(bookmaker.get("title", ""))

                # Skip non-whitelisted books (DK/FD/MGM only)
                if book_name not in self.allowed_books:
                    continue

                # Process each market
                for market in bookmaker.get("markets", []):
                    market_legs = self.process_market_outcomes(
                        game_id, book_name, market, commence_time_utc
                    )
                    legs.extend(market_legs)

        except Exception as e:
            logger.warning(
                f"⚠️ Failed to process game {
                    game.get(
                        'id', 'unknown')}: {e}")

        return legs

    def process_market_outcomes(
        self, game_id: str, book: str, market: dict, commence_time_utc: str
    ) -> list[OddsLeg]:
        """Process market outcomes into OddsLeg objects."""
        legs = []
        market_key = market.get("key")

        # Map API market names
        market_mapping = {"h2h": "moneyline", "spreads": "spread", "totals": "total"}

        market_name = market_mapping.get(market_key)
        if not market_name:
            return legs

        for outcome in market.get("outcomes", []):
            try:
                selection = outcome.get("name", "")
                odds = outcome.get("price")
                point = outcome.get("point")

                if not selection or odds is None:
                    continue

                leg = OddsLeg(
                    book=book,
                    game_id=game_id,
                    market=market_name,
                    selection=selection,
                    odds=odds,
                    point=point,
                    commence_time_utc=commence_time_utc,
                )

                legs.append(leg)

            except Exception as e:
                logger.warning(f"⚠️ Failed to process outcome: {e}")

        return legs

    def generate_game_id(self, game: dict) -> str:
        """Generate standardized game ID."""
        try:
            # Parse commence time for date
            commence_time = parse_commence_time(game["commence_time"])
            date_str = commence_time.strftime("%Y%m%d")

            # Normalize team names
            away_team = game["away_team"].lower().replace(" ", "_")
            home_team = game["home_team"].lower().replace(" ", "_")

            return f"nfl_{date_str}_{away_team}_at_{home_team}"

        except Exception:
            # Fallback to API ID
            return f"game_{game.get('id', int(datetime.now().timestamp()))}"

    def normalize_commence_time(self, commence_time_str: str) -> str:
        """Normalize commence time to UTC ISO format."""
        try:
            dt = parse_commence_time(commence_time_str)
            return dt.isoformat()
        except Exception:
            logger.warning(f"⚠️ Failed to parse commence time: {commence_time_str}")
            return utc_now().isoformat()

    def normalize_book_name(self, book_name: str) -> str:
        """Normalize book names to standard format."""
        book_lower = book_name.lower()

        if "draft" in book_lower or "dk" in book_lower:
            return "draftkings"
        elif "fan" in book_lower or "fd" in book_lower:
            return "fanduel"
        elif "mgm" in book_lower or "betmgm" in book_lower:
            return "betmgm"

        return book_lower

    def filter_upcoming_games(self, legs: list[OddsLeg]) -> list[OddsLeg]:
        """Filter to upcoming games only (expert timing)."""
        now_utc = utc_now()
        cutoff_time = now_utc + timedelta(minutes=30)  # 30 min minimum to kickoff

        upcoming = []
        for leg in legs:
            try:
                commence_time = parse_commence_time(leg.commence_time_utc)
                if commence_time > cutoff_time:
                    upcoming.append(leg)
            except Exception:
                continue

        return upcoming

    async def enrich_with_model_probs(self, legs: list[OddsLeg]) -> list[OddsLeg]:
        """Apply model probabilities and calculate EV/Kelly."""
        enriched = []

        for leg in legs:
            try:
                # Apply model probability (expert betting edge)
                model_prob = self.get_model_probability(leg)

                # Update leg with calculated values
                leg.model_prob = model_prob
                leg.ev = expected_value_percentage(model_prob, leg.odds)
                leg.kelly = kelly_fraction(
                    model_prob, leg.odds, kelly_cut=0.5, max_kelly=0.05)

                enriched.append(leg)

            except Exception as e:
                logger.warning(f"⚠️ Failed to enrich leg: {e}")

        return enriched

    def get_model_probability(self, leg: OddsLeg) -> float:
        """
        Calculate model probability for a leg.
        This is where your edge comes from - replace with actual model.
        """
        # Start with implied probability
        implied = implied_prob_from_american(leg.odds)

        # Expert adjustments based on market inefficiencies
        if leg.market == "moneyline":
            # Public bias adjustment
            if leg.odds < -150:  # Heavy favorite
                return min(0.95, implied * 1.03)  # Slight edge on chalk
            elif leg.odds > 150:  # Underdog
                return max(0.05, implied * 0.97)  # Fade public dogs slightly
            else:
                return implied

        elif leg.market == "spread":
            # Hook advantage (expert knowledge)
            if leg.hook_flag and leg.point is not None:
                key_numbers = [3, 7, 10, 14]  # NFL key numbers
                distance_to_key = min(abs(abs(leg.point) - kn) for kn in key_numbers)

                if distance_to_key == 0.5:  # Perfect hook
                    return min(0.95, implied * 1.08)  # 8% boost for hooks
                elif distance_to_key <= 1:  # Near key number
                    return min(0.95, implied * 1.04)  # 4% boost

            return implied

        elif leg.market == "total":
            # Weather and pace adjustments (expert factors)
            if leg.hook_flag:
                return min(0.95, implied * 1.05)  # 5% boost for total hooks
            return implied

        return implied

    async def persist_legs(self, legs: list[OddsLeg]):
        """Persist legs to structured JSON files."""
        timestamp = utc_now().strftime("%Y%m%d_%H%M%S")

        # Main legs file
        legs_file = self.logs_dir / f"odds_legs_{timestamp}.json"
        legs_data = {
            "timestamp_utc": utc_now().isoformat(),
            "legs_count": len(legs),
            "books": list({leg.book for leg in legs}),
            "legs": [asdict(leg) for leg in legs],
        }

        async with aiofiles.open(legs_file, "w") as f:
            await f.write(json.dumps(legs_data, indent=2))

        # Latest snapshot (for schedulers to consume)
        latest_file = self.logs_dir / "latest_odds_legs.json"
        async with aiofiles.open(latest_file, "w") as f:
            await f.write(json.dumps(legs_data, indent=2))

        logger.info(f"💾 Persisted {len(legs)} legs to {legs_file.name}")

        # Statistics
        positive_ev_count = len([leg for leg in legs if leg.ev > 0])
        hook_count = len([leg for leg in legs if leg.hook_flag])

        logger.info(f"📊 Stats: {positive_ev_count} +EV legs, {hook_count} hooks")

    async def check_ev_spikes(self, legs: list[OddsLeg]):
        """Check for EV spikes that should trigger parlay builders."""
        high_ev_legs = [leg for leg in legs if leg.ev > 0.08]  # 8% threshold

        if len(high_ev_legs) >= 3:  # Minimum for parlay
            spike_file = self.logs_dir / "ev_spike_trigger.json"
            spike_data = {
                "timestamp_utc": utc_now().isoformat(),
                "trigger_reason": "high_ev_spike",
                "high_ev_count": len(high_ev_legs),
                "threshold": 0.08,
                "should_build_parlays": True,
            }

            async with aiofiles.open(spike_file, "w") as f:
                await f.write(json.dumps(spike_data, indent=2))

            logger.info(
                f"🚨 EV SPIKE: {
                    len(high_ev_legs)} legs >8% EV - triggering builders")


async def main():
    """Main entry point for odds ingest automation."""
    logger.info("🔄 EQ12 Automated Odds Ingest Starting")
    logger.info("=" * 50)

    try:
        ingestor = EQ12OddsIngestor()
        await ingestor.start_continuous_polling()

    except KeyboardInterrupt:
        logger.info("\n👋 Odds ingest stopped by user")
    except Exception as e:
        logger.error(f"❌ Odds ingest failed: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
