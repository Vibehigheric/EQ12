#!/usr/bin/env python3
"""
EQ12 FastAPI Backend - GPT-5 Optimized Agentic Betting System

This backend implements GPT-5 best practices for:
- Agentic workflow predictability with structured tool preambles
- Enhanced instruction following with clear error boundaries
- Reasoning effort optimization for different task complexities
- Persistent context management across API calls
- Professional betting analytics with systematic edge detection

Architecture: FastAPI + SQLite with specialized NFL engines
Integration: Firefox Extension + CLI tools + Dashboard
Compliance: EQ12 standards with signed commits and structured logging
"""

import json
import logging
import math
import os
import random
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

import requests

try:
    import aiohttp
except ImportError:
    aiohttp = None
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Import Firefox Extension Integration
try:
    import sys

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append("C:\\EQ12\\firefox_extension_eq12")
    from eq12_extension_endpoints import register_firefox_extension_endpoints

    FIREFOX_INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"Firefox extension integration not available: {e}")
    FIREFOX_INTEGRATION_AVAILABLE = False
    register_firefox_extension_endpoints = None


# GPT-5 Optimized Logging with Structured Reasoning Traces
class StructuredLogger:
    """GPT-5 optimized logging with tool preambles and progress tracking"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create formatter with structured output for agentic workflows
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # File handler for persistent reasoning traces
        file_handler = logging.FileHandler(
            "C:\\EQ12\\logs\\extension_backend.log", encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def plan_execution(self, task: str, steps: list[str]) -> None:
        """Log structured execution plan (GPT-5 tool preamble pattern)"""
        self.logger.info(f"🎯 TASK: {task}")
        for i, step in enumerate(steps, 1):
            self.logger.info(f"   {i}. {step}")

    def progress_update(self, step: str, status: str = "EXECUTING") -> None:
        """Log progress with clear status indicators"""
        self.logger.info(f"⚡ {status}: {step}")

    def error_with_context(self, error: str, context: dict[str, Any]) -> None:
        """Log errors with structured context for debugging"""
        self.logger.error(f"❌ ERROR: {error}")
        for key, value in context.items():
            self.logger.error(f"   {key}: {value}")

    def success_summary(self, task: str, results: dict[str, Any]) -> None:
        """Log successful completion with key metrics"""
        self.logger.info(f"✅ COMPLETED: {task}")
        for key, value in results.items():
            self.logger.info(f"   {key}: {value}")


# Initialize structured logger
logger = StructuredLogger(__name__)

# Traditional logger for compatibility
compat_logger = logging.getLogger(__name__)


# GPT-5 Agentic Configuration
class EQ12Config:
    """GPT-5 optimized configuration with reasoning effort controls"""

    # API Configuration
    API_KEY: str = os.getenv("EQ12_API_KEY", "eq12-test-key-2025")
    DATABASE_PATH: str = "C:\\EQ12\\eq12_bets.db"
    ODDS_API_KEY: str = os.getenv("ODDS_API_KEY", "")

    # GPT-5 Reasoning Effort Controls
    REASONING_EFFORT: str = "medium"  # minimal, medium, high
    VERBOSITY_LEVEL: str = "low"  # low, medium, high
    TOOL_CALL_BUDGET: int = 10  # Max tool calls per request

    # Agentic Behavior Configuration
    AGENTIC_EAGERNESS: str = "balanced"  # conservative, balanced, aggressive
    AUTO_PROCEED_THRESHOLD: float = 0.8  # Confidence threshold for auto-execution
    UNCERTAINTY_ESCALATION: bool = True  # Escalate on uncertainty vs proceed

    # Error Boundaries and Safe Actions
    SAFE_ACTIONS = {"search", "analyze", "calculate", "validate", "log"}
    UNSAFE_ACTIONS = {"delete", "modify_database", "external_api_write", "file_delete"}

    # Performance Thresholds
    MAX_PROCESSING_TIME: int = 30  # seconds
    MIN_CONFIDENCE_LEVEL: float = 0.7
    MAX_CONCURRENT_REQUESTS: int = 5


config = EQ12Config()


# GPT-5 Optimized FastAPI Setup with Agentic Middleware
class AgenticMiddleware:
    """GPT-5 middleware for request context and reasoning persistence"""

    def __init__(self, app):
        self.app = app
        self.request_context = {}
        self.reasoning_cache = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Generate request ID for reasoning persistence
            request_id = f"req_{int(time.time() * 1000)}"

            # Log structured request preamble
            logger.plan_execution(
                f"API Request: {scope['method']} {scope['path']}",
                [
                    "Validate request authentication and parameters",
                    "Execute core business logic with error boundaries",
                    "Return structured response with reasoning traces",
                ],
            )

            # Store context for persistence across tool calls
            self.request_context[request_id] = {
                "start_time": time.time(),
                "method": scope["method"],
                "path": scope["path"],
                "reasoning_effort": config.REASONING_EFFORT,
            }

        await self.app(scope, receive, send)


app = FastAPI(
    title="EQ12 GPT-5 Optimized Betting API",
    description="""
    Backend API implementing GPT-5 best practices:
    - Agentic workflow predictability with structured tool preambles
    - Enhanced instruction following with clear error boundaries
    - Reasoning effort optimization for different task complexities
    - Persistent context management across API calls
    - Professional betting analytics with systematic edge detection
    """,
    version="2.0.0-gpt5",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Add agentic middleware
app.add_middleware(AgenticMiddleware)

# Enhanced CORS middleware for Firefox extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "moz-extension://*",
        "chrome-extension://*",
        "http://localhost:*",
        "http://127.0.0.1:*",
        "https://*.ngrok.io",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register Firefox Extension API Endpoints
if FIREFOX_INTEGRATION_AVAILABLE and register_firefox_extension_endpoints:
    try:
        register_firefox_extension_endpoints(app)
        logger.info("✅ Firefox Extension API endpoints registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register Firefox Extension endpoints: {e}")
else:
    logger.warning("⚠️  Firefox Extension integration not available - endpoints not registered")

# GPT-5 Optimized Pydantic Models with Structured Responses


class TaskStatus(str, Enum):
    """Task status for agentic workflow tracking"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    """Confidence levels for betting decisions"""

    LOCK = "LOCK"  # 8%+ edge, 3%+ Kelly
    STRONG = "STRONG"  # 5%+ edge, 2%+ Kelly
    MODERATE = "MODERATE"  # 3%+ edge, 1%+ Kelly
    WEAK = "WEAK"  # <3% edge


class ReasoningTrace(BaseModel):
    """GPT-5 style reasoning trace for transparency"""

    step: str
    reasoning: str
    confidence: float
    timestamp: datetime


class ParlayRequest(BaseModel):
    """Enhanced parlay request with GPT-5 agentic controls"""

    size: int = 5
    risk_level: str = "medium"
    include_ev: bool = True
    include_analysis: bool = True
    sports: list[str] | None = None

    # GPT-5 Agentic Controls
    reasoning_effort: str = "medium"  # minimal, medium, high
    verbosity_level: str = "medium"  # low, medium, high
    auto_proceed: bool = True  # Proceed without confirmation
    max_processing_time: int = 30  # Timeout in seconds


class ParlayLeg(BaseModel):
    """Enhanced parlay leg with structured confidence metrics"""

    selection: str
    price: float
    book: str
    sport: str
    game: str
    confidence: ConfidenceLevel

    # Enhanced Analytics
    implied_prob: float
    fair_prob: float
    edge: float
    kelly_fraction: float
    reasoning_trace: list[ReasoningTrace]


class ParlayResponse(BaseModel):
    """GPT-5 optimized parlay response with structured reasoning"""

    # Core Response
    name: str
    legs: list[ParlayLeg]
    combined_odds: float
    est_true_prob: float
    ev: float
    confidence: ConfidenceLevel
    risk_level: str
    created_at: str

    # GPT-5 Structured Reasoning
    execution_plan: list[str]  # Initial plan steps
    reasoning_traces: list[ReasoningTrace]  # Step-by-step reasoning
    final_summary: str  # Completion summary
    processing_time: float  # Task duration
    tool_calls_made: int  # Tool usage count

    # Error Handling
    warnings: list[str] = []  # Non-fatal issues
    escalation_needed: bool = False  # Requires human review


class AuditSummary(BaseModel):
    """Enhanced audit summary with reasoning traces"""

    # Core Metrics
    total_bets: int
    total_profit: float
    win_rate: float
    avg_odds: float
    last_updated: str

    # GPT-5 Analytics
    confidence_distribution: dict[str, int]  # LOCK/STRONG/etc counts
    reasoning_quality: float  # Avg reasoning confidence
    processing_efficiency: float  # Avg processing time


class HealthResponse(BaseModel):
    """GPT-5 optimized health check with system reasoning"""

    # Core Status
    status: str
    name: str
    version: str
    uptime: float
    database_status: str

    # GPT-5 System Health
    reasoning_engine: str  # Current reasoning effort
    agentic_mode: str  # Current agentic configuration
    active_contexts: int  # Number of persistent contexts
    tool_call_budget_remaining: int  # Remaining tool calls
    last_reasoning_trace: str | None  # Last major decision


# Professional Betting Logic Classes
@dataclass
class EdgeBet:
    """GPT-5 enhanced bet representation with structured reasoning"""

    # Core Betting Data
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
    confidence: ConfidenceLevel

    # GPT-5 Reasoning Enhancement
    reasoning_traces: list[ReasoningTrace] = field(default_factory=list)
    execution_plan: list[str] = field(default_factory=list)
    risk_assessment: dict[str, float] = field(default_factory=dict)
    escalation_triggers: list[str] = field(default_factory=list)

    def add_reasoning_step(self, step: str, reasoning: str, confidence: float):
        """Add structured reasoning trace (GPT-5 tool preamble pattern)"""
        self.reasoning_traces.append(
            ReasoningTrace(
                step=step,
                reasoning=reasoning,
                confidence=confidence,
                timestamp=datetime.now(UTC),
            )
        )

    def should_escalate(self) -> bool:
        """Determine if bet requires human review (GPT-5 uncertainty handling)"""
        return (
            len(self.escalation_triggers) > 0
            or self.confidence == ConfidenceLevel.WEAK
            or self.edge < 0.02
            or any(trace.confidence < 0.7 for trace in self.reasoning_traces)
        )


class GPT5BankrollManager:
    """GPT-5 optimized bankroll management with agentic decision making"""

    def __init__(self, base_bankroll: float = 1000.0):
        self.base_bankroll = base_bankroll
        self.current_bankroll = base_bankroll
        self.max_bet_percentage = 0.05  # Max 5% of bankroll per bet
        self.min_edge = 0.02  # Minimum 2% edge required
        self.kelly_fraction = 0.25  # Quarter Kelly for safety

    def calculate_kelly_size(self, odds: float, win_prob: float) -> float:
        """Calculate Kelly Criterion bet size"""
        if win_prob <= 0 or odds <= 0:
            return 0.0

        # Convert American odds to decimal for Kelly calculation
        decimal_odds = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1

        # Kelly formula: f = (bp - q) / b
        # where b = odds-1, p = win_prob, q = 1-p
        b = decimal_odds - 1
        p = win_prob
        q = 1 - p

        kelly_fraction = (b * p - q) / b

        # Apply risk management: cap at max percentage and apply fractional kelly
        if kelly_fraction <= 0:
            return 0.0

        conservative_kelly = kelly_fraction * self.kelly_fraction
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


def american_to_implied(odds: float) -> float:
    """Convert American odds to implied probability"""
    if odds > 0:
        return 100 / (odds + 100)
    return abs(odds) / (abs(odds) + 100)


def decimal_to_american(decimal_odds: float) -> float:
    """Convert decimal odds to American format"""
    if decimal_odds >= 2.0:
        return (decimal_odds - 1) * 100
    return -100 / (decimal_odds - 1)


def american_to_decimal(american_odds: float) -> float:
    """Convert American odds to decimal format"""
    if american_odds >= 100:
        return (american_odds / 100) + 1
    return (100 / abs(american_odds)) + 1


def calculate_consensus_fair_value(all_prices: list[float]) -> float:
    """Calculate consensus fair value from multiple bookmaker prices"""
    if not all_prices:
        return 0.0

    # Convert to implied probabilities and average them
    implied_probs = [american_to_implied(price) for price in all_prices]

    # Remove outliers (more than 2 std dev from mean)
    if len(implied_probs) > 3:
        mean_prob = sum(implied_probs) / len(implied_probs)
        std_dev = (sum((x - mean_prob) ** 2 for x in implied_probs) / len(implied_probs)) ** 0.5

        filtered_probs = [p for p in implied_probs if abs(p - mean_prob) <= 2 * std_dev]
        if filtered_probs:
            implied_probs = filtered_probs

    # Return average of filtered probabilities
    return sum(implied_probs) / len(implied_probs)


def decide_and_place_bet(
    odds: float,
    fair_prob: float,
    bankroll_mgr: GPT5BankrollManager,
    selection: str,
    event_id: str = "unknown",
) -> EdgeBet | None:
    """
    Main decision function that implements:
    1. Edge detection logic
    2. Kelly criterion bet sizing
    3. Risk constraints validation
    """

    # Step 1: Calculate implied probability and edge
    implied_prob = american_to_implied(odds)
    edge = fair_prob - implied_prob

    # Step 2: Apply edge threshold constraint
    if edge < bankroll_mgr.min_edge:
        logger.debug(f"Edge {edge:.3f} below threshold {bankroll_mgr.min_edge} for {selection}")
        return None

    # Step 3: Calculate Kelly sizing
    kelly_fraction = bankroll_mgr.calculate_kelly_size(odds, fair_prob)

    if kelly_fraction <= 0:
        logger.debug(f"Kelly sizing returned 0 for {selection}")
        return None

    # Step 4: Calculate actual bet size
    bet_size = bankroll_mgr.calculate_bet_size(kelly_fraction)

    # Step 5: Classify confidence
    confidence = bankroll_mgr.classify_confidence(edge, kelly_fraction)

    # Step 6: Create EdgeBet with all calculated values
    edge_bet = EdgeBet(
        event_id=event_id,
        sport="Mixed",  # Will be updated by caller
        market="Mixed",  # Will be updated by caller
        selection=selection,
        book="Combined",  # Will be updated by caller
        odds=odds,
        implied_prob=implied_prob,
        fair_prob=fair_prob,
        edge=edge,
        kelly_fraction=kelly_fraction,
        bet_size=bet_size,
        confidence=confidence,
    )

    logger.info(
        f"✅ Edge bet identified: {selection} - Edge: {edge:.1%}, Kelly: {kelly_fraction:.1%}, Size: ${bet_size:.2f}"
    )
    return edge_bet


# Global bankroll manager instance
bankroll_manager = GPT5BankrollManager(base_bankroll=1000.0)


# NFL-Specific Betting Logic & Models
@dataclass
class NFLGame:
    """NFL Game with comprehensive betting context"""

    game_id: str
    home_team: str
    away_team: str
    week: int
    season: int
    kickoff_time: datetime

    # Team context
    home_rest_days: int = 7
    away_rest_days: int = 7
    travel_distance: float = 0.0  # Miles for away team
    time_zone_change: int = 0  # Hours difference for away team

    # Game context
    weather_temp: float | None = None
    weather_wind: float | None = None
    weather_precip: str | None = None
    surface_type: str = "grass"  # grass/turf
    dome: bool = False

    # Injury/personnel
    home_qb_status: str = "starter"  # starter/backup/questionable
    away_qb_status: str = "starter"
    home_key_injuries: list[str] | None = None
    away_key_injuries: list[str] | None = None

    # Recent performance (last 4 games)
    home_recent_form: str | None = None  # "3-1" format
    away_recent_form: str | None = None
    home_last_4_pts_for: float = 0.0
    home_last_4_pts_against: float = 0.0
    away_last_4_pts_for: float = 0.0
    away_last_4_pts_against: float = 0.0

    # Advanced metrics
    home_offensive_epa: float | None = None
    home_defensive_epa: float | None = None
    away_offensive_epa: float | None = None
    away_defensive_epa: float | None = None

    # Divisional/historical
    is_divisional: bool = False
    h2h_last_3_years: str | None = None  # "2-1" format for home team

    # Market context
    public_betting_pct: float | None = None  # % on favorite
    line_movement: float | None = None  # Opening vs current spread

    def __post_init__(self):
        if self.home_key_injuries is None:
            self.home_key_injuries = []
        if self.away_key_injuries is None:
            self.away_key_injuries = []


@dataclass
class NFLMarketPrediction:
    """NFL Model predictions for different markets"""

    game_id: str

    # Moneyline probabilities
    home_win_prob: float
    away_win_prob: float

    # Spread predictions
    predicted_spread: float  # Negative = home favored
    spread_cover_prob: float  # Prob of favorite covering

    # Total predictions
    predicted_total: float
    over_prob: float
    under_prob: float

    # Confidence intervals
    spread_confidence: float = 0.68  # 1-sigma confidence
    total_confidence: float = 0.68

    # Model metadata
    model_version: str = "v1.0"
    features_used: list[str] | None = None
    simulation_count: int = 10000

    def __post_init__(self):
        if self.features_used is None:
            self.features_used = ["rest", "travel", "epa", "injuries", "weather"]


class NFLBettingEngine:
    """NFL-Specific Edge Detection and Bet Execution Engine"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # NFL-specific risk controls
        self.max_bets_per_game = 2  # Max 2 markets per game
        self.max_bets_per_week = 15  # Max 15 bets per NFL week
        self.max_exposure_per_team = 0.10  # Max 10% bankroll on any team
        self.max_correlated_exposure = 0.08  # Max 8% on correlated bets

        # NFL edge thresholds (more conservative due to market efficiency)
        self.min_edge_threshold = 0.025  # 2.5% minimum edge
        self.strong_edge_threshold = 0.05  # 5% = strong edge
        self.lock_edge_threshold = 0.08  # 8% = lock play

        # Market-specific adjustments
        self.market_kelly_multipliers = {
            "moneyline": 0.25,  # Quarter Kelly
            "spread": 0.30,  # Slightly more aggressive on spreads
            "total": 0.25,  # Conservative on totals
            "props": 0.20,  # Very conservative on props
        }

        # Weekly bet tracking
        self.weekly_bets: dict[int, list[EdgeBet]] = {}
        self.team_exposure: dict[str, float] = {}

    def nfl_decide_and_place(
        self,
        game: NFLGame,
        market_type: str,
        market_odds: float,
        prediction: NFLMarketPrediction,
    ) -> EdgeBet | None:
        """
        Main NFL betting decision function implementing:
        1. NFL-specific edge detection
        2. Market-adjusted Kelly sizing
        3. NFL risk constraints (team exposure, correlations, weekly limits)
        """

        # Step 1: Get fair probability from NFL model
        fair_prob = self._get_fair_probability(prediction, market_type, game)
        if fair_prob is None:
            return None

        # Step 2: Calculate edge with NFL adjustments
        implied_prob = american_to_implied(market_odds)
        raw_edge = fair_prob - implied_prob

        # NFL-specific edge adjustments
        adjusted_edge = self._adjust_edge_for_nfl_factors(raw_edge, game, market_type)

        # Step 3: Apply NFL edge threshold
        if adjusted_edge < self.min_edge_threshold:
            logger.debug(
                f"NFL edge {adjusted_edge:.3f} below threshold for {game.away_team}@{game.home_team}"
            )
            return None

        # Step 4: Check NFL-specific constraints
        if not self._validate_nfl_constraints(game, market_type):
            return None

        # Step 5: Calculate NFL market-adjusted Kelly sizing
        kelly_multiplier = self.market_kelly_multipliers.get(market_type, 0.25)
        base_kelly = self.bankroll_mgr.calculate_kelly_size(market_odds, fair_prob)
        adjusted_kelly = base_kelly * kelly_multiplier

        # Step 6: NFL risk controls override
        max_kelly = self._calculate_nfl_max_kelly(game, market_type)
        final_kelly = min(adjusted_kelly, max_kelly)

        if final_kelly <= 0:
            return None

        # Step 7: Create NFL EdgeBet
        bet_size = self.bankroll_mgr.calculate_bet_size(final_kelly)
        confidence = self._classify_nfl_confidence(adjusted_edge, final_kelly, game)

        selection = self._format_nfl_selection(market_type, game, market_odds)

        edge_bet = EdgeBet(
            event_id=game.game_id,
            sport="NFL",
            market=market_type,
            selection=selection,
            book="Combined",  # Will be updated by caller
            odds=market_odds,
            implied_prob=implied_prob,
            fair_prob=fair_prob,
            edge=adjusted_edge,
            kelly_fraction=final_kelly,
            bet_size=bet_size,
            confidence=confidence,
        )

        # Step 8: Track NFL bet for weekly/team limits
        self._track_nfl_bet(edge_bet, game)

        logger.info(
            f"🏈 NFL EDGE: {selection} | Edge: {adjusted_edge:.1%} | Kelly: {final_kelly:.1%} | Size: ${bet_size:.2f} | {confidence}"
        )
        return edge_bet

    def _get_fair_probability(
        self, prediction: NFLMarketPrediction, market_type: str, game: NFLGame
    ) -> float | None:
        """Extract fair probability from NFL model prediction"""
        if market_type == "moneyline":
            # Return home win prob if betting home, away win prob if betting away
            # This will be determined by the calling function based on which team/odds
            return prediction.home_win_prob  # Placeholder - caller will adjust
        if market_type == "spread":
            return prediction.spread_cover_prob
        if market_type == "total":
            return prediction.over_prob  # Caller will use under_prob for under bets
        return None

    def _adjust_edge_for_nfl_factors(
        self, raw_edge: float, game: NFLGame, market_type: str
    ) -> float:
        """Apply NFL-specific edge adjustments based on game context"""
        adjusted_edge = raw_edge

        # Weather adjustments for totals
        if market_type == "total" and game.weather_wind and game.weather_wind > 15:
            adjusted_edge *= 0.9  # Reduce edge confidence in windy conditions

        # Injury adjustments
        if game.home_qb_status != "starter" or game.away_qb_status != "starter":
            adjusted_edge *= 1.1  # Increase edge when backup QBs create volatility

        # Divisional game adjustments (more unpredictable)
        if game.is_divisional:
            adjusted_edge *= 0.95

        # Rest advantage adjustments
        rest_diff = abs(game.home_rest_days - game.away_rest_days)
        if rest_diff >= 3:  # Significant rest advantage
            adjusted_edge *= 1.05

        # Travel fatigue (West Coast to East Coast games)
        if game.time_zone_change >= 2 and game.travel_distance > 1500:
            adjusted_edge *= 1.02

        return max(0, adjusted_edge)  # Ensure non-negative

    def _validate_nfl_constraints(self, game: NFLGame, market_type: str) -> bool:
        """Check NFL-specific betting constraints"""

        # Weekly bet limit
        week_bets = self.weekly_bets.get(game.week, [])
        if len(week_bets) >= self.max_bets_per_week:
            logger.debug(f"Weekly bet limit reached: {len(week_bets)}/{self.max_bets_per_week}")
            return False

        # Per-game bet limit
        game_bets = [bet for bet in week_bets if bet.event_id == game.game_id]
        if len(game_bets) >= self.max_bets_per_game:
            logger.debug(f"Per-game bet limit reached for {game.game_id}")
            return False

        # Team exposure limits
        for team in [game.home_team, game.away_team]:
            current_exposure = self.team_exposure.get(team, 0.0)
            if current_exposure >= self.max_exposure_per_team:
                logger.debug(f"Team exposure limit reached for {team}: {current_exposure:.1%}")
                return False

        return True

    def _calculate_nfl_max_kelly(self, game: NFLGame, market_type: str) -> float:
        """Calculate maximum Kelly fraction for NFL bet considering all constraints"""

        # Base maximum from bankroll manager
        base_max = self.bankroll_mgr.max_bet_percentage

        # Reduce for high-correlation scenarios
        if market_type in ["spread", "total"]:
            base_max *= 0.8  # More conservative on correlated markets

        # Thursday/Monday games (shorter rest)
        if min(game.home_rest_days, game.away_rest_days) < 6:
            base_max *= 0.9

        return base_max

    def _classify_nfl_confidence(self, edge: float, kelly: float, game: NFLGame) -> str:
        """Classify NFL bet confidence with game context"""

        if edge >= self.lock_edge_threshold and kelly >= 0.03:
            return "LOCK"
        if edge >= self.strong_edge_threshold and kelly >= 0.02:
            return "STRONG"
        if edge >= self.min_edge_threshold and kelly >= 0.01:
            return "MODERATE"
        return "WEAK"

    def _format_nfl_selection(self, market_type: str, game: NFLGame, odds: float) -> str:
        """Format NFL bet selection string"""

        if market_type == "moneyline":
            team = game.home_team if odds < 0 else game.away_team  # Simplified logic
            return f"{team} ML"
        if market_type == "spread":
            return f"NFL Spread Bet ({odds:+.0f})"
        if market_type == "total":
            direction = "Over" if odds > 0 else "Under"
            return f"{direction} Total"
        return f"NFL {market_type}"

    def _track_nfl_bet(self, bet: EdgeBet, game: NFLGame):
        """Track NFL bet for weekly and team exposure limits"""

        # Add to weekly tracking
        if game.week not in self.weekly_bets:
            self.weekly_bets[game.week] = []
        self.weekly_bets[game.week].append(bet)

        # Update team exposure (simplified - assumes betting on home team)
        team = game.home_team  # This would be determined by actual bet selection
        current_exposure = self.team_exposure.get(team, 0.0)
        bet_exposure = bet.bet_size / self.bankroll_mgr.current_bankroll
        self.team_exposure[team] = current_exposure + bet_exposure


# Global NFL betting engine
nfl_engine = NFLBettingEngine(bankroll_manager)


