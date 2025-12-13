#!/usr/bin/env python3
"""
EQ12 API Client Framework
=========================

Comprehensive API client following the tight runbook specifications:
- Scoped to DraftKings, FanDuel, BetMGM only
- Proper timezone handling (UTC-aware)
- All query types from ingest to settlement
- Built for production with error handling and rate limiting
"""

import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class BookMaker(Enum):
    """Supported bookmakers (DK/FD/BetMGM only)"""

    DRAFTKINGS = "draftkings"
    FANDUEL = "fanduel"
    BETMGM = "betmgm"


class Market(Enum):
    """Core betting markets"""

    H2H = "h2h"  # Moneyline
    SPREADS = "spreads"
    TOTALS = "totals"


class RiskLevel(Enum):
    """Parlay risk levels"""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    YOLO = "yolo"


@dataclass
class GameData:
    """Structured game data with timezone-aware timestamps"""

    id: str
    home_team: str
    away_team: str
    commence_time: datetime
    bookmakers: list[dict]

    def __post_init__(self):
        """Ensure commence_time is UTC-aware"""
        if self.commence_time.tzinfo is None:
            # Assume UTC if naive
            self.commence_time = self.commence_time.replace(tzinfo=UTC)


@dataclass
class Opportunity:
    """Betting opportunity with EV calculation"""

    game_id: str
    book: BookMaker
    market: Market
    selection: str
    team: str
    price: int  # American odds
    point: float | None = None  # For spreads/totals
    implied_prob: float = 0.0
    model_prob: float = 0.0
    edge_percent: float = 0.0
    kelly_fraction: float = 0.0
    last_update: datetime | None = None

    def calculate_edge(self, model_probability: float) -> None:
        """Calculate edge and Kelly fraction"""
        self.model_prob = model_probability
        self.implied_prob = self._american_to_probability(self.price)
        self.edge_percent = ((self.model_prob - self.implied_prob) / self.implied_prob) * 100
        self.kelly_fraction = self._kelly_criterion(self.price, self.model_prob)

    @staticmethod
    def _american_to_probability(american_odds: int) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)

    @staticmethod
    def _kelly_criterion(american_odds: int, model_prob: float) -> float:
        """Calculate Kelly fraction with caps"""
        if american_odds > 0:
            decimal_odds = (american_odds / 100) + 1
        else:
            decimal_odds = (100 / abs(american_odds)) + 1

        kelly = (model_prob * decimal_odds - 1) / (decimal_odds - 1)

        # Apply caps per market type
        return max(0, min(kelly, 0.05))  # Max 5% of bankroll


