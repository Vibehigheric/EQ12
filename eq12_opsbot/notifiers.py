"""
Notification Manager
==================

Handles Slack, Teams, and Telegram notifications with structured messages.
"""

import asyncio
import logging
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None

from .config import get_config

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages notifications across multiple channels"""

    def __init__(self):
        self.config = get_config()

    async def send_alert(
        self,
        title: str,
        message: str,
        priority: str = "medium",
        event_data: dict[str, Any] | None = None,
    ):
        """Send alert to all configured channels"""
        if not self.config.notifications_enabled:
            logger.debug("Notifications disabled, skipping alert")
            return

        # Send to all channels concurrently
        tasks = []

        if self.config.slack_webhook_url:
            tasks.append(self.send_slack(title, message, priority))

        if self.config.teams_webhook_url:
            tasks.append(self.send_teams(title, message, priority))

        if self.config.telegram_bot_token and self.config.telegram_chat_id:
            tasks.append(self.send_telegram(title, message, priority))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_slack(self, title: str, message: str, priority: str):
        """Send Slack notification"""
        if not httpx:
            logger.warning("httpx not available for Slack notifications")
            return

        color = {"high": "#ff0000", "medium": "#ffaa00", "low": "#00ff00"}.get(priority, "#cccccc")
        emoji = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}.get(priority, "🤖")

        payload = {
            "text": f"{emoji} EQ12 OpsBot Alert",
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "text": message,
                    "footer": "EQ12 OpsBot",
                    "ts": int(asyncio.get_event_loop().time()),
                }
            ],
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.slack_webhook_url, json=payload, timeout=10
                )

                if response.status_code == 200:
                    logger.debug("Slack notification sent successfully")
                else:
                    logger.warning(f"Slack notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")

    async def send_teams(self, title: str, message: str, priority: str):
        """Send Teams notification"""
        if not httpx:
            logger.warning("httpx not available for Teams notifications")
            return

        color = {"high": "ff0000", "medium": "ffaa00", "low": "00ff00"}.get(priority, "cccccc")

        payload = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": color,
            "summary": title,
            "sections": [
                {
                    "activityTitle": title,
                    "activitySubtitle": "EQ12 OpsBot Alert",
                    "text": message,
                    "markdown": True,
                }
            ],
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.config.teams_webhook_url, json=payload, timeout=10
                )

                if response.status_code == 200:
                    logger.debug("Teams notification sent successfully")
                else:
                    logger.warning(f"Teams notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Teams notification: {e}")

    async def send_telegram(self, title: str, message: str, priority: str):
        """Send Telegram notification"""
        if not httpx:
            logger.warning("httpx not available for Telegram notifications")
            return

        emoji = {"high": "🚨", "medium": "⚠️", "low": "ℹ️"}.get(priority, "🤖")
        text = f"{emoji} *{title}*\n\n{message}\n\n_EQ12 OpsBot_"

        url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
        payload = {"chat_id": self.config.telegram_chat_id, "text": text, "parse_mode": "Markdown"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)

                if response.status_code == 200:
                    logger.debug("Telegram notification sent successfully")
                else:
                    logger.warning(f"Telegram notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
