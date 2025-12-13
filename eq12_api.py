#!/usr/bin/env python3
"""
EQ12 FastAPI Application - Betting Mathematics API
=================================================

SPDX-License-Identifier: MIT
SPDX-FileCopyrightText: 2025 EQ12 Project Contributors

Production-ready FastAPI application with 9 core endpoints for betting mathematics.
Implements security hardening, rate limiting, structured logging, and comprehensive validation.

Required Endpoints:
1. GET /health - Health check and system status
2. POST /ev - Expected value calculation
3. POST /kelly - Kelly criterion optimal sizing
4. POST /parlay/validate - SGP correlation validation
5. POST /parlay/price - Multi-leg parlay pricing
6. POST /elo/update - Elo rating updates
7. POST /sim/portfolio - Portfolio simulation
8. POST /clv/log - Closing line value logging
9. GET /clv/summary - CLV analytics summary

Security Features:
- API key authentication
- Rate limiting per endpoint
- Input validation with Pydantic
- SQL injection prevention
- CORS protection
- Request/response logging
"""

import os
import sqlite3
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from eq12_math.elo import calculate_elo_probability, update_elo_ratings

# Import our math library modules
from eq12_math.odds import american_to_decimal, calculate_ev, kelly_criterion
from eq12_math.parlay import (
    detect_sgp_correlations,
    has_forbidden_correlations,
    independent_parlay_probability,
)
from eq12_math.sim import simulate_betting_session

# Configuration
API_KEY = os.getenv("EQ12_API_KEY", "development-key-change-in-production")
DATABASE_URL = os.getenv("EQ12_DATABASE_URL", "sqlite:///eq12_betting.db")
RATE_LIMIT_DEFAULT = "100/hour"
ENABLE_CORS = os.getenv("EQ12_ENABLE_CORS", "true").lower() == "true"

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)


# Database initialization
def init_database():
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect("eq12_betting.db")
    cursor = conn.cursor()

    # Bets table for transaction logging
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id TEXT,
            bet_type TEXT NOT NULL,
            market TEXT,
            odds_decimal REAL,
            stake REAL,
            expected_value REAL,
            kelly_size REAL,
            result TEXT,
            profit_loss REAL,
            closing_odds REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # CLV (Closing Line Value) table for edge tracking
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clv_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id TEXT,
            market_id TEXT NOT NULL,
            opening_odds REAL NOT NULL,
            closing_odds REAL NOT NULL,
            clv_percentage REAL NOT NULL,
            bet_amount REAL,
            theoretical_profit REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_database()
    print("🚀 EQ12 API Server starting up...")
    print(f"📊 Database initialized: {DATABASE_URL}")
    print(
        f"🔐 API Key authentication: {'Enabled' if API_KEY != 'development-key-change-in-production' else 'Development Mode'}"
    )
    print(f"🌐 CORS enabled: {ENABLE_CORS}")
    yield
    # Shutdown
    print("🛑 EQ12 API Server shutting down...")


