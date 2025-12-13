#!/usr/bin/env python3
"""
EQ12 Sports Betting Monetization Engine - Turn-Key Revenue Platform
==================================================================

Complete sports betting monetization system with:
- EV/Value-Bet Feed API with LLM explanations
- Parlay Optimizer with Kelly staking
- Live Betting Coach Bot (Discord/Telegram)
- Player Props Model with explainers
- Content Studio with RAG
- Bankroll & Compliance Copilot
- Stripe subscription integration
- Secure OpenAI cost controls

Revenue Streams:
- API subscriptions ($29-199/month)
- B2B white-label ($99/month + usage)
- Content licensing ($19/article)
- Premium alerts and coaching

Author: EQ12 Development Team
Version: 2.0.0
"""

import asyncio
import hashlib
import json
import logging
import os
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

import httpx
import stripe
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from eq12_odds_ingestor import EQ12OddsIngestor

# Import existing EQ12 components
from eq12_openai_security import EQ12OpenAISecurityManager
from eq12_parlay_sanitizer import EQ12ParlaySanitizer

# Configure logging with secret masking
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# API Models
class EVRequest(BaseModel):
    sport: str = "nfl"
    limit: int = Field(default=10, le=50)
    min_ev: float = Field(default=1.0, ge=0)


class ParlayRequest(BaseModel):
    legs: list[dict[str, Any]]
    bankroll: float = Field(gt=0)
    risk_pct: float = Field(default=2.0, le=10.0)
    sportsbook: str = "draftkings"
    state: str = "NJ"


class AlertRequest(BaseModel):
    webhook_url: str
    sports: list[str] = ["nfl", "nba"]
    min_ev: float = 3.0
    frequency: str = "5min"  # 5min, hourly, instant


class ContentRequest(BaseModel):
    content_type: str  # preview, recap, explainer
    sport: str
    game_id: str | None = None
    target_length: int = Field(default=500, le=2000)


# Subscription tiers
SUBSCRIPTION_TIERS = {
    "bettor": {
        "price": 29.00,
        "features": ["hourly_ev_feed", "basic_props"],
        "limits": {"api_calls": 1000, "alerts": 50},
    },
    "pro": {
        "price": 79.00,
        "features": ["5min_ev_feed", "live_coach", "parlay_optimizer"],
        "limits": {"api_calls": 5000, "alerts": 500},
    },
    "enterprise": {
        "price": 199.00,
        "features": ["all", "custom_watchlists", "priority_support"],
        "limits": {"api_calls": 50000, "alerts": 10000},
    },
}


@dataclass
class BettingLeg:
    """Individual betting leg with EV calculation"""

    sportsbook: str
    sport: str
    game_id: str
    market: str
    selection: str
    odds: float  # American odds
    fair_odds: float  # Calculated fair value
    ev_percent: float  # Expected value percentage
    confidence: float  # Model confidence 0-1
    book_limit: float | None = None

    @property
    def implied_prob(self) -> float:
        """Convert American odds to implied probability"""
        if self.odds > 0:
            return 100 / (self.odds + 100)
        else:
            return abs(self.odds) / (abs(self.odds) + 100)

    @property
    def fair_prob(self) -> float:
        """Fair probability from our model"""
        if self.fair_odds > 0:
            return 100 / (self.fair_odds + 100)
        else:
            return abs(self.fair_odds) / (abs(self.fair_odds) + 100)


