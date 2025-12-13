#!/usr/bin/env python3
"""
EQ12 Firefox Extension API Endpoints
Integration layer between Firefox extension and EQ12 betting backend

These endpoints handle data captured by the Firefox extension:
- Odds data from betting sites
- Travel deals from booking sites
- Financial/affiliate data
- Ticket deals and promotions
"""

import json
import logging
import sqlite3
import time
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Header, Request
from pydantic import BaseModel, field_validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================================
# FIREFOX EXTENSION DATA MODELS
# ================================


class BrowserDataCapture(BaseModel):
    """Base model for data captured by Firefox extension"""

    url: str
    timestamp: str  # ISO format from JavaScript Date.toISOString()
    domain: str
    user_agent: str | None = None
    viewport_size: dict[str, int] | None = None  # {width: 1920, height: 1080}

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v):
        try:
            # Validate ISO timestamp from JavaScript
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError("Invalid ISO timestamp format")


class OddsCapture(BrowserDataCapture):
    """Odds data captured from betting sites"""

    # Core Betting Data
    event_name: str
    sport: str | None = None
    league: str | None = None

    # Odds Information
    home_team: str | None = None
    away_team: str | None = None
    moneyline_home: float | None = None
    moneyline_away: float | None = None
    spread_line: float | None = None
    spread_home_odds: float | None = None
    spread_away_odds: float | None = None
    total_line: float | None = None
    over_odds: float | None = None
    under_odds: float | None = None

    # Market Context
    sportsbook: str  # DraftKings, FanDuel, etc.
    market_type: str  # "pre_game", "live", "futures"
    event_date: str | None = None

    # Prop Bets (if available)
    player_props: list[dict[str, Any]] | None = None

    # AI Analysis Results
    ai_analysis: dict[str, Any] | None = None
    confidence_score: float | None = None


class TravelDealsCapture(BrowserDataCapture):
    """Travel deals captured from booking sites"""

    # Deal Information
    deal_type: str  # "flight", "hotel", "car_rental", "package"
    provider: str  # "Expedia", "Booking.com", "Kayak", etc.

    # Travel Details
    destination: str | None = None
    origin: str | None = None
    departure_date: str | None = None
    return_date: str | None = None

    # Pricing
    original_price: float | None = None
    sale_price: float | None = None
    discount_percentage: float | None = None
    currency: str = "USD"

    # Additional Context
    availability: str | None = None  # "limited", "high", "low"
    deal_expires: str | None = None
    promo_code: str | None = None

    # AI Analysis
    value_score: float | None = None  # 0-100 scale
    recommendation: str | None = None


class FinancialDataCapture(BrowserDataCapture):
    """Financial/investment data capture"""

    # Data Type
    data_type: str  # "stock_price", "crypto", "forex", "commodity"

    # Financial Instrument
    symbol: str | None = None
    name: str | None = None
    exchange: str | None = None

    # Pricing Data
    current_price: float | None = None
    change_amount: float | None = None
    change_percentage: float | None = None
    volume: int | None = None

    # Market Context
    market_cap: float | None = None
    pe_ratio: float | None = None

    # AI Analysis
    trend_analysis: dict[str, Any] | None = None
    risk_assessment: str | None = None


class TicketDealsCapture(BrowserDataCapture):
    """Event ticket deals capture"""

    # Event Information
    event_name: str
    event_type: str  # "concert", "sports", "theater", "comedy"
    venue: str | None = None
    event_date: str | None = None

    # Ticket Details
    section: str | None = None
    row: str | None = None
    seat_numbers: str | None = None
    quantity: int | None = None

    # Pricing
    face_value: float | None = None
    listed_price: float | None = None
    fees: float | None = None
    total_price: float | None = None

    # Seller/Platform
    seller_platform: str  # "StubHub", "Ticketmaster", "SeatGeek"
    seller_rating: float | None = None

    # Deal Quality
    market_value: float | None = None
    value_rating: str | None = None  # "excellent", "good", "fair", "poor"


class GenericDataCapture(BrowserDataCapture):
    """Generic data capture for other sites"""

    # Content Information
    page_title: str | None = None
    meta_description: str | None = None

    # Extracted Data
    structured_data: dict[str, Any] | None = None
    key_metrics: dict[str, float] | None = None
    text_content: str | None = None

    # Classification
    content_category: str | None = None
    relevance_score: float | None = None


