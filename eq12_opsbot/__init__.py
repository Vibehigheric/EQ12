"""
EQ12 OpsBot - Production Webhook & Automation Suite
==================================================

Comprehensive automation bot for EQ12 platform including:
- OpenAI webhook handling with HMAC verification
- Budget & rate-limit guardrails with circuit breakers
- Model allow/deny policy enforcement
- OpenAI Community forum monitoring
- Automated CI tasks and health monitoring
- First-run self-initialization

Usage:
    python -m eq12_opsbot.main run       # Start webhook server + scheduler
    python -m eq12_opsbot.main doctor    # Health checks and diagnostics
    python -m eq12_opsbot.main limits sync    # Sync rate limit configuration
    python -m eq12_opsbot.main model-policy enforce    # Enforce model policies
"""

__version__ = "1.0.0"
__author__ = "EQ12 Platform"

# Export main components for easy importing
from .budget_guard import BudgetGuard
from .config import OpsConfig
from .model_policy import ModelPolicy
from .rate_limits import RateLimiter
from .server import create_app

__all__ = ["BudgetGuard", "ModelPolicy", "OpsConfig", "RateLimiter", "create_app"]