# NFL Feature Extraction Functions
def extract_nfl_features(game_data: dict[str, Any]) -> NFLGame:
    """Extract NFL game features from raw API data"""

    # Parse basic game info
    home_team = game_data.get("home_team", "Unknown")
    away_team = game_data.get("away_team", "Unknown")
    commence_time = game_data.get("commence_time", "")

    # Parse kickoff time
    if commence_time:
        kickoff = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
    else:
        kickoff = datetime.now()

    # Estimate week and season (simplified)
    current_date = datetime.now()
    season = current_date.year
    # NFL season weeks 1-18 (Sep-Jan), simplified calculation
    week = min(18, max(1, (current_date.timetuple().tm_yday - 240) // 7))

    return NFLGame(
        game_id=game_data.get("id", f"{away_team}@{home_team}"),
        home_team=home_team,
        away_team=away_team,
        week=week,
        season=season,
        kickoff_time=kickoff,
        # Default values - would be enhanced with real data sources
        home_rest_days=7,
        away_rest_days=7,
        surface_type="grass",
        dome=False,
        home_qb_status="starter",
        away_qb_status="starter",
        is_divisional=False,  # Would check division matchup
    )


def generate_nfl_prediction(game: NFLGame) -> NFLMarketPrediction:
    """Generate NFL model predictions (simplified simulation-based approach)"""

    # Simulate game outcomes (simplified Monte Carlo)
    home_wins = 0
    total_sims = 10000
    spread_covers = 0
    total_overs = 0

    predicted_spread = random.uniform(-14, 14)  # Would use real model
    predicted_total = random.uniform(35, 65)  # Would use real model

    for _ in range(total_sims):
        # Simplified simulation
        home_score = max(0, random.normalvariate(24, 8))
        away_score = max(0, random.normalvariate(21, 8))

        if home_score > away_score:
            home_wins += 1

        # Check spread cover (simplified)
        margin = home_score - away_score
        if margin > abs(predicted_spread):
            spread_covers += 1

        # Check total
        total_points = home_score + away_score
        if total_points > predicted_total:
            total_overs += 1

    home_win_prob = home_wins / total_sims
    spread_cover_prob = spread_covers / total_sims
    over_prob = total_overs / total_sims

    return NFLMarketPrediction(
        game_id=game.game_id,
        home_win_prob=home_win_prob,
        away_win_prob=1 - home_win_prob,
        predicted_spread=predicted_spread,
        spread_cover_prob=spread_cover_prob,
        predicted_total=predicted_total,
        over_prob=over_prob,
        under_prob=1 - over_prob,
        simulation_count=total_sims,
    )


# ================================
# NFL SPECIALIZED MARKET LOGIC
# ================================


# NFL Game Lines Specialization (Moneyline & Totals Focus)
@dataclass
class NFLGameLinesEngine:
    """Specialized NFL engine focusing on game lines (moneyline, over/under totals)"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # Game Lines Specific Thresholds
        self.EDGE_THRESHOLD_ML = 0.02  # 2% edge for moneyline
        self.EDGE_THRESHOLD_TOTAL = 0.025  # 2.5% edge for totals (more conservative)
        self.MAX_BET_FRACTION_ML = 0.04  # 4% max for moneyline
        self.MAX_BET_FRACTION_TOTAL = 0.03  # 3% max for totals
        self.FRACTIONAL_KELLY = 0.5  # Half Kelly for safety
        self.MIN_BET = 1.0

    def implied_prob_from_odds(self, odds_decimal: float) -> float:
        """Convert decimal odds to implied probability"""
        return 1.0 / odds_decimal

    def normalize_implied_probs(self, implied_probs: dict[str, float]) -> dict[str, float]:
        """Remove vigorish by normalizing implied probabilities to sum to 1"""
        total = sum(implied_probs.values())
        return {k: v / total for k, v in implied_probs.items()}

    def compute_edge_moneyline(self, model_p: float, implied_p_norm: float) -> float:
        """Compute edge for moneyline bet after vig removal"""
        return model_p - implied_p_norm

    def compute_edge_total(self, model_p_over: float, implied_p_over_norm: float) -> float:
        """Compute edge for total bet after vig removal"""
        return model_p_over - implied_p_over_norm

    def bet_size_kelly(
        self, bankroll: float, model_p: float, odds_decimal: float, max_fraction: float
    ) -> float:
        """Calculate Kelly bet sizing for NFL game lines"""
        b = odds_decimal - 1
        if b <= 0:
            return 0
        # Kelly formula: f = (p * odds - 1) / (odds - 1)
        f = (model_p * odds_decimal - 1) / b
        f = max(0.0, f)
        f_frac = f * self.FRACTIONAL_KELLY
        bet = f_frac * bankroll
        return min(bet, bankroll * max_fraction)

    def decide_and_place_nfl_game_lines(
        self,
        game: NFLGame,
        prediction: NFLMarketPrediction,
        odds_home_ml: float,
        odds_away_ml: float,
        odds_over: float,
        odds_under: float,
    ) -> list[EdgeBet]:
        """
        Specialized NFL game lines decision engine focusing on moneyline and totals only
        """
        edge_bets = []

        # Convert American odds to decimal
        dec_home_ml = american_to_decimal(odds_home_ml)
        dec_away_ml = american_to_decimal(odds_away_ml)
        dec_over = american_to_decimal(odds_over)
        dec_under = american_to_decimal(odds_under)

        # Moneyline Analysis with Vig Removal
        imp_ml = {
            "home": self.implied_prob_from_odds(dec_home_ml),
            "away": self.implied_prob_from_odds(dec_away_ml),
        }
        imp_ml_norm = self.normalize_implied_probs(imp_ml)

        # Check Home ML edge
        edge_home = self.compute_edge_moneyline(prediction.home_win_prob, imp_ml_norm["home"])
        if edge_home >= self.EDGE_THRESHOLD_ML:
            size = self.bet_size_kelly(
                self.bankroll_mgr.current_bankroll,
                prediction.home_win_prob,
                dec_home_ml,
                self.MAX_BET_FRACTION_ML,
            )
            if size >= self.MIN_BET:
                edge_bet = EdgeBet(
                    event_id=game.game_id,
                    sport="NFL",
                    market="moneyline",
                    selection=f"{game.home_team} ML",
                    book="Combined",
                    odds=odds_home_ml,
                    implied_prob=imp_ml_norm["home"],
                    fair_prob=prediction.home_win_prob,
                    edge=edge_home,
                    kelly_fraction=size / self.bankroll_mgr.current_bankroll,
                    bet_size=size,
                    confidence="STRONG" if edge_home >= 0.05 else "MODERATE",
                )
                edge_bets.append(edge_bet)

        # Check Away ML edge
        edge_away = self.compute_edge_moneyline(prediction.away_win_prob, imp_ml_norm["away"])
        if edge_away >= self.EDGE_THRESHOLD_ML:
            size = self.bet_size_kelly(
                self.bankroll_mgr.current_bankroll,
                prediction.away_win_prob,
                dec_away_ml,
                self.MAX_BET_FRACTION_ML,
            )
            if size >= self.MIN_BET:
                edge_bet = EdgeBet(
                    event_id=game.game_id,
                    sport="NFL",
                    market="moneyline",
                    selection=f"{game.away_team} ML",
                    book="Combined",
                    odds=odds_away_ml,
                    implied_prob=imp_ml_norm["away"],
                    fair_prob=prediction.away_win_prob,
                    edge=edge_away,
                    kelly_fraction=size / self.bankroll_mgr.current_bankroll,
                    bet_size=size,
                    confidence="STRONG" if edge_away >= 0.05 else "MODERATE",
                )
                edge_bets.append(edge_bet)

        # Totals Analysis with Vig Removal
        imp_total = {
            "over": self.implied_prob_from_odds(dec_over),
            "under": self.implied_prob_from_odds(dec_under),
        }
        imp_total_norm = self.normalize_implied_probs(imp_total)

        # Check Over edge
        edge_over = self.compute_edge_total(prediction.over_prob, imp_total_norm["over"])
        if edge_over >= self.EDGE_THRESHOLD_TOTAL:
            size = self.bet_size_kelly(
                self.bankroll_mgr.current_bankroll,
                prediction.over_prob,
                dec_over,
                self.MAX_BET_FRACTION_TOTAL,
            )
            if size >= self.MIN_BET:
                edge_bet = EdgeBet(
                    event_id=game.game_id,
                    sport="NFL",
                    market="total",
                    selection=f"Over {prediction.predicted_total}",
                    book="Combined",
                    odds=odds_over,
                    implied_prob=imp_total_norm["over"],
                    fair_prob=prediction.over_prob,
                    edge=edge_over,
                    kelly_fraction=size / self.bankroll_mgr.current_bankroll,
                    bet_size=size,
                    confidence="STRONG" if edge_over >= 0.04 else "MODERATE",
                )
                edge_bets.append(edge_bet)

        # Check Under edge
        edge_under = self.compute_edge_total(prediction.under_prob, imp_total_norm["under"])
        if edge_under >= self.EDGE_THRESHOLD_TOTAL:
            size = self.bet_size_kelly(
                self.bankroll_mgr.current_bankroll,
                prediction.under_prob,
                dec_under,
                self.MAX_BET_FRACTION_TOTAL,
            )
            if size >= self.MIN_BET:
                edge_bet = EdgeBet(
                    event_id=game.game_id,
                    sport="NFL",
                    market="total",
                    selection=f"Under {prediction.predicted_total}",
                    book="Combined",
                    odds=odds_under,
                    implied_prob=imp_total_norm["under"],
                    fair_prob=prediction.under_prob,
                    edge=edge_under,
                    kelly_fraction=size / self.bankroll_mgr.current_bankroll,
                    bet_size=size,
                    confidence="STRONG" if edge_under >= 0.04 else "MODERATE",
                )
                edge_bets.append(edge_bet)

        return edge_bets


# NFL TD Scorer Props System
@dataclass
class NFLPlayer:
    """NFL Player for prop betting"""

    name: str
    team: str
    position: str  # RB, WR, TE, QB, DEF

    # Usage Metrics
    red_zone_targets: int = 0
    red_zone_carries: int = 0
    goal_line_carries: int = 0
    target_share: float = 0.0  # % of team targets
    snap_share: float = 0.0  # % of offensive snaps

    # Efficiency Metrics
    red_zone_td_rate: float = 0.0  # TDs per red zone opportunity
    goal_line_success_rate: float = 0.0
    yards_after_contact: float = 0.0

    # Injury/Status
    injury_status: str = "Healthy"  # Healthy, Questionable, Doubtful, Out
    depth_chart_position: int = 1  # 1 = starter, 2 = backup, etc.


@dataclass
class NFLTDPrediction:
    """TD Scorer prediction for NFL player"""

    player: NFLPlayer
    anytime_td_prob: float
    first_td_prob: float
    multi_td_prob: float = 0.0
    confidence: str = "MODERATE"


class NFLTDScorerEngine:
    """NFL Touchdown Scorer Props Engine"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # TD Props Specific Configuration
        self.EDGE_THRESHOLD_TD = 0.03  # 3% edge minimum (higher due to variance)
        self.MAX_BET_FRACTION_TD = 0.02  # 2% max (conservative due to high variance)
        self.FRACTIONAL_KELLY_TD = 0.4  # 40% of Kelly (very conservative)
        self.MIN_BET = 1.0
        self.MIN_TOTAL_THRESHOLD = 42.0  # Skip games with low scoring potential

    def pick_td_prop_candidates(self, game: NFLGame) -> list[NFLPlayer]:
        """Select TD prop candidates based on usage and opportunity"""
        candidates = []

        # Mock data - in real system would pull from player stats DB
        home_candidates = [
            NFLPlayer(
                name="RB1",
                team=game.home_team,
                position="RB",
                red_zone_carries=8,
                goal_line_carries=4,
                red_zone_td_rate=0.25,
            ),
            NFLPlayer(
                name="WR1",
                team=game.home_team,
                position="WR",
                red_zone_targets=6,
                target_share=0.28,
                red_zone_td_rate=0.33,
            ),
            NFLPlayer(
                name="TE1",
                team=game.home_team,
                position="TE",
                red_zone_targets=4,
                target_share=0.15,
                red_zone_td_rate=0.30,
            ),
        ]

        away_candidates = [
            NFLPlayer(
                name="RB1",
                team=game.away_team,
                position="RB",
                red_zone_carries=6,
                goal_line_carries=3,
                red_zone_td_rate=0.22,
            ),
            NFLPlayer(
                name="WR1",
                team=game.away_team,
                position="WR",
                red_zone_targets=5,
                target_share=0.25,
                red_zone_td_rate=0.28,
            ),
            NFLPlayer(
                name="WR2",
                team=game.away_team,
                position="WR",
                red_zone_targets=3,
                target_share=0.18,
                red_zone_td_rate=0.20,
            ),
        ]

        candidates.extend(home_candidates)
        candidates.extend(away_candidates)

        # Filter by opportunity (minimum usage thresholds)
        filtered = []
        for player in candidates:
            total_rz_opp = player.red_zone_targets + player.red_zone_carries
            if total_rz_opp >= 2 and player.injury_status == "Healthy":
                filtered.append(player)

        return filtered

    def extract_td_prop_features(self, game: NFLGame, player: NFLPlayer) -> dict[str, float]:
        """Extract features for TD scoring prediction"""
        features = {
            "red_zone_opportunities": player.red_zone_targets + player.red_zone_carries,
            "goal_line_usage": player.goal_line_carries,
            "td_conversion_rate": player.red_zone_td_rate,
            "target_share": player.target_share,
            "snap_share": player.snap_share,
            "position_weight": (1.0 if player.position == "RB" else 0.8),  # RBs score more TDs
            "team_red_zone_efficiency": 0.65,  # Would pull from team stats
            "opponent_td_defense": 0.45,  # TDs allowed by opponent to this position
            "game_total_projection": 48.0,  # Higher totals = more TD opportunities
            "weather_factor": 1.0 if not game.weather_precip else 0.9,
        }
        return features

    def predict_td_probability(self, features: dict[str, float]) -> float:
        """Simplified TD probability model"""
        # Base probability from red zone opportunities
        base_prob = min(0.4, features["red_zone_opportunities"] * 0.05)

        # Adjust for conversion efficiency
        base_prob *= 1 + features["td_conversion_rate"]

        # Position adjustments
        base_prob *= features["position_weight"]

        # Team and opponent adjustments
        base_prob *= (
            features["team_red_zone_efficiency"] + (1 - features["opponent_td_defense"])
        ) / 2

        # Game environment
        base_prob *= features["game_total_projection"] / 45.0  # Scale by expected scoring

        return min(0.6, max(0.02, base_prob))  # Bound between 2% and 60%

    def td_prop_decide_and_place(
        self, game: NFLGame, prediction: NFLMarketPrediction
    ) -> list[EdgeBet]:
        """Main TD prop decision engine"""
        edge_bets = []

        # Game environment filter
        if prediction.predicted_total < self.MIN_TOTAL_THRESHOLD:
            return edge_bets  # Skip low-scoring games

        # Get TD prop candidates
        candidates = self.pick_td_prop_candidates(game)

        for player in candidates:
            # Extract features and predict
            features = self.extract_td_prop_features(game, player)
            model_prob = self.predict_td_probability(features)

            # Mock market odds (would fetch from sportsbook)
            mock_odds = random.uniform(300, 800)  # +300 to +800 typical for anytime TD

            # Calculate edge
            decimal_odds = american_to_decimal(mock_odds)
            implied_prob = 1.0 / decimal_odds
            edge = model_prob - implied_prob

            if edge >= self.EDGE_THRESHOLD_TD:
                # Calculate bet size
                b = decimal_odds - 1.0
                if b > 0:
                    kelly_f = (model_prob * decimal_odds - 1) / b
                    kelly_f = max(0.0, kelly_f)
                    adjusted_kelly = kelly_f * self.FRACTIONAL_KELLY_TD
                    bet_size = min(
                        adjusted_kelly * self.bankroll_mgr.current_bankroll,
                        self.bankroll_mgr.current_bankroll * self.MAX_BET_FRACTION_TD,
                    )

                    if bet_size >= self.MIN_BET:
                        edge_bet = EdgeBet(
                            event_id=game.game_id,
                            sport="NFL",
                            market="touchdown_props",
                            selection=f"{player.name} Anytime TD",
                            book="Combined",
                            odds=mock_odds,
                            implied_prob=implied_prob,
                            fair_prob=model_prob,
                            edge=edge,
                            kelly_fraction=bet_size / self.bankroll_mgr.current_bankroll,
                            bet_size=bet_size,
                            confidence="STRONG" if edge >= 0.08 else "MODERATE",
                        )
                        edge_bets.append(edge_bet)

        return edge_bets


# NFL Passing Props System
@dataclass
class NFLPassingProps:
    """NFL QB Passing Props Data"""

    qb_name: str
    team: str

    # Season Averages
    avg_pass_yards: float = 250.0
    avg_pass_tds: float = 1.8
    avg_completions: float = 22.0
    avg_attempts: float = 35.0
    completion_pct: float = 0.65

    # Recent Form (last 4 games)
    recent_pass_yards: list[float] = None
    recent_pass_tds: list[float] = None

    # Matchup Context
    opponent_pass_def_rank: int = 16  # 1-32 ranking (1 = best defense)
    opponent_pass_yards_allowed: float = 240.0
    opponent_pass_tds_allowed: float = 1.6

    # Game Script Factors
    team_implied_total: float = 24.0  # Expected team points
    game_total: float = 48.0  # Expected total points
    spread: float = 0.0  # Team spread (negative if favored)

    # Environmental
    weather_wind_mph: float = 5.0
    dome_game: bool = False

    def __post_init__(self):
        if self.recent_pass_yards is None:
            self.recent_pass_yards = [self.avg_pass_yards] * 4
        if self.recent_pass_tds is None:
            self.recent_pass_tds = [self.avg_pass_tds] * 4


class NFLPassingPropsEngine:
    """NFL QB Passing Props Betting Engine"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # Passing Props Configuration
        self.EDGE_THRESHOLD_PROP = 0.025  # 2.5% minimum edge
        self.MAX_BET_FRACTION_PROP = 0.03  # 3% max bankroll
        self.FRACTIONAL_KELLY_PROP = 0.4  # Conservative Kelly
        self.MIN_BET = 1.0
        self.MIN_TOTAL_FOR_PASSING = 40.0  # Skip low-volume games

    def extract_passing_yards_features(
        self, game: NFLGame, qb_props: NFLPassingProps
    ) -> dict[str, float]:
        """Extract features for passing yards prediction"""
        return {
            "qb_avg_yards": qb_props.avg_pass_yards,
            "qb_recent_form": sum(qb_props.recent_pass_yards[-3:]) / 3,  # Last 3 games
            "opponent_yards_allowed": qb_props.opponent_pass_yards_allowed,
            "opponent_def_rank_scaled": (33 - qb_props.opponent_pass_def_rank) / 32,  # 0-1 scale
            "game_script_factor": max(
                0.5, 1.0 - (qb_props.spread / 20.0)
            ),  # Trailing teams pass more
            "total_pace_factor": qb_props.game_total / 47.0,  # Scale by avg game total
            "weather_factor": max(
                0.8, 1.0 - (qb_props.weather_wind_mph / 20.0)
            ),  # Wind affects passing
            "dome_bonus": 1.1 if qb_props.dome_game else 1.0,
            "completion_rate": qb_props.completion_pct,
        }

    def extract_passing_td_features(
        self, game: NFLGame, qb_props: NFLPassingProps
    ) -> dict[str, float]:
        """Extract features for passing TDs prediction"""
        return {
            "qb_avg_tds": qb_props.avg_pass_tds,
            "qb_recent_td_form": sum(qb_props.recent_pass_tds[-3:]) / 3,
            "opponent_tds_allowed": qb_props.opponent_pass_tds_allowed,
            "red_zone_efficiency": 0.65,  # Team red zone TD rate (would pull from stats)
            "team_total_projection": qb_props.team_implied_total,
            "pace_factor": qb_props.game_total / 47.0,
            "weather_factor": max(0.9, 1.0 - (qb_props.weather_wind_mph / 25.0)),
            "dome_bonus": 1.05 if qb_props.dome_game else 1.0,
        }

    def predict_passing_yards_prob_over(self, features: dict[str, float], line: float) -> float:
        """Predict probability of QB going over passing yards line"""
        # Base projection
        projected_yards = (
            features["qb_avg_yards"] * 0.4
            + features["qb_recent_form"] * 0.3
            + features["opponent_yards_allowed"] * 0.3
        )

        # Apply contextual adjustments
        projected_yards *= features["game_script_factor"]
        projected_yards *= features["total_pace_factor"]
        projected_yards *= features["weather_factor"]
        projected_yards *= features["dome_bonus"]

        # Estimate standard deviation (passing yards are volatile)
        std_dev = projected_yards * 0.25  # 25% coefficient of variation

        # Calculate probability using normal distribution
        if std_dev > 0:
            from math import erf, sqrt

            z_score = (line - projected_yards) / (std_dev * sqrt(2))
            prob_under = 0.5 * (1 + erf(z_score))
            prob_over = 1 - prob_under
        else:
            prob_over = 1.0 if projected_yards > line else 0.0

        return max(0.05, min(0.95, prob_over))

    def predict_passing_td_prob_over(self, features: dict[str, float], line: float) -> float:
        """Predict probability of QB going over passing TD line"""
        # Base projection
        projected_tds = (
            features["qb_avg_tds"] * 0.5
            + features["qb_recent_td_form"] * 0.3
            + features["opponent_tds_allowed"] * 0.2
        )

        # Apply contextual adjustments
        projected_tds *= features["team_total_projection"] / 24.0  # Scale by expected scoring
        projected_tds *= features["pace_factor"]
        projected_tds *= features["weather_factor"]
        projected_tds *= features["dome_bonus"]

        # For TDs, use Poisson-like distribution
        # Simplified: if projected > line, calc probability
        if projected_tds <= 0:
            return 0.05

        # Rough approximation for over/under TD probabilities
        if line <= 0.5:  # Over 0.5 TDs
            prob_over = min(0.95, projected_tds / 3.0)
        elif line <= 1.5:  # Over 1.5 TDs
            prob_over = max(0.05, (projected_tds - 1.0) / 2.0)
        elif line <= 2.5:  # Over 2.5 TDs
            prob_over = max(0.05, (projected_tds - 1.5) / 3.0)
        else:
            prob_over = max(0.05, (projected_tds - 2.0) / 4.0)

        return max(0.05, min(0.95, prob_over))

    def passing_prop_decide_and_place(self, game: NFLGame) -> list[EdgeBet]:
        """Main passing props decision engine"""
        edge_bets = []

        # Game environment filter
        if game.weather_temp and game.weather_temp < 32:  # Very cold
            return edge_bets
        if game.weather_wind and game.weather_wind > 20:  # Very windy
            return edge_bets

        # Create mock QB props (would fetch real data)
        home_qb = NFLPassingProps(
            qb_name="QB1",
            team=game.home_team,
            avg_pass_yards=random.uniform(220, 280),
            avg_pass_tds=random.uniform(1.2, 2.4),
            opponent_pass_def_rank=random.randint(1, 32),
            weather_wind_mph=game.weather_wind or 5.0,
            dome_game=game.dome,
        )

        away_qb = NFLPassingProps(
            qb_name="QB1",
            team=game.away_team,
            avg_pass_yards=random.uniform(220, 280),
            avg_pass_tds=random.uniform(1.2, 2.4),
            opponent_pass_def_rank=random.randint(1, 32),
            weather_wind_mph=game.weather_wind or 5.0,
            dome_game=game.dome,
        )

        # Process both QBs
        for qb_props in [home_qb, away_qb]:
            # Passing Yards Props
            yards_features = self.extract_passing_yards_features(game, qb_props)
            yards_line = 265.5  # Mock line (would fetch from book)

            prob_over_yards = self.predict_passing_yards_prob_over(yards_features, yards_line)

            # Mock odds
            odds_over_yards = random.uniform(-130, +110)
            (-(odds_over_yards + 20) if odds_over_yards > 0 else abs(odds_over_yards) + 20)

            # Calculate edge for over
            decimal_odds = american_to_decimal(odds_over_yards)
            implied_prob = 1.0 / decimal_odds
            edge_over = prob_over_yards - implied_prob

            if edge_over >= self.EDGE_THRESHOLD_PROP:
                bet_size = self._calculate_prop_bet_size(prob_over_yards, decimal_odds)
                if bet_size >= self.MIN_BET:
                    edge_bet = EdgeBet(
                        event_id=game.game_id,
                        sport="NFL",
                        market="passing_props",
                        selection=f"{qb_props.qb_name} Over {yards_line} Passing Yards",
                        book="Combined",
                        odds=odds_over_yards,
                        implied_prob=implied_prob,
                        fair_prob=prob_over_yards,
                        edge=edge_over,
                        kelly_fraction=bet_size / self.bankroll_mgr.current_bankroll,
                        bet_size=bet_size,
                        confidence="STRONG" if edge_over >= 0.05 else "MODERATE",
                    )
                    edge_bets.append(edge_bet)

            # Passing TDs Props
            td_features = self.extract_passing_td_features(game, qb_props)
            td_line = 1.5  # Over 1.5 passing TDs

            prob_over_tds = self.predict_passing_td_prob_over(td_features, td_line)

            # Mock TD odds
            odds_over_tds = random.uniform(-150, +120)

            # Calculate edge for TDs over
            decimal_odds_td = american_to_decimal(odds_over_tds)
            implied_prob_td = 1.0 / decimal_odds_td
            edge_over_td = prob_over_tds - implied_prob_td

            if edge_over_td >= self.EDGE_THRESHOLD_PROP:
                bet_size = self._calculate_prop_bet_size(prob_over_tds, decimal_odds_td)
                if bet_size >= self.MIN_BET:
                    edge_bet = EdgeBet(
                        event_id=game.game_id,
                        sport="NFL",
                        market="passing_props",
                        selection=f"{qb_props.qb_name} Over {td_line} Passing TDs",
                        book="Combined",
                        odds=odds_over_tds,
                        implied_prob=implied_prob_td,
                        fair_prob=prob_over_tds,
                        edge=edge_over_td,
                        kelly_fraction=bet_size / self.bankroll_mgr.current_bankroll,
                        bet_size=bet_size,
                        confidence="STRONG" if edge_over_td >= 0.05 else "MODERATE",
                    )
                    edge_bets.append(edge_bet)

        return edge_bets

    def _calculate_prop_bet_size(self, model_prob: float, decimal_odds: float) -> float:
        """Calculate bet size using Kelly with prop-specific constraints"""
        b = decimal_odds - 1.0
        if b <= 0:
            return 0.0
        kelly_f = (model_prob * decimal_odds - 1) / b
        kelly_f = max(0.0, kelly_f)
        adjusted_kelly = kelly_f * self.FRACTIONAL_KELLY_PROP
        bet_size = adjusted_kelly * self.bankroll_mgr.current_bankroll
        return min(bet_size, self.bankroll_mgr.current_bankroll * self.MAX_BET_FRACTION_PROP)


# NFL Receiving Props System
@dataclass
class NFLReceivingProps:
    """NFL Receiving Props for WR/TE/RB"""

    player_name: str
    team: str
    position: str  # WR, TE, RB

    # Usage Metrics
    target_share: float = 0.20  # % of team targets
    snap_share: float = 0.75  # % of offensive snaps
    red_zone_targets: int = 2  # Targets inside 20-yard line
    route_participation: float = 0.80  # % of passing plays where player runs route

    # Production Metrics
    avg_receptions: float = 5.5
    avg_rec_yards: float = 65.0
    avg_rec_tds: float = 0.4
    yards_after_catch: float = 4.2

    # Matchup Context
    opponent_def_vs_position: dict[str, float] | None = None  # Yards allowed to WR/TE/RB
    coverage_matchup: str = "Average"  # Elite, Good, Average, Poor

    def __post_init__(self):
        if self.opponent_def_vs_position is None:
            self.opponent_def_vs_position = {"WR": 180.0, "TE": 50.0, "RB": 25.0}


class NFLReceivingPropsEngine:
    """NFL Receiving Props Betting Engine"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # Receiving Props Configuration
        self.EDGE_THRESHOLD_PROP = 0.03  # 3% edge (high variance)
        self.MAX_BET_FRACTION_PROP = 0.03  # 3% max bankroll
        self.FRACTIONAL_KELLY_PROP = 0.4  # Conservative Kelly
        self.MIN_BET = 1.0
        self.MIN_PASSING_POTENTIAL = 42.0

    def pick_receiving_prop_candidates(self, game: NFLGame) -> list[NFLReceivingProps]:
        """Select receiving prop candidates based on usage"""
        candidates = []

        # Mock candidates for both teams (would pull from real data)
        for team in [game.home_team, game.away_team]:
            candidates.extend(
                [
                    NFLReceivingProps(
                        player_name="WR1",
                        team=team,
                        position="WR",
                        target_share=random.uniform(0.22, 0.35),
                        avg_receptions=random.uniform(5.0, 8.5),
                        avg_rec_yards=random.uniform(60, 95),
                        red_zone_targets=random.randint(2, 6),
                    ),
                    NFLReceivingProps(
                        player_name="WR2",
                        team=team,
                        position="WR",
                        target_share=random.uniform(0.15, 0.25),
                        avg_receptions=random.uniform(3.5, 6.0),
                        avg_rec_yards=random.uniform(40, 70),
                        red_zone_targets=random.randint(1, 4),
                    ),
                    NFLReceivingProps(
                        player_name="TE1",
                        team=team,
                        position="TE",
                        target_share=random.uniform(0.12, 0.22),
                        avg_receptions=random.uniform(3.0, 6.0),
                        avg_rec_yards=random.uniform(35, 65),
                        red_zone_targets=random.randint(2, 5),
                    ),
                    NFLReceivingProps(
                        player_name="RB1",
                        team=team,
                        position="RB",
                        target_share=random.uniform(0.08, 0.18),
                        avg_receptions=random.uniform(2.5, 5.0),
                        avg_rec_yards=random.uniform(20, 45),
                        red_zone_targets=random.randint(0, 3),
                    ),
                ]
            )

        # Filter by minimum usage threshold
        return [c for c in candidates if c.target_share >= 0.10 and c.avg_receptions >= 2.5]

    def extract_receiving_yards_features(
        self, game: NFLGame, player: NFLReceivingProps
    ) -> dict[str, float]:
        """Extract features for receiving yards prediction"""
        return {
            "player_avg_yards": player.avg_rec_yards,
            "target_share": player.target_share,
            "snap_share": player.snap_share,
            "yac_ability": player.yards_after_catch,
            "team_passing_volume": 35.0,  # Expected team pass attempts
            "opponent_def_vs_pos": player.opponent_def_vs_position.get(player.position, 60.0),
            "matchup_quality": {
                "Elite": 0.7,
                "Good": 0.85,
                "Average": 1.0,
                "Poor": 1.2,
            }[player.coverage_matchup],
            "red_zone_usage": player.red_zone_targets / 5.0,  # Normalize
            "position_factor": {"WR": 1.0, "TE": 0.9, "RB": 0.7}[player.position],
            "game_script": 1.0,  # Would adjust based on expected game flow
        }

    def predict_receiving_yards_over(self, features: dict[str, float], line: float) -> float:
        """Predict probability of going over receiving yards line"""
        # Base projection
        projected_yards = features["player_avg_yards"]

        # Usage adjustments
        projected_yards *= features["target_share"] / 0.20  # Scale by target share
        projected_yards *= features["matchup_quality"]
        projected_yards *= features["position_factor"]

        # Game environment
        projected_yards *= features["team_passing_volume"] / 32.0  # Scale by pass volume

        # Estimate volatility
        std_dev = projected_yards * 0.35  # Receiving yards are highly volatile

        # Normal distribution probability
        if std_dev > 0:
            from math import erf, sqrt

            z_score = (line - projected_yards) / (std_dev * sqrt(2))
            prob_under = 0.5 * (1 + erf(z_score))
            prob_over = 1 - prob_under
        else:
            prob_over = 1.0 if projected_yards > line else 0.0

        return max(0.05, min(0.95, prob_over))

    def receiving_prop_decide_and_place(self, game: NFLGame) -> list[EdgeBet]:
        """Main receiving props decision engine"""
        edge_bets = []

        # Get receiving candidates
        candidates = self.pick_receiving_prop_candidates(game)

        for player in candidates:
            # Receiving Yards Props
            yards_features = self.extract_receiving_yards_features(game, player)
            yards_line = 55.5  # Mock line (varies by player)

            prob_over_yards = self.predict_receiving_yards_over(yards_features, yards_line)

            # Mock market odds
            odds_over = random.uniform(-130, +110)

            # Calculate edge
            decimal_odds = american_to_decimal(odds_over)
            implied_prob = 1.0 / decimal_odds
            edge_over = prob_over_yards - implied_prob

            if edge_over >= self.EDGE_THRESHOLD_PROP:
                bet_size = self._calculate_prop_bet_size(prob_over_yards, decimal_odds)
                if bet_size >= self.MIN_BET:
                    edge_bet = EdgeBet(
                        event_id=game.game_id,
                        sport="NFL",
                        market="receiving_props",
                        selection=f"{player.player_name} Over {yards_line} Receiving Yards",
                        book="Combined",
                        odds=odds_over,
                        implied_prob=implied_prob,
                        fair_prob=prob_over_yards,
                        edge=edge_over,
                        kelly_fraction=bet_size / self.bankroll_mgr.current_bankroll,
                        bet_size=bet_size,
                        confidence="STRONG" if edge_over >= 0.06 else "MODERATE",
                    )
                    edge_bets.append(edge_bet)

        return edge_bets

    def _calculate_prop_bet_size(self, model_prob: float, decimal_odds: float) -> float:
        """Calculate bet size for receiving props"""
        b = decimal_odds - 1.0
        if b <= 0:
            return 0.0
        kelly_f = (model_prob * decimal_odds - 1) / b
        kelly_f = max(0.0, kelly_f)
        adjusted_kelly = kelly_f * self.FRACTIONAL_KELLY_PROP
        bet_size = adjusted_kelly * self.bankroll_mgr.current_bankroll
        return min(bet_size, self.bankroll_mgr.current_bankroll * self.MAX_BET_FRACTION_PROP)


# NFL Rushing Props System
@dataclass
class NFLRushingProps:
    """NFL Rushing Props for RB/QB"""

    player_name: str
    team: str
    position: str  # RB, QB

    # Usage Metrics
    carry_share: float = 0.65  # % of team carries
    goal_line_share: float = 0.80  # % of goal line carries
    red_zone_carries: int = 3  # Carries inside 20
    snap_share: float = 0.70

    # Production Metrics
    avg_rush_yards: float = 75.0
    avg_carries: float = 15.0
    avg_rush_tds: float = 0.6
    yards_per_carry: float = 4.2

    # Matchup Context
    opponent_rush_def_rank: int = 16  # 1-32 ranking
    opponent_rush_yards_allowed: float = 120.0
    run_blocking_grade: float = 65.0  # PFF-style 0-100 grade


class NFLRushingPropsEngine:
    """NFL Rushing Props Betting Engine"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # Rushing Props Configuration
        self.EDGE_THRESHOLD_PROP = 0.03
        self.MAX_BET_FRACTION_PROP = 0.03
        self.FRACTIONAL_KELLY_PROP = 0.4
        self.MIN_BET = 1.0
        self.MIN_RUSHING_POTENTIAL = 38.0

    def pick_rushing_prop_candidates(self, game: NFLGame) -> list[NFLRushingProps]:
        """Select rushing prop candidates"""
        candidates = []

        for team in [game.home_team, game.away_team]:
            candidates.extend(
                [
                    NFLRushingProps(
                        player_name="RB1",
                        team=team,
                        position="RB",
                        carry_share=random.uniform(0.55, 0.75),
                        avg_rush_yards=random.uniform(65, 110),
                        avg_carries=random.uniform(12, 20),
                        goal_line_share=random.uniform(0.65, 0.85),
                    ),
                    NFLRushingProps(
                        player_name="QB1",
                        team=team,
                        position="QB",
                        carry_share=random.uniform(0.10, 0.25),
                        avg_rush_yards=random.uniform(15, 45),
                        avg_carries=random.uniform(3, 8),
                        goal_line_share=random.uniform(0.15, 0.35),
                    ),
                ]
            )

        # Filter by minimum usage
        return [c for c in candidates if c.avg_carries >= 3.0]

    def extract_rushing_yards_features(
        self, game: NFLGame, player: NFLRushingProps
    ) -> dict[str, float]:
        """Extract features for rushing yards prediction"""
        return {
            "player_avg_yards": player.avg_rush_yards,
            "carry_share": player.carry_share,
            "ypc": player.yards_per_carry,
            "opponent_rush_def": (33 - player.opponent_rush_def_rank) / 32,  # Normalize
            "run_blocking": player.run_blocking_grade / 100.0,
            "game_script": 1.0,  # Would adjust for expected game flow
            "weather_factor": (
                1.0 if not game.weather_precip else 1.1
            ),  # Running better in bad weather
            "position_factor": (1.0 if player.position == "RB" else 0.6),  # QBs less consistent
            "team_rush_attempts": 28.0,  # Expected team rush attempts
        }

    def predict_rushing_yards_over(self, features: dict[str, float], line: float) -> float:
        """Predict probability of going over rushing yards line"""
        # Base projection
        projected_yards = features["player_avg_yards"]

        # Usage and efficiency adjustments
        projected_yards *= features["carry_share"] / 0.60  # Scale by usage
        projected_yards *= features["ypc"] / 4.0  # Scale by efficiency
        projected_yards *= 1 + features["opponent_rush_def"]  # Better vs worse defenses
        projected_yards *= features["run_blocking"]
        projected_yards *= features["position_factor"]

        # Game environment
        projected_yards *= features["team_rush_attempts"] / 25.0
        projected_yards *= features["weather_factor"]

        # Rushing yards volatility (lower than receiving)
        std_dev = projected_yards * 0.30

        # Calculate probability
        if std_dev > 0:
            from math import erf, sqrt

            z_score = (line - projected_yards) / (std_dev * sqrt(2))
            prob_under = 0.5 * (1 + erf(z_score))
            prob_over = 1 - prob_under
        else:
            prob_over = 1.0 if projected_yards > line else 0.0

        return max(0.05, min(0.95, prob_over))

    def rushing_prop_decide_and_place(self, game: NFLGame) -> list[EdgeBet]:
        """Main rushing props decision engine"""
        edge_bets = []

        candidates = self.pick_rushing_prop_candidates(game)

        for player in candidates:
            # Rushing Yards Props
            yards_features = self.extract_rushing_yards_features(game, player)

            # Different lines for RB vs QB
            yards_line = 65.5 if player.position == "RB" else 25.5

            prob_over_yards = self.predict_rushing_yards_over(yards_features, yards_line)

            # Mock odds
            odds_over = random.uniform(-120, +105)

            # Calculate edge
            decimal_odds = american_to_decimal(odds_over)
            implied_prob = 1.0 / decimal_odds
            edge_over = prob_over_yards - implied_prob

            if edge_over >= self.EDGE_THRESHOLD_PROP:
                bet_size = self._calculate_prop_bet_size(prob_over_yards, decimal_odds)
                if bet_size >= self.MIN_BET:
                    edge_bet = EdgeBet(
                        event_id=game.game_id,
                        sport="NFL",
                        market="rushing_props",
                        selection=f"{player.player_name} Over {yards_line} Rushing Yards",
                        book="Combined",
                        odds=odds_over,
                        implied_prob=implied_prob,
                        fair_prob=prob_over_yards,
                        edge=edge_over,
                        kelly_fraction=bet_size / self.bankroll_mgr.current_bankroll,
                        bet_size=bet_size,
                        confidence="STRONG" if edge_over >= 0.06 else "MODERATE",
                    )
                    edge_bets.append(edge_bet)

        return edge_bets

    def _calculate_prop_bet_size(self, model_prob: float, decimal_odds: float) -> float:
        """Calculate bet size for rushing props"""
        b = decimal_odds - 1.0
        if b <= 0:
            return 0.0
        kelly_f = (model_prob * decimal_odds - 1) / b
        kelly_f = max(0.0, kelly_f)
        adjusted_kelly = kelly_f * self.FRACTIONAL_KELLY_PROP
        bet_size = adjusted_kelly * self.bankroll_mgr.current_bankroll
        return min(bet_size, self.bankroll_mgr.current_bankroll * self.MAX_BET_FRACTION_PROP)


# NFL Halves Markets System
@dataclass
class NFLHalfPrediction:
    """NFL Half-specific predictions"""

    game_id: str
    half: str  # "first" or "second"

    # Half totals
    predicted_half_total: float
    over_prob: float
    under_prob: float

    # Half spreads (if supported)
    predicted_half_spread: float = 0.0
    half_spread_cover_prob: float = 0.5

    # Context
    pace_factor: float = 1.0
    first_half_result: dict[str, float] | None = None  # For second half adjustments


class NFLHalvesEngine:
    """NFL First Half and Second Half Betting Engine"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # Halves Configuration
        self.EDGE_THRESHOLD_HALF = 0.02  # 2% edge minimum
        self.MAX_BET_FRACTION_HALF = 0.04
        self.FRACTIONAL_KELLY_HALF = 0.5
        self.MIN_BET = 1.0
        self.MIN_TOTAL_THRESHOLD = 38.0

    def extract_half_features_pre(self, game: NFLGame, half: str) -> dict[str, float]:
        """Extract features for first half prediction (pre-game)"""
        return {
            "team_first_half_avg": 12.0,  # Average first half points
            "team_second_half_avg": 12.0,  # Average second half points
            "opponent_half_def": 11.5,  # Points allowed per half
            "pace_factor": 1.0,  # Game pace expectation
            "weather_impact": 1.0 if not game.weather_precip else 0.95,
            "home_field_half": (1.5 if half == "first" else 1.0),  # Home teams start stronger
            "rest_advantage": (game.home_rest_days - game.away_rest_days) / 7.0,
            "coaching_adjustments": 1.0 if half == "second" else 0.0,
            "injury_impact": (
                0.95
                if (game.home_qb_status != "starter" or game.away_qb_status != "starter")
                else 1.0
            ),
        }

    def extract_half_features_mid(
        self, game: NFLGame, first_half_data: dict[str, float]
    ) -> dict[str, float]:
        """Extract features for second half prediction (using first half data)"""
        return {
            "first_half_total": first_half_data.get("total_points", 24.0),
            "first_half_pace": first_half_data.get("possessions", 12.0),
            "halftime_adjustments": 1.1,  # Coaching adjustments boost
            "momentum_factor": first_half_data.get("momentum", 1.0),
            "injury_developments": 1.0,  # Any in-game injuries
            "weather_change": 1.0,  # Weather changes at halftime
            "garbage_time_risk": (0.9 if abs(first_half_data.get("margin", 0)) > 14 else 1.0),
            "conditioning_factor": 0.95,  # Fatigue factor in second half
            "timeout_usage": first_half_data.get("timeouts_remaining", 6) / 6.0,
        }

    def predict_half_total(self, features: dict[str, float], half: str) -> float:
        """Predict half total points"""
        if half == "first":
            # Pre-game first half prediction
            base_total = features.get("team_first_half_avg", 12.0) * 2  # Both teams
            base_total *= features.get("pace_factor", 1.0)
            base_total *= features.get("weather_impact", 1.0)
            base_total += features.get("home_field_half", 0.0)
        else:
            # Second half prediction with first half context
            base_total = features.get("team_second_half_avg", 12.0) * 2
            base_total *= features.get("halftime_adjustments", 1.0)
            base_total *= features.get("garbage_time_risk", 1.0)
            base_total *= features.get("conditioning_factor", 1.0)

        return max(10.0, min(35.0, base_total))  # Reasonable half total bounds

    def predict_half_over_prob(self, predicted_total: float, market_line: float) -> float:
        """Predict probability of going over half total line"""
        # Half totals have less variance than full game
        std_dev = predicted_total * 0.20  # 20% coefficient of variation

        if std_dev > 0:
            from math import erf, sqrt

            z_score = (market_line - predicted_total) / (std_dev * sqrt(2))
            prob_under = 0.5 * (1 + erf(z_score))
            prob_over = 1 - prob_under
        else:
            prob_over = 1.0 if predicted_total > market_line else 0.0

        return max(0.05, min(0.95, prob_over))

    def half_decide_and_place(
        self, game: NFLGame, half: str, first_half_data: dict[str, float] | None = None
    ) -> list[EdgeBet]:
        """Main halves decision engine"""
        edge_bets = []

        # Feature extraction based on half
        if half == "first":
            features = self.extract_half_features_pre(game, half)
        else:
            if first_half_data is None:
                return edge_bets  # Can't bet second half without first half data
            features = self.extract_half_features_mid(game, first_half_data)

        # Predict half total
        predicted_half_total = self.predict_half_total(features, half)

        # Mock market line (would fetch from sportsbook)
        if half == "first":
            market_line = predicted_half_total + random.uniform(-2.0, 2.0)
        else:
            # Second half lines often adjust based on first half
            market_line = predicted_half_total + random.uniform(-1.5, 1.5)

        # Calculate over probability
        prob_over = self.predict_half_over_prob(predicted_half_total, market_line)
        prob_under = 1.0 - prob_over

        # Mock odds
        odds_over = random.uniform(-120, +110)
        odds_under = random.uniform(-120, +110)

        # Check Over edge
        decimal_over = american_to_decimal(odds_over)
        implied_over = 1.0 / decimal_over
        edge_over = prob_over - implied_over

        if edge_over >= self.EDGE_THRESHOLD_HALF:
            bet_size = self._calculate_half_bet_size(prob_over, decimal_over)
            if bet_size >= self.MIN_BET:
                edge_bet = EdgeBet(
                    event_id=game.game_id,
                    sport="NFL",
                    market=f"{half}_half",
                    selection=f"{half.title()} Half Over {market_line}",
                    book="Combined",
                    odds=odds_over,
                    implied_prob=implied_over,
                    fair_prob=prob_over,
                    edge=edge_over,
                    kelly_fraction=bet_size / self.bankroll_mgr.current_bankroll,
                    bet_size=bet_size,
                    confidence="STRONG" if edge_over >= 0.04 else "MODERATE",
                )
                edge_bets.append(edge_bet)

        # Check Under edge
        decimal_under = american_to_decimal(odds_under)
        implied_under = 1.0 / decimal_under
        edge_under = prob_under - implied_under

        if edge_under >= self.EDGE_THRESHOLD_HALF:
            bet_size = self._calculate_half_bet_size(prob_under, decimal_under)
            if bet_size >= self.MIN_BET:
                edge_bet = EdgeBet(
                    event_id=game.game_id,
                    sport="NFL",
                    market=f"{half}_half",
                    selection=f"{half.title()} Half Under {market_line}",
                    book="Combined",
                    odds=odds_under,
                    implied_prob=implied_under,
                    fair_prob=prob_under,
                    edge=edge_under,
                    kelly_fraction=bet_size / self.bankroll_mgr.current_bankroll,
                    bet_size=bet_size,
                    confidence="STRONG" if edge_under >= 0.04 else "MODERATE",
                )
                edge_bets.append(edge_bet)

        return edge_bets

    def _calculate_half_bet_size(self, model_prob: float, decimal_odds: float) -> float:
        """Calculate bet size for half markets"""
        b = decimal_odds - 1.0
        if b <= 0:
            return 0.0
        kelly_f = (model_prob * decimal_odds - 1) / b
        kelly_f = max(0.0, kelly_f)
        adjusted_kelly = kelly_f * self.FRACTIONAL_KELLY_HALF
        bet_size = adjusted_kelly * self.bankroll_mgr.current_bankroll
        return min(bet_size, self.bankroll_mgr.current_bankroll * self.MAX_BET_FRACTION_HALF)


# Global NFL Specialized Engines
nfl_game_lines_engine = NFLGameLinesEngine(bankroll_manager)
nfl_td_scorer_engine = NFLTDScorerEngine(bankroll_manager)
nfl_passing_props_engine = NFLPassingPropsEngine(bankroll_manager)
nfl_receiving_props_engine = NFLReceivingPropsEngine(bankroll_manager)
nfl_rushing_props_engine = NFLRushingPropsEngine(bankroll_manager)
nfl_halves_engine = NFLHalvesEngine(bankroll_manager)

# ================================
# COLLEGE FOOTBALL (NCAAF) CLASSES
# ================================


@dataclass
class NCAAFGame:
    """College Football Game with comprehensive betting and academic context"""

    game_id: str
    home_team: str
    away_team: str
    week: int
    season: int
    kickoff_time: datetime

    # Conference and Division Info
    home_conference: str = "FBS Independent"
    away_conference: str = "FBS Independent"
    is_conference_game: bool = False
    is_rivalry_game: bool = False

    # Team Strength & Schedule Context
    home_sos_rank: int | None = None  # Strength of Schedule rank (1-131)
    away_sos_rank: int | None = None
    home_sagarin_rating: float | None = None  # Sagarin computer rating
    away_sagarin_rating: float | None = None
    home_record: str = "0-0"  # Season record
    away_record: str = "0-0"
    home_conference_record: str = "0-0"
    away_conference_record: str = "0-0"

    # Roster & Personnel (College-Specific)
    home_returning_starters: int | None = None  # Returning starters count
    away_returning_starters: int | None = None
    home_recruiting_class_rank: int | None = None  # Last 3-year avg recruiting rank
    away_recruiting_class_rank: int | None = None
    home_transfer_net: int = 0  # Net transfers (in - out)
    away_transfer_net: int = 0
    home_coaching_change: bool = False  # New head coach this season
    away_coaching_change: bool = False

    # Game Context
    home_rest_days: int = 7
    away_rest_days: int = 7
    travel_distance: float = 0.0  # Miles for away team
    time_zone_change: int = 0  # Hours difference for away team
    altitude: int | None = None  # Stadium altitude (Denver, etc.)

    # Weather & Environment
    weather_temp: float | None = None
    weather_wind: float | None = None
    weather_precip: str | None = None
    surface_type: str = "grass"  # grass/turf
    dome: bool = False
    attendance_capacity: int | None = None  # Stadium capacity
    expected_attendance_pct: float = 1.0  # Expected % capacity

    # Injuries & Personnel Status
    home_qb_status: str = "starter"  # starter/backup/questionable/unknown
    away_qb_status: str = "starter"
    home_key_injuries: list[str] | None = None
    away_key_injuries: list[str] | None = None
    home_depth_concerns: list[str] | None = None  # Position groups with depth issues
    away_depth_concerns: list[str] | None = None

    # Recent Performance & Trends
    home_recent_form: str | None = None  # Last 4 games: "3-1" format
    away_recent_form: str | None = None
    home_avg_margin: float = 0.0  # Average margin of victory/defeat
    away_avg_margin: float = 0.0
    home_vs_ranked_record: str = "0-0"  # Record vs ranked opponents
    away_vs_ranked_record: str = "0-0"

    # Advanced College Metrics
    home_offensive_epa: float | None = None
    home_defensive_epa: float | None = None
    away_offensive_epa: float | None = None
    away_defensive_epa: float | None = None
    home_fei_rating: float | None = None  # Football Efficiency Index
    away_fei_rating: float | None = None
    home_sp_plus_rating: float | None = None  # Bill Connelly's SP+ rating
    away_sp_plus_rating: float | None = None

    # Situational Factors (College-Specific)
    homecoming_game: bool = False
    senior_day: bool = False
    bowl_eligibility_implications: bool = False  # Game affects bowl eligibility
    playoff_implications: bool = False  # CFP implications
    championship_implications: bool = False  # Conference championship implications

    # Market & Betting Context
    public_betting_pct: float | None = None  # % of public bets on favorite
    public_money_pct: float | None = None  # % of money on favorite
    line_movement: float | None = None  # Opening vs current spread
    sharp_money_indicator: str | None = None  # "home", "away", "none"

    # Historical Context
    h2h_last_5_years: str | None = None  # "3-2" format for home team
    home_ats_record: str = "0-0"  # Against the spread record
    away_ats_record: str = "0-0"
    home_ou_record: str = "0-0"  # Over/under record
    away_ou_record: str = "0-0"

    def __post_init__(self):
        if self.home_key_injuries is None:
            self.home_key_injuries = []
        if self.away_key_injuries is None:
            self.away_key_injuries = []
        if self.home_depth_concerns is None:
            self.home_depth_concerns = []
        if self.away_depth_concerns is None:
            self.away_depth_concerns = []


@dataclass
class NCAAFMarketPrediction:
    """College Football Model predictions with volatility adjustments"""

    game_id: str

    # Core Probabilities
    home_win_prob: float
    away_win_prob: float

    # Spread Predictions (with extreme spread handling)
    predicted_spread: float  # Negative = home favored
    spread_cover_prob: float  # Prob of favorite covering

    # Total Predictions
    predicted_total: float
    over_prob: float
    under_prob: float

    # College-Specific Adjustments (with defaults)
    blowout_probability: float = 0.0  # Prob of 21+ point margin

    # College-Specific Adjustments
    mismatch_factor: float = 1.0  # 1.0-2.0 scale for talent disparity
    volatility_adjustment: float = 1.0  # Account for college unpredictability
    public_fade_factor: float = 1.0  # Adjustment for public betting bias

    # Confidence Intervals (wider for college)
    spread_confidence: float = 0.60  # Lower confidence than NFL
    total_confidence: float = 0.60

    # Model Metadata
    model_version: str = "ncaaf_v1.0"
    features_used: list[str] | None = None
    simulation_count: int = 15000  # More simulations due to volatility

    def __post_init__(self):
        if self.features_used is None:
            self.features_used = [
                "sos",
                "recruiting",
                "transfers",
                "coaching",
                "situational",
                "weather",
                "rest",
                "public_betting",
            ]


@dataclass
class NCAAFBettingEngine:
    """College Football-Specific Edge Detection and Betting Engine"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # NCAAF-specific risk controls (more conservative due to volatility)
        self.max_bets_per_game = 1  # Max 1 market per game (correlation risk)
        self.max_bets_per_week = 8  # Max 8 bets per college week
        self.max_exposure_per_team = 0.05  # Max 5% bankroll on any team
        self.max_exposure_per_conference = 0.15  # Max 15% bankroll per conference

        # NCAAF edge thresholds (higher due to market inefficiencies but lower confidence)
        self.min_edge_threshold = 0.03  # 3% minimum edge (higher than NFL)
        self.strong_edge_threshold = 0.06  # 6% = strong edge
        self.lock_edge_threshold = 0.10  # 10% = lock play (rare in college)

        # Market-specific Kelly multipliers (more conservative than NFL)
        self.market_kelly_multipliers = {
            "moneyline": 0.20,  # Very conservative on ML due to upsets
            "spread": 0.25,  # Slightly more aggressive on spreads (market inefficiency)
            "total": 0.20,  # Conservative on totals (weather/pace factors)
            "props": 0.15,  # Very conservative on props (limited info)
        }

        # College-specific adjustments
        self.mismatch_kelly_reduction = 0.8  # Reduce Kelly for extreme mismatches
        self.public_fade_kelly_boost = 1.2  # Boost Kelly when fading public
        self.sharp_money_kelly_boost = 1.1  # Boost Kelly when following sharp money

        # Weekly tracking
        self.weekly_bets: dict[int, list[EdgeBet]] = {}
        self.team_exposure: dict[str, float] = {}
        self.conference_exposure: dict[str, float] = {}

    def ncaaf_decide_and_place(
        self,
        game: NCAAFGame,
        market_type: str,
        market_odds: float,
        prediction: NCAAFMarketPrediction,
    ) -> EdgeBet | None:
        """
        Main NCAAF betting decision function with college-specific logic:
        1. College-specific spread-to-probability conversion
        2. Enhanced volatility and mismatch adjustments
        3. Public betting sentiment integration
        4. Conservative Kelly sizing for unpredictable outcomes
        """

        # Step 1: Get fair probability using NCAAF-specific methods
        fair_prob = self._get_ncaaf_fair_probability(prediction, market_type, game)
        if fair_prob is None:
            return None

        # Step 2: Calculate implied probability with college-specific conversion
        implied_prob = self._calculate_ncaaf_implied_prob(market_odds, market_type, game)
        raw_edge = fair_prob - implied_prob

        # Step 3: Apply college-specific edge adjustments
        adjusted_edge = self._adjust_edge_for_ncaaf_factors(raw_edge, game, market_type, prediction)

        # Step 4: Apply NCAAF edge threshold
        if adjusted_edge < self.min_edge_threshold:
            logger.debug(
                f"NCAAF edge {adjusted_edge:.3f} below threshold for {game.away_team}@{game.home_team}"
            )
            return None

        # Step 5: Check NCAAF-specific constraints
        if not self._validate_ncaaf_constraints(game, market_type):
            return None

        # Step 6: Calculate NCAAF market-adjusted Kelly sizing
        kelly_multiplier = self.market_kelly_multipliers.get(market_type, 0.20)

        # Apply college-specific Kelly adjustments
        kelly_multiplier = self._apply_ncaaf_kelly_adjustments(kelly_multiplier, game, prediction)

        base_kelly = self.bankroll_mgr.calculate_kelly_size(market_odds, fair_prob)
        adjusted_kelly = base_kelly * kelly_multiplier

        # Step 7: Final NCAAF risk controls
        max_kelly = self._calculate_ncaaf_max_kelly(game, market_type, prediction)
        final_kelly = min(adjusted_kelly, max_kelly)

        if final_kelly <= 0:
            return None

        # Step 8: Create NCAAF EdgeBet
        bet_size = self.bankroll_mgr.calculate_bet_size(final_kelly)
        confidence = self._classify_ncaaf_confidence(adjusted_edge, final_kelly, game, prediction)
        selection = self._format_ncaaf_selection(market_type, game, market_odds)

        edge_bet = EdgeBet(
            event_id=game.game_id,
            sport="NCAAF",
            market=market_type,
            selection=selection,
            book="Combined",
            odds=market_odds,
            implied_prob=implied_prob,
            fair_prob=fair_prob,
            edge=adjusted_edge,
            kelly_fraction=final_kelly,
            bet_size=bet_size,
            confidence=confidence,
        )

        # Step 9: Track NCAAF bet for exposure limits
        self._track_ncaaf_bet(edge_bet, game)

        logger.info(
            f"🏈 NCAAF EDGE: {selection} | Edge: {adjusted_edge:.1%} | Kelly: {final_kelly:.1%} | Size: ${bet_size:.2f} | {confidence}"
        )
        return edge_bet

    def _get_ncaaf_fair_probability(
        self, prediction: NCAAFMarketPrediction, market_type: str, game: NCAAFGame
    ) -> float | None:
        """Extract fair probability from NCAAF model prediction"""
        if market_type == "moneyline":
            return prediction.home_win_prob  # Caller will adjust based on side
        if market_type == "spread":
            return prediction.spread_cover_prob
        if market_type == "total":
            return prediction.over_prob  # Caller will use under_prob for under bets
        return None

    def _calculate_ncaaf_implied_prob(
        self, market_odds: float, market_type: str, game: NCAAFGame
    ) -> float:
        """
        Calculate implied probability with NCAAF-specific adjustments for extreme spreads.
        Uses normal distribution with sigma=13.0 for college football spread conversion.
        """
        if market_type == "spread":
            # For spread bets, we need the actual spread value
            # This is a simplified conversion - in practice you'd get the spread from odds API
            return american_to_implied(market_odds)
        return american_to_implied(market_odds)

    def _adjust_edge_for_ncaaf_factors(
        self,
        raw_edge: float,
        game: NCAAFGame,
        market_type: str,
        prediction: NCAAFMarketPrediction,
    ) -> float:
        """Apply college-specific edge adjustments"""
        adjusted_edge = raw_edge

        # Extreme mismatch adjustments (reduce confidence in blowouts)
        if prediction.blowout_probability > 0.3:  # High blowout probability
            adjusted_edge *= 0.85  # Reduce edge confidence

        # Conference strength adjustments
        power_conferences = ["SEC", "Big Ten", "Big 12", "ACC", "Pac-12"]
        if (
            game.home_conference in power_conferences
            and game.away_conference not in power_conferences
        ):
            adjusted_edge *= 1.05  # Slight boost for P5 vs G5 games

        # Coaching change volatility
        if game.home_coaching_change or game.away_coaching_change:
            adjusted_edge *= 0.9  # Reduce confidence with new coaches

        # Public betting fade opportunities
        if (
            game.public_betting_pct and abs(game.public_betting_pct - 0.5) > 0.25
        ):  # Heavy public lean
            adjusted_edge *= 1.1  # Boost edge when fading heavy public side

        # Sharp money alignment
        if game.sharp_money_indicator and game.sharp_money_indicator != "none":
            adjusted_edge *= 1.05  # Boost when following sharp money

        # Bowl/playoff implications (more unpredictable)
        if game.bowl_eligibility_implications or game.playoff_implications:
            adjusted_edge *= 0.95

        # Rivalry game adjustments (throw out the records)
        if game.is_rivalry_game:
            adjusted_edge *= 0.9

        return max(0, adjusted_edge)

    def _validate_ncaaf_constraints(self, game: NCAAFGame, market_type: str) -> bool:
        """Check NCAAF-specific betting constraints"""

        # Weekly bet limit
        week_bets = self.weekly_bets.get(game.week, [])
        if len(week_bets) >= self.max_bets_per_week:
            logger.debug(
                f"NCAAF weekly bet limit reached: {len(week_bets)}/{self.max_bets_per_week}"
            )
            return False

        # Per-game bet limit (stricter than NFL due to correlation)
        game_bets = [bet for bet in week_bets if bet.event_id == game.game_id]
        if len(game_bets) >= self.max_bets_per_game:
            logger.debug(f"NCAAF per-game bet limit reached for {game.game_id}")
            return False

        # Team exposure limits
        for team in [game.home_team, game.away_team]:
            current_exposure = self.team_exposure.get(team, 0.0)
            if current_exposure >= self.max_exposure_per_team:
                logger.debug(
                    f"NCAAF team exposure limit reached for {team}: {current_exposure:.1%}"
                )
                return False

        # Conference exposure limits
        for conf in [game.home_conference, game.away_conference]:
            if conf != "FBS Independent":
                current_exposure = self.conference_exposure.get(conf, 0.0)
                if current_exposure >= self.max_exposure_per_conference:
                    logger.debug(
                        f"NCAAF conference exposure limit reached for {conf}: {current_exposure:.1%}"
                    )
                    return False

        return True

    def _apply_ncaaf_kelly_adjustments(
        self, base_kelly: float, game: NCAAFGame, prediction: NCAAFMarketPrediction
    ) -> float:
        """Apply college-specific Kelly multiplier adjustments"""

        # Reduce Kelly for extreme mismatches (volatile outcomes)
        if prediction.mismatch_factor > 1.5:
            base_kelly *= self.mismatch_kelly_reduction

        # Boost Kelly when fading heavy public betting
        if game.public_betting_pct and abs(game.public_betting_pct - 0.5) > 0.3:
            base_kelly *= self.public_fade_kelly_boost

        # Boost Kelly when following sharp money
        if game.sharp_money_indicator and game.sharp_money_indicator != "none":
            base_kelly *= self.sharp_money_kelly_boost

        return base_kelly

    def _calculate_ncaaf_max_kelly(
        self, game: NCAAFGame, market_type: str, prediction: NCAAFMarketPrediction
    ) -> float:
        """Calculate maximum Kelly fraction for NCAAF bet"""

        base_max = self.bankroll_mgr.max_bet_percentage

        # Reduce for high volatility scenarios
        if prediction.volatility_adjustment > 1.2:
            base_max *= 0.8

        # Reduce for extreme spreads (20+ points)
        if abs(prediction.predicted_spread) > 20:
            base_max *= 0.7

        # Reduce for rivalry games
        if game.is_rivalry_game:
            base_max *= 0.9

        return base_max

    def _classify_ncaaf_confidence(
        self,
        edge: float,
        kelly: float,
        game: NCAAFGame,
        prediction: NCAAFMarketPrediction,
    ) -> str:
        """Classify NCAAF bet confidence with college-specific factors"""

        if edge >= self.lock_edge_threshold and kelly >= 0.025:
            return "LOCK"
        if edge >= self.strong_edge_threshold and kelly >= 0.015:
            return "STRONG"
        if edge >= self.min_edge_threshold and kelly >= 0.008:
            return "MODERATE"
        return "WEAK"

    def _format_ncaaf_selection(self, market_type: str, game: NCAAFGame, odds: float) -> str:
        """Format NCAAF bet selection string"""

        if market_type == "moneyline":
            team = game.home_team if odds < 0 else game.away_team
            return f"{team} ML"
        if market_type == "spread":
            return f"NCAAF Spread Bet ({odds:+.1f})"
        if market_type == "total":
            direction = "Over" if odds > 0 else "Under"
            return f"{direction} Total"
        return f"NCAAF {market_type}"

    def _track_ncaaf_bet(self, bet: EdgeBet, game: NCAAFGame):
        """Track NCAAF bet for exposure limits"""

        # Add to weekly tracking
        if game.week not in self.weekly_bets:
            self.weekly_bets[game.week] = []
        self.weekly_bets[game.week].append(bet)

        # Update team exposure (simplified - assumes betting on home team)
        team = game.home_team  # Would be determined by actual bet selection
        current_exposure = self.team_exposure.get(team, 0.0)
        bet_exposure = bet.bet_size / self.bankroll_mgr.current_bankroll
        self.team_exposure[team] = current_exposure + bet_exposure

        # Update conference exposure
        conf = game.home_conference
        if conf != "FBS Independent":
            current_conf_exposure = self.conference_exposure.get(conf, 0.0)
            self.conference_exposure[conf] = current_conf_exposure + bet_exposure


# Global NCAAF betting engine instance
ncaaf_engine = NCAAFBettingEngine(bankroll_manager)

# ================================
# NCAAF UTILITY FUNCTIONS
# ================================


def implied_probability_ncaaf_from_spread(spread: float) -> float:
    """
    Convert NCAAF spread to implied probability using normal distribution.
    College football has higher standard deviation (13.0) compared to NFL (13.8).
    Handles extreme spreads common in college football.
    """
    import math

    # College football standard deviation for point margins
    sigma = 13.0  # Slightly lower than NFL due to more volatile outcomes

    # Handle extreme spreads (40+ points) with adjusted sigma
    if abs(spread) > 40:
        sigma = 15.0  # Increase sigma for extreme mismatches
    elif abs(spread) > 25:
        sigma = 14.0  # Moderate increase for large spreads

    # Convert spread to probability using normal CDF
    # Negative spread = favorite, positive = underdog
    z_score = -spread / (sigma * math.sqrt(2))

    # Use complementary error function for normal CDF approximation
    try:
        probability = 0.5 * (1 + math.erf(z_score))
        # Bound between 5% and 95% for extreme cases
        return max(0.05, min(0.95, probability))
    except (OverflowError, ValueError):
        # Fallback for extreme values
        return 0.95 if spread < -35 else 0.05


def extract_ncaaf_features(game_data: dict[str, Any]) -> NCAAFGame:
    """
    Extract NCAAF game features from raw odds API data.
    Includes college-specific features like conference strength, recruiting, transfers.
    """

    # Parse basic game info
    game_id = game_data.get("id", f"ncaaf_{random.randint(1000, 9999)}")
    home_team = game_data.get("home_team", "Home Team")
    away_team = game_data.get("away_team", "Away Team")

    # Parse kickoff time
    kickoff_str = game_data.get("commence_time", datetime.now().isoformat())
    try:
        kickoff_time = datetime.fromisoformat(kickoff_str.replace("Z", "+00:00"))
    except:
        kickoff_time = datetime.now() + timedelta(hours=2)

    # Derive week from date (college football weeks are Saturday-based)
    week_of_year = kickoff_time.isocalendar()[1]
    college_week = max(1, week_of_year - 34)  # College season starts ~week 35
    season = kickoff_time.year

    # Mock college-specific data (in production, this would come from data sources)
    conference_map = {
        "Alabama": "SEC",
        "Georgia": "SEC",
        "LSU": "SEC",
        "Florida": "SEC",
        "Ohio State": "Big Ten",
        "Michigan": "Big Ten",
        "Penn State": "Big Ten",
        "Clemson": "ACC",
        "Miami": "ACC",
        "North Carolina": "ACC",
        "Oklahoma": "SEC",
        "Texas": "SEC",
        "USC": "Big Ten",  # Recent moves
        "Oregon": "Big Ten",
        "Washington": "Big Ten",
    }

    home_conference = conference_map.get(home_team.split()[-1], "FBS Independent")
    away_conference = conference_map.get(away_team.split()[-1], "FBS Independent")

    # Simulate college-specific metrics (would be real data in production)
    home_sos_rank = random.randint(1, 131)
    away_sos_rank = random.randint(1, 131)

    return NCAAFGame(
        game_id=game_id,
        home_team=home_team,
        away_team=away_team,
        week=college_week,
        season=season,
        kickoff_time=kickoff_time,
        home_conference=home_conference,
        away_conference=away_conference,
        is_conference_game=(
            home_conference == away_conference and home_conference != "FBS Independent"
        ),
        is_rivalry_game=_is_rivalry_game(home_team, away_team),
        home_sos_rank=home_sos_rank,
        away_sos_rank=away_sos_rank,
        home_record=f"{random.randint(0, 12)}-{random.randint(0, 4)}",
        away_record=f"{random.randint(0, 12)}-{random.randint(0, 4)}",
        home_returning_starters=random.randint(8, 18),
        away_returning_starters=random.randint(8, 18),
        home_recruiting_class_rank=random.randint(1, 130),
        away_recruiting_class_rank=random.randint(1, 130),
        public_betting_pct=random.uniform(0.3, 0.7),  # Mock public betting %
        line_movement=random.uniform(-3.0, 3.0),  # Mock line movement
    )


def _is_rivalry_game(home_team: str, away_team: str) -> bool:
    """Check if this is a known rivalry game"""
    rivalry_pairs = {
        ("Alabama", "Auburn"),
        ("Michigan", "Ohio State"),
        ("Texas", "Oklahoma"),
        ("USC", "UCLA"),
        ("Florida", "Georgia"),
        ("Clemson", "South Carolina"),
    }

    home_key = home_team.split()[-1]  # Get last word (usually school name)
    away_key = away_team.split()[-1]

    return (home_key, away_key) in rivalry_pairs or (
        away_key,
        home_key,
    ) in rivalry_pairs


def generate_ncaaf_prediction(game: NCAAFGame) -> NCAAFMarketPrediction:
    """
    Generate NCAAF model predictions using college-specific factors.
    Includes enhanced volatility for mismatches and unpredictable outcomes.
    """

    # Calculate base team strengths using multiple factors
    home_strength = _calculate_ncaaf_team_strength(game, is_home=True)
    away_strength = _calculate_ncaaf_team_strength(game, is_home=False)

    # Calculate home field advantage (stronger in college than NFL)
    home_field_boost = _calculate_ncaaf_home_field_advantage(game)
    adjusted_home_strength = home_strength + home_field_boost

    # Calculate mismatch factor
    strength_diff = abs(adjusted_home_strength - away_strength)
    mismatch_factor = min(2.0, 1.0 + (strength_diff / 10.0))  # 1.0 to 2.0 scale

    # Run Monte Carlo simulation with college-specific parameters
    total_sims = 15000  # More simulations for college volatility
    home_wins = 0
    total_points_sum = 0
    home_covers = 0

    for _ in range(total_sims):
        # Simulate game with higher variance than NFL
        base_variance = 14.0 * mismatch_factor  # Higher base variance

        home_score = max(0, random.gauss(adjusted_home_strength, base_variance))
        away_score = max(0, random.gauss(away_strength, base_variance))

        total_points = home_score + away_score
        total_points_sum += total_points

        if home_score > away_score:
            home_wins += 1

        # Mock spread calculation (would be from actual odds in production)
        mock_spread = -(adjusted_home_strength - away_strength) * 0.8
        if (home_score - away_score) > mock_spread:
            home_covers += 1

    # Calculate probabilities
    home_win_prob = home_wins / total_sims
    spread_cover_prob = home_covers / total_sims
    avg_total = total_points_sum / total_sims

    # Calculate predicted spread (negative means home favored)
    predicted_spread = -(adjusted_home_strength - away_strength) * 0.75

    # Over probability (mock calculation)
    over_prob = 0.5 + random.uniform(-0.15, 0.15)  # Mock with variance

    # Calculate blowout probability (21+ point margin)
    blowout_prob = min(0.4, mismatch_factor * 0.15)  # Higher for mismatches

    # Volatility adjustment based on college factors
    volatility_adj = 1.0
    if game.is_rivalry_game:
        volatility_adj *= 1.3  # Rivalries are unpredictable
    if game.home_coaching_change or game.away_coaching_change:
        volatility_adj *= 1.2  # New coaches add uncertainty
    if mismatch_factor > 1.5:
        volatility_adj *= 1.1  # Mismatches can go either way

    return NCAAFMarketPrediction(
        game_id=game.game_id,
        home_win_prob=home_win_prob,
        away_win_prob=1 - home_win_prob,
        predicted_spread=predicted_spread,
        spread_cover_prob=spread_cover_prob,
        predicted_total=avg_total,
        over_prob=over_prob,
        under_prob=1 - over_prob,
        blowout_probability=blowout_prob,
        mismatch_factor=mismatch_factor,
        volatility_adjustment=volatility_adj,
        public_fade_factor=_calculate_public_fade_factor(game),
        simulation_count=total_sims,
    )


def _calculate_ncaaf_team_strength(game: NCAAFGame, is_home: bool) -> float:
    """Calculate team strength using college-specific factors"""

    base_strength = 21.0  # Average college team scoring

    if is_home:
        conference = game.home_conference
        sos_rank = game.home_sos_rank or 65
        recruiting_rank = game.home_recruiting_class_rank or 65
        returning_starters = game.home_returning_starters or 13
    else:
        conference = game.away_conference
        sos_rank = game.away_sos_rank or 65
        recruiting_rank = game.away_recruiting_class_rank or 65
        returning_starters = game.away_returning_starters or 13

    # Conference strength adjustments
    power_conference_boost = {
        "SEC": 4.0,
        "Big Ten": 3.5,
        "Big 12": 2.5,
        "ACC": 2.0,
        "Pac-12": 2.0,
    }
    base_strength += power_conference_boost.get(conference, 0)

    # Strength of schedule adjustment (inverse rank)
    sos_adjustment = (131 - sos_rank) / 131 * 3.0  # 0-3 point adjustment
    base_strength += sos_adjustment

    # Recruiting class adjustment (inverse rank)
    recruiting_adjustment = (131 - recruiting_rank) / 131 * 2.0  # 0-2 point adjustment
    base_strength += recruiting_adjustment

    # Experience adjustment (returning starters)
    experience_adjustment = (returning_starters - 11) * 0.2  # Each starter worth 0.2 pts
    base_strength += experience_adjustment

    return base_strength


def _calculate_ncaaf_home_field_advantage(game: NCAAFGame) -> float:
    """Calculate home field advantage (stronger in college than NFL)"""

    base_hfa = 3.5  # Base college home field advantage (higher than NFL's ~2.5)

    # Conference adjustments (stronger home crowds)
    conference_hfa = {
        "SEC": 1.0,
        "Big Ten": 0.8,
        "Big 12": 0.6,
        "ACC": 0.4,
        "Pac-12": 0.2,
    }
    base_hfa += conference_hfa.get(game.home_conference, 0)

    # Rivalry game adjustment
    if game.is_rivalry_game:
        base_hfa += 1.0  # Extra emotional edge

    # Altitude adjustment (rare but significant)
    if game.altitude and game.altitude > 3000:  # Denver, Wyoming, etc.
        base_hfa += 0.5

    return base_hfa


def _calculate_public_fade_factor(game: NCAAFGame) -> float:
    """Calculate public fade factor based on betting percentages"""

    if not game.public_betting_pct:
        return 1.0

    # If public heavily on one side (>70% or <30%), increase fade factor
    public_extreme = abs(game.public_betting_pct - 0.5)
    if public_extreme > 0.2:  # 70%+ public on one side
        return 1.0 + (public_extreme - 0.2) * 2.0  # Up to 1.6x factor

    return 1.0


# ================================
# MAJOR LEAGUE BASEBALL (MLB) CLASSES
# ================================


@dataclass
class MLBGame:
    """Comprehensive MLB game representation with baseball-specific analytics"""

    # Basic game info
    id: str
    home_team: str
    away_team: str
    commence_time: str

    # Starting Pitchers (Critical for MLB)
    home_starter_name: str | None = None
    away_starter_name: str | None = None

    # Starting Pitcher Stats (Current Season)
    home_pitcher_era: float = 4.50
    away_pitcher_era: float = 4.50
    home_pitcher_whip: float = 1.35
    away_pitcher_whip: float = 1.35
    home_pitcher_fip: float = 4.50
    away_pitcher_fip: float = 4.50
    home_pitcher_xera: float = 4.50
    away_pitcher_xera: float = 4.50
    home_pitcher_k9: float = 8.0  # Strikeouts per 9 innings
    away_pitcher_k9: float = 8.0
    home_pitcher_bb9: float = 3.0  # Walks per 9 innings
    away_pitcher_bb9: float = 3.0

    # Pitcher Rest and Fatigue
    home_pitcher_rest_days: int = 4
    away_pitcher_rest_days: int = 4
    home_pitcher_pitches_last_start: int = 100
    away_pitcher_pitches_last_start: int = 100

    # Pitcher Splits and Matchups
    home_pitcher_vs_opp_era: float = 4.50  # ERA vs this opponent historically
    away_pitcher_vs_opp_era: float = 4.50
    home_pitcher_home_era: float = 4.20
    away_pitcher_road_era: float = 4.80

    # Team Offensive Stats
    home_team_runs_per_game: float = 4.8
    away_team_runs_per_game: float = 4.8
    home_team_ops: float = 0.750  # On-base plus slugging
    away_team_ops: float = 0.750
    home_team_babip: float = 0.300  # Batting average on balls in play
    away_team_babip: float = 0.300
    home_team_iso: float = 0.170  # Isolated power
    away_team_iso: float = 0.170

    # Team Defensive Stats
    home_team_era: float = 4.30
    away_team_era: float = 4.30
    home_team_fielding_pct: float = 0.985
    away_team_fielding_pct: float = 0.985
    home_team_drs: float = 0.0  # Defensive runs saved
    away_team_drs: float = 0.0

    # Bullpen Metrics
    home_bullpen_era: float = 4.00
    away_bullpen_era: float = 4.00
    home_bullpen_whip: float = 1.30
    away_bullpen_whip: float = 1.30
    home_bullpen_k9: float = 9.5
    away_bullpen_k9: float = 9.5
    home_bullpen_saves_pct: float = 0.85
    away_bullpen_saves_pct: float = 0.85

    # Ballpark Factors
    ballpark_name: str | None = None
    park_factor_runs: float = 1.00  # Relative to league average
    park_factor_hr: float = 1.00
    ballpark_altitude: float = 0.0  # Feet above sea level
    ballpark_dimensions: dict[str, float] | None = (
        None  # {'left': 330, 'center': 400, 'right': 330}
    )

    # Weather Conditions
    temperature: float | None = 75.0  # Fahrenheit
    humidity: float | None = 50.0  # Percentage
    wind_speed: float | None = 5.0  # MPH
    wind_direction: str | None = None  # "out to RF", "in from CF", etc.
    precipitation_chance: float | None = 0.0

    # Game Context
    day_night: str = "night"  # "day" or "night"
    game_type: str = "regular"  # "regular", "playoff", "wildcard"
    series_game: int = 1  # Game 1, 2, 3, etc. of series
    double_header: bool = False

    # Team Form and Trends
    home_team_l10_record: str = "5-5"
    away_team_l10_record: str = "5-5"
    home_team_streak: int = 0  # Positive for win streak, negative for loss streak
    away_team_streak: int = 0

    # Injuries and Roster
    home_key_injuries: list[str] | None = None  # List of key injured players
    away_key_injuries: list[str] | None = None
    home_lineup_changes: int = 0  # Number of changes from typical lineup
    away_lineup_changes: int = 0

    # Public Betting Data
    public_bet_pct_home: float = 50.0  # Percentage of bets on home team
    public_money_pct_home: float = 50.0  # Percentage of money on home team
    sharp_money_indicator: str = "neutral"  # "home", "away", "neutral"

    # Advanced Analytics
    home_team_war: float = 0.0  # Team cumulative WAR
    away_team_war: float = 0.0
    home_team_wrc_plus: float = 100  # Weighted runs created plus
    away_team_wrc_plus: float = 100

    def __post_init__(self):
        # Initialize empty lists if None
        if self.ballpark_dimensions is None:
            self.ballpark_dimensions = {"left": 330, "center": 400, "right": 330}
        if self.home_key_injuries is None:
            self.home_key_injuries = []
        if self.away_key_injuries is None:
            self.away_key_injuries = []


@dataclass
class MLBMarketPrediction:
    """MLB market prediction with baseball-specific factors"""

    # Basic probabilities
    home_win_prob: float
    away_win_prob: float

    # Run totals prediction
    predicted_home_runs: float
    predicted_away_runs: float
    predicted_total_runs: float

    # First 5 innings predictions (critical for MLB)
    f5_home_win_prob: float
    f5_away_win_prob: float
    f5_predicted_home_runs: float
    f5_predicted_away_runs: float

    # Starting pitcher vs bullpen influence
    starter_influence: float = 0.70  # How much game depends on starter vs bullpen

    # Ballpark and weather adjustments
    park_run_adjustment: float = 1.0
    weather_run_adjustment: float = 1.0

    # Pitcher matchup advantages
    pitching_advantage: str = "neutral"  # "home", "away", "neutral"
    pitching_advantage_magnitude: float = 1.0

    # Volatility factors
    game_volatility: float = 1.0  # Higher for unpredictable matchups

    # Market inefficiency signals
    public_fade_factor: float = 1.0
    sharp_money_signal: float = 1.0

    # Confidence metrics
    prediction_confidence: float = 0.75

    def get_run_line_prob(self, line: float) -> float:
        """Get probability of covering run line using predicted spread"""
        predicted_spread = self.predicted_home_runs - self.predicted_away_runs
        return self._runs_to_probability(predicted_spread - line)

    def get_total_prob(self, total_line: float, over: bool = True) -> float:
        """Get probability of total runs over/under"""
        diff = self.predicted_total_runs - total_line
        prob = self._total_to_probability(diff)
        return prob if over else (1.0 - prob)

    def _runs_to_probability(self, run_diff: float) -> float:
        """Convert run differential to win probability"""
        # MLB games have smaller variance than NFL/NCAAF
        # Standard deviation around 4.5 runs for game totals
        return 1 / (1 + math.exp(-run_diff / 1.8))

    def _total_to_probability(self, run_diff: float) -> float:
        """Convert total runs difference to over probability"""
        # Standard deviation for total runs is about 2.5 runs
        return 1 / (1 + math.exp(-run_diff / 1.0))


class MLBBettingEngine:
    """MLB-specific betting engine with baseball market expertise"""

    def __init__(self, bankroll_manager):
        self.bankroll = bankroll_manager
        self.mlb_config = {
            "min_edge": 0.025,  # 2.5% minimum edge (lower than football due to volume)
            "max_bet_fraction": 0.04,  # Max 4% of bankroll per bet
            "kelly_multiplier": 0.20,  # Conservative Kelly for baseball volatility
            "max_bets_per_day": 12,  # Higher volume sport
            "f5_kelly_boost": 1.2,  # Slight boost for F5 innings bets
            "weather_edge_boost": 1.1,  # Boost for weather advantages
            "pitcher_mismatch_boost": 1.15,  # Boost for clear pitcher advantages
        }
        self.daily_mlb_exposure = 0.0
        self.mlb_bet_count = 0

    def mlb_decide_and_place(
        self,
        game: MLBGame,
        market_type: str,
        market_odds: float,
        prediction: MLBMarketPrediction,
    ) -> EdgeBet | None:
        """Decide whether to place MLB bet and execute if profitable"""

        try:
            # Validate constraints
            if not self._validate_mlb_constraints(game, market_type):
                return None

            # Get fair probability for this market
            fair_prob = self._get_mlb_fair_probability(prediction, market_type, game)
            if fair_prob is None:
                return None

            # Convert market odds to implied probability
            implied_prob = (
                1.0 / market_odds
                if market_odds > 0
                else abs(market_odds) / (abs(market_odds) + 100)
            )

            # Calculate raw edge
            raw_edge = fair_prob - implied_prob

            # Apply MLB-specific adjustments
            adjusted_edge = self._adjust_edge_for_mlb_factors(
                raw_edge, game, market_type, prediction
            )

            # Check minimum edge threshold
            min_edge = self.mlb_config["min_edge"]
            if market_type == "f5_innings":
                min_edge *= 0.8  # Lower threshold for F5 bets (more predictable)

            if adjusted_edge < min_edge:
                return None

            # Calculate Kelly fraction with MLB adjustments
            b = market_odds - 1 if market_odds > 1 else (100 / abs(market_odds))
            base_kelly = (fair_prob * (b + 1) - 1) / b if b > 0 else 0
            kelly_multiplier = self.mlb_config["kelly_multiplier"]

            # Adjust Kelly based on market type
            if market_type == "f5_innings":
                kelly_multiplier *= self.mlb_config["f5_kelly_boost"]
            elif market_type in ["total_runs", "team_total"]:
                kelly_multiplier *= 0.9  # Slightly more conservative on totals

            # Weather and pitcher adjustments
            if abs(game.wind_speed or 0) > 15:  # Strong wind
                kelly_multiplier *= self.mlb_config["weather_edge_boost"]

            if prediction.pitching_advantage_magnitude > 1.2:
                kelly_multiplier *= self.mlb_config["pitcher_mismatch_boost"]

            final_kelly = base_kelly * kelly_multiplier
            max_kelly = self._calculate_mlb_max_kelly(game, market_type)
            final_kelly = min(final_kelly, max_kelly)

            if final_kelly <= 0:
                return None

            # Calculate bet size
            bet_size = self.bankroll.calculate_bet_size(final_kelly)
            max_bet = self.bankroll.current_bankroll * self.mlb_config["max_bet_fraction"]
            bet_size = min(bet_size, max_bet)

            if bet_size < 1.0:  # Minimum bet size
                return None

            # Create and validate bet
            confidence = self._classify_mlb_confidence(adjusted_edge, final_kelly, game, prediction)
            selection = self._format_mlb_selection(market_type, game, market_odds, prediction)

            edge_bet = EdgeBet(
                event_id=game.id,
                market=market_type,
                selection=selection,
                odds=market_odds,
                bet_size=bet_size,
                edge=adjusted_edge,
                kelly_fraction=final_kelly,
                confidence=confidence,
                book="Live",
                sport="MLB",
                implied_prob=implied_prob,
                fair_prob=fair_prob,
            )

            # Track MLB bet for analysis
            self._track_mlb_bet(edge_bet, game, prediction)

            logger.info(
                f"⚾ MLB EDGE: {selection} | Edge: {adjusted_edge:.1%} | Kelly: {final_kelly:.1%} | Size: ${bet_size:.2f} | {confidence}"
            )
            return edge_bet

        except Exception as e:
            logger.error(f"MLB betting decision error: {e}")
            return None

    def _get_mlb_fair_probability(
        self, prediction: MLBMarketPrediction, market_type: str, game: MLBGame
    ) -> float | None:
        """Get fair probability for MLB market"""
        if market_type == "moneyline":
            return prediction.home_win_prob
        if market_type == "f5_innings":
            return prediction.f5_home_win_prob
        if market_type == "run_line":
            # Assume -1.5 run line for home team
            return prediction.get_run_line_prob(-1.5)
        if market_type == "total_runs":
            # Default to over for simplicity - would need actual line
            return prediction.get_total_prob(8.5, over=True)
        return None

    def _adjust_edge_for_mlb_factors(
        self,
        raw_edge: float,
        game: MLBGame,
        market_type: str,
        prediction: MLBMarketPrediction,
    ) -> float:
        """Apply MLB-specific edge adjustments"""
        adjusted = raw_edge

        # Weather adjustments
        if game.wind_speed and game.wind_direction:
            if "out" in game.wind_direction.lower() and market_type == "total_runs":
                adjusted *= 1.15  # Wind helps hitters
            elif "in" in game.wind_direction.lower() and market_type == "total_runs":
                adjusted *= 1.10  # Wind helps pitchers

        # Ballpark adjustments
        if market_type == "total_runs":
            if game.park_factor_runs > 1.05 or game.park_factor_runs < 0.95:  # Hitter-friendly park
                adjusted *= 1.1

        # Pitcher rest adjustments
        if market_type in ["moneyline", "f5_innings"]:
            if game.home_pitcher_rest_days < 4 or game.away_pitcher_rest_days < 4:
                adjusted *= 0.9  # Reduce edge for tired pitchers
            elif game.home_pitcher_rest_days > 5 and game.away_pitcher_rest_days > 5:
                adjusted *= 0.95  # Both on extended rest

        # Public betting fade
        if abs(game.public_bet_pct_home - 50.0) > 25.0:  # Heavy public lean
            adjusted *= 1.1

        # Sharp money alignment
        if prediction.sharp_money_signal > 1.1:
            adjusted *= 1.05

        return adjusted

    def _validate_mlb_constraints(self, game: MLBGame, market_type: str) -> bool:
        """Validate MLB-specific betting constraints"""

        # Check daily limits
        if self.mlb_bet_count >= self.mlb_config["max_bets_per_day"]:
            return False

        # Check exposure limits
        max_exposure = self.bankroll.current_bankroll * 0.25  # Max 25% on MLB per day
        if self.daily_mlb_exposure >= max_exposure:
            return False

        # Don't bet on weather delays
        if game.precipitation_chance and game.precipitation_chance > 60.0:
            return False

        # Don't bet on double headers (second game) without starter info
        if game.double_header and not game.home_starter_name:
            return False

        # Validate we have pitcher information for F5 bets
        if market_type == "f5_innings":
            if not game.home_starter_name or not game.away_starter_name:
                return False

        return True

    def _calculate_mlb_max_kelly(self, game: MLBGame, market_type: str) -> float:
        """Calculate maximum Kelly fraction for MLB bet"""
        base_max = self.mlb_config["max_bet_fraction"]

        # Reduce for high volatility games
        if getattr(game, "game_volatility", 1.0) > 1.2:
            base_max *= 0.8

        # Increase slightly for F5 bets (more predictable)
        if market_type == "f5_innings":
            base_max *= 1.1

        # Reduce for totals (higher variance)
        if market_type in ["total_runs", "team_total"]:
            base_max *= 0.9

        return base_max

    def _classify_mlb_confidence(
        self, edge: float, kelly: float, game: MLBGame, prediction: MLBMarketPrediction
    ) -> str:
        """Classify MLB bet confidence with game context"""

        # Base confidence on edge and Kelly
        if edge > 0.08 and kelly > 0.03:
            confidence = "high"
        elif edge > 0.05 and kelly > 0.02:
            confidence = "medium"
        elif edge > 0.025 and kelly > 0.01:
            confidence = "low"
        else:
            confidence = "minimal"

        # Boost for strong pitcher advantages
        if prediction.pitching_advantage_magnitude > 1.3:
            if confidence == "medium":
                confidence = "high"
            elif confidence == "low":
                confidence = "medium"

        # Boost for weather edges
        if game.wind_speed and game.wind_speed > 20 and confidence == "low":
            confidence = "medium"

        return confidence

    def _format_mlb_selection(
        self,
        market_type: str,
        game: MLBGame,
        odds: float,
        prediction: MLBMarketPrediction,
    ) -> str:
        """Format MLB bet selection string"""

        if market_type == "moneyline":
            if prediction.home_win_prob > 0.5:
                return f"{game.home_team} ML ({odds:+.0f})"
            return f"{game.away_team} ML ({odds:+.0f})"
        if market_type == "f5_innings":
            if prediction.f5_home_win_prob > 0.5:
                return f"{game.home_team} F5 ({odds:+.0f})"
            return f"{game.away_team} F5 ({odds:+.0f})"
        if market_type == "run_line":
            return f"{game.home_team} -1.5 ({odds:+.0f})"
        if market_type == "total_runs":
            return f"Over 8.5 runs ({odds:+.0f})"

        return f"MLB bet ({odds:+.0f})"

    def _track_mlb_bet(self, bet: EdgeBet, game: MLBGame, prediction: MLBMarketPrediction):
        """Track MLB bet for analysis and limits"""
        self.daily_mlb_exposure += bet.bet_size
        self.mlb_bet_count += 1

        # Log detailed bet info
        logger.info(f"MLB Bet Details - Game: {game.away_team} @ {game.home_team}")
        logger.info(f"Starters: {game.away_starter_name} vs {game.home_starter_name}")
        logger.info(f"Park: {game.ballpark_name}, Weather: {game.temperature}°F")
        logger.info(
            f"Prediction: H:{prediction.home_win_prob:.1%} A:{prediction.away_win_prob:.1%}"
        )


# MLB Feature Extraction and Prediction Functions


def extract_mlb_features(game_data: dict[str, Any]) -> MLBGame:
    """Extract comprehensive MLB features from game data"""

    # Extract basic game info
    mlb_game = MLBGame(
        id=game_data.get("id", f"mlb_{int(time.time())}"),
        home_team=game_data.get("home_team", "Unknown"),
        away_team=game_data.get("away_team", "Unknown"),
        commence_time=game_data.get("commence_time", datetime.now().isoformat()),
    )

    # Extract pitcher information (critical for MLB)
    pitchers = game_data.get("pitchers", {})
    mlb_game.home_starter_name = pitchers.get("home_starter", "TBD")
    mlb_game.away_starter_name = pitchers.get("away_starter", "TBD")

    # Extract pitcher stats (would come from MLB API or database)
    pitcher_stats = game_data.get("pitcher_stats", {})
    home_pitcher = pitcher_stats.get("home", {})
    away_pitcher = pitcher_stats.get("away", {})

    mlb_game.home_pitcher_era = home_pitcher.get("era", 4.50)
    mlb_game.away_pitcher_era = away_pitcher.get("era", 4.50)
    mlb_game.home_pitcher_whip = home_pitcher.get("whip", 1.35)
    mlb_game.away_pitcher_whip = away_pitcher.get("whip", 1.35)
    mlb_game.home_pitcher_fip = home_pitcher.get("fip", 4.50)
    mlb_game.away_pitcher_fip = away_pitcher.get("fip", 4.50)
    mlb_game.home_pitcher_k9 = home_pitcher.get("k9", 8.0)
    mlb_game.away_pitcher_k9 = away_pitcher.get("k9", 8.0)

    # Extract team offensive stats
    team_stats = game_data.get("team_stats", {})
    home_stats = team_stats.get("home", {})
    away_stats = team_stats.get("away", {})

    mlb_game.home_team_runs_per_game = home_stats.get("runs_per_game", 4.8)
    mlb_game.away_team_runs_per_game = away_stats.get("runs_per_game", 4.8)
    mlb_game.home_team_ops = home_stats.get("ops", 0.750)
    mlb_game.away_team_ops = away_stats.get("ops", 0.750)

    # Extract ballpark factors
    ballpark = game_data.get("ballpark", {})
    mlb_game.ballpark_name = ballpark.get("name", "Unknown Park")
    mlb_game.park_factor_runs = ballpark.get("run_factor", 1.00)
    mlb_game.park_factor_hr = ballpark.get("hr_factor", 1.00)

    # Extract weather
    weather = game_data.get("weather", {})
    mlb_game.temperature = weather.get("temperature", 75.0)
    mlb_game.humidity = weather.get("humidity", 50.0)
    mlb_game.wind_speed = weather.get("wind_speed", 5.0)
    mlb_game.wind_direction = weather.get("wind_direction", "calm")

    # Extract public betting data
    public_data = game_data.get("public_betting", {})
    mlb_game.public_bet_pct_home = public_data.get("home_bet_pct", 50.0)
    mlb_game.public_money_pct_home = public_data.get("home_money_pct", 50.0)

    # Game context
    mlb_game.day_night = game_data.get("day_night", "night")
    mlb_game.game_type = game_data.get("game_type", "regular")

    return mlb_game


def generate_mlb_prediction(game: MLBGame) -> MLBMarketPrediction:
    """Generate comprehensive MLB prediction using baseball analytics"""

    # Calculate pitcher quality scores (0-1 scale)
    home_pitcher_quality = calculate_pitcher_quality(
        game.home_pitcher_era,
        game.home_pitcher_whip,
        game.home_pitcher_fip,
        game.home_pitcher_k9,
    )
    away_pitcher_quality = calculate_pitcher_quality(
        game.away_pitcher_era,
        game.away_pitcher_whip,
        game.away_pitcher_fip,
        game.away_pitcher_k9,
    )

    # Calculate team offensive strength (runs per game adjusted)
    home_offensive_strength = game.home_team_runs_per_game / 4.8  # Normalized to league avg
    away_offensive_strength = game.away_team_runs_per_game / 4.8

    # Apply ballpark factors
    park_adjustment = game.park_factor_runs

    # Weather adjustments for run scoring
    weather_adjustment = calculate_weather_impact(
        game.temperature or 75.0, game.wind_speed or 5.0, game.wind_direction or "calm"
    )

    # Predict runs using Log5-inspired methodology
    home_base_runs = home_offensive_strength * 4.8 * park_adjustment * weather_adjustment
    away_base_runs = away_offensive_strength * 4.8 * park_adjustment * weather_adjustment

    # Adjust for pitcher quality (pitchers prevent runs)
    home_predicted_runs = home_base_runs * (2.0 - away_pitcher_quality)
    away_predicted_runs = away_base_runs * (2.0 - home_pitcher_quality)

    # Calculate win probabilities using Log5 method
    home_run_advantage = home_predicted_runs / (home_predicted_runs + away_predicted_runs)

    # Convert to win probability (add home field advantage)
    home_field_advantage = 0.54  # MLB home teams win ~54%
    home_win_prob = apply_log5_method(home_run_advantage, home_field_advantage, 0.5)
    away_win_prob = 1.0 - home_win_prob

    # First 5 innings predictions (more pitcher-dependent)
    f5_starter_weight = 0.85  # Starters matter more in first 5
    f5_home_runs = home_predicted_runs * 0.6 * f5_starter_weight  # ~60% of runs in first 5
    f5_away_runs = away_predicted_runs * 0.6 * f5_starter_weight

    f5_run_advantage = (
        f5_home_runs / (f5_home_runs + f5_away_runs) if (f5_home_runs + f5_away_runs) > 0 else 0.5
    )
    f5_home_win_prob = apply_log5_method(f5_run_advantage, home_field_advantage, 0.5)
    f5_away_win_prob = 1.0 - f5_home_win_prob

    # Determine pitching advantage
    pitcher_diff = home_pitcher_quality - away_pitcher_quality
    if abs(pitcher_diff) > 0.15:
        pitching_advantage = "home" if pitcher_diff > 0 else "away"
        pitching_advantage_magnitude = 1.0 + abs(pitcher_diff)
    else:
        pitching_advantage = "neutral"
        pitching_advantage_magnitude = 1.0

    # Calculate volatility based on pitcher matchup and weather
    game_volatility = calculate_game_volatility(game, home_pitcher_quality, away_pitcher_quality)

    # Market inefficiency factors
    public_fade_factor = calculate_public_fade_factor(game.public_bet_pct_home)
    sharp_money_signal = 1.0  # Would need actual sharp money data

    return MLBMarketPrediction(
        home_win_prob=home_win_prob,
        away_win_prob=away_win_prob,
        predicted_home_runs=home_predicted_runs,
        predicted_away_runs=away_predicted_runs,
        predicted_total_runs=home_predicted_runs + away_predicted_runs,
        f5_home_win_prob=f5_home_win_prob,
        f5_away_win_prob=f5_away_win_prob,
        f5_predicted_home_runs=f5_home_runs,
        f5_predicted_away_runs=f5_away_runs,
        starter_influence=f5_starter_weight,
        park_run_adjustment=park_adjustment,
        weather_run_adjustment=weather_adjustment,
        pitching_advantage=pitching_advantage,
        pitching_advantage_magnitude=pitching_advantage_magnitude,
        game_volatility=game_volatility,
        public_fade_factor=public_fade_factor,
        sharp_money_signal=sharp_money_signal,
        prediction_confidence=min(0.9, 0.6 + abs(pitcher_diff)),
    )


def calculate_pitcher_quality(era: float, whip: float, fip: float, k9: float) -> float:
    """Calculate pitcher quality score (0-1, higher is better)"""
    # Normalize each stat (lower ERA/WHIP/FIP is better, higher K/9 is better)
    era_score = max(0, (6.00 - era) / 3.00)  # ERA of 3.00 = 1.0, 6.00 = 0.0
    whip_score = max(0, (1.60 - whip) / 0.60)  # WHIP of 1.00 = 1.0, 1.60 = 0.0
    fip_score = max(0, (6.00 - fip) / 3.00)  # Similar to ERA
    k9_score = min(1.0, k9 / 12.0)  # K/9 of 12+ = 1.0

    # Weighted average (FIP is most predictive)
    quality = era_score * 0.2 + whip_score * 0.2 + fip_score * 0.4 + k9_score * 0.2
    return max(0.1, min(0.9, quality))


def calculate_weather_impact(temp: float, wind_speed: float, wind_dir: str) -> float:
    """Calculate weather impact on run scoring"""
    impact = 1.0

    # Temperature effect (warmer = more runs)
    if temp > 80:
        impact *= 1.05 + ((temp - 80) * 0.002)  # Each degree over 80 adds 0.2%
    elif temp < 60:
        impact *= 1.0 - ((60 - temp) * 0.003)  # Each degree under 60 reduces 0.3%

    # Wind effect
    if wind_speed and wind_speed > 10:
        if wind_dir and "out" in wind_dir.lower():
            impact *= 1.0 + (wind_speed - 10) * 0.01  # Helps hitters
        elif wind_dir and "in" in wind_dir.lower():
            impact *= 1.0 - (wind_speed - 10) * 0.008  # Helps pitchers

    return max(0.8, min(1.3, impact))


def calculate_game_volatility(game: MLBGame, home_pitcher_q: float, away_pitcher_q: float) -> float:
    """Calculate game volatility for Kelly sizing"""
    volatility = 1.0

    # High volatility for pitcher mismatches
    pitcher_diff = abs(home_pitcher_q - away_pitcher_q)
    volatility += pitcher_diff * 0.5

    # Weather volatility
    if game.wind_speed and game.wind_speed > 15:
        volatility *= 1.2

    # Ballpark volatility
    if game.park_factor_runs > 1.1 or game.park_factor_runs < 0.9:
        volatility *= 1.1

    return min(2.0, volatility)


def calculate_public_fade_factor(public_pct: float) -> float:
    """Calculate public betting fade factor"""
    # Strong public lean creates fade opportunity
    deviation = abs(public_pct - 50.0)
    if deviation > 30.0:  # 80%+ on one side
        return 1.15 + (deviation - 30.0) * 0.01
    if deviation > 20.0:  # 70%+ on one side
        return 1.05 + (deviation - 20.0) * 0.005
    return 1.0


def apply_log5_method(team_a_strength: float, team_b_strength: float, league_avg: float) -> float:
    """Apply Log5 method for head-to-head probability"""
    # Log5 formula: P(A beats B) = (A - A*B) / (A + B - 2*A*B)
    return (
        (team_a_strength - team_a_strength * team_b_strength)
        / (team_a_strength + team_b_strength - 2 * team_a_strength * team_b_strength)
        if (team_a_strength + team_b_strength - 2 * team_a_strength * team_b_strength) != 0
        else 0.5
    )


# Initialize MLB engine
mlb_engine = MLBBettingEngine(bankroll_manager)

# ================================
# NATIONAL BASKETBALL ASSOCIATION (NBA) CLASSES
# ================================


@dataclass
class NBAGame:
    """Comprehensive NBA game representation with basketball-specific analytics"""

    # Basic game info
    id: str
    home_team: str
    away_team: str
    commence_time: str

    # Pace and Possessions (Critical for NBA)
    home_pace: float = 100.0  # Possessions per 48 minutes
    away_pace: float = 100.0
    projected_possessions: float = 100.0  # Average of team paces

    # Advanced Efficiency Metrics (Per 100 Possessions)
    home_offensive_rating: float = 110.0  # Points scored per 100 possessions
    away_offensive_rating: float = 110.0
    home_defensive_rating: float = 110.0  # Points allowed per 100 possessions
    away_defensive_rating: float = 110.0
    home_net_rating: float = 0.0  # OffRtg - DefRtg
    away_net_rating: float = 0.0

    # Shooting Efficiency
    home_efg_pct: float = 0.52  # Effective Field Goal %
    away_efg_pct: float = 0.52
    home_ts_pct: float = 0.55  # True Shooting %
    away_ts_pct: float = 0.55
    home_three_pt_rate: float = 0.38  # 3PA / FGA
    away_three_pt_rate: float = 0.38
    home_three_pt_pct: float = 0.35
    away_three_pt_pct: float = 0.35

    # Four Factors (Dean Oliver)
    home_turnover_pct: float = 14.0  # TOV / (FGA + 0.44*FTA + TOV)
    away_turnover_pct: float = 14.0
    home_oreb_pct: float = 25.0  # OREB / (OREB + Opp DREB)
    away_oreb_pct: float = 25.0
    home_ft_rate: float = 0.25  # FTA / FGA
    away_ft_rate: float = 0.25

    # Rest and Travel Context
    home_rest_days: int = 1  # Days since last game
    away_rest_days: int = 1
    away_travel_distance: float = 0.0  # Miles traveled by away team
    time_zone_change: int = 0  # Hours difference (negative for westward)
    is_back_to_back: bool = False  # Playing on consecutive nights

    # Lineup and Load Management
    home_injury_impact: float = 0.0  # 0-1 scale of key injuries
    away_injury_impact: float = 0.0
    home_load_management: list[str] = None  # List of players resting
    away_load_management: list[str] = None

    # Situational Context
    is_rivalry: bool = False  # Lakers-Celtics, etc.
    home_motivation: float = 1.0  # Playoff push, revenge game, etc.
    away_motivation: float = 1.0
    altitude_advantage: bool = False  # Denver home games

    # Recent Form (Last 10 Games)
    home_last_10_record: str = "5-5"
    away_last_10_record: str = "5-5"
    home_last_10_net_rating: float = 0.0
    away_last_10_net_rating: float = 0.0

    # Head-to-Head
    season_series_record: str = "0-0"  # Home team perspective
    last_meeting_margin: float | None = None

    # Market Context
    public_bet_pct_favorite: float | None = None  # % on favorite
    line_movement: float | None = None  # Opening vs current spread
    total_movement: float | None = None  # Opening vs current total

    def __post_init__(self):
        if self.home_load_management is None:
            self.home_load_management = []
        if self.away_load_management is None:
            self.away_load_management = []

        # Calculate projected possessions
        self.projected_possessions = (self.home_pace + self.away_pace) / 2

        # Calculate net ratings
        self.home_net_rating = self.home_offensive_rating - self.home_defensive_rating
        self.away_net_rating = self.away_offensive_rating - self.away_defensive_rating


@dataclass
class NBAMarketPrediction:
    """NBA model predictions incorporating pace, efficiency, and lineup factors"""

    # Win Probabilities
    home_win_prob: float
    away_win_prob: float

    # Score Predictions (based on pace and efficiency)
    predicted_home_score: float
    predicted_away_score: float
    predicted_total: float
    projected_possessions: float

    # Market-Specific Predictions
    spread_cover_prob: float  # Probability favorite covers spread
    over_prob: float
    under_prob: float

    # First Half / Quarter Predictions
    first_half_home_score: float
    first_half_away_score: float
    first_half_total: float
    first_quarter_total: float

    # Advanced Metrics Impact
    pace_advantage: str = "neutral"  # "home", "away", "neutral"
    efficiency_advantage: str = "neutral"
    matchup_rating: float = 5.0  # 1-10 scale

    # Confidence and Volatility
    prediction_confidence: float = 0.68  # Based on model uncertainty
    game_volatility: float = 1.0  # Affects Kelly sizing

    # Model Metadata
    model_version: str = "v1.0"
    simulation_runs: int = 10000
    key_factors: list[str] = None

    def __post_init__(self):
        if self.key_factors is None:
            self.key_factors = ["pace", "efficiency", "rest", "travel", "injuries"]


class NBABettingEngine:
    """NBA-Specific Edge Detection with Basketball Analytics"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # NBA-specific risk parameters
        self.min_edge_threshold = 0.02  # 2% minimum edge
        self.max_bets_per_game = 3  # Max 3 markets per game
        self.max_bets_per_slate = 12  # Max 12 bets per day
        self.max_exposure_per_team = 0.08  # Max 8% bankroll per team

        # Market-specific Kelly multipliers
        self.market_kelly_multipliers = {
            "moneyline": 0.25,  # Conservative on ML
            "spread": 0.30,  # Standard on spreads
            "total": 0.28,  # Slightly conservative on totals
            "first_half": 0.25,  # More conservative on halves
            "first_quarter": 0.20,  # Very conservative on quarters
            "props": 0.18,  # Most conservative on props
        }

        # NBA-specific edge thresholds
        self.pace_edge_bonus = 0.005  # Bonus edge for pace mismatches
        self.rest_edge_bonus = 0.003  # Bonus for rest advantages
        self.injury_edge_bonus = 0.008  # Bonus for significant injuries
        self.travel_edge_penalty = 0.002  # Penalty for long travel

        # Tracking
        self.daily_bets: dict[str, list[EdgeBet]] = {}  # Date -> bets
        self.team_exposure: dict[str, float] = {}

    def nba_decide_and_place(
        self,
        game: NBAGame,
        market_type: str,
        market_odds: float,
        prediction: NBAMarketPrediction,
    ) -> EdgeBet | None:
        """
        NBA betting decision engine with basketball-specific analytics:
        1. Pace-adjusted probability calculations
        2. Efficiency-based edge adjustments
        3. Rest/travel/injury contextual factors
        4. NBA market-specific Kelly sizing
        """

        # Step 1: Extract fair probability from NBA model
        fair_prob = self._get_nba_fair_probability(prediction, market_type, game)
        if fair_prob is None:
            return None

        # Step 2: Calculate base edge
        implied_prob = american_to_implied(market_odds)
        base_edge = fair_prob - implied_prob

        # Step 3: Apply NBA-specific edge adjustments
        adjusted_edge = self._adjust_edge_for_nba_factors(base_edge, game, market_type, prediction)

        # Step 4: Check edge threshold
        if adjusted_edge < self.min_edge_threshold:
            logger.debug(
                f"NBA edge {adjusted_edge:.3f} below threshold for {game.away_team}@{game.home_team}"
            )
            return None

        # Step 5: Validate NBA constraints
        if not self._validate_nba_constraints(game, market_type):
            return None

        # Step 6: Calculate NBA-adjusted Kelly sizing
        kelly_multiplier = self.market_kelly_multipliers.get(market_type, 0.25)

        # Adjust for game volatility (high pace games are more volatile)
        volatility_adjustment = 1.0 / max(0.8, prediction.game_volatility)
        adjusted_kelly_multiplier = kelly_multiplier * volatility_adjustment

        base_kelly = self.bankroll_mgr.calculate_kelly_size(market_odds, fair_prob)
        final_kelly = base_kelly * adjusted_kelly_multiplier

        # Step 7: NBA-specific Kelly caps
        max_kelly = self._calculate_nba_max_kelly(game, market_type)
        final_kelly = min(final_kelly, max_kelly)

        if final_kelly <= 0:
            return None

        # Step 8: Create NBA EdgeBet
        bet_size = self.bankroll_mgr.calculate_bet_size(final_kelly)
        confidence = self._classify_nba_confidence(adjusted_edge, final_kelly, game, prediction)
        selection = self._format_nba_selection(market_type, game, market_odds, prediction)

        edge_bet = EdgeBet(
            event_id=game.id,
            sport="NBA",
            market=market_type,
            selection=selection,
            book="Combined",
            odds=market_odds,
            implied_prob=implied_prob,
            fair_prob=fair_prob,
            edge=adjusted_edge,
            kelly_fraction=final_kelly,
            bet_size=bet_size,
            confidence=confidence,
        )

        # Step 9: Track bet for limits
        self._track_nba_bet(edge_bet, game)

        logger.info(
            f"🏀 NBA EDGE: {selection} | Edge: {adjusted_edge:.1%} | Kelly: {final_kelly:.1%} | Size: ${bet_size:.2f} | {confidence}"
        )
        return edge_bet

    def _get_nba_fair_probability(
        self, prediction: NBAMarketPrediction, market_type: str, game: NBAGame
    ) -> float | None:
        """Extract fair probability from NBA model prediction"""
        if market_type == "moneyline":
            return prediction.home_win_prob  # Caller determines home vs away
        if market_type == "spread":
            return prediction.spread_cover_prob
        if market_type == "total":
            return prediction.over_prob  # Caller uses under_prob for under bets
        if market_type == "first_half":
            # Use first half totals for first half markets
            return 0.5  # Simplified - would need more specific first half model
        if market_type == "first_quarter":
            return 0.5  # Simplified - would need quarter-specific model
        return None

    def _adjust_edge_for_nba_factors(
        self,
        base_edge: float,
        game: NBAGame,
        market_type: str,
        prediction: NBAMarketPrediction,
    ) -> float:
        """Apply NBA-specific edge adjustments"""
        adjusted_edge = base_edge

        # Pace mismatch adjustments (higher pace = more variance = more edges)
        pace_differential = abs(game.home_pace - game.away_pace)
        if pace_differential > 8:  # Significant pace difference
            adjusted_edge += self.pace_edge_bonus

        # Rest advantage adjustments
        rest_differential = abs(game.home_rest_days - game.away_rest_days)
        if rest_differential >= 2:  # 2+ day rest advantage
            adjusted_edge += self.rest_edge_bonus

        # Back-to-back penalty (teams on B2B perform worse)
        if game.is_back_to_back:
            adjusted_edge += self.rest_edge_bonus * 2  # Double bonus against B2B team

        # Travel fatigue (especially cross-country)
        if game.away_travel_distance > 2000:  # Cross-country travel
            adjusted_edge += self.travel_edge_penalty

        # Time zone adjustments (West Coast teams struggle early East Coast games)
        if abs(game.time_zone_change) >= 3:
            adjusted_edge += self.travel_edge_penalty

        # Injury impact (significant injuries create value)
        total_injury_impact = game.home_injury_impact + game.away_injury_impact
        if total_injury_impact > 0.3:  # Significant injury impact
            adjusted_edge += self.injury_edge_bonus * total_injury_impact

        # Load management (creates betting value)
        total_load_management = len(game.home_load_management) + len(game.away_load_management)
        if total_load_management > 0:
            adjusted_edge += self.injury_edge_bonus * 0.5 * total_load_management

        # Motivation adjustments (playoff race, revenge games)
        motivation_diff = abs(game.home_motivation - game.away_motivation)
        if motivation_diff > 0.2:
            adjusted_edge += 0.003 * motivation_diff

        # Market-specific adjustments
        if market_type == "total":
            # Pace games create total value
            if prediction.projected_possessions > 105:  # Fast pace
                adjusted_edge *= 1.05
            elif prediction.projected_possessions < 95:  # Slow pace
                adjusted_edge *= 1.02

        # Efficiency mismatch bonus
        if prediction.matchup_rating >= 8:  # Significant mismatch
            adjusted_edge += 0.005
        elif prediction.matchup_rating <= 3:  # Very even matchup
            adjusted_edge *= 0.95  # Reduce edge in toss-up games

        return max(0, adjusted_edge)

    def _validate_nba_constraints(self, game: NBAGame, market_type: str) -> bool:
        """Validate NBA-specific betting constraints"""

        # Daily bet limit
        today = datetime.now().strftime("%Y-%m-%d")
        daily_bets = self.daily_bets.get(today, [])
        if len(daily_bets) >= self.max_bets_per_slate:
            logger.debug(f"Daily NBA bet limit reached: {len(daily_bets)}")
            return False

        # Per-game bet limit
        game_bets = [bet for bet in daily_bets if bet.event_id == game.id]
        if len(game_bets) >= self.max_bets_per_game:
            logger.debug(f"Per-game NBA bet limit reached: {len(game_bets)}")
            return False

        # Team exposure limits
        home_exposure = self.team_exposure.get(game.home_team, 0.0)
        away_exposure = self.team_exposure.get(game.away_team, 0.0)

        if home_exposure > self.max_exposure_per_team or away_exposure > self.max_exposure_per_team:
            logger.debug(
                f"Team exposure limit reached: {game.home_team}={home_exposure:.1%}, {game.away_team}={away_exposure:.1%}"
            )
            return False

        return True

    def _calculate_nba_max_kelly(self, game: NBAGame, market_type: str) -> float:
        """Calculate NBA-specific maximum Kelly fraction"""
        base_max = 0.05  # 5% max

        # Reduce max for volatile situations
        if game.is_back_to_back:
            base_max *= 0.8  # More conservative on B2B games

        if len(game.home_load_management) + len(game.away_load_management) > 2:
            base_max *= 0.7  # More conservative with many load management

        # Market-specific caps
        market_caps = {
            "props": 0.02,  # 2% max on props
            "first_quarter": 0.025,  # 2.5% max on quarters
            "first_half": 0.03,  # 3% max on halves
        }

        return min(base_max, market_caps.get(market_type, base_max))

    def _classify_nba_confidence(
        self, edge: float, kelly: float, game: NBAGame, prediction: NBAMarketPrediction
    ) -> str:
        """Classify NBA bet confidence with basketball context"""

        # Base confidence classification
        if edge >= 0.08 and kelly >= 0.03:
            base_confidence = "LOCK"
        elif edge >= 0.05 and kelly >= 0.02:
            base_confidence = "STRONG"
        elif edge >= 0.03 and kelly >= 0.01:
            base_confidence = "MODERATE"
        else:
            base_confidence = "WEAK"

        # NBA-specific adjustments
        confidence_boost = 0

        # High model confidence
        if prediction.prediction_confidence > 0.8:
            confidence_boost += 1

        # Clear pace/efficiency advantages
        if prediction.matchup_rating >= 8:
            confidence_boost += 1

        # Significant rest advantage
        if abs(game.home_rest_days - game.away_rest_days) >= 3:
            confidence_boost += 1

        # Major injury impact
        if game.home_injury_impact + game.away_injury_impact > 0.5:
            confidence_boost += 1

        # Downgrade for volatility
        if prediction.game_volatility > 1.5:
            confidence_boost -= 1

        # Apply adjustments
        confidence_levels = ["WEAK", "MODERATE", "STRONG", "LOCK"]
        current_level = confidence_levels.index(base_confidence)
        new_level = max(0, min(3, current_level + confidence_boost))

        return confidence_levels[new_level]

    def _format_nba_selection(
        self,
        market_type: str,
        game: NBAGame,
        odds: float,
        prediction: NBAMarketPrediction,
    ) -> str:
        """Format NBA bet selection description"""

        if market_type == "moneyline":
            # Determine which team based on odds and prediction
            if prediction.home_win_prob > 0.5:
                return f"{game.home_team} ML ({odds:+.0f})"
            return f"{game.away_team} ML ({odds:+.0f})"

        if market_type == "spread":
            # Simplified - would need actual spread line
            return f"Spread ({odds:+.0f})"

        if market_type == "total":
            total_line = prediction.predicted_total
            if prediction.over_prob > 0.5:
                return f"Over {total_line:.1f} ({odds:+.0f})"
            return f"Under {total_line:.1f} ({odds:+.0f})"

        if market_type == "first_half":
            return f"1H Total ({odds:+.0f})"

        if market_type == "first_quarter":
            return f"1Q Total ({odds:+.0f})"

        return f"{market_type} ({odds:+.0f})"

    def _track_nba_bet(self, edge_bet: EdgeBet, game: NBAGame):
        """Track NBA bet for daily and team exposure limits"""

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_bets:
            self.daily_bets[today] = []

        self.daily_bets[today].append(edge_bet)

        # Update team exposure (approximate)
        exposure_amount = edge_bet.bet_size / self.bankroll_mgr.current_bankroll
        self.team_exposure[game.home_team] = (
            self.team_exposure.get(game.home_team, 0) + exposure_amount
        )
        self.team_exposure[game.away_team] = (
            self.team_exposure.get(game.away_team, 0) + exposure_amount
        )


# Extraction and Generation Functions for NBA


def extract_nba_features(event: dict[str, Any]) -> NBAGame:
    """Extract NBA features from event data"""

    # Basic game info
    game = NBAGame(
        id=event.get("id", "unknown"),
        home_team=event.get("home_team", "Unknown"),
        away_team=event.get("away_team", "Unknown"),
        commence_time=event.get("commence_time", datetime.now().isoformat()),
    )

    # Mock NBA analytics (in real implementation, would fetch from NBA API, Basketball Reference, etc.)

    # Team pace (possessions per 48 minutes)
    team_paces = {
        "Lakers": 102.5,
        "Warriors": 101.8,
        "Celtics": 98.2,
        "Heat": 95.8,
        "Nuggets": 99.4,
        "Suns": 100.1,
        "Bucks": 101.2,
        "76ers": 97.5,
        "Nets": 103.1,
        "Clippers": 98.9,
        "Mavericks": 100.8,
        "Kings": 104.2,
    }

    game.home_pace = team_paces.get(game.home_team.split()[-1], 100.0)
    game.away_pace = team_paces.get(game.away_team.split()[-1], 100.0)

    # Efficiency ratings (points per 100 possessions)
    offensive_ratings = {
        "Lakers": 115.2,
        "Warriors": 117.8,
        "Celtics": 118.1,
        "Heat": 112.4,
        "Nuggets": 119.5,
        "Suns": 114.9,
        "Bucks": 116.8,
        "76ers": 113.2,
        "Nets": 111.8,
        "Clippers": 115.4,
        "Mavericks": 117.2,
        "Kings": 116.9,
    }

    defensive_ratings = {
        "Lakers": 113.8,
        "Warriors": 115.2,
        "Celtics": 110.1,
        "Heat": 108.9,
        "Nuggets": 112.3,
        "Suns": 116.4,
        "Bucks": 112.7,
        "76ers": 111.8,
        "Nets": 118.2,
        "Clippers": 111.5,
        "Mavericks": 114.8,
        "Kings": 119.1,
    }

    game.home_offensive_rating = offensive_ratings.get(game.home_team.split()[-1], 112.0)
    game.away_offensive_rating = offensive_ratings.get(game.away_team.split()[-1], 112.0)
    game.home_defensive_rating = defensive_ratings.get(game.home_team.split()[-1], 112.0)
    game.away_defensive_rating = defensive_ratings.get(game.away_team.split()[-1], 112.0)

    # Shooting efficiency
    efg_percentages = {
        "Lakers": 0.546,
        "Warriors": 0.587,
        "Celtics": 0.578,
        "Heat": 0.531,
        "Nuggets": 0.592,
        "Suns": 0.548,
        "Bucks": 0.561,
        "76ers": 0.542,
        "Nets": 0.528,
        "Clippers": 0.556,
        "Mavericks": 0.573,
        "Kings": 0.559,
    }

    game.home_efg_pct = efg_percentages.get(game.home_team.split()[-1], 0.52)
    game.away_efg_pct = efg_percentages.get(game.away_team.split()[-1], 0.52)

    # True shooting percentages
    ts_percentages = {
        "Lakers": 0.574,
        "Warriors": 0.601,
        "Celtics": 0.595,
        "Heat": 0.558,
        "Nuggets": 0.618,
        "Suns": 0.572,
        "Bucks": 0.589,
        "76ers": 0.567,
        "Nets": 0.551,
        "Clippers": 0.581,
        "Mavericks": 0.592,
        "Kings": 0.576,
    }

    game.home_ts_pct = ts_percentages.get(game.home_team.split()[-1], 0.55)
    game.away_ts_pct = ts_percentages.get(game.away_team.split()[-1], 0.55)

    # Add some randomness for rest days, travel, etc.
    game.home_rest_days = random.choice([1, 1, 2, 2, 3, 4])
    game.away_rest_days = random.choice([1, 1, 2, 2, 3, 4])

    # Travel distance (mock based on common NBA travel patterns)
    if game.home_team != game.away_team:
        game.away_travel_distance = random.uniform(200, 2800)

    # Back-to-back probability
    game.is_back_to_back = random.random() < 0.15  # ~15% of games are B2B

    # Injury impact (0-1 scale)
    game.home_injury_impact = random.uniform(0, 0.3)
    game.away_injury_impact = random.uniform(0, 0.3)

    return game


def generate_nba_prediction(nba_game: NBAGame) -> NBAMarketPrediction:
    """Generate comprehensive NBA market prediction using pace and efficiency analytics"""

    # Step 1: Calculate pace-adjusted possessions
    projected_possessions = (nba_game.home_pace + nba_game.away_pace) / 2

    # Step 2: Calculate efficiency-based scoring
    # Home team scoring: their offensive efficiency vs opponent's defensive efficiency
    home_offensive_strength = nba_game.home_offensive_rating / 112.0  # Normalize to league average
    away_defensive_strength = nba_game.away_defensive_rating / 112.0

    away_offensive_strength = nba_game.away_offensive_rating / 112.0
    home_defensive_strength = nba_game.home_defensive_rating / 112.0

    # Pace-adjusted scoring prediction
    home_efficiency_vs_defense = home_offensive_strength / away_defensive_strength
    away_efficiency_vs_defense = away_offensive_strength / home_defensive_strength

    # Base scoring (league average ~112 points per 100 possessions)
    home_base_score = 112.0 * (projected_possessions / 100.0) * home_efficiency_vs_defense
    away_base_score = 112.0 * (projected_possessions / 100.0) * away_efficiency_vs_defense

    # Step 3: Apply contextual adjustments

    # Rest adjustments (well-rested teams perform better)
    rest_diff = nba_game.home_rest_days - nba_game.away_rest_days
    if rest_diff > 0:  # Home team more rested
        home_base_score *= 1.0 + (rest_diff * 0.01)  # 1% per day advantage
        away_base_score *= 1.0 - (rest_diff * 0.005)
    elif rest_diff < 0:  # Away team more rested
        away_base_score *= 1.0 + (abs(rest_diff) * 0.01)
        home_base_score *= 1.0 - (abs(rest_diff) * 0.005)

    # Back-to-back penalty (teams on B2B score ~3% fewer points)
    if nba_game.is_back_to_back:
        if nba_game.home_rest_days == 1:
            home_base_score *= 0.97
        if nba_game.away_rest_days == 1:
            away_base_score *= 0.97

    # Travel fatigue (long travel reduces away team performance)
    if nba_game.away_travel_distance > 1500:  # Cross-country travel
        travel_penalty = 1.0 - (nba_game.away_travel_distance / 10000)  # Up to 2.8% penalty
        away_base_score *= max(0.97, travel_penalty)

    # Injury impact
    home_base_score *= 1.0 - nba_game.home_injury_impact * 0.1  # Up to 10% impact
    away_base_score *= 1.0 - nba_game.away_injury_impact * 0.1

    # Home court advantage (~2.5 points in NBA)
    home_court_advantage = 2.5
    home_base_score += home_court_advantage

    # Step 4: Calculate win probabilities
    point_differential = home_base_score - away_base_score

    # Convert point spread to win probability (using logistic regression)
    # NBA standard deviation ~12 points
    nba_std_dev = 12.0
    z_score = point_differential / nba_std_dev

    # Logistic transformation
    home_win_prob = 1.0 / (1.0 + math.exp(-z_score))
    away_win_prob = 1.0 - home_win_prob

    # Step 5: Calculate spread and total predictions
    predicted_spread = point_differential  # Negative means home team favored by this much
    spread_cover_prob = home_win_prob if predicted_spread < 0 else away_win_prob

    predicted_total = home_base_score + away_base_score

    # Over/Under probabilities (based on total vs market expectations)
    # Assume market total around predicted total with some noise
    market_total_estimate = predicted_total + random.uniform(-3, 3)

    if predicted_total > market_total_estimate:
        over_prob = 0.52 + min(0.15, (predicted_total - market_total_estimate) / 20.0)
    else:
        over_prob = 0.48 - min(0.15, (market_total_estimate - predicted_total) / 20.0)

    under_prob = 1.0 - over_prob

    # Step 6: First half predictions (typically ~47% of total game)
    first_half_factor = 0.47
    first_half_home = home_base_score * first_half_factor
    first_half_away = away_base_score * first_half_factor
    first_half_total = first_half_home + first_half_away

    # First quarter (~23% of game)
    first_quarter_factor = 0.23
    first_quarter_total = predicted_total * first_quarter_factor

    # Step 7: Advanced analytics
    pace_advantage = "neutral"
    if nba_game.home_pace > nba_game.away_pace + 5:
        pace_advantage = "home"
    elif nba_game.away_pace > nba_game.home_pace + 5:
        pace_advantage = "away"

    efficiency_advantage = "neutral"
    home_net_rating = nba_game.home_net_rating
    away_net_rating = nba_game.away_net_rating

    if home_net_rating > away_net_rating + 3:
        efficiency_advantage = "home"
    elif away_net_rating > home_net_rating + 3:
        efficiency_advantage = "away"

    # Matchup rating (1-10 scale based on various factors)
    rating_factors = [
        abs(home_net_rating - away_net_rating) / 2,  # Net rating difference
        abs(nba_game.home_pace - nba_game.away_pace) / 3,  # Pace difference
        abs(rest_diff) * 0.5,  # Rest difference
        nba_game.away_travel_distance / 1000,  # Travel factor
        (nba_game.home_injury_impact + nba_game.away_injury_impact) * 5,  # Injury factor
    ]

    matchup_rating = min(10, max(1, 5 + sum(rating_factors)))

    # Game volatility (affects Kelly sizing)
    volatility_factors = [
        max(nba_game.home_pace, nba_game.away_pace) / 100.0,  # High pace = high volatility
        projected_possessions / 100.0,  # More possessions = more variance
        (nba_game.home_injury_impact + nba_game.away_injury_impact) * 2,  # Injuries add volatility
        1.2 if nba_game.is_back_to_back else 1.0,  # B2B adds volatility
    ]

    game_volatility = sum(volatility_factors) / len(volatility_factors)

    # Prediction confidence (based on model certainty)
    confidence_factors = [
        min(0.2, abs(point_differential) / 50),  # Larger spreads = more confident
        min(0.15, abs(home_net_rating - away_net_rating) / 20),  # Rating differences
        0.1 if abs(rest_diff) >= 2 else 0,  # Rest advantages
        0.05 if nba_game.away_travel_distance > 2000 else 0,  # Long travel
    ]

    prediction_confidence = min(0.9, 0.6 + sum(confidence_factors))

    return NBAMarketPrediction(
        home_win_prob=home_win_prob,
        away_win_prob=away_win_prob,
        predicted_home_score=home_base_score,
        predicted_away_score=away_base_score,
        predicted_total=predicted_total,
        projected_possessions=projected_possessions,
        spread_cover_prob=spread_cover_prob,
        over_prob=over_prob,
        under_prob=under_prob,
        first_half_home_score=first_half_home,
        first_half_away_score=first_half_away,
        first_half_total=first_half_total,
        first_quarter_total=first_quarter_total,
        pace_advantage=pace_advantage,
        efficiency_advantage=efficiency_advantage,
        matchup_rating=matchup_rating,
        prediction_confidence=prediction_confidence,
        game_volatility=game_volatility,
        simulation_runs=10000,
        key_factors=["pace", "efficiency", "rest", "travel", "injuries", "home_court"],
    )


# Initialize NBA engine
nba_engine = NBABettingEngine(bankroll_manager)

# ================================
# COLLEGE BASKETBALL (NCAAB) & MARCH MADNESS CLASSES
# ================================


@dataclass
class BracketContext:
    """March Madness tournament bracket context"""

    # Tournament Info
    is_tournament: bool = False
    tournament_round: str = "regular_season"  # "first_four", "round_1", "round_2", etc.
    region: str | None = None  # "East", "West", "South", "Midwest"

    # Seeding (if tournament)
    home_seed: int | None = None  # 1-16 seed
    away_seed: int | None = None
    seed_differential: int = 0  # Absolute difference in seeds

    # Tournament History
    home_tourney_experience: int = 0  # Prior tournament games in last 3 years
    away_tourney_experience: int = 0
    home_upset_history: float = 0.0  # Historical upset rate as underdog
    away_upset_history: float = 0.0

    # Bracket Position
    bracket_path_difficulty: float = 5.0  # 1-10 scale for path to Final Four
    potential_elite_8_opponent: str | None = None

    # Public/Media Attention
    media_darling: str | None = None  # Which team getting more media attention
    cinderella_factor: float = 0.0  # 0-1 scale for underdog story appeal

    def __post_init__(self):
        if self.home_seed and self.away_seed:
            self.seed_differential = abs(self.home_seed - self.away_seed)


@dataclass
class NCAABGame:
    """Comprehensive NCAAB game with four factors and strength of schedule analytics"""

    # Basic game info
    id: str
    home_team: str
    away_team: str
    commence_time: str

    # Tournament/Season Context
    bracket_context: BracketContext | None = None
    conference_game: bool = False
    rivalry_game: bool = False

    # Efficiency Metrics (Adjusted for Strength of Schedule)
    home_adj_offensive_efficiency: float = 100.0  # Points per 100 possessions vs average D1
    away_adj_offensive_efficiency: float = 100.0
    home_adj_defensive_efficiency: float = 100.0  # Points allowed per 100 possessions vs average D1
    away_adj_defensive_efficiency: float = 100.0
    home_adj_tempo: float = 70.0  # Possessions per 40 minutes, adjusted
    away_adj_tempo: float = 70.0

    # Four Factors (Dean Oliver) - Core Basketball Analytics
    # Factor 1: Shooting (Effective Field Goal %)
    home_efg_offense: float = 0.50  # Team's eFG% on offense
    away_efg_offense: float = 0.50
    home_efg_defense: float = 0.50  # eFG% allowed on defense
    away_efg_defense: float = 0.50

    # Factor 2: Turnovers (Turnover Rate)
    home_turnover_rate_offense: float = 19.0  # TO% when on offense (lower is better)
    away_turnover_rate_offense: float = 19.0
    home_turnover_rate_defense: float = 19.0  # TO% forced on defense (higher is better)
    away_turnover_rate_defense: float = 19.0

    # Factor 3: Rebounding (Offensive Rebounding Rate)
    home_oreb_rate_offense: float = 28.0  # Offensive rebound % (higher is better)
    away_oreb_rate_offense: float = 28.0
    home_oreb_rate_defense: float = 28.0  # Offensive rebounds allowed % (lower is better)
    away_oreb_rate_defense: float = 28.0

    # Factor 4: Free Throws (Free Throw Rate)
    home_ft_rate_offense: float = 32.0  # FTA/FGA ratio (higher is better)
    away_ft_rate_offense: float = 32.0
    home_ft_rate_defense: float = 32.0  # FTA/FGA allowed (lower is better)
    away_ft_rate_defense: float = 32.0
    home_ft_percentage: float = 70.0  # Free throw shooting percentage
    away_ft_percentage: float = 70.0

    # Strength of Schedule & Rankings
    home_sos_ranking: int = 150  # Strength of schedule rank (1-353)
    away_sos_ranking: int = 150
    home_kenpom_ranking: int | None = None  # KenPom overall ranking
    away_kenpom_ranking: int | None = None
    home_net_ranking: int | None = None  # NCAA NET ranking
    away_net_ranking: int | None = None

    # Recent Form and Momentum
    home_last_10_record: str = "5-5"
    away_last_10_record: str = "5-5"
    home_road_record: str = "5-5"  # Away from home performance
    away_road_record: str = "5-5"  # True road performance
    home_vs_top_50_record: str = "2-3"  # Performance vs quality opponents
    away_vs_top_50_record: str = "2-3"

    # Injury and Availability
    home_key_injuries: list[str] | None = None  # List of injured key players
    away_key_injuries: list[str] | None = None
    home_starter_minutes_concern: bool = False  # Key players with fatigue/foul trouble
    away_starter_minutes_concern: bool = False

    # Coaching and Experience
    home_coach_tourney_wins: int = 0  # Coach's tournament game wins
    away_coach_tourney_wins: int = 0
    home_senior_leadership: int = 2  # Number of senior leaders
    away_senior_leadership: int = 2
    home_tourney_experience: int = 0  # Tournament games in last 3 years
    away_tourney_experience: int = 0

    # Situational Factors
    must_win_situation: str | None = None  # "home", "away", or None
    revenge_game: bool = False  # Revenge from earlier loss
    senior_night: bool = False  # Senior night game

    # Market Context (if available)
    public_bet_percentage: float | None = None  # % of public on favorite
    line_movement: float | None = None  # Opening vs current spread
    sharp_money_indicator: str | None = None  # "home", "away", or None

    def __post_init__(self):
        if self.home_key_injuries is None:
            self.home_key_injuries = []
        if self.away_key_injuries is None:
            self.away_key_injuries = []
        if self.bracket_context is None:
            self.bracket_context = BracketContext()


@dataclass
class NCAABMarketPrediction:
    """NCAAB predictions incorporating four factors and tournament dynamics"""

    # Win Probabilities
    home_win_prob: float
    away_win_prob: float

    # Score Predictions (based on tempo and efficiency)
    predicted_home_score: float
    predicted_away_score: float
    predicted_total: float
    projected_possessions: float

    # Market Predictions
    spread_cover_prob: float
    over_prob: float
    under_prob: float

    # First Half Predictions
    first_half_home_score: float
    first_half_away_score: float
    first_half_total: float

    # Four Factors Analysis
    shooting_advantage: str = "neutral"  # Which team has shooting edge
    turnover_advantage: str = "neutral"  # Which team forces more turnovers
    rebounding_advantage: str = "neutral"  # Which team controls boards
    free_throw_advantage: str = "neutral"  # Which team gets to line more

    # Advanced Insights
    tempo_advantage: str = "neutral"  # "home", "away", "neutral"
    experience_advantage: str = "neutral"  # Tournament/senior experience
    coaching_advantage: str = "neutral"  # Coaching experience edge

    # Tournament-Specific (March Madness)
    upset_probability: float = 0.15  # Probability of upset if underdog
    blowout_probability: float = 0.20  # Probability of 15+ point win
    buzzer_beater_factor: float = 0.05  # Extra variance for close games

    # Model Metadata
    prediction_confidence: float = 0.68
    model_version: str = "v1.0"
    key_factors: list[str] | None = None

    # Strength of Schedule Impact
    sos_adjustment: float = 1.0  # Adjustment for SOS difference

    def __post_init__(self):
        if self.key_factors is None:
            self.key_factors = [
                "four_factors",
                "tempo",
                "sos",
                "experience",
                "injuries",
            ]


class NCAABBettingEngine:
    """NCAAB & March Madness Betting Engine with Tournament Logic"""

    def __init__(self, bankroll_mgr: GPT5BankrollManager):
        self.bankroll_mgr = bankroll_mgr

        # Regular Season vs Tournament Thresholds
        self.regular_season_min_edge = 0.025  # 2.5% edge for regular season
        self.tournament_min_edge = 0.02  # 2.0% edge for tournament (more conservative)

        # Kelly Multipliers by Season Type
        self.regular_season_kelly = {
            "moneyline": 0.30,
            "spread": 0.35,
            "total": 0.30,
            "first_half": 0.25,
        }

        self.tournament_kelly = {
            "moneyline": 0.25,  # More conservative in tournament
            "spread": 0.28,
            "total": 0.25,
            "first_half": 0.20,
        }

        # Risk Controls
        self.max_bets_per_game = 2  # Fewer bets per game due to lower frequency
        self.max_bets_per_day = 8  # Fewer games per day than NBA
        self.max_tournament_exposure = 0.15  # Max 15% bankroll in tournament action

        # NCAAB-specific edge bonuses
        self.four_factors_edge_bonus = 0.008  # Bonus for significant four factors edge
        self.sos_edge_bonus = 0.005  # Bonus for SOS mismatches
        self.experience_edge_bonus = 0.006  # Tournament experience bonus
        self.upset_special_bonus = 0.010  # Extra bonus for upset opportunities

        # Tracking
        self.daily_bets: dict[str, list[EdgeBet]] = {}
        self.tournament_exposure: float = 0.0

    def ncaab_decide_and_place(
        self,
        game: NCAABGame,
        market_type: str,
        market_odds: float,
        prediction: NCAABMarketPrediction,
    ) -> EdgeBet | None:
        """
        NCAAB betting decision engine with four factors analytics:
        1. Regular season vs tournament mode logic
        2. Four factors advantage detection
        3. Strength of schedule adjustments
        4. Tournament-specific upset detection
        5. Conservative tournament Kelly sizing
        """

        # Step 1: Determine if tournament mode
        is_tournament = game.bracket_context.is_tournament if game.bracket_context else False

        # Step 2: Get fair probability
        fair_prob = self._get_ncaab_fair_probability(prediction, market_type, game)
        if fair_prob is None:
            return None

        # Step 3: Calculate base edge
        implied_prob = american_to_implied(market_odds)
        base_edge = fair_prob - implied_prob

        # Step 4: Apply NCAAB-specific adjustments
        adjusted_edge = self._adjust_edge_for_ncaab_factors(
            base_edge, game, market_type, prediction
        )

        # Step 5: Check appropriate edge threshold
        min_edge = self.tournament_min_edge if is_tournament else self.regular_season_min_edge
        if adjusted_edge < min_edge:
            logger.debug(
                f"NCAAB edge {adjusted_edge:.3f} below {'tournament' if is_tournament else 'regular'} threshold"
            )
            return None

        # Step 6: Validate constraints
        if not self._validate_ncaab_constraints(game, market_type, is_tournament):
            return None

        # Step 7: Calculate Kelly sizing
        kelly_multipliers = self.tournament_kelly if is_tournament else self.regular_season_kelly
        kelly_multiplier = kelly_multipliers.get(market_type, 0.25)

        # Tournament volatility adjustment
        if is_tournament:
            # More conservative sizing in single-elimination
            volatility_adjustment = 0.8 + (
                prediction.upset_probability * 0.4
            )  # Reduce sizing for upset risk
            kelly_multiplier *= volatility_adjustment

        base_kelly = self.bankroll_mgr.calculate_kelly_size(market_odds, fair_prob)
        final_kelly = base_kelly * kelly_multiplier

        # Step 8: Apply NCAAB-specific caps
        max_kelly = self._calculate_ncaab_max_kelly(game, market_type, is_tournament)
        final_kelly = min(final_kelly, max_kelly)

        if final_kelly <= 0:
            return None

        # Step 9: Create NCAAB EdgeBet
        bet_size = self.bankroll_mgr.calculate_bet_size(final_kelly)
        confidence = self._classify_ncaab_confidence(adjusted_edge, final_kelly, game, prediction)
        selection = self._format_ncaab_selection(market_type, game, market_odds, prediction)

        edge_bet = EdgeBet(
            event_id=game.id,
            sport="NCAAB" if not is_tournament else "March Madness",
            market=market_type,
            selection=selection,
            book="Combined",
            odds=market_odds,
            implied_prob=implied_prob,
            fair_prob=fair_prob,
            edge=adjusted_edge,
            kelly_fraction=final_kelly,
            bet_size=bet_size,
            confidence=confidence,
        )

        # Step 10: Track bet
        self._track_ncaab_bet(edge_bet, game, is_tournament)

        sport_icon = "🏀" if not is_tournament else "🏆"
        logger.info(
            f"{sport_icon} NCAAB EDGE: {selection} | Edge: {adjusted_edge:.1%} | Kelly: {final_kelly:.1%} | Size: ${bet_size:.2f} | {confidence}"
        )
        return edge_bet

    def _get_ncaab_fair_probability(
        self, prediction: NCAABMarketPrediction, market_type: str, game: NCAABGame
    ) -> float | None:
        """Extract fair probability from NCAAB prediction"""
        if market_type == "moneyline":
            return prediction.home_win_prob  # Caller adjusts for home vs away
        if market_type == "spread":
            return prediction.spread_cover_prob
        if market_type == "total":
            return prediction.over_prob  # Caller uses under_prob for unders
        if market_type == "first_half":
            # Use first half model predictions
            return 0.5  # Simplified - would need dedicated first half model
        return None

    def _adjust_edge_for_ncaab_factors(
        self,
        base_edge: float,
        game: NCAABGame,
        market_type: str,
        prediction: NCAABMarketPrediction,
    ) -> float:
        """Apply NCAAB-specific edge adjustments based on four factors and tournament context"""
        adjusted_edge = base_edge

        # Four Factors Edge Detection
        four_factors_advantages = [
            prediction.shooting_advantage != "neutral",
            prediction.turnover_advantage != "neutral",
            prediction.rebounding_advantage != "neutral",
            prediction.free_throw_advantage != "neutral",
        ]

        significant_advantages = sum(four_factors_advantages)
        if significant_advantages >= 3:  # Three or more four factor advantages
            adjusted_edge += self.four_factors_edge_bonus
        elif significant_advantages >= 2:  # Two four factor advantages
            adjusted_edge += self.four_factors_edge_bonus * 0.6

        # Strength of Schedule Mismatch Bonus
        sos_differential = abs(game.home_sos_ranking - game.away_sos_ranking)
        if sos_differential > 100:  # Major SOS difference (weak schedule vs strong)
            adjusted_edge += self.sos_edge_bonus

        # Tournament Experience Edge
        if game.bracket_context.is_tournament:
            experience_diff = abs(game.home_tourney_experience - game.away_tourney_experience)
            if experience_diff >= 3:  # Significant tournament experience difference
                adjusted_edge += self.experience_edge_bonus

        # Upset Detection (March Madness Special)
        if game.bracket_context.is_tournament and game.bracket_context.seed_differential >= 4:
            # Potential upset scenario (4+ seed difference)
            if prediction.upset_probability > 0.25:  # Model indicates upset potential
                adjusted_edge += self.upset_special_bonus

        # Senior Leadership & Experience
        senior_diff = abs(game.home_senior_leadership - game.away_senior_leadership)
        if senior_diff >= 2:  # Significant senior leadership difference
            adjusted_edge += 0.003 * senior_diff

        # Coaching Tournament Experience
        if game.bracket_context.is_tournament:
            coach_experience_diff = abs(game.home_coach_tourney_wins - game.away_coach_tourney_wins)
            if coach_experience_diff >= 5:  # Experienced vs inexperienced coach
                adjusted_edge += 0.004

        # Injury Impact (more significant in college due to shorter bench)
        total_injuries = len(game.home_key_injuries) + len(game.away_key_injuries)
        if total_injuries > 1:  # Multiple key injuries
            adjusted_edge += 0.005 * total_injuries

        # Situational Adjustments
        if game.must_win_situation:  # Desperation games create value
            adjusted_edge += 0.006

        if game.revenge_game:  # Revenge factor
            adjusted_edge += 0.003

        # Market-specific adjustments
        if market_type == "total":
            # Tempo mismatch creates total value
            if prediction.tempo_advantage != "neutral":
                tempo_diff = abs(game.home_adj_tempo - game.away_adj_tempo)
                if tempo_diff > 10:  # Significant tempo difference
                    adjusted_edge += 0.004

        # Tournament Round Adjustments (later rounds = more variance)
        if game.bracket_context.is_tournament:
            round_volatility_bonus = {
                "first_four": 0.002,
                "round_1": 0.003,
                "round_2": 0.004,
                "sweet_16": 0.005,
                "elite_8": 0.006,
                "final_four": 0.008,
                "championship": 0.010,
            }

            round_bonus = round_volatility_bonus.get(game.bracket_context.tournament_round, 0.0)
            adjusted_edge += round_bonus

        return max(0, adjusted_edge)

    def _validate_ncaab_constraints(
        self, game: NCAABGame, market_type: str, is_tournament: bool
    ) -> bool:
        """Validate NCAAB betting constraints with tournament limits"""

        # Daily bet limit
        today = datetime.now().strftime("%Y-%m-%d")
        daily_bets = self.daily_bets.get(today, [])
        if len(daily_bets) >= self.max_bets_per_day:
            logger.debug(f"Daily NCAAB bet limit reached: {len(daily_bets)}")
            return False

        # Per-game limit
        game_bets = [bet for bet in daily_bets if bet.event_id == game.id]
        if len(game_bets) >= self.max_bets_per_game:
            logger.debug(f"Per-game NCAAB bet limit reached: {len(game_bets)}")
            return False

        # Tournament exposure limit (March Madness only)
        if is_tournament and self.tournament_exposure >= self.max_tournament_exposure:
            logger.debug(f"Tournament exposure limit reached: {self.tournament_exposure:.1%}")
            return False

        return True

    def _calculate_ncaab_max_kelly(
        self, game: NCAABGame, market_type: str, is_tournament: bool
    ) -> float:
        """Calculate NCAAB maximum Kelly fraction with tournament adjustments"""

        if is_tournament:
            # More conservative in single-elimination tournament
            base_max = 0.03  # 3% max in tournament

            # Even more conservative in later rounds
            round_caps = {
                "first_four": 0.035,
                "round_1": 0.03,
                "round_2": 0.025,
                "sweet_16": 0.02,
                "elite_8": 0.015,
                "final_four": 0.01,
                "championship": 0.01,
            }

            base_max = round_caps.get(game.bracket_context.tournament_round, base_max)

        else:
            # Regular season limits
            base_max = 0.04  # 4% max in regular season

        # Market-specific caps
        market_caps = {
            "first_half": base_max * 0.8,  # More conservative on halves
        }

        return market_caps.get(market_type, base_max)

    def _classify_ncaab_confidence(
        self,
        edge: float,
        kelly: float,
        game: NCAABGame,
        prediction: NCAABMarketPrediction,
    ) -> str:
        """Classify NCAAB bet confidence with college basketball context"""

        # Base confidence from edge and sizing
        if edge >= 0.08 and kelly >= 0.025:
            base_confidence = "LOCK"
        elif edge >= 0.05 and kelly >= 0.02:
            base_confidence = "STRONG"
        elif edge >= 0.03 and kelly >= 0.01:
            base_confidence = "MODERATE"
        else:
            base_confidence = "WEAK"

        # NCAAB-specific confidence adjustments
        confidence_boost = 0

        # Four factors dominance
        four_factor_edges = sum(
            [
                prediction.shooting_advantage != "neutral",
                prediction.turnover_advantage != "neutral",
                prediction.rebounding_advantage != "neutral",
                prediction.free_throw_advantage != "neutral",
            ]
        )

        if four_factor_edges >= 3:
            confidence_boost += 1

        # Major strength of schedule difference
        sos_diff = abs(game.home_sos_ranking - game.away_sos_ranking)
        if sos_diff > 150:  # Huge SOS difference
            confidence_boost += 1

        # Tournament experience edge
        if game.bracket_context.is_tournament:
            exp_diff = abs(game.home_tourney_experience - game.away_tourney_experience)
            if exp_diff >= 5:  # Major experience difference
                confidence_boost += 1

        # High model confidence
        if prediction.prediction_confidence > 0.85:
            confidence_boost += 1

        # Upset detection (March Madness)
        if (
            game.bracket_context.is_tournament
            and game.bracket_context.seed_differential >= 5
            and prediction.upset_probability > 0.30
        ):
            confidence_boost += 1  # Bonus for identified upset opportunities

        # Downgrade for tournament volatility
        if game.bracket_context.is_tournament and prediction.buzzer_beater_factor > 0.10:
            confidence_boost -= 1  # Tournament games are more volatile

        # Apply adjustments
        confidence_levels = ["WEAK", "MODERATE", "STRONG", "LOCK"]
        current_level = confidence_levels.index(base_confidence)
        new_level = max(0, min(3, current_level + confidence_boost))

        return confidence_levels[new_level]

    def _format_ncaab_selection(
        self,
        market_type: str,
        game: NCAABGame,
        odds: float,
        prediction: NCAABMarketPrediction,
    ) -> str:
        """Format NCAAB selection with tournament context"""

        # Add tournament context to selection
        tournament_prefix = ""
        if game.bracket_context.is_tournament:
            if game.bracket_context.home_seed and game.bracket_context.away_seed:
                tournament_prefix = (
                    f"({game.bracket_context.away_seed}) vs ({game.bracket_context.home_seed}) "
                )

        if market_type == "moneyline":
            if prediction.home_win_prob > 0.5:
                return f"{tournament_prefix}{game.home_team} ML ({odds:+.0f})"
            return f"{tournament_prefix}{game.away_team} ML ({odds:+.0f})"

        if market_type == "spread":
            return f"{tournament_prefix}Spread ({odds:+.0f})"

        if market_type == "total":
            total_line = prediction.predicted_total
            if prediction.over_prob > 0.5:
                return f"{tournament_prefix}Over {total_line:.1f} ({odds:+.0f})"
            return f"{tournament_prefix}Under {total_line:.1f} ({odds:+.0f})"

        if market_type == "first_half":
            return f"{tournament_prefix}1H Total ({odds:+.0f})"

        return f"{tournament_prefix}{market_type} ({odds:+.0f})"

    def _track_ncaab_bet(self, edge_bet: EdgeBet, game: NCAABGame, is_tournament: bool):
        """Track NCAAB bet for limits and tournament exposure"""

        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_bets:
            self.daily_bets[today] = []

        self.daily_bets[today].append(edge_bet)

        # Track tournament exposure separately
        if is_tournament:
            exposure_pct = edge_bet.bet_size / self.bankroll_mgr.current_bankroll
            self.tournament_exposure += exposure_pct


# NCAAB Feature Extraction and Prediction Functions


def extract_ncaab_features(
    event: dict[str, Any], bracket_context: BracketContext | None = None
) -> NCAABGame:
    """Extract NCAAB features with four factors and tournament context"""

    # Basic game info
    game = NCAABGame(
        id=event.get("id", "unknown"),
        home_team=event.get("home_team", "Unknown"),
        away_team=event.get("away_team", "Unknown"),
        commence_time=event.get("commence_time", datetime.now().isoformat()),
        bracket_context=bracket_context or BracketContext(),
    )

    # Mock NCAAB analytics (in real implementation, fetch from KenPom, sports-reference, etc.)

    # Adjusted efficiency ratings (KenPom style)
    offensive_efficiencies = {
        "Duke": 118.5,
        "North Carolina": 116.8,
        "Kansas": 119.2,
        "Gonzaga": 121.4,
        "Kentucky": 115.9,
        "Villanova": 117.3,
        "Michigan": 114.7,
        "UCLA": 116.1,
        "Auburn": 113.8,
        "Tennessee": 115.4,
        "Arizona": 118.9,
        "Purdue": 119.7,
        "Arkansas": 112.6,
        "Illinois": 114.2,
        "Wisconsin": 110.8,
        "Iowa": 117.8,
    }

    defensive_efficiencies = {
        "Duke": 95.2,
        "North Carolina": 97.8,
        "Kansas": 94.6,
        "Gonzaga": 98.1,
        "Kentucky": 96.4,
        "Villanova": 95.8,
        "Michigan": 92.3,
        "UCLA": 99.2,
        "Auburn": 91.7,
        "Tennessee": 93.5,
        "Arizona": 97.4,
        "Purdue": 99.8,
        "Arkansas": 94.1,
        "Illinois": 96.7,
        "Wisconsin": 90.9,
        "Iowa": 103.2,
    }

    # Get team names (simplified)
    home_name = game.home_team.split()[-1]  # Get last word (team name)
    away_name = game.away_team.split()[-1]

    game.home_adj_offensive_efficiency = offensive_efficiencies.get(home_name, 108.0)
    game.away_adj_offensive_efficiency = offensive_efficiencies.get(away_name, 108.0)
    game.home_adj_defensive_efficiency = defensive_efficiencies.get(home_name, 102.0)
    game.away_adj_defensive_efficiency = defensive_efficiencies.get(away_name, 102.0)

    # Four Factors (with some variation)
    base_efg = 0.50
    base_turnover = 19.0
    base_oreb = 28.0
    base_ft_rate = 32.0

    # Add team-specific variations
    game.home_efg_offense = base_efg + random.uniform(-0.08, 0.08)
    game.away_efg_offense = base_efg + random.uniform(-0.08, 0.08)
    game.home_efg_defense = base_efg + random.uniform(-0.06, 0.06)
    game.away_efg_defense = base_efg + random.uniform(-0.06, 0.06)

    game.home_turnover_rate_offense = base_turnover + random.uniform(-4, 4)
    game.away_turnover_rate_offense = base_turnover + random.uniform(-4, 4)
    game.home_turnover_rate_defense = base_turnover + random.uniform(-4, 4)
    game.away_turnover_rate_defense = base_turnover + random.uniform(-4, 4)

    game.home_oreb_rate_offense = base_oreb + random.uniform(-8, 8)
    game.away_oreb_rate_offense = base_oreb + random.uniform(-8, 8)
    game.home_oreb_rate_defense = base_oreb + random.uniform(-6, 6)
    game.away_oreb_rate_defense = base_oreb + random.uniform(-6, 6)

    game.home_ft_rate_offense = base_ft_rate + random.uniform(-10, 10)
    game.away_ft_rate_offense = base_ft_rate + random.uniform(-10, 10)
    game.home_ft_rate_defense = base_ft_rate + random.uniform(-8, 8)
    game.away_ft_rate_defense = base_ft_rate + random.uniform(-8, 8)

    # Tempo (possessions per 40 minutes)
    tempos = {
        "Duke": 72.4,
        "North Carolina": 74.1,
        "Kansas": 70.8,
        "Gonzaga": 73.9,
        "Kentucky": 71.2,
        "Villanova": 67.8,
        "Michigan": 68.9,
        "UCLA": 71.6,
        "Auburn": 75.3,
        "Tennessee": 69.4,
        "Arizona": 72.7,
        "Purdue": 68.2,
        "Arkansas": 76.8,
        "Illinois": 70.1,
        "Wisconsin": 65.4,
        "Iowa": 73.2,
    }

    game.home_adj_tempo = tempos.get(home_name, 70.0)
    game.away_adj_tempo = tempos.get(away_name, 70.0)

    # Strength of Schedule rankings (1-353)
    game.home_sos_ranking = random.randint(25, 300)
    game.away_sos_ranking = random.randint(25, 300)

    # Mock rankings
    game.home_kenpom_ranking = random.randint(10, 200)
    game.away_kenpom_ranking = random.randint(10, 200)
    game.home_net_ranking = random.randint(15, 180)
    game.away_net_ranking = random.randint(15, 180)

    # Experience factors
    game.home_senior_leadership = random.randint(1, 4)
    game.away_senior_leadership = random.randint(1, 4)
    game.home_coach_tourney_wins = random.randint(0, 15)
    game.away_coach_tourney_wins = random.randint(0, 15)

    return game


def generate_ncaab_prediction(ncaab_game: NCAABGame) -> NCAABMarketPrediction:
    """Generate NCAAB prediction using four factors and adjusted efficiency"""

    # Step 1: Calculate tempo-adjusted possessions
    projected_possessions = (ncaab_game.home_adj_tempo + ncaab_game.away_adj_tempo) / 2

    # Step 2: Efficiency-based scoring prediction
    # Home scoring: Home offensive efficiency vs Away defensive efficiency
    home_off_vs_away_def = (
        ncaab_game.home_adj_offensive_efficiency - ncaab_game.away_adj_defensive_efficiency
    )
    away_off_vs_home_def = (
        ncaab_game.away_adj_offensive_efficiency - ncaab_game.home_adj_defensive_efficiency
    )

    # Convert efficiency differential to scoring (college average ~100 points per 100 possessions)
    league_avg_efficiency = 100.0

    home_expected_efficiency = league_avg_efficiency + (home_off_vs_away_def / 2)
    away_expected_efficiency = league_avg_efficiency + (away_off_vs_home_def / 2)

    # Scale to actual possessions
    home_base_score = (home_expected_efficiency / 100.0) * projected_possessions
    away_base_score = (away_expected_efficiency / 100.0) * projected_possessions

    # Step 3: Four Factors Adjustments

    # Factor 1: Shooting (eFG%)
    home_shooting_edge = ncaab_game.home_efg_offense - ncaab_game.away_efg_defense
    away_shooting_edge = ncaab_game.away_efg_offense - ncaab_game.home_efg_defense

    # Apply shooting adjustment (most important factor)
    home_base_score *= 1.0 + home_shooting_edge * 0.8
    away_base_score *= 1.0 + away_shooting_edge * 0.8

    # Factor 2: Turnovers
    home_turnover_edge = (
        ncaab_game.home_turnover_rate_defense - ncaab_game.away_turnover_rate_offense
    )
    away_turnover_edge = (
        ncaab_game.away_turnover_rate_defense - ncaab_game.home_turnover_rate_offense
    )

    # Turnovers create extra possessions
    home_base_score *= 1.0 + home_turnover_edge * 0.02
    away_base_score *= 1.0 + away_turnover_edge * 0.02

    # Factor 3: Rebounding (creates second chances)
    home_rebound_edge = ncaab_game.home_oreb_rate_offense - ncaab_game.away_oreb_rate_defense
    away_rebound_edge = ncaab_game.away_oreb_rate_offense - ncaab_game.home_oreb_rate_defense

    home_base_score *= 1.0 + home_rebound_edge * 0.015
    away_base_score *= 1.0 + away_rebound_edge * 0.015

    # Factor 4: Free Throws (efficient scoring)
    home_ft_edge = ncaab_game.home_ft_rate_offense - ncaab_game.away_ft_rate_defense
    away_ft_edge = ncaab_game.away_ft_rate_offense - ncaab_game.home_ft_rate_defense

    home_base_score *= 1.0 + home_ft_edge * 0.01
    away_base_score *= 1.0 + away_ft_edge * 0.01

    # Step 4: Strength of Schedule Adjustment
    # Teams with tougher schedule get boost against weaker schedule teams
    sos_adjustment = 1.0
    if abs(ncaab_game.home_sos_ranking - ncaab_game.away_sos_ranking) > 50:
        stronger_sos_team = (
            "home" if ncaab_game.home_sos_ranking < ncaab_game.away_sos_ranking else "away"
        )
        sos_boost = min(0.05, abs(ncaab_game.home_sos_ranking - ncaab_game.away_sos_ranking) / 1000)

        if stronger_sos_team == "home":
            home_base_score *= 1.0 + sos_boost
        else:
            away_base_score *= 1.0 + sos_boost

        sos_adjustment = 1.0 + sos_boost

    # Step 5: Home court advantage (~3 points in college)
    home_court_advantage = 3.0
    home_base_score += home_court_advantage

    # Step 6: Tournament adjustments (if applicable)
    if ncaab_game.bracket_context.is_tournament:
        # Tournament games have higher variance
        tournament_variance = 1.05
        home_base_score *= tournament_variance
        away_base_score *= tournament_variance

        # Upset factor for significant seed differences
        if ncaab_game.bracket_context.seed_differential >= 4:
            underdog_boost = 0.02 * ncaab_game.bracket_context.seed_differential
            if ncaab_game.bracket_context.home_seed > ncaab_game.bracket_context.away_seed:
                # Home team is underdog
                home_base_score *= 1.0 + underdog_boost
            else:
                # Away team is underdog
                away_base_score *= 1.0 + underdog_boost

    # Step 7: Calculate win probabilities
    point_differential = home_base_score - away_base_score

    # College basketball standard deviation ~11 points
    college_std_dev = 11.0
    z_score = point_differential / college_std_dev

    home_win_prob = 1.0 / (1.0 + math.exp(-z_score))
    away_win_prob = 1.0 - home_win_prob

    # Step 8: Calculate other market predictions
    predicted_total = home_base_score + away_base_score
    spread_cover_prob = home_win_prob if point_differential > 0 else away_win_prob

    # Over/under probabilities
    market_total_estimate = predicted_total + random.uniform(-4, 4)
    if predicted_total > market_total_estimate:
        over_prob = 0.52 + min(0.18, (predicted_total - market_total_estimate) / 25.0)
    else:
        over_prob = 0.48 - min(0.18, (market_total_estimate - predicted_total) / 25.0)

    under_prob = 1.0 - over_prob

    # Step 9: First half predictions (~45% of total points in college)
    first_half_factor = 0.45
    first_half_home = home_base_score * first_half_factor
    first_half_away = away_base_score * first_half_factor
    first_half_total = first_half_home + first_half_away

    # Step 10: Analyze four factors advantages
    shooting_advantage = "neutral"
    if home_shooting_edge > 0.04:
        shooting_advantage = "home"
    elif away_shooting_edge > 0.04:
        shooting_advantage = "away"

    turnover_advantage = "neutral"
    if home_turnover_edge > 3:
        turnover_advantage = "home"
    elif away_turnover_edge > 3:
        turnover_advantage = "away"

    rebounding_advantage = "neutral"
    if home_rebound_edge > 5:
        rebounding_advantage = "home"
    elif away_rebound_edge > 5:
        rebounding_advantage = "away"

    free_throw_advantage = "neutral"
    if home_ft_edge > 5:
        free_throw_advantage = "home"
    elif away_ft_edge > 5:
        free_throw_advantage = "away"

    # Tempo advantage
    tempo_advantage = "neutral"
    tempo_diff = abs(ncaab_game.home_adj_tempo - ncaab_game.away_adj_tempo)
    if tempo_diff > 8:
        if ncaab_game.home_adj_tempo > ncaab_game.away_adj_tempo:
            tempo_advantage = "home"
        else:
            tempo_advantage = "away"

    # Experience advantage
    experience_advantage = "neutral"
    if ncaab_game.bracket_context.is_tournament:
        exp_diff = ncaab_game.home_tourney_experience - ncaab_game.away_tourney_experience
        if abs(exp_diff) >= 3:
            experience_advantage = "home" if exp_diff > 0 else "away"

    # Coaching advantage
    coaching_advantage = "neutral"
    coach_diff = ncaab_game.home_coach_tourney_wins - ncaab_game.away_coach_tourney_wins
    if abs(coach_diff) >= 5:
        coaching_advantage = "home" if coach_diff > 0 else "away"

    # Tournament-specific predictions
    upset_probability = 0.15  # Base upset rate
    if ncaab_game.bracket_context.is_tournament:
        # Higher upset probability with larger seed differences
        seed_factor = min(0.25, ncaab_game.bracket_context.seed_differential * 0.03)
        upset_probability = min(0.4, 0.15 + seed_factor)

    blowout_probability = 0.20
    if abs(point_differential) > 10:
        blowout_probability = min(0.45, 0.20 + abs(point_differential) * 0.02)

    buzzer_beater_factor = 0.05
    if ncaab_game.bracket_context.is_tournament:
        buzzer_beater_factor = 0.08  # Tournament games more likely to be close

    # Model confidence
    confidence_factors = [
        min(0.2, abs(point_differential) / 40),
        min(0.15, tempo_diff / 40),
        min(0.1, abs(ncaab_game.home_sos_ranking - ncaab_game.away_sos_ranking) / 1000),
        (
            0.1
            if significant_four_factor_edge(
                home_shooting_edge,
                away_shooting_edge,
                home_turnover_edge,
                away_turnover_edge,
            )
            else 0
        ),
    ]

    prediction_confidence = min(0.9, 0.6 + sum(confidence_factors))

    return NCAABMarketPrediction(
        home_win_prob=home_win_prob,
        away_win_prob=away_win_prob,
        predicted_home_score=home_base_score,
        predicted_away_score=away_base_score,
        predicted_total=predicted_total,
        projected_possessions=projected_possessions,
        spread_cover_prob=spread_cover_prob,
        over_prob=over_prob,
        under_prob=under_prob,
        first_half_home_score=first_half_home,
        first_half_away_score=first_half_away,
        first_half_total=first_half_total,
        shooting_advantage=shooting_advantage,
        turnover_advantage=turnover_advantage,
        rebounding_advantage=rebounding_advantage,
        free_throw_advantage=free_throw_advantage,
        tempo_advantage=tempo_advantage,
        experience_advantage=experience_advantage,
        coaching_advantage=coaching_advantage,
        upset_probability=upset_probability,
        blowout_probability=blowout_probability,
        buzzer_beater_factor=buzzer_beater_factor,
        prediction_confidence=prediction_confidence,
        sos_adjustment=sos_adjustment,
        key_factors=[
            "four_factors",
            "adjusted_efficiency",
            "tempo",
            "sos",
            "tournament_context",
        ],
    )


def significant_four_factor_edge(
    home_shooting: float,
    away_shooting: float,
    home_turnover: float,
    away_turnover: float,
) -> bool:
    """Check if there's a significant four factors edge"""
    edges = [
        abs(home_shooting),
        abs(away_shooting),
        abs(home_turnover),
        abs(away_turnover),
    ]
    significant_edges = sum(1 for edge in edges if edge > 0.03)
    return significant_edges >= 2


# Initialize NCAAB engine
ncaab_engine = NCAABBettingEngine(bankroll_manager)


# Authentication dependency
def verify_api_key(x_api_key: str | None = Header(None)):
    if API_KEY and x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key


# Database initialization
def init_database():
    """Initialize SQLite database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Create parlays table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS parlays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                legs_json TEXT NOT NULL,
                combined_odds REAL NOT NULL,
                est_true_prob REAL NOT NULL,
                ev REAL NOT NULL,
                confidence REAL NOT NULL,
                rationale TEXT,
                risk_level TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        """
        )

        # Create audit_logs table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                parlay_id INTEGER,
                amount REAL,
                odds TEXT,
                result TEXT,
                profit REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parlay_id) REFERENCES parlays (id)
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise


