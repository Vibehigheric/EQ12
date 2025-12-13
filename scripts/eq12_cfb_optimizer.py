#!/usr/bin/env python3
"""
EQ12 NCAA College Football DraftKings Mystery Profit Boost Optimizer
====================================================================

This module uses OddsAPI to build the optimal DraftKings-eligible Friday CFB (FBS-only)
parlay for Mystery Profit Boost promotions. It strictly enforces all DK promo rules
and selects the parlay that maximizes expected value (EV) after applying the boost.

Features:
- Full OddsAPI integration with rate limiting and error handling
- Advanced de-vigging using multiple sportsbooks for fair probability estimation
- EV optimization with configurable boost percentages (25%, 33%, 50%)
- FBS-only filtering with comprehensive team database
- DraftKings-specific line validation and slip generation
- EQ12 backend integration for logging and analytics
- Comprehensive promo rule enforcement
- SQLite storage for historical analysis

Author: EQ12 Development Team
Version: 2.0.0
Updated: 2025-10-03
"""

from eq12_logging_config import setup_eq12_logger
import itertools
import json
import logging
import os
import sqlite3
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

# EQ12 imports
sys.path.append(str(Path(__file__).parent.parent))

# Configuration
ODDS_API_KEY = os.getenv("ODDSAPI_KEY", "YOUR_ODDSAPI_KEY_HERE")
SPORT = "americanfootball_ncaaf"
REGION = "us"
MARKETS = "h2h"  # moneyline only for clean de-vig
PROMO_DATE = "2025-10-03"  # YYYY-MM-DD (Friday promo day)
DK_BOOKMAKER_KEYWORDS = ["DraftKings", "Draft Kings", "DraftKings Sportsbook"]

# EQ12 Configuration
EQ12_DB_PATH = "C:/EQ12/eq12_bets.db"
EQ12_LOGS_DIR = "C:/EQ12/logs"

# Promo Rules
MIN_LEGS = 3
MAX_LEGS = 5
MIN_COMBINED_AMERICAN = 300  # +300 minimum
MIN_COMBINED_DECIMAL = 1 + (MIN_COMBINED_AMERICAN / 100)  # 4.0
MAX_STAKE = 100.0

# FBS Teams Database (comprehensive list to filter FCS)
FBS_TEAMS = {
    # Power 5 Conferences
    "Alabama",
    "Auburn",
    "Arkansas",
    "Florida",
    "Georgia",
    "Kentucky",
    "LSU",
    "Mississippi State",
    "Missouri",
    "Ole Miss",
    "South Carolina",
    "Tennessee",
    "Texas A&M",
    "Vanderbilt",
    "Clemson",
    "Duke",
    "Florida State",
    "Georgia Tech",
    "Louisville",
    "Miami",
    "North Carolina",
    "NC State",
    "Notre Dame",
    "Pittsburgh",
    "Syracuse",
    "Virginia",
    "Virginia Tech",
    "Wake Forest",
    "Illinois",
    "Indiana",
    "Iowa",
    "Maryland",
    "Michigan",
    "Michigan State",
    "Minnesota",
    "Nebraska",
    "Northwestern",
    "Ohio State",
    "Penn State",
    "Purdue",
    "Rutgers",
    "Wisconsin",
    "Arizona",
    "Arizona State",
    "California",
    "Colorado",
    "Oregon",
    "Oregon State",
    "Stanford",
    "UCLA",
    "USC",
    "Utah",
    "Washington",
    "Washington State",
    "Baylor",
    "Cincinnati",
    "Houston",
    "Iowa State",
    "Kansas",
    "Kansas State",
    "Oklahoma",
    "Oklahoma State",
    "TCU",
    "Texas",
    "Texas Tech",
    "UCF",
    "West Virginia",
    "BYU",
    # Group of 5 Conferences
    "Air Force",
    "Boise State",
    "Colorado State",
    "Fresno State",
    "Hawaii",
    "Nevada",
    "New Mexico",
    "San Diego State",
    "San Jose State",
    "UNLV",
    "Utah State",
    "Wyoming",
    "Akron",
    "Ball State",
    "Bowling Green",
    "Buffalo",
    "Central Michigan",
    "Eastern Michigan",
    "Kent State",
    "Miami (OH)",
    "Northern Illinois",
    "Ohio",
    "Toledo",
    "Western Michigan",
    "Charlotte",
    "East Carolina",
    "FAU",
    "FIU",
    "Marshall",
    "Middle Tennessee",
    "North Texas",
    "Old Dominion",
    "Rice",
    "Southern Miss",
    "UAB",
    "UTEP",
    "UTSA",
    "Western Kentucky",
    "Army",
    "Navy",
    "Temple",
    "Tulane",
    "Tulsa",
    "Memphis",
    "SMU",
    "South Florida",
    "Connecticut",
    "UMass",
    "Liberty",
    "New Mexico State",
    "Jacksonville State",
}


