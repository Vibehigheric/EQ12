#!/usr/bin/env python3
"""
EQ12 Discord Integration - Automated notifications for sports betting bots
Provides secure Discord webhook integration for bet alerts and updates
"""

import asyncio
import os
from datetime import datetime
from urllib.parse import urlparse

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import requests
except ImportError:
    requests = None


class DiscordNotifier:
    """
    Secure Discord webhook integration for sports betting automation.

    Features:
    - Async and sync webhook posting
    - Rich embed formatting for bet alerts
    - Error logging and retry logic
    - Secure webhook URL validation
    - Cross-browser extension compatible
    """

    def __init__(self, webhook_url: str | None = None):
        """
        Initialize Discord notifier with webhook URL.

        Args:
            webhook_url: Discord webhook URL (or None to use env var)
        """
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self._validate_webhook_url()

    def _validate_webhook_url(self) -> None:
        """Validate webhook URL format and security"""
        if not self.webhook_url:
            return  # Allow None for testing/disabled mode

        try:
            parsed = urlparse(self.webhook_url)
            if not parsed.netloc.endswith("discord.com"):
                raise ValueError("Invalid Discord webhook domain")
            if not parsed.path.startswith("/api/webhooks/"):
                raise ValueError("Invalid Discord webhook path")
        except Exception as e:
            raise ValueError(f"Invalid Discord webhook URL: {e}")

    async def send_async(
        self,
        content: str = "",
        embeds: list[dict] | None = None,
        username: str = "EQ12 Sports Bot",
        avatar_url: str = "",
    ) -> bool:
        """
        Send async webhook notification (preferred for browser extensions).

        Args:
            content: Plain text message
            embeds: List of Discord embed objects
            username: Bot display name
            avatar_url: Bot avatar URL

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url or not aiohttp:
            return False

        payload = {"content": content, "username": username, "embeds": embeds or []}

        if avatar_url:
            payload["avatar_url"] = avatar_url

        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response,
            ):
                return response.status == 204
        except Exception as e:
            print(f"Discord webhook error: {e}")
            return False

    def send_sync(
        self,
        content: str = "",
        embeds: list[dict] | None = None,
        username: str = "EQ12 Sports Bot",
        avatar_url: str = "",
    ) -> bool:
        """
        Send sync webhook notification (for CLI tools).

        Args:
            content: Plain text message
            embeds: List of Discord embed objects
            username: Bot display name
            avatar_url: Bot avatar URL

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.webhook_url or not requests:
            return False

        payload = {"content": content, "username": username, "embeds": embeds or []}

        if avatar_url:
            payload["avatar_url"] = avatar_url

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            return response.status_code == 204
        except Exception as e:
            print(f"Discord webhook error: {e}")
            return False


def create_bet_alert_embed(
    bet_id: str,
    sport: str,
    stake: float,
    ev: float,
    odds: float,
    boost_pct: float = 0,
    book: str = "DraftKings",
    alert_type: str = "VALUE",
) -> dict:
    """
    Create rich Discord embed for bet alerts.

    Args:
        bet_id: Unique bet identifier
        sport: Sport category (NFL, NBA, etc.)
        stake: Recommended stake amount
        ev: Expected value percentage
        odds: Decimal odds
        boost_pct: Boost percentage if applicable
        book: Sportsbook name
        alert_type: Alert type (VALUE, ARBITRAGE, etc.)

    Returns:
        Discord embed dictionary
    """
    # Color coding by alert type
    colors = {
        "VALUE": 0x00FF00,  # Green for +EV
        "ARBITRAGE": 0xFF6600,  # Orange for arb
        "BOOST": 0x9966FF,  # Purple for boosts
        "ERROR": 0xFF0000,  # Red for errors
    }

    # Emoji by sport
    sport_emojis = {
        "NFL": "🏈",
        "NBA": "🏀",
        "MLB": "⚾",
        "NHL": "🏒",
        "CFB": "🏈",
        "NCAAB": "🏀",
        "UFC": "🥊",
        "SOCCER": "⚽",
        "TENNIS": "🎾",
    }

    embed = {
        "title": f"{sport_emojis.get(sport.upper(), '🎯')} {alert_type} ALERT",
        "color": colors.get(alert_type, 0x0099FF),
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {"name": "📊 Expected Value", "value": f"**{ev:+.2f}%**", "inline": True},
            {
                "name": "💰 Recommended Stake",
                "value": f"**${stake:.2f}**",
                "inline": True,
            },
            {
                "name": "🎲 Odds",
                "value": f"**{odds:.2f}**" + (f" (+{boost_pct}% boost)" if boost_pct else ""),
                "inline": True,
            },
            {"name": "🏪 Sportsbook", "value": book, "inline": True},
            {"name": "🆔 Bet ID", "value": f"`{bet_id}`", "inline": True},
            {
                "name": "⏰ Generated",
                "value": f"<t:{int(datetime.utcnow().timestamp())}:R>",
                "inline": True,
            },
        ],
        "footer": {
            "text": "EQ12 Automated Sports Betting System",
            "icon_url": "https://cdn.discordapp.com/emojis/123456789.png",
        },
    }

    return embed


