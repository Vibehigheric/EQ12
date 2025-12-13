#!/usr/bin/env python3
"""
EQ12 NCAA College Football Backend Integration
==============================================

FastAPI endpoints for NCAA CFB Mystery Profit Boost optimization integration.
Extends the main EQ12 backend with CFB-specific analytics, parlay tracking,
and web interface endpoints.

Features:
- CFB parlay analytics and historical tracking
- Real-time optimization results API
- EV analysis and performance metrics
- DraftKings promo compliance monitoring
- Integration with existing EQ12 backend system

Author: EQ12 Development Team
Version: 1.0.0
Updated: 2025-10-03
"""

from eq12_logging_config import setup_eq12_logger
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add EQ12 to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configuration
EQ12_DB_PATH = "C:/EQ12/eq12_bets.db"
EQ12_LOGS_DIR = "C:/EQ12/logs"

# Setup logging
logger = setup_eq12_logger("cfb_backend")


# Pydantic Models
class CFBLegResponse(BaseModel):
    """Response model for CFB parlay leg"""

    game_id: str
    home_team: str
    away_team: str
    selection_team: str
    dk_american: int
    dk_decimal: float
    fair_prob: float
    commence_time: str
    market_type: str = "moneyline"


class CFBParlayResponse(BaseModel):
    """Response model for CFB parlay"""

    id: int | None = None
    promo_date: str
    token_percent: int
    stake: float
    legs_count: int
    combined_decimal: float
    combined_american: int
    p_win: float
    boosted_payout: float
    boosted_profit: float
    ev: float
    legs: list[CFBLegResponse]
    created_at: str
    placed: bool | None = False
    result: str | None = None
    actual_payout: float | None = None


class CFBGameResponse(BaseModel):
    """Response model for CFB game data"""

    id: str
    home_team: str
    away_team: str
    commence_time: str
    is_fbs: bool
    dk_home_odds: int | None = None
    dk_away_odds: int | None = None
    fair_home_prob: float | None = None
    fair_away_prob: float | None = None
    created_at: str
    completed: bool = False
    home_score: int | None = None
    away_score: int | None = None


class CFBOptimizationRequest(BaseModel):
    """Request model for CFB optimization"""

    token_percent: int = 25
    stake: float = 100.0
    promo_date: str = "2025-10-03"
    use_cash: bool = True


class CFBAnalyticsResponse(BaseModel):
    """Response model for CFB analytics"""

    total_parlays: int
    total_ev: float
    avg_ev: float
    win_rate: float
    placed_parlays: int
    pending_parlays: int
    total_stake: float
    total_payout: float
    roi: float
    by_token_percent: dict[str, dict[str, Any]]
    recent_activity: list[dict[str, Any]]