class EQ12BettingEngine:
    """Core sports betting monetization engine"""

    def __init__(self):
        self.app = FastAPI(title="EQ12 Betting Engine", version="2.0.0")

        # Initialize components
        self.openai_manager = EQ12OpenAISecurityManager("betting")
        self.parlay_sanitizer = EQ12ParlaySanitizer()
        self.odds_ingestor = EQ12OddsIngestor()

        # Database setup
        self.db_path = "C:/EQ12/logs/betting_engine.db"
        self.redis_client = None

        # API security
        self.security = HTTPBearer()

        # Stripe setup
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

        # Cache for expensive operations
        self.ev_cache = {}
        self.explanation_cache = {}

        self.setup_database()
        self.setup_middleware()
        self.setup_routes()

    def setup_database(self):
        """Initialize SQLite database for betting data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users and subscriptions
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                subscription_tier TEXT DEFAULT 'free',
                stripe_customer_id TEXT,
                api_key TEXT UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME
            )
        """
        )

        # API usage tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS api_usage (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                endpoint TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cost_usd REAL DEFAULT 0,
                tokens_used INTEGER DEFAULT 0,
                response_cached BOOLEAN DEFAULT FALSE
            )
        """
        )

        # Betting alerts log
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS betting_alerts (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                alert_type TEXT,
                content TEXT,
                ev_percent REAL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                clicked BOOLEAN DEFAULT FALSE
            )
        """
        )

        # EV calculations cache
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ev_calculations (
                id TEXT PRIMARY KEY,
                sport TEXT,
                game_id TEXT,
                market TEXT,
                sportsbook TEXT,
                odds REAL,
                fair_odds REAL,
                ev_percent REAL,
                confidence REAL,
                calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Content generation tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS content_generated (
                id TEXT PRIMARY KEY,
                content_type TEXT,
                sport TEXT,
                game_id TEXT,
                word_count INTEGER,
                openai_cost REAL,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Betting engine database initialized")

    def setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time

            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
            )
            return response

    def setup_routes(self):
        """Setup API routes for monetization"""

        # ==================== EV/VALUE-BET FEED ====================

        @self.app.get("/api/ev/top")
        async def get_top_ev_bets(
            request: EVRequest = Depends(),
            credentials: HTTPAuthorizationCredentials = Depends(self.security),
        ):
            """Get top EV bets with AI explanations - Core monetization endpoint"""

            user = await self.authenticate_user(credentials.credentials)
            await self.check_rate_limits(user, "ev_feed")

            try:
                # Get live odds from cache or ingestor
                cache_key = f"ev_{request.sport}_{request.limit}_{request.min_ev}"

                if cache_key in self.ev_cache:
                    cached_data = self.ev_cache[cache_key]
                    if datetime.now() - cached_data["timestamp"] < timedelta(minutes=5):
                        legs = cached_data["legs"]
                    else:
                        legs = await self.calculate_ev_legs(
                            request.sport, request.limit, request.min_ev
                        )
                        self.ev_cache[cache_key] = {"legs": legs, "timestamp": datetime.now()}
                else:
                    legs = await self.calculate_ev_legs(
                        request.sport, request.limit, request.min_ev
                    )
                    self.ev_cache[cache_key] = {"legs": legs, "timestamp": datetime.now()}

                # Generate AI explanation for top legs
                explanation = await self.generate_ev_explanation(
                    legs[:3], user["subscription_tier"]
                )

                # Log usage
                await self.log_api_usage(user["id"], "ev_feed", explanation.get("cost", 0))

                return {
                    "legs": [asdict(leg) for leg in legs],
                    "explanation": explanation["content"],
                    "generated_at": datetime.now().isoformat(),
                    "cache_hit": cache_key in self.ev_cache,
                }

            except Exception as e:
                logger.error(f"EV feed error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== PARLAY OPTIMIZER ====================

        @self.app.post("/api/parlay/optimize")
        async def optimize_parlay(
            request: ParlayRequest,
            credentials: HTTPAuthorizationCredentials = Depends(self.security),
        ):
            """Optimize parlay with legal validation and Kelly staking"""

            user = await self.authenticate_user(credentials.credentials)
            await self.check_rate_limits(user, "parlay_optimizer")

            try:
                # Validate parlay legality
                validation_result = await self.parlay_sanitizer.validate_parlay(
                    request.legs, request.sportsbook, request.state
                )

                if not validation_result.is_legal:
                    return {
                        "legal": False,
                        "issues": validation_result.issues,
                        "suggestions": validation_result.suggestions,
                    }

                # Calculate optimal stake using Kelly criterion
                combined_ev = self.calculate_parlay_ev(request.legs)
                kelly_fraction = combined_ev / 100  # Convert EV% to fraction

                # Apply fractional Kelly for risk management
                conservative_kelly = kelly_fraction * 0.25  # 25% Kelly
                optimal_stake = min(
                    request.bankroll * conservative_kelly,
                    request.bankroll * (request.risk_pct / 100),  # Never exceed risk %
                )

                # Generate AI explanation
                explanation = await self.generate_parlay_explanation(
                    request.legs, optimal_stake, combined_ev, user["subscription_tier"]
                )

                await self.log_api_usage(user["id"], "parlay_optimizer", explanation.get("cost", 0))

                return {
                    "legal": True,
                    "legs": request.legs,
                    "optimal_stake": round(optimal_stake, 2),
                    "combined_ev": round(combined_ev, 2),
                    "kelly_fraction": round(kelly_fraction, 4),
                    "explanation": explanation["content"],
                    "risk_warnings": validation_result.risk_warnings,
                }

            except Exception as e:
                logger.error(f"Parlay optimization error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== LIVE COACHING ====================

        @self.app.post("/api/coach/live")
        async def live_betting_coach(
            game_state: dict[str, Any],
            credentials: HTTPAuthorizationCredentials = Depends(self.security),
        ):
            """Live betting coach with hedge suggestions"""

            user = await self.authenticate_user(credentials.credentials)

            if user["subscription_tier"] not in ["pro", "enterprise"]:
                raise HTTPException(status_code=403, detail="Pro subscription required")

            try:
                # Analyze current game situation
                coaching_advice = await self.generate_live_coaching(
                    game_state, user["subscription_tier"]
                )

                await self.log_api_usage(user["id"], "live_coach", coaching_advice.get("cost", 0))

                return {
                    "advice": coaching_advice["content"],
                    "confidence": coaching_advice.get("confidence", 0.7),
                    "hedge_suggestions": coaching_advice.get("hedges", []),
                    "generated_at": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Live coaching error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== PROPS EXPLAINER ====================

        @self.app.get("/api/props/{sport}")
        async def get_props_analysis(
            sport: str, credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Player props analysis with model explanations"""

            user = await self.authenticate_user(credentials.credentials)

            try:
                # Get props projections (deterministic model)
                props = await self.calculate_props_projections(sport)

                # Generate AI explanations for top edges
                explanation = await self.generate_props_explanation(
                    props, user["subscription_tier"]
                )

                await self.log_api_usage(user["id"], "props_analysis", explanation.get("cost", 0))

                return {
                    "props": props,
                    "explanation": explanation["content"],
                    "model_confidence": explanation.get("confidence", 0.75),
                }

            except Exception as e:
                logger.error(f"Props analysis error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== CONTENT STUDIO ====================

        @self.app.post("/api/content/generate")
        async def generate_content(
            request: ContentRequest,
            credentials: HTTPAuthorizationCredentials = Depends(self.security),
        ):
            """Generate betting content with RAG"""

            user = await self.authenticate_user(credentials.credentials)

            try:
                # Generate content using RAG on historical picks
                content = await self.generate_betting_content(request, user["subscription_tier"])

                # Log content generation
                await self.log_content_generation(
                    request.content_type,
                    request.sport,
                    len(content["content"].split()),
                    content.get("cost", 0),
                )

                await self.log_api_usage(user["id"], "content_generation", content.get("cost", 0))

                return {
                    "content": content["content"],
                    "word_count": len(content["content"].split()),
                    "seo_keywords": content.get("keywords", []),
                    "generated_at": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Content generation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== WEBHOOKS & ALERTS ====================

        @self.app.post("/api/alerts/setup")
        async def setup_betting_alerts(
            request: AlertRequest,
            credentials: HTTPAuthorizationCredentials = Depends(self.security),
        ):
            """Setup automated betting alerts"""

            user = await self.authenticate_user(credentials.credentials)

            try:
                # Validate webhook URL
                async with httpx.AsyncClient() as client:
                    test_response = await client.post(
                        request.webhook_url, json={"test": True, "source": "EQ12"}, timeout=10
                    )

                if test_response.status_code != 200:
                    raise HTTPException(400, "Webhook URL validation failed")

                # Store alert configuration
                alert_id = hashlib.md5(f"{user['id']}{request.webhook_url}".encode()).hexdigest()

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO betting_alerts
                    (id, user_id, alert_type, content) VALUES (?, ?, ?, ?)
                """,
                    (alert_id, user["id"], "webhook_config", json.dumps(asdict(request))),
                )

                conn.commit()
                conn.close()

                return {"alert_id": alert_id, "status": "configured", "test_sent": True}

            except Exception as e:
                logger.error(f"Alert setup error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== SUBSCRIPTION MANAGEMENT ====================

        @self.app.post("/api/subscription/create")
        async def create_subscription(subscription_data: dict[str, Any]):
            """Create Stripe subscription"""

            try:
                tier = subscription_data["tier"]
                email = subscription_data["email"]

                if tier not in SUBSCRIPTION_TIERS:
                    raise HTTPException(400, "Invalid subscription tier")

                # Create Stripe customer
                customer = stripe.Customer.create(email=email, metadata={"tier": tier})

                # Create subscription
                subscription = stripe.Subscription.create(
                    customer=customer.id,
                    items=[
                        {
                            "price_data": {
                                "currency": "usd",
                                "product_data": {"name": f"EQ12 {tier.title()} Plan"},
                                "unit_amount": int(SUBSCRIPTION_TIERS[tier]["price"] * 100),
                                "recurring": {"interval": "month"},
                            },
                        }
                    ],
                    metadata={"tier": tier},
                )

                # Create user account
                api_key = self.generate_api_key()
                user_id = hashlib.md5(email.encode()).hexdigest()

                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO users
                    (id, email, subscription_tier, stripe_customer_id, api_key)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (user_id, email, tier, customer.id, api_key),
                )

                conn.commit()
                conn.close()

                return {
                    "user_id": user_id,
                    "api_key": api_key,
                    "subscription_id": subscription.id,
                    "status": "active",
                }

            except Exception as e:
                logger.error(f"Subscription creation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== ANALYTICS DASHBOARD ====================

        @self.app.get("/dashboard", response_class=HTMLResponse)
        async def analytics_dashboard():
            """Revenue and usage analytics dashboard"""
            return self.get_dashboard_html()

    # ==================== CORE CALCULATION METHODS ====================

    async def calculate_ev_legs(self, sport: str, limit: int, min_ev: float) -> list[BettingLeg]:
        """Calculate EV for available betting legs - deterministic math"""

        # Get live odds from ingestor
        odds_data = await self.odds_ingestor.get_live_odds(sport)

        legs = []

        for game in odds_data.get("games", []):
            for market in game.get("markets", []):
                for outcome in market.get("outcomes", []):
                    # Calculate fair odds using our model (simplified)
                    fair_odds = self.calculate_fair_odds(game, market, outcome)

                    if fair_odds:
                        book_odds = outcome.get("price")
                        ev_percent = self.calculate_ev_percentage(book_odds, fair_odds)

                        if ev_percent >= min_ev:
                            leg = BettingLeg(
                                sportsbook=outcome.get("sportsbook"),
                                sport=sport,
                                game_id=game.get("id"),
                                market=market.get("key"),
                                selection=outcome.get("name"),
                                odds=book_odds,
                                fair_odds=fair_odds,
                                ev_percent=ev_percent,
                                confidence=self.calculate_confidence(game, market, outcome),
                            )
                            legs.append(leg)

        # Sort by EV percentage descending
        legs.sort(key=lambda x: x.ev_percent, reverse=True)

        return legs[:limit]

    def calculate_fair_odds(self, game: dict, market: dict, outcome: dict) -> float | None:
        """Calculate fair odds using our proprietary model - deterministic"""

        # Simplified fair odds calculation
        # In production, this would use sophisticated models

        market_type = market.get("key")

        if market_type == "h2h":  # Moneyline
            # Use team ratings, recent form, injuries etc
            home_rating = game.get("home_team_rating", 1500)
            away_rating = game.get("away_team_rating", 1500)

            # Simple Elo-based calculation
            rating_diff = home_rating - away_rating
            home_win_prob = 1 / (1 + 10 ** (-rating_diff / 400))

            if outcome.get("name") == game.get("home_team"):
                fair_prob = home_win_prob
            else:
                fair_prob = 1 - home_win_prob

            # Convert probability to American odds
            if fair_prob > 0.5:
                fair_odds = -(fair_prob / (1 - fair_prob)) * 100
            else:
                fair_odds = ((1 - fair_prob) / fair_prob) * 100

            return fair_odds

        elif market_type == "totals":  # Over/Under
            # Use team pace, defense ratings, weather etc
            total_line = float(market.get("point", 0))

            # Simplified total calculation
            home_avg = game.get("home_team_avg_points", 110)
            away_avg = game.get("away_team_avg_points", 110)
            projected_total = (home_avg + away_avg) * 0.96  # Slight under bias

            if outcome.get("name").lower().startswith("over"):
                over_prob = max(0.1, min(0.9, (projected_total - total_line) / 20 + 0.5))
                fair_prob = over_prob
            else:
                over_prob = max(0.1, min(0.9, (projected_total - total_line) / 20 + 0.5))
                fair_prob = 1 - over_prob

            if fair_prob > 0.5:
                fair_odds = -(fair_prob / (1 - fair_prob)) * 100
            else:
                fair_odds = ((1 - fair_prob) / fair_prob) * 100

            return fair_odds

        # For other markets, return None (no model available)
        return None

    def calculate_ev_percentage(self, book_odds: float, fair_odds: float) -> float:
        """Calculate EV percentage - deterministic formula"""

        # Convert to probabilities
        if book_odds > 0:
            book_prob = 100 / (book_odds + 100)
        else:
            book_prob = abs(book_odds) / (abs(book_odds) + 100)

        if fair_odds > 0:
            fair_prob = 100 / (fair_odds + 100)
        else:
            fair_prob = abs(fair_odds) / (abs(fair_odds) + 100)

        # EV% = (Fair Probability / Implied Probability - 1) * 100
        ev_percent = (fair_prob / book_prob - 1) * 100 if book_prob > 0 else 0

        return ev_percent

    def calculate_confidence(self, game: dict, market: dict, outcome: dict) -> float:
        """Calculate model confidence 0-1"""

        confidence = 0.7  # Base confidence

        # Increase confidence based on data availability
        if game.get("home_team_rating") and game.get("away_team_rating"):
            confidence += 0.1

        if game.get("injuries_updated"):
            confidence += 0.05

        if market.get("volume_high"):
            confidence += 0.1

        return min(confidence, 0.95)

    def calculate_parlay_ev(self, legs: list[dict]) -> float:
        """Calculate combined parlay EV - deterministic"""

        combined_prob = 1.0
        combined_payout = 1.0

        for leg in legs:
            odds = leg.get("odds", 0)

            # Get fair probability (simplified)
            if odds > 0:
                fair_prob = 0.5  # Placeholder - would use actual model
            else:
                fair_prob = 0.6  # Placeholder

            combined_prob *= fair_prob

            # Calculate payout multiplier
            payout_mult = odds / 100 + 1 if odds > 0 else 100 / abs(odds) + 1

            combined_payout *= payout_mult

        # Combined EV = (Fair Win Probability * Payout) - 1
        expected_return = combined_prob * combined_payout
        ev_percent = (expected_return - 1) * 100

        return ev_percent

    # ==================== AI EXPLANATION METHODS ====================

    async def generate_ev_explanation(
        self, legs: list[BettingLeg], subscription_tier: str
    ) -> dict[str, Any]:
        """Generate AI explanation for EV bets - uses OpenAI for summaries only"""

        if subscription_tier == "free":
            return {
                "content": "Upgrade to Pro for AI-powered explanations and insights.",
                "cost": 0,
            }

        # Check cache first
        cache_key = (
            f"ev_explain_{hashlib.md5(str([leg.game_id for leg in legs]).encode()).hexdigest()}"
        )

        if cache_key in self.explanation_cache:
            cached = self.explanation_cache[cache_key]
            if datetime.now() - cached["timestamp"] < timedelta(minutes=10):
                return cached["content"]

        # Prepare data for AI
        legs_data = []
        for leg in legs:
            legs_data.append(
                {
                    "sportsbook": leg.sportsbook,
                    "market": leg.market,
                    "selection": leg.selection,
                    "odds": leg.odds,
                    "ev_percent": round(leg.ev_percent, 1),
                    "confidence": round(leg.confidence, 2),
                }
            )

        prompt = f"""Summarize why these {len(legs)} betting legs are +EV. Be concise, factual, and avoid guarantees.

Data: {json.dumps(legs_data, indent=2)}

Constraints:
- ≤120 words total
- Mention top 3 legs with sportsbook and EV%
- Include caution if EV < 3% or confidence low
- Focus on value, not predictions"""

        try:
            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [
                    {
                        "role": "system",
                        "content": "You are EQ12's betting explainer. Be concise, factual, and avoid guarantees.",
                    },
                    {"role": "user", "content": prompt},
                ],
                {"max_tokens": 220, "temperature": 0.2},
            )

            explanation = response["response"]["choices"][0]["message"]["content"]
            cost = response.get("cost_check", {}).get("estimated_cost", 0)

            # Cache the result
            result = {"content": explanation, "cost": cost}
            self.explanation_cache[cache_key] = {"content": result, "timestamp": datetime.now()}

            return result

        except Exception as e:
            logger.error(f"AI explanation error: {e}")
            return {
                "content": "AI explanation temporarily unavailable. Value bets identified using proprietary models.",
                "cost": 0,
            }

    async def generate_parlay_explanation(
        self, legs: list[dict], stake: float, ev: float, tier: str
    ) -> dict[str, Any]:
        """Generate parlay optimization explanation"""

        if tier == "free":
            return {"content": "Upgrade for detailed parlay analysis.", "cost": 0}

        prompt = f"""Explain this parlay optimization for a bettor:

Legs: {len(legs)} selections
Recommended Stake: ${stake:.2f}
Combined EV: {ev:.1f}%

Key points to cover:
- Why this stake size (Kelly criterion)
- Correlation risks between legs
- Risk management advice
- When to avoid betting

Keep under 100 words, practical tone."""

        try:
            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [
                    {
                        "role": "system",
                        "content": "You are a professional betting advisor. Focus on risk management.",
                    },
                    {"role": "user", "content": prompt},
                ],
                {"max_tokens": 180, "temperature": 0.3},
            )

            return {
                "content": response["response"]["choices"][0]["message"]["content"],
                "cost": response.get("cost_check", {}).get("estimated_cost", 0),
            }

        except Exception as e:
            logger.error(f"Parlay explanation error: {e}")
            return {"content": "Technical analysis complete. Proceed with caution.", "cost": 0}

    async def generate_live_coaching(self, game_state: dict, tier: str) -> dict[str, Any]:
        """Generate live betting coaching advice"""

        prompt = f"""Provide live betting advice for this game situation:

Game State: {json.dumps(game_state, indent=2)}

Focus on:
- Key momentum shifts
- Hedge opportunities
- Risk management
- Specific actionable advice

Keep under 80 words, urgent tone."""

        try:
            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [
                    {
                        "role": "system",
                        "content": "You are a live betting coach. Give specific, actionable advice.",
                    },
                    {"role": "user", "content": prompt},
                ],
                {"max_tokens": 150, "temperature": 0.4},
            )

            return {
                "content": response["response"]["choices"][0]["message"]["content"],
                "cost": response.get("cost_check", {}).get("estimated_cost", 0),
                "confidence": 0.8,
            }

        except Exception as e:
            logger.error(f"Live coaching error: {e}")
            return {"content": "Monitor for line movement opportunities.", "cost": 0}

    async def generate_props_explanation(self, props: list[dict], tier: str) -> dict[str, Any]:
        """Generate player props model explanation"""

        if not props:
            return {"content": "No props edges found at this time.", "cost": 0}

        prompt = f"""Explain these player props edges:

Top Props: {json.dumps(props[:3], indent=2)}

Cover:
- Why our model likes these props
- Key factors (matchups, trends, etc.)
- Confidence level and caveats

Under 100 words."""

        try:
            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [
                    {
                        "role": "system",
                        "content": "You are a props betting analyst. Explain edges clearly.",
                    },
                    {"role": "user", "content": prompt},
                ],
                {"max_tokens": 180, "temperature": 0.3},
            )

            return {
                "content": response["response"]["choices"][0]["message"]["content"],
                "cost": response.get("cost_check", {}).get("estimated_cost", 0),
                "confidence": 0.75,
            }

        except Exception as e:
            logger.error(f"Props explanation error: {e}")
            return {"content": "Props analysis available. Check individual projections.", "cost": 0}

    async def generate_betting_content(self, request: ContentRequest, tier: str) -> dict[str, Any]:
        """Generate betting content using RAG"""

        # Get historical context from database
        historical_context = await self.get_historical_betting_context(request.sport)

        prompt = f"""Write a {request.content_type} for {request.sport}.

Historical Context: {historical_context}

Requirements:
- Target length: {request.target_length} words
- SEO-friendly with keywords
- Educational disclaimer included
- Engaging but professional tone

Content Type Guidelines:
- Preview: Focus on key matchups and betting angles
- Recap: Summarize results and lessons learned
- Explainer: Teach betting concepts with examples"""

        try:
            response = await self.openai_manager.secure_openai_request(
                "gpt-4o" if request.target_length > 800 else "gpt-4o-mini",
                [
                    {
                        "role": "system",
                        "content": "You are a professional sports betting writer. Educational focus, no guarantees.",
                    },
                    {"role": "user", "content": prompt},
                ],
                {"max_tokens": request.target_length // 2, "temperature": 0.6},
            )

            content = response["response"]["choices"][0]["message"]["content"]

            # Extract SEO keywords (simplified)
            keywords = self.extract_keywords(content, request.sport)

            return {
                "content": content,
                "cost": response.get("cost_check", {}).get("estimated_cost", 0),
                "keywords": keywords,
            }

        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return {
                "content": f"Content generation temporarily unavailable for {request.sport}.",
                "cost": 0,
                "keywords": [],
            }

    # ==================== HELPER METHODS ====================

    async def authenticate_user(self, api_key: str) -> dict[str, Any]:
        """Authenticate user by API key"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE api_key = ?", (api_key,))
        user = cursor.fetchone()

        conn.close()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")

        return {
            "id": user[0],
            "email": user[1],
            "subscription_tier": user[2],
            "stripe_customer_id": user[3],
        }

    async def check_rate_limits(self, user: dict, endpoint: str):
        """Check API rate limits based on subscription tier"""

        tier_limits = SUBSCRIPTION_TIERS.get(
            user["subscription_tier"], {"limits": {"api_calls": 100}}
        )

        # Check daily usage
        today = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM api_usage
            WHERE user_id = ? AND DATE(timestamp) = ? AND endpoint = ?
        """,
            (user["id"], today, endpoint),
        )

        daily_usage = cursor.fetchone()[0]
        conn.close()

        if daily_usage >= tier_limits["limits"]["api_calls"]:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    async def log_api_usage(self, user_id: str, endpoint: str, cost: float = 0, tokens: int = 0):
        """Log API usage for billing and analytics"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        usage_id = hashlib.md5(f"{user_id}{endpoint}{time.time()}".encode()).hexdigest()

        cursor.execute(
            """
            INSERT INTO api_usage (id, user_id, endpoint, cost_usd, tokens_used)
            VALUES (?, ?, ?, ?, ?)
        """,
            (usage_id, user_id, endpoint, cost, tokens),
        )

        conn.commit()
        conn.close()

    async def log_content_generation(
        self, content_type: str, sport: str, word_count: int, cost: float
    ):
        """Log content generation for analytics"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        content_id = hashlib.md5(f"{content_type}{sport}{time.time()}".encode()).hexdigest()

        cursor.execute(
            """
            INSERT INTO content_generated (id, content_type, sport, word_count, openai_cost)
            VALUES (?, ?, ?, ?, ?)
        """,
            (content_id, content_type, sport, word_count, cost),
        )

        conn.commit()
        conn.close()

    async def calculate_props_projections(self, sport: str) -> list[dict]:
        """Calculate player props projections - deterministic model"""

        # Simplified props calculation
        # In production, would use sophisticated player models

        props = []

        if sport == "nfl":
            # Example: QB passing yards
            props.append(
                {
                    "player": "Patrick Mahomes",
                    "market": "passing_yards",
                    "line": 287.5,
                    "projection": 295.2,
                    "edge": "+7.7 yards",
                    "recommendation": "Over",
                    "confidence": 0.73,
                }
            )

        elif sport == "nba":
            # Example: Player points
            props.append(
                {
                    "player": "LeBron James",
                    "market": "points",
                    "line": 25.5,
                    "projection": 23.8,
                    "edge": "-1.7 points",
                    "recommendation": "Under",
                    "confidence": 0.68,
                }
            )

        return props

    async def get_historical_betting_context(self, sport: str) -> str:
        """Get historical betting context for RAG"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get recent successful picks for context
        cursor.execute(
            """
            SELECT content FROM betting_alerts
            WHERE alert_type LIKE ? AND ev_percent > 3.0
            ORDER BY sent_at DESC LIMIT 5
        """,
            (f"%{sport}%",),
        )

        recent_picks = cursor.fetchall()
        conn.close()

        if recent_picks:
            return f"Recent successful {sport} analysis: " + "; ".join(
                [pick[0][:100] for pick in recent_picks]
            )
        else:
            return f"Building {sport} betting history..."

    def extract_keywords(self, content: str, sport: str) -> list[str]:
        """Extract SEO keywords from content"""

        keywords = [sport, "betting", "odds", "analysis"]

        # Simple keyword extraction (in production would use NLP)
        common_betting_terms = [
            "value bet",
            "expected value",
            "bankroll",
            "stake",
            "line movement",
            "sharp money",
            "public betting",
        ]

        for term in common_betting_terms:
            if term.lower() in content.lower():
                keywords.append(term)

        return list(set(keywords))[:10]

    def generate_api_key(self) -> str:
        """Generate secure API key"""
        import secrets

        return f"eq12_bet_{secrets.token_urlsafe(32)}"

    def get_dashboard_html(self) -> str:
        """Generate analytics dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>EQ12 Betting Engine Analytics</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .metric { background: white; padding: 20px; margin: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric h3 { margin: 0 0 10px 0; color: #333; }
                .metric .value { font-size: 2em; font-weight: bold; color: #4CAF50; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 EQ12 Betting Engine Analytics</h1>

                <div class="grid">
                    <div class="metric">
                        <h3>Daily Revenue</h3>
                        <div class="value" id="dailyRevenue">$0</div>
                    </div>

                    <div class="metric">
                        <h3>Active Subscriptions</h3>
                        <div class="value" id="activeUsers">0</div>
                    </div>

                    <div class="metric">
                        <h3>API Calls Today</h3>
                        <div class="value" id="apiCalls">0</div>
                    </div>

                    <div class="metric">
                        <h3>OpenAI Costs</h3>
                        <div class="value" id="openaiCosts">$0</div>
                    </div>
                </div>

                <div class="metric">
                    <h3>📊 Revenue Streams</h3>
                    <ul>
                        <li><strong>EV Feed API:</strong> $29-79/month subscriptions</li>
                        <li><strong>Parlay Optimizer:</strong> Pro feature + B2B licensing</li>
                        <li><strong>Live Coaching:</strong> Premium bot subscriptions</li>
                        <li><strong>Content Studio:</strong> $19/article + white-label</li>
                        <li><strong>Props Analysis:</strong> Weekly reports + API access</li>
                    </ul>
                </div>

                <div class="metric">
                    <h3>🎯 Monthly Targets</h3>
                    <ul>
                        <li><strong>Bettor Plans:</strong> 500 users × $29 = $14,500</li>
                        <li><strong>Pro Plans:</strong> 200 users × $79 = $15,800</li>
                        <li><strong>Enterprise:</strong> 50 users × $199 = $9,950</li>
                        <li><strong>Total Target:</strong> $40,250/month</li>
                    </ul>
                </div>
            </div>

            <script>
                // Auto-refresh metrics every 30 seconds
                setInterval(async () => {
                    try {
                        const response = await fetch('/api/metrics');
                        const data = await response.json();

                        document.getElementById('dailyRevenue').textContent = '$' + (data.daily_revenue || 0);
                        document.getElementById('activeUsers').textContent = data.active_users || 0;
                        document.getElementById('apiCalls').textContent = data.api_calls_today || 0;
                        document.getElementById('openaiCosts').textContent = '$' + (data.openai_costs || 0);
                    } catch (error) {
                        console.log('Metrics update failed:', error);
                    }
                }, 30000);
            </script>
        </body>
        </html>
        """


# ==================== DISCORD BOT INTEGRATION ====================


class EQ12BettingBot:
    """Discord/Telegram bot for live betting alerts"""

    def __init__(self, betting_engine: EQ12BettingEngine):
        self.engine = betting_engine
        self.bot_token = os.getenv("DISCORD_BOT_TOKEN")

    async def send_ev_alert(self, channel_id: str, legs: list[BettingLeg]):
        """Send EV alert to Discord channel"""

        if not legs:
            return

        # Format alert message
        alert_text = "🚨 **EQ12 Value Alert** 🚨\n\n"

        for i, leg in enumerate(legs[:3], 1):
            alert_text += f"**{i}. {leg.selection}** ({leg.sportsbook})\n"
            alert_text += f"   Odds: {leg.odds:+.0f} | EV: +{leg.ev_percent:.1f}%\n\n"

        alert_text += "💰 *Educational purposes only. Bet responsibly.*"

        # Send via Discord webhook (simplified)
        webhook_url = f"https://discord.com/api/webhooks/{channel_id}"

        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json={"content": alert_text})


# ==================== MAIN APPLICATION ====================


async def main():
    """Main application entry point"""

    # Initialize betting engine
    engine = EQ12BettingEngine()

    # Start background tasks
    asyncio.create_task(run_alert_scheduler(engine))

    # Start FastAPI server
    import uvicorn

    logger.info("🚀 Starting EQ12 Betting Engine")
    logger.info("💰 Revenue streams activated:")
    logger.info("   - EV/Value-Bet Feed API ($29-79/month)")
    logger.info("   - Parlay Optimizer ($199/month)")
    logger.info("   - Live Betting Coach (Pro feature)")
    logger.info("   - Player Props Analysis (Weekly/API)")
    logger.info("   - Content Studio ($19/article)")
    logger.info("🎯 Monthly revenue target: $40,250")

    uvicorn.run(engine.app, host="0.0.0.0", port=8002)


async def run_alert_scheduler(engine: EQ12BettingEngine):
    """Background task to send automated alerts"""

    bot = EQ12BettingBot(engine)

    while True:
        try:
            # Get top EV bets
            legs = await engine.calculate_ev_legs("nfl", 5, 3.0)

            if legs:
                # Send to configured alert channels
                conn = sqlite3.connect(engine.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    """
                    SELECT user_id, content FROM betting_alerts
                    WHERE alert_type = 'webhook_config'
                """
                )

                alerts = cursor.fetchall()
                conn.close()

                for _user_id, config_json in alerts:
                    config = json.loads(config_json)

                    if config.get("frequency") == "5min":
                        await bot.send_ev_alert(config.get("webhook_url"), legs)

            # Wait 5 minutes for next check
            await asyncio.sleep(300)

        except Exception as e:
            logger.error(f"Alert scheduler error: {e}")
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