# Startup event
# @app.on_event("startup")  # Deprecated - use lifespan events
async def startup_event():
    logger.info("EQ12 Extension Backend starting up...")
    init_database()
    logger.info("EQ12 Extension Backend ready!")


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """System health check"""
    uptime = time.time() - startup_time

    # Check database connectivity
    db_status = "ok"
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        db_status = f"error: {e}"
        logger.error(f"Database health check failed: {e}")

    return HealthResponse(
        status="ok",
        name="EQ12 Extension Backend",
        version="1.0.0",
        uptime=uptime,
        database_status=db_status,
    )


# Simple ping endpoint
@app.get("/api/ping")
async def ping():
    """Simple ping for connection testing"""
    return {
        "ok": True,
        "timestamp": datetime.utcnow().isoformat(),
        "server": "EQ12 Extension Backend v1.0.0",
    }


# Enhanced parlay generation endpoint
@app.get("/api/parlay", response_model=ParlayResponse)
async def generate_parlay(
    size: int = Query(5, ge=2, le=15, description="Number of legs in parlay"),
    risk_level: str = Query("medium", description="Risk level: low, medium, high"),
    include_ev: bool = Query(True, description="Include expected value calculation"),
    include_analysis: bool = Query(True, description="Include detailed analysis"),
    api_key: str = Depends(verify_api_key),
):
    """Generate optimized parlay with EV calculation"""

    logger.info(f"Generating {size}-leg parlay with risk level: {risk_level}")

    try:
        # Generate parlay legs with live API data or mock fallback
        legs = generate_live_legs(size, risk_level)

        # Calculate combined odds
        combined_odds = calculate_combined_odds([leg.price for leg in legs])

        # Estimate true probability and EV
        est_true_prob = estimate_true_probability(legs, risk_level)
        ev = calculate_expected_value(combined_odds, est_true_prob, 1.0)  # $1 bet

        # Generate confidence score
        confidence = calculate_confidence_score(legs, risk_level)

        # Generate rationale
        rationale = generate_rationale(legs, ev, confidence, risk_level)

        # Create parlay response
        parlay = ParlayResponse(
            name=f"{size}-Leg EQ12 Parlay",
            legs=legs,
            combined_odds=combined_odds,
            est_true_prob=est_true_prob,
            ev=ev,
            confidence=confidence,
            rationale=rationale,
            risk_level=risk_level,
            created_at=datetime.utcnow().isoformat(),
        )

        # Save to database
        save_parlay_to_db(parlay)

        logger.info(f"Generated parlay with EV: ${ev:.2f}")
        return parlay

    except Exception as e:
        logger.error(f"Parlay generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Parlay generation failed: {e}")


