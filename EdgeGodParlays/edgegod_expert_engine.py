#!/usr/bin/env python3
"""
EQ12 EdgeGod Expert Odds Engine
Enhanced production-ready odds engine integrated with EQ12 stack
Includes: Telegram alerts, bankroll sizing, parlay construction, MLB TB/HR logic
"""

import asyncio
import json
import logging
import os
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import aiofiles
import httpx
import numpy as np
import pytz
from api_manager import EdgeGodAPIManager
from fastapi import BackgroundTasks, FastAPI, Query
from pydantic import BaseModel
from telegram import Bot

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# API Configuration
API_HOST = "https://api.the-odds-api.com/v4"
API_KEY = os.environ.get("ODDS_API_KEY", "")
NY_TZ = pytz.timezone("America/New_York")

# EQ12 Integration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
EQ12_LOGS = os.environ.get("EQ12_LOGS", "./logs")

# EdgeGod Configuration
BANKROLL_BASE = float(os.environ.get("BANKROLL_BASE", "1000"))
MIN_EDGE_THRESHOLD = float(os.environ.get("MIN_EDGE_THRESHOLD", "0.02"))  # 2% minimum edge
MAX_SINGLE_BET_PERCENTAGE = float(
    os.environ.get("MAX_SINGLE_BET_PERCENTAGE", "0.05")
)  # 5% max per bet
PARLAY_MIN_LEGS = int(os.environ.get("PARLAY_MIN_LEGS", "2"))
PARLAY_MAX_LEGS = int(os.environ.get("PARLAY_MAX_LEGS", "8"))

# API Management Configuration
MAX_CONCURRENT_REQUESTS = 8  # Limit concurrent API calls
REQUEST_JITTER_MAX = 0.05  # Add small random delays (50ms max)
BATCH_SIZE = 15  # Events per API call batch
RETRY_DELAYS = [1.0, 2.0, 4.0, 8.0]  # Exponential backoff delays

# Initialize EdgeGod API Manager
api_manager = None
concurrency_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


async def initialize_api_manager():
    """Initialize the EdgeGod API manager with comprehensive rate limiting"""
    global api_manager
    if not API_KEY:
        raise ValueError("ODDS_API_KEY environment variable required")

    api_manager = EdgeGodAPIManager(
        api_key=API_KEY,
        max_daily_quota=450,  # Conservative daily limit
        rate_limit=25.0,  # 25 calls/sec (under 30/sec API limit)
        cache_duration=900,  # 15-minute cache
    )
    logger.info("EdgeGod API Manager initialized with comprehensive rate limiting")
    return api_manager


async def close_api_manager():
    """Clean shutdown of API manager"""
    global api_manager
    if api_manager:
        await api_manager.close()
        logger.info("API Manager closed")


async def make_api_call_with_management(endpoint: str, params: dict[str, Any] | None = None) -> Any:
    """Make API call using EdgeGod API manager with comprehensive protection"""
    global api_manager
    if not api_manager:
        await initialize_api_manager()

    # Add request jitter to prevent burst patterns
    if REQUEST_JITTER_MAX > 0:
        jitter = random.uniform(0, REQUEST_JITTER_MAX)
        await asyncio.sleep(jitter)

    # Use concurrency control
    async with concurrency_semaphore:
        try:
            response = await api_manager.make_api_call(endpoint, params or {})
            return response
        except Exception as e:
            logger.error(f"API call failed for {endpoint}: {e}")
            # Log usage stats on errors for debugging
            if api_manager:
                stats = api_manager.get_usage_stats()
                logger.info(
                    f"Current API usage: {stats['requests']['total']} total, {stats['quota']['daily_used']}/{stats['quota']['daily_limit']} daily"
                )
            raise


@dataclass
class EdgeBet:
    """Represents a bet with calculated edge and kelly sizing"""

    event_id: str
    sport: str
    market: str
    selection: str
    book: str
    odds: float
    implied_prob: float
    fair_prob: float
    edge: float
    kelly_fraction: float
    bet_size: float
    confidence: str  # 'LOCK', 'STRONG', 'MODERATE', 'WEAK'