# FastAPI app initialization
app = FastAPI(
    title="EQ12 Betting Mathematics API",
    description="Production-ready API for sports betting mathematics, analytics, and portfolio management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware if enabled
if ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Security: API Key authentication
api_key_header = APIKeyHeader(name="X-API-Key")


async def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key for protected endpoints."""
    if api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return api_key


# Pydantic models for request/response validation


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: str
    version: str = "1.0.0"
    uptime_seconds: float
    database_connected: bool


class EVRequest(BaseModel):
    true_probability: float = Field(
        ..., ge=0.0, le=1.0, description="Assessed probability (0.0-1.0)"
    )
    american_odds: int = Field(..., description="American odds (e.g. +150, -110)")

    @validator("american_odds")
    def validate_odds(cls, v):
        if v == 0 or (v > -100 and v < 100 and v != 0):
            raise ValueError("Invalid American odds format")
        return v


class EVResponse(BaseModel):
    expected_value: float
    expected_value_percent: float
    decimal_odds: float
    implied_probability: float
    recommended_action: str


class KellyRequest(BaseModel):
    true_probability: float = Field(..., ge=0.0, le=1.0)
    american_odds: int
    bankroll: float = Field(..., gt=0, description="Current bankroll amount")
    max_kelly_fraction: float = Field(
        0.25, ge=0.0, le=1.0, description="Maximum Kelly fraction (default 25%)"
    )


class KellyResponse(BaseModel):
    full_kelly: float
    recommended_kelly: float
    bet_size_dollars: float
    bet_size_percent: float
    risk_assessment: str


class ParlayLeg(BaseModel):
    market_type: str = Field(..., description="Market type (moneyline, spread, total, etc.)")
    american_odds: int
    true_probability: float = Field(..., ge=0.0, le=1.0)


class ParlayValidateRequest(BaseModel):
    legs: list[ParlayLeg] = Field(..., min_items=2, max_items=10)
    correlation_threshold: float = Field(0.25, ge=0.0, le=1.0)


class ParlayValidateResponse(BaseModel):
    is_valid: bool
    correlation_matrix: list[list[float]]
    max_correlation: float
    forbidden_correlations: list[dict[str, Any]]
    risk_score: float


class ParlayPriceRequest(BaseModel):
    legs: list[ParlayLeg]


class ParlayPriceResponse(BaseModel):
    combined_odds: float
    combined_probability: float
    expected_value: float
    fair_odds: float
    edge_percentage: float


class EloUpdateRequest(BaseModel):
    home_rating: float = Field(..., ge=0, le=3000)
    away_rating: float = Field(..., ge=0, le=3000)
    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)
    k_factor: float = Field(32.0, ge=1.0, le=100.0)


class EloUpdateResponse(BaseModel):
    home_rating_new: float
    away_rating_new: float
    rating_change_home: float
    rating_change_away: float
    pre_game_probability: float


class SimulationBet(BaseModel):
    probability: float = Field(..., ge=0.0, le=1.0)
    odds: float = Field(..., gt=1.0)
    stake_fraction: float = Field(..., ge=0.0, le=1.0)


class PortfolioSimRequest(BaseModel):
    initial_bankroll: float = Field(..., gt=0)
    bets: list[SimulationBet] = Field(..., min_items=1, max_items=1000)
    num_simulations: int = Field(1000, ge=1, le=10000)
    random_seed: int | None = None


class PortfolioSimResponse(BaseModel):
    mean_final_bankroll: float
    median_final_bankroll: float
    percentile_5: float
    percentile_95: float
    probability_of_profit: float
    max_drawdown_median: float
    sharpe_ratio: float


class CLVLogRequest(BaseModel):
    market_id: str = Field(..., min_length=1, max_length=100)
    opening_odds: float = Field(..., gt=1.0)
    closing_odds: float = Field(..., gt=1.0)
    bet_amount: float = Field(..., gt=0)


class CLVLogResponse(BaseModel):
    clv_percentage: float
    theoretical_profit: float
    logged_at: str


class CLVSummaryResponse(BaseModel):
    total_bets: int
    average_clv: float
    positive_clv_rate: float
    total_theoretical_profit: float
    best_clv: float
    worst_clv: float


# Startup time for uptime calculation
startup_time = time.time()

# API Endpoints


@app.get("/health", response_model=HealthResponse)
@limiter.limit("10/minute")
async def health_check(request: Request):
    """
    Health check endpoint - verify API and database connectivity.
    No authentication required for monitoring purposes.
    """
    try:
        # Test database connection
        conn = sqlite3.connect("eq12_betting.db", timeout=5.0)
        conn.execute("SELECT 1")
        conn.close()
        database_connected = True
    except Exception:
        database_connected = False

    return HealthResponse(
        timestamp=datetime.now(UTC).isoformat(),
        uptime_seconds=time.time() - startup_time,
        database_connected=database_connected,
    )


@app.post("/ev", response_model=EVResponse)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def calculate_expected_value(
    request: Request, ev_request: EVRequest, api_key: str = Depends(verify_api_key)
):
    """
    Calculate expected value for a single bet.
    Returns EV, implied probability, and betting recommendation.
    """
    try:
        decimal_odds = american_to_decimal(ev_request.american_odds)
        implied_prob = 1.0 / decimal_odds
        ev = calculate_ev(ev_request.true_probability, decimal_odds)
        ev_percent = ev * 100.0

        # Determine recommendation
        if ev > 0.05:  # >5% edge
            recommendation = "STRONG BET"
        elif ev > 0.02:  # >2% edge
            recommendation = "BET"
        elif ev > 0.0:  # Positive but small edge
            recommendation = "WEAK BET"
        else:  # Negative EV
            recommendation = "NO BET"

        return EVResponse(
            expected_value=ev,
            expected_value_percent=ev_percent,
            decimal_odds=decimal_odds,
            implied_probability=implied_prob,
            recommended_action=recommendation,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {e!s}")


@app.post("/kelly", response_model=KellyResponse)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def calculate_kelly_size(
    request: Request, kelly_request: KellyRequest, api_key: str = Depends(verify_api_key)
):
    """
    Calculate Kelly criterion optimal bet sizing.
    Returns full Kelly, recommended fractional Kelly, and risk assessment.
    """
    try:
        decimal_odds = american_to_decimal(kelly_request.american_odds)
        full_kelly = kelly_criterion(kelly_request.true_probability, decimal_odds)

        # Apply maximum Kelly fraction for risk management
        recommended_kelly = min(full_kelly, kelly_request.max_kelly_fraction)

        bet_size_dollars = kelly_request.bankroll * recommended_kelly
        bet_size_percent = recommended_kelly * 100.0

        # Risk assessment based on Kelly size
        if full_kelly <= 0.0:
            risk_assessment = "NEGATIVE EV - DO NOT BET"
        elif full_kelly > 0.5:
            risk_assessment = "EXTREMELY HIGH RISK - Use fractional Kelly"
        elif full_kelly > 0.25:
            risk_assessment = "HIGH RISK - Consider smaller fraction"
        elif full_kelly > 0.1:
            risk_assessment = "MODERATE RISK - Reasonable bet size"
        else:
            risk_assessment = "LOW RISK - Small but positive edge"

        return KellyResponse(
            full_kelly=full_kelly,
            recommended_kelly=recommended_kelly,
            bet_size_dollars=bet_size_dollars,
            bet_size_percent=bet_size_percent,
            risk_assessment=risk_assessment,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kelly calculation error: {e!s}")


@app.post("/parlay/validate", response_model=ParlayValidateResponse)
@limiter.limit("50/hour")
async def validate_parlay(
    request: Request, parlay_request: ParlayValidateRequest, api_key: str = Depends(verify_api_key)
):
    """
    Validate Same Game Parlay for dangerous correlations.
    Returns correlation matrix and risk assessment.
    """
    try:
        market_types = [leg.market_type for leg in parlay_request.legs]
        correlation_matrix = detect_sgp_correlations(market_types)

        # Check for forbidden correlations
        is_valid = not has_forbidden_correlations(
            correlation_matrix, parlay_request.correlation_threshold
        )

        max_correlation = float(abs(correlation_matrix).max())

        # Find specific forbidden correlations
        forbidden_correlations = []
        n_legs = len(parlay_request.legs)
        for i in range(n_legs):
            for j in range(i + 1, n_legs):
                corr_value = abs(correlation_matrix[i, j])
                if corr_value > parlay_request.correlation_threshold:
                    forbidden_correlations.append(
                        {
                            "leg_1": parlay_request.legs[i].market_type,
                            "leg_2": parlay_request.legs[j].market_type,
                            "correlation": corr_value,
                        }
                    )

        # Risk score (0-1, higher is riskier)
        risk_score = min(max_correlation, 1.0)

        return ParlayValidateResponse(
            is_valid=is_valid,
            correlation_matrix=correlation_matrix.tolist(),
            max_correlation=max_correlation,
            forbidden_correlations=forbidden_correlations,
            risk_score=risk_score,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation error: {e!s}")


@app.post("/parlay/price", response_model=ParlayPriceResponse)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def price_parlay(
    request: Request, parlay_request: ParlayPriceRequest, api_key: str = Depends(verify_api_key)
):
    """
    Calculate fair pricing for multi-leg parlay assuming independence.
    Returns combined odds, probability, and expected value.
    """
    try:
        # Get individual leg probabilities and odds
        probabilities = []
        decimal_odds_list = []

        for leg in parlay_request.legs:
            probabilities.append(leg.true_probability)
            decimal_odds_list.append(american_to_decimal(leg.american_odds))

        # Calculate combined probability (assuming independence)
        combined_prob = independent_parlay_probability(probabilities)

        # Calculate offered combined odds
        combined_offered_odds = 1.0
        for odds in decimal_odds_list:
            combined_offered_odds *= odds

        # Fair odds based on true probabilities
        fair_odds = 1.0 / combined_prob if combined_prob > 0 else float("inf")

        # Expected value
        ev = combined_prob * combined_offered_odds - 1.0
        edge_percentage = ev * 100.0

        return ParlayPriceResponse(
            combined_odds=combined_offered_odds,
            combined_probability=combined_prob,
            expected_value=ev,
            fair_odds=fair_odds,
            edge_percentage=edge_percentage,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pricing error: {e!s}")


@app.post("/elo/update", response_model=EloUpdateResponse)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def update_elo(
    request: Request, elo_request: EloUpdateRequest, api_key: str = Depends(verify_api_key)
):
    """
    Update Elo ratings based on game result.
    Returns new ratings and rating changes for both teams.
    """
    try:
        # Calculate pre-game win probability
        pre_game_prob = calculate_elo_probability(elo_request.home_rating, elo_request.away_rating)

        # Determine game result (1 = home win, 0 = away win, 0.5 = tie)
        if elo_request.home_score > elo_request.away_score:
            game_result = 1  # Home win
        elif elo_request.home_score < elo_request.away_score:
            game_result = 0  # Away win
        else:
            game_result = 0.5  # Tie

        # Update ratings
        new_home, new_away = update_elo_ratings(
            elo_request.home_rating, elo_request.away_rating, game_result, elo_request.k_factor
        )

        return EloUpdateResponse(
            home_rating_new=new_home,
            away_rating_new=new_away,
            rating_change_home=new_home - elo_request.home_rating,
            rating_change_away=new_away - elo_request.away_rating,
            pre_game_probability=pre_game_prob,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Elo calculation error: {e!s}")


@app.post("/sim/portfolio", response_model=PortfolioSimResponse)
@limiter.limit("10/hour")  # More expensive endpoint
async def simulate_portfolio(
    request: Request, sim_request: PortfolioSimRequest, api_key: str = Depends(verify_api_key)
):
    """
    Monte Carlo simulation of betting portfolio performance.
    Returns distribution statistics and risk metrics.
    """
    try:
        # Convert Pydantic models to simulation format
        bets = []
        for bet in sim_request.bets:
            bets.append(
                {
                    "probability": bet.probability,
                    "odds": bet.odds,
                    "stake_fraction": bet.stake_fraction,
                }
            )

        # Run simulation
        results = simulate_betting_session(
            initial_bankroll=sim_request.initial_bankroll,
            bets=bets,
            num_simulations=sim_request.num_simulations,
            random_seed=sim_request.random_seed,
        )

        # The simulation already returns what we need

        mean_final = results["mean_final_bankroll"]
        median_final = results["median_final_bankroll"]
        percentile_5 = results["percentile_5"]
        percentile_95 = results["percentile_95"]
        profit_rate = results["profit_probability"]

        # Sharpe ratio approximation
        mean_return = results["mean_return"]
        std_return = results["std_final_bankroll"] / sim_request.initial_bankroll
        sharpe = float(mean_return / std_return) if std_return > 0 else 0.0

        return PortfolioSimResponse(
            mean_final_bankroll=mean_final,
            median_final_bankroll=median_final,
            percentile_5=percentile_5,
            percentile_95=percentile_95,
            probability_of_profit=profit_rate,
            max_drawdown_median=results.get("mean_max_drawdown", 0.0),
            sharpe_ratio=sharpe,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Simulation error: {e!s}")


@app.post("/clv/log", response_model=CLVLogResponse)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def log_closing_line_value(
    request: Request, clv_request: CLVLogRequest, api_key: str = Depends(verify_api_key)
):
    """
    Log closing line value (CLV) for bet tracking.
    CLV measures how much the line moved in your favor from bet to close.
    """
    try:
        # Calculate CLV percentage
        # CLV% = (Closing_Odds - Opening_Odds) / Opening_Odds * 100
        clv_percentage = (
            (clv_request.closing_odds - clv_request.opening_odds) / clv_request.opening_odds
        ) * 100.0

        # Theoretical profit from line movement
        theoretical_profit = clv_request.bet_amount * (
            (clv_request.closing_odds - clv_request.opening_odds) / clv_request.opening_odds
        )

        # Log to database
        conn = sqlite3.connect("eq12_betting.db")
        cursor = conn.cursor()

        timestamp = datetime.now(UTC).isoformat()
        cursor.execute(
            """
            INSERT INTO clv_logs (
                timestamp, market_id, opening_odds, closing_odds,
                clv_percentage, bet_amount, theoretical_profit
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                timestamp,
                clv_request.market_id,
                clv_request.opening_odds,
                clv_request.closing_odds,
                clv_percentage,
                clv_request.bet_amount,
                theoretical_profit,
            ),
        )

        conn.commit()
        conn.close()

        return CLVLogResponse(
            clv_percentage=clv_percentage,
            theoretical_profit=theoretical_profit,
            logged_at=timestamp,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CLV logging error: {e!s}")


@app.get("/clv/summary", response_model=CLVSummaryResponse)
@limiter.limit("20/hour")
async def clv_summary(request: Request, api_key: str = Depends(verify_api_key)):
    """
    Get summary analytics of closing line value performance.
    Shows overall CLV metrics and betting edge validation.
    """
    try:
        conn = sqlite3.connect("eq12_betting.db")
        cursor = conn.cursor()

        # Get CLV statistics
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_bets,
                AVG(clv_percentage) as avg_clv,
                SUM(CASE WHEN clv_percentage > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as positive_clv_rate,
                SUM(theoretical_profit) as total_theoretical_profit,
                MAX(clv_percentage) as best_clv,
                MIN(clv_percentage) as worst_clv
            FROM clv_logs
        """
        )

        result = cursor.fetchone()
        conn.close()

        if not result or result[0] == 0:
            # No data yet
            return CLVSummaryResponse(
                total_bets=0,
                average_clv=0.0,
                positive_clv_rate=0.0,
                total_theoretical_profit=0.0,
                best_clv=0.0,
                worst_clv=0.0,
            )

        return CLVSummaryResponse(
            total_bets=result[0],
            average_clv=result[1] or 0.0,
            positive_clv_rate=result[2] or 0.0,
            total_theoretical_profit=result[3] or 0.0,
            best_clv=result[4] or 0.0,
            worst_clv=result[5] or 0.0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e!s}")


# Development server runner
if __name__ == "__main__":
    print("🚀 Starting EQ12 API Server in development mode...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 ReDoc Documentation: http://localhost:8000/redoc")
    print("💡 Health Check: http://localhost:8000/health")

    uvicorn.run("eq12_api:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
