"""
OpenAI Event Handlers
====================

Processes OpenAI webhook events and routes to appropriate actions.
"""

import logging

from .budget_guard import BudgetGuard
from .config import get_config
from .notifiers import NotificationManager

logger = logging.getLogger(__name__)


class OpenAIEventHandler:
    """Handles OpenAI webhook events"""

    def __init__(self):
        self.config = get_config()
        self.notifier = NotificationManager()

        # Try to get budget guard for cost tracking
        try:
            self.budget_guard = BudgetGuard()
        except Exception as e:
            logger.warning(f"Budget guard not available: {e}")
            self.budget_guard = None

    async def handle_event(self, event):
        """Route webhook event to appropriate handler"""
        try:
            event_type = event.type

            logger.info(f"Processing OpenAI event: {event_type} ({event.id})")

            # Route based on event type
            if event_type == "job.completed":
                await self.handle_job_completed(event)
            elif event_type == "job.failed":
                await self.handle_job_failed(event)
            elif event_type == "rate_limit.warning":
                await self.handle_rate_limit_warning(event)
            elif event_type == "billing.updated":
                await self.handle_billing_updated(event)
            elif event_type == "model.deprecated":
                await self.handle_model_deprecated(event)
            else:
                logger.info(f"Unhandled event type: {event_type}")

        except Exception as e:
            logger.error(f"Error handling event {event.id}: {e}")

    async def handle_job_completed(self, event):
        """Handle completed job events"""
        data = event.data

        # Extract usage information if available
        usage = data.get("usage", {})
        model = data.get("model", "unknown")

        if usage and self.budget_guard:
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            # Record usage for budget tracking
            self.budget_guard.record_usage(
                model=model, input_tokens=input_tokens, output_tokens=output_tokens
            )

        logger.debug(f"Job completed: {model} (tokens: {usage})")

    async def handle_job_failed(self, event):
        """Handle failed job events"""
        data = event.data
        error = data.get("error", {})

        # Send notification for job failures
        await self.notifier.send_alert(
            title="OpenAI Job Failed",
            message=f"Job {event.id} failed: {error.get('message', 'Unknown error')}",
            priority="high",
            event_data=data,
        )

    async def handle_rate_limit_warning(self, event):
        """Handle rate limit warnings"""
        data = event.data

        message = (
            f"Rate limit warning for {data.get('model', 'unknown')}\n"
            f"Current usage: {data.get('current_usage', 'N/A')}\n"
            f"Limit: {data.get('limit', 'N/A')}"
        )

        await self.notifier.send_alert(
            title="OpenAI Rate Limit Warning", message=message, priority="medium", event_data=data
        )

    async def handle_billing_updated(self, event):
        """Handle billing update events"""
        data = event.data

        # Check if we're approaching budget limits
        current_usage = data.get("current_usage", 0)
        limit = data.get("limit", 0)

        if limit > 0:
            usage_percent = (current_usage / limit) * 100

            if usage_percent >= 90:
                await self.notifier.send_alert(
                    title="OpenAI Billing Alert",
                    message=f"Usage at {usage_percent:.1f}% of limit (${current_usage:.2f}/${limit:.2f})",
                    priority="high",
                    event_data=data,
                )
            elif usage_percent >= 70:
                await self.notifier.send_alert(
                    title="OpenAI Usage Warning",
                    message=f"Usage at {usage_percent:.1f}% of limit (${current_usage:.2f}/${limit:.2f})",
                    priority="medium",
                    event_data=data,
                )

    async def handle_model_deprecated(self, event):
        """Handle model deprecation events"""
        data = event.data
        model = data.get("model", "unknown")
        sunset_date = data.get("sunset_date", "unknown")

        message = (
            f"Model {model} has been deprecated.\n"
            f"Sunset date: {sunset_date}\n"
            f"Please update your model policy configuration."
        )

        await self.notifier.send_alert(
            title="OpenAI Model Deprecated", message=message, priority="high", event_data=data
        )

        # TODO: Optionally create GitHub issue to update model policy