class BankrollManager:
    """EQ12 Bankroll Management with Kelly Criterion and Risk Controls"""

    def __init__(self, base_bankroll: float):
        self.base_bankroll = base_bankroll
        self.current_bankroll = base_bankroll
        self.max_bet_percentage = MAX_SINGLE_BET_PERCENTAGE
        self.min_edge = MIN_EDGE_THRESHOLD

    def calculate_kelly_size(self, odds: float, win_prob: float) -> float:
        """Calculate Kelly Criterion bet size"""
        if win_prob <= 0 or odds <= 0:
            return 0.0

        # Convert American odds to decimal for Kelly calculation
        if odds > 0:
            decimal_odds = (odds / 100) + 1
        else:
            decimal_odds = (100 / abs(odds)) + 1

        # Kelly formula: f = (bp - q) / b
        # where b = odds-1, p = win_prob, q = 1-p
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p

        kelly_fraction = (b * p - q) / b

        # Apply risk management: cap at max percentage and apply fractional kelly
        conservative_kelly = kelly_fraction * 0.25  # Quarter Kelly for safety
        return min(conservative_kelly, self.max_bet_percentage)

    def calculate_bet_size(self, kelly_fraction: float) -> float:
        """Convert Kelly fraction to actual bet size"""
        return self.current_bankroll * kelly_fraction

    def classify_confidence(self, edge: float, kelly_fraction: float) -> str:
        """Classify bet confidence based on edge and Kelly sizing"""
        if edge >= 0.08 and kelly_fraction >= 0.03:  # 8% edge, 3%+ Kelly
            return "LOCK"
        if edge >= 0.05 and kelly_fraction >= 0.02:  # 5% edge, 2%+ Kelly
            return "STRONG"
        if edge >= 0.03 and kelly_fraction >= 0.01:  # 3% edge, 1%+ Kelly
            return "MODERATE"
        return "WEAK"


class MLBExpertAnalyzer:
    """MLB-specific analysis with TB/HR logic and IL exclusions"""

    def __init__(self):
        self.il_exclusions = set()  # Injured List exclusions
        self.tb_hr_correlations = {}  # Team total bases / home run correlations

    async def analyze_mlb_props(self, event: dict[str, Any]) -> list[EdgeBet]:
        """Analyze MLB player props with advanced metrics"""
        edge_bets = []

        # Extract teams for IL checking
        home_team = event.get("home_team", "")
        away_team = event.get("away_team", "")

        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                market_key = market.get("key", "")

                # Focus on MLB-specific props
                if "batter_" in market_key:
                    if (
                        "total_bases" in market_key
                        or "home_runs" in market_key
                        or "hits" in market_key
                    ):
                        prop_bets = await self._analyze_tb_hr_props(market, bookmaker)
                        edge_bets.extend(prop_bets)

        return edge_bets

    async def _analyze_tb_hr_props(self, market: dict, bookmaker: dict) -> list[EdgeBet]:
        """Analyze total bases and home run props with correlation logic"""
        edge_bets = []

        for outcome in market.get("outcomes", []):
            if outcome.get("name") != "Over":
                continue
            player_name = outcome.get("description", "") or outcome.get("name", "")

            # Skip if player is on IL
            if self._is_on_injured_list(player_name):
                logger.info(f"Skipping IL player: {player_name}")
                continue

            # Calculate fair value based on historical data
            fair_prob = await self._calculate_fair_probability(
                player_name,
                market["key"],
                float(outcome.get("point", 0.0) or 0.0),
            )

            if fair_prob > 0:
                odds = outcome.get("price", 0)
                implied_prob = self._american_to_implied(odds)
                edge = fair_prob - implied_prob

                if edge >= MIN_EDGE_THRESHOLD:
                    bankroll_mgr = BankrollManager(BANKROLL_BASE)
                    kelly = bankroll_mgr.calculate_kelly_size(odds, fair_prob)
                    bet_size = bankroll_mgr.calculate_bet_size(kelly)
                    confidence = bankroll_mgr.classify_confidence(edge, kelly)

                    edge_bet = EdgeBet(
                        event_id=outcome.get("event_id", ""),
                        sport="MLB",
                        market=market["key"],
                        selection=f"{player_name} Over {outcome.get('point', 'N/A')}",
                        book=bookmaker["title"],
                        odds=odds,
                        implied_prob=implied_prob,
                        fair_prob=fair_prob,
                        edge=edge,
                        kelly_fraction=kelly,
                        bet_size=bet_size,
                        confidence=confidence,
                    )
                    edge_bets.append(edge_bet)

        return edge_bets

    def _is_on_injured_list(self, player_name: str) -> bool:
        """Check if player is on injured list"""
        return player_name.lower() in self.il_exclusions

    async def _calculate_fair_probability(
        self,
        player_name: str,
        market_key: str,
        line: float,
    ) -> float:
        """Calculate fair probability based on historical data and models"""
        # Placeholder for advanced statistical modeling
        # In production, this would query player stats, weather, matchups, etc.

        if "hits" in market_key:
            if line <= 0.5:
                return 0.62
            if line <= 1.5:
                return 0.28
            return 0.12
        if "total_bases" in market_key:
            if line <= 0.5:
                return 0.60
            if line <= 1.5:
                return 0.38
            if line <= 2.5:
                return 0.22
            return 0.10
        if "home_runs" in market_key:
            if line <= 0.5:
                return 0.18
            return 0.04

        return 0.0

    def _american_to_implied(self, american: float) -> float:
        """Convert American odds to implied probability"""
        if american > 0:
            return 100.0 / (american + 100.0)
        return (-american) / ((-american) + 100.0)