@dataclass
class CFBLeg:
    """Represents a single leg in a CFB parlay"""

    game_id: str
    home_team: str
    away_team: str
    selection_team: str
    dk_american: int
    dk_decimal: float
    fair_prob: float
    commence_time: str
    market_type: str = "moneyline"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CFBParlay:
    """Represents a complete CFB parlay with EV analysis"""

    legs: list[CFBLeg]
    legs_count: int
    combined_decimal: float
    combined_american: int
    p_win: float
    boosted_payout: float
    boosted_profit: float
    ev: float
    token_percent: int
    stake: float
    promo_date: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "legs": [leg.to_dict() for leg in self.legs]}


class CFBMysteryBoostOptimizer:
    """
    EQ12 NCAA College Football DraftKings Mystery Profit Boost Optimizer

    Finds the optimal CFB parlay for DraftKings Mystery Profit Boost promotions
    by maximizing expected value after applying boost percentages.
    """

    def __init__(
        self,
        token_percent: int = 25,
        max_bet: float = 100.0,
        promo_date: str = PROMO_DATE,
        eq12_integration: bool = True,
    ):
        """
        Initialize the CFB optimizer

        Args:
            token_percent: Boost percentage (25, 33, or 50)
            max_bet: Maximum bet amount ($100 for DK promos)
            promo_date: Promo date in YYYY-MM-DD format
            eq12_integration: Enable EQ12 backend integration
        """
        if token_percent not in [25, 33, 50]:
            raise ValueError("Token must be 25, 33, or 50 percent")

        self.token_percent = token_percent
        self.max_bet = max_bet
        self.promo_date = promo_date
        self.eq12_integration = eq12_integration

        # Set expiry to end of promo date in UTC
        self.expiry = datetime.fromisoformat(promo_date + "T23:59:59+00:00")

        # Setup logging
        self.logger = setup_eq12_logger(
            "cfb_optimizer",
            log_file=f"{EQ12_LOGS_DIR}/cfb_optimizer_{datetime.now().strftime('%Y%m%d')}.log",
        )

        # Initialize EQ12 database if enabled
        if self.eq12_integration:
            self._init_eq12_database()

        self.logger.info(
            f"CFB Optimizer initialized: {token_percent}% boost, ${max_bet} max, {promo_date}"
        )

    def _init_eq12_database(self):
        """Initialize EQ12 database tables for CFB optimization"""
        try:
            with sqlite3.connect(EQ12_DB_PATH) as conn:
                cursor = conn.cursor()

                # CFB parlays table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cfb_parlays (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        promo_date TEXT NOT NULL,
                        token_percent INTEGER NOT NULL,
                        stake REAL NOT NULL,
                        legs_count INTEGER NOT NULL,
                        combined_decimal REAL NOT NULL,
                        combined_american INTEGER NOT NULL,
                        p_win REAL NOT NULL,
                        boosted_payout REAL NOT NULL,
                        boosted_profit REAL NOT NULL,
                        ev REAL NOT NULL,
                        parlay_data TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        placed BOOLEAN DEFAULT FALSE,
                        result TEXT DEFAULT NULL,
                        actual_payout REAL DEFAULT NULL
                    )
                """
                )

                # CFB legs table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cfb_legs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        parlay_id INTEGER NOT NULL,
                        game_id TEXT NOT NULL,
                        home_team TEXT NOT NULL,
                        away_team TEXT NOT NULL,
                        selection_team TEXT NOT NULL,
                        dk_american INTEGER NOT NULL,
                        dk_decimal REAL NOT NULL,
                        fair_prob REAL NOT NULL,
                        commence_time TEXT NOT NULL,
                        market_type TEXT DEFAULT 'moneyline',
                        created_at TEXT NOT NULL,
                        result TEXT DEFAULT NULL,
                        FOREIGN KEY (parlay_id) REFERENCES cfb_parlays (id)
                    )
                """
                )

                # CFB games table for historical tracking
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cfb_games (
                        id TEXT PRIMARY KEY,
                        home_team TEXT NOT NULL,
                        away_team TEXT NOT NULL,
                        commence_time TEXT NOT NULL,
                        is_fbs BOOLEAN NOT NULL,
                        dk_home_odds INTEGER,
                        dk_away_odds INTEGER,
                        fair_home_prob REAL,
                        fair_away_prob REAL,
                        all_books_data TEXT,
                        created_at TEXT NOT NULL,
                        completed BOOLEAN DEFAULT FALSE,
                        home_score INTEGER DEFAULT NULL,
                        away_score INTEGER DEFAULT NULL
                    )
                """
                )

                conn.commit()
                self.logger.info("EQ12 CFB database tables initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize EQ12 database: {e}")
            raise

    def validate_parlay(
        self,
        legs: list[CFBLeg],
        combined_decimal: float,
        stake: float,
        use_cash: bool = True,
    ) -> tuple[bool, str]:
        """
        Validate parlay against DraftKings Mystery Profit Boost rules

        Args:
            legs: List of parlay legs
            combined_decimal: Combined decimal odds
            stake: Bet amount
            use_cash: Must use cash/DK Dollars (required for promo)

        Returns:
            Tuple of (is_valid, message)
        """
        # Check leg count
        if len(legs) < MIN_LEGS:
            return False, f"Minimum of {MIN_LEGS} legs required"

        # Check combined odds
        if combined_decimal < MIN_COMBINED_DECIMAL:
            return (
                False,
                f"Combined odds must be > = (
                    +{MIN_COMBINED_AMERICAN} (decimal {MIN_COMBINED_DECIMAL})",
                )
            )

        # Check stake
        if stake > self.max_bet:
            return False, f"Bet cannot exceed ${self.max_bet:.2f}"

        # Check payment method
        if not use_cash:
            return False, "Bet must be placed with cash or DK Dollars"

        # Check expiry
        if datetime.now(UTC) > self.expiry:
            return False, "Boost token has expired for the promo day"

        # Validate FBS teams
        for leg in legs:
            if not self._is_fbs_team(leg.home_team) or not self._is_fbs_team(leg.away_team):
                return (
                    False,
                    f"Non-FBS team detected: {leg.home_team} vs {leg.away_team}",
                )

        return True, f"Valid parlay. Boost applied: {self.token_percent}%"

    def _is_fbs_team(self, team_name: str) -> bool:
        """Check if team is FBS using comprehensive team database"""
        # Normalize team name for matching
        normalized = team_name.strip()

        # Direct match
        if normalized in FBS_TEAMS:
            return True

        # Fuzzy matching for common variations
        for fbs_team in FBS_TEAMS:
            if fbs_team.lower() in normalized.lower() or normalized.lower() in fbs_team.lower():
                return True

        # Check for FCS indicators
        fcs_indicators = ["FCS", "(FCS)", "D-II", "Division II"]
        if any(indicator in normalized for indicator in fcs_indicators):
            return False

        # Default to True if uncertain (can be manually reviewed)
        self.logger.warning(f"Team classification uncertain for: {team_name}")
        return True

    def boosted_payout_from_decimal(self, stake: float, decimal_odds: float) -> float:
        """Calculate boosted payout from decimal odds"""
        profit = stake * (decimal_odds - 1.0)
        boosted_profit = profit * (1 + self.token_percent / 100.0)
        return round(stake + boosted_profit, 2)

    def american_to_decimal(self, american: int) -> float:
        """Convert American odds to decimal odds"""
        return 1 + (100 / abs(american)) if american < 0 else 1 + (american / 100)

    def decimal_to_american(self, decimal_odds: float) -> int:
        """Convert decimal odds to American odds"""
        if decimal_odds >= 2.0:
            return int(round((decimal_odds - 1.0) * 100))
        return int(round(-100 / (decimal_odds - 1.0)))

    def fetch_ncaaf_moneylines(self, max_retries: int = 3) -> list[dict[str, Any]]:
        """
        Fetch NCAAF moneylines from OddsAPI with retry logic

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            List of game data from OddsAPI
        """
        url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds/"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": REGION,
            "markets": MARKETS,
            "dateFormat": "iso",
            "oddsFormat": "american",
        }

        for attempt in range(max_retries):
            try:
                self.logger.info(f"Fetching NCAAF odds (attempt {attempt + 1})")
                # Use rate-limited requests if available
                try:
                    from eq12_rate_limit import get_with_limit

                    response = get_with_limit(url, params=params, timeout=30)
                except ImportError:
                    response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                self.logger.info(f"Successfully fetched {len(data)} NCAAF games")

                # Store raw data for EQ12 analytics
                if self.eq12_integration:
                    self._store_raw_odds_data(data)

                return data

            except requests.exceptions.RequestException as e:
                self.logger.warning(f"OddsAPI request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                else:
                    raise

            except Exception as e:
                self.logger.error(f"Unexpected error fetching odds: {e}")
                raise

    def _store_raw_odds_data(self, data: list[dict[str, Any]]):
        """Store raw odds data in EQ12 database for analytics"""
        try:
            with sqlite3.connect(EQ12_DB_PATH) as conn:
                cursor = conn.cursor()

                for game in data:
                    dk_prices, pairs = self._extract_dk_and_allbooks_prices(game)
                    fair = self._best_fair_probs_from_books(pairs) if pairs else {}

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO cfb_games
                        (id, home_team, away_team, commence_time, is_fbs,
                         dk_home_odds, dk_away_odds, fair_home_prob, fair_away_prob,
                         all_books_data, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            game["id"],
                            game.get("home_team", ""),
                            game.get("away_team", ""),
                            game.get("commence_time", ""),
                            self._is_fbs_matchup(game),
                            (dk_prices.get(game.get("home_team", "")) if dk_prices else None),
                            (dk_prices.get(game.get("away_team", "")) if dk_prices else None),
                            fair.get(game.get("home_team", "")) if fair else None,
                            fair.get(game.get("away_team", "")) if fair else None,
                            json.dumps(
                                {
                                    "bookmakers": game.get("bookmakers", []),
                                    "pairs": pairs,
                                }
                            ),
                            datetime.now(UTC).isoformat(),
                        ),
                    )

                conn.commit()
                self.logger.info(f"Stored {len(data)} games in EQ12 database")

        except Exception as e:
            self.logger.error(f"Failed to store raw odds data: {e}")

    def is_friday_game_on_promo_date(self, game: dict[str, Any]) -> bool:
        """Check if game is on Friday promo date"""
        commence_time = game.get("commence_time", "")
        return commence_time.startswith(self.promo_date)

    def _is_fbs_matchup(self, game: dict[str, Any]) -> bool:
        """Check if both teams are FBS"""
        home = game.get("home_team", "")
        away = game.get("away_team", "")
        return self._is_fbs_team(home) and self._is_fbs_team(away)

    def _extract_dk_and_allbooks_prices(
        self, game: dict[str, Any]
    ) -> tuple[dict[str, int] | None, list[tuple]]:
        """
        Extract DraftKings prices and all books data for de-vigging

        Returns:
            Tuple of (dk_prices dict or None, list of price pairs from all books)
        """
        dk_prices = {}
        pairs = []

        for bookmaker in game.get("bookmakers", []):
            title = bookmaker.get("title", "")
            market = None

            # Find h2h market
            for m in bookmaker.get("markets", []):
                if m.get("key") == "h2h":
                    market = m
                    break

            if not market:
                continue

            outcomes = market.get("outcomes", [])
            if len(outcomes) != 2:
                continue

            team_a = outcomes[0]
            team_b = outcomes[1]

            # Check if this is DraftKings
            if any(keyword.lower() in title.lower() for keyword in DK_BOOKMAKER_KEYWORDS):
                dk_prices[team_a["name"]] = int(team_a["price"])
                dk_prices[team_b["name"]] = int(team_b["price"])

            # Store for de-vigging
            pairs.append(
                (
                    int(team_a["price"]),
                    int(team_b["price"]),
                    team_a["name"],
                    team_b["name"],
                    title,
                )
            )

        return dk_prices if dk_prices else None, pairs

    def _american_to_implied_prob(self, american: int) -> float:
        """Convert American odds to implied probability"""
        return (abs(american) / (abs(american) + 100)) if american < 0 else (100 / (american + 100))

    def _devig_two_way_pair(self, a_price: int, b_price: int) -> tuple[float | None, float | None]:
        """Remove overround from 2-way betting market"""
        pa_raw = self._american_to_implied_prob(a_price)
        pb_raw = self._american_to_implied_prob(b_price)
        total = pa_raw + pb_raw

        if total <= 0:
            return None, None

        return pa_raw / total, pb_raw / total

    def _best_fair_probs_from_books(self, pairs: list[tuple]) -> dict[str, float]:
        """Aggregate de-vigged probabilities from all available books"""
        aggregated = {}
        counts = {}

        for a_price, b_price, a_name, b_name, title in pairs:
            pa, pb = self._devig_two_way_pair(a_price, b_price)
            if pa is None:
                continue

            aggregated[a_name] = aggregated.get(a_name, 0.0) + pa
            aggregated[b_name] = aggregated.get(b_name, 0.0) + pb
            counts[a_name] = counts.get(a_name, 0) + 1
            counts[b_name] = counts.get(b_name, 0) + 1

        # Average probabilities across books
        fair_probs = {}
        for team, total_prob in aggregated.items():
            count = counts.get(team, 1)
            fair_probs[team] = total_prob / count

        return fair_probs

    def build_candidate_legs(self, games: list[dict[str, Any]]) -> list[list[CFBLeg]]:
        """
        Build candidate legs from games data

        Args:
            games: List of game data from OddsAPI

        Returns:
            List of leg options per game
        """
        legs_by_game = []

        for game in games:
            dk_prices, pairs = self._extract_dk_and_allbooks_prices(game)

            if not pairs or not dk_prices:
                continue

            fair_probs = self._best_fair_probs_from_books(pairs)

            # Create legs for each team
            game_legs = []
            for team, dk_american in dk_prices.items():
                if team not in fair_probs:
                    continue

                leg = CFBLeg(
                    game_id=game["id"],
                    home_team=game.get("home_team", ""),
                    away_team=game.get("away_team", ""),
                    selection_team=team,
                    dk_american=dk_american,
                    dk_decimal=self.american_to_decimal(dk_american),
                    fair_prob=max(min(fair_probs[team], 0.99), 0.01),  # Clamp extremes
                    commence_time=game.get("commence_time", ""),
                )
                game_legs.append(leg)

            if game_legs:
                legs_by_game.append(game_legs)

        return legs_by_game

    def _combine_decimal_odds(self, legs: list[CFBLeg]) -> float:
        """Calculate combined decimal odds for parlay legs"""
        product = 1.0
        for leg in legs:
            product *= leg.dk_decimal
        return product

    def _product_fair_prob(self, legs: list[CFBLeg]) -> float:
        """Calculate combined fair probability for parlay legs"""
        product = 1.0
        for leg in legs:
            product *= leg.fair_prob
        return product

    def search_best_parlay(
        self,
        legs_by_game: list[list[CFBLeg]],
        stake: float,
        max_legs: int = MAX_LEGS,
        shortlist_k: int = 8,
    ) -> tuple[CFBParlay | None, list[CFBParlay]]:
        """
        Search for the best CFB parlay by EV optimization

        Args:
            legs_by_game: List of leg options per game
            stake: Bet amount
            max_legs: Maximum number of legs to consider
            shortlist_k: Number of top parlays to return

        Returns:
            Tuple of (best_parlay, shortlist_of_top_parlays)
        """
        best_parlay = None
        all_parlays = []

        self.logger.info(
            f"Searching parlays with {len(legs_by_game)} games, {MIN_LEGS}-{max_legs} legs"
        )

        # Generate all valid combinations
        for leg_count in range(MIN_LEGS, min(max_legs, len(legs_by_game)) + 1):
            for game_indices in itertools.combinations(range(len(legs_by_game)), leg_count):
                # Get leg options for selected games
                pools = [legs_by_game[i] for i in game_indices]

                # Try all combinations of leg selections
                for leg_combination in itertools.product(*pools):
                    legs = list(leg_combination)

                    # Calculate odds and probabilities
                    combined_decimal = self._combine_decimal_odds(legs)

                    # Early exit if doesn't meet minimum odds
                    if combined_decimal < MIN_COMBINED_DECIMAL:
                        continue

                    p_win = self._product_fair_prob(legs)
                    boosted_payout = self.boosted_payout_from_decimal(stake, combined_decimal)
                    boosted_profit = boosted_payout - stake
                    ev = p_win * boosted_profit - (1 - p_win) * stake

                    # Create parlay object
                    parlay = CFBParlay(
                        legs=legs,
                        legs_count=len(legs),
                        combined_decimal=combined_decimal,
                        combined_american=self.decimal_to_american(combined_decimal),
                        p_win=p_win,
                        boosted_payout=boosted_payout,
                        boosted_profit=boosted_profit,
                        ev=ev,
                        token_percent=self.token_percent,
                        stake=stake,
                        promo_date=self.promo_date,
                        created_at=datetime.now(UTC).isoformat(),
                    )

                    all_parlays.append(parlay)

                    # Update best if this is better
                    if best_parlay is None or ev > best_parlay.ev:
                        best_parlay = parlay

        # Sort all parlays by EV and return top shortlist
        all_parlays.sort(key=lambda x: x.ev, reverse=True)
        shortlist = all_parlays[:shortlist_k]

        self.logger.info(
            f"Evaluated {len(all_parlays)} valid parlays, best EV: ${best_parlay.ev:.2f}"
            if best_parlay
            else "No valid parlays found"
        )

        return best_parlay, shortlist

    def _store_parlay_in_eq12(self, parlay: CFBParlay) -> int:
        """Store parlay in EQ12 database and return parlay_id"""
        try:
            with sqlite3.connect(EQ12_DB_PATH) as conn:
                cursor = conn.cursor()

                # Insert parlay
                cursor.execute(
                    """
                    INSERT INTO cfb_parlays
                    (promo_date, token_percent, stake, legs_count, combined_decimal,
                     combined_american, p_win, boosted_payout, boosted_profit, ev,
                     parlay_data, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        parlay.promo_date,
                        parlay.token_percent,
                        parlay.stake,
                        parlay.legs_count,
                        parlay.combined_decimal,
                        parlay.combined_american,
                        parlay.p_win,
                        parlay.boosted_payout,
                        parlay.boosted_profit,
                        parlay.ev,
                        json.dumps(parlay.to_dict()),
                        parlay.created_at,
                    ),
                )

                parlay_id = cursor.lastrowid

                # Insert legs
                for leg in parlay.legs:
                    cursor.execute(
                        """
                        INSERT INTO cfb_legs
                        (parlay_id, game_id, home_team, away_team, selection_team,
                         dk_american, dk_decimal, fair_prob, commence_time, market_type, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            parlay_id,
                            leg.game_id,
                            leg.home_team,
                            leg.away_team,
                            leg.selection_team,
                            leg.dk_american,
                            leg.dk_decimal,
                            leg.fair_prob,
                            leg.commence_time,
                            leg.market_type,
                            datetime.now(UTC).isoformat(),
                        ),
                    )

                conn.commit()
                self.logger.info(f"Stored parlay {parlay_id} in EQ12 database")
                return parlay_id

        except Exception as e:
            self.logger.error(f"Failed to store parlay in EQ12 database: {e}")
            return -1

    def optimize_cfb_parlay(
        self, stake: float = 100.0, use_cash: bool = True, store_results: bool = True
    ) -> tuple[CFBParlay | None, list[CFBParlay]]:
        """
        Main optimization function - finds the best CFB parlay for DK Mystery Profit Boost

        Args:
            stake: Bet amount (max $100 for DK promo)
            use_cash: Must use cash/DK Dollars (required for promo)
            store_results: Store results in EQ12 database

        Returns:
            Tuple of (best_parlay, shortlist)
        """
        self.logger.info(f"Starting CFB optimization: ${stake} stake, {self.token_percent}% boost")

        # Validate inputs
        if stake > MAX_STAKE:
            raise ValueError(f"Stake cannot exceed ${MAX_STAKE}")

        if not use_cash:
            raise ValueError("Must use cash/DK Dollars for Mystery Profit Boost")

        # Fetch odds data
        games_data = self.fetch_ncaaf_moneylines()

        # Filter to Friday FBS games
        friday_games = [g for g in games_data if self.is_friday_game_on_promo_date(g)]
        friday_fbs_games = [g for g in friday_games if self._is_fbs_matchup(g)]

        self.logger.info(f"Found {len(friday_fbs_games)} Friday FBS games")

        if not friday_fbs_games:
            self.logger.warning(f"No FBS Friday games found for {self.promo_date}")
            return None, []

        # Build candidate legs
        legs_by_game = self.build_candidate_legs(friday_fbs_games)

        if len(legs_by_game) < MIN_LEGS:
            self.logger.warning(
                f"Not enough DK-priced games ({len(legs_by_game)}) for {MIN_LEGS}-leg parlay"
            )
            return None, []

        # Search for best parlay
        best_parlay, shortlist = self.search_best_parlay(legs_by_game, stake)

        if not best_parlay:
            self.logger.warning("No valid parlays found meeting +300 minimum")
            return None, []

        # Validate against promo rules
        is_valid, message = self.validate_parlay(
            best_parlay.legs, best_parlay.combined_decimal, stake, use_cash
        )

        if not is_valid:
            self.logger.error(f"Best parlay failed validation: {message}")
            return None, []

        # Store in EQ12 database if enabled
        if store_results and self.eq12_integration:
            parlay_id = self._store_parlay_in_eq12(best_parlay)
            self.logger.info(f"Stored best parlay as ID {parlay_id}")

        self.logger.info(
            f"Optimization complete: {best_parlay.legs_count} legs, {best_parlay.combined_american:+d} odds, EV ${best_parlay.ev:.2f}"
        )

        return best_parlay, shortlist

    def format_dk_slip(self, parlay: CFBParlay) -> str:
        """Format parlay as DraftKings betting slip"""
        slip_lines = [
            "\n✅ DraftKings CFB Mystery Profit Boost Slip",
            f"📅 Date: {self.promo_date} | 🎯 Token: {self.token_percent}% | 💰 Stake: ${parlay.stake:.2f}",
            f"🎲 Legs: {parlay.legs_count} | 📊 Combined Odds: {parlay.combined_american:+d} (decimal {parlay.combined_decimal:.3f})",
            f"🧮 Fair Win Probability: {parlay.p_win * 100:.2f}%",
            f"💸 Boosted Payout: ${parlay.boosted_payout:.2f} | 🔥 Profit: ${parlay.boosted_profit:.2f}",
            f"📈 Expected Value: ${parlay.ev:.2f}",
            "\n🏈 Place on DraftKings (Cash/DK Dollars Only):",
        ]

        for i, leg in enumerate(parlay.legs, 1):
            matchup = f"{leg.away_team} @ {leg.home_team}"
            slip_lines.append(f"  {i}. {leg.selection_team} ML ({leg.dk_american:+d}) | {matchup}")

        slip_lines.extend(
            [
                "\n⚠️  IMPORTANT REMINDERS:",
                f"   • Apply {self.token_percent}% Mystery Profit Boost token BEFORE placing",
                "   • Use Cash or DK Dollars only (no bonus funds)",
                f"   • Verify all games are FBS and on {self.promo_date}",
                f"   • Maximum stake ${MAX_STAKE}, minimum +{MIN_COMBINED_AMERICAN} odds",
                f"   • One token per day, expires end of {self.promo_date}",
            ]
        )

        return "\n".join(slip_lines)


def main():
    """
    Main function to run CFB optimization
    Usage: python eq12_cfb_optimizer.py
    """
    # Configuration from environment variables or defaults
    token_percent = int(os.getenv("CFB_TOKEN_PERCENT", "25"))
    stake = float(os.getenv("CFB_STAKE", "100.0"))
    promo_date = os.getenv("CFB_PROMO_DATE", "2025-10-03")
    eq12_integration = os.getenv("CFB_NO_EQ12_INTEGRATION", "false").lower() != "true"

    try:
        # Initialize optimizer
        optimizer = CFBMysteryBoostOptimizer(
            token_percent=token_percent,
            max_bet=stake,
            promo_date=promo_date,
            eq12_integration=eq12_integration,
        )

        # Run optimization
        best_parlay, shortlist = optimizer.optimize_cfb_parlay(
            stake=stake, use_cash=True, store_results=True
        )

        if not best_parlay:
            print("\n❌ No valid CFB parlays found for the specified criteria")
            return

        # Display results
        print(optimizer.format_dk_slip(best_parlay))

        # Show alternatives
        if len(shortlist) > 1:
            print(f"\n🔄 Top {len(shortlist)} Alternative Parlays (by EV):")
            for i, parlay in enumerate(shortlist, 1):
                print(
                    f"  {i}. {parlay.legs_count} legs | {parlay.combined_american:+d} odds | "
                    f"P(win) {parlay.p_win * 100:.2f}% | EV ${parlay.ev:.2f}"
                )

        print(f"\n🔗 EQ12 Integration: Results stored in {EQ12_DB_PATH}")
        print("📊 View analytics: http://localhost:8000/api/cfb/analytics")

    except Exception as e:
        print(f"\n❌ CFB Optimization failed: {e}")
        logging.exception("CFB optimization error")


if __name__ == "__main__":
    main()