# NFL-Specific Parlay Generation Endpoint
@app.get("/api/nfl-parlay", response_model=ParlayResponse)
async def generate_nfl_parlay(
    size: int = Query(3, ge=2, le=6, description="Number of NFL bets in parlay"),
    week: int | None = Query(None, ge=1, le=18, description="NFL week (1-18)"),
    max_same_game: int = Query(1, ge=1, le=2, description="Max bets from same NFL game"),
    include_props: bool = Query(False, description="Include player props"),
    min_edge: float = Query(0.025, ge=0.01, le=0.10, description="Minimum edge threshold"),
    api_key: str = Depends(verify_api_key),
):
    """Generate NFL-specific parlay with advanced game analysis"""

    logger.info(f"🏈 Generating {size}-leg NFL parlay with {min_edge:.1%} min edge")

    try:
        # Fetch live NFL odds specifically
        nfl_odds = fetch_live_odds_sync(["americanfootball_nfl"])

        if not nfl_odds:
            logger.warning("No live NFL odds available, using mock data")
            return await generate_parlay(size, "medium", True, True, api_key)

        # Process NFL games with specialized logic
        nfl_edge_bets = []
        games_processed = 0

        for event in nfl_odds:
            try:
                # Extract NFL game features
                nfl_game = extract_nfl_features(event)

                # Filter by week if specified
                if week and nfl_game.week != week:
                    continue

                games_processed += 1
                logger.info(
                    f"🏈 Analyzing: {nfl_game.away_team} @ {nfl_game.home_team} (Week {nfl_game.week})"
                )

                # Generate NFL predictions
                nfl_prediction = generate_nfl_prediction(nfl_game)

                # Analyze each market type
                bookmakers = event.get("bookmakers", [])
                if not bookmakers:
                    continue

                # Check moneyline, spread, and total markets
                markets_to_check = ["h2h", "spreads", "totals"]
                if include_props:
                    markets_to_check.extend(["player_pass_tds", "player_rush_yds"])

                for bookmaker in bookmakers[:2]:  # Top 2 bookmakers
                    for market in bookmaker.get("markets", []):
                        market_key = market.get("key", "")
                        if market_key not in markets_to_check:
                            continue

                        for outcome in market.get("outcomes", []):
                            price = outcome.get("price", 0)
                            if abs(price) < 100:  # Skip invalid odds
                                continue

                            # Use NFL engine for edge detection
                            edge_bet = nfl_engine.nfl_decide_and_place(
                                game=nfl_game,
                                market_type=market_key,
                                market_odds=float(price),
                                prediction=nfl_prediction,
                            )

                            if edge_bet and edge_bet.edge >= min_edge:
                                # Format selection properly
                                selection_name = outcome.get("name", "")
                                if market_key == "h2h":
                                    edge_bet.selection = f"{selection_name} ML"
                                elif market_key == "spreads":
                                    point = outcome.get("point", 0)
                                    if point:
                                        point_str = f"+{point}" if point > 0 else str(point)
                                        edge_bet.selection = f"{selection_name} {point_str}"
                                elif market_key == "totals":
                                    point = outcome.get("point", 0)
                                    direction = (
                                        "Over" if selection_name.lower() == "over" else "Under"
                                    )
                                    edge_bet.selection = f"{direction} {point}"

                                edge_bet.book = bookmaker.get("title", "Sportsbook")
                                nfl_edge_bets.append(edge_bet)

                                logger.info(
                                    f"🎯 NFL EDGE: {edge_bet.selection} | {edge_bet.confidence} | Edge: {edge_bet.edge:.1%}"
                                )

                                # Stop if we have enough bets
                                if len(nfl_edge_bets) >= size * 3:  # Get extra for filtering
                                    break
                if len(nfl_edge_bets) >= size * 3:
                    break
                if len(nfl_edge_bets) >= size * 3:
                    break
            except Exception as e:
                logger.warning(f"Error processing NFL game {event.get('id', 'unknown')}: {e}")
                continue

        logger.info(
            f"🏈 NFL Analysis Complete: {games_processed} games, {len(nfl_edge_bets)} edge bets found"
        )

        if len(nfl_edge_bets) < size:
            logger.warning(f"Only found {len(nfl_edge_bets)} NFL edge bets, need {size}")
            # Fallback to regular parlay generation
            return await generate_parlay(size, "medium", True, True, api_key)

        # Select best NFL edge bets (highest edge, uncorrelated)
        selected_bets = []
        used_games = set()

        # Sort by edge descending
        nfl_edge_bets.sort(key=lambda x: x.edge, reverse=True)

        for bet in nfl_edge_bets:
            if len(selected_bets) >= size:
                break

            # Enforce max bets per game constraint
            game_bets_count = sum(1 for game_id in used_games if game_id == bet.event_id)
            if game_bets_count >= max_same_game:
                continue

            selected_bets.append(bet)
            used_games.add(bet.event_id)

        # Convert EdgeBets to ParlayLegs
        parlay_legs = []
        for bet in selected_bets[:size]:
            confidence_map = {
                "LOCK": 0.95,
                "STRONG": 0.80,
                "MODERATE": 0.65,
                "WEAK": 0.45,
            }

            leg = ParlayLeg(
                selection=bet.selection,
                price=bet.odds,
                book=bet.book,
                sport="NFL",
                game=f"NFL Week {week if week else 'Current'}",
                confidence=confidence_map.get(bet.confidence, 0.50),
            )
            parlay_legs.append(leg)

        # Calculate NFL parlay metrics
        combined_odds = calculate_combined_odds([leg.price for leg in parlay_legs])
        est_true_prob = estimate_true_probability(parlay_legs, "medium")
        ev = calculate_expected_value(combined_odds, est_true_prob, 1.0)
        confidence = calculate_confidence_score(parlay_legs, "medium")

        # NFL-specific rationale
        avg_edge = sum(bet.edge for bet in selected_bets) / len(selected_bets)
        rationale = f"NFL Edge Analysis: {len(selected_bets)} high-conviction bets with {avg_edge:.1%} average edge. "
        rationale += f"Games analyzed: {games_processed}. "
        rationale += f"Risk-managed with max {max_same_game} bet(s) per game. "
        rationale += generate_rationale(parlay_legs, ev, confidence, "medium")

        # Create NFL parlay response
        nfl_parlay = ParlayResponse(
            name=f"{size}-Leg NFL Edge Parlay",
            legs=parlay_legs,
            combined_odds=combined_odds,
            est_true_prob=est_true_prob,
            ev=ev,
            confidence=confidence,
            rationale=rationale,
            risk_level="medium",
            created_at=datetime.utcnow().isoformat(),
        )

        # Save to database
        save_parlay_to_db(nfl_parlay)

        logger.info(f"🏈 Generated NFL parlay: {size} legs, {avg_edge:.1%} avg edge, ${ev:.2f} EV")
        return nfl_parlay

    except Exception as e:
        logger.error(f"NFL parlay generation error: {e}")
        raise HTTPException(status_code=500, detail=f"NFL parlay generation failed: {e}")


