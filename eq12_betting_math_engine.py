#!/usr/bin/env python3
"""
EQ12 Betting Math Engine - Deterministic Calculations Engine
===========================================================

Math-first sports betting analytics engine with OpenAI explanations only.
Built from GitHub OpenAI patterns for enterprise-grade reliability.

Core Features:
- Deterministic odds math (no-vig, EV, Kelly)
- Parlay optimization with correlation detection
- Arbitrage & middle detection
- CLV tracking and steam monitoring
- Elo/Glicko team ratings with Poisson totals
- Monte Carlo game simulation
- Risk scoring and compliance

Payment Integration:
- PayPal Standard & Express Checkout
- CashApp Business API
- Venmo Business Profile
- Automated subscription management

Revenue Model:
- EV Feed API: $29-99/month
- Parlay Builder: $49-199/month
- Arbitrage Alerts: $99-299/month
- B2B Licensing: $999+/month

Author: EQ12 Development Team
Version: 3.0.0 - GitHub Pattern Enhanced
"""

import asyncio
import hashlib
import json
import logging
import sqlite3
import statistics
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import numpy as np
from scipy import stats

# Import EQ12 components
from eq12_openai_security import EQ12OpenAISecurityManager

# Configure logging with GitHub patterns
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ==================== DATA MODELS ====================


@dataclass
class OddsData:
    """Odds data with vig removal"""

    american: int
    decimal: float
    implied_prob: float
    implied_prob_no_vig: float
    book: str
    timestamp: datetime

    @classmethod
    def from_american(cls, american: int, book: str, opponent_american: int | None = None):
        """Create from American odds with vig removal"""
        decimal = cls.american_to_decimal(american)
        implied = cls.decimal_to_implied_prob(decimal)

        # Remove vig if opponent odds available
        no_vig_prob = implied
        if opponent_american is not None:
            opp_decimal = cls.american_to_decimal(opponent_american)
            opp_implied = cls.decimal_to_implied_prob(opp_decimal)
            no_vig_prob = implied / (implied + opp_implied)

        return cls(
            american=american,
            decimal=decimal,
            implied_prob=implied,
            implied_prob_no_vig=no_vig_prob,
            book=book,
            timestamp=datetime.now(UTC),
        )

    @staticmethod
    def american_to_decimal(american: int) -> float:
        """Convert American odds to decimal"""
        if american > 0:
            return (american / 100) + 1
        else:
            return (100 / abs(american)) + 1

    @staticmethod
    def decimal_to_implied_prob(decimal: float) -> float:
        """Convert decimal odds to implied probability"""
        return 1.0 / decimal

    @staticmethod
    def decimal_to_american(decimal: float) -> int:
        """Convert decimal odds to American"""
        if decimal >= 2.0:
            return int((decimal - 1) * 100)
        else:
            return int(-100 / (decimal - 1))


@dataclass
class BettingLeg:
    """Individual betting leg with EV calculations"""

    selection: str
    market: str
    odds_data: OddsData
    model_prob: float
    ev_decimal: float
    ev_percent: float
    kelly_fraction: float
    risk_score: float
    confidence: float

    @property
    def is_positive_ev(self) -> bool:
        return self.ev_percent > 0

    @property
    def edge_classification(self) -> str:
        if self.ev_percent >= 5.0:
            return "strong"
        elif self.ev_percent >= 2.0:
            return "moderate"
        elif self.ev_percent > 0:
            return "slight"
        else:
            return "negative"


@dataclass
class ParlayData:
    """Parlay with correlation analysis"""

    legs: list[BettingLeg]
    correlation_matrix: np.ndarray
    joint_probability: float
    parlay_odds: float
    parlay_ev_percent: float
    kelly_fraction: float
    risk_score: float

    @property
    def is_sgp(self) -> bool:
        """Check if same-game parlay"""
        games = set()
        for leg in self.legs:
            # Extract game identifier from selection
            game_id = self._extract_game_id(leg.selection)
            games.add(game_id)
        return len(games) == 1

    def _extract_game_id(self, selection: str) -> str:
        """Extract game identifier from selection string"""
        # Simple implementation - in production would be more sophisticated
        parts = selection.split(" ")
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
        return selection.split("_")[0] if "_" in selection else selection


@dataclass
class ArbitrageOpportunity:
    """Arbitrage betting opportunity"""

    leg_a: BettingLeg
    leg_b: BettingLeg
    profit_percent: float
    stake_a: float
    stake_b: float
    total_stake: float
    guaranteed_profit: float


@dataclass
class TeamRating:
    """Elo/Glicko team rating"""

    team: str
    offensive_rating: float
    defensive_rating: float
    overall_rating: float
    home_field_advantage: float
    recent_form: float
    last_updated: datetime


# ==================== CORE MATH ENGINE ====================


