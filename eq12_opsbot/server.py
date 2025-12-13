"""
EQ12 OpsBot FastAPI Server
==========================

Production webhook server with HMAC verification, idempotency, and health monitoring.
Handles OpenAI webhook events and provides system status endpoint.
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import UTC, datetime
from typing import Any

from cachetools import TTLCache
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .budget_guard import BudgetGuard
from .config import get_config
from .handlers_openai import OpenAIEventHandler
from .model_policy import ModelPolicy
from .rate_limits import RateLimiter

logger = logging.getLogger(__name__)

# Global instances
event_handler = None
budget_guard = None
rate_limiter = None
model_policy = None

# Idempotency cache (event_id -> timestamp)
idempotency_cache = TTLCache(maxsize=1000, ttl=600)  # 10 minutes TTL

# Application startup time
startup_time = datetime.now(UTC)


class WebhookEvent(BaseModel):
    """OpenAI webhook event model"""

    id: str
    type: str
    created_at: int
    data: dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    uptime_seconds: int
    timestamp: str
    config_summary: dict[str, Any]
    budget_status: dict[str, Any] | None = None
    rate_limit_status: dict[str, Any] | None = None
    model_policy_status: dict[str, Any] | None = None
    last_webhook_event: str | None = None
    cache_stats: dict[str, int]


def verify_webhook_signature(request: Request, body: bytes) -> bool:
    """
    Verify OpenAI webhook signature using HMAC SHA-256

    Expected header format: OpenAI-Signature: t=<timestamp>,v1=<hex_signature>
    """
    config = get_config()

    if not config.openai_webhook_secret:
        if config.demo_mode:
            logger.warning("Demo mode: skipping webhook signature verification")
            return True
        logger.error("OpenAI webhook secret not configured")
        return False

    signature_header = request.headers.get("OpenAI-Signature")
    if not signature_header:
        logger.error("Missing OpenAI-Signature header")
        return False

    try:
        # Parse signature header: t=timestamp,v1=signature
        parts = dict(part.split("=", 1) for part in signature_header.split(","))
        timestamp_str = parts.get("t")
        signature = parts.get("v1")

        if not timestamp_str or not signature:
            logger.error("Invalid signature header format")
            return False

        # Check timestamp skew (max 5 minutes)
        webhook_timestamp = int(timestamp_str)
        current_timestamp = int(time.time())
        if abs(current_timestamp - webhook_timestamp) > 300:  # 5 minutes
            logger.error(
                f"Webhook timestamp skew too large: {abs(current_timestamp - webhook_timestamp)}s"
            )
            return False

        # Verify HMAC
        expected_signature = hmac.new(
            config.openai_webhook_secret.encode(), body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            logger.error("Webhook signature verification failed")
            return False

        return True

    except (ValueError, KeyError) as e:
        logger.error(f"Signature verification error: {e}")
        return False


def is_duplicate_event(event_id: str) -> bool:
    """Check if event was already processed (idempotency)"""
    if event_id in idempotency_cache:
        logger.info(f"Duplicate event ignored: {event_id}")
        return True

    # Mark as processed
    idempotency_cache[event_id] = time.time()
    return False


def log_webhook_event(event: WebhookEvent):
    """Log webhook event to daily JSONL file"""
    config = get_config()

    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_id": event.id,
        "event_type": event.type,
        "created_at": event.created_at,
        "data": event.data,
    }

    # Daily log file
    date_str = datetime.now().strftime("%Y%m%d")
    log_file = config.log_directory / "webhooks" / f"openai_{date_str}.jsonl"

    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to log webhook event: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    config = get_config()

    app = FastAPI(
        title="EQ12 OpsBot",
        description="Production webhook & automation suite for EQ12 platform",
        version="1.0.0",
        docs_url="/docs" if not config.demo_mode else None,
        redoc_url="/redoc" if not config.demo_mode else None,
    )

    # Initialize components
    global event_handler, budget_guard, rate_limiter, model_policy

    try:
        event_handler = OpenAIEventHandler()

        if config.enable_budget_guard:
            budget_guard = BudgetGuard()

        if config.enable_rate_limits:
            rate_limiter = RateLimiter()

        if config.enable_model_policy:
            model_policy = ModelPolicy()

        logger.info("EQ12 OpsBot components initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        if not config.demo_mode:
            raise

    @app.post("/webhooks/openai")
    async def handle_openai_webhook(request: Request, background_tasks: BackgroundTasks):
        """Handle OpenAI webhook events with HMAC verification and idempotency"""
        try:
            # Get raw body for signature verification
            body = await request.body()

            # Verify webhook signature
            if not verify_webhook_signature(request, body):
                logger.warning("Webhook signature verification failed")
                raise HTTPException(status_code=401, detail="Invalid signature")

            # Parse event
            try:
                event_data = json.loads(body)
                event = WebhookEvent(**event_data)
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Invalid webhook payload: {e}")
                raise HTTPException(status_code=400, detail="Invalid JSON payload")

            # Check for duplicate (idempotency)
            if is_duplicate_event(event.id):
                return JSONResponse(
                    status_code=200, content={"status": "ok", "message": "Event already processed"}
                )

            # Log event
            log_webhook_event(event)

            # Process event in background
            if event_handler:
                background_tasks.add_task(event_handler.handle_event, event)

            logger.info(f"Webhook event processed: {event.type} ({event.id})")

            return JSONResponse(
                status_code=200,
                content={
                    "status": "ok",
                    "event_id": event.id,
                    "event_type": event.type,
                    "processed_at": datetime.now(UTC).isoformat(),
                },
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/healthz", response_model=HealthResponse)
    async def health_check():
        """System health and status endpoint"""
        config = get_config()
        current_time = datetime.now(UTC)
        uptime_seconds = int((current_time - startup_time).total_seconds())

        # Get component status
        budget_status = None
        if budget_guard:
            budget_status = budget_guard.get_status()

        rate_limit_status = None
        if rate_limiter:
            rate_limit_status = rate_limiter.get_status()

        model_policy_status = None
        if model_policy:
            model_policy_status = model_policy.get_status()

        # Get last webhook event time
        last_webhook_event = None
        webhook_logs = config.log_directory / "webhooks"
        if webhook_logs.exists():
            try:
                # Get most recent log file
                log_files = sorted(webhook_logs.glob("openai_*.jsonl"), reverse=True)
                if log_files:
                    with open(log_files[0], encoding="utf-8") as f:
                        lines = f.readlines()
                        if lines:
                            last_entry = json.loads(lines[-1])
                            last_webhook_event = last_entry.get("timestamp")
            except Exception as e:
                logger.warning(f"Error reading webhook logs: {e}")

        # Determine overall status
        status = "healthy"
        if config.demo_mode:
            status = "demo"
        elif not config.is_production_ready:
            status = "not_configured"
        elif budget_guard and budget_status.get("circuit_breaker_active"):
            status = "budget_exceeded"

        return HealthResponse(
            status=status,
            uptime_seconds=uptime_seconds,
            timestamp=current_time.isoformat(),
            config_summary=config.get_config_summary(),
            budget_status=budget_status,
            rate_limit_status=rate_limit_status,
            model_policy_status=model_policy_status,
            last_webhook_event=last_webhook_event,
            cache_stats={
                "idempotency_cache_size": len(idempotency_cache),
                "idempotency_cache_maxsize": idempotency_cache.maxsize,
            },
        )

    @app.get("/")
    async def root():
        """Root endpoint with basic info"""
        config = get_config()
        return {
            "name": "EQ12 OpsBot",
            "version": "1.0.0",
            "status": "running",
            "demo_mode": config.demo_mode,
            "endpoints": {
                "webhook": "/webhooks/openai",
                "health": "/healthz",
                "docs": "/docs" if not config.demo_mode else "disabled",
            },
        }

    return app