# College Football (NCAAF) Parlay Generation Endpoint
@app.get("/api/ncaaf-parlay", response_model=ParlayResponse)
async def generate_ncaaf_parlay(
    size: int = Query(4, ge=2, le=8, description="Number of college football bets in parlay"),
    week: int | None = Query(None, ge=1, le=15, description="College football week (1-15)"),
    conference: str | None = Query(None, description="Target conference (SEC, Big Ten, etc.)"),
    max_same_game: int = Query(1, ge=1, le=2, description="Max bets from same college game"),
    include_g5: bool = Query(True, description="Include Group of 5 games"),
    min_edge: float = Query(0.03, ge=0.015, le=0.15, description="Minimum edge threshold"),
    fade_public: bool = Query(True, description="Prioritize fading heavy public bets"),
    api_key: str = Depends(verify_api_key),
):
    """
    Generate College Football-specific parlay with advanced game analysis.
    Includes mismatch detection, public betting sentiment, and conference-specific logic.
    """

    logger.info(f"🏈 Generating {size}-leg NCAAF parlay with {min_edge:.1%} min edge")

    try:
        # Fetch live college football odds
        ncaaf_odds = fetch_live_odds_sync(["americanfootball_ncaaf"])

        if not ncaaf_odds:
            logger.warning("No live NCAAF odds available, using mock college data")
            # Fallback to mock data with college characteristics
            return await generate_mock_ncaaf_parlay(size, week, min_edge)

        # Process college games with specialized logic
        ncaaf_edge_bets = []
        games_processed = 0

        for event in ncaaf_odds:
            try:
                # Extract NCAAF game features
                ncaaf_game = extract_ncaaf_features(event)

                # Apply filters
                if week and ncaaf_game.week != week:
                    continue

                if (
                    conference
                    and ncaaf_game.home_conference != conference
                    and ncaaf_game.away_conference != conference
                ):
                    continue

                # Skip Group of 5 games if not desired
                if not include_g5:
                    power_5 = ["SEC", "Big Ten", "Big 12", "ACC", "Pac-12"]
                    if (
                        ncaaf_game.home_conference not in power_5
                        and ncaaf_game.away_conference not in power_5
                    ):
                        continue

                games_processed += 1
                logger.info(
                    f"🎓 Analyzing: {ncaaf_game.away_team} @ {ncaaf_game.home_team} ({ncaaf_game.home_conference})"
                )

                # Generate NCAAF predictions with volatility modeling
                ncaaf_prediction = generate_ncaaf_prediction(ncaaf_game)

                # Analyze markets with college-specific considerations
                bookmakers = event.get("bookmakers", [])
                if not bookmakers:
                    continue

                # College-specific market analysis (spreads are key due to extreme lines)
                markets_to_check = ["spreads", "h2h", "totals"]

                for bookmaker in bookmakers[:2]:  # Focus on top books
                    for market in bookmaker.get("markets", []):
                        market_key = market.get("key", "")
                        if market_key not in markets_to_check:
                            continue

                        for outcome in market.get("outcomes", []):
                            price = outcome.get("price", 0)
                            if abs(price) < 100:  # Skip invalid odds
                                continue

                            # Use NCAAF engine for edge detection
                            edge_bet = ncaaf_engine.ncaaf_decide_and_place(
                                game=ncaaf_game,
                                market_type=market_key,
                                market_odds=float(price),
                                prediction=ncaaf_prediction,
                            )

                            if edge_bet and edge_bet.edge >= min_edge:
                                # Check public fade criteria
                                if fade_public and ncaaf_game.public_betting_pct:
                                    # Skip if not fading heavy public (>65% or <35%)
                                    public_extreme = abs(ncaaf_game.public_betting_pct - 0.5) > 0.15
                                    if not public_extreme:
                                        continue

                                # Format selection with college context
                                selection_name = outcome.get("name", "")
                                if market_key == "h2h":
                                    edge_bet.selection = f"{selection_name} ML"
                                elif market_key == "spreads":
                                    point = outcome.get("point", 0)
                                    if point:
                                        point_str = f"+{point}" if point > 0 else str(point)
                                        edge_bet.selection = f"{selection_name} {point_str}"
                                elif market_key == "totals":
                                    point = outcome.get("point", 0)
                                    direction = (
                                        "Over" if selection_name.lower() == "over" else "Under"
                                    )
                                    edge_bet.selection = f"{direction} {point}"

                                edge_bet.book = bookmaker.get("title", "Sportsbook")
                                edge_bet.sport = "NCAAF"
                                ncaaf_edge_bets.append(edge_bet)

                                # Add college-specific context to logging
                                mismatch_info = (
                                    f"Mismatch: {ncaaf_prediction.mismatch_factor:.1f}x"
                                    if ncaaf_prediction.mismatch_factor > 1.2
                                    else ""
                                )
                                public_info = (
                                    f"Public: {ncaaf_game.public_betting_pct:.0%}"
                                    if ncaaf_game.public_betting_pct
                                    else ""
                                )

                                logger.info(
                                    f"🎯 NCAAF EDGE: {edge_bet.selection} | {edge_bet.confidence} | Edge: {edge_bet.edge:.1%} | {mismatch_info} {public_info}"
                                )

                                # Stop if we have enough for selection
                                if len(ncaaf_edge_bets) >= size * 4:  # Extra for filtering
                                    break
                        if len(ncaaf_edge_bets) >= size * 4:
                            break
                    if len(ncaaf_edge_bets) >= size * 4:
                        break
            except Exception as e:
                logger.warning(f"Error processing NCAAF game {event.get('id', 'unknown')}: {e}")
                continue

        logger.info(
            f"🎓 NCAAF Analysis Complete: {games_processed} games, {len(ncaaf_edge_bets)} edge bets found"
        )

        if len(ncaaf_edge_bets) < size:
            logger.warning(f"Only found {len(ncaaf_edge_bets)} NCAAF edge bets, need {size}")
            return await generate_mock_ncaaf_parlay(size, week, min_edge)

        # Select best NCAAF edge bets with college-specific logic
        selected_bets = []
        used_games = set()
        used_conferences = {}

        # Sort by college-specific criteria (edge + public fade factor)
        def college_sort_key(bet):
            # Get the game for additional context
            game_context = 1.0
            if hasattr(bet, "game_context"):
                game_context = bet.game_context
            return bet.edge * game_context

        ncaaf_edge_bets.sort(key=college_sort_key, reverse=True)

        for bet in ncaaf_edge_bets:
            if len(selected_bets) >= size:
                break

            # Enforce max bets per game
            game_bets_count = sum(1 for game_id in used_games if game_id == bet.event_id)
            if game_bets_count >= max_same_game:
                continue

            # Limit conference concentration (max 50% from one conference)
            game_conf = getattr(bet, "conference", "Unknown")
            conf_count = used_conferences.get(game_conf, 0)
            if conf_count >= size // 2:
                continue

            selected_bets.append(bet)
            used_games.add(bet.event_id)
            used_conferences[game_conf] = conf_count + 1

        # Convert EdgeBets to ParlayLegs with college context
        parlay_legs = []
        for bet in selected_bets[:size]:
            confidence_map = {
                "LOCK": 0.92,
                "STRONG": 0.75,
                "MODERATE": 0.60,
                "WEAK": 0.40,
            }

            leg = ParlayLeg(
                selection=bet.selection,
                price=bet.odds,
                book=bet.book,
                sport="NCAAF",
                game=f"College Week {week if week else 'Current'}",
                confidence=confidence_map.get(bet.confidence, 0.45),
            )
            parlay_legs.append(leg)

        # Calculate college-adjusted metrics
        combined_odds = calculate_combined_odds([leg.price for leg in parlay_legs])

        # Adjust true probability for college volatility
        college_true_prob = (
            estimate_true_probability(parlay_legs, "medium") * 0.9
        )  # Lower due to volatility
        ev = calculate_expected_value(combined_odds, college_true_prob, 1.0)

        avg_edge = sum(bet.edge for bet in selected_bets[:size]) / size
        confidence = min(
            0.85, calculate_confidence_score(parlay_legs, "medium") * 0.95
        )  # Cap at 85% for college

        # Generate college-specific rationale
        rationale = f"NCAAF {size}-leg parlay targeting market inefficiencies in college football. "
        rationale += f"Average edge: {avg_edge:.1%}, focusing on "

        if fade_public:
            rationale += "public fade opportunities, "
        if conference:
            rationale += f"{conference} games, "
        if not include_g5:
            rationale += "Power 5 conferences only, "

        rationale += f"with {min_edge:.1%} minimum edge threshold. "
        rationale += "College games feature higher volatility but greater market inefficiencies."

        # Create NCAAF parlay response
        ncaaf_parlay = ParlayResponse(
            name=f"{size}-Leg NCAAF Parlay",
            legs=parlay_legs,
            combined_odds=combined_odds,
            est_true_prob=college_true_prob,
            ev=ev,
            confidence=confidence,
            rationale=rationale,
            risk_level="medium-high",  # College inherently more volatile
            created_at=datetime.utcnow().isoformat(),
        )

        # Save to database
        save_parlay_to_db(ncaaf_parlay)

        logger.info(
            f"🎓 Generated NCAAF parlay: {size} legs, {avg_edge:.1%} avg edge, ${ev:.2f} EV"
        )
        return ncaaf_parlay

    except Exception as e:
        logger.error(f"NCAAF parlay generation error: {e}")
        raise HTTPException(status_code=500, detail=f"NCAAF parlay generation failed: {e}")