class EQ12BettingMathEngine:
    """Deterministic sports betting calculations engine"""

    def __init__(self):
        # OpenAI for explanations only (GitHub pattern)
        self.openai_manager = EQ12OpenAISecurityManager("math_engine")

        # Database
        self.db_path = "C:/EQ12/logs/betting_math.db"

        # Kelly multipliers by risk tolerance
        self.kelly_multipliers = {
            "conservative": 0.125,  # 1/8 Kelly
            "moderate": 0.25,  # 1/4 Kelly
            "aggressive": 0.5,  # 1/2 Kelly
        }

        # Risk thresholds
        self.risk_thresholds = {
            "max_ev_threshold": 15.0,  # Cap at 15% EV for sanity
            "min_model_prob": 0.05,  # Don't bet < 5% chances
            "max_model_prob": 0.95,  # Don't bet > 95% chances
            "max_parlay_legs": 8,  # Max 8-leg parlays
            "correlation_threshold": 0.25,  # Block correlated SGP legs
        }

        # Payment processors
        self.payment_processors = {
            "paypal": {"client_id": None, "client_secret": None},
            "cashapp": {"client_id": None, "client_secret": None},
            "venmo": {"access_token": None},
        }

        # Pricing tiers
        self.pricing_tiers = {
            "starter": {"price": 29.00, "ev_calls": 100, "parlays": 10},
            "pro": {"price": 99.00, "ev_calls": 1000, "parlays": 100},
            "enterprise": {"price": 299.00, "ev_calls": 10000, "parlays": 1000},
        }

        self.setup_database()
        logger.info("✅ EQ12 Betting Math Engine initialized")

    def setup_database(self):
        """Initialize math engine database with GitHub patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Odds history with normalized structure
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS odds_history (
                id TEXT PRIMARY KEY,
                selection TEXT NOT NULL,
                market TEXT NOT NULL,
                sportsbook TEXT NOT NULL,
                american_odds INTEGER NOT NULL,
                decimal_odds REAL NOT NULL,
                implied_prob REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                game_date DATETIME,
                sport TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_odds_history
            ON odds_history(selection, sportsbook, timestamp)
        """
        )

        # EV calculations log
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ev_calculations (
                id TEXT PRIMARY KEY,
                selection TEXT NOT NULL,
                model_prob REAL NOT NULL,
                best_odds_decimal REAL NOT NULL,
                best_sportsbook TEXT NOT NULL,
                ev_decimal REAL NOT NULL,
                ev_percent REAL NOT NULL,
                kelly_fraction REAL NOT NULL,
                calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ev_calculations
            ON ev_calculations(ev_percent DESC, calculated_at DESC)
        """
        )

        # Parlay analysis
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS parlay_analysis (
                id TEXT PRIMARY KEY,
                legs_json TEXT NOT NULL,
                joint_probability REAL NOT NULL,
                parlay_odds REAL NOT NULL,
                parlay_ev_percent REAL NOT NULL,
                correlation_score REAL NOT NULL,
                is_sgp BOOLEAN NOT NULL,
                calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )
        """
        )

        # Team ratings (Elo)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS team_ratings (
                team TEXT PRIMARY KEY,
                sport TEXT NOT NULL,
                offensive_rating REAL NOT NULL,
                defensive_rating REAL NOT NULL,
                overall_rating REAL NOT NULL,
                home_field_advantage REAL NOT NULL,
                games_played INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # CLV tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clv_tracking (
                id TEXT PRIMARY KEY,
                selection TEXT NOT NULL,
                entry_odds REAL NOT NULL,
                closing_odds REAL NOT NULL,
                clv_percent REAL NOT NULL,
                outcome TEXT,
                profit_loss REAL,
                tracked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_clv_tracking
            ON clv_tracking(clv_percent DESC, tracked_at DESC)
        """
        )

        # Revenue tracking with payment processor support
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS revenue_tracking (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                subscription_tier TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_processor TEXT NOT NULL,
                transaction_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Database schema initialized with GitHub patterns")

    # ==================== ODDS MATH (DETERMINISTIC) ====================

    def calculate_ev_for_leg(
        self,
        selection: str,
        american_odds: int,
        sportsbook: str,
        model_prob: float,
        opponent_odds: int | None = None,
    ) -> BettingLeg:
        """Calculate EV for a single betting leg (pure math)"""

        # Create odds data with vig removal
        odds_data = OddsData.from_american(american_odds, sportsbook, opponent_odds)

        # EV calculation: EV = p*(odds-1) - (1-p)
        ev_decimal = model_prob * (odds_data.decimal - 1) - (1 - model_prob)
        ev_percent = ev_decimal * 100

        # Kelly criterion: f* = (bp - q) / b where b = decimal - 1
        b = odds_data.decimal - 1
        q = 1 - model_prob
        kelly_fraction = max(0, (b * model_prob - q) / b)

        # Risk scoring
        risk_score = self._calculate_leg_risk(odds_data, model_prob, kelly_fraction)

        # Confidence based on edge size and probability range
        confidence = self._calculate_confidence(ev_percent, model_prob)

        leg = BettingLeg(
            selection=selection,
            market=self._extract_market(selection),
            odds_data=odds_data,
            model_prob=model_prob,
            ev_decimal=ev_decimal,
            ev_percent=ev_percent,
            kelly_fraction=kelly_fraction,
            risk_score=risk_score,
            confidence=confidence,
        )

        # Log calculation
        self._log_ev_calculation(leg)

        return leg

    def remove_vig_two_way(self, odds_a: int, odds_b: int) -> tuple[float, float]:
        """Remove vig from two-way market (deterministic)"""

        decimal_a = OddsData.american_to_decimal(odds_a)
        decimal_b = OddsData.american_to_decimal(odds_b)

        implied_a = 1.0 / decimal_a
        implied_b = 1.0 / decimal_b

        total_implied = implied_a + implied_b

        # No-vig probabilities
        prob_a_no_vig = implied_a / total_implied
        prob_b_no_vig = implied_b / total_implied

        return prob_a_no_vig, prob_b_no_vig

    def find_best_odds(self, selection: str, odds_dict: dict[str, int]) -> tuple[str, int]:
        """Find sportsbook with best odds for selection"""

        best_book = None
        best_odds = None
        best_decimal = 0

        for book, odds in odds_dict.items():
            decimal = OddsData.american_to_decimal(odds)
            if decimal > best_decimal:
                best_decimal = decimal
                best_odds = odds
                best_book = book

        return best_book, best_odds

    # ==================== KELLY STAKING ====================

    def calculate_kelly_stake(
        self,
        kelly_fraction: float,
        bankroll: float,
        risk_tolerance: str = "moderate",
        max_bet_size: float | None = None,
    ) -> float:
        """Calculate optimal bet size using Kelly criterion"""

        # Apply fractional Kelly multiplier
        multiplier = self.kelly_multipliers.get(risk_tolerance, 0.25)
        adjusted_kelly = kelly_fraction * multiplier

        # Calculate stake
        stake = bankroll * adjusted_kelly

        # Apply maximum bet size if specified
        if max_bet_size is not None:
            stake = min(stake, max_bet_size)

        # Ensure minimum stake (avoid micro-bets)
        min_stake = max(1.0, bankroll * 0.001)  # 0.1% of bankroll minimum
        stake = max(stake, min_stake) if stake > 0 else 0

        return round(stake, 2)

    # ==================== PARLAY OPTIMIZATION ====================

    def optimize_parlay(
        self, legs: list[BettingLeg], max_legs: int = 4, bankroll: float = 1000.0
    ) -> ParlayData | None:
        """Optimize parlay selection with correlation analysis"""

        if len(legs) < 2:
            return None

        if len(legs) > max_legs:
            legs = legs[:max_legs]  # Truncate to max

        # Check for same-game correlations
        if self._is_same_game_parlay(legs):
            correlation_matrix = self._calculate_sgp_correlations(legs)
            if self._has_forbidden_correlations(correlation_matrix):
                logger.warning("🚫 Blocking correlated SGP legs")
                return None
        else:
            # Independent games - assume zero correlation
            correlation_matrix = np.zeros((len(legs), len(legs)))

        # Calculate joint probability
        if np.any(correlation_matrix != 0):
            # Use Monte Carlo for correlated events
            joint_prob = self._monte_carlo_joint_probability(legs, correlation_matrix)
        else:
            # Independent multiplication
            joint_prob = np.prod([leg.model_prob for leg in legs])

        # Calculate parlay odds (multiply decimals)
        parlay_odds = np.prod([leg.odds_data.decimal for leg in legs])

        # Parlay EV
        parlay_ev = joint_prob * (parlay_odds - 1) - (1 - joint_prob)
        parlay_ev_percent = parlay_ev * 100

        # Kelly for parlay
        b_parlay = parlay_odds - 1
        q_parlay = 1 - joint_prob
        kelly_parlay = max(0, (b_parlay * joint_prob - q_parlay) / b_parlay)

        # Risk scoring
        risk_score = self._calculate_parlay_risk(legs, correlation_matrix)

        parlay_data = ParlayData(
            legs=legs,
            correlation_matrix=correlation_matrix,
            joint_probability=joint_prob,
            parlay_odds=parlay_odds,
            parlay_ev_percent=parlay_ev_percent,
            kelly_fraction=kelly_parlay,
            risk_score=risk_score,
        )

        # Log parlay analysis
        self._log_parlay_analysis(parlay_data)

        return parlay_data

    def _is_same_game_parlay(self, legs: list[BettingLeg]) -> bool:
        """Check if all legs are from the same game"""
        game_ids = set()
        for leg in legs:
            game_id = self._extract_game_id(leg.selection)
            game_ids.add(game_id)

        return len(game_ids) == 1

    def _calculate_sgp_correlations(self, legs: list[BettingLeg]) -> np.ndarray:
        """Calculate correlations for same-game parlay legs"""
        n = len(legs)
        correlation_matrix = np.eye(n)

        # Hardcoded correlations for common SGP combinations
        correlation_rules = {
            ("moneyline", "spread"): 0.85,  # ML and spread highly correlated
            ("spread", "total"): 0.15,  # Spread and total slightly correlated
            ("player_points", "team_total"): 0.40,  # Player props and team totals
            ("first_half", "full_game"): 0.75,  # First half and full game results
        }

        for i in range(n):
            for j in range(i + 1, n):
                market_i = legs[i].market.lower()
                market_j = legs[j].market.lower()

                # Check correlation rules
                correlation = 0.0
                for (market_a, market_b), corr_value in correlation_rules.items():
                    if (market_a in market_i and market_b in market_j) or (
                        market_b in market_i and market_a in market_j
                    ):
                        correlation = corr_value
                        break

                correlation_matrix[i][j] = correlation
                correlation_matrix[j][i] = correlation

        return correlation_matrix

    def _has_forbidden_correlations(self, correlation_matrix: np.ndarray) -> bool:
        """Check if parlay has forbidden high correlations"""
        threshold = self.risk_thresholds["correlation_threshold"]

        # Check for correlations above threshold
        for i in range(correlation_matrix.shape[0]):
            for j in range(i + 1, correlation_matrix.shape[1]):
                if abs(correlation_matrix[i][j]) > threshold:
                    return True

        return False

    def _monte_carlo_joint_probability(
        self, legs: list[BettingLeg], correlation_matrix: np.ndarray, n_simulations: int = 10000
    ) -> float:
        """Monte Carlo simulation for correlated joint probability"""

        n_legs = len(legs)
        probabilities = [leg.model_prob for leg in legs]

        # Convert probabilities to normal distributions for correlation
        normal_thresholds = [stats.norm.ppf(p) for p in probabilities]

        # Generate correlated random variables
        successes = 0

        for _ in range(n_simulations):
            # Generate correlated normal variables
            random_normals = np.random.multivariate_normal(
                mean=np.zeros(n_legs), cov=correlation_matrix, size=1
            )[0]

            # Check if each leg hits based on threshold
            all_hit = True
            for _i, (threshold, random_val) in enumerate(
                zip(normal_thresholds, random_normals, strict=False)
            ):
                if random_val <= threshold:
                    all_hit = False
                    break

            if all_hit:
                successes += 1

        return successes / n_simulations

    # ==================== ARBITRAGE DETECTION ====================

    def detect_arbitrage(
        self,
        selection_a: str,
        odds_a: int,
        book_a: str,
        selection_b: str,
        odds_b: int,
        book_b: str,
        total_stake: float = 100.0,
    ) -> ArbitrageOpportunity | None:
        """Detect arbitrage opportunity between two selections"""

        decimal_a = OddsData.american_to_decimal(odds_a)
        decimal_b = OddsData.american_to_decimal(odds_b)

        # Check for arbitrage: 1/decimal_a + 1/decimal_b < 1
        implied_total = (1 / decimal_a) + (1 / decimal_b)

        if implied_total >= 1.0:
            return None  # No arbitrage

        # Calculate optimal stakes
        stake_a = total_stake * (1 / decimal_a) / implied_total
        stake_b = total_stake * (1 / decimal_b) / implied_total

        # Calculate guaranteed profit
        payout_a = stake_a * decimal_a
        payout_b = stake_b * decimal_b
        guaranteed_profit = min(payout_a, payout_b) - total_stake
        profit_percent = (guaranteed_profit / total_stake) * 100

        # Create legs for the arbitrage
        leg_a = BettingLeg(
            selection=selection_a,
            market=self._extract_market(selection_a),
            odds_data=OddsData.from_american(odds_a, book_a),
            model_prob=0.5,  # Not relevant for arbitrage
            ev_decimal=0.0,
            ev_percent=0.0,
            kelly_fraction=0.0,
            risk_score=0.0,  # Arbitrage has no risk
            confidence=1.0,  # 100% confidence in arbitrage
        )

        leg_b = BettingLeg(
            selection=selection_b,
            market=self._extract_market(selection_b),
            odds_data=OddsData.from_american(odds_b, book_b),
            model_prob=0.5,
            ev_decimal=0.0,
            ev_percent=0.0,
            kelly_fraction=0.0,
            risk_score=0.0,
            confidence=1.0,
        )

        return ArbitrageOpportunity(
            leg_a=leg_a,
            leg_b=leg_b,
            profit_percent=profit_percent,
            stake_a=round(stake_a, 2),
            stake_b=round(stake_b, 2),
            total_stake=total_stake,
            guaranteed_profit=round(guaranteed_profit, 2),
        )

    def detect_middle_opportunity(
        self,
        spread_line_a: float,
        odds_a: int,
        book_a: str,
        spread_line_b: float,
        odds_b: int,
        book_b: str,
    ) -> dict | None:
        """Detect middle betting opportunity on spreads"""

        # Check if lines create a middle (gap between them)
        if spread_line_a >= spread_line_b:
            return None  # No middle possible

        middle_gap = spread_line_b - spread_line_a

        # Check if gap is around key numbers (3, 7, 10, 14)
        key_numbers = [3, 7, 10, 14]
        contains_key_number = any(
            spread_line_a < key_num < spread_line_b for key_num in key_numbers
        )

        if middle_gap < 1.5:  # Minimum gap for viable middle
            return None

        OddsData.american_to_decimal(odds_a)
        OddsData.american_to_decimal(odds_b)

        return {
            "spread_a": spread_line_a,
            "odds_a": odds_a,
            "book_a": book_a,
            "spread_b": spread_line_b,
            "odds_b": odds_b,
            "book_b": book_b,
            "middle_gap": middle_gap,
            "contains_key_number": contains_key_number,
            "potential_middle_win": middle_gap > 1.5 and contains_key_number,
        }

    # ==================== TEAM RATINGS & MODELING ====================

    def update_team_rating(self, team: str, sport: str, game_result: dict[str, Any]):
        """Update Elo ratings based on game result"""

        # Get current rating
        current_rating = self._get_team_rating(team, sport)

        # Elo parameters
        k_factor = 32  # Adjustment rate
        home_advantage = 100 if game_result.get("home_team") == team else 0

        # Calculate expected score
        opponent = game_result["opponent"]
        opponent_rating = self._get_team_rating(opponent, sport)

        rating_diff = (
            current_rating.overall_rating - opponent_rating.overall_rating + home_advantage
        )
        expected_score = 1 / (1 + 10 ** (-rating_diff / 400))

        # Actual score (1 for win, 0.5 for tie, 0 for loss)
        actual_score = 1.0 if game_result["won"] else 0.0
        if game_result.get("tie", False):
            actual_score = 0.5

        # Update rating
        new_rating = current_rating.overall_rating + k_factor * (actual_score - expected_score)

        # Update in database
        self._update_team_rating_db(team, sport, new_rating, game_result)

    def calculate_win_probability(self, home_team: str, away_team: str, sport: str) -> float:
        """Calculate win probability using team ratings"""

        home_rating = self._get_team_rating(home_team, sport)
        away_rating = self._get_team_rating(away_team, sport)

        # Elo win probability with home field advantage
        rating_diff = (
            home_rating.overall_rating
            - away_rating.overall_rating
            + home_rating.home_field_advantage
        )
        win_prob = 1 / (1 + 10 ** (-rating_diff / 400))

        return min(max(win_prob, 0.05), 0.95)  # Clamp between 5% and 95%

    def simulate_game_total(self, home_team: str, away_team: str, sport: str) -> dict[str, float]:
        """Simulate game total using Poisson model"""

        home_rating = self._get_team_rating(home_team, sport)
        away_rating = self._get_team_rating(away_team, sport)

        # Convert ratings to scoring rates (simplified)
        league_avg_scoring = {"nfl": 23.0, "nba": 110.0, "nhl": 3.0}.get(sport, 20.0)

        home_scoring_rate = league_avg_scoring * (home_rating.offensive_rating / 1500)
        away_scoring_rate = league_avg_scoring * (away_rating.offensive_rating / 1500)

        # Adjust for defense
        home_scoring_rate *= 1600 / away_rating.defensive_rating
        away_scoring_rate *= 1600 / home_rating.defensive_rating

        # Home field advantage
        home_scoring_rate *= 1.05

        # Monte Carlo simulation
        n_sims = 1000
        home_scores = np.random.poisson(home_scoring_rate, n_sims)
        away_scores = np.random.poisson(away_scoring_rate, n_sims)
        total_scores = home_scores + away_scores

        return {
            "mean_total": float(np.mean(total_scores)),
            "std_total": float(np.std(total_scores)),
            "over_prob": lambda total_line: float(np.mean(total_scores > total_line)),
            "home_win_prob": float(np.mean(home_scores > away_scores)),
        }

    # ==================== CLV TRACKING ====================

    def track_closing_line_value(
        self,
        selection: str,
        entry_odds: int,
        closing_odds: int,
        outcome: str | None = None,
        profit_loss: float | None = None,
    ):
        """Track closing line value for bet"""

        entry_decimal = OddsData.american_to_decimal(entry_odds)
        closing_decimal = OddsData.american_to_decimal(closing_odds)

        # CLV% = (closing_decimal - entry_decimal) / entry_decimal * 100
        clv_percent = ((closing_decimal - entry_decimal) / entry_decimal) * 100

        # Store CLV data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        clv_id = hashlib.md5(f"{selection}{entry_odds}{time.time()}".encode()).hexdigest()

        cursor.execute(
            """
            INSERT INTO clv_tracking
            (id, selection, entry_odds, closing_odds, clv_percent, outcome, profit_loss)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (clv_id, selection, entry_decimal, closing_decimal, clv_percent, outcome, profit_loss),
        )

        conn.commit()
        conn.close()

        logger.info(f"📊 CLV tracked: {selection} = {clv_percent:.2f}%")

        return clv_percent

    def get_clv_performance(self, days: int = 30) -> dict[str, float]:
        """Get CLV performance statistics"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT clv_percent, outcome, profit_loss
            FROM clv_tracking
            WHERE tracked_at >= datetime('now', '-{days} days')
        """
        )

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {}

        clv_values = [row[0] for row in rows]
        outcomes = [row[1] for row in rows if row[1] is not None]
        profits = [row[2] for row in rows if row[2] is not None]

        stats = {
            "avg_clv": statistics.mean(clv_values),
            "positive_clv_rate": len([c for c in clv_values if c > 0]) / len(clv_values),
            "total_bets": len(rows),
        }

        if outcomes:
            wins = len([o for o in outcomes if o == "win"])
            stats["win_rate"] = wins / len(outcomes)

        if profits:
            stats["total_profit"] = sum(profits)
            stats["roi"] = (sum(profits) / len(profits)) * 100

        return stats

    # ==================== PAYMENT INTEGRATION ====================

    async def create_paypal_subscription(self, user_id: str, tier: str) -> dict[str, Any]:
        """Create PayPal subscription"""

        try:
            # PayPal API integration (simplified)
            tier_info = self.pricing_tiers.get(tier, self.pricing_tiers["starter"])

            # Simulate PayPal API call
            subscription_id = f"paypal_{user_id}_{int(time.time())}"

            # Store subscription
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            revenue_id = hashlib.md5(f"{user_id}{tier}{time.time()}".encode()).hexdigest()
            expires_at = datetime.now() + timedelta(days=30)

            cursor.execute(
                """
                INSERT INTO revenue_tracking
                (id, user_id, subscription_tier, amount, payment_processor, transaction_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    revenue_id,
                    user_id,
                    tier,
                    tier_info["price"],
                    "paypal",
                    subscription_id,
                    expires_at,
                ),
            )

            conn.commit()
            conn.close()

            return {
                "subscription_id": subscription_id,
                "approval_url": f"https://paypal.com/subscribe/{subscription_id}",
                "status": "pending",
            }

        except Exception as e:
            logger.error(f"PayPal subscription error: {e}")
            raise

    async def create_cashapp_payment(self, user_id: str, tier: str) -> dict[str, Any]:
        """Create CashApp payment"""

        try:
            tier_info = self.pricing_tiers.get(tier, self.pricing_tiers["starter"])

            # CashApp API integration (simplified)
            {
                "amount": int(tier_info["price"] * 100),  # Amount in cents
                "currency": "USD",
                "redirect_url": "https://eq12.com/cashapp/success",
                "note": f"EQ12 Betting Math Engine - {tier.title()} Subscription",
            }

            # Simulate CashApp API
            payment_id = f"cashapp_{user_id}_{int(time.time())}"

            # Store payment record
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            revenue_id = hashlib.md5(f"{user_id}{tier}{time.time()}".encode()).hexdigest()
            expires_at = datetime.now() + timedelta(days=30)

            cursor.execute(
                """
                INSERT INTO revenue_tracking
                (id, user_id, subscription_tier, amount, payment_processor, transaction_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (revenue_id, user_id, tier, tier_info["price"], "cashapp", payment_id, expires_at),
            )

            conn.commit()
            conn.close()

            return {
                "payment_id": payment_id,
                "payment_url": f"https://cash.app/pay/{payment_id}",
                "qr_code_url": f"https://cash.app/qr/{payment_id}",
                "status": "pending",
            }

        except Exception as e:
            logger.error(f"CashApp payment error: {e}")
            raise

    async def create_venmo_charge(self, user_id: str, tier: str) -> dict[str, Any]:
        """Create Venmo payment charge"""

        try:
            tier_info = self.pricing_tiers.get(tier, self.pricing_tiers["starter"])

            # Venmo API integration (simplified)
            {
                "amount": tier_info["price"],
                "note": f"EQ12 {tier.title()} Subscription",
                "target": {"user_id": user_id},
            }

            # Simulate Venmo API
            charge_id = f"venmo_{user_id}_{int(time.time())}"

            # Store charge record
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            revenue_id = hashlib.md5(f"{user_id}{tier}{time.time()}".encode()).hexdigest()
            expires_at = datetime.now() + timedelta(days=30)

            cursor.execute(
                """
                INSERT INTO revenue_tracking
                (id, user_id, subscription_tier, amount, payment_processor, transaction_id, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (revenue_id, user_id, tier, tier_info["price"], "venmo", charge_id, expires_at),
            )

            conn.commit()
            conn.close()

            return {
                "charge_id": charge_id,
                "venmo_url": f"https://venmo.com/charge/{charge_id}",
                "status": "pending",
            }

        except Exception as e:
            logger.error(f"Venmo charge error: {e}")
            raise

    # ==================== API ENDPOINTS ====================

    def create_fastapi_app(self):
        """Create FastAPI app with all betting math endpoints"""

        from fastapi import FastAPI, HTTPException, Query

        app = FastAPI(
            title="EQ12 Betting Math Engine",
            description="Deterministic sports betting calculations with OpenAI explanations",
            version="3.0.0",
        )

        @app.post("/api/ev/calculate")
        async def calculate_ev(data: dict[str, Any]):
            """Calculate EV for betting leg"""
            try:
                leg = self.calculate_ev_for_leg(
                    selection=data["selection"],
                    american_odds=data["american_odds"],
                    sportsbook=data["sportsbook"],
                    model_prob=data["model_prob"],
                    opponent_odds=data.get("opponent_odds"),
                )

                # Get OpenAI explanation if requested
                explanation = None
                if data.get("include_explanation", False):
                    explanation = await self._get_ev_explanation(leg)

                return {
                    "selection": leg.selection,
                    "ev_percent": leg.ev_percent,
                    "kelly_fraction": leg.kelly_fraction,
                    "edge_classification": leg.edge_classification,
                    "confidence": leg.confidence,
                    "explanation": explanation,
                }

            except Exception as e:
                raise HTTPException(500, str(e))

        @app.post("/api/parlay/optimize")
        async def optimize_parlay_endpoint(data: dict[str, Any]):
            """Optimize parlay with correlation analysis"""
            try:
                # Convert legs data to BettingLeg objects
                legs = []
                for leg_data in data["legs"]:
                    leg = self.calculate_ev_for_leg(
                        selection=leg_data["selection"],
                        american_odds=leg_data["american_odds"],
                        sportsbook=leg_data["sportsbook"],
                        model_prob=leg_data["model_prob"],
                    )
                    legs.append(leg)

                parlay = self.optimize_parlay(
                    legs=legs,
                    max_legs=data.get("max_legs", 4),
                    bankroll=data.get("bankroll", 1000.0),
                )

                if not parlay:
                    return {"error": "No viable parlay found"}

                # Get explanation
                explanation = None
                if data.get("include_explanation", False):
                    explanation = await self._get_parlay_explanation(parlay)

                return {
                    "parlay_ev_percent": parlay.parlay_ev_percent,
                    "joint_probability": parlay.joint_probability,
                    "kelly_fraction": parlay.kelly_fraction,
                    "is_sgp": parlay.is_sgp,
                    "risk_score": parlay.risk_score,
                    "legs_count": len(parlay.legs),
                    "explanation": explanation,
                }

            except Exception as e:
                raise HTTPException(500, str(e))

        @app.post("/api/arbitrage/detect")
        async def detect_arbitrage_endpoint(data: dict[str, Any]):
            """Detect arbitrage opportunities"""
            try:
                arb = self.detect_arbitrage(
                    selection_a=data["selection_a"],
                    odds_a=data["odds_a"],
                    book_a=data["book_a"],
                    selection_b=data["selection_b"],
                    odds_b=data["odds_b"],
                    book_b=data["book_b"],
                    total_stake=data.get("total_stake", 100.0),
                )

                if not arb:
                    return {"arbitrage_found": False}

                return {
                    "arbitrage_found": True,
                    "profit_percent": arb.profit_percent,
                    "stake_a": arb.stake_a,
                    "stake_b": arb.stake_b,
                    "guaranteed_profit": arb.guaranteed_profit,
                }

            except Exception as e:
                raise HTTPException(500, str(e))

        @app.get("/api/clv/performance")
        async def get_clv_performance_endpoint(days: int = Query(30)):
            """Get CLV performance statistics"""
            try:
                stats = self.get_clv_performance(days)
                return stats
            except Exception as e:
                raise HTTPException(500, str(e))

        @app.post("/api/subscription/paypal")
        async def create_paypal_subscription_endpoint(data: dict[str, Any]):
            """Create PayPal subscription"""
            try:
                result = await self.create_paypal_subscription(
                    user_id=data["user_id"], tier=data["tier"]
                )
                return result
            except Exception as e:
                raise HTTPException(500, str(e))

        @app.post("/api/payment/cashapp")
        async def create_cashapp_payment_endpoint(data: dict[str, Any]):
            """Create CashApp payment"""
            try:
                result = await self.create_cashapp_payment(
                    user_id=data["user_id"], tier=data["tier"]
                )
                return result
            except Exception as e:
                raise HTTPException(500, str(e))

        @app.post("/api/charge/venmo")
        async def create_venmo_charge_endpoint(data: dict[str, Any]):
            """Create Venmo charge"""
            try:
                result = await self.create_venmo_charge(user_id=data["user_id"], tier=data["tier"])
                return result
            except Exception as e:
                raise HTTPException(500, str(e))

        @app.get("/api/pricing")
        async def get_pricing():
            """Get pricing tiers"""
            return {"tiers": self.pricing_tiers, "payment_methods": ["paypal", "cashapp", "venmo"]}

        return app

    # ==================== HELPER METHODS ====================

    def _extract_market(self, selection: str) -> str:
        """Extract market type from selection string"""
        selection_lower = selection.lower()

        if "moneyline" in selection_lower or "ml" in selection_lower:
            return "moneyline"
        elif "spread" in selection_lower or "point spread" in selection_lower:
            return "spread"
        elif "total" in selection_lower or "over" in selection_lower or "under" in selection_lower:
            return "total"
        elif "prop" in selection_lower or "player" in selection_lower:
            return "player_prop"
        else:
            return "other"

    def _extract_game_id(self, selection: str) -> str:
        """Extract game identifier from selection"""
        # Simple implementation - extract team names
        parts = selection.replace("@", " ").split()
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
        return selection.split("_")[0] if "_" in selection else "unknown"

    def _calculate_leg_risk(
        self, odds_data: OddsData, model_prob: float, kelly_fraction: float
    ) -> float:
        """Calculate risk score for individual leg"""

        risk_factors = []

        # Probability risk (extreme probabilities are risky)
        if model_prob < 0.1 or model_prob > 0.9:
            risk_factors.append(0.3)

        # Odds risk (very long or very short odds)
        if odds_data.decimal > 10.0 or odds_data.decimal < 1.2:
            risk_factors.append(0.2)

        # Kelly risk (high Kelly fractions)
        if kelly_fraction > 0.1:  # > 10% of bankroll
            risk_factors.append(0.4)

        # Vig risk (high vig means worse prices)
        if odds_data.implied_prob > odds_data.implied_prob_no_vig * 1.1:
            risk_factors.append(0.1)

        return min(sum(risk_factors), 1.0)

    def _calculate_confidence(self, ev_percent: float, model_prob: float) -> float:
        """Calculate confidence in the betting recommendation"""

        # Base confidence on edge size
        edge_confidence = min(abs(ev_percent) / 10.0, 1.0)  # Max at 10% EV

        # Probability confidence (higher for moderate probabilities)
        prob_confidence = 1.0 - abs(model_prob - 0.5) * 2

        # Combined confidence
        return (edge_confidence + prob_confidence) / 2

    def _calculate_parlay_risk(
        self, legs: list[BettingLeg], correlation_matrix: np.ndarray
    ) -> float:
        """Calculate risk score for parlay"""

        # Base risk from individual legs
        leg_risks = [leg.risk_score for leg in legs]
        avg_leg_risk = statistics.mean(leg_risks)

        # Correlation risk
        correlation_risk = 0.0
        if correlation_matrix.size > 0:
            max_correlation = np.max(np.abs(correlation_matrix))
            correlation_risk = max_correlation * 0.5

        # Length risk (more legs = higher risk)
        length_risk = min(len(legs) / 10.0, 0.5)

        return min(avg_leg_risk + correlation_risk + length_risk, 1.0)

    def _get_team_rating(self, team: str, sport: str) -> TeamRating:
        """Get team rating from database or create default"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM team_ratings WHERE team = ? AND sport = ?
        """,
            (team, sport),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return TeamRating(
                team=row[0],
                offensive_rating=row[2],
                defensive_rating=row[3],
                overall_rating=row[4],
                home_field_advantage=row[5],
                recent_form=0.0,  # Would calculate from recent games
                last_updated=datetime.fromisoformat(row[7]),
            )
        else:
            # Create default rating
            default_rating = TeamRating(
                team=team,
                offensive_rating=1500.0,  # Elo-style default
                defensive_rating=1500.0,
                overall_rating=1500.0,
                home_field_advantage=50.0,
                recent_form=0.0,
                last_updated=datetime.now(),
            )

            # Store default in database
            self._create_team_rating_db(default_rating, sport)
            return default_rating

    def _create_team_rating_db(self, rating: TeamRating, sport: str):
        """Create team rating in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO team_ratings
            (team, sport, offensive_rating, defensive_rating, overall_rating, home_field_advantage)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                rating.team,
                sport,
                rating.offensive_rating,
                rating.defensive_rating,
                rating.overall_rating,
                rating.home_field_advantage,
            ),
        )

        conn.commit()
        conn.close()

    def _update_team_rating_db(self, team: str, sport: str, new_rating: float, game_result: dict):
        """Update team rating in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE team_ratings
            SET overall_rating = ?, games_played = games_played + 1, last_updated = CURRENT_TIMESTAMP
            WHERE team = ? AND sport = ?
        """,
            (new_rating, team, sport),
        )

        conn.commit()
        conn.close()

    def _log_ev_calculation(self, leg: BettingLeg):
        """Log EV calculation to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        calc_id = hashlib.md5(
            f"{leg.selection}{leg.odds_data.american}{time.time()}".encode()
        ).hexdigest()

        cursor.execute(
            """
            INSERT INTO ev_calculations
            (id, selection, model_prob, best_odds_decimal, best_sportsbook,
             ev_decimal, ev_percent, kelly_fraction)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                calc_id,
                leg.selection,
                leg.model_prob,
                leg.odds_data.decimal,
                leg.odds_data.book,
                leg.ev_decimal,
                leg.ev_percent,
                leg.kelly_fraction,
            ),
        )

        conn.commit()
        conn.close()

    def _log_parlay_analysis(self, parlay: ParlayData):
        """Log parlay analysis to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        parlay_id = hashlib.md5(f"{len(parlay.legs)}{time.time()}".encode()).hexdigest()
        legs_json = json.dumps(
            [{"selection": leg.selection, "ev": leg.ev_percent} for leg in parlay.legs]
        )

        cursor.execute(
            """
            INSERT INTO parlay_analysis
            (id, legs_json, joint_probability, parlay_odds, parlay_ev_percent,
             correlation_score, is_sgp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                parlay_id,
                legs_json,
                parlay.joint_probability,
                parlay.parlay_odds,
                parlay.parlay_ev_percent,
                float(np.max(parlay.correlation_matrix)),
                parlay.is_sgp,
            ),
        )

        conn.commit()
        conn.close()

    async def _get_ev_explanation(self, leg: BettingLeg) -> str:
        """Get OpenAI explanation for EV calculation"""

        try:
            prompt = f"""
            Explain this betting edge in simple terms:

            Selection: {leg.selection}
            Model Probability: {leg.model_prob:.1%}
            Odds: {leg.odds_data.american} ({leg.odds_data.decimal:.2f})
            Expected Value: {leg.ev_percent:.2f}%

            Keep explanation under 100 words, focus on why this represents value.
            """

            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [{"role": "user", "content": prompt}],
                {"max_tokens": 120, "temperature": 0.3},
            )

            return response["response"]["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Explanation generation error: {e}")
            return f"Edge detected: {leg.ev_percent:.2f}% expected value vs market price."

    async def _get_parlay_explanation(self, parlay: ParlayData) -> str:
        """Get OpenAI explanation for parlay"""

        try:
            prompt = f"""
            Explain this parlay opportunity:

            Legs: {len(parlay.legs)}
            Combined Probability: {parlay.joint_probability:.1%}
            Parlay EV: {parlay.parlay_ev_percent:.2f}%
            Same Game: {parlay.is_sgp}

            Brief explanation under 100 words.
            """

            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [{"role": "user", "content": prompt}],
                {"max_tokens": 120, "temperature": 0.3},
            )

            return response["response"]["choices"][0]["message"]["content"]

        except Exception as e:
            logger.error(f"Parlay explanation error: {e}")
            return f"Parlay shows {parlay.parlay_ev_percent:.2f}% expected value with {len(parlay.legs)} legs."


# ==================== MAIN EXECUTION ====================


async def main():
    """Main betting math engine execution"""

    engine = EQ12BettingMathEngine()

    logger.info("🚀 EQ12 Betting Math Engine Started")
    logger.info("📊 Features:")
    logger.info("   - Deterministic EV calculations")
    logger.info("   - Parlay optimization with correlations")
    logger.info("   - Arbitrage & middle detection")
    logger.info("   - CLV tracking & team ratings")
    logger.info("   - PayPal/CashApp/Venmo integration")
    logger.info("💰 Revenue tiers: $29-299/month")
    logger.info("🎯 Math first, LLM explanations only")

    # Create and start FastAPI app
    app = engine.create_fastapi_app()

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)


if __name__ == "__main__":
    asyncio.run(main())