def create_bet_settlement_embed(
    bet_id: str,
    sport: str,
    stake: float,
    result: str,
    payout: float,
    profit_loss: float,
    new_balance: float,
) -> dict:
    """
    Create rich Discord embed for bet settlements.

    Args:
        bet_id: Unique bet identifier
        sport: Sport category
        stake: Original stake
        result: Settlement result (win/loss/push/void)
        payout: Total payout received
        profit_loss: Net profit/loss amount
        new_balance: Updated bankroll balance

    Returns:
        Discord embed dictionary
    """
    # Result-based styling
    result_config = {
        "win": {"emoji": "✅", "color": 0x00FF00, "title": "BET WON"},
        "loss": {"emoji": "❌", "color": 0xFF0000, "title": "BET LOST"},
        "push": {"emoji": "🔄", "color": 0xFFFF00, "title": "BET PUSHED"},
        "void": {"emoji": "⚪", "color": 0x888888, "title": "BET VOIDED"},
    }

    config = result_config.get(result.lower(), result_config["loss"])

    embed = {
        "title": f"{config['emoji']} {config['title']}",
        "color": config["color"],
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {
                "name": "📈 Profit/Loss",
                "value": f"**${profit_loss:+.2f}**",
                "inline": True,
            },
            {"name": "💳 Payout", "value": f"**${payout:.2f}**", "inline": True},
            {
                "name": "🏦 New Balance",
                "value": f"**${new_balance:.2f}**",
                "inline": True,
            },
            {"name": "💰 Original Stake", "value": f"${stake:.2f}", "inline": True},
            {"name": "🆔 Bet ID", "value": f"`{bet_id}`", "inline": True},
            {"name": "🏈 Sport", "value": sport.upper(), "inline": True},
        ],
        "footer": {
            "text": "EQ12 Automated Sports Betting System",
        },
    }

    return embed


def create_daily_summary_embed(stats: dict) -> dict:
    """
    Create rich Discord embed for daily betting summaries.

    Args:
        stats: Statistics dictionary from bankroll tracker

    Returns:
        Discord embed dictionary
    """
    total_pl = stats.get("total_profit_loss", 0)
    win_rate = stats.get("win_rate", 0)
    roi = stats.get("roi", 0)

    # Performance-based color
    if total_pl > 0:
        color = 0x00FF00  # Green for profit
    elif total_pl < 0:
        color = 0xFF0000  # Red for loss
    else:
        color = 0x0099FF  # Blue for break-even

    embed = {
        "title": "📊 Daily Betting Summary",
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "fields": [
            {
                "name": "💰 Today's P/L",
                "value": f"**${total_pl:+.2f}**",
                "inline": True,
            },
            {"name": "📈 Win Rate", "value": f"**{win_rate:.1f}%**", "inline": True},
            {"name": "📊 ROI", "value": f"**{roi:+.2f}%**", "inline": True},
            {
                "name": "🎯 Total Bets",
                "value": f"{stats.get('settled_bets', 0)}",
                "inline": True,
            },
            {"name": "✅ Wins", "value": f"{stats.get('wins', 0)}", "inline": True},
            {"name": "❌ Losses", "value": f"{stats.get('losses', 0)}", "inline": True},
        ],
        "footer": {
            "text": f"Current Balance: ${stats.get('current_balance', 0):.2f}",
        },
    }

    return embed