# Database helper functions
def get_cfb_database_connection():
    """Get database connection with CFB tables"""
    try:
        conn = sqlite3.connect(EQ12_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


def ensure_cfb_tables():
    """Ensure CFB tables exist in database"""
    try:
        with get_cfb_database_connection() as conn:
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name IN ('cfb_parlays', 'cfb_legs', 'cfb_games')
            """
            )
            existing_tables = [row[0] for row in cursor.fetchall()]

            if len(existing_tables) < 3:
                logger.warning(
                    "CFB tables missing, please run CFB optimizer to initialize")
                return False

        return True
    except Exception as e:
        logger.error(f"Failed to check CFB tables: {e}")
        return False


# API Endpoints
async def get_cfb_parlays(
    limit: int = Query(50, description="Maximum number of parlays to return"),
    token_percent: int | None = Query(None, description="Filter by boost percentage"),
    promo_date: str | None = Query(None, description="Filter by promo date"),
    placed_only: bool = Query(False, description="Show only placed parlays"),
) -> list[CFBParlayResponse]:
    """
    Get CFB parlays with optional filtering

    Returns list of CFB parlays with their legs and analytics
    """
    if not ensure_cfb_tables():
        raise HTTPException(status_code=503, detail="CFB tables not initialized")

    try:
        with get_cfb_database_connection() as conn:
            cursor = conn.cursor()

            # Build query with filters
            query = "SELECT * FROM cfb_parlays WHERE 1=1"
            params = []

            if token_percent is not None:
                query += " AND token_percent = ?"
                params.append(token_percent)

            if promo_date is not None:
                query += " AND promo_date = ?"
                params.append(promo_date)

            if placed_only:
                query += " AND placed = 1"

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            parlay_rows = cursor.fetchall()

            parlays = []
            for row in parlay_rows:
                # Get legs for this parlay
                cursor.execute(
                    """
                    SELECT * FROM cfb_legs WHERE parlay_id = ? ORDER BY id
                """,
                    (row["id"],),
                )
                leg_rows = cursor.fetchall()

                legs = [
                    CFBLegResponse(
                        game_id=leg["game_id"],
                        home_team=leg["home_team"],
                        away_team=leg["away_team"],
                        selection_team=leg["selection_team"],
                        dk_american=leg["dk_american"],
                        dk_decimal=leg["dk_decimal"],
                        fair_prob=leg["fair_prob"],
                        commence_time=leg["commence_time"],
                        market_type=leg["market_type"],
                    )
                    for leg in leg_rows
                ]

                parlays.append(
                    CFBParlayResponse(
                        id=row["id"],
                        promo_date=row["promo_date"],
                        token_percent=row["token_percent"],
                        stake=row["stake"],
                        legs_count=row["legs_count"],
                        combined_decimal=row["combined_decimal"],
                        combined_american=row["combined_american"],
                        p_win=row["p_win"],
                        boosted_payout=row["boosted_payout"],
                        boosted_profit=row["boosted_profit"],
                        ev=row["ev"],
                        legs=legs,
                        created_at=row["created_at"],
                        placed=bool(row["placed"]),
                        result=row["result"],
                        actual_payout=row["actual_payout"],
                    )
                )

            logger.info(f"Retrieved {len(parlays)} CFB parlays")
            return parlays

    except Exception as e:
        logger.error(f"Failed to get CFB parlays: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve parlays")


async def get_cfb_parlay_by_id(parlay_id: int) -> CFBParlayResponse:
    """Get specific CFB parlay by ID"""
    if not ensure_cfb_tables():
        raise HTTPException(status_code=503, detail="CFB tables not initialized")

    try:
        with get_cfb_database_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM cfb_parlays WHERE id = ?", (parlay_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Parlay not found")

            # Get legs
            cursor.execute(
                "SELECT * FROM cfb_legs WHERE parlay_id = ? ORDER BY id", (parlay_id,))
            leg_rows = cursor.fetchall()

            legs = [
                CFBLegResponse(
                    game_id=leg["game_id"],
                    home_team=leg["home_team"],
                    away_team=leg["away_team"],
                    selection_team=leg["selection_team"],
                    dk_american=leg["dk_american"],
                    dk_decimal=leg["dk_decimal"],
                    fair_prob=leg["fair_prob"],
                    commence_time=leg["commence_time"],
                    market_type=leg["market_type"],
                )
                for leg in leg_rows
            ]

            return CFBParlayResponse(
                id=row["id"],
                promo_date=row["promo_date"],
                token_percent=row["token_percent"],
                stake=row["stake"],
                legs_count=row["legs_count"],
                combined_decimal=row["combined_decimal"],
                combined_american=row["combined_american"],
                p_win=row["p_win"],
                boosted_payout=row["boosted_payout"],
                boosted_profit=row["boosted_profit"],
                ev=row["ev"],
                legs=legs,
                created_at=row["created_at"],
                placed=bool(row["placed"]),
                result=row["result"],
                actual_payout=row["actual_payout"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get CFB parlay {parlay_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve parlay")


async def get_cfb_games(
    limit: int = Query(100, description="Maximum number of games to return"),
    is_fbs: bool | None = Query(None, description="Filter by FBS status"),
    completed: bool | None = Query(None, description="Filter by completion status"),
) -> list[CFBGameResponse]:
    """Get CFB games data"""
    if not ensure_cfb_tables():
        raise HTTPException(status_code=503, detail="CFB tables not initialized")

    try:
        with get_cfb_database_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM cfb_games WHERE 1=1"
            params = []

            if is_fbs is not None:
                query += " AND is_fbs = ?"
                params.append(is_fbs)

            if completed is not None:
                query += " AND completed = ?"
                params.append(completed)

            query += " ORDER BY commence_time DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            games = [
                CFBGameResponse(
                    id=row["id"],
                    home_team=row["home_team"],
                    away_team=row["away_team"],
                    commence_time=row["commence_time"],
                    is_fbs=bool(row["is_fbs"]),
                    dk_home_odds=row["dk_home_odds"],
                    dk_away_odds=row["dk_away_odds"],
                    fair_home_prob=row["fair_home_prob"],
                    fair_away_prob=row["fair_away_prob"],
                    created_at=row["created_at"],
                    completed=bool(row["completed"]),
                    home_score=row["home_score"],
                    away_score=row["away_score"],
                )
                for row in rows
            ]

            logger.info(f"Retrieved {len(games)} CFB games")
            return games

    except Exception as e:
        logger.error(f"Failed to get CFB games: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve games")


async def get_cfb_analytics() -> CFBAnalyticsResponse:
    """Get comprehensive CFB analytics"""
    if not ensure_cfb_tables():
        raise HTTPException(status_code=503, detail="CFB tables not initialized")

    try:
        with get_cfb_database_connection() as conn:
            cursor = conn.cursor()

            # Overall statistics
            cursor.execute(
                """
                SELECT
                    COUNT(*) as total_parlays,
                    SUM(ev) as total_ev,
                    AVG(ev) as avg_ev,
                    SUM(CASE WHEN placed = 1 THEN 1 ELSE 0 END) as placed_parlays,
                    SUM(CASE WHEN placed = 0 THEN 1 ELSE 0 END) as pending_parlays,
                    SUM(stake) as total_stake,
                    SUM(CASE WHEN actual_payout IS NOT NULL THEN actual_payout ELSE 0 END) as total_payout,
                    AVG(CASE WHEN result = 'win' THEN 1.0 ELSE 0.0 END) as win_rate
                FROM cfb_parlays
            """
            )
            row = cursor.fetchone()

            total_parlays = row["total_parlays"] or 0
            total_ev = row["total_ev"] or 0
            avg_ev = row["avg_ev"] or 0
            placed_parlays = row["placed_parlays"] or 0
            pending_parlays = row["pending_parlays"] or 0
            total_stake = row["total_stake"] or 0
            total_payout = row["total_payout"] or 0
            win_rate = row["win_rate"] or 0

            # Calculate ROI
            roi = ((total_payout - total_stake) /
                   total_stake * 100) if total_stake > 0 else 0

            # Analytics by token percentage
            cursor.execute(
                """
                SELECT
                    token_percent,
                    COUNT(*) as count,
                    AVG(ev) as avg_ev,
                    SUM(stake) as total_stake,
                    AVG(CASE WHEN result = 'win' THEN 1.0 ELSE 0.0 END) as win_rate
                FROM cfb_parlays
                GROUP BY token_percent
                ORDER BY token_percent
            """
            )
            token_rows = cursor.fetchall()

            by_token_percent = {}
            for token_row in token_rows:
                by_token_percent[str(token_row["token_percent"])] = {
                    "count": token_row["count"],
                    "avg_ev": token_row["avg_ev"] or 0,
                    "total_stake": token_row["total_stake"] or 0,
                    "win_rate": token_row["win_rate"] or 0,
                }

            # Recent activity (last 10 parlays)
            cursor.execute(
                """
                SELECT
                    id, promo_date, token_percent, ev, legs_count,
                    combined_american, placed, result, created_at
                FROM cfb_parlays
                ORDER BY created_at DESC
                LIMIT 10
            """
            )
            recent_rows = cursor.fetchall()

            recent_activity = [
                {
                    "id": row["id"],
                    "promo_date": row["promo_date"],
                    "token_percent": row["token_percent"],
                    "ev": row["ev"],
                    "legs_count": row["legs_count"],
                    "combined_american": row["combined_american"],
                    "placed": bool(row["placed"]),
                    "result": row["result"],
                    "created_at": row["created_at"],
                }
                for row in recent_rows
            ]

            return CFBAnalyticsResponse(
                total_parlays=total_parlays,
                total_ev=total_ev,
                avg_ev=avg_ev,
                win_rate=win_rate,
                placed_parlays=placed_parlays,
                pending_parlays=pending_parlays,
                total_stake=total_stake,
                total_payout=total_payout,
                roi=roi,
                by_token_percent=by_token_percent,
                recent_activity=recent_activity,
            )

    except Exception as e:
        logger.error(f"Failed to get CFB analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


async def update_cfb_parlay_status(
    parlay_id: int,
    placed: bool = Query(..., description="Whether parlay was placed"),
    result: str | None = Query(None, description="Result (win/loss/push)"),
    actual_payout: float | None = Query(None, description="Actual payout received"),
) -> dict[str, str]:
    """Update CFB parlay status (placed, result, payout)"""
    if not ensure_cfb_tables():
        raise HTTPException(status_code=503, detail="CFB tables not initialized")

    try:
        with get_cfb_database_connection() as conn:
            cursor = conn.cursor()

            # Check if parlay exists
            cursor.execute("SELECT id FROM cfb_parlays WHERE id = ?", (parlay_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Parlay not found")

            # Update parlay status
            cursor.execute(
                """
                UPDATE cfb_parlays
                SET placed = ?, result = ?, actual_payout = ?
                WHERE id = ?
            """,
                (placed, result, actual_payout, parlay_id),
            )

            conn.commit()
            logger.info(
                f"Updated CFB parlay {parlay_id}: placed={placed}, result={result}")

            return {
                "status": "success",
                "message": f"Parlay {parlay_id} updated successfully",
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update CFB parlay {parlay_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update parlay")


def register_cfb_endpoints(app: FastAPI):
    """Register CFB endpoints with the main FastAPI app"""

    @app.get("/api/cfb/parlays", response_model=list[CFBParlayResponse])
    async def api_get_cfb_parlays(
        limit: int = Query(50, description="Maximum number of parlays to return"),
        token_percent: int | None = Query(None, description="Filter by boost percentage"),
        promo_date: str | None = Query(None, description="Filter by promo date"),
        placed_only: bool = Query(False, description="Show only placed parlays"),
    ):
        """Get CFB parlays with filtering options"""
        return await get_cfb_parlays(limit, token_percent, promo_date, placed_only)

    @app.get("/api/cfb/parlays/{parlay_id}", response_model=CFBParlayResponse)
    async def api_get_cfb_parlay_by_id(parlay_id: int):
        """Get specific CFB parlay by ID"""
        return await get_cfb_parlay_by_id(parlay_id)

    @app.get("/api/cfb/games", response_model=list[CFBGameResponse])
    async def api_get_cfb_games(
        limit: int = Query(100, description="Maximum number of games to return"),
        is_fbs: bool | None = Query(None, description="Filter by FBS status"),
        completed: bool | None = Query(None, description="Filter by completion status"),
    ):
        """Get CFB games data"""
        return await get_cfb_games(limit, is_fbs, completed)

    @app.get("/api/cfb/analytics", response_model=CFBAnalyticsResponse)
    async def api_get_cfb_analytics():
        """Get comprehensive CFB analytics"""
        return await get_cfb_analytics()

    @app.post("/api/cfb/parlays/{parlay_id}/status")
    async def api_update_cfb_parlay_status(
        parlay_id: int,
        placed: bool = Query(..., description="Whether parlay was placed"),
        result: str | None = Query(None, description="Result (win/loss/push)"),
        actual_payout: float | None = Query(None, description="Actual payout received"),
    ):
        """Update CFB parlay status"""
        return await update_cfb_parlay_status(parlay_id, placed, result, actual_payout)

    @app.get("/api/cfb/status")
    async def api_cfb_status():
        """Get CFB system status"""
        tables_ready = ensure_cfb_tables()

        status = {
            "system": "EQ12 NCAA CFB Mystery Profit Boost Optimizer",
            "version": "2.0.0",
            "database_ready": tables_ready,
            "database_path": EQ12_DB_PATH,
            "endpoints": [
                "GET /api/cfb/parlays - List CFB parlays",
                "GET /api/cfb/parlays/{id} - Get specific parlay",
                "GET /api/cfb/games - List CFB games",
                "GET /api/cfb/analytics - Get analytics dashboard",
                "POST /api/cfb/parlays/{id}/status - Update parlay status",
                "GET /api/cfb/status - This status endpoint",
            ],
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return JSONResponse(content=status)


if __name__ == "__main__":
    # Test the CFB backend integration
    from fastapi import FastAPI

    app = FastAPI(title="EQ12 CFB Backend Test")
    register_cfb_endpoints(app)

    print("EQ12 CFB Backend endpoints registered successfully!")
    print("Available endpoints:")
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            print(f"  {next(iter(route.methods))} {route.path}")
