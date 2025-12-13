#!/usr/bin/env python3
"""
EQ12 Alerting System - Professional Sports Betting Notifications
Telegram and Slack integration with EV thresholds and rate limiting.

Sends compact parlay cards and real-time alerts using:
- pmpt_eq12_alert_copy_v1 for one-liner generation
- EV-based filtering and prioritization
- Rate limiting to prevent spam
- Professional formatting for mobile consumption
"""

from eq12_responses_client import EQ12ResponsesClient
from eq12_timezone import parse_commence_time, to_eastern_display, utc_now
import asyncio
import json
import logging
import os
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

import aiohttp

# Add EQ12 modules to path
sys.path.insert(0, str(Path(__file__).parent))


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@dataclass
class AlertConfig:
    """Configuration for EQ12 alerting system."""

    telegram_bot_token: str
    telegram_chat_id: str
    slack_webhook_url: str | None = None

    # EV thresholds for alerts
    min_parlay_ev: float = 0.12  # 12% minimum for parlay alerts
    high_ev_threshold: float = 0.18  # 18% for priority alerts
    critical_ev_threshold: float = 0.25  # 25% for immediate alerts

    # Rate limiting
    max_alerts_per_hour: int = 10
    max_same_game_alerts: int = 2
    cooldown_minutes: int = 15  # Between similar alerts

    # Formatting
    use_compact_cards: bool = True
    include_reasoning: bool = False
    max_legs_display: int = 4