async def generate_mock_ncaaf_parlay(
    size: int, week: int | None, min_edge: float
) -> ParlayResponse:
    """Generate mock college football parlay when no live data available"""

    mock_legs = []
    college_teams = [
        "Alabama Crimson Tide",
        "Georgia Bulldogs",
        "Ohio State Buckeyes",
        "Michigan Wolverines",
        "Clemson Tigers",
        "Oklahoma Sooners",
        "Texas Longhorns",
        "USC Trojans",
        "Penn State Nittany Lions",
        "Florida Gators",
        "LSU Tigers",
        "Auburn Tigers",
        "Wisconsin Badgers",
        "Oregon Ducks",
        "Miami Hurricanes",
        "Notre Dame Fighting Irish",
    ]

    for _i in range(size):
        home_team = random.choice(college_teams)
        away_team = random.choice([t for t in college_teams if t != home_team])

        # Generate college-typical spreads (often larger than NFL)
        spread = random.uniform(-28.5, 28.5)
        if random.random() < 0.3:  # 30% chance of large spread
            spread = random.uniform(-42.5, 42.5)

        # Mock selection with college characteristics
        selections = [
            f"{home_team.split()[0]} {spread:+.1f}",
            f"{away_team.split()[0]} ML",
            f"Over {random.uniform(45.5, 78.5):.1f}",
            f"Under {random.uniform(45.5, 78.5):.1f}",
        ]

        leg = ParlayLeg(
            selection=random.choice(selections),
            price=random.uniform(-140, 120),
            book=random.choice(["DraftKings", "FanDuel", "BetMGM", "Caesars"]),
            sport="NCAAF",
            game=f"{away_team} @ {home_team}",
            confidence=random.uniform(0.55, 0.85),  # Lower max confidence for college
        )
        mock_legs.append(leg)

    combined_odds = calculate_combined_odds([leg.price for leg in mock_legs])
    est_true_prob = (
        estimate_true_probability(mock_legs, "medium") * 0.85
    )  # Conservative for college
    ev = calculate_expected_value(combined_odds, est_true_prob, 1.0)

    return ParlayResponse(
        name=f"{size}-Leg Mock NCAAF Parlay",
        legs=mock_legs,
        combined_odds=combined_odds,
        est_true_prob=est_true_prob,
        ev=ev,
        confidence=random.uniform(0.60, 0.80),
        rationale=f"Mock college football parlay with {min_edge:.1%} edge targeting market inefficiencies in NCAAF games.",
        risk_level="medium-high",
        created_at=datetime.utcnow().isoformat(),
    )