class ParlayConstructor:
    """Intelligent parlay construction with correlation analysis"""

    def __init__(self):
        self.max_legs = PARLAY_MAX_LEGS
        self.min_legs = PARLAY_MIN_LEGS
        self.correlation_matrix = {}

    def build_optimal_parlays(self, edge_bets: list[EdgeBet]) -> list[dict[str, Any]]:
        """Build optimal parlays from available edge bets"""
        parlays = []

        # Filter for quality bets
        quality_bets = [bet for bet in edge_bets if bet.confidence in ["LOCK", "STRONG"]]

        if len(quality_bets) < self.min_legs:
            return parlays

        # Build uncorrelated parlays
        for combo_size in range(self.min_legs, min(self.max_legs + 1, len(quality_bets) + 1)):
            best_combos = self._find_best_combinations(quality_bets, combo_size)

            for combo in best_combos[:3]:  # Top 3 combinations per size
                parlay = self._construct_parlay(combo)
                if parlay:
                    parlays.append(parlay)

        return sorted(parlays, key=lambda x: x["expected_value"], reverse=True)

    def _find_best_combinations(self, bets: list[EdgeBet], combo_size: int) -> list[list[EdgeBet]]:
        """Find best uncorrelated combinations"""
        from itertools import combinations

        valid_combos = []

        for combo in combinations(bets, combo_size):
            if self._is_uncorrelated(combo):
                expected_value = self._calculate_combo_ev(combo)
                valid_combos.append((combo, expected_value))

        # Sort by expected value and return top combinations
        valid_combos.sort(key=lambda x: x[1], reverse=True)
        return [combo[0] for combo in valid_combos[:10]]

    def _is_uncorrelated(self, bets: list[EdgeBet]) -> bool:
        """Check if bets are uncorrelated (same game, same player, etc.)"""
        events = set()
        players = set()

        for bet in bets:
            # Same event correlation
            if bet.event_id in events:
                return False
            events.add(bet.event_id)

            # Same player correlation (extract from selection)
            player = bet.selection.split(" - ")[0] if " - " in bet.selection else bet.selection
            if player in players:
                return False
            players.add(player)

        return True

    def _calculate_combo_ev(self, bets: list[EdgeBet]) -> float:
        """Calculate expected value of parlay combination"""
        total_prob = 1.0
        total_odds = 1.0

        for bet in bets:
            total_prob *= bet.fair_prob

            # Convert to decimal odds
            if bet.odds > 0:
                decimal_odds = (bet.odds / 100) + 1
            else:
                decimal_odds = (100 / abs(bet.odds)) + 1

            total_odds *= decimal_odds

        return (total_prob * total_odds) - 1.0  # Expected value

    def _construct_parlay(self, bets: list[EdgeBet]) -> dict[str, Any] | None:
        """Construct parlay details"""
        if not bets:
            return None

        total_odds = 1.0
        total_prob = 1.0
        selections = []

        for bet in bets:
            # Convert to decimal for calculation
            if bet.odds > 0:
                decimal_odds = (bet.odds / 100) + 1
            else:
                decimal_odds = (100 / abs(bet.odds)) + 1

            total_odds *= decimal_odds
            total_prob *= bet.fair_prob

            selections.append(
                {
                    "sport": bet.sport,
                    "market": bet.market,
                    "selection": bet.selection,
                    "book": bet.book,
                    "odds": bet.odds,
                    "confidence": bet.confidence,
                }
            )

        # Convert back to American odds for display
        american_odds = (total_odds - 1) * 100 if total_odds >= 2 else -100 / (total_odds - 1)

        expected_value = self._calculate_combo_ev(bets)

        # Kelly sizing for parlay
        bankroll_mgr = BankrollManager(BANKROLL_BASE)
        kelly = bankroll_mgr.calculate_kelly_size(american_odds, total_prob)
        bet_size = bankroll_mgr.calculate_bet_size(kelly) * 0.5  # Conservative for parlays

        return {
            "legs": len(bets),
            "selections": selections,
            "combined_odds": american_odds,
            "implied_probability": total_prob,
            "expected_value": expected_value,
            "kelly_fraction": kelly,
            "suggested_bet_size": bet_size,
            "confidence_tier": min(bet.confidence for bet in bets),  # Weakest link
        }


