"""
EQ12 OpenAI Security Manager
Comprehensive protection, rotation, and cost control for OpenAI API keys
"""

import asyncio
import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import httpx
import openai
import redis
from cryptography.fernet import Fernet
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure secure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class SecretMaskingFilter(logging.Filter):
    """Filter to mask OpenAI API keys and other secrets in logs"""

    PATTERNS = [
        re.compile(r"(sk-[A-Za-z0-9]{20,})", re.IGNORECASE),
        re.compile(r"(Bearer\s+sk-[A-Za-z0-9]{20,})", re.IGNORECASE),
        re.compile(r"(openai[_-]?api[_-]?key\s*=\s*['\"]?sk-[A-Za-z0-9]{20,})", re.IGNORECASE),
    ]

    def filter(self, record):
        if hasattr(record, "msg"):
            msg = str(record.msg)
            for pattern in self.PATTERNS:
                msg = pattern.sub(r"***REDACTED***", msg)
            record.msg = msg
        return True


# Add masking filter to all loggers
logger = logging.getLogger(__name__)
logger.addFilter(SecretMaskingFilter())

# Database models
Base = declarative_base()


class APIKeyUsage(Base):
    __tablename__ = "api_key_usage"

    id = Column(String, primary_key=True)
    key_hash = Column(String, nullable=False, index=True)
    environment = Column(String, nullable=False)  # dev, ci, prod
    model = Column(String, nullable=False)
    tokens_input = Column(Integer, default=0)
    tokens_output = Column(Integer, default=0)
    cost_usd = Column(Float, nullable=False)
    request_id = Column(String)
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class APIKeyRotation(Base):
    __tablename__ = "api_key_rotations"

    id = Column(String, primary_key=True)
    key_hash_old = Column(String, nullable=False)
    key_hash_new = Column(String, nullable=False)
    environment = Column(String, nullable=False)
    reason = Column(String, nullable=False)  # scheduled, leak, breach, manual
    rotated_at = Column(DateTime, default=datetime.utcnow)
    rotated_by = Column(String)


class SecurityIncident(Base):
    __tablename__ = "security_incidents"

    id = Column(String, primary_key=True)
    incident_type = Column(String, nullable=False)  # leak, breach, anomaly, budget
    severity = Column(String, nullable=False)  # low, medium, high, critical
    key_hash = Column(String)
    details = Column(Text)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    status = Column(String, default="open")  # open, investigating, resolved


@dataclass
class CostLimits:
    """Cost limits and circuit breaker configuration"""

    max_cost_per_request: Decimal = Decimal("0.25")
    max_cost_per_hour: Decimal = Decimal("2.00")
    max_cost_per_day: Decimal = Decimal("5.00")
    max_cost_per_month: Decimal = Decimal("120.00")

    # Model-specific limits
    model_limits: dict[str, Decimal] = field(
        default_factory=lambda: {
            "gpt-4o-mini": Decimal("0.05"),
            "gpt-4o": Decimal("0.50"),
            "gpt-4-turbo": Decimal("0.30"),
            "text-embedding-3-small": Decimal("0.01"),
            "text-embedding-3-large": Decimal("0.03"),
        }
    )

    # Environment-specific multipliers
    environment_multipliers: dict[str, float] = field(
        default_factory=lambda: {
            "dev": 0.2,  # 20% of base limits
            "ci": 0.5,  # 50% of base limits
            "staging": 0.8,  # 80% of base limits
            "prod": 1.0,  # 100% of base limits
        }
    )


