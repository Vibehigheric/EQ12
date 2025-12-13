"""
EQ12 FastAPI License Server
Handles credit management, billing, and API access for EQ12 platform
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import jwt
import redis
import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="EQ12 License Server",
    description="Premium sports betting intelligence licensing and credit management",
    version="1.0.0",
)

# Security
security = HTTPBearer()

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database models
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    github_username = Column(String, unique=True, nullable=False)
    email = Column(String)
    plan = Column(String, default="free")  # free, pro, enterprise
    credits = Column(Integer, default=0)
    total_usage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    api_key = Column(String, unique=True)


class Usage(Base):
    __tablename__ = "usage"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    action = Column(String, nullable=False)  # analysis, report, backtest, etc.
    credits_consumed = Column(Integer, nullable=False)
    metadata = Column(Text)  # JSON metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    repo = Column(String)
    commit_sha = Column(String)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    credits = Column(Integer, nullable=False)
    transaction_type = Column(String, nullable=False)  # purchase, refund, bonus
    status = Column(String, default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    metadata = Column(Text)


# Pydantic models
class LicenseRequest(BaseModel):
    github_username: str
    repo: str
    action: str
    metadata: dict[str, Any] | None = None


class LicenseResponse(BaseModel):
    valid: bool
    credits_remaining: int
    plan: str
    message: str | None = None
    rate_limit: dict[str, int] | None = None


class AnalysisRequest(BaseModel):
    repo: str
    commit_sha: str
    analysis_type: str = "comprehensive"
    include_predictions: bool = True
    include_correlations: bool = True


class CreditPurchase(BaseModel):
    user_id: str
    credits: int
    payment_method: str = "stripe"
    metadata: dict[str, Any] | None = None


@dataclass
class EQ12Config:
    """EQ12 platform configuration"""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///eq12_license.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret-key")
    API_KEY_PREFIX: str = "eq12_"

    # Pricing (credits per action)
    CREDIT_RATES: dict[str, int] = {
        "basic_analysis": 1,
        "premium_analysis": 5,
        "backtest_simulation": 10,
        "live_arbitrage": 15,
        "correlation_matrix": 20,
        "ai_predictions": 25,
        "comprehensive_report": 50,
    }

    # Plan limits
    PLAN_LIMITS: dict[str, dict[str, int]] = {
        "free": {"daily_credits": 10, "monthly_credits": 100},
        "pro": {"daily_credits": 500, "monthly_credits": 10000},
        "enterprise": {"daily_credits": -1, "monthly_credits": -1},  # unlimited
    }

    # Rate limiting
    RATE_LIMITS: dict[str, dict[str, int]] = {
        "free": {"requests_per_hour": 50, "requests_per_day": 200},
        "pro": {"requests_per_hour": 500, "requests_per_day": 5000},
        "enterprise": {"requests_per_hour": -1, "requests_per_day": -1},
    }


config = EQ12Config()

# Database setup
engine = create_engine(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Redis setup
try:
    redis_client = redis.from_url(config.REDIS_URL)
    redis_client.ping()
except Exception as e:
    logger.warning(f"Redis connection failed: {e}, using in-memory cache")
    redis_client = None


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Verify API key and return user ID"""
    try:
        token = credentials.credentials

        # Try JWT first
        if token.startswith("eyJ"):
            try:
                payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
                return payload["user_id"]
            except jwt.InvalidTokenError:
                pass

        # Try API key
        if token.startswith(config.API_KEY_PREFIX):
            db = next(get_db())
            user = db.query(User).filter(User.api_key == token).first()
            if user and user.is_active:
                return user.id

        raise HTTPException(status_code=401, detail="Invalid API key")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")


async def check_rate_limit(user_id: str, plan: str) -> bool:
    """Check if user is within rate limits"""
    if plan == "enterprise":
        return True

    if not redis_client:
        return True  # Skip rate limiting if Redis unavailable

    limits = config.RATE_LIMITS.get(plan, config.RATE_LIMITS["free"])

    # Check hourly limit
    hour_key = f"rate_limit:{user_id}:hour:{datetime.utcnow().strftime('%Y%m%d%H')}"
    hourly_count = await redis_client.incr(hour_key)
    if hourly_count == 1:
        await redis_client.expire(hour_key, 3600)

    if limits["requests_per_hour"] > 0 and hourly_count > limits["requests_per_hour"]:
        return False

    # Check daily limit
    day_key = f"rate_limit:{user_id}:day:{datetime.utcnow().strftime('%Y%m%d')}"
    daily_count = await redis_client.incr(day_key)
    if daily_count == 1:
        await redis_client.expire(day_key, 86400)

    return not (limits["requests_per_day"] > 0 and daily_count > limits["requests_per_day"])