class TelegramAlerter:
    """EQ12 Telegram integration for bet alerts"""

    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None
        self.chat_id = TELEGRAM_CHAT_ID

    async def send_edge_alert(self, edge_bet: EdgeBet):
        """Send individual edge bet alert"""
        if not self.bot:
            logger.warning("Telegram bot not configured")
            return

        message = f"""
🎯 **EDGE DETECTED** - {edge_bet.confidence}

🏆 **{edge_bet.sport}**
📊 **Market**: {edge_bet.market}
🎲 **Selection**: {edge_bet.selection}
🏪 **Book**: {edge_bet.book}

💰 **Odds**: {edge_bet.odds:+.0f}
📈 **Edge**: {edge_bet.edge:.1%}
💵 **Suggested Bet**: ${edge_bet.bet_size:.2f}
🧮 **Kelly**: {edge_bet.kelly_fraction:.1%}

⚡️ **Fair Prob**: {edge_bet.fair_prob:.1%}
📉 **Implied Prob**: {edge_bet.implied_prob:.1%}
"""

        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    async def send_parlay_alert(self, parlay: dict[str, Any]):
        """Send parlay construction alert"""
        if not self.bot:
            return

        selections_text = "\n".join(
            [
                f"• {sel['selection']} ({sel['odds']:+.0f}) - {sel['confidence']}"
                for sel in parlay["selections"]
            ]
        )

        message = f"""
🎰 **PARLAY CONSTRUCTED** - {parlay['confidence_tier']}

🔢 **{parlay['legs']} Legs**
💰 **Combined Odds**: {parlay['combined_odds']:+.0f}
📈 **Expected Value**: {parlay['expected_value']:.1%}
💵 **Suggested Bet**: ${parlay['suggested_bet_size']:.2f}

**Selections:**
{selections_text}

⚡️ **Win Probability**: {parlay['implied_probability']:.1%}
🧮 **Kelly**: {parlay['kelly_fraction']:.1%}
"""

        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Failed to send parlay alert: {e}")


# Enhanced Utilities
def now_utc():
    return datetime.now(UTC)