# ================================
# RESPONSE MODELS
# ================================


class CaptureResponse(BaseModel):
    """Response for data capture endpoints"""

    success: bool
    message: str
    record_id: int | None = None
    processing_time: float | None = None
    ai_insights: dict[str, Any] | None = None


class StatusResponse(BaseModel):
    """Firefox extension status response"""

    backend_status: str
    database_status: str
    capture_stats: dict[str, int]
    last_capture: str | None = None
    recommendations: list[str] | None = None


# ================================
# DATABASE OPERATIONS
# ================================


def init_firefox_extension_db():
    """Initialize Firefox extension database tables"""
    conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
    cursor = conn.cursor()

    # Create tables for each capture type

    # Odds captures table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS odds_captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            domain TEXT NOT NULL,
            event_name TEXT NOT NULL,
            sport TEXT,
            league TEXT,
            home_team TEXT,
            away_team TEXT,
            moneyline_home REAL,
            moneyline_away REAL,
            spread_line REAL,
            spread_home_odds REAL,
            spread_away_odds REAL,
            total_line REAL,
            over_odds REAL,
            under_odds REAL,
            sportsbook TEXT NOT NULL,
            market_type TEXT NOT NULL,
            event_date TEXT,
            player_props TEXT,  -- JSON string
            ai_analysis TEXT,   -- JSON string
            confidence_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Travel deals table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS travel_captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            domain TEXT NOT NULL,
            deal_type TEXT NOT NULL,
            provider TEXT NOT NULL,
            destination TEXT,
            origin TEXT,
            departure_date TEXT,
            return_date TEXT,
            original_price REAL,
            sale_price REAL,
            discount_percentage REAL,
            currency TEXT DEFAULT 'USD',
            availability TEXT,
            deal_expires TEXT,
            promo_code TEXT,
            value_score REAL,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Financial data table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS financial_captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            domain TEXT NOT NULL,
            data_type TEXT NOT NULL,
            symbol TEXT,
            name TEXT,
            exchange TEXT,
            current_price REAL,
            change_amount REAL,
            change_percentage REAL,
            volume INTEGER,
            market_cap REAL,
            pe_ratio REAL,
            trend_analysis TEXT,  -- JSON string
            risk_assessment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Ticket deals table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ticket_captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            domain TEXT NOT NULL,
            event_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            venue TEXT,
            event_date TEXT,
            section TEXT,
            row_number TEXT,
            seat_numbers TEXT,
            quantity INTEGER,
            face_value REAL,
            listed_price REAL,
            fees REAL,
            total_price REAL,
            seller_platform TEXT NOT NULL,
            seller_rating REAL,
            market_value REAL,
            value_rating TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Generic captures table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS generic_captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            domain TEXT NOT NULL,
            page_title TEXT,
            meta_description TEXT,
            structured_data TEXT,  -- JSON string
            key_metrics TEXT,      -- JSON string
            text_content TEXT,
            content_category TEXT,
            relevance_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_odds_timestamp ON odds_captures(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_odds_domain ON odds_captures(domain)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_travel_timestamp ON travel_captures(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_financial_symbol ON financial_captures(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_event ON ticket_captures(event_name)")

    conn.commit()
    conn.close()
    logger.info("Firefox extension database tables initialized")


def insert_odds_capture(data: OddsCapture) -> int:
    """Insert odds capture into database"""
    conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO odds_captures (
            url, timestamp, domain, event_name, sport, league,
            home_team, away_team, moneyline_home, moneyline_away,
            spread_line, spread_home_odds, spread_away_odds,
            total_line, over_odds, under_odds, sportsbook, market_type,
            event_date, player_props, ai_analysis, confidence_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            data.url,
            data.timestamp,
            data.domain,
            data.event_name,
            data.sport,
            data.league,
            data.home_team,
            data.away_team,
            data.moneyline_home,
            data.moneyline_away,
            data.spread_line,
            data.spread_home_odds,
            data.spread_away_odds,
            data.total_line,
            data.over_odds,
            data.under_odds,
            data.sportsbook,
            data.market_type,
            data.event_date,
            json.dumps(data.player_props) if data.player_props else None,
            json.dumps(data.ai_analysis) if data.ai_analysis else None,
            data.confidence_score,
        ),
    )

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def insert_travel_capture(data: TravelDealsCapture) -> int:
    """Insert travel deal capture into database"""
    conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO travel_captures (
            url, timestamp, domain, deal_type, provider, destination, origin,
            departure_date, return_date, original_price, sale_price,
            discount_percentage, currency, availability, deal_expires,
            promo_code, value_score, recommendation
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            data.url,
            data.timestamp,
            data.domain,
            data.deal_type,
            data.provider,
            data.destination,
            data.origin,
            data.departure_date,
            data.return_date,
            data.original_price,
            data.sale_price,
            data.discount_percentage,
            data.currency,
            data.availability,
            data.deal_expires,
            data.promo_code,
            data.value_score,
            data.recommendation,
        ),
    )

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_capture_stats() -> dict[str, int]:
    """Get statistics on captured data"""
    conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
    cursor = conn.cursor()

    stats = {}

    # Count records in each table
    tables = {
        "odds_captures": "odds",
        "travel_captures": "travel",
        "financial_captures": "financial",
        "ticket_captures": "tickets",
        "generic_captures": "generic",
    }

    for table, key in tables.items():
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[key] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats[key] = 0

    # Get last 24 hours
    cursor.execute(
        """
        SELECT COUNT(*) FROM odds_captures
        WHERE datetime(created_at) > datetime('now', '-24 hours')
    """
    )
    stats["odds_last_24h"] = cursor.fetchone()[0]

    conn.close()
    return stats


# ================================
# FIREFOX EXTENSION API ENDPOINTS
# ================================


def register_firefox_extension_endpoints(app: FastAPI):
    """Register Firefox extension endpoints with the main FastAPI app"""

    @app.post("/api/firefox/capture/odds", response_model=CaptureResponse)
    async def capture_odds_data(
        data: OddsCapture,
        x_api_key: str | None = Header(None, alias="X-API-Key"),
        request: Request = None,
    ):
        """Capture odds data from betting sites"""
        start_time = time.time()

        try:
            # Validate API key (in production)
            # if x_api_key != "expected_key":
            #     raise HTTPException(status_code=401, detail="Invalid API key")

            # Insert into database
            record_id = insert_odds_capture(data)

            # Generate AI insights (placeholder)
            ai_insights = {
                "edge_detected": False,
                "value_rating": "unknown",
                "recommendation": "Monitor for line movement",
            }

            # Basic edge detection
            if data.moneyline_home and data.moneyline_away:
                home_implied = 1 / (
                    (abs(data.moneyline_home) / 100 + 1)
                    if data.moneyline_home > 0
                    else (100 / abs(data.moneyline_home) + 1)
                )
                away_implied = 1 / (
                    (abs(data.moneyline_away) / 100 + 1)
                    if data.moneyline_away > 0
                    else (100 / abs(data.moneyline_away) + 1)
                )

                total_implied = home_implied + away_implied
                if total_implied < 1.05:  # Low vig indicates potential value
                    ai_insights["edge_detected"] = True
                    ai_insights["value_rating"] = "potential_value"
                    ai_insights["recommendation"] = (
                        f"Low vig detected ({total_implied:.3f}). Consider for analysis."
                    )

            processing_time = time.time() - start_time

            logger.info(
                f"Captured odds data: {data.sportsbook} - {data.event_name} (ID: {record_id})"
            )

            return CaptureResponse(
                success=True,
                message=f"Odds data captured successfully from {data.sportsbook}",
                record_id=record_id,
                processing_time=processing_time,
                ai_insights=ai_insights,
            )

        except Exception as e:
            logger.error(f"Error capturing odds data: {e}")
            return CaptureResponse(
                success=False,
                message=f"Error capturing odds data: {e!s}",
                processing_time=time.time() - start_time,
            )

    @app.post("/api/firefox/capture/travel", response_model=CaptureResponse)
    async def capture_travel_data(
        data: TravelDealsCapture,
        x_api_key: str | None = Header(None, alias="X-API-Key"),
    ):
        """Capture travel deals data"""
        start_time = time.time()

        try:
            record_id = insert_travel_capture(data)

            # AI insights for travel deals
            ai_insights = {
                "deal_quality": "unknown",
                "booking_urgency": "low",
                "recommendation": "Standard travel deal",
            }

            if data.discount_percentage:
                if data.discount_percentage > 30:
                    ai_insights["deal_quality"] = "excellent"
                    ai_insights["booking_urgency"] = "high"
                    ai_insights["recommendation"] = (
                        f"Exceptional {data.discount_percentage:.0f}% discount!"
                    )
                elif data.discount_percentage > 15:
                    ai_insights["deal_quality"] = "good"
                    ai_insights["booking_urgency"] = "medium"

            processing_time = time.time() - start_time

            logger.info(
                f"Captured travel data: {data.provider} - {data.deal_type} (ID: {record_id})"
            )

            return CaptureResponse(
                success=True,
                message=f"Travel deal captured from {data.provider}",
                record_id=record_id,
                processing_time=processing_time,
                ai_insights=ai_insights,
            )

        except Exception as e:
            logger.error(f"Error capturing travel data: {e}")
            return CaptureResponse(
                success=False,
                message=f"Error capturing travel data: {e!s}",
                processing_time=time.time() - start_time,
            )

    @app.post("/api/firefox/capture/financial", response_model=CaptureResponse)
    async def capture_financial_data(
        data: FinancialDataCapture,
        x_api_key: str | None = Header(None, alias="X-API-Key"),
    ):
        """Capture financial/investment data"""
        start_time = time.time()

        try:
            conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO financial_captures (
                    url, timestamp, domain, data_type, symbol, name, exchange,
                    current_price, change_amount, change_percentage, volume,
                    market_cap, pe_ratio, trend_analysis, risk_assessment
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data.url,
                    data.timestamp,
                    data.domain,
                    data.data_type,
                    data.symbol,
                    data.name,
                    data.exchange,
                    data.current_price,
                    data.change_amount,
                    data.change_percentage,
                    data.volume,
                    data.market_cap,
                    data.pe_ratio,
                    json.dumps(data.trend_analysis) if data.trend_analysis else None,
                    data.risk_assessment,
                ),
            )

            record_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # AI insights for financial data
            ai_insights = {
                "momentum": "neutral",
                "volatility": "normal",
                "recommendation": "No specific action recommended",
            }

            if data.change_percentage and abs(data.change_percentage) > 5:
                ai_insights["volatility"] = "high"
                ai_insights["momentum"] = (
                    "strong_up" if data.change_percentage > 0 else "strong_down"
                )
                ai_insights["recommendation"] = (
                    f"High volatility detected ({data.change_percentage:+.1f}%)"
                )

            processing_time = time.time() - start_time

            logger.info(f"Captured financial data: {data.symbol or data.name} (ID: {record_id})")

            return CaptureResponse(
                success=True,
                message=f"Financial data captured for {data.symbol or data.name}",
                record_id=record_id,
                processing_time=processing_time,
                ai_insights=ai_insights,
            )

        except Exception as e:
            logger.error(f"Error capturing financial data: {e}")
            return CaptureResponse(
                success=False,
                message=f"Error capturing financial data: {e!s}",
                processing_time=time.time() - start_time,
            )

    @app.post("/api/firefox/capture/tickets", response_model=CaptureResponse)
    async def capture_ticket_data(
        data: TicketDealsCapture,
        x_api_key: str | None = Header(None, alias="X-API-Key"),
    ):
        """Capture event ticket deals"""
        start_time = time.time()

        try:
            conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO ticket_captures (
                    url, timestamp, domain, event_name, event_type, venue,
                    event_date, section, row_number, seat_numbers, quantity,
                    face_value, listed_price, fees, total_price, seller_platform,
                    seller_rating, market_value, value_rating
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data.url,
                    data.timestamp,
                    data.domain,
                    data.event_name,
                    data.event_type,
                    data.venue,
                    data.event_date,
                    data.section,
                    data.row,
                    data.seat_numbers,
                    data.quantity,
                    data.face_value,
                    data.listed_price,
                    data.fees,
                    data.total_price,
                    data.seller_platform,
                    data.seller_rating,
                    data.market_value,
                    data.value_rating,
                ),
            )

            record_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # AI insights for ticket deals
            ai_insights = {
                "value_assessment": data.value_rating or "unknown",
                "price_vs_market": "unknown",
                "recommendation": "Review ticket details",
            }

            if data.face_value and data.listed_price:
                premium = ((data.listed_price - data.face_value) / data.face_value) * 100
                if premium < 10:
                    ai_insights["value_assessment"] = "excellent"
                    ai_insights["recommendation"] = (
                        f"Great deal - only {premium:.0f}% above face value"
                    )
                elif premium > 100:
                    ai_insights["value_assessment"] = "poor"
                    ai_insights["recommendation"] = (
                        f"High premium - {premium:.0f}% above face value"
                    )

            processing_time = time.time() - start_time

            logger.info(
                f"Captured ticket data: {data.event_name} - {data.seller_platform} (ID: {record_id})"
            )

            return CaptureResponse(
                success=True,
                message=f"Ticket deal captured for {data.event_name}",
                record_id=record_id,
                processing_time=processing_time,
                ai_insights=ai_insights,
            )

        except Exception as e:
            logger.error(f"Error capturing ticket data: {e}")
            return CaptureResponse(
                success=False,
                message=f"Error capturing ticket data: {e!s}",
                processing_time=time.time() - start_time,
            )

    @app.post("/api/firefox/capture/generic", response_model=CaptureResponse)
    async def capture_generic_data(
        data: GenericDataCapture,
        x_api_key: str | None = Header(None, alias="X-API-Key"),
    ):
        """Capture generic web data"""
        start_time = time.time()

        try:
            conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO generic_captures (
                    url, timestamp, domain, page_title, meta_description,
                    structured_data, key_metrics, text_content,
                    content_category, relevance_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data.url,
                    data.timestamp,
                    data.domain,
                    data.page_title,
                    data.meta_description,
                    json.dumps(data.structured_data) if data.structured_data else None,
                    json.dumps(data.key_metrics) if data.key_metrics else None,
                    data.text_content,
                    data.content_category,
                    data.relevance_score,
                ),
            )

            record_id = cursor.lastrowid
            conn.commit()
            conn.close()

            processing_time = time.time() - start_time

            logger.info(f"Captured generic data from {data.domain} (ID: {record_id})")

            return CaptureResponse(
                success=True,
                message=f"Generic data captured from {data.domain}",
                record_id=record_id,
                processing_time=processing_time,
            )

        except Exception as e:
            logger.error(f"Error capturing generic data: {e}")
            return CaptureResponse(
                success=False,
                message=f"Error capturing generic data: {e!s}",
                processing_time=time.time() - start_time,
            )

    @app.get("/api/firefox/status", response_model=StatusResponse)
    async def firefox_extension_status():
        """Get Firefox extension integration status"""
        try:
            # Check database connectivity
            conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            db_status = "connected"

            # Get capture statistics
            capture_stats = get_capture_stats()

            # Get last capture timestamp
            conn = sqlite3.connect("C:\\EQ12\\eq12_bets.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT MAX(created_at) FROM (
                    SELECT created_at FROM odds_captures
                    UNION ALL SELECT created_at FROM travel_captures
                    UNION ALL SELECT created_at FROM financial_captures
                    UNION ALL SELECT created_at FROM ticket_captures
                    UNION ALL SELECT created_at FROM generic_captures
                )
            """
            )
            last_capture = cursor.fetchone()[0]
            conn.close()

            # Generate recommendations
            recommendations = []
            if capture_stats.get("odds", 0) > 50:
                recommendations.append("High odds capture volume - consider analysis automation")
            if capture_stats.get("travel", 0) > 20:
                recommendations.append(
                    "Multiple travel deals captured - review for booking opportunities"
                )

            return StatusResponse(
                backend_status="operational",
                database_status=db_status,
                capture_stats=capture_stats,
                last_capture=last_capture,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Firefox extension status error: {e}")
            return StatusResponse(
                backend_status="error",
                database_status="error",
                capture_stats={},
                last_capture=None,
                recommendations=[f"System error: {e!s}"],
            )

    # Initialize database tables on startup
    try:
        init_firefox_extension_db()
    except Exception as e:
        logger.error(f"Failed to initialize Firefox extension database: {e}")


# Export the registration function
__all__ = ["register_firefox_extension_endpoints"]