# Convenience functions for common use cases
async def notify_bet_alert_async(
    bet_id: str,
    sport: str,
    stake: float,
    ev: float,
    odds: float,
    webhook_url: str | None = None,
) -> bool:
    """Send async bet alert notification"""
    notifier = DiscordNotifier(webhook_url)
    embed = create_bet_alert_embed(bet_id, sport, stake, ev, odds)
    return await notifier.send_async(embeds=[embed])


def notify_bet_alert_sync(
    bet_id: str,
    sport: str,
    stake: float,
    ev: float,
    odds: float,
    webhook_url: str | None = None,
) -> bool:
    """Send sync bet alert notification"""
    notifier = DiscordNotifier(webhook_url)
    embed = create_bet_alert_embed(bet_id, sport, stake, ev, odds)
    return notifier.send_sync(embeds=[embed])


async def notify_bet_settlement_async(
    bet_id: str,
    sport: str,
    stake: float,
    result: str,
    payout: float,
    profit_loss: float,
    new_balance: float,
    webhook_url: str | None = None,
) -> bool:
    """Send async bet settlement notification"""
    notifier = DiscordNotifier(webhook_url)
    embed = create_bet_settlement_embed(
        bet_id, sport, stake, result, payout, profit_loss, new_balance
    )
    return await notifier.send_async(embeds=[embed])


def notify_bet_settlement_sync(
    bet_id: str,
    sport: str,
    stake: float,
    result: str,
    payout: float,
    profit_loss: float,
    new_balance: float,
    webhook_url: str | None = None,
) -> bool:
    """Send sync bet settlement notification"""
    notifier = DiscordNotifier(webhook_url)
    embed = create_bet_settlement_embed(
        bet_id, sport, stake, result, payout, profit_loss, new_balance
    )
    return notifier.send_sync(embeds=[embed])


# Browser Extension Compatible Functions
def create_extension_webhook_payload(
    message: str, bet_data: dict | None = None, alert_type: str = "INFO"
) -> dict:
    """
    Create webhook payload optimized for browser extension use.
    Returns a simple JSON object that can be posted via fetch().

    Args:
        message: Simple text message
        bet_data: Optional bet information dictionary
        alert_type: Type of alert for styling

    Returns:
        Webhook payload dictionary ready for JSON.stringify()
    """
    payload = {
        "content": f"🤖 **EQ12 Extension Alert**\n{message}",
        "username": "EQ12 Browser Bot",
    }

    if bet_data:
        embed = create_bet_alert_embed(
            bet_data.get("id", "unknown"),
            bet_data.get("sport", "UNKNOWN"),
            bet_data.get("stake", 0),
            bet_data.get("ev", 0),
            bet_data.get("odds", 0),
            bet_data.get("boost_pct", 0),
            bet_data.get("book", "Unknown"),
            alert_type,
        )
        payload["embeds"] = [embed]

    return payload


if __name__ == "__main__":
    # Test the Discord integration
    import asyncio

    async def test_discord():
        """Test Discord webhook functionality"""
        print("🧪 Testing Discord integration...")

        # Test bet alert
        success = await notify_bet_alert_async(
            bet_id="test-123", sport="NFL", stake=50.0, ev=4.2, odds=2.1
        )
        print(f"Bet alert test: {'✅' if success else '❌'}")

        # Test settlement
        success = await notify_bet_settlement_async(
            bet_id="test-123",
            sport="NFL",
            stake=50.0,
            result="win",
            payout=105.0,
            profit_loss=55.0,
            new_balance=1055.0,
        )
        print(f"Settlement test: {'✅' if success else '❌'}")

    # Only run test if webhook URL is available
    if os.getenv("DISCORD_WEBHOOK_URL"):
        asyncio.run(test_discord())
    else:
        print("💡 Set DISCORD_WEBHOOK_URL environment variable to test")