def to_iso(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_ny(dt_iso: str) -> str:
    dt = datetime.fromisoformat(dt_iso.replace("Z", "+00:00"))
    return dt.astimezone(NY_TZ).strftime("%Y-%m-%d %H:%M")


def american_to_implied(american: float) -> float:
    if american > 0:
        return 100.0 / (american + 100.0)
    return (-american) / ((-american) + 100.0)


def decimal_to_implied(decimal_odds: float) -> float:
    return 1.0 / decimal_odds if decimal_odds > 0 else float("nan")


def calculate_consensus_fair_value(prices: list[float], format: str = "american") -> float:
    """Calculate consensus fair value from multiple bookmaker prices"""
    if not prices:
        return 0.0

    implied_probs = []
    for price in prices:
        if format == "american":
            implied_probs.append(american_to_implied(price))
        else:
            implied_probs.append(decimal_to_implied(price))

    # Remove vig using multiplicative method
    total_implied = sum(implied_probs)
    if total_implied > 1.0:
        fair_probs = [p / total_implied for p in implied_probs]
        return np.mean(fair_probs)

    return np.mean(implied_probs)


# HTTP Client
client = httpx.AsyncClient(timeout=15.0)


async def get_in_season_sports() -> list[dict[str, Any]]:
    """Get in-season sports with EdgeGod API management"""
    try:
        # Use EdgeGod API manager with intelligent caching
        response = await make_api_call_with_management("sports", {"all": "false"})
        return response if isinstance(response, list) else []
    except Exception as e:
        logger.error(f"Failed to fetch sports: {e}")
        return []


async def get_events(sport_key: str, start_iso: str, end_iso: str) -> list[dict[str, Any]]:
    """Get events with EdgeGod API management and intelligent caching"""
    params = {
        "commenceTimeFrom": start_iso,
        "commenceTimeTo": end_iso,
        "dateFormat": "iso",
    }

    try:
        response = await make_api_call_with_management(f"sports/{sport_key}/events", params)
        return response if isinstance(response, list) else []
    except Exception as e:
        logger.error(f"Failed to fetch events for {sport_key}: {e}")
        return []


async def get_odds_for_events(
    sport_key: str,
    event_ids: list[str],
    markets: str = "h2h,spreads,totals,batter_home_runs,batter_total_bases,batter_hits",
    regions: str = "us",
    odds_format: str = "american",
) -> list[dict[str, Any]]:
    """Get odds for events with EdgeGod API management and intelligent batching"""
    if not event_ids:
        return []

    # Use EdgeGod API manager's built-in batching for optimal performance
    params = {
        "regions": regions,
        "markets": markets,
        "oddsFormat": odds_format,
        "dateFormat": "iso",
    }

    try:
        # EdgeGod API manager handles batching, caching, and rate limiting
        response = await make_api_call_with_management(
            f"sports/{sport_key}/odds", {**params, "eventIds": ",".join(event_ids)}
        )
        return response if isinstance(response, list) else []
    except Exception as e:
        logger.error(f"Failed to fetch odds for {sport_key} events: {e}")
        return []


# Expert Analysis Engine
class EdgeGodExpertEngine:
    """Main expert analysis engine combining all components"""

    def __init__(self):
        self.bankroll_manager = BankrollManager(BANKROLL_BASE)
        self.mlb_analyzer = MLBExpertAnalyzer()
        self.parlay_constructor = ParlayConstructor()
        self.telegram_alerter = TelegramAlerter()

    async def analyze_full_slate(self, window: str = "today") -> dict[str, Any]:
        """Comprehensive slate analysis with all expert features"""

        # Get in-season sports
        sports = await get_in_season_sports()

        # Calculate time window
        start_iso, end_iso = self._calculate_time_window(window)

        all_edge_bets = []
        analysis_results = {
            "window": window,
            "sports_analyzed": [],
            "edge_bets": [],
            "parlays": [],
            "summary": {},
        }

        for sport in sports:
            sport_key = sport["key"]
            sport_title = sport.get("title", sport_key)

            logger.info(f"Analyzing {sport_title}...")

            # Get events in window
            events = await get_events(sport_key, start_iso, end_iso)

            if not events:
                continue

            # Filter by discipline window
            filtered_events = [
                e for e in events if self._is_within_disciplined_window(e["commence_time"])
            ]

            if not filtered_events:
                continue

            # Get odds for filtered events
            odds_events = await get_odds_for_events(sport_key, [e["id"] for e in filtered_events])

            # Analyze for edge bets
            sport_edge_bets = []

            for odds_event in odds_events:
                # Standard market analysis
                standard_edges = await self._analyze_standard_markets(odds_event)
                sport_edge_bets.extend(standard_edges)

                # MLB-specific analysis
                if sport_key == "baseball_mlb":
                    mlb_edges = await self.mlb_analyzer.analyze_mlb_props(odds_event)
                    sport_edge_bets.extend(mlb_edges)

            all_edge_bets.extend(sport_edge_bets)

            if sport_edge_bets:
                analysis_results["sports_analyzed"].append(
                    {
                        "sport": sport_title,
                        "events_analyzed": len(odds_events),
                        "edge_bets_found": len(sport_edge_bets),
                    }
                )

        # Filter for quality edge bets
        quality_edges = [bet for bet in all_edge_bets if bet.edge >= MIN_EDGE_THRESHOLD]

        # Send individual alerts for LOCK and STRONG bets
        for edge_bet in quality_edges:
            if edge_bet.confidence in ["LOCK", "STRONG"]:
                await self.telegram_alerter.send_edge_alert(edge_bet)

        # Construct parlays
        parlays = self.parlay_constructor.build_optimal_parlays(quality_edges)

        # Send parlay alerts for top parlays
        for parlay in parlays[:3]:  # Top 3 parlays
            if parlay["confidence_tier"] in ["LOCK", "STRONG"]:
                await self.telegram_alerter.send_parlay_alert(parlay)

        # Compile results
        analysis_results["edge_bets"] = [self._edge_bet_to_dict(bet) for bet in quality_edges]
        analysis_results["parlays"] = parlays
        analysis_results["summary"] = {
            "total_sports": len(sports),
            "sports_with_edges": len(analysis_results["sports_analyzed"]),
            "total_edge_bets": len(quality_edges),
            "lock_bets": len([b for b in quality_edges if b.confidence == "LOCK"]),
            "strong_bets": len([b for b in quality_edges if b.confidence == "STRONG"]),
            "total_parlays": len(parlays),
            "bankroll_allocated": sum(bet.bet_size for bet in quality_edges),
            "expected_return": sum(bet.bet_size * bet.edge for bet in quality_edges),
        }

        # Log analysis to EQ12 logs
        await self._log_analysis(analysis_results)

        return analysis_results

    def _calculate_time_window(self, window: str) -> tuple[str, str]:
        """Calculate start and end ISO timestamps for window"""
        ny_now = datetime.now(NY_TZ)

        if window == "today":
            start_ny = ny_now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_ny = start_ny + timedelta(days=1)
        elif window == "tonight":
            start_ny = ny_now.replace(hour=17, minute=0, second=0, microsecond=0)
            end_ny = ny_now.replace(hour=23, minute=59, second=59, microsecond=0)
            if ny_now > end_ny:
                end_ny = ny_now + timedelta(hours=6)
        else:  # "24h"
            start_ny = ny_now
            end_ny = ny_now + timedelta(hours=24)

        start_iso = to_iso(start_ny.astimezone(UTC))
        end_iso = to_iso(end_ny.astimezone(UTC))

        return start_iso, end_iso

    def _is_within_disciplined_window(
        self, commence_iso: str, min_minutes_ahead: int = 20, max_days_ahead: int = 3
    ) -> bool:
        """Check if event is within disciplined betting window"""
        now = now_utc()
        start = datetime.fromisoformat(commence_iso.replace("Z", "+00:00"))
        delta = start - now
        return delta.total_seconds() >= min_minutes_ahead * 60 and delta <= timedelta(
            days=max_days_ahead
        )

    async def _analyze_standard_markets(self, event: dict[str, Any]) -> list[EdgeBet]:
        """Analyze standard H2H, spread, and total markets"""
        edge_bets = []

        for bookmaker in event.get("bookmakers", []):
            for market in bookmaker.get("markets", []):
                market_key = market.get("key", "")

                if market_key in ["h2h", "spreads", "totals"]:
                    # Collect all prices for consensus calculation
                    all_prices = {}

                    for outcome in market.get("outcomes", []):
                        name = outcome.get("name", "")
                        price = outcome.get("price", 0)

                        if name not in all_prices:
                            all_prices[name] = []
                        all_prices[name].append(price)

                    # Calculate consensus and find edges
                    for outcome in market.get("outcomes", []):
                        name = outcome.get("name", "")
                        price = outcome.get("price", 0)

                        # Calculate consensus fair value
                        fair_prob = calculate_consensus_fair_value(all_prices[name])

                        if fair_prob > 0:
                            implied_prob = american_to_implied(price)
                            edge = fair_prob - implied_prob

                            if edge >= MIN_EDGE_THRESHOLD:
                                kelly = self.bankroll_manager.calculate_kelly_size(price, fair_prob)
                                bet_size = self.bankroll_manager.calculate_bet_size(kelly)
                                confidence = self.bankroll_manager.classify_confidence(edge, kelly)

                                edge_bet = EdgeBet(
                                    event_id=event["id"],
                                    sport=event.get("sport_title", "Unknown"),
                                    market=market_key,
                                    selection=f"{name}"
                                    + (
                                        f" ({outcome.get('point', '')})"
                                        if outcome.get("point")
                                        else ""
                                    ),
                                    book=bookmaker["title"],
                                    odds=price,
                                    implied_prob=implied_prob,
                                    fair_prob=fair_prob,
                                    edge=edge,
                                    kelly_fraction=kelly,
                                    bet_size=bet_size,
                                    confidence=confidence,
                                )
                                edge_bets.append(edge_bet)

        return edge_bets

    def _edge_bet_to_dict(self, bet: EdgeBet) -> dict[str, Any]:
        """Convert EdgeBet to dictionary for JSON serialization"""
        return {
            "event_id": bet.event_id,
            "sport": bet.sport,
            "market": bet.market,
            "selection": bet.selection,
            "book": bet.book,
            "odds": bet.odds,
            "implied_prob": bet.implied_prob,
            "fair_prob": bet.fair_prob,
            "edge": bet.edge,
            "kelly_fraction": bet.kelly_fraction,
            "bet_size": bet.bet_size,
            "confidence": bet.confidence,
        }

    async def _log_analysis(self, results: dict[str, Any]):
        """Log analysis results to EQ12 logs directory"""
        os.makedirs(EQ12_LOGS, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = Path(EQ12_LOGS) / f"edgegod_analysis_{timestamp}.json"

        async with aiofiles.open(log_file, "w") as f:
            await f.write(json.dumps(results, indent=2, default=str))

        logger.info(f"Analysis logged to {log_file}")


# FastAPI Application
app = FastAPI(
    title="EQ12 EdgeGod Expert Odds Engine",
    version="2.1.0",
    description="Expert-grade odds analysis with comprehensive API rate limiting and 429 error prevention",
)


# @app.on_event("startup")  # Deprecated - use lifespan events
async def startup_event():
    """Initialize API manager on startup"""
    await initialize_api_manager()
    logger.info("EdgeGod Expert Engine startup complete with API rate limiting")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup API manager on shutdown"""
    await close_api_manager()
    logger.info("EdgeGod Expert Engine shutdown complete")


# Initialize expert engine
expert_engine = EdgeGodExpertEngine()


# API Models
class SlateItem(BaseModel):
    event_id: str
    sport: str
    away_team: str
    home_team: str
    commence_time_ny: str
    edge_bets: list[dict[str, Any]]


class AnalysisResponse(BaseModel):
    window: str
    sports_analyzed: list[dict[str, Any]]
    edge_bets: list[dict[str, Any]]
    parlays: list[dict[str, Any]]
    summary: dict[str, Any]


@app.get("/slate", response_model=list[SlateItem])
async def get_slate(
    window: str = Query("today", enum=["today", "tonight", "24h"]),
    regions: str = "us",
    odds_format: str = "american",
):
    """Get bettable slate with edge analysis"""
    analysis = await expert_engine.analyze_full_slate(window)

    # Convert to slate format
    slate_items = []
    event_edges = {}

    # Group edge bets by event
    for edge_bet in analysis["edge_bets"]:
        event_id = edge_bet["event_id"]
        if event_id not in event_edges:
            event_edges[event_id] = []
        event_edges[event_id].append(edge_bet)

    # Get event details for slate items
    sports = await get_in_season_sports()
    start_iso, end_iso = expert_engine._calculate_time_window(window)

    for sport in sports:
        events = await get_events(sport["key"], start_iso, end_iso)

        for event in events:
            if event["id"] in event_edges:
                slate_items.append(
                    SlateItem(
                        event_id=event["id"],
                        sport=event.get("sport_title", sport["key"]),
                        away_team=event["away_team"],
                        home_team=event["home_team"],
                        commence_time_ny=to_ny(event["commence_time"]),
                        edge_bets=event_edges[event["id"]],
                    )
                )

    return slate_items


@app.get("/analysis", response_model=AnalysisResponse)
async def get_full_analysis(
    window: str = Query("today", enum=["today", "tonight", "24h"]),
    background_tasks: BackgroundTasks = None,
):
    """Get comprehensive expert analysis"""
    return await expert_engine.analyze_full_slate(window)


@app.post("/analyze")
async def trigger_analysis(
    window: str = Query("today", enum=["today", "tonight", "24h"]),
    background_tasks: BackgroundTasks = None,
):
    """Trigger background analysis with alerts"""
    if background_tasks:
        background_tasks.add_task(expert_engine.analyze_full_slate, window)
        return {"status": "Analysis triggered", "window": window}
    analysis = await expert_engine.analyze_full_slate(window)
    return {"status": "Analysis complete", "summary": analysis["summary"]}


@app.get("/bankroll")
async def get_bankroll_status():
    """Get current bankroll management status"""
    return {
        "base_bankroll": expert_engine.bankroll_manager.base_bankroll,
        "current_bankroll": expert_engine.bankroll_manager.current_bankroll,
        "max_bet_percentage": expert_engine.bankroll_manager.max_bet_percentage,
        "min_edge_threshold": expert_engine.bankroll_manager.min_edge,
    }


@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
