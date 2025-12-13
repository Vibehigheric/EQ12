"""
EQ12 Enterprise AI Governance SaaS Platform
Multi-tenant API Gateway with Billing Integration and OpenAI Optimization
"""

import asyncio
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Any

import redis
import stripe
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# Import EQ12 OpenAI Optimizer
from eq12_openai_optimizer import AIProfile, OpenAIOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
Base = declarative_base()


class SubscriptionTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ENTERPRISE_PLUS = "enterprise_plus"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    stripe_customer_id = Column(String, unique=True)
    subscription_tier = Column(String, default=SubscriptionTier.STARTER)
    api_key = Column(String, unique=True)
    ai_preferences = Column(Text)  # JSON string for AI optimization preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="customer")
    api_calls = relationship("APICall", back_populates="customer")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"))
    stripe_subscription_id = Column(String, unique=True)
    tier = Column(String, nullable=False)
    status = Column(String, default="active")
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="subscriptions")


class APICall(Base):
    __tablename__ = "api_calls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"))
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    response_time_ms = Column(Float)
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    ai_profile_used = Column(String)  # Track which AI profile was used
    ai_parameters = Column(Text)  # JSON string of AI parameters used
    status_code = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="api_calls")


class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"))
    report_type = Column(String, nullable=False)
    content = Column(Text)
    risk_score = Column(Float)
    findings = Column(Text)  # JSON string
    generated_at = Column(DateTime, default=datetime.utcnow)


# Pydantic Models for API


class AIOptimizationSettings(BaseModel):
    profile: str = "balanced"  # AIProfile enum value
    temperature: float | None = None  # Override profile temperature
    top_p: float | None = None  # Override profile top_p
    max_tokens: int | None = None
    custom_system_prompt: str | None = None


class CustomerCreate(BaseModel):
    company_name: str
    email: str
    subscription_tier: SubscriptionTier = SubscriptionTier.STARTER


class CustomerResponse(BaseModel):
    id: str
    company_name: str
    email: str
    subscription_tier: str
    api_key: str
    monthly_quota: int
    current_usage: int
    ai_preferences: dict[str, Any] | None = None
    created_at: datetime


class GovernanceRequest(BaseModel):
    content: str
    compliance_frameworks: list[str] = ["gdpr", "sox", "hipaa"]
    risk_assessment: bool = True
    generate_report: bool = False
    ai_optimization: AIOptimizationSettings | None = None
    task_type: str | None = "governance"  # For intelligent profile selection


class GovernanceResponse(BaseModel):
    request_id: str
    risk_score: float
    compliance_status: str
    findings: list[dict[str, Any]]
    processing_time_ms: float
    tokens_used: int
    cost: float
    ai_profile_used: str
    ai_parameters: dict[str, Any]


class AIProfileInfo(BaseModel):
    name: str
    description: str
    temperature: float
    top_p: float
    use_case: str
    recommended_for: list[str]


class AIOptimizationResponse(BaseModel):
    available_profiles: dict[str, AIProfileInfo]
    current_settings: AIOptimizationSettings | None
    usage_statistics: dict[str, Any]
    recommendations: list[str]


class UsageStats(BaseModel):
    current_period_usage: int
    quota_remaining: int
    total_calls_this_month: int
    average_processing_time_ms: float
    total_cost_this_month: float
    ai_optimization_stats: dict[str, Any]


# Pricing Configuration
TIER_PRICING = {
    SubscriptionTier.STARTER: {
        "monthly_fee": 99.0,
        "quota": 1000,
        "cost_per_call": 0.01,
        "features": [
            "basic_governance",
            "standard_templates",
            "community_support",
            "basic_ai_optimization",
        ],
    },
    SubscriptionTier.PROFESSIONAL: {
        "monthly_fee": 499.0,
        "quota": 10000,
        "cost_per_call": 0.008,
        "features": [
            "advanced_governance",
            "custom_templates",
            "priority_support",
            "full_ai_optimization",
            "custom_profiles",
        ],
    },
    SubscriptionTier.ENTERPRISE: {
        "monthly_fee": 2999.0,
        "quota": 100000,
        "cost_per_call": 0.005,
        "features": [
            "unlimited_governance",
            "white_label",
            "dedicated_manager",
            "advanced_analytics",
            "enterprise_ai_features",
        ],
    },
    SubscriptionTier.ENTERPRISE_PLUS: {
        "monthly_fee": 0.0,  # Custom pricing
        "quota": -1,  # Unlimited
        "cost_per_call": 0.003,
        "features": [
            "on_premises",
            "custom_training",
            "consulting",
            "24_7_support",
            "custom_ai_training",
        ],
    },
}