class EQ12LicenseServer:
    """Main license server class"""

    def __init__(self):
        self.config = config
        self.logger = logger

    async def validate_license(self, request: LicenseRequest, user_id: str) -> LicenseResponse:
        """Validate license and check credits"""
        db = next(get_db())

        try:
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return LicenseResponse(
                    valid=False,
                    credits_remaining=0,
                    plan="free",
                    message="User not found or inactive",
                )

            # Check rate limits
            rate_ok = await check_rate_limit(user_id, user.plan)
            if not rate_ok:
                return LicenseResponse(
                    valid=False,
                    credits_remaining=user.credits,
                    plan=user.plan,
                    message="Rate limit exceeded",
                    rate_limit=config.RATE_LIMITS.get(user.plan),
                )

            # Check credits required
            credits_required = config.CREDIT_RATES.get(request.action, 1)

            if user.plan != "enterprise" and user.credits < credits_required:
                return LicenseResponse(
                    valid=False,
                    credits_remaining=user.credits,
                    plan=user.plan,
                    message=f"Insufficient credits. Required: {credits_required}, Available: {user.credits}",
                )

            return LicenseResponse(
                valid=True, credits_remaining=user.credits, plan=user.plan, message="License valid"
            )

        except Exception as e:
            self.logger.error(f"License validation error: {e}")
            return LicenseResponse(
                valid=False, credits_remaining=0, plan="free", message="Internal error"
            )

    async def consume_credits(
        self,
        user_id: str,
        action: str,
        repo: str | None = None,
        commit_sha: str | None = None,
        metadata: dict | None = None,
    ):
        """Consume credits for an action"""
        db = next(get_db())

        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return

            credits_required = config.CREDIT_RATES.get(action, 1)

            # Don't deduct for enterprise plans
            if user.plan == "enterprise":
                credits_required = 0

            # Update user credits and usage
            user.credits = max(0, user.credits - credits_required)
            user.total_usage += credits_required
            user.last_active = datetime.utcnow()

            # Record usage
            usage = Usage(
                id=f"usage_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}",
                user_id=user_id,
                action=action,
                credits_consumed=credits_required,
                metadata=json.dumps(metadata or {}),
                repo=repo,
                commit_sha=commit_sha,
            )

            db.add(usage)
            db.commit()

            self.logger.info(
                f"Consumed {credits_required} credits for user {user_id}, action {action}"
            )

        except Exception as e:
            db.rollback()
            self.logger.error(f"Error consuming credits: {e}")

    async def generate_premium_analysis(self, request: AnalysisRequest) -> dict[str, Any]:
        """Generate premium analysis report"""
        try:
            # This would integrate with your existing EQ12 analysis engines
            analysis = {
                "repo": request.repo,
                "commit_sha": request.commit_sha,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_type": request.analysis_type,
                "report": {
                    "correlation_analysis": {
                        "enabled": request.include_correlations,
                        "strong_correlations": (
                            [
                                {
                                    "pair": "team_performance_home_odds",
                                    "correlation": 0.847,
                                    "confidence": 0.95,
                                },
                                {
                                    "pair": "weather_total_points",
                                    "correlation": -0.623,
                                    "confidence": 0.89,
                                },
                            ]
                            if request.include_correlations
                            else []
                        ),
                    },
                    "predictive_models": {
                        "enabled": request.include_predictions,
                        "predictions": (
                            [
                                {
                                    "market": "spread",
                                    "prediction": -3.5,
                                    "confidence": 0.78,
                                    "roi_projection": 12.4,
                                },
                                {
                                    "market": "total",
                                    "prediction": 47.5,
                                    "confidence": 0.81,
                                    "roi_projection": 8.9,
                                },
                            ]
                            if request.include_predictions
                            else []
                        ),
                    },
                    "arbitrage_opportunities": [
                        {
                            "books": ["DraftKings", "FanDuel"],
                            "profit_margin": 3.2,
                            "recommended_stakes": {"dk": 100, "fd": 97},
                        },
                        {
                            "books": ["Caesars", "BetMGM"],
                            "profit_margin": 1.8,
                            "recommended_stakes": {"caesars": 150, "mgm": 152},
                        },
                    ],
                    "risk_assessment": {
                        "overall_risk": "medium",
                        "volatility_score": 6.2,
                        "recommendation": "Consider reduced stake sizes due to weather uncertainty",
                    },
                    "performance_metrics": {
                        "backtested_roi": 15.7,
                        "sharpe_ratio": 2.31,
                        "max_drawdown": 4.2,
                        "win_rate": 0.647,
                    },
                },
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error generating analysis: {e}")
            raise HTTPException(status_code=500, detail="Analysis generation failed")


# Initialize license server
license_server = EQ12LicenseServer()


# API endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "EQ12 License Server",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/license/validate", response_model=LicenseResponse)
async def validate_license(request: LicenseRequest, user_id: str = Depends(verify_api_key)):
    """Validate license for an action"""
    return await license_server.validate_license(request, user_id)


@app.post("/license/consume")
async def consume_license(
    request: LicenseRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_api_key),
):
    """Consume credits for an action"""
    # Validate first
    validation = await license_server.validate_license(request, user_id)
    if not validation.valid:
        raise HTTPException(status_code=403, detail=validation.message)

    # Consume credits in background
    background_tasks.add_task(
        license_server.consume_credits,
        user_id,
        request.action,
        request.repo,
        request.metadata.get("commit_sha") if request.metadata else None,
        request.metadata,
    )

    return {"status": "success", "message": "Credits consumed"}


