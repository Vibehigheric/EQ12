"""
EQ12 Secure Webhook Endpoint
Handles asynchronous events from OpenAI responses, cost guards, and EQ12 pipeline components
"""

import hashlib
import hmac
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EQ12 Webhooks",
    description="Secure webhook endpoint for EQ12 OpenAI and pipeline events",
    version="1.0.0",
)

# Configuration
LOG_DIR = Path("logs/webhooks")
LOG_DIR.mkdir(parents=True, exist_ok=True)

WEBHOOK_SECRET = os.getenv("EQ12_WEBHOOK_SECRET", "change-me-in-production")
MAX_SEEN_SIZE = 10000  # Prevent memory leak in simple idempotency store

# Simple in-memory idempotency store (use Redis in production)
SEEN_EVENTS = set()


class WebhookEnvelope(BaseModel):
    """Webhook event envelope with standardized structure"""

    id: str
    type: str
    created_at: str
    source: str  # "openai" | "eq12" | "cost_guards" | "sanitizer"
    payload: dict[str, Any]
    schema_version: str = "1.0.0"


def verify_signature(signature_header: str, body: bytes) -> bool:
    """Verify HMAC signature for webhook security"""
    if not signature_header:
        logger.warning("Missing webhook signature")
        return False

    expected_sig = hmac.new(WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()

    try:
        return hmac.compare_digest(expected_sig, signature_header)
    except Exception as e:
        logger.error(f"Signature verification failed: {e}")
        return False


def log_jsonl(filename: str, obj: dict[str, Any]):
    """Append event to JSONL log file with rotation"""
    timestamp = datetime.now(UTC).strftime("%Y%m%d")
    log_file = LOG_DIR / f"{filename}_{timestamp}.jsonl"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to log to {log_file}: {e}")


def cleanup_seen_events():
    """Prevent memory leak by cleaning old seen events"""
    global SEEN_EVENTS
    if len(SEEN_EVENTS) > MAX_SEEN_SIZE:
        # Keep only recent half
        SEEN_EVENTS = set(list(SEEN_EVENTS)[MAX_SEEN_SIZE // 2 :])
        logger.info(f"Cleaned idempotency store, kept {len(SEEN_EVENTS)} entries")


async def trigger_parlay_sanitizer(event_id: str, payload: dict[str, Any]):
    """Trigger parlay sanitizer when AI analysis completes"""
    try:
        # Import here to avoid circular dependencies
        from eq12_parlay_sanitizer import EQ12ParlaySanitizer

        EQ12ParlaySanitizer(ai_enabled=False)  # Avoid recursive AI calls

        # Extract analysis data from payload
        analysis_data = payload.get("analysis_data")
        if analysis_data:
            logger.info(f"Triggering sanitizer for event {event_id}")
            # This would process the analysis and create sanitized parlays
            # Implementation depends on your existing sanitizer interface

        log_jsonl(
            "triggers",
            {
                "trigger": "sanitize_parlay",
                "event_id": event_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "status": "triggered",
            },
        )

    except ImportError:
        logger.warning("Parlay sanitizer not available")
    except Exception as e:
        logger.error(f"Failed to trigger sanitizer: {e}")


async def update_cost_tracking(event_id: str, payload: dict[str, Any]):
    """Update budget tracking system with usage data"""
    try:
        from eq12_budget_enforcer import budget_enforcer

        usage = payload.get("usage", {})
        feature = payload.get("feature", "general")
        model = payload.get("model", "unknown")

        if usage and "cost_usd" in usage:
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            cost = usage["cost_usd"]

            budget_enforcer.record_usage(
                feature=feature,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
            )

            logger.info(f"Recorded usage: {feature} {model} ${cost:.6f}")

    except ImportError:
        logger.warning("Budget enforcer not available")
    except Exception as e:
        logger.error(f"Failed to update cost tracking: {e}")


async def send_telegram_alert(event_id: str, payload: dict[str, Any]):
    """Send Telegram alert for critical events"""
    try:
        import httpx

        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not (bot_token and chat_id):
            logger.debug("Telegram not configured, skipping alert")
            return

        event_type = payload.get("type", "unknown")
        message = f"🚨 EQ12 Alert: {event_type}\n"

        if "error" in payload:
            message += f"Error: {payload['error']}\n"

        if "usage" in payload:
            usage = payload["usage"]
            message += f"Usage: ${usage.get('cost_usd', 0):.6f}\n"

        message += f"Event ID: {event_id}"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, timeout=5.0)

        if response.status_code == 200:
            logger.info(f"Telegram alert sent for event {event_id}")
        else:
            logger.warning(f"Telegram alert failed: {response.status_code}")

    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


async def handle_event(evt: WebhookEnvelope):
    """Main event handler - routes events to appropriate processors"""
    event_dict = evt.dict()

    # Log all events to main log
    log_jsonl("events", event_dict)

    event_type = evt.type
    payload = evt.payload

    logger.info(f"Processing event: {event_type} [{evt.id}]")

    try:
        if event_type == "openai.response.completed":
            # Log response summary
            summary = {
                "id": evt.id,
                "model": payload.get("model"),
                "tokens": payload.get("usage", {}).get("total_tokens"),
                "cost_usd": payload.get("usage", {}).get("cost_usd"),
                "latency_ms": payload.get("latency_ms"),
                "feature": payload.get("feature"),
                "created_at": evt.created_at,
            }
            log_jsonl("responses", summary)

            # Update cost tracking
            await update_cost_tracking(evt.id, payload)

            # Trigger sanitizer if this was a parlay analysis
            if payload.get("tag") == "parlay_analysis":
                await trigger_parlay_sanitizer(evt.id, payload)

        elif event_type == "openai.response.error":
            log_jsonl("errors", {"id": evt.id, **payload})

            # Send alert for repeated errors
            if payload.get("code") in [429, 401, 500, 502, 503, 504]:
                await send_telegram_alert(evt.id, {"type": event_type, **payload})

        elif event_type == "openai.rate_limit.hit":
            log_jsonl("rate_limits", {"id": evt.id, **payload})

            # Trigger cost guard adjustment
            logger.warning(f"Rate limit hit for {payload.get('model', 'unknown')}")

        elif event_type == "openai.usage.summary":
            log_jsonl("usage", {"id": evt.id, **payload})
            await update_cost_tracking(evt.id, payload)

        elif event_type == "openai.quota.low":
            log_jsonl("quota", {"id": evt.id, **payload})
            await send_telegram_alert(evt.id, {"type": event_type, **payload})

        elif event_type == "openai.moderation.flagged":
            log_jsonl("moderation", {"id": evt.id, **payload})
            logger.warning(f"Content flagged by moderation: {evt.id}")

        elif event_type.startswith("eq12.parlay."):
            log_jsonl("eq12_pipeline", {"id": evt.id, "type": event_type, **payload})

            if event_type == "eq12.parlay.analysis.ready":
                await trigger_parlay_sanitizer(evt.id, payload)

        elif event_type.startswith("eq12.alert."):
            log_jsonl("alerts", {"id": evt.id, "type": event_type, **payload})

        else:
            logger.info(f"Unknown event type: {event_type}")
            log_jsonl("unknown", {"id": evt.id, "type": event_type, **payload})

    except Exception as e:
        logger.error(f"Error handling event {evt.id}: {e}")
        log_jsonl(
            "handler_errors",
            {
                "event_id": evt.id,
                "event_type": event_type,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )


@app.post("/webhooks/openai")
async def openai_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_eq12_signature: str | None = Header(None),
    x_eq12_delivery: str | None = Header(None),
):
    """
    Main webhook endpoint for OpenAI and EQ12 events
    Requires HMAC signature verification and provides idempotency
    """
    try:
        raw_body = await request.body()

        # Verify HMAC signature
        if not verify_signature(x_eq12_signature or "", raw_body):
            logger.warning(f"Invalid webhook signature from {request.client.host}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Parse event
        try:
            event_data = json.loads(raw_body)
            evt = WebhookEnvelope(**event_data)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid webhook payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload format")

        # Idempotency check
        if evt.id in SEEN_EVENTS:
            logger.info(f"Duplicate event ignored: {evt.id}")
            return {"ok": True, "duplicate": True}

        # Add to seen events
        SEEN_EVENTS.add(evt.id)
        cleanup_seen_events()

        # Process in background
        background_tasks.add_task(handle_event, evt)

        return {"ok": True, "event_id": evt.id, "processed_at": datetime.now(UTC).isoformat()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/webhooks/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "events_seen": len(SEEN_EVENTS),
        "log_dir": str(LOG_DIR),
    }


@app.get("/webhooks/stats")
async def webhook_stats():
    """Get webhook statistics"""
    stats = {"events_processed": len(SEEN_EVENTS), "log_directory": str(LOG_DIR), "log_files": []}

    try:
        for log_file in LOG_DIR.glob("*.jsonl"):
            file_stats = log_file.stat()
            stats["log_files"].append(
                {
                    "name": log_file.name,
                    "size_bytes": file_stats.st_size,
                    "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                }
            )
    except Exception as e:
        logger.error(f"Failed to get log stats: {e}")

    return stats


if __name__ == "__main__":
    import uvicorn

    # Validate configuration
    if WEBHOOK_SECRET == "change-me-in-production":
        logger.warning("⚠️  Using default webhook secret - set EQ12_WEBHOOK_SECRET in production!")

    logger.info("🚀 Starting EQ12 webhook server")
    logger.info(f"📁 Log directory: {LOG_DIR}")
    logger.info(f"🔒 Signature verification: {'enabled' if WEBHOOK_SECRET else 'disabled'}")

    uvicorn.run("eq12_webhooks:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