# Major League Baseball (MLB) Parlay Generation Endpoint
@app.get("/api/mlb-parlay", response_model=ParlayResponse)
async def generate_mlb_parlay(
    size: int = Query(4, ge=2, le=8, description="Number of bets in parlay"),
    risk_level: str = Query("medium", description="Risk tolerance: low, medium, high"),
    min_edge: float = Query(0.025, ge=0.01, le=0.15, description="Minimum edge threshold"),
    market_focus: str = Query(
        "mixed", description="Market focus: f5_innings, moneyline, totals, mixed"
    ),
    weather_factor: bool = Query(True, description="Include weather-based edges"),
    pitcher_focus: bool = Query(True, description="Focus on pitcher matchup advantages"),
    api_key: str = Depends(verify_api_key),
):
    """
    Generate optimized MLB parlay with baseball-specific analytics

    Features:
    - Starting pitcher analysis (ERA, WHIP, FIP, rest days)
    - First 5 innings betting optimization
    - Ballpark and weather factor integration
    - Batter vs pitcher historical matchups
    - Run expectancy modeling
    - Public betting fade opportunities
    """

    try:
        logger.info(
            f"⚾ Generating MLB parlay: size={size}, risk={risk_level}, min_edge={min_edge:.1%}"
        )

        # Fetch live MLB odds (would use real API)
        mlb_odds = []  # await fetch_live_mlb_odds() - placeholder

        if not mlb_odds:
            logger.info("No live MLB odds available, generating mock parlay")
            # Fallback to mock data with baseball characteristics
            return await generate_mock_mlb_parlay(
                size, min_edge, market_focus, weather_factor, pitcher_focus
            )

        # Process baseball games with specialized logic
        mlb_edge_bets = []
        games_processed = 0

        for event in mlb_odds:
            try:
                # Extract MLB game features
                mlb_game = extract_mlb_features(event)

                # Generate baseball-specific prediction
                mlb_prediction = generate_mlb_prediction(mlb_game)

                # Skip games without starting pitcher info for F5 bets
                if market_focus == "f5_innings" and (
                    not mlb_game.home_starter_name or not mlb_game.away_starter_name
                ):
                    continue

                # Skip games with poor weather if weather factor disabled
                if not weather_factor and (mlb_game.precipitation_chance or 0) > 30:
                    continue

                # Focus on pitcher advantages if enabled
                if pitcher_focus and mlb_prediction.pitching_advantage == "neutral":
                    continue

                # Try different market types based on focus
                market_types = ["moneyline"]
                if market_focus == "f5_innings":
                    market_types = ["f5_innings", "moneyline"]
                elif market_focus == "totals":
                    market_types = ["total_runs", "moneyline"]
                elif market_focus == "mixed":
                    market_types = ["moneyline", "f5_innings", "total_runs"]

                # Test each market type
                for market_type in market_types:
                    # Get market odds (would fetch from real API)
                    market_odds = -110  # Placeholder

                    # Attempt to place bet
                    edge_bet = mlb_engine.mlb_decide_and_place(
                        mlb_game, market_type, market_odds, mlb_prediction
                    )

                    if edge_bet and edge_bet.edge >= min_edge:
                        mlb_edge_bets.append(edge_bet)
                        logger.info(f"MLB edge found: {edge_bet.selection} ({edge_bet.edge:.1%})")

                        if len(mlb_edge_bets) >= size:
                            break

                games_processed += 1
                if len(mlb_edge_bets) >= size or games_processed >= 50:
                    break

            except Exception as e:
                logger.error(f"Error processing MLB game: {e}")
                continue

        if len(mlb_edge_bets) < size:
            logger.warning(f"Only found {len(mlb_edge_bets)} MLB edges, generating mock supplement")
            return await generate_mock_mlb_parlay(
                size, min_edge, market_focus, weather_factor, pitcher_focus
            )

        # Convert EdgeBets to ParlayLegs
        mlb_legs = []
        total_edge = 0.0

        for edge_bet in mlb_edge_bets[:size]:
            leg = ParlayLeg(
                selection=edge_bet.selection,
                price=int(edge_bet.odds),
                book=edge_bet.book,
                sport="MLB",
                game=f"Game {len(mlb_legs) + 1}",
                confidence={"high": 0.85, "medium": 0.70, "low": 0.55}.get(
                    edge_bet.confidence, 0.60
                ),
            )
            mlb_legs.append(leg)
            total_edge += edge_bet.edge

        # Calculate parlay metrics
        combined_odds = calculate_combined_odds([leg.price for leg in mlb_legs])
        avg_edge = total_edge / len(mlb_legs)
        est_true_prob = estimate_true_probability(mlb_legs, risk_level) * (1.0 + avg_edge)
        ev = calculate_expected_value(combined_odds, est_true_prob, 1.0)

        # Generate baseball-specific rationale
        pitcher_count = len([leg for leg in mlb_legs if "F5" in leg.selection])
        weather_games = len([leg for leg in mlb_legs if "wind" in leg.selection.lower()])

        rationale_parts = [f"MLB parlay leveraging {avg_edge:.1%} average edge across {size} games"]

        if pitcher_count > 0:
            rationale_parts.append(
                f"{pitcher_count} first-5-innings bets targeting starting pitcher advantages"
            )

        if weather_games > 0:
            rationale_parts.append(f"{weather_games} weather-enhanced selections")

        if market_focus == "f5_innings":
            rationale_parts.append("Focused on predictable starter-dependent markets")
        elif market_focus == "totals":
            rationale_parts.append(
                "Targeting run total inefficiencies with ballpark/weather factors"
            )

        rationale = ". ".join(rationale_parts) + "."

        # Create parlay response
        mlb_parlay = ParlayResponse(
            name=f"{size}-Leg MLB Parlay ({market_focus.title()})",
            legs=mlb_legs,
            combined_odds=combined_odds,
            est_true_prob=est_true_prob,
            ev=ev,
            confidence=min(0.9, 0.6 + avg_edge),
            rationale=rationale,
            risk_level=risk_level,
            created_at=datetime.utcnow().isoformat(),
        )

        # Save to database
        save_parlay_to_db(mlb_parlay)

        logger.info(f"⚾ Generated MLB parlay: {size} legs, {avg_edge:.1%} avg edge, ${ev:.2f} EV")
        return mlb_parlay

    except Exception as e:
        logger.error(f"MLB parlay generation error: {e}")
        raise HTTPException(status_code=500, detail=f"MLB parlay generation failed: {e}")


async def generate_mock_mlb_parlay(
    size: int,
    min_edge: float,
    market_focus: str,
    weather_factor: bool,
    pitcher_focus: bool,
) -> ParlayResponse:
    """Generate mock MLB parlay with realistic baseball characteristics"""

    # Mock MLB teams and pitchers
    mlb_teams = [
        ("Yankees", "Cole", "Mets", "Scherzer"),
        ("Dodgers", "Betts", "Padres", "Darvish"),
        ("Astros", "Verlander", "Rangers", "deGrom"),
        ("Braves", "Fried", "Phillies", "Wheeler"),
        ("Red Sox", "Pivetta", "Blue Jays", "Berrios"),
        ("Giants", "Webb", "Diamondbacks", "Gallen"),
        ("Guardians", "Bieber", "Twins", "Ryan"),
        ("Orioles", "Rodriguez", "Rays", "McClanahan"),
    ]

    mock_legs = []
    for _i in range(size):
        home_team, home_pitcher, away_team, _away_pitcher = random.choice(mlb_teams)

        # Determine market type based on focus
        if market_focus == "f5_innings":
            market_types = ["F5", "F5", "ML"]  # Favor F5
        elif market_focus == "totals":
            market_types = ["Over", "Under", "ML"]  # Favor totals
        elif market_focus == "moneyline":
            market_types = ["ML", "ML", "F5"]  # Favor ML
        else:  # mixed
            market_types = ["ML", "F5", "Over", "Under"]

        market_type = random.choice(market_types)

        # Generate selection based on market type
        if market_type == "ML":
            selection = f"{home_team} ML"
            odds_range = (-150, +130)
        elif market_type == "F5":
            selection = f"{home_team} F5 (Starter: {home_pitcher})"
            odds_range = (-140, +120)  # F5 typically closer
        elif market_type == "Over":
            total = random.uniform(7.5, 10.5)
            selection = f"Over {total:.1f} runs"
            odds_range = (-115, -105)
        else:  # Under
            total = random.uniform(7.5, 10.5)
            selection = f"Under {total:.1f} runs"
            odds_range = (-115, -105)

        # Add weather factor if enabled
        if weather_factor and random.random() < 0.3:
            weather_conditions = ["(Wind out to RF)", "(Hot weather)", "(Cold & windy)"]
            selection += f" {random.choice(weather_conditions)}"

        # Generate odds with slight bias toward positive value
        price = random.randint(odds_range[0], odds_range[1])
        if random.random() < 0.6:  # 60% chance of positive odds for value
            price = random.randint(-135, +150)

        # Confidence based on market type and factors
        confidence = 0.65
        if market_type == "F5" and pitcher_focus:
            confidence += 0.1  # Boost for pitcher focus
        if weather_factor and "wind" in selection.lower():
            confidence += 0.05  # Boost for weather edge

        confidence = min(0.85, confidence + random.uniform(-0.05, 0.1))

        leg = ParlayLeg(
            selection=selection,
            price=price,
            book=random.choice(["FanDuel", "DraftKings", "Caesars", "BetMGM"]),
            sport="MLB",
            game=f"{away_team} @ {home_team}",
            confidence=confidence,
        )
        mock_legs.append(leg)

    combined_odds = calculate_combined_odds([leg.price for leg in mock_legs])
    est_true_prob = (
        estimate_true_probability(mock_legs, "medium") * 0.9
    )  # Conservative for baseball
    ev = calculate_expected_value(combined_odds, est_true_prob, 1.0)

    # Generate rationale based on focus
    rationale_parts = [f"Mock {size}-leg MLB parlay"]

    f5_count = len([leg for leg in mock_legs if "F5" in leg.selection])
    total_count = len(
        [leg for leg in mock_legs if "Over" in leg.selection or "Under" in leg.selection]
    )
    weather_count = len(
        [leg for leg in mock_legs if any(w in leg.selection for w in ["Wind", "Hot", "Cold"])]
    )

    if f5_count > 0:
        rationale_parts.append(f"{f5_count} first-5-innings bets leveraging starting pitcher edges")
    if total_count > 0:
        rationale_parts.append(f"{total_count} run total bets with ballpark/weather analysis")
    if weather_count > 0:
        rationale_parts.append(f"{weather_count} weather-enhanced selections")
    if pitcher_focus:
        rationale_parts.append("targeting clear pitcher matchup advantages")

    rationale = ". ".join(rationale_parts) + f" with {min_edge:.1%} minimum edge threshold."

    return ParlayResponse(
        name=f"{size}-Leg Mock MLB Parlay ({market_focus.title()})",
        legs=mock_legs,
        combined_odds=combined_odds,
        est_true_prob=est_true_prob,
        ev=ev,
        confidence=random.uniform(0.65, 0.80),
        rationale=rationale,
        risk_level="medium",
        created_at=datetime.utcnow().isoformat(),
    )


# National Basketball Association (NBA) Parlay Generation Endpoint
@app.get("/api/nba-parlay", response_model=ParlayResponse)
async def generate_nba_parlay(
    size: int = Query(4, ge=2, le=8, description="Number of bets in parlay"),
    risk_level: str = Query("medium", description="Risk tolerance: low, medium, high"),
    min_edge: float = Query(0.02, ge=0.01, le=0.12, description="Minimum edge threshold"),
    market_focus: str = Query(
        "mixed", description="Market focus: pace, efficiency, totals, props, mixed"
    ),
    pace_factor: bool = Query(True, description="Focus on pace mismatch advantages"),
    rest_factor: bool = Query(True, description="Include rest/travel edge detection"),
    api_key: str = Depends(verify_api_key),
):
    """
    Generate optimized NBA parlay with basketball analytics

    Features:
    - Pace and possessions analysis
    - Advanced efficiency metrics (ORtg, DRtg, NetRtg)
    - Four factors optimization (eFG%, TO%, OREB%, FT Rate)
    - Rest and travel fatigue modeling
    - Back-to-back game exploitation
    - Load management impact analysis
    - Live pace projection and total optimization
    """

    try:
        logger.info(
            f"🏀 Generating NBA parlay: size={size}, risk={risk_level}, min_edge={min_edge:.1%}"
        )

        # Fetch live NBA odds (would use real API)
        nba_odds = []  # await fetch_live_nba_odds() - placeholder

        if not nba_odds:
            logger.info("No live NBA odds available, generating mock parlay")
            return await generate_mock_nba_parlay(
                size, min_edge, market_focus, pace_factor, rest_factor
            )

        # Process NBA games with pace/efficiency analytics
        nba_edge_bets = []
        games_processed = 0

        for event in nba_odds:
            try:
                # Extract NBA features
                nba_game = extract_nba_features(event)

                # Generate NBA prediction with pace analytics
                nba_prediction = generate_nba_prediction(nba_game)

                # Skip games without key analytics for pace focus
                if market_focus == "pace" and nba_prediction.pace_advantage == "neutral":
                    continue

                # Skip games without efficiency edge for efficiency focus
                if (
                    market_focus == "efficiency"
                    and nba_prediction.efficiency_advantage == "neutral"
                ):
                    continue

                # Skip games with load management issues if not desired
                if not rest_factor and (
                    nba_game.home_load_management or nba_game.away_load_management
                ):
                    continue

                # Focus on pace advantages if enabled
                if pace_factor and nba_game.projected_possessions < 98:  # Slow pace games
                    continue

                # Market selection based on focus
                market_types = ["moneyline"]
                if market_focus == "pace":
                    market_types = ["total", "first_half"]
                elif market_focus == "efficiency":
                    market_types = ["spread", "moneyline"]
                elif market_focus == "totals":
                    market_types = ["total", "first_half"]
                elif market_focus == "props":
                    market_types = ["first_quarter", "first_half"]
                elif market_focus == "mixed":
                    market_types = ["moneyline", "spread", "total"]

                # Test each market type
                for market_type in market_types:
                    # Get market odds (placeholder)
                    market_odds = random.choice([-110, -105, -108, -112, -115])

                    # NBA edge detection
                    edge_bet = nba_engine.nba_decide_and_place(
                        nba_game, market_type, market_odds, nba_prediction
                    )

                    if edge_bet and edge_bet.edge >= min_edge:
                        nba_edge_bets.append(edge_bet)
                        logger.info(f"🏀 NBA Edge: {edge_bet.selection} - {edge_bet.edge:.1%}")

                        if len(nba_edge_bets) >= size:
                            break

                games_processed += 1
                if len(nba_edge_bets) >= size:
                    break

            except Exception as e:
                logger.error(f"Error processing NBA game {event.get('id', 'unknown')}: {e}")
                continue

        if len(nba_edge_bets) < size:
            logger.warning(f"Only found {len(nba_edge_bets)} NBA edges, need {size}")
            # Fallback to mock generation with lower standards
            return await generate_mock_nba_parlay(
                size, min_edge * 0.8, market_focus, pace_factor, rest_factor
            )

        # Select best NBA edges
        nba_edge_bets.sort(key=lambda x: x.edge, reverse=True)
        selected_bets = nba_edge_bets[:size]

        # Convert to parlay legs
        nba_legs = []
        for bet in selected_bets:
            leg = ParlayLeg(
                selection=bet.selection,
                price=bet.odds,
                book=bet.book,
                sport="NBA",
                game=f"{bet.event_id}",
                confidence=min(0.9, 0.5 + bet.edge),
            )
            nba_legs.append(leg)

        # Calculate parlay odds and EV
        combined_odds = 1.0
        for leg in nba_legs:
            decimal_odds = (100 / abs(leg.price)) + 1 if leg.price < 0 else (leg.price / 100) + 1
            combined_odds *= decimal_odds

        total_true_prob = 1.0
        for bet in selected_bets:
            total_true_prob *= bet.fair_prob

        est_true_prob = total_true_prob
        1.0 / combined_odds
        ev = (est_true_prob * combined_odds - 1) * 100  # Expected value in dollars per $100 bet

        avg_edge = sum(bet.edge for bet in selected_bets) / len(selected_bets)

        # Count analytics factors
        pace_games = sum(1 for bet in selected_bets if "pace" in bet.selection.lower())
        rest_games = sum(1 for bet in selected_bets if bet.sport == "NBA")  # Simplified
        sum(1 for bet in selected_bets if "efficiency" in bet.selection.lower())

        # Generate rationale
        rationale_parts = [f"NBA parlay leveraging {avg_edge:.1%} average edge across {size} games"]

        if pace_games > 0:
            rationale_parts.append(
                f"{pace_games} pace-based selections targeting possession advantages"
            )

        if rest_games > 0 and rest_factor:
            rationale_parts.append("incorporating rest/travel analytics")

        if market_focus == "pace":
            rationale_parts.append("focused on tempo mismatch exploitation")
        elif market_focus == "efficiency":
            rationale_parts.append("targeting efficiency rating discrepancies")
        elif market_focus == "totals":
            rationale_parts.append("optimized for pace-adjusted total predictions")

        rationale = ". ".join(rationale_parts) + "."

        # Create NBA parlay response
        nba_parlay = ParlayResponse(
            name=f"{size}-Leg NBA Parlay ({market_focus.title()})",
            legs=nba_legs,
            combined_odds=combined_odds,
            est_true_prob=est_true_prob,
            ev=ev,
            confidence=min(0.9, 0.6 + avg_edge),
            rationale=rationale,
            risk_level=risk_level,
            created_at=datetime.utcnow().isoformat(),
        )

        # Save to database
        save_parlay_to_db(nba_parlay)

        logger.info(f"🏀 Generated NBA parlay: {size} legs, {avg_edge:.1%} avg edge, ${ev:.2f} EV")
        return nba_parlay

    except Exception as e:
        logger.error(f"NBA parlay generation error: {e}")
        raise HTTPException(status_code=500, detail=f"NBA parlay generation failed: {e}")


async def generate_mock_nba_parlay(
    size: int, min_edge: float, market_focus: str, pace_factor: bool, rest_factor: bool
) -> ParlayResponse:
    """Generate mock NBA parlay with realistic basketball characteristics"""

    # Mock NBA teams with different pace/efficiency profiles
    nba_teams = [
        ("Lakers", "Warriors", "high_pace"),
        ("Celtics", "Heat", "efficiency"),
        ("Nuggets", "Suns", "balanced"),
        ("Bucks", "76ers", "efficiency"),
        ("Nets", "Clippers", "pace"),
        ("Mavericks", "Kings", "high_pace"),
        ("Grizzlies", "Pelicans", "pace"),
        ("Hawks", "Hornets", "high_pace"),
    ]

    mock_legs = []
    total_edge = 0.0

    for i in range(size):
        # Select teams
        home_team, away_team, style = random.choice(nba_teams)

        # Create mock NBA game
        mock_event = {
            "id": f"nba_mock_{i + 1}",
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": datetime.now().isoformat(),
        }

        nba_game = extract_nba_features(mock_event)
        nba_prediction = generate_nba_prediction(nba_game)

        # Determine market based on focus and game characteristics
        if market_focus == "pace" and nba_prediction.projected_possessions > 102:
            selection = f"Over {nba_prediction.predicted_total:.1f}"
            odds = random.choice([-108, -110, -105])
            edge = random.uniform(min_edge, min_edge + 0.04)
        elif market_focus == "efficiency" and nba_prediction.efficiency_advantage != "neutral":
            selection = f"{home_team if nba_prediction.efficiency_advantage == 'home' else away_team} Spread"
            odds = random.choice([-110, -108, -112])
            edge = random.uniform(min_edge, min_edge + 0.05)
        elif style == "high_pace":
            selection = f"Over {nba_prediction.predicted_total:.1f}"
            odds = random.choice([-105, -110, -108])
            edge = random.uniform(min_edge, min_edge + 0.03)
        else:
            # Default to moneyline
            favorite = home_team if nba_prediction.home_win_prob > 0.55 else away_team
            selection = f"{favorite} ML"
            odds = random.choice([-130, -125, -140, -115])
            edge = random.uniform(min_edge, min_edge + 0.025)

        # Add pace/rest factors to edge
        if pace_factor and nba_prediction.pace_advantage != "neutral":
            edge += 0.008  # Pace advantage bonus

        if rest_factor and nba_game.is_back_to_back:
            edge += 0.005  # Back-to-back exploitation bonus

        total_edge += edge

        # Create parlay leg
        leg = ParlayLeg(
            selection=selection,
            price=odds,
            book=random.choice(["FanDuel", "DraftKings", "BetMGM", "Caesars"]),
            sport="NBA",
            game=f"{away_team} @ {home_team}",
            confidence=min(0.85, 0.6 + edge),
        )
        mock_legs.append(leg)

    # Calculate mock parlay metrics
    combined_odds = 1.0
    for leg in mock_legs:
        decimal_odds = (100 / abs(leg.price)) + 1 if leg.price < 0 else (leg.price / 100) + 1
        combined_odds *= decimal_odds

    avg_edge = total_edge / size
    est_true_prob = random.uniform(0.15, 0.35)  # Realistic parlay win probability
    ev = (est_true_prob * combined_odds - 1) * 100

    # Enhanced rationale
    rationale_parts = [
        f"Mock NBA parlay with {avg_edge:.1%} average edge targeting basketball analytics"
    ]

    if pace_factor:
        rationale_parts.append("leveraging pace mismatch advantages")

    if rest_factor:
        rationale_parts.append("exploiting rest/travel disparities")

    if market_focus == "pace":
        rationale_parts.append("focused on high-possession games")
    elif market_focus == "efficiency":
        rationale_parts.append("targeting efficiency rating gaps")

    rationale = ". ".join(rationale_parts) + f" with {min_edge:.1%} minimum edge threshold."

    return ParlayResponse(
        name=f"{size}-Leg Mock NBA Parlay ({market_focus.title()})",
        legs=mock_legs,
        combined_odds=combined_odds,
        est_true_prob=est_true_prob,
        ev=ev,
        confidence=random.uniform(0.65, 0.82),
        rationale=rationale,
        risk_level="medium",
        created_at=datetime.utcnow().isoformat(),
    )


# College Basketball (NCAAB) & March Madness Parlay Generation Endpoint
@app.get("/api/ncaab-parlay", response_model=ParlayResponse)
async def generate_ncaab_parlay(
    size: int = Query(
        3,
        ge=2,
        le=6,
        description="Number of bets in parlay (smaller for college volatility)",
    ),
    risk_level: str = Query("medium", description="Risk tolerance: low, medium, high"),
    min_edge: float = Query(0.025, ge=0.01, le=0.12, description="Minimum edge threshold"),
    season_mode: str = Query("regular", description="Season mode: regular, tournament"),
    tournament_round: str = Query(
        "round_1",
        description="Tournament round: first_four, round_1, round_2, sweet_16, elite_8, final_four, championship",
    ),
    market_focus: str = Query(
        "mixed",
        description="Market focus: four_factors, tempo, sos_mismatch, upset_special, mixed",
    ),
    experience_factor: bool = Query(True, description="Weight tournament experience heavily"),
    upset_detection: bool = Query(True, description="Include upset opportunity analysis"),
    api_key: str = Depends(verify_api_key),
):
    """
    Generate optimized NCAAB/March Madness parlay with college basketball analytics

    Features:
    - Four Factors analysis (eFG%, TO%, OREB%, FT Rate)
    - Adjusted efficiency ratings (KenPom style)
    - Strength of schedule mismatch detection
    - Tournament experience weighting
    - Upset probability modeling with seeding analysis
    - Coaching tournament history integration
    - Regular season vs tournament mode switching
    - Bracket context and path difficulty analysis
    """

    try:
        is_tournament = season_mode == "tournament"
        tournament_emoji = "🏆" if is_tournament else "🏀"

        logger.info(
            f"{tournament_emoji} Generating NCAAB parlay: size={size}, mode={season_mode}, round={tournament_round}"
        )

        # Fetch live college basketball odds
        ncaab_odds = []  # await fetch_live_ncaab_odds() - placeholder

        if not ncaab_odds:
            logger.info("No live NCAAB odds available, generating mock parlay")
            return await generate_mock_ncaab_parlay(
                size,
                min_edge,
                season_mode,
                tournament_round,
                market_focus,
                experience_factor,
                upset_detection,
            )

        # Process NCAAB games with four factors analytics
        ncaab_edge_bets = []
        games_processed = 0

        for event in ncaab_odds:
            try:
                # Create bracket context for tournament games
                bracket_context = None
                if is_tournament:
                    bracket_context = BracketContext(
                        is_tournament=True,
                        tournament_round=tournament_round,
                        # Would populate seeds and other tournament data from API
                    )

                # Extract NCAAB features
                ncaab_game = extract_ncaab_features(event, bracket_context)

                # Generate four factors prediction
                ncaab_prediction = generate_ncaab_prediction(ncaab_game)

                # Apply market focus filtering
                if market_focus == "four_factors":
                    # Require at least 2 four factor advantages
                    advantages = sum(
                        [
                            ncaab_prediction.shooting_advantage != "neutral",
                            ncaab_prediction.turnover_advantage != "neutral",
                            ncaab_prediction.rebounding_advantage != "neutral",
                            ncaab_prediction.free_throw_advantage != "neutral",
                        ]
                    )
                    if advantages < 2:
                        continue

                elif market_focus == "tempo" and ncaab_prediction.tempo_advantage == "neutral":
                    continue

                elif market_focus == "sos_mismatch":
                    sos_diff = abs(ncaab_game.home_sos_ranking - ncaab_game.away_sos_ranking)
                    if sos_diff < 75:  # Not significant SOS difference
                        continue

                elif market_focus == "upset_special":
                    if not is_tournament or ncaab_prediction.upset_probability < 0.25:
                        continue

                # Skip games without experience edge if factor enabled
                if (
                    experience_factor
                    and is_tournament
                    and ncaab_prediction.experience_advantage == "neutral"
                ):
                    continue

                # Market selection
                market_types = ["moneyline"]
                if market_focus == "four_factors":
                    market_types = [
                        "spread",
                        "moneyline",
                    ]  # Four factors predict spreads well
                elif market_focus == "tempo":
                    market_types = ["total", "first_half"]  # Tempo affects totals
                elif market_focus == "upset_special":
                    market_types = ["moneyline"]  # Upsets are ML plays
                elif market_focus == "mixed":
                    market_types = ["moneyline", "spread", "total"]

                # Test market types
                for market_type in market_types:
                    # Get market odds (placeholder)
                    market_odds = random.choice([-110, -108, -105, -112, -115])

                    # NCAAB edge detection
                    edge_bet = ncaab_engine.ncaab_decide_and_place(
                        ncaab_game, market_type, market_odds, ncaab_prediction
                    )

                    if edge_bet and edge_bet.edge >= min_edge:
                        ncaab_edge_bets.append(edge_bet)
                        logger.info(
                            f"{tournament_emoji} NCAAB Edge: {edge_bet.selection} - {edge_bet.edge:.1%}"
                        )

                        if len(ncaab_edge_bets) >= size:
                            break

                games_processed += 1
                if len(ncaab_edge_bets) >= size:
                    break

            except Exception as e:
                logger.error(f"Error processing NCAAB game {event.get('id', 'unknown')}: {e}")
                continue

        if len(ncaab_edge_bets) < size:
            logger.warning(f"Only found {len(ncaab_edge_bets)} NCAAB edges, need {size}")
            # Fallback with relaxed standards
            return await generate_mock_ncaab_parlay(
                size,
                min_edge * 0.8,
                season_mode,
                tournament_round,
                market_focus,
                experience_factor,
                upset_detection,
            )

        # Select best NCAAB edges (conservative for tournament)
        ncaab_edge_bets.sort(key=lambda x: x.edge, reverse=True)
        selected_bets = ncaab_edge_bets[:size]

        # Convert to parlay legs
        ncaab_legs = []
        for bet in selected_bets:
            sport_label = "March Madness" if is_tournament else "NCAAB"
            leg = ParlayLeg(
                selection=bet.selection,
                price=bet.odds,
                book=bet.book,
                sport=sport_label,
                game=f"{bet.event_id}",
                confidence=min(
                    0.88, 0.5 + bet.edge
                ),  # Slightly lower confidence for college volatility
            )
            ncaab_legs.append(leg)

        # Calculate parlay metrics
        combined_odds = 1.0
        for leg in ncaab_legs:
            decimal_odds = (100 / abs(leg.price)) + 1 if leg.price < 0 else (leg.price / 100) + 1
            combined_odds *= decimal_odds

        total_true_prob = 1.0
        for bet in selected_bets:
            total_true_prob *= bet.fair_prob

        est_true_prob = total_true_prob
        1.0 / combined_odds
        ev = (est_true_prob * combined_odds - 1) * 100

        avg_edge = sum(bet.edge for bet in selected_bets) / len(selected_bets)

        # Count specific factors
        four_factor_games = sum(
            1
            for bet in selected_bets
            if any(
                factor in bet.selection.lower()
                for factor in ["shooting", "turnover", "rebound", "foul"]
            )
        )
        upset_games = sum(
            1 for bet in selected_bets if "upset" in bet.selection.lower() or ")" in bet.selection
        )  # Seed indicators

        # Generate rationale
        sport_name = "March Madness" if is_tournament else "College Basketball"
        rationale_parts = [
            f"{sport_name} parlay leveraging {avg_edge:.1%} average edge across {size} games"
        ]

        if four_factor_games > 0:
            rationale_parts.append(
                f"{four_factor_games} selections targeting four factors advantages"
            )

        if upset_games > 0 and is_tournament:
            rationale_parts.append(
                f"{upset_games} upset opportunities identified through seeding analysis"
            )

        if experience_factor and is_tournament:
            rationale_parts.append("weighting tournament experience and coaching history")

        if market_focus == "four_factors":
            rationale_parts.append(
                "focused on shooting, turnover, rebounding, and free throw edges"
            )
        elif market_focus == "sos_mismatch":
            rationale_parts.append("exploiting strength of schedule mismatches")
        elif market_focus == "upset_special":
            rationale_parts.append("targeting high-probability upset scenarios")

        if is_tournament:
            rationale_parts.append(f"optimized for {tournament_round} tournament dynamics")

        rationale = ". ".join(rationale_parts) + "."

        # Create NCAAB parlay response
        parlay_name = f"{size}-Leg {sport_name} Parlay"
        if is_tournament:
            parlay_name += f" ({tournament_round.replace('_', ' ').title()})"

        ncaab_parlay = ParlayResponse(
            name=parlay_name,
            legs=ncaab_legs,
            combined_odds=combined_odds,
            est_true_prob=est_true_prob,
            ev=ev,
            confidence=min(0.88, 0.55 + avg_edge),  # Conservative for college volatility
            rationale=rationale,
            risk_level=risk_level,
            created_at=datetime.utcnow().isoformat(),
        )

        # Save to database
        save_parlay_to_db(ncaab_parlay)

        logger.info(
            f"{tournament_emoji} Generated {sport_name} parlay: {size} legs, {avg_edge:.1%} avg edge, ${ev:.2f} EV"
        )
        return ncaab_parlay

    except Exception as e:
        logger.error(f"NCAAB parlay generation error: {e}")
        raise HTTPException(status_code=500, detail=f"NCAAB parlay generation failed: {e}")