class EQ12AlertingService:
    """
    Professional alerting service for EQ12 automation.
    Handles Telegram, Slack, and rate limiting.
    """

    def __init__(self):
        # Load config from environment
        self.config = AlertConfig(
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
        )

        if not self.config.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
        if not self.config.telegram_chat_id:
            raise ValueError("TELEGRAM_CHAT_ID environment variable not set")

        # Initialize responses client for alert copy generation
        self.responses_client = EQ12ResponsesClient()

        # Rate limiting state
        self.alert_history: list[dict] = []
        self.game_alert_counts: dict[str, int] = {}
        self.last_alert_times: dict[str, float] = {}

        # Paths
        self.logs_dir = Path("C:/EQ12/logs")
        self.logs_dir.mkdir(exist_ok=True)

        logger.info("🚨 EQ12 Alerting Service initialized")
        logger.info(f"   Telegram: {'✓' if self.config.telegram_bot_token else '✗'}")
        logger.info(f"   Slack: {'✓' if self.config.slack_webhook_url else '✗'}")
        logger.info(f"   EV threshold: {self.config.min_parlay_ev:.1%}")

    async def process_parlay_alerts(self, parlays_file: str | None = None) -> dict:
        """
        Process parlay results and send appropriate alerts.
        Returns summary of alerts sent.
        """
        try:
            # Load parlay results
            parlays_data = await self.load_parlay_results(parlays_file)
            if not parlays_data:
                return {"error": "No parlay data available"}

            parlays = parlays_data.get("parlays", [])
            if not parlays:
                return {"message": "No parlays to process"}

            # Filter parlays by EV threshold
            alert_worthy_parlays = self.filter_alert_worthy_parlays(parlays)

            logger.info(
                f"📊 Processing {len(alert_worthy_parlays)} alert-worthy parlays "
                f"from {len(parlays)} total"
            )

            # Apply rate limiting
            filtered_parlays = await self.apply_rate_limiting(alert_worthy_parlays)

            if not filtered_parlays:
                return {
                    "message": "No parlays passed rate limiting",
                    "rate_limited_count": len(alert_worthy_parlays),
                }

            # Send alerts
            alerts_sent = []
            for parlay in filtered_parlays:
                try:
                    alert_result = await self.send_parlay_alert(parlay)
                    if alert_result.get("success"):
                        alerts_sent.append(alert_result)

                    # Small delay between alerts
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"❌ Failed to send alert for parlay: {e}")

            # Update alert history
            await self.update_alert_history(alerts_sent)

            summary = {
                "timestamp_utc": utc_now().isoformat(),
                "total_parlays": len(parlays),
                "alert_worthy": len(alert_worthy_parlays),
                "rate_limited": len(alert_worthy_parlays) - len(filtered_parlays),
                "alerts_sent": len(alerts_sent),
                "alerts_details": alerts_sent,
            }

            logger.info(f"✅ Alert processing complete: {len(alerts_sent)} alerts sent")
            return summary

        except Exception as e:
            logger.error(f"❌ Alert processing failed: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    async def load_parlay_results(self, file_path: str | None = None) -> dict | None:
        """Load parlay results from file or latest snapshot."""
        try:
            if not file_path:
                file_path = self.logs_dir / "latest_parlay_results.json"

            with open(file_path) as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Failed to load parlay results: {e}")
            return None

    def filter_alert_worthy_parlays(self, parlays: list[dict]) -> list[dict]:
        """Filter parlays that meet alerting criteria."""
        worthy = []

        for parlay in parlays:
            try:
                total_ev = parlay.get("total_ev", 0)
                legs_count = len(parlay.get("legs", []))

                # Basic EV threshold
                if total_ev < self.config.min_parlay_ev:
                    continue

                # Must have reasonable leg count
                if legs_count < 2 or legs_count > self.config.max_legs_display:
                    continue

                # Check if all legs are upcoming
                if not self.all_legs_upcoming(parlay.get("legs", [])):
                    continue

                # Add priority classification
                parlay["alert_priority"] = self.classify_alert_priority(total_ev)
                parlay["alert_worthy"] = True

                worthy.append(parlay)

            except Exception as e:
                logger.warning(f"⚠️ Failed to evaluate parlay for alerts: {e}")

        return worthy

    def all_legs_upcoming(self, legs: list[dict]) -> bool:
        """Check if all parlay legs are upcoming games."""
        try:
            for leg in legs:
                commence_time_str = leg.get("commence_time_utc", "")
                if not commence_time_str:
                    continue

                commence_time = parse_commence_time(commence_time_str)
                now = utc_now()

                # Must be at least 30 minutes in the future
                if (commence_time - now).total_seconds() < 1800:  # 30 minutes
                    return False

            return True

        except Exception:
            return False

    def classify_alert_priority(self, total_ev: float) -> str:
        """Classify alert priority based on EV."""
        if total_ev >= self.config.critical_ev_threshold:
            return "CRITICAL"
        elif total_ev >= self.config.high_ev_threshold:
            return "HIGH"
        else:
            return "NORMAL"

    async def apply_rate_limiting(self, parlays: list[dict]) -> list[dict]:
        """Apply rate limiting rules to prevent spam."""
        now = time.time()
        current_hour = int(now // 3600)

        # Clean old alert history (keep last 24 hours)
        cutoff_time = now - 86400  # 24 hours
        self.alert_history = [
            alert for alert in self.alert_history if alert.get(
                "timestamp", 0) > cutoff_time]

        # Count alerts in current hour
        current_hour_alerts = [
            alert
            for alert in self.alert_history
            if int(alert.get("timestamp", 0) // 3600) == current_hour
        ]

        if len(current_hour_alerts) >= self.config.max_alerts_per_hour:
            logger.warning(
                f"⚠️ Rate limit reached: {
                    len(current_hour_alerts)} alerts this hour")
            return []

        filtered = []

        for parlay in parlays:
            try:
                # Check game-specific limits
                game_ids = self.extract_game_ids(parlay.get("legs", []))

                # Skip if too many alerts for these games
                game_alert_count = sum(
                    self.game_alert_counts.get(
                        gid, 0) for gid in game_ids)
                if game_alert_count >= self.config.max_same_game_alerts:
                    continue

                # Check cooldown for similar parlays
                parlay_signature = self.generate_parlay_signature(parlay)
                last_similar_alert = self.last_alert_times.get(parlay_signature, 0)

                if now - last_similar_alert < (self.config.cooldown_minutes * 60):
                    continue

                # Priority alerts bypass some limits
                if parlay.get("alert_priority") == "CRITICAL":
                    filtered.append(parlay)
                    continue

                # Normal rate limiting
                if len(filtered) < (
                        self.config.max_alerts_per_hour -
                        len(current_hour_alerts)):
                    filtered.append(parlay)

            except Exception as e:
                logger.warning(f"⚠️ Rate limiting failed for parlay: {e}")

        return filtered

    def extract_game_ids(self, legs: list[dict]) -> list[str]:
        """Extract unique game IDs from parlay legs."""
        return list({leg.get("game_id", "") for leg in legs if leg.get("game_id")})

    def generate_parlay_signature(self, parlay: dict) -> str:
        """Generate signature for parlay similarity detection."""
        try:
            legs = parlay.get("legs", [])
            leg_sigs = []

            for leg in legs:
                sig = f"{leg.get('market', '')}_{leg.get('selection', '')}"
                leg_sigs.append(sig)

            return "_".join(sorted(leg_sigs))

        except Exception:
            return f"parlay_{int(time.time())}"

    async def send_parlay_alert(self, parlay: dict) -> dict:
        """Send alert for a single parlay to all configured channels."""
        try:
            # Generate alert copy using reusable prompt
            alert_copy = await self.generate_alert_copy(parlay)

            # Format parlay card
            parlay_card = self.format_parlay_card(parlay)

            # Send to Telegram
            telegram_result = await self.send_telegram_alert(alert_copy, parlay_card)

            # Send to Slack (if configured)
            slack_result = None
            if self.config.slack_webhook_url:
                slack_result = await self.send_slack_alert(alert_copy, parlay_card)

            return {
                "success": True,
                "parlay_id": parlay.get("id", "unknown"),
                "alert_copy": alert_copy,
                "telegram": telegram_result,
                "slack": slack_result,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.error(f"❌ Failed to send parlay alert: {e}")
            return {"success": False, "error": str(e), "timestamp": time.time()}

    async def generate_alert_copy(self, parlay: dict) -> str:
        """Generate alert copy using pmpt_eq12_alert_copy_v1."""
        try:
            # Prepare parlay data for prompt
            alert_data = {
                "parlay": {
                    "total_ev": parlay.get("total_ev", 0),
                    "total_kelly": parlay.get("total_kelly", 0),
                    "total_odds": parlay.get("total_odds", 100),
                    "legs_count": len(parlay.get("legs", [])),
                    "strategy": parlay.get("strategy", "balanced"),
                    "priority": parlay.get("alert_priority", "NORMAL"),
                },
                "legs_preview": [
                    {
                        "selection": leg.get("selection", ""),
                        "odds": leg.get("odds", 0),
                        "market": leg.get("market", ""),
                        "hook_flag": leg.get("hook_flag", False),
                    }
                    for leg in parlay.get("legs", [])[:3]  # First 3 legs for preview
                ],
                "style": "telegram_oneliner",
            }

            logger.info("📝 Generating alert copy with pmpt_eq12_alert_copy_v1")

            # Use reusable prompt for alert copy
            response = await self.responses_client.generate_alert_copy_with_prompt_id(
                prompt_id="pmpt_eq12_alert_copy_v1",
                variables={"alert_data": json.dumps(alert_data, indent=2)},
                reasoning_effort="minimal",  # Quick generation for alerts
            )

            # Extract alert text from response
            alert_copy = self.parse_alert_response(response)
            return alert_copy or self.generate_fallback_copy(parlay)

        except Exception as e:
            logger.error(f"❌ Alert copy generation failed: {e}")
            return self.generate_fallback_copy(parlay)

    def parse_alert_response(self, response: dict) -> str | None:
        """Parse alert copy from OpenAI response."""
        try:
            choices = response.get("choices", [])
            if not choices:
                return None

            message = choices[0].get("message", {})
            content = message.get("content", "").strip()

            # Extract first line if multi-line response
            if "\n" in content:
                content = content.split("\n")[0].strip()

            return content if content else None

        except Exception:
            return None

    def generate_fallback_copy(self, parlay: dict) -> str:
        """Generate fallback alert copy without AI."""
        try:
            total_ev = parlay.get("total_ev", 0)
            legs_count = len(parlay.get("legs", []))
            priority = parlay.get("alert_priority", "NORMAL")

            priority_emoji = {
                "CRITICAL": "🚨",
                "HIGH": "🔥",
                "NORMAL": "⚡"}.get(
                priority,
                "📊")

            return (
                f"{priority_emoji} {legs_count}-leg parlay @ {total_ev:.1%} EV "
                f"- {priority.lower()} priority alert"
            )

        except Exception:
            return "📊 EQ12 Parlay Alert - check logs for details"

    def format_parlay_card(self, parlay: dict) -> str:
        """Format compact parlay card for mobile consumption."""
        try:
            legs = parlay.get("legs", [])
            total_ev = parlay.get("total_ev", 0)
            total_odds = parlay.get("total_odds", 100)
            strategy = parlay.get("strategy", "balanced")

            # Header
            card_lines = [
                f"🎯 **{len(legs)}-Leg {strategy.title()} Parlay**",
                f"💰 **EV:** {total_ev:.1%} | **Odds:** {total_odds:+d}",
                "",
            ]

            # Legs (limit to max display)
            display_legs = legs[: self.config.max_legs_display]

            for i, leg in enumerate(display_legs, 1):
                selection = leg.get("selection", "Unknown")
                odds = leg.get("odds", 0)
                market = leg.get("market", "")
                point = leg.get("point")
                hook_flag = leg.get("hook_flag", False)

                # Format leg line
                leg_line = f"{i}. **{selection}**"

                if market == "spread" and point is not None:
                    leg_line += f" {point:+g}"
                elif market == "total" and point is not None:
                    leg_line += f" {market} {point}"

                leg_line += f" ({odds:+d})"

                if hook_flag:
                    leg_line += " 🎣"  # Hook indicator

                card_lines.append(leg_line)

            # Footer with timing
            if legs:
                first_game_time = legs[0].get("commence_time_utc", "")
                if first_game_time:
                    try:
                        game_dt = parse_commence_time(first_game_time)
                        time_display = to_eastern_display(game_dt)
                        card_lines.extend(["", f"⏰ First game: {time_display}"])
                    except Exception:
                        pass

            return "\n".join(card_lines)

        except Exception as e:
            logger.error(f"Failed to format parlay card: {e}")
            return f"📊 Parlay Details (formatting error: {e})"

    async def send_telegram_alert(self, alert_copy: str, parlay_card: str) -> dict:
        """Send alert to Telegram."""
        try:
            url = f"https://api.telegram.org/bot{
                self.config.telegram_bot_token}/sendMessage"

            # Combine alert copy and parlay card
            full_message = f"{alert_copy}\n\n{parlay_card}"

            # Telegram has 4096 character limit
            if len(full_message) > 4000:
                full_message = full_message[:4000] + "..."

            payload = {
                "chat_id": self.config.telegram_chat_id,
                "text": full_message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    result = await response.json()

                    if response.status == 200 and result.get("ok"):
                        logger.info("📱 Telegram alert sent successfully")
                        return {
                            "success": True,
                            "message_id": result.get("result", {}).get("message_id"),
                        }
                    else:
                        logger.error(f"❌ Telegram alert failed: {result}")
                        return {"success": False, "error": result}

        except Exception as e:
            logger.error(f"❌ Telegram alert error: {e}")
            return {"success": False, "error": str(e)}

    async def send_slack_alert(self, alert_copy: str, parlay_card: str) -> dict:
        """Send alert to Slack webhook."""
        try:
            # Format for Slack
            slack_payload = {"text": alert_copy, "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": parlay_card}}], }

            async with (
                aiohttp.ClientSession() as session,
                session.post(self.config.slack_webhook_url, json=slack_payload) as response,
            ):
                if response.status == 200:
                    logger.info("💬 Slack alert sent successfully")
                    return {"success": True}
                else:
                    error_text = await response.text()
                    logger.error(
                        f"❌ Slack alert failed: {
                            response.status} - {error_text}")
                    return {"success": False, "error": error_text}

        except Exception as e:
            logger.error(f"❌ Slack alert error: {e}")
            return {"success": False, "error": str(e)}

    async def update_alert_history(self, alerts_sent: list[dict]):
        """Update alert history for rate limiting."""
        try:
            current_time = time.time()

            for alert in alerts_sent:
                # Update alert history
                self.alert_history.append(
                    {
                        "timestamp": current_time,
                        "parlay_id": alert.get("parlay_id", ""),
                        "alert_copy": alert.get("alert_copy", ""),
                    }
                )

                # Update game alert counts (simplified - would need parlay details)
                # game_ids = alert.get("game_ids", [])
                # for gid in game_ids:
                #     self.game_alert_counts[gid] = self.game_alert_counts.get(gid, 0) + 1

            # Persist alert state
            state_file = self.logs_dir / "alert_state.json"
            state_data = {
                "last_update": current_time,
                "alert_history_count": len(self.alert_history),
                "game_alert_counts": self.game_alert_counts,
            }

            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to update alert history: {e}")


async def main():
    """Main entry point for alerting service."""
    logger.info("🚨 EQ12 Alerting Service Starting")
    logger.info("=" * 50)

    try:
        alerting_service = EQ12AlertingService()
        result = await alerting_service.process_parlay_alerts()

        if "error" in result:
            logger.error(f"❌ Alerting failed: {result['error']}")
        else:
            logger.info(
                f"✅ Alerting complete: {
                    result.get(
                        'alerts_sent',
                        0)} alerts sent")

        return result

    except KeyboardInterrupt:
        logger.info("\n👋 Alerting service stopped by user")
    except Exception as e:
        logger.error(f"❌ Alerting service failed: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