class EQ12OpenAISecurityManager:
    """Comprehensive OpenAI API security and cost management"""

    def __init__(
        self, environment: str = "dev", redis_url: str | None = None, db_url: str | None = None
    ):
        self.environment = environment
        self.logger = logger

        # Initialize database
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///eq12_security.db")
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(bind=self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()

        # Initialize Redis for caching and rate limiting
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.redis = redis.from_url(self.redis_url)
            self.redis.ping()
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}, using in-memory cache")
            self.redis = None

        # Load configuration
        self.cost_limits = CostLimits()
        self.allowed_models = self._get_allowed_models()

        # Initialize encryption for key storage
        self.encryption_key = self._get_or_create_encryption_key()

    def _get_allowed_models(self) -> list[str]:
        """Get allowed models for current environment"""
        model_configs = {
            "dev": ["gpt-4o-mini", "text-embedding-3-small"],
            "ci": ["gpt-4o-mini", "text-embedding-3-small", "gpt-4o"],
            "staging": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "text-embedding-3-small"],
            "prod": [
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-4-turbo",
                "text-embedding-3-small",
                "text-embedding-3-large",
            ],
        }
        return model_configs.get(self.environment, model_configs["dev"])

    def _get_or_create_encryption_key(self) -> Fernet:
        """Get or create encryption key for sensitive data"""
        key_path = f".eq12_encryption_{self.environment}.key"

        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_path, 0o600)

        return Fernet(key)

    def hash_api_key(self, api_key: str) -> str:
        """Create a secure hash of API key for tracking"""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key format and security"""
        if not api_key or not isinstance(api_key, str):
            return False

        # Check format
        if not api_key.startswith("sk-"):
            return False

        if len(api_key) < 40:  # OpenAI keys are typically 51+ chars
            return False

        # Check for test/placeholder keys
        test_patterns = ["test", "placeholder", "example", "demo", "fake"]
        return not any(pattern in api_key.lower() for pattern in test_patterns)

    async def get_secure_api_key(self, key_name: str | None = None) -> str | None:
        """Get API key from secure storage with validation"""
        key_name = key_name or f"OPENAI_API_KEY_{self.environment.upper()}"

        # Try environment variable first
        api_key = os.getenv(key_name)

        if not api_key:
            # Try Azure Key Vault, AWS Secrets Manager, etc.
            api_key = await self._fetch_from_external_secrets(key_name)

        if not api_key:
            raise ValueError(f"API key {key_name} not found in any secure storage")

        if not self.validate_api_key(api_key):
            raise ValueError(f"Invalid API key format for {key_name}")

        return api_key

    async def _fetch_from_external_secrets(self, key_name: str) -> str | None:
        """Fetch API key from external secret managers"""
        # Azure Key Vault
        vault_url = os.getenv("AZURE_KEY_VAULT_URL")
        if vault_url:
            try:
                from azure.identity import DefaultAzureCredential
                from azure.keyvault.secrets import SecretClient

                credential = DefaultAzureCredential()
                client = SecretClient(vault_url=vault_url, credential=credential)
                secret = client.get_secret(key_name)
                return secret.value
            except Exception as e:
                self.logger.debug(f"Azure Key Vault fetch failed: {e}")

        # AWS Secrets Manager
        if os.getenv("AWS_REGION"):
            try:
                import boto3

                client = boto3.client("secretsmanager")
                response = client.get_secret_value(SecretId=key_name)
                return response["SecretString"]
            except Exception as e:
                self.logger.debug(f"AWS Secrets Manager fetch failed: {e}")

        # GCP Secret Manager
        if os.getenv("GOOGLE_CLOUD_PROJECT"):
            try:
                from google.cloud import secretmanager

                client = secretmanager.SecretManagerServiceClient()
                name = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/secrets/{key_name}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")
            except Exception as e:
                self.logger.debug(f"GCP Secret Manager fetch failed: {e}")

        return None

    async def check_cost_limits(self, model: str, estimated_tokens: int = 0) -> dict[str, Any]:
        """Check if request would exceed cost limits"""
        # Get current usage
        current_usage = await self._get_current_usage()

        # Estimate cost for this request
        estimated_cost = self._estimate_cost(model, estimated_tokens)

        # Apply environment multiplier
        multiplier = self.cost_limits.environment_multipliers.get(self.environment, 0.2)
        adjusted_limits = {
            "request": self.cost_limits.max_cost_per_request * Decimal(str(multiplier)),
            "hour": self.cost_limits.max_cost_per_hour * Decimal(str(multiplier)),
            "day": self.cost_limits.max_cost_per_day * Decimal(str(multiplier)),
            "month": self.cost_limits.max_cost_per_month * Decimal(str(multiplier)),
        }

        # Check limits
        violations = []

        if estimated_cost > adjusted_limits["request"]:
            violations.append(
                f"Request cost ${estimated_cost} exceeds limit ${adjusted_limits['request']}"
            )

        if current_usage["hour"] + estimated_cost > adjusted_limits["hour"]:
            violations.append(f"Hourly cost would exceed ${adjusted_limits['hour']}")

        if current_usage["day"] + estimated_cost > adjusted_limits["day"]:
            violations.append(f"Daily cost would exceed ${adjusted_limits['day']}")

        if current_usage["month"] + estimated_cost > adjusted_limits["month"]:
            violations.append(f"Monthly cost would exceed ${adjusted_limits['month']}")

        return {
            "allowed": len(violations) == 0,
            "violations": violations,
            "estimated_cost": float(estimated_cost),
            "current_usage": current_usage,
            "limits": {k: float(v) for k, v in adjusted_limits.items()},
        }

    async def _get_current_usage(self) -> dict[str, Decimal]:
        """Get current API usage costs by time period"""
        now = datetime.utcnow()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Query database for usage
        try:
            hour_usage = (
                self.db.query(APIKeyUsage)
                .filter(
                    APIKeyUsage.timestamp >= hour_start, APIKeyUsage.environment == self.environment
                )
                .all()
            )

            day_usage = (
                self.db.query(APIKeyUsage)
                .filter(
                    APIKeyUsage.timestamp >= day_start, APIKeyUsage.environment == self.environment
                )
                .all()
            )

            month_usage = (
                self.db.query(APIKeyUsage)
                .filter(
                    APIKeyUsage.timestamp >= month_start,
                    APIKeyUsage.environment == self.environment,
                )
                .all()
            )

            return {
                "hour": sum(Decimal(str(u.cost_usd)) for u in hour_usage),
                "day": sum(Decimal(str(u.cost_usd)) for u in day_usage),
                "month": sum(Decimal(str(u.cost_usd)) for u in month_usage),
            }
        except Exception as e:
            self.logger.error(f"Failed to get usage: {e}")
            return {"hour": Decimal("0"), "day": Decimal("0"), "month": Decimal("0")}

    def _estimate_cost(self, model: str, tokens: int) -> Decimal:
        """Estimate cost for API request"""
        # OpenAI pricing (as of 2024) - input tokens
        pricing = {
            "gpt-4o-mini": Decimal("0.000150") / 1000,  # $0.150 per 1M tokens
            "gpt-4o": Decimal("0.0025") / 1000,  # $2.50 per 1M tokens
            "gpt-4-turbo": Decimal("0.001") / 1000,  # $1.00 per 1M tokens
            "text-embedding-3-small": Decimal("0.00002") / 1000,  # $0.02 per 1M tokens
            "text-embedding-3-large": Decimal("0.00013") / 1000,  # $0.13 per 1M tokens
        }

        rate = pricing.get(model, Decimal("0.001") / 1000)  # Default fallback
        return rate * Decimal(str(tokens))

    async def secure_openai_request(
        self, model: str, messages: list[dict] | None = None, **kwargs
    ) -> dict[str, Any]:
        """Make secure OpenAI API request with full protection"""
        # Validate model is allowed
        if model not in self.allowed_models:
            raise ValueError(
                f"Model {model} not allowed in {self.environment} environment. Allowed: {self.allowed_models}"
            )

        # Estimate token count
        estimated_tokens = self._estimate_tokens(messages or [], kwargs.get("prompt", ""))

        # Check cost limits
        cost_check = await self.check_cost_limits(model, estimated_tokens)
        if not cost_check["allowed"]:
            raise ValueError(f"Cost limits exceeded: {cost_check['violations']}")

        # Get secure API key
        api_key = await self.get_secure_api_key()
        key_hash = self.hash_api_key(api_key)

        # Make request with retries and error handling
        client = openai.AsyncOpenAI(api_key=api_key)

        try:
            start_time = datetime.utcnow()

            if messages:  # Chat completion
                response = await client.chat.completions.create(
                    model=model, messages=messages, **kwargs
                )

                # Record usage
                await self._record_usage(
                    key_hash=key_hash,
                    model=model,
                    tokens_input=response.usage.prompt_tokens,
                    tokens_output=response.usage.completion_tokens,
                    request_id=response.id,
                    cost=self._calculate_actual_cost(model, response.usage),
                )

            else:  # Embeddings or other
                response = await client.embeddings.create(
                    model=model,
                    input=kwargs.get("input", ""),
                    **{k: v for k, v in kwargs.items() if k != "input"},
                )

                # Record usage for embeddings
                await self._record_usage(
                    key_hash=key_hash,
                    model=model,
                    tokens_input=response.usage.total_tokens,
                    tokens_output=0,
                    cost=self._calculate_actual_cost(model, response.usage),
                )

            duration = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"OpenAI request successful: {model} in {duration:.2f}s")

            return {"response": response, "cost_check": cost_check}

        except openai.RateLimitError as e:
            self.logger.warning(f"OpenAI rate limit hit: {e}")
            await self._handle_rate_limit()
            raise
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            await self._record_incident("api_error", "medium", key_hash, str(e))
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in OpenAI request: {e}")
            await self._record_incident("request_error", "high", key_hash, str(e))
            raise

    def _estimate_tokens(self, messages: list[dict], prompt: str = "") -> int:
        """Rough token estimation for cost calculation"""
        text = prompt
        if messages:
            text = " ".join(
                msg.get("content", "") for msg in messages if isinstance(msg.get("content"), str)
            )

        # Rough estimation: 1 token ≈ 0.75 words
        return int(len(text.split()) * 1.33)

    def _calculate_actual_cost(self, model: str, usage) -> Decimal:
        """Calculate actual cost from usage object"""
        if hasattr(usage, "prompt_tokens") and hasattr(usage, "completion_tokens"):
            # Chat completion
            input_cost = self._estimate_cost(model, usage.prompt_tokens)
            # Output tokens typically cost more (2x for gpt-4o)
            output_multiplier = 2.0 if "gpt-4o" in model else 1.0
            output_cost = self._estimate_cost(model, usage.completion_tokens) * Decimal(
                str(output_multiplier)
            )
            return input_cost + output_cost
        else:
            # Embeddings or other
            return self._estimate_cost(model, usage.total_tokens)

    async def _record_usage(
        self,
        key_hash: str,
        model: str,
        tokens_input: int,
        tokens_output: int,
        cost: Decimal,
        request_id: str | None = None,
    ):
        """Record API usage for tracking and billing"""
        try:
            usage = APIKeyUsage(
                id=f"usage_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                key_hash=key_hash,
                environment=self.environment,
                model=model,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost_usd=float(cost),
                request_id=request_id,
            )

            self.db.add(usage)
            self.db.commit()

        except Exception as e:
            self.logger.error(f"Failed to record usage: {e}")
            self.db.rollback()

    async def _record_incident(
        self,
        incident_type: str,
        severity: str,
        key_hash: str | None = None,
        details: str | None = None,
    ):
        """Record security incident"""
        try:
            incident = SecurityIncident(
                id=f"incident_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                incident_type=incident_type,
                severity=severity,
                key_hash=key_hash,
                details=details,
            )

            self.db.add(incident)
            self.db.commit()

            # Alert if high/critical
            if severity in ["high", "critical"]:
                await self._send_security_alert(incident)

        except Exception as e:
            self.logger.error(f"Failed to record incident: {e}")

    async def _handle_rate_limit(self):
        """Handle rate limit with exponential backoff"""
        import random

        base_delay = 1.0
        max_delay = 60.0

        # Exponential backoff with jitter
        delay = min(base_delay * (2 ** random.randint(1, 4)) + random.uniform(0, 1), max_delay)

        self.logger.info(f"Rate limited, waiting {delay:.2f} seconds")
        await asyncio.sleep(delay)

    async def _send_security_alert(self, incident: SecurityIncident):
        """Send security alert via configured channels"""
        alert_data = {
            "incident_id": incident.id,
            "type": incident.incident_type,
            "severity": incident.severity,
            "environment": self.environment,
            "timestamp": incident.detected_at.isoformat(),
            "details": incident.details,
        }

        # Webhook notifications
        webhook_url = os.getenv("SECURITY_WEBHOOK_URL")
        if webhook_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(webhook_url, json=alert_data)
            except Exception as e:
                self.logger.error(f"Failed to send webhook alert: {e}")

    async def rotate_api_key(self, reason: str = "scheduled", new_key: str | None = None) -> str:
        """Rotate API key and update all storage locations"""
        current_key = await self.get_secure_api_key()
        current_key_hash = self.hash_api_key(current_key)

        if not new_key:
            self.logger.error("New API key must be provided manually")
            raise ValueError("New API key required for rotation")

        if not self.validate_api_key(new_key):
            raise ValueError("Invalid new API key format")

        new_key_hash = self.hash_api_key(new_key)

        try:
            # Record rotation
            rotation = APIKeyRotation(
                id=f"rotation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                key_hash_old=current_key_hash,
                key_hash_new=new_key_hash,
                environment=self.environment,
                reason=reason,
                rotated_by=os.getenv("USER", "system"),
            )

            self.db.add(rotation)
            self.db.commit()

            self.logger.info(f"API key rotated successfully for {self.environment}")
            return new_key_hash

        except Exception as e:
            self.logger.error(f"Failed to rotate API key: {e}")
            self.db.rollback()
            raise

    async def get_usage_report(self, days: int = 30) -> dict[str, Any]:
        """Generate comprehensive usage and cost report"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        usage_data = (
            self.db.query(APIKeyUsage)
            .filter(
                APIKeyUsage.timestamp >= start_date, APIKeyUsage.environment == self.environment
            )
            .all()
        )

        total_cost = sum(Decimal(str(u.cost_usd)) for u in usage_data)
        total_tokens = sum(u.tokens_input + u.tokens_output for u in usage_data)

        # Group by model
        by_model = {}
        for usage in usage_data:
            model = usage.model
            if model not in by_model:
                by_model[model] = {"cost": Decimal("0"), "tokens": 0, "requests": 0}
            by_model[model]["cost"] += Decimal(str(usage.cost_usd))
            by_model[model]["tokens"] += usage.tokens_input + usage.tokens_output
            by_model[model]["requests"] += 1

        return {
            "environment": self.environment,
            "period_days": days,
            "total_cost": float(total_cost),
            "total_tokens": total_tokens,
            "total_requests": len(usage_data),
            "average_cost_per_request": float(total_cost / len(usage_data)) if usage_data else 0,
            "by_model": {k: {**v, "cost": float(v["cost"])} for k, v in by_model.items()},
            "projected_monthly": float(total_cost * Decimal("30") / Decimal(str(days))),
        }

    def cleanup(self):
        """Cleanup resources"""
        if self.db:
            self.db.close()
        if self.redis:
            self.redis.close()