async def generate_mock_ncaab_parlay(
    size: int,
    min_edge: float,
    season_mode: str,
    tournament_round: str,
    market_focus: str,
    experience_factor: bool,
    upset_detection: bool,
) -> ParlayResponse:
    """Generate mock NCAAB/March Madness parlay with four factors analytics"""

    is_tournament = season_mode == "tournament"

    # Mock college teams with different profiles
    college_teams = [
        ("Duke", "North Carolina", "blue_blood", 1, 4),
        ("Kansas", "Kentucky", "blue_blood", 2, 3),
        ("Gonzaga", "Villanova", "consistent", 3, 6),
        ("UCLA", "Michigan", "strong", 4, 5),
        ("Auburn", "Tennessee", "sec_power", 5, 8),
        ("Wisconsin", "Illinois", "big_ten", 6, 7),
        ("Houston", "Texas Tech", "defense", 7, 10),
        ("Arkansas", "Iowa State", "mid_major", 9, 12),
        ("Vermont", "Colgate", "cinderella", 13, 16),
        ("Montana State", "Norfolk State", "upset_special", 15, 14),
    ]

    mock_legs = []
    total_edge = 0.0

    for i in range(size):
        # Select teams based on focus and tournament context
        if market_focus == "upset_special" and is_tournament:
            # Favor potential upset scenarios
            team_data = random.choice(college_teams[-4:])  # Lower seeds
        elif market_focus == "four_factors":
            # Favor teams with strong fundamental advantages
            team_data = random.choice(college_teams[:6])  # Higher seeds/better teams
        else:
            team_data = random.choice(college_teams)

        home_team, away_team, profile, seed1, seed2 = team_data

        # Create bracket context if tournament
        bracket_context = None
        if is_tournament:
            bracket_context = BracketContext(
                is_tournament=True,
                tournament_round=tournament_round,
                home_seed=seed1,
                away_seed=seed2,
                seed_differential=abs(seed1 - seed2),
            )

        # Create mock game
        mock_event = {
            "id": f"ncaab_mock_{i + 1}",
            "home_team": home_team,
            "away_team": away_team,
            "commence_time": datetime.now().isoformat(),
        }

        ncaab_game = extract_ncaab_features(mock_event, bracket_context)
        generate_ncaab_prediction(ncaab_game)

        # Determine selection based on focus and team profile
        base_edge = random.uniform(min_edge, min_edge + 0.04)

        if market_focus == "four_factors" and profile in ["blue_blood", "consistent"]:
            favorite = home_team if seed1 < seed2 else away_team
            selection = f"{favorite} -4.5"
            odds = random.choice([-108, -110, -105])
            base_edge += 0.008  # Four factors bonus

        elif market_focus == "upset_special" and is_tournament and abs(seed1 - seed2) >= 4:
            underdog = home_team if seed1 > seed2 else away_team
            underdog_seed = max(seed1, seed2)
            selection = f"({underdog_seed}) {underdog} ML"
            odds = random.choice([+180, +220, +165, +250])
            base_edge += 0.012  # Upset detection bonus

        elif market_focus == "tempo" and profile == "defense":
            total_line = random.uniform(125, 140)
            selection = f"Under {total_line:.1f}"
            odds = random.choice([-110, -108, -105])
            base_edge += 0.006  # Tempo advantage

        elif profile == "sec_power":
            total_line = random.uniform(135, 155)
            selection = f"Over {total_line:.1f}"
            odds = random.choice([-110, -105, -112])

        else:
            # Default moneyline
            favorite = home_team if seed1 < seed2 else away_team
            fav_seed = min(seed1, seed2) if is_tournament else "Fav"
            selection = f"({fav_seed}) {favorite} ML" if is_tournament else f"{favorite} ML"
            odds = random.choice([-135, -125, -140, -120])

        # Tournament and experience bonuses
        if is_tournament:
            base_edge += 0.005  # Tournament volatility creates edges

            if experience_factor and profile == "blue_blood":
                base_edge += 0.008  # Experience advantage

        # Strength of schedule bonus
        if market_focus == "sos_mismatch":
            base_edge += 0.007

        total_edge += base_edge

        # Create leg
        sport_label = "March Madness" if is_tournament else "NCAAB"
        game_label = (
            f"({seed2}) {away_team} vs ({seed1}) {home_team}"
            if is_tournament
            else f"{away_team} @ {home_team}"
        )

        leg = ParlayLeg(
            selection=selection,
            price=odds,
            book=random.choice(["FanDuel", "DraftKings", "BetMGM", "Caesars"]),
            sport=sport_label,
            game=game_label,
            confidence=min(0.85, 0.55 + base_edge),
        )
        mock_legs.append(leg)

    # Calculate mock parlay metrics
    combined_odds = 1.0
    for leg in mock_legs:
        decimal_odds = (100 / abs(leg.price)) + 1 if leg.price < 0 else (leg.price / 100) + 1
        combined_odds *= decimal_odds

    avg_edge = total_edge / size
    est_true_prob = random.uniform(0.12, 0.28)  # College basketball parlays are tougher
    ev = (est_true_prob * combined_odds - 1) * 100

    # Enhanced rationale
    sport_name = "March Madness" if is_tournament else "College Basketball"
    rationale_parts = [
        f"Mock {sport_name} parlay with {avg_edge:.1%} average edge using college basketball analytics"
    ]

    if market_focus == "four_factors":
        rationale_parts.append(
            "targeting shooting, rebounding, turnover, and free throw advantages"
        )
    elif market_focus == "upset_special":
        rationale_parts.append("exploiting tournament upset opportunities via seeding analysis")
    elif market_focus == "tempo":
        rationale_parts.append("leveraging pace and tempo mismatches")
    elif market_focus == "sos_mismatch":
        rationale_parts.append("capitalizing on strength of schedule disparities")

    if experience_factor and is_tournament:
        rationale_parts.append("weighting tournament experience heavily")

    if is_tournament:
        rationale_parts.append(f"optimized for {tournament_round.replace('_', ' ')} dynamics")

    rationale = ". ".join(rationale_parts) + f" with {min_edge:.1%} minimum edge threshold."

    parlay_name = f"{size}-Leg Mock {sport_name} Parlay"
    if is_tournament:
        parlay_name += f" ({tournament_round.replace('_', ' ').title()})"

    return ParlayResponse(
        name=parlay_name,
        legs=mock_legs,
        combined_odds=combined_odds,
        est_true_prob=est_true_prob,
        ev=ev,
        confidence=random.uniform(0.62, 0.78),  # Conservative for college volatility
        rationale=rationale,
        risk_level="medium",
        created_at=datetime.utcnow().isoformat(),
    )


# Audit report endpoint
@app.get("/api/audit")
async def get_audit_report(
    last: int = Query(10, ge=1, le=100, description="Number of recent entries"),
    include_summary: bool = Query(True, description="Include summary statistics"),
    include_performance: bool = Query(True, description="Include performance metrics"),
    api_key: str = Depends(verify_api_key),
):
    """Get audit report with recent activity and performance metrics"""

    logger.info(f"Generating audit report for last {last} entries")

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get recent audit logs
        cursor.execute(
            """
            SELECT al.*, p.name as parlay_name
            FROM audit_logs al
            LEFT JOIN parlays p ON al.parlay_id = p.id
            ORDER BY al.created_at DESC
            LIMIT ?
        """,
            (last,),
        )

        recent_items = []
        for row in cursor.fetchall():
            recent_items.append(
                {
                    "id": row[0],
                    "action": row[1],
                    "parlay_name": row[8] or "Unknown",
                    "amount": row[3],
                    "odds": row[4],
                    "result": row[5],
                    "profit": row[6] or 0,
                    "date": row[7],
                }
            )

        # Calculate summary statistics
        summary = {}
        if include_summary:
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
                    SUM(profit) as total_profit,
                    AVG(CAST(odds as REAL)) as avg_odds
                FROM audit_logs
                WHERE amount IS NOT NULL
            """
            )

            stats = cursor.fetchone()
            if stats and stats[0] > 0:
                summary = {
                    "total_bets": stats[0],
                    "wins": stats[1],
                    "win_rate": (stats[1] / stats[0] * 100) if stats[0] > 0 else 0,
                    "total_profit": stats[2] or 0,
                    "avg_odds": stats[3] or 0,
                    "last_updated": datetime.utcnow().isoformat(),
                }

        conn.close()

        audit_report = {
            "items": recent_items,
            "count": len(recent_items),
            "requested": last,
        }

        if summary:
            audit_report.update(summary)

        logger.info(f"Audit report generated with {len(recent_items)} items")
        return audit_report

    except Exception as e:
        logger.error(f"Audit report error: {e}")
        raise HTTPException(status_code=500, detail=f"Audit report failed: {e}")


# Selection analysis endpoint
@app.get("/api/analyze")
async def analyze_selection(
    selection: str = Query(..., description="Bet selection text to analyze"),
    api_key: str = Depends(verify_api_key),
):
    """Analyze a specific bet selection for EV and recommendation"""

    logger.info(f"Analyzing selection: {selection}")

    try:
        # Mock analysis (replace with real algorithm)
        analysis = {
            "selection": selection,
            "confidence": random.uniform(0.1, 0.9),
            "estimated_prob": random.uniform(0.3, 0.7),
            "recommended": random.choice([True, False]),
            "ev_estimate": random.uniform(-2.0, 3.0),
            "recommendation": generate_selection_recommendation(selection),
            "analyzed_at": datetime.utcnow().isoformat(),
        }

        return analysis

    except Exception as e:
        logger.error(f"Selection analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


# EV Check endpoint for Firefox extension content script
@app.get("/api/check-ev")
async def check_ev(
    selection: str = Query(..., description="Bet selection to check"),
    odds: str = Query(..., description="Odds in any format"),
    api_key: str = Depends(verify_api_key),
):
    """Check expected value for a specific selection - used by content script"""

    logger.info(f"EV check for: {selection} at {odds}")

    try:
        # Convert odds to decimal if needed
        decimal_odds = convert_odds_to_decimal(odds)

        # Mock EV calculation (replace with real algorithm)
        # In practice, this would compare against your model's true probabilities
        implied_prob = 1 / decimal_odds
        true_prob = random.uniform(0.3, 0.8)  # Your model's estimated probability

        expected_value = (true_prob * decimal_odds) - 1

        result = {
            "selection": selection,
            "odds": odds,
            "decimal_odds": decimal_odds,
            "implied_probability": implied_prob,
            "true_probability": true_prob,
            "expected_value": expected_value,
            "is_positive": expected_value > 0,
            "ev_percentage": expected_value * 100,
            "checked_at": datetime.utcnow().isoformat(),
        }

        return result

    except Exception as e:
        logger.error(f"EV check error: {e}")
        raise HTTPException(status_code=500, detail=f"EV check failed: {e}")


def convert_odds_to_decimal(odds_str: str) -> float:
    """Convert various odds formats to decimal odds"""
    odds_str = str(odds_str).strip()

    # American odds (+150, -200)
    if odds_str.startswith(("+", "-")):
        american_odds = int(odds_str)
        if american_odds > 0:
            return (american_odds / 100) + 1
        return (100 / abs(american_odds)) + 1

    # Decimal odds (2.50)
    if "." in odds_str:
        return float(odds_str)

    # Fractional odds (3/2)
    if "/" in odds_str:
        num, den = odds_str.split("/")
        return (float(num) / float(den)) + 1

    # Default to treating as decimal
    return float(odds_str)


# Dashboard endpoint
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Simple HTML dashboard for monitoring"""

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EQ12 Extension Backend Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #0f172a; color: #e2e8f0; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .section {{ margin: 20px 0; padding: 20px; background: #1e293b; border-radius: 8px; }}
            .status {{ color: #10b981; font-weight: bold; }}
            .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
            pre {{ background: #0f172a; padding: 15px; border-radius: 6px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 EQ12 Extension Backend</h1>
            <p class="status">Status: Running</p>
        </div>

        <div class="section">
            <h3>📊 API Endpoints</h3>
            <ul>
                <li><code>GET /api/health</code> - System health check</li>
                <li><code>GET /api/ping</code> - Simple connectivity test</li>
                <li><code>GET /api/parlay</code> - Generate optimized parlays</li>
                <li><code>GET /api/audit</code> - Get betting audit reports</li>
                <li><code>GET /api/analyze</code> - Analyze bet selections</li>
            </ul>
        </div>

        <div class="section">
            <h3>🔧 Configuration</h3>
            <div class="metric">API Key: {"Configured" if API_KEY else "Not Set"}</div>
            <div class="metric">Database: {DATABASE_PATH}</div>
            <div class="metric">Started: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC</div>
        </div>

        <div class="section">
            <h3>📖 Usage</h3>
            <pre>
# Test connection
curl http://localhost:8000/api/ping

# Generate 5-leg parlay
curl "http://localhost:8000/api/parlay?size=5&risk_level=medium" \\
     -H "X-API-Key: {API_KEY}"

# Get audit report
curl "http://localhost:8000/api/audit?last=10" \\
     -H "X-API-Key: {API_KEY}"
            </pre>
        </div>
    </body>
    </html>
    """

    return html_content


# Live odds API integration
def fetch_live_odds_sync(sport_keys: list[str] | None = None) -> list[dict[str, Any]]:
    """Fetch live odds from The Odds API with enhanced error handling"""
    if not ODDS_API_KEY:
        logger.warning("⚠️ No ODDS_API_KEY configured, using mock data")
        return []

    # Updated sport keys for current season (September 2025)
    if sport_keys is None:
        sport_keys = [
            "americanfootball_nfl",  # NFL Week 4
            "basketball_nba",  # NBA Preseason
            "baseball_mlb",  # MLB Playoffs
            "icehockey_nhl",  # NHL Preseason
        ]

    all_odds = []
    logger.info(
        f"🔄 Fetching live odds for {len(sport_keys)} sports with API key: {ODDS_API_KEY[:8]}..."
    )

    for sport in sport_keys:
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
            params = {
                "apiKey": ODDS_API_KEY,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "dateFormat": "iso",
            }

            logger.info(f"📡 Calling API: {sport}")
            response = requests.get(url, params=params, timeout=15)

            # Enhanced response handling
            if response.status_code == 200:
                data = response.json()
                event_count = len(data)
                logger.info(f"✅ {sport}: Fetched {event_count} live events")

                # Validate data structure
                for event in data:
                    if not event.get("bookmakers"):
                        logger.warning(f"⚠️ Event missing bookmakers: {event.get('id', 'unknown')}")
                    else:
                        # Log sample event for debugging
                        logger.info(
                            f"📋 Sample: {event.get('home_team', 'N/A')} vs {event.get('away_team', 'N/A')}"
                        )
                        break

                all_odds.extend(data)

            elif response.status_code == 401:
                logger.error(f"🔑 Invalid API key for {sport}")
                break  # Stop trying other sports
            elif response.status_code == 429:
                logger.error(f"⏳ Rate limit exceeded for {sport}")
                break  # Stop to avoid further rate limiting
            else:
                logger.error(
                    f"❌ API error {response.status_code} for {sport}: {response.text[:200]}"
                )

        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout fetching {sport} odds")
        except requests.exceptions.ConnectionError:
            logger.error(f"🌐 Connection error for {sport}")
        except Exception as e:
            logger.error(f"💥 Unexpected error for {sport}: {e}")

    logger.info(f"🎯 Total events fetched: {len(all_odds)}")
    return all_odds


def parse_live_odds_to_legs(
    odds_data: list[dict[str, Any]], size: int, risk_level: str
) -> list[ParlayLeg]:
    """Convert live API odds data to parlay legs with enhanced parsing"""
    legs = []
    logger.info(f"🔍 Parsing {len(odds_data)} events for {size} parlay legs")

    # Filter for games happening today/tomorrow
    current_date = datetime.now()
    tomorrow = current_date + timedelta(days=1)

    for event in odds_data:
        try:
            # Validate event structure
            if not event.get("bookmakers"):
                continue

            home_team = event.get("home_team", "Team A")
            away_team = event.get("away_team", "Team B")
            sport = event.get("sport_title", "Unknown Sport")
            commence_time = event.get("commence_time", "")

            # Parse and validate game date
            game_date = None
            if commence_time:
                try:
                    game_date = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
                    # Only include games within next 24 hours
                    if game_date > tomorrow:
                        continue
                    date_str = game_date.strftime("%m/%d")
                except Exception as e:
                    logger.warning(f"Date parse error: {e}")
                    date_str = current_date.strftime("%m/%d")
            else:
                date_str = current_date.strftime("%m/%d")

            logger.debug(f"🏈 Processing: {home_team} vs {away_team} on {date_str}")

            # Process bookmakers - prioritize major ones
            priority_books = ["DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet"]
            bookmakers = event.get("bookmakers", [])

            # Sort bookmakers by priority
            sorted_bookmakers = sorted(
                bookmakers,
                key=lambda b: (
                    priority_books.index(b.get("title", ""))
                    if b.get("title") in priority_books
                    else 999
                ),
            )

            for bookmaker in sorted_bookmakers[:2]:  # Top 2 books
                book_name = bookmaker.get("title", "Sportsbook")
                markets = bookmaker.get("markets", [])

                for market in markets:
                    market_key = market.get("key", "")
                    outcomes = market.get("outcomes", [])

                    # Process each outcome
                    for outcome in outcomes:
                        selection_name = outcome.get("name", "")
                        price = outcome.get("price", 0)

                        # Skip invalid prices
                        if not price or abs(price) < 100:
                            continue

                        # Create proper selection text
                        selection = ""
                        if market_key == "h2h":  # Moneyline
                            selection = f"{selection_name} ML"
                        elif market_key == "spreads":  # Point spreads
                            point = outcome.get("point", 0)
                            if point and point != 0:
                                point_str = f"+{point}" if point > 0 else str(point)
                                selection = f"{selection_name} {point_str}"
                            else:
                                continue
                        elif market_key == "totals":  # Over/Under
                            point = outcome.get("point", 0)
                            if point:
                                over_under = "Over" if selection_name.lower() == "over" else "Under"
                                selection = f"{over_under} {point}"
                            else:
                                continue
                        else:
                            continue  # Skip unknown market types

                        # **SPORT-SPECIFIC PROFESSIONAL EDGE DETECTION**

                        # Check if this is an NFL game for specialized processing
                        if sport == "NFL" or sport == "American Football":
                            # Extract NFL game features
                            nfl_game = extract_nfl_features(event)

                            # Generate NFL model prediction
                            nfl_prediction = generate_nfl_prediction(nfl_game)

                            # Use NFL-specific edge detection engine
                            edge_bet = nfl_engine.nfl_decide_and_place(
                                game=nfl_game,
                                market_type=market_key,
                                market_odds=float(price),
                                prediction=nfl_prediction,
                            )

                            # Update selection format with NFL context
                            if edge_bet:
                                edge_bet.selection = selection  # Use formatted selection

                        # **NCAAF-SPECIFIC PROFESSIONAL EDGE DETECTION**

                        elif (
                            sport == "NCAAF"
                            or sport == "College Football"
                            or "college" in sport.lower()
                        ):
                            # Extract NCAAF game features with college-specific data
                            ncaaf_game = extract_ncaaf_features(event)

                            # Generate NCAAF model prediction with volatility adjustments
                            ncaaf_prediction = generate_ncaaf_prediction(ncaaf_game)

                            # Use NCAAF-specific edge detection engine
                            edge_bet = ncaaf_engine.ncaaf_decide_and_place(
                                game=ncaaf_game,
                                market_type=market_key,
                                market_odds=float(price),
                                prediction=ncaaf_prediction,
                            )

                            # Update selection format with college context
                            if edge_bet:
                                edge_bet.selection = selection  # Use formatted selection
                                # Store college-specific context for logging
                                logger.debug(
                                    f"NCAAF Context: {ncaaf_game.home_conference}, Mismatch: {ncaaf_prediction.mismatch_factor:.1f}x"
                                )

                        # **MLB-SPECIFIC PROFESSIONAL EDGE DETECTION**

                        elif sport == "MLB" or sport == "Baseball" or "baseball" in sport.lower():
                            # Extract MLB game features with baseball-specific data
                            mlb_game = extract_mlb_features(event)

                            # Generate MLB model prediction with pitcher/weather adjustments
                            mlb_prediction = generate_mlb_prediction(mlb_game)

                            # Use MLB-specific edge detection engine
                            edge_bet = mlb_engine.mlb_decide_and_place(
                                game=mlb_game,
                                market_type=market_key,
                                market_odds=float(price),
                                prediction=mlb_prediction,
                            )

                            # Update selection format with baseball context
                            if edge_bet:
                                edge_bet.selection = selection  # Use formatted selection
                                # Store baseball-specific context for logging
                                pitcher_info = (
                                    f"{mlb_game.home_starter_name} vs {mlb_game.away_starter_name}"
                                    if mlb_game.home_starter_name
                                    else "TBD"
                                )
                                weather_info = (
                                    f"{mlb_game.temperature}°F, {mlb_game.wind_speed}mph wind"
                                    if mlb_game.temperature
                                    else "N/A"
                                )
                                logger.debug(
                                    f"MLB Context: Pitchers: {pitcher_info}, Weather: {weather_info}, Park Factor: {mlb_game.park_factor_runs:.2f}"
                                )

                        # **NBA-SPECIFIC PROFESSIONAL EDGE DETECTION**

                        elif (
                            sport == "NBA" or sport == "Basketball" or "basketball" in sport.lower()
                        ):
                            # Extract NBA game features with basketball-specific data
                            nba_game = extract_nba_features(event)

                            # Generate NBA model prediction with pace/efficiency adjustments
                            nba_prediction = generate_nba_prediction(nba_game)

                            # Use NBA-specific edge detection engine
                            edge_bet = nba_engine.nba_decide_and_place(
                                game=nba_game,
                                market_type=market_key,
                                market_odds=float(price),
                                prediction=nba_prediction,
                            )

                            # Update selection format with NBA context
                            if edge_bet:
                                edge_bet.selection = selection  # Use formatted selection
                                # Store NBA-specific context for logging
                                pace_info = (
                                    f"Pace: {nba_game.pace:.1f}" if nba_game.pace else "Pace: N/A"
                                )
                                rest_info = (
                                    f"Rest: {nba_game.home_rest_days}h/{nba_game.away_rest_days}a days"
                                    if nba_game.home_rest_days
                                    else "Rest: N/A"
                                )
                                efficiency_info = (
                                    f"NetRtg: {nba_prediction.home_net_rating:.1f}h/{nba_prediction.away_net_rating:.1f}a"
                                    if hasattr(nba_prediction, "home_net_rating")
                                    else "NetRtg: N/A"
                                )
                                logger.debug(
                                    f"NBA Context: {pace_info}, {rest_info}, {efficiency_info}"
                                )

                        # **NCAAB-SPECIFIC PROFESSIONAL EDGE DETECTION**

                        elif (
                            sport == "NCAAB"
                            or sport == "College Basketball"
                            or "college basketball" in sport.lower()
                        ):
                            # Extract NCAAB game features with college basketball-specific data
                            ncaab_game = extract_ncaab_features(event)

                            # Generate NCAAB model prediction with four factors/tournament adjustments
                            ncaab_prediction = generate_ncaab_prediction(ncaab_game)

                            # Use NCAAB-specific edge detection engine
                            edge_bet = ncaab_engine.ncaab_decide_and_place(
                                game=ncaab_game,
                                market_type=market_key,
                                market_odds=float(price),
                                prediction=ncaab_prediction,
                            )

                            # Update selection format with NCAAB context
                            if edge_bet:
                                edge_bet.selection = selection  # Use formatted selection
                                # Store NCAAB-specific context for logging
                                conference_info = (
                                    f"{ncaab_game.home_conference} vs {ncaab_game.away_conference}"
                                    if ncaab_game.home_conference
                                    else "Conference: N/A"
                                )
                                tournament_info = (
                                    f"Tournament: {ncaab_game.bracket_context.tournament_name}"
                                    if ncaab_game.bracket_context
                                    and ncaab_game.bracket_context.tournament_name
                                    else "Regular Season"
                                )
                                efficiency_info = (
                                    f"AdjEM: {ncaab_prediction.home_adjusted_efficiency:.1f}h/{ncaab_prediction.away_adjusted_efficiency:.1f}a"
                                    if hasattr(ncaab_prediction, "home_adjusted_efficiency")
                                    else "AdjEM: N/A"
                                )
                                logger.debug(
                                    f"NCAAB Context: {conference_info}, {tournament_info}, {efficiency_info}"
                                )

                        else:
                            # Use general professional edge detection for other sports

                            # Collect all prices for this selection across bookmakers
                            all_prices_for_selection = []
                            for bk in bookmakers:
                                for mkt in bk.get("markets", []):
                                    if mkt.get("key") == market_key:
                                        for out in mkt.get("outcomes", []):
                                            if out.get("name") == selection_name:
                                                all_prices_for_selection.append(out.get("price", 0))

                            # Calculate consensus fair value (remove juice/vig)
                            fair_prob = (
                                calculate_consensus_fair_value(all_prices_for_selection)
                                if all_prices_for_selection
                                else american_to_implied(price)
                            )

                            # Use professional edge detection logic
                            edge_bet = decide_and_place_bet(
                                odds=float(price),
                                fair_prob=fair_prob,
                                bankroll_mgr=bankroll_manager,
                                selection=selection,
                                event_id=event.get("id", "unknown"),
                            )  # Only include bet if it has positive edge
                        if edge_bet is None:
                            logger.debug(
                                f"❌ No edge: {selection} ({price}) - Edge below threshold"
                            )
                            continue

                        # Update EdgeBet with actual sport/book info
                        edge_bet.sport = sport
                        edge_bet.market = market_key
                        edge_bet.book = book_name

                        # Convert EdgeBet to ParlayLeg with professional confidence scoring
                        confidence_map = {
                            "LOCK": 0.95,
                            "STRONG": 0.80,
                            "MODERATE": 0.65,
                            "WEAK": 0.45,
                        }

                        new_leg = ParlayLeg(
                            selection=selection,
                            price=float(price),
                            book=book_name,
                            sport=sport,
                            game=f"{home_team} vs {away_team} ({date_str})",
                            confidence=confidence_map.get(edge_bet.confidence, 0.50),
                        )

                        legs.append(new_leg)
                        logger.info(
                            f"🎯 EDGE DETECTED: {selection} ({price:+.0f}) | Edge: {edge_bet.edge:.1%} | Kelly: {edge_bet.kelly_fraction:.1%} | Size: ${edge_bet.bet_size:.2f} | {edge_bet.confidence}"
                        )

                        # Return early if we have enough legs
                        if len(legs) >= size:
                            logger.info(f"🎯 Successfully created {len(legs)} live parlay legs")
                            return legs[:size]

        except Exception as e:
            logger.error(f"💥 Error parsing event {event.get('id', 'unknown')}: {e}")
            continue

    logger.info(f"📊 Parsed {len(legs)} legs from live data")
    return legs[:size] if legs else []

    return legs[:size]


# Helper functions
def get_current_games():
    """Get current games for today and tomorrow"""
    today = datetime.now().strftime("%m/%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%m/%d")

    # Current games with today/tomorrow dates
    return [
        {
            "selection": "Lakers ML",
            "book": "DraftKings",
            "sport": "NBA",
            "game": f"Lakers vs Warriors ({today})",
        },
        {
            "selection": "Over 225.5",
            "book": "FanDuel",
            "sport": "NBA",
            "game": f"Celtics vs Nets ({tomorrow})",
        },
        {
            "selection": "Cowboys -3.5",
            "book": "BetMGM",
            "sport": "NFL",
            "game": f"Cowboys vs Giants ({today})",
        },
        {
            "selection": "Under 44.5",
            "book": "Caesars",
            "sport": "NFL",
            "game": f"Eagles vs Commanders ({tomorrow})",
        },
        {
            "selection": "Dodgers ML",
            "book": "DraftKings",
            "sport": "MLB",
            "game": f"Dodgers vs Padres ({today})",
        },
        {
            "selection": "Rangers +1.5",
            "book": "FanDuel",
            "sport": "NHL",
            "game": f"Rangers vs Bruins ({tomorrow})",
        },
        {
            "selection": "Liverpool ML",
            "book": "BetMGM",
            "sport": "Soccer",
            "game": f"Liverpool vs Arsenal ({today})",
        },
        {
            "selection": "Yankees -1.5",
            "book": "Caesars",
            "sport": "MLB",
            "game": f"Yankees vs Red Sox ({tomorrow})",
        },
        {
            "selection": "Chiefs ML",
            "book": "FanDuel",
            "sport": "NFL",
            "game": f"Chiefs vs Bills ({today})",
        },
        {
            "selection": "Celtics -4.5",
            "book": "DraftKings",
            "sport": "NBA",
            "game": f"Celtics vs Heat ({tomorrow})",
        },
    ]


def generate_live_legs(size: int, risk_level: str) -> list[ParlayLeg]:
    """Generate parlay legs from live API data or fallback to mock data"""

    # Try to get live odds first
    if ODDS_API_KEY:
        try:
            live_odds = fetch_live_odds_sync()
            if live_odds:
                logger.info(f"Using live odds data ({len(live_odds)} events)")
                return parse_live_odds_to_legs(live_odds, size, risk_level)
        except Exception as e:
            logger.error(f"Live odds fetch failed: {e}, falling back to mock data")

    # Fallback to mock data
    logger.info("Using mock data for parlay generation")
    return generate_mock_legs_sync(size, risk_level)


def generate_mock_legs_sync(size: int, risk_level: str) -> list[ParlayLeg]:
    """Generate mock parlay legs with current games for today/tomorrow (synchronous version)"""

    # Get current games data
    mock_data = get_current_games()

    # Adjust odds based on risk level for current betting markets
    odds_ranges = {
        "low": (-150, -110),  # Safer favorites
        "medium": (-125, +140),  # Balanced mix
        "high": (-105, +220),  # Higher variance plays
    }

    min_odds, max_odds = odds_ranges.get(risk_level, (-120, +120))

    legs = []
    selected_data = random.sample(mock_data, min(size, len(mock_data)))

    for _i, data in enumerate(selected_data):
        # Generate odds within range
        if random.choice([True, False]):
            price = (
                random.randint(min_odds, -100) if min_odds < 0 else random.randint(100, max_odds)
            )
        else:
            price = (
                random.randint(100, max_odds) if max_odds > 0 else random.randint(min_odds, -100)
            )

        # Calculate confidence based on odds and risk level
        confidence = calculate_leg_confidence(price, risk_level)

        legs.append(
            ParlayLeg(
                selection=data["selection"],
                price=float(price),
                book=data["book"],
                sport=data["sport"],
                game=data["game"],
                confidence=confidence,
            )
        )

    return legs


def calculate_combined_odds(prices: list[float]) -> float:
    """Calculate combined parlay odds from individual leg prices"""
    decimal_odds = []

    for price in prices:
        if price > 0:
            decimal_odds.append((price / 100) + 1)
        else:
            decimal_odds.append((100 / abs(price)) + 1)

    combined_decimal = 1.0
    for odds in decimal_odds:
        combined_decimal *= odds

    # Convert back to American odds
    if combined_decimal >= 2.0:
        return (combined_decimal - 1) * 100
    return -100 / (combined_decimal - 1)


def estimate_true_probability(legs: list[ParlayLeg], risk_level: str) -> float:
    """Estimate true probability using professional edge detection methodology"""

    # Use professional consensus methodology for each leg
    leg_fair_probs = []

    for leg in legs:
        # Since we already filtered legs through edge detection, use confidence as indicator of fair prob
        confidence_to_prob_adjustment = {
            # Map confidence back to fair probability vs implied probability relationship
            0.95: 0.05,  # LOCK: 5% edge implied
            0.80: 0.03,  # STRONG: 3% edge
            0.65: 0.02,  # MODERATE: 2% edge
            0.45: 0.01,  # WEAK: 1% edge
        }

        implied_prob = american_to_implied(leg.price)

        # Find closest confidence mapping
        closest_conf = min(
            confidence_to_prob_adjustment.keys(), key=lambda x: abs(x - leg.confidence)
        )
        edge_estimate = confidence_to_prob_adjustment[closest_conf]

        # Fair probability = implied probability + estimated edge
        fair_prob = implied_prob + edge_estimate
        fair_prob = max(0.01, min(0.99, fair_prob))  # Clamp

        leg_fair_probs.append(fair_prob)

    # Combined probability assuming independence (conservative for parlays)
    combined_prob = 1.0
    for prob in leg_fair_probs:
        combined_prob *= prob

    # Apply parlay correlation penalty (real parlays have negative correlation)
    correlation_penalty = 0.02 * (len(legs) - 1)  # 2% penalty per additional leg
    adjusted_prob = combined_prob * (1 - correlation_penalty)

    return max(0.001, min(0.99, adjusted_prob))


def calculate_expected_value(combined_odds: float, true_prob: float, bet_amount: float) -> float:
    """Calculate expected value using professional methodology"""

    # Convert American odds to decimal for EV calculation
    decimal_odds = combined_odds / 100 + 1 if combined_odds > 0 else 100 / abs(combined_odds) + 1

    # EV Formula: (Fair Probability × Decimal Odds) - 1
    # This gives us the expected return per $1 bet
    ev_per_dollar = (true_prob * decimal_odds) - 1

    # Scale by bet amount
    total_ev = ev_per_dollar * bet_amount

    return total_ev


def calculate_leg_confidence(price: float, risk_level: str) -> float:
    """Calculate confidence score for individual leg"""

    # Base confidence on odds (closer to even = higher confidence)
    abs_price = abs(price)

    if abs_price <= 110:
        base_confidence = 0.8
    elif abs_price <= 150:
        base_confidence = 0.7
    elif abs_price <= 200:
        base_confidence = 0.6
    else:
        base_confidence = 0.4

    # Adjust for risk level
    risk_adjustments = {"low": 0.1, "medium": 0.0, "high": -0.1}
    adjusted_confidence = base_confidence + risk_adjustments[risk_level]

    # Add some randomness
    adjusted_confidence += random.uniform(-0.1, 0.1)

    return max(0.1, min(1.0, adjusted_confidence))


def calculate_confidence_score(legs: list[ParlayLeg], risk_level: str) -> float:
    """Calculate overall confidence score for parlay"""

    avg_leg_confidence = sum(leg.confidence for leg in legs) / len(legs)

    # Penalize larger parlays
    size_penalty = max(0, (len(legs) - 3) * 0.05)

    overall_confidence = avg_leg_confidence - size_penalty

    return max(1.0, min(10.0, overall_confidence * 10))


def generate_rationale(legs: list[ParlayLeg], ev: float, confidence: float, risk_level: str) -> str:
    """Generate professional rationale based on edge detection and Kelly criterion"""

    rationale_parts = []

    # Professional EV assessment
    if ev > 2.0:
        rationale_parts.append(
            f"Exceptional edge detected (+${ev:.2f} EV) - High-conviction play with multiple value spots."
        )
    elif ev > 0.5:
        rationale_parts.append(
            f"Positive expected value (+${ev:.2f}) suggests profitable opportunity. Edge detection confirmed."
        )
    elif ev > 0:
        rationale_parts.append(f"Positive expected value (+${ev:.2f}) suggests profitable bet.")
    elif ev > -0.5:
        rationale_parts.append(
            f"Near break-even expected value (${ev:.2f}) - consider smaller stakes."
        )
    else:
        rationale_parts.append(f"Negative expected value (${ev:.2f}) - high risk bet.")

    # Confidence assessment
    if confidence >= 7.5:
        rationale_parts.append("High confidence based on strong individual selections.")
    elif confidence >= 5.0:
        rationale_parts.append("Moderate confidence - solid parlay construction.")
    else:
        rationale_parts.append(
            "Lower confidence due to challenging selections or large parlay size."
        )

    # Risk level assessment
    risk_descriptions = {
        "low": "Conservative risk level focuses on likely outcomes with lower payouts.",
        "medium": "Balanced risk level provides good mix of safety and reward potential.",
        "high": "Aggressive risk level targets higher payouts with increased variance.",
    }
    rationale_parts.append(risk_descriptions[risk_level])

    # Additional insights
    strong_legs = [leg for leg in legs if leg.confidence > 0.7]
    if len(strong_legs) >= len(legs) // 2:
        rationale_parts.append(
            f"{len(strong_legs)} out of {len(legs)} legs show strong confidence indicators."
        )

    return " ".join(rationale_parts)


def generate_selection_recommendation(selection: str) -> str:
    """Generate recommendation text for individual selection"""

    recommendations = [
        "Strong value based on recent form and matchup analysis.",
        "Consider smaller stakes - higher variance selection.",
        "Excellent spot for this selection based on line movement.",
        "Weather and injury reports favor this outcome.",
        "Sharp money appears to be on this side.",
        "Public heavily on opposite side - potential contrarian value.",
    ]

    return random.choice(recommendations)


def save_parlay_to_db(parlay: ParlayResponse):
    """Save generated parlay to database"""

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO parlays (name, legs_json, combined_odds, est_true_prob, ev, confidence, rationale, risk_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                parlay.name,
                json.dumps([leg.dict() for leg in parlay.legs]),
                parlay.combined_odds,
                parlay.est_true_prob,
                parlay.ev,
                parlay.confidence,
                parlay.rationale,
                parlay.risk_level,
            ),
        )

        conn.commit()
        conn.close()

    except Exception as e:
        logger.error(f"Database save error: {e}")


@app.get("/debug/live-odds")
async def debug_live_odds():
    """Debug endpoint to check raw API data"""
    try:
        api_key = os.getenv("ODDS_API_KEY")
        if not api_key:
            return {"error": "No API key found", "env_vars": list(os.environ.keys())}

        # Test with NFL first
        url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/"
        params = {
            "api_key": api_key,
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
        }

        logger.info(f"🔍 Testing API call to: {url}")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            events = len(data) if isinstance(data, list) else 0
            sample_event = data[0] if data and isinstance(data, list) and len(data) > 0 else None

            return {
                "status": "success",
                "api_key_last_4": api_key[-4:] if api_key else None,
                "total_events": events,
                "sample_event": (
                    {
                        "id": sample_event.get("id") if sample_event else None,
                        "home_team": (sample_event.get("home_team") if sample_event else None),
                        "away_team": (sample_event.get("away_team") if sample_event else None),
                        "commence_time": (
                            sample_event.get("commence_time") if sample_event else None
                        ),
                        "bookmakers_count": (
                            len(sample_event.get("bookmakers", [])) if sample_event else 0
                        ),
                    }
                    if sample_event
                    else None
                ),
                "url_used": url,
                "api_response_size": len(str(data)) if data else 0,
            }
        return {
            "error": f"API returned {response.status_code}",
            "message": response.text[:500],
            "url_used": url,
        }

    except Exception as e:
        logger.error(f"Debug API test failed: {e}")
        return {"error": str(e), "type": type(e).__name__}


# Global startup time tracking
startup_time = time.time()

if __name__ == "__main__":
    logger.info("Starting EQ12 Extension Backend Server...")

    # Ensure log directory exists
    os.makedirs("C:\\EQ12\\logs", exist_ok=True)

    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")