class EQ12APIClient:
    """
    Production-ready API client for The Odds API
    Implements the complete EQ12 runbook with proper error handling
    """

    BASE_URL = "https://api.the-odds-api.com/v4"
    SPORT = "americanfootball_nfl"

    # Key numbers for hooks (spreads and totals)
    SPREAD_HOOKS = [
        -10.5,
        -9.5,
        -7.5,
        -6.5,
        -3.5,
        -2.5,
        -1.5,
        -0.5,
        0.5,
        1.5,
        2.5,
        3.5,
        6.5,
        7.5,
        9.5,
        10.5,
    ]
    TOTAL_HOOKS = [
        37.5,
        38.5,
        39.5,
        40.5,
        41.5,
        42.5,
        43.5,
        44.5,
        45.5,
        46.5,
        47.5,
        48.5,
        49.5,
        50.5,
        51.5,
        52.5,
    ]

    def __init__(self, api_key: str):
        """Initialize with API key and configure session"""
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Track API usage
        self.requests_made = 0
        self.last_reset = datetime.now(UTC)

    # =============================================================================
    # INGEST & HEALTH (PRE-FLIGHT)
    # =============================================================================

    def heartbeat(self) -> dict:
        """API heartbeat / quota check"""
        try:
            # Lightweight ping
            response = self._make_request("/sports")
            self.logger.info("✅ API heartbeat successful")

            # Quick odds check with minimal data
            odds_check = self._make_request(
                f"/sports/{self.SPORT}/odds",
                params={"bookmakers": "draftkings", "markets": "h2h", "limit": 1},
            )

            return {
                "status": "healthy",
                "sports_count": len(response),
                "nfl_games_available": len(odds_check),
                "requests_remaining": self._get_requests_remaining(),
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"❌ API heartbeat failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
            }

    def clock_sanity_check(self) -> dict:
        """Verify timezone handling and clock accuracy"""
        now_utc = datetime.now(UTC)

        try:
            # Get a sample game to check commence_time parsing
            response = self._make_request(
                f"/sports/{self.SPORT}/odds",
                params={
                    "bookmakers": "draftkings",
                    "markets": "h2h",
                    "limit": 1,
                    "dateFormat": "iso",
                },
            )

            if response:
                game = response[0]
                commence_time_str = game.get("commence_time")
                if commence_time_str:
                    # Parse and ensure UTC awareness
                    commence_time = datetime.fromisoformat(commence_time_str.replace("Z", "+00:00"))
                    time_diff = (commence_time - now_utc).total_seconds() / 3600  # Hours

                    return {
                        "status": "ok",
                        "server_time_utc": now_utc.isoformat(),
                        "sample_game_time": commence_time.isoformat(),
                        "hours_until_game": round(time_diff, 2),
                        "timezone_aware": commence_time.tzinfo is not None,
                    }

            return {"status": "no_games_found"}

        except Exception as e:
            self.logger.error(f"❌ Clock sanity check failed: {e}")
            return {"status": "error", "error": str(e)}

    def book_availability_snapshot(self) -> dict:
        """Check book availability across all core markets"""
        books = [b.value for b in BookMaker]
        markets = [m.value for m in Market]

        try:
            response = self._make_request(
                f"/sports/{self.SPORT}/odds",
                params={
                    "regions": "us",
                    "bookmakers": ",".join(books),
                    "markets": ",".join(markets),
                    "oddsFormat": "american",
                    "dateFormat": "iso",
                },
            )

            # Analyze availability
            book_stats = {
                book: {"games": 0, "markets": dict.fromkeys(markets, 0)} for book in books
            }

            for game in response:
                available_books = set()
                for bookmaker in game.get("bookmakers", []):
                    book_key = bookmaker.get("key")
                    if book_key in books:
                        available_books.add(book_key)
                        book_stats[book_key]["games"] += 1

                        for market in bookmaker.get("markets", []):
                            market_key = market.get("key")
                            if market_key in markets:
                                book_stats[book_key]["markets"][market_key] += 1

            return {
                "status": "complete",
                "total_games": len(response),
                "book_statistics": book_stats,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"❌ Book availability check failed: {e}")
            return {"status": "error", "error": str(e)}

    # =============================================================================
    # CORE MARKET PULLS (GAME ODDS)
    # =============================================================================

    def get_24h_slate(self) -> list[GameData]:
        """Get today + next 24h slate with timezone filtering"""
        now_utc = datetime.now(UTC)
        cutoff_time = now_utc + timedelta(hours=24)

        try:
            response = self._make_request(
                f"/sports/{self.SPORT}/odds",
                params={
                    "regions": "us",
                    "bookmakers": ",".join([b.value for b in BookMaker]),
                    "markets": ",".join([m.value for m in Market]),
                    "oddsFormat": "american",
                    "dateFormat": "iso",
                },
            )

            games = []
            for game_data in response:
                commence_time = datetime.fromisoformat(
                    game_data["commence_time"].replace("Z", "+00:00")
                )

                # Filter to 24h window
                if now_utc <= commence_time <= cutoff_time:
                    game = GameData(
                        id=game_data["id"],
                        home_team=game_data["home_team"],
                        away_team=game_data["away_team"],
                        commence_time=commence_time,
                        bookmakers=game_data.get("bookmakers", []),
                    )
                    games.append(game)

            self.logger.info(f"📅 Found {len(games)} games in next 24h")
            return games

        except Exception as e:
            self.logger.error(f"❌ Failed to get 24h slate: {e}")
            return []

    def get_steaming_window(self) -> list[GameData]:
        """Get games in last-minute/steaming window (≤60m to kickoff)"""
        now_utc = datetime.now(UTC)
        steam_window = now_utc + timedelta(minutes=60)

        games_24h = self.get_24h_slate()
        steaming_games = [game for game in games_24h if game.commence_time <= steam_window]

        self.logger.info(f"🔥 Found {len(steaming_games)} games in steaming window")
        return steaming_games

    def poll_for_updates(self, previous_data: dict) -> dict:
        """Poll for line movement updates"""
        current_data = {}
        movements = []

        try:
            response = self._make_request(
                f"/sports/{self.SPORT}/odds",
                params={
                    "regions": "us",
                    "bookmakers": ",".join([b.value for b in BookMaker]),
                    "markets": ",".join([m.value for m in Market]),
                    "oddsFormat": "american",
                    "dateFormat": "iso",
                },
            )

            # Build current data structure
            for game in response:
                game_id = game["id"]
                current_data[game_id] = {}

                for bookmaker in game.get("bookmakers", []):
                    book_key = bookmaker["key"]
                    last_update = datetime.fromisoformat(
                        bookmaker["last_update"].replace("Z", "+00:00")
                    )

                    current_data[game_id][book_key] = {
                        "last_update": last_update,
                        "markets": {},
                    }

                    for market in bookmaker.get("markets", []):
                        market_key = market["key"]
                        current_data[game_id][book_key]["markets"][market_key] = market["outcomes"]

            # Compare with previous data for movements
            if previous_data:
                movements = self._detect_movements(previous_data, current_data)

            return {
                "current_data": current_data,
                "movements": movements,
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to poll for updates: {e}")
            return {"error": str(e)}

    # =============================================================================
    # TARGETED MARKET PULLS (VALUE HUNTING)
    # =============================================================================

    def get_moneylines_only(self) -> list[Opportunity]:
        """Pull moneylines only for all games"""
        return self._get_market_opportunities(Market.H2H)

    def get_spreads_with_hooks(self) -> list[Opportunity]:
        """Pull spreads focusing on key numbers (hooks)"""
        opportunities = self._get_market_opportunities(Market.SPREADS)

        # Filter for hook numbers
        hook_opportunities = []
        for opp in opportunities:
            if opp.point is not None and opp.point in self.SPREAD_HOOKS:
                hook_opportunities.append(opp)

        self.logger.info(
            f"🎣 Found {len(hook_opportunities)} spread hooks out of {len(opportunities)} total"
        )
        return hook_opportunities

    def get_totals_with_hooks(self) -> list[Opportunity]:
        """Pull totals focusing on key numbers"""
        opportunities = self._get_market_opportunities(Market.TOTALS)

        # Filter for hook numbers
        hook_opportunities = []
        for opp in opportunities:
            if opp.point is not None and opp.point in self.TOTAL_HOOKS:
                hook_opportunities.append(opp)

        self.logger.info(
            f"🎣 Found {len(hook_opportunities)} total hooks out of {len(opportunities)} total"
        )
        return hook_opportunities

    def get_alternate_lines(self, market: Market) -> list[Opportunity]:
        """Get all available lines for a market (for alternate line scanning)"""
        return self._get_market_opportunities(market)

    # =============================================================================
    # MODELING & EDGE COMPUTATION
    # =============================================================================

    def calculate_edges(
        self, opportunities: list[Opportunity], model_probabilities: dict[str, float]
    ) -> list[Opportunity]:
        """Calculate edges using model probabilities"""
        opportunities_with_edges = []

        for opp in opportunities:
            # Create unique key for this opportunity
            opp_key = f"{opp.game_id}_{opp.market.value}_{opp.selection}_{opp.point}"

            if opp_key in model_probabilities:
                opp.calculate_edge(model_probabilities[opp_key])
                opportunities_with_edges.append(opp)

        return opportunities_with_edges

    def filter_minimum_ev(
        self, opportunities: list[Opportunity], min_ev_percent: float = 2.0
    ) -> list[Opportunity]:
        """Filter opportunities by minimum EV threshold"""
        filtered = [opp for opp in opportunities if opp.edge_percent >= min_ev_percent]

        self.logger.info(f"📊 {len(filtered)} opportunities above {min_ev_percent}% EV threshold")
        return filtered

    def select_best_books(self, opportunities: list[Opportunity]) -> dict[str, Opportunity]:
        """Select best book for each unique opportunity"""
        best_opportunities = {}

        # Group by (game, market, selection, point)
        for opp in opportunities:
            key = f"{opp.game_id}_{opp.market.value}_{opp.selection}_{opp.point}"

            if (
                key not in best_opportunities
                or opp.edge_percent > best_opportunities[key].edge_percent
            ):
                best_opportunities[key] = opp

        return best_opportunities

    def detect_conflicts(self, opportunities: list[Opportunity]) -> list[Opportunity]:
        """Remove conflicting legs (same game, opposite sides)"""
        game_selections = {}
        clean_opportunities = []

        for opp in opportunities:
            game_id = opp.game_id

            if game_id not in game_selections:
                game_selections[game_id] = []
                clean_opportunities.append(opp)
            else:
                # Check for conflicts (simplified - would need more sophisticated logic)
                has_conflict = False
                for existing in game_selections[game_id]:
                    if self._is_conflicting(opp, existing):
                        has_conflict = True
                        break

                if not has_conflict:
                    clean_opportunities.append(opp)

            game_selections[game_id].append(opp)

        conflicts_removed = len(opportunities) - len(clean_opportunities)
        if conflicts_removed > 0:
            self.logger.info(f"🚫 Removed {conflicts_removed} conflicting opportunities")

        return clean_opportunities

    # =============================================================================
    # PARLAY BUILDERS (BOOK-SPECIFIC)
    # =============================================================================

    def build_max_legs_parlay(self, book: BookMaker, max_legs: int = 12) -> dict:
        """Build maximum legs YOLO parlay for specific book"""
        opportunities = self._get_book_opportunities(book)
        opportunities = self.detect_conflicts(opportunities)

        # Sort by EV and take top N
        top_opportunities = sorted(opportunities, key=lambda x: x.edge_percent, reverse=True)[
            :max_legs
        ]

        return self._create_parlay_structure(top_opportunities, RiskLevel.YOLO, book)

    def build_balanced_risk_parlay(self, book: BookMaker) -> dict:
        """Build balanced risk parlay with mix of markets"""
        opportunities = self._get_book_opportunities(book)
        opportunities = [
            opp for opp in opportunities if opp.edge_percent >= 3.0
        ]  # Medium threshold

        # Balance across markets
        balanced_opportunities = self._balance_markets(opportunities)

        return self._create_parlay_structure(balanced_opportunities, RiskLevel.BALANCED, book)

    def build_conservative_high_ev_parlay(self, book: BookMaker) -> dict:
        """Build conservative parlay with only high EV picks"""
        opportunities = self._get_book_opportunities(book)
        high_ev_opportunities = [opp for opp in opportunities if opp.edge_percent >= 6.0]

        # Prefer hook spreads/totals for conservative approach
        hook_preferred = []
        for opp in high_ev_opportunities:
            if opp.market in [Market.SPREADS, Market.TOTALS]:
                if opp.point in (
                    self.SPREAD_HOOKS if opp.market == Market.SPREADS else self.TOTAL_HOOKS
                ):
                    hook_preferred.append(opp)
            else:
                hook_preferred.append(opp)

        return self._create_parlay_structure(hook_preferred, RiskLevel.CONSERVATIVE, book)

    def build_spreads_only_parlay(self, book: BookMaker) -> dict:
        """Build spreads-only parlay focusing on hooks"""
        spread_opportunities = [
            opp for opp in self._get_book_opportunities(book) if opp.market == Market.SPREADS
        ]

        # Focus on key numbers
        hook_spreads = [opp for opp in spread_opportunities if opp.point in self.SPREAD_HOOKS]

        return self._create_parlay_structure(hook_spreads, RiskLevel.BALANCED, book)

    def build_totals_only_parlay(self, book: BookMaker) -> dict:
        """Build totals-only parlay with hooks"""
        total_opportunities = [
            opp for opp in self._get_book_opportunities(book) if opp.market == Market.TOTALS
        ]

        # Focus on key numbers
        hook_totals = [opp for opp in total_opportunities if opp.point in self.TOTAL_HOOKS]

        return self._create_parlay_structure(hook_totals, RiskLevel.BALANCED, book)

    def build_close_games_parlay(self, book: BookMaker) -> dict:
        """Build parlay for close games (|spread| ≤ 3.0, price ≥ -120)"""
        spread_opportunities = [
            opp for opp in self._get_book_opportunities(book) if opp.market == Market.SPREADS
        ]

        close_games = [
            opp for opp in spread_opportunities if abs(opp.point or 0) <= 3.0 and opp.price >= -120
        ]

        return self._create_parlay_structure(close_games, RiskLevel.CONSERVATIVE, book)

    # =============================================================================
    # RESULTS & SETTLEMENT
    # =============================================================================

    def get_scores_for_settlement(self, days_back: int = 2) -> dict:
        """Get scores/finals for settlement"""
        try:
            response = self._make_request(
                f"/sports/{self.SPORT}/scores",
                params={"daysFrom": days_back, "dateFormat": "iso"},
            )

            return {
                "scores": response,
                "games_count": len(response),
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to get scores: {e}")
            return {"error": str(e)}

    # =============================================================================
    # HELPER METHODS
    # =============================================================================

    def _make_request(self, endpoint: str, params: dict | None = None) -> Any:
        """Make API request with error handling and rate limiting"""
        url = f"{self.BASE_URL}{endpoint}"

        if params is None:
            params = {}

        params["apiKey"] = self.api_key

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            self.requests_made += 1
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {url} - {e}")
            raise

    def _get_requests_remaining(self) -> int | None:
        """Get remaining API requests (if available in headers)"""
        # This would need to be implemented based on The Odds API's rate limiting headers
        return None

    def _get_market_opportunities(self, market: Market) -> list[Opportunity]:
        """Get opportunities for a specific market"""
        opportunities = []

        try:
            response = self._make_request(
                f"/sports/{self.SPORT}/odds",
                params={
                    "regions": "us",
                    "bookmakers": ",".join([b.value for b in BookMaker]),
                    "markets": market.value,
                    "oddsFormat": "american",
                    "dateFormat": "iso",
                },
            )

            for game in response:
                for bookmaker in game.get("bookmakers", []):
                    book_key = bookmaker["key"]
                    if book_key not in [b.value for b in BookMaker]:
                        continue

                    book = BookMaker(book_key)

                    for market_data in bookmaker.get("markets", []):
                        if market_data["key"] == market.value:
                            for outcome in market_data.get("outcomes", []):
                                opp = Opportunity(
                                    game_id=game["id"],
                                    book=book,
                                    market=market,
                                    selection=outcome["name"],
                                    team=outcome["name"],
                                    price=outcome["price"],
                                    point=outcome.get("point"),
                                    last_update=datetime.fromisoformat(
                                        bookmaker["last_update"].replace("Z", "+00:00")
                                    ),
                                )
                                opportunities.append(opp)

        except Exception as e:
            self.logger.error(f"❌ Failed to get {market.value} opportunities: {e}")

        return opportunities

    def _get_book_opportunities(self, book: BookMaker) -> list[Opportunity]:
        """Get all opportunities for a specific book"""
        all_opportunities = []

        for market in Market:
            market_opportunities = self._get_market_opportunities(market)
            book_opportunities = [opp for opp in market_opportunities if opp.book == book]
            all_opportunities.extend(book_opportunities)

        return all_opportunities

    def _detect_movements(self, previous: dict, current: dict) -> list[dict]:
        """Detect line movements between polls"""
        movements = []

        # Implementation would compare price/point changes
        # This is a placeholder for the actual movement detection logic

        return movements

    def _is_conflicting(self, opp1: Opportunity, opp2: Opportunity) -> bool:
        """Check if two opportunities conflict (simplified logic)"""
        if opp1.market == opp2.market == Market.H2H:
            # Both teams in same game
            return True

        if opp1.market == opp2.market == Market.TOTALS:
            # Over/Under in same game
            return "Over" in opp1.selection and "Under" in opp2.selection

        # More sophisticated conflict detection would be needed for real use
        return False

    def _balance_markets(self, opportunities: list[Opportunity]) -> list[Opportunity]:
        """Balance opportunities across different markets"""
        market_counts = dict.fromkeys(Market, 0)
        balanced = []

        # Sort by EV
        sorted_opportunities = sorted(opportunities, key=lambda x: x.edge_percent, reverse=True)

        for opp in sorted_opportunities:
            if market_counts[opp.market] < 4:  # Max 4 per market type
                balanced.append(opp)
                market_counts[opp.market] += 1

                if len(balanced) >= 12:  # Max parlay size
                    break

        return balanced

    def _create_parlay_structure(
        self, opportunities: list[Opportunity], risk_level: RiskLevel, book: BookMaker
    ) -> dict:
        """Create structured parlay output"""
        if not opportunities:
            return {"error": "No opportunities available"}

        # Calculate combined odds (simplified)
        combined_odds = 1.0
        for opp in opportunities:
            decimal_odds = opp.price / 100 + 1 if opp.price > 0 else 100 / abs(opp.price) + 1
            combined_odds *= decimal_odds

        american_combined = (
            int((combined_odds - 1) * 100)
            if combined_odds >= 2
            else int(-100 / (combined_odds - 1))
        )

        return {
            "book": book.value,
            "risk_level": risk_level.value,
            "legs": [asdict(opp) for opp in opportunities],
            "leg_count": len(opportunities),
            "combined_odds": american_combined,
            "decimal_odds": combined_odds,
            "total_edge_percent": sum(opp.edge_percent for opp in opportunities)
            / len(opportunities),
            "total_kelly": sum(opp.kelly_fraction for opp in opportunities),
            "timestamp": datetime.now(UTC).isoformat(),
        }


def create_client() -> EQ12APIClient:
    """Factory function to create API client with environment API key"""
    api_key = os.getenv("ODDS_API_KEY")
    if not api_key:
        raise ValueError("ODDS_API_KEY environment variable not set")

    return EQ12APIClient(api_key)


if __name__ == "__main__":
    """Test the API client"""
    try:
        client = create_client()

        # Run heartbeat
        health = client.heartbeat()
        print("🔍 API Health Check:")
        print(json.dumps(health, indent=2))

        # Clock sanity check
        clock_check = client.clock_sanity_check()
        print("\n⏰ Clock Sanity Check:")
        print(json.dumps(clock_check, indent=2))

        # Book availability
        availability = client.book_availability_snapshot()
        print("\n📚 Book Availability:")
        print(json.dumps(availability, indent=2))

        # Get 24h slate
        games = client.get_24h_slate()
        print(f"\n📅 Found {len(games)} games in next 24h")

        if games:
            # Get moneylines
            moneylines = client.get_moneylines_only()
            print(f"\n💰 Found {len(moneylines)} moneyline opportunities")

            # Build sample parlay for DraftKings
            parlay = client.build_balanced_risk_parlay(BookMaker.DRAFTKINGS)
            print("\n🎰 Sample DraftKings Parlay:")
            print(json.dumps(parlay, indent=2, default=str))

    except Exception as e:
        print(f"❌ Error: {e}")