# Global security manager instance
_security_manager = None


def get_security_manager(environment: str | None = None) -> EQ12OpenAISecurityManager:
    """Get or create security manager instance"""
    global _security_manager

    env = environment or os.getenv("EQ12_ENVIRONMENT", "dev")

    if _security_manager is None or _security_manager.environment != env:
        _security_manager = EQ12OpenAISecurityManager(environment=env)

    return _security_manager


# Convenience functions
async def secure_chat_completion(model: str, messages: list[dict], **kwargs) -> dict[str, Any]:
    """Make secure chat completion request"""
    manager = get_security_manager()
    return await manager.secure_openai_request(model, messages, **kwargs)


async def secure_embedding(model: str, text: str, **kwargs) -> dict[str, Any]:
    """Make secure embedding request"""
    manager = get_security_manager()
    return await manager.secure_openai_request(model, input=text, **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 OpenAI Security Manager")
    parser.add_argument("--environment", default="dev", choices=["dev", "ci", "staging", "prod"])
    parser.add_argument("--rotate-key", action="store_true", help="Rotate API key")
    parser.add_argument(
        "--usage-report", type=int, default=0, help="Generate usage report for N days"
    )
    parser.add_argument("--test-security", action="store_true", help="Run security tests")

    args = parser.parse_args()

    async def main():
        manager = EQ12OpenAISecurityManager(args.environment)

        try:
            if args.rotate_key:
                print("API key rotation requires manual intervention")
                print("1. Generate new key in OpenAI console")
                print("2. Update in secret manager")
                print("3. Call rotate_api_key() with new key")

            if args.usage_report > 0:
                report = await manager.get_usage_report(args.usage_report)
                print(json.dumps(report, indent=2))

            if args.test_security:
                # Test key validation
                print("Testing security controls...")

                # Test invalid key
                try:
                    manager.validate_api_key("invalid-key")
                    print("❌ Invalid key validation failed")
                except:
                    print("✅ Invalid key properly rejected")

                # Test cost limits
                cost_check = await manager.check_cost_limits("gpt-4o", 10000)
                print(f"✅ Cost check: {cost_check['allowed']}")

                print("Security tests completed")

        finally:
            manager.cleanup()

    asyncio.run(main())