@app.post("/analysis/premium")
async def premium_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(verify_api_key),
):
    """Generate premium analysis report"""
    # Validate license
    license_req = LicenseRequest(
        github_username="",  # Not needed for this flow
        repo=request.repo,
        action="premium_analysis",
        metadata={"commit_sha": request.commit_sha},
    )

    validation = await license_server.validate_license(license_req, user_id)
    if not validation.valid:
        raise HTTPException(status_code=403, detail=validation.message)

    # Generate analysis
    analysis = await license_server.generate_premium_analysis(request)

    # Consume credits in background
    background_tasks.add_task(
        license_server.consume_credits,
        user_id,
        "premium_analysis",
        request.repo,
        request.commit_sha,
        {"analysis_type": request.analysis_type},
    )

    return analysis


@app.post("/credits/purchase")
async def purchase_credits(request: CreditPurchase, db: Session = Depends(get_db)):
    """Purchase credits (placeholder for payment integration)"""
    try:
        # In production, integrate with Stripe/PayPal/etc
        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create transaction record
        transaction = Transaction(
            id=f"txn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{request.user_id}",
            user_id=request.user_id,
            amount=request.credits * 0.01,  # $0.01 per credit
            credits=request.credits,
            transaction_type="purchase",
            status="completed",  # Would be "pending" in real implementation
            processed_at=datetime.utcnow(),
            metadata=json.dumps(request.metadata or {}),
        )

        # Add credits to user
        user.credits += request.credits

        db.add(transaction)
        db.commit()

        return {
            "status": "success",
            "transaction_id": transaction.id,
            "credits_added": request.credits,
            "new_balance": user.credits,
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Credit purchase error: {e}")
        raise HTTPException(status_code=500, detail="Purchase failed")


@app.get("/user/stats")
async def user_stats(user_id: str = Depends(verify_api_key), db: Session = Depends(get_db)):
    """Get user statistics"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get recent usage
    recent_usage = (
        db.query(Usage)
        .filter(Usage.user_id == user_id, Usage.timestamp >= datetime.utcnow() - timedelta(days=30))
        .all()
    )

    usage_by_action = {}
    for usage in recent_usage:
        action = usage.action
        usage_by_action[action] = usage_by_action.get(action, 0) + usage.credits_consumed

    return {
        "user_id": user.id,
        "plan": user.plan,
        "credits_remaining": user.credits,
        "total_usage": user.total_usage,
        "last_active": user.last_active.isoformat(),
        "monthly_usage": usage_by_action,
        "rate_limits": config.RATE_LIMITS.get(user.plan),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 License Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--create-user", help="Create a new user (github_username)")

    args = parser.parse_args()

    if args.create_user:
        # Create a new user
        db = SessionLocal()
        try:
            import secrets

            user_id = f"user_{secrets.token_hex(8)}"
            api_key = f"{config.API_KEY_PREFIX}{secrets.token_hex(32)}"

            user = User(
                id=user_id,
                github_username=args.create_user,
                plan="free",
                credits=100,  # Welcome bonus
                api_key=api_key,
            )

            db.add(user)
            db.commit()

            print(f"Created user: {args.create_user}")
            print(f"User ID: {user_id}")
            print(f"API Key: {api_key}")
            print("Credits: 100")

        except Exception as e:
            print(f"Error creating user: {e}")
        finally:
            db.close()
    else:
        uvicorn.run("eq12_license_server:app", host=args.host, port=args.port, reload=args.reload)