class EQ12EnterpriseAPI:
    def __init__(self):
        self.app = FastAPI(
            title="EQ12 AI Governance Enterprise API",
            description="Scalable AI governance platform with OpenAI optimization and enterprise features",
            version="2.0.0",
            lifespan=self.lifespan,
        )

        # Configure middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Initialize components
        self.security = HTTPBearer()
        self.redis_client = None
        self.db_engine = None
        self.SessionLocal = None
        self.openai_optimizer = None

        # Configure Stripe
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_your_stripe_key_here")

        self.setup_routes()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        # Startup
        await self.initialize_database()
        await self.initialize_redis()
        await self.initialize_openai()
        logger.info("EQ12 Enterprise API started successfully")
        yield
        # Shutdown
        if self.redis_client:
            await self.redis_client.close()
        logger.info("EQ12 Enterprise API shut down")

    async def initialize_database(self):
        """Initialize database connection"""
        try:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./eq12_enterprise.db")
            self.db_engine = create_engine(database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.db_engine)

            # Create tables
            Base.metadata.create_all(bind=self.db_engine)
            logger.info(f"Database initialized: {database_url}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def initialize_redis(self):
        """Initialize Redis connection"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)

            # Test connection
            await asyncio.to_thread(self.redis_client.ping)
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Rate limiting disabled.")
            self.redis_client = None

    async def initialize_openai(self):
        """Initialize OpenAI optimizer"""
        try:
            self.openai_optimizer = OpenAIOptimizer()
            logger.info("OpenAI optimizer initialized successfully")
        except Exception as e:
            logger.error(f"OpenAI optimizer initialization failed: {e}")
            raise

    def get_db(self) -> Session:
        """Get database session"""
        db = self.SessionLocal()
        try:
            return db
        finally:
            db.close()

    async def get_customer_by_api_key(self, api_key: str) -> dict[str, Any] | None:
        """Get customer information by API key with caching"""
        if self.redis_client:
            # Try cache first
            cached_customer = self.redis_client.get(f"api_key:{api_key}")
            if cached_customer:
                return json.loads(cached_customer)

        # Query database
        db = self.get_db()
        customer = db.query(Customer).filter(Customer.api_key == api_key).first()

        if customer:
            customer_data = {
                "id": customer.id,
                "company_name": customer.company_name,
                "email": customer.email,
                "subscription_tier": customer.subscription_tier,
                "ai_preferences": (
                    json.loads(customer.ai_preferences) if customer.ai_preferences else {}
                ),
            }

            # Cache for 5 minutes
            if self.redis_client:
                self.redis_client.setex(f"api_key:{api_key}", 300, json.dumps(customer_data))

            return customer_data
        return None

    async def authenticate_customer(
        self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())
    ):
        """Authenticate customer using API key"""
        api_key = credentials.credentials
        customer = await self.get_customer_by_api_key(api_key)

        if not customer:
            raise HTTPException(status_code=401, detail="Invalid API key")

        return customer

    async def check_rate_limit(self, customer_id: str) -> bool:
        """Check if customer is within rate limits"""
        if not self.redis_client:
            return True

        rate_limit_key = f"rate_limit:{customer_id}"
        current_requests = self.redis_client.get(rate_limit_key)

        # Rate limiting: 100 requests per minute for all tiers
        rate_limit = 100

        return not (current_requests and int(current_requests) >= rate_limit)

    async def increment_rate_limit(self, customer_id: str):
        """Increment rate limit counter"""
        if self.redis_client:
            rate_limit_key = f"rate_limit:{customer_id}"
            self.redis_client.incr(rate_limit_key)
            self.redis_client.expire(rate_limit_key, 60)  # 1 minute expiry

    async def log_api_call(
        self,
        customer_id: str,
        endpoint: str,
        method: str,
        response_time_ms: float,
        tokens_used: int = 0,
        cost: float = 0.0,
        ai_profile_used: str | None = None,
        ai_parameters: dict[str, Any] | None = None,
        status_code: int = 200,
    ):
        """Log API call for usage tracking and billing"""
        db = self.get_db()

        api_call = APICall(
            customer_id=customer_id,
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
            cost=cost,
            ai_profile_used=ai_profile_used,
            ai_parameters=json.dumps(ai_parameters) if ai_parameters else None,
            status_code=status_code,
        )

        db.add(api_call)
        db.commit()

    def setup_routes(self):
        """Setup API routes"""

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "version": "2.0.0",
                "ai_optimization": "enabled",
            }

        @self.app.post("/customers", response_model=CustomerResponse)
        async def create_customer(customer_data: CustomerCreate):
            """Create new customer with API key"""
            db = self.get_db()

            # Generate API key
            api_key = f"eq12_{uuid.uuid4().hex[:16]}"

            # Create customer
            customer = Customer(
                company_name=customer_data.company_name,
                email=customer_data.email,
                subscription_tier=customer_data.subscription_tier,
                api_key=api_key,
                ai_preferences=json.dumps({"default_profile": "balanced", "custom_profiles": {}}),
            )

            db.add(customer)
            db.commit()
            db.refresh(customer)

            # Get tier info
            tier_info = TIER_PRICING[customer_data.subscription_tier]

            return CustomerResponse(
                id=customer.id,
                company_name=customer.company_name,
                email=customer.email,
                subscription_tier=customer.subscription_tier,
                api_key=api_key,
                monthly_quota=tier_info["quota"],
                current_usage=0,
                ai_preferences=json.loads(customer.ai_preferences),
                created_at=customer.created_at,
            )

        @self.app.post("/governance/analyze", response_model=GovernanceResponse)
        async def analyze_governance(
            request: GovernanceRequest,
            customer: dict = Depends(self.authenticate_customer),
        ):
            """Analyze content for governance compliance with AI optimization"""
            start_time = time.time()

            # Check rate limits
            if not await self.check_rate_limit(customer["id"]):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            # Increment rate limit counter
            await self.increment_rate_limit(customer["id"])

            try:
                # Determine AI optimization settings
                ai_settings = request.ai_optimization or AIOptimizationSettings()

                # Use customer's default profile if none specified
                if ai_settings.profile == "balanced" and "default_profile" in customer.get(
                    "ai_preferences", {}
                ):
                    ai_settings.profile = customer["ai_preferences"]["default_profile"]

                # Perform governance analysis using AI optimization
                analysis_result = await self.perform_optimized_governance_analysis(
                    request, ai_settings
                )

                processing_time = (time.time() - start_time) * 1000

                # Calculate cost based on tokens and tier
                tier_info = TIER_PRICING[customer["subscription_tier"]]
                cost = analysis_result["tokens_used"] * tier_info["cost_per_call"]

                # Log API call
                await self.log_api_call(
                    customer_id=customer["id"],
                    endpoint="/governance/analyze",
                    method="POST",
                    response_time_ms=processing_time,
                    tokens_used=analysis_result["tokens_used"],
                    cost=cost,
                    ai_profile_used=analysis_result["ai_profile_used"],
                    ai_parameters=analysis_result["ai_parameters"],
                )

                # Generate response
                return GovernanceResponse(
                    request_id=str(uuid.uuid4()),
                    risk_score=analysis_result["risk_score"],
                    compliance_status=analysis_result["compliance_status"],
                    findings=analysis_result["findings"],
                    processing_time_ms=processing_time,
                    tokens_used=analysis_result["tokens_used"],
                    cost=cost,
                    ai_profile_used=analysis_result["ai_profile_used"],
                    ai_parameters=analysis_result["ai_parameters"],
                )

            except Exception as e:
                logger.error(f"Governance analysis failed: {e}")
                raise HTTPException(status_code=500, detail="Analysis failed")

        @self.app.get("/ai/profiles", response_model=AIOptimizationResponse)
        async def get_ai_profiles(customer: dict = Depends(self.authenticate_customer)):
            """Get available AI optimization profiles and current settings"""

            # Get available profiles
            available_profiles = {}
            for profile in AIProfile:
                profile_info = self.openai_optimizer.get_profile(profile)
                available_profiles[profile.value] = AIProfileInfo(
                    name=profile_info.name,
                    description=profile_info.description,
                    temperature=profile_info.temperature,
                    top_p=profile_info.top_p,
                    use_case=profile_info.use_case,
                    recommended_for=self.get_profile_recommendations(profile),
                )

            # Get customer's current settings
            current_settings = None
            if "ai_preferences" in customer and "default_profile" in customer["ai_preferences"]:
                current_settings = AIOptimizationSettings(
                    profile=customer["ai_preferences"]["default_profile"]
                )

            # Get usage statistics
            usage_stats = self.openai_optimizer.get_usage_report()

            return AIOptimizationResponse(
                available_profiles=available_profiles,
                current_settings=current_settings,
                usage_statistics=usage_stats,
                recommendations=usage_stats.get("recommendations", []),
            )

        @self.app.put("/ai/preferences")
        async def update_ai_preferences(
            ai_settings: AIOptimizationSettings,
            customer: dict = Depends(self.authenticate_customer),
        ):
            """Update customer's AI optimization preferences"""
            db = self.get_db()

            # Update customer preferences
            customer_obj = db.query(Customer).filter(Customer.id == customer["id"]).first()
            if not customer_obj:
                raise HTTPException(status_code=404, detail="Customer not found")

            # Update AI preferences
            preferences = (
                json.loads(customer_obj.ai_preferences) if customer_obj.ai_preferences else {}
            )
            preferences["default_profile"] = ai_settings.profile

            if ai_settings.temperature is not None:
                preferences["temperature_override"] = ai_settings.temperature
            if ai_settings.top_p is not None:
                preferences["top_p_override"] = ai_settings.top_p
            if ai_settings.max_tokens is not None:
                preferences["max_tokens_override"] = ai_settings.max_tokens
            if ai_settings.custom_system_prompt is not None:
                preferences["custom_system_prompt"] = ai_settings.custom_system_prompt

            customer_obj.ai_preferences = json.dumps(preferences)
            customer_obj.updated_at = datetime.utcnow()

            db.commit()

            return {
                "message": "AI preferences updated successfully",
                "preferences": preferences,
            }

        @self.app.get("/usage/stats", response_model=UsageStats)
        async def get_usage_stats(customer: dict = Depends(self.authenticate_customer)):
            """Get customer usage statistics including AI optimization metrics"""
            db = self.get_db()

            # Get current month's usage
            current_month_start = datetime.utcnow().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )

            api_calls = (
                db.query(APICall)
                .filter(
                    APICall.customer_id == customer["id"],
                    APICall.created_at >= current_month_start,
                )
                .all()
            )

            total_calls = len(api_calls)
            sum(call.tokens_used or 0 for call in api_calls)
            total_cost = sum(call.cost or 0.0 for call in api_calls)
            avg_processing_time = sum(call.response_time_ms or 0 for call in api_calls) / max(
                total_calls, 1
            )

            # AI optimization statistics
            ai_stats = {}
            for call in api_calls:
                if call.ai_profile_used:
                    if call.ai_profile_used not in ai_stats:
                        ai_stats[call.ai_profile_used] = {
                            "calls": 0,
                            "tokens": 0,
                            "cost": 0.0,
                        }
                    ai_stats[call.ai_profile_used]["calls"] += 1
                    ai_stats[call.ai_profile_used]["tokens"] += call.tokens_used or 0
                    ai_stats[call.ai_profile_used]["cost"] += call.cost or 0.0

            # Get tier quota
            tier_info = TIER_PRICING[customer["subscription_tier"]]
            quota = tier_info["quota"]
            quota_remaining = max(0, quota - total_calls) if quota > 0 else -1  # -1 for unlimited

            return UsageStats(
                current_period_usage=total_calls,
                quota_remaining=quota_remaining,
                total_calls_this_month=total_calls,
                average_processing_time_ms=avg_processing_time,
                total_cost_this_month=total_cost,
                ai_optimization_stats=ai_stats,
            )

    def get_profile_recommendations(self, profile: AIProfile) -> list[str]:
        """Get recommendations for when to use each AI profile"""
        recommendations = {
            AIProfile.COMPLIANCE: [
                "Policy analysis",
                "Regulatory compliance",
                "Audit preparations",
                "Risk documentation",
            ],
            AIProfile.CREATIVE: [
                "Innovation workshops",
                "Problem solving",
                "Strategic planning",
                "Change management",
            ],
            AIProfile.BALANCED: [
                "General analysis",
                "Team discussions",
                "Regular reporting",
                "Training materials",
            ],
            AIProfile.CODE_GENERATION: [
                "Automation scripts",
                "Technical documentation",
                "System integration",
                "Development tasks",
            ],
            AIProfile.CODE_COMMENTS: [
                "Code reviews",
                "Documentation updates",
                "Technical guides",
                "API documentation",
            ],
            AIProfile.DATA_ANALYSIS: [
                "Financial reporting",
                "Performance metrics",
                "Trend analysis",
                "Business intelligence",
            ],
            AIProfile.EXPLORATORY: [
                "Research projects",
                "Pilot programs",
                "Technology evaluation",
                "Innovation labs",
            ],
            AIProfile.CHATBOT: [
                "Customer support",
                "Internal help desk",
                "Training assistance",
                "FAQ generation",
            ],
            AIProfile.GOVERNANCE: [
                "Board reporting",
                "Policy development",
                "Compliance monitoring",
                "Executive summaries",
            ],
            AIProfile.RISK_ASSESSMENT: [
                "Security audits",
                "Financial risk analysis",
                "Operational risk",
                "Regulatory compliance",
            ],
        }
        return recommendations.get(profile, ["General use cases"])

    async def perform_optimized_governance_analysis(
        self, request: GovernanceRequest, ai_settings: AIOptimizationSettings
    ) -> dict[str, Any]:
        """Perform governance analysis using optimized AI parameters"""

        # Build analysis prompt
        prompt = f"""
        Analyze the following content for governance compliance:

        Content: {request.content}

        Compliance Frameworks: {", ".join(request.compliance_frameworks)}

        Please provide:
        1. Risk assessment score (0-100, where 100 is highest risk)
        2. Compliance status (compliant/non-compliant/needs-review)
        3. Specific findings and recommendations

        Focus on practical, actionable insights for enterprise governance.
        """

        # Use AI optimizer to generate analysis
        if ai_settings.custom_system_prompt:
            system_prompt = ai_settings.custom_system_prompt
        else:
            system_prompt = "You are an expert enterprise governance analyst with deep knowledge of compliance frameworks, risk management, and regulatory requirements."

        # Create custom profile if overrides are provided
        if (
            ai_settings.temperature is not None
            or ai_settings.top_p is not None
            or ai_settings.max_tokens is not None
        ):
            base_profile = self.openai_optimizer.get_profile(ai_settings.profile)
            custom_profile = self.openai_optimizer.create_custom_profile(
                name=f"Custom_{ai_settings.profile}",
                description=f"Customized version of {ai_settings.profile} profile",
                temperature=ai_settings.temperature or base_profile.temperature,
                top_p=ai_settings.top_p or base_profile.top_p,
                max_tokens=ai_settings.max_tokens or base_profile.max_tokens,
            )

            result = self.openai_optimizer.optimize_completion(
                prompt=prompt, profile=custom_profile, system_prompt=system_prompt
            )
        else:
            # Use task-based optimization
            result = self.openai_optimizer.optimize_governance_task(
                task_type=request.task_type,
                content=request.content,
                context=f"Frameworks: {', '.join(request.compliance_frameworks)}",
            )

        # Parse the AI response to extract structured data
        analysis_content = result["content"]

        # Simple parsing - in production, you'd want more sophisticated parsing
        risk_score = 50.0  # Default medium risk
        compliance_status = "needs-review"  # Default status

        # Try to extract risk score from response
        if "risk" in analysis_content.lower():
            import re

            risk_matches = re.findall(r"risk.*?(\d+)", analysis_content.lower())
            if risk_matches:
                risk_score = float(risk_matches[0])

        # Try to extract compliance status
        content_lower = analysis_content.lower()
        if "compliant" in content_lower and "non-compliant" not in content_lower:
            compliance_status = "compliant"
        elif "non-compliant" in content_lower:
            compliance_status = "non-compliant"

        # Extract findings (split by numbered points or paragraphs)
        findings = [
            {
                "type": "analysis",
                "description": (
                    analysis_content[:500] + "..."
                    if len(analysis_content) > 500
                    else analysis_content
                ),
            },
            {
                "type": "recommendation",
                "description": "Review AI-generated analysis for accuracy and completeness",
            },
        ]

        return {
            "risk_score": risk_score,
            "compliance_status": compliance_status,
            "findings": findings,
            "tokens_used": result["usage"]["total_tokens"],
            "ai_profile_used": result["profile_used"],
            "ai_parameters": result["parameters_used"],
        }


# Create global API instance
api_instance = EQ12EnterpriseAPI()
app = api_instance.app

# For running with uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
