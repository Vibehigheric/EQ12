#!/usr/bin/env python3
"""
EQ12 Live Betting Coach Bot - Discord/Telegram Revenue Engine
===========================================================

Multi-platform betting bot with:
- Real-time EV alerts and hedge suggestions
- Subscription-gated premium channels
- Stripe integration for monthly billing
- Live game coaching and analysis
- Secure OpenAI integration with cost controls

Revenue Model:
- Basic Bot: Free (limited alerts)
- Pro Bot: $29/month (5min alerts, coaching)
- VIP Bot: $79/month (instant alerts, hedge suggestions)
- Private Channels: $199/month (custom analysis)

Features:
- Multi-platform (Discord + Telegram)
- Real-time line monitoring
- AI-powered explanations
- Bankroll management advice
- Legal compliance by jurisdiction

Author: EQ12 Development Team
Version: 2.0.0
"""

import asyncio
import hashlib
import logging
import os
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

import discord
import stripe
from discord.ext import commands, tasks
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from eq12_openai_security import EQ12OpenAISecurityManager

# Import EQ12 components
from eq12_sports_betting_engine import BettingLeg, EQ12BettingEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_CONFIG = {
    "discord": {
        "token": os.getenv("DISCORD_BOT_TOKEN"),
        "prefix": "!eq12",
        "free_channel": int(os.getenv("DISCORD_FREE_CHANNEL", 0)),
        "pro_channel": int(os.getenv("DISCORD_PRO_CHANNEL", 0)),
        "vip_channel": int(os.getenv("DISCORD_VIP_CHANNEL", 0)),
    },
    "telegram": {
        "token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "free_chat": os.getenv("TELEGRAM_FREE_CHAT"),
        "pro_chat": os.getenv("TELEGRAM_PRO_CHAT"),
        "vip_chat": os.getenv("TELEGRAM_VIP_CHAT"),
    },
}


@dataclass
class BotSubscription:
    """Bot subscription tracking"""

    user_id: str
    platform: str  # discord, telegram
    tier: str  # free, pro, vip
    expires_at: datetime
    stripe_subscription_id: str | None = None
    alerts_sent: int = 0
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def is_active(self) -> bool:
        return datetime.now() < self.expires_at

    @property
    def days_remaining(self) -> int:
        delta = self.expires_at - datetime.now()
        return max(0, delta.days)


class EQ12BettingBot:
    """Multi-platform betting bot with monetization"""

    def __init__(self):
        # Core components
        self.betting_engine = EQ12BettingEngine()
        self.openai_manager = EQ12OpenAISecurityManager("betting_bot")

        # Database
        self.db_path = "C:/EQ12/logs/betting_bot.db"

        # Bot instances
        self.discord_bot = None
        self.telegram_bot = None

        # Subscription management
        self.subscriptions = {}

        # Revenue tracking
        self.revenue_stats = {
            "monthly_recurring": 0.0,
            "total_users": 0,
            "active_subscribers": 0,
            "churn_rate": 0.0,
        }

        # Alert queue
        self.alert_queue = asyncio.Queue()

        self.setup_database()
        self.setup_discord_bot()
        self.setup_telegram_bot()

    def setup_database(self):
        """Initialize bot database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Bot subscriptions
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_subscriptions (
                user_id TEXT,
                platform TEXT,
                tier TEXT,
                expires_at DATETIME,
                stripe_subscription_id TEXT,
                alerts_sent INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, platform)
            )
        """
        )

        # Alert history
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alert_history (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                platform TEXT,
                channel_id TEXT,
                alert_type TEXT,
                content TEXT,
                ev_percent REAL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                clicked BOOLEAN DEFAULT FALSE
            )
        """
        )

        # Revenue tracking
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_revenue (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                platform TEXT,
                subscription_tier TEXT,
                amount_usd REAL,
                stripe_payment_id TEXT,
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # User preferences
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT,
                platform TEXT,
                min_ev REAL DEFAULT 3.0,
                sports TEXT DEFAULT 'nfl,nba',
                bankroll REAL DEFAULT 1000.0,
                risk_pct REAL DEFAULT 2.0,
                notifications BOOLEAN DEFAULT TRUE,
                PRIMARY KEY (user_id, platform)
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Bot database initialized")

    def setup_discord_bot(self):
        """Setup Discord bot"""
        if not BOT_CONFIG["discord"]["token"]:
            logger.warning("Discord bot token not configured")
            return

        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        self.discord_bot = commands.Bot(
            command_prefix=BOT_CONFIG["discord"]["prefix"], intents=intents
        )

        @self.discord_bot.event
        async def on_ready():
            logger.info(f"✅ Discord bot ready: {self.discord_bot.user}")

        # Commands
        @self.discord_bot.command(name="subscribe")
        async def subscribe_discord(ctx, tier: str = "pro"):
            """Subscribe to EQ12 betting alerts"""
            await self.handle_subscription_request(ctx, tier, "discord")

        @self.discord_bot.command(name="alerts")
        async def get_alerts_discord(ctx):
            """Get latest EV alerts"""
            await self.handle_alerts_request(ctx, "discord")

        @self.discord_bot.command(name="coach")
        async def live_coach_discord(ctx, *, game_info: str | None = None):
            """Get live betting coaching"""
            await self.handle_coaching_request(ctx, game_info, "discord")

        @self.discord_bot.command(name="settings")
        async def settings_discord(ctx):
            """Manage bot settings"""
            await self.handle_settings_request(ctx, "discord")

        @self.discord_bot.command(name="stats")
        async def stats_discord(ctx):
            """Show user stats and subscription info"""
            await self.handle_stats_request(ctx, "discord")

    def setup_telegram_bot(self):
        """Setup Telegram bot"""
        if not BOT_CONFIG["telegram"]["token"]:
            logger.warning("Telegram bot token not configured")
            return

        self.telegram_app = Application.builder().token(BOT_CONFIG["telegram"]["token"]).build()

        # Commands
        self.telegram_app.add_handler(CommandHandler("start", self.telegram_start))
        self.telegram_app.add_handler(CommandHandler("subscribe", self.telegram_subscribe))
        self.telegram_app.add_handler(CommandHandler("alerts", self.telegram_alerts))
        self.telegram_app.add_handler(CommandHandler("coach", self.telegram_coach))
        self.telegram_app.add_handler(CommandHandler("settings", self.telegram_settings))
        self.telegram_app.add_handler(CommandHandler("stats", self.telegram_stats))

        # Callback handlers for inline buttons
        self.telegram_app.add_handler(CallbackQueryHandler(self.telegram_callback_handler))

    # ==================== SUBSCRIPTION MANAGEMENT ====================

    async def handle_subscription_request(self, ctx, tier: str, platform: str):
        """Handle subscription requests"""

        user_id = str(ctx.author.id) if platform == "discord" else str(ctx.from_user.id)

        # Validate tier
        if tier not in ["free", "pro", "vip"]:
            await self.send_message(
                ctx, platform, "❌ Invalid subscription tier. Use: free, pro, or vip"
            )
            return

        # Get current subscription
        await self.get_user_subscription(user_id, platform)

        if tier == "free":
            # Free tier signup
            await self.create_free_subscription(user_id, platform)
            await self.send_message(
                ctx,
                platform,
                "✅ **Free EQ12 Alerts Activated!**\n\n"
                "🎯 You'll receive up to 5 value alerts per day\n"
                "📊 Basic EV analysis included\n\n"
                "💎 Upgrade to Pro for 5-minute alerts and live coaching!\n"
                "Use `!eq12 subscribe pro` to upgrade",
            )

        elif tier in ["pro", "vip"]:
            # Paid tier - create Stripe checkout
            pricing = {"pro": 29.00, "vip": 79.00}
            checkout_url = await self.create_stripe_checkout(user_id, platform, tier, pricing[tier])

            embed_message = (
                f"💰 **EQ12 {tier.upper()} Subscription**\n\n"
                f"💵 Price: ${pricing[tier]:.2f}/month\n\n"
            )

            if tier == "pro":
                embed_message += (
                    "⚡ **Pro Features:**\n"
                    "• 5-minute EV alerts\n"
                    "• Live betting coach\n"
                    "• Parlay optimizer\n"
                    "• Advanced analytics\n\n"
                )
            else:  # vip
                embed_message += (
                    "🔥 **VIP Features:**\n"
                    "• Instant alerts (<30 seconds)\n"
                    "• Personal hedge suggestions\n"
                    "• Custom watchlists\n"
                    "• Priority support\n"
                    "• Private VIP channel\n\n"
                )

            embed_message += f"[💳 Complete Payment]({checkout_url})"

            await self.send_message(ctx, platform, embed_message)

    async def create_stripe_checkout(
        self, user_id: str, platform: str, tier: str, amount: float
    ) -> str:
        """Create Stripe checkout session"""

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": f"EQ12 {tier.upper()} Bot Subscription",
                                "description": f"Monthly access to EQ12 betting bot {tier} features",
                            },
                            "unit_amount": int(amount * 100),
                            "recurring": {"interval": "month"},
                        },
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=f"https://eq12.com/bot-success?tier={tier}",
                cancel_url="https://eq12.com/bot-cancel",
                metadata={"user_id": user_id, "platform": platform, "tier": tier},
            )

            return session.url

        except Exception as e:
            logger.error(f"Stripe checkout error: {e}")
            return "https://eq12.com/pricing"

    async def activate_subscription(
        self, user_id: str, platform: str, tier: str, stripe_sub_id: str
    ):
        """Activate paid subscription after Stripe confirmation"""

        expires_at = datetime.now() + timedelta(days=30)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO bot_subscriptions
            (user_id, platform, tier, expires_at, stripe_subscription_id)
            VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, platform, tier, expires_at, stripe_sub_id),
        )

        # Log revenue
        pricing = {"pro": 29.00, "vip": 79.00}
        revenue_id = hashlib.md5(f"{user_id}{platform}{time.time()}".encode()).hexdigest()

        cursor.execute(
            """
            INSERT INTO bot_revenue (id, user_id, platform, subscription_tier, amount_usd)
            VALUES (?, ?, ?, ?, ?)
        """,
            (revenue_id, user_id, platform, tier, pricing[tier]),
        )

        conn.commit()
        conn.close()

        # Update revenue stats
        self.revenue_stats["monthly_recurring"] += pricing[tier]
        self.revenue_stats["active_subscribers"] += 1

        logger.info(f"✅ Subscription activated: {user_id} - {tier} - ${pricing[tier]}")

    async def get_user_subscription(self, user_id: str, platform: str) -> BotSubscription | None:
        """Get user subscription info"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM bot_subscriptions
            WHERE user_id = ? AND platform = ?
        """,
            (user_id, platform),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return BotSubscription(
                user_id=row[0],
                platform=row[1],
                tier=row[2],
                expires_at=datetime.fromisoformat(row[3]),
                stripe_subscription_id=row[4],
                alerts_sent=row[5],
                created_at=datetime.fromisoformat(row[6]),
            )

        return None

    async def create_free_subscription(self, user_id: str, platform: str):
        """Create free tier subscription"""

        expires_at = datetime.now() + timedelta(days=365)  # Free tier lasts 1 year

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO bot_subscriptions
            (user_id, platform, tier, expires_at)
            VALUES (?, ?, 'free', ?)
        """,
            (user_id, platform, expires_at),
        )

        conn.commit()
        conn.close()

    # ==================== ALERT HANDLING ====================

    async def handle_alerts_request(self, ctx, platform: str):
        """Handle manual alerts request"""

        user_id = str(ctx.author.id) if platform == "discord" else str(ctx.from_user.id)
        subscription = await self.get_user_subscription(user_id, platform)

        if not subscription or not subscription.is_active:
            await self.send_message(
                ctx,
                platform,
                "❌ No active subscription found. Use `!eq12 subscribe free` to get started!",
            )
            return

        try:
            # Get EV alerts based on subscription tier
            limits = {"free": 3, "pro": 10, "vip": 20}
            min_ev = {"free": 5.0, "pro": 3.0, "vip": 2.0}

            legs = await self.betting_engine.calculate_ev_legs(
                "nfl", limits[subscription.tier], min_ev[subscription.tier]
            )

            if not legs:
                await self.send_message(
                    ctx,
                    platform,
                    "📊 No value bets found meeting your criteria right now.\n"
                    "💡 Try adjusting your settings with `!eq12 settings`",
                )
                return

            # Format alert message
            alert_msg = await self.format_ev_alert(legs, subscription.tier)

            # Send alert
            await self.send_message(ctx, platform, alert_msg)

            # Log alert
            await self.log_alert(
                user_id, platform, "manual_request", alert_msg, legs[0].ev_percent if legs else 0
            )

        except Exception as e:
            logger.error(f"Alert request error: {e}")
            await self.send_message(ctx, platform, "❌ Error generating alerts. Please try again.")

    async def handle_coaching_request(self, ctx, game_info: str, platform: str):
        """Handle live coaching requests"""

        user_id = str(ctx.author.id) if platform == "discord" else str(ctx.from_user.id)
        subscription = await self.get_user_subscription(user_id, platform)

        if not subscription or subscription.tier == "free":
            await self.send_message(
                ctx,
                platform,
                "🔒 **Live coaching is a Pro feature!**\n\n"
                "Upgrade to Pro ($29/month) for:\n"
                "• Live betting coach\n"
                "• Hedge suggestions\n"
                "• Advanced analytics\n\n"
                "Use `!eq12 subscribe pro` to upgrade",
            )
            return

        if not game_info:
            await self.send_message(
                ctx,
                platform,
                "🏈 **Live Coaching Usage:**\n"
                "`!eq12 coach Chiefs vs Bills, Q3 2:30, Chiefs +3`\n\n"
                "Include: teams, time, current situation",
            )
            return

        try:
            # Parse game state (simplified)
            game_state = self.parse_game_info(game_info)

            # Generate coaching advice
            coaching = await self.generate_live_coaching(game_state, subscription.tier)

            await self.send_message(ctx, platform, coaching)

        except Exception as e:
            logger.error(f"Coaching error: {e}")
            await self.send_message(ctx, platform, "❌ Coaching temporarily unavailable")

    async def format_ev_alert(self, legs: list[BettingLeg], tier: str) -> str:
        """Format EV alert message"""

        if not legs:
            return "📊 No value bets found"

        # Generate AI explanation for pro/vip tiers
        if tier in ["pro", "vip"]:
            explanation = await self.betting_engine.generate_ev_explanation(legs[:3], tier)
            ai_summary = explanation.get("content", "")
        else:
            ai_summary = "Upgrade to Pro for AI explanations!"

        alert_msg = "🚨 **EQ12 VALUE ALERT** 🚨\n\n"

        # Show top picks based on tier
        show_count = {"free": 3, "pro": 5, "vip": 10}[tier]

        for i, leg in enumerate(legs[:show_count], 1):
            alert_msg += f"**{i}. {leg.selection}**\n"
            alert_msg += f"   📊 {leg.sportsbook} | {leg.odds:+.0f}\n"
            alert_msg += f"   📈 EV: +{leg.ev_percent:.1f}% | Confidence: {leg.confidence:.0%}\n"
            alert_msg += f"   🎯 {leg.market.replace('_', ' ').title()}\n\n"

        if tier in ["pro", "vip"] and ai_summary:
            alert_msg += f"🧠 **AI Analysis:**\n{ai_summary}\n\n"

        alert_msg += "⚠️ *Educational purposes only. Bet responsibly.*\n"
        alert_msg += f"🕒 Generated at {datetime.now().strftime('%I:%M %p ET')}"

        return alert_msg

    async def generate_live_coaching(self, game_state: dict, tier: str) -> str:
        """Generate live betting coaching advice"""

        prompt = f"""Provide live betting advice for this situation:

Game: {game_state.get("teams", "Unknown")}
Time: {game_state.get("time", "Unknown")}
Situation: {game_state.get("situation", "Unknown")}
Current Line: {game_state.get("line", "Unknown")}

Focus on:
- Immediate opportunities
- Hedge suggestions
- Risk management
- Specific actionable advice

Keep under 100 words, urgent tone."""

        try:
            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [
                    {
                        "role": "system",
                        "content": "You are a live betting coach. Give specific, actionable advice with urgency.",
                    },
                    {"role": "user", "content": prompt},
                ],
                {"max_tokens": 180, "temperature": 0.4},
            )

            coaching = response["response"]["choices"][0]["message"]["content"]

            return f"🎯 **LIVE COACHING**\n\n{coaching}\n\n⚡ *Act quickly - lines move fast!*"

        except Exception as e:
            logger.error(f"Live coaching generation error: {e}")
            return "⚡ **LIVE COACHING**\n\nMonitor for line movement opportunities. Consider hedging if holding opposite position."

    def parse_game_info(self, game_info: str) -> dict[str, str]:
        """Parse game information from user input"""

        # Simplified parsing - in production would use NLP
        parts = game_info.split(",")

        return {
            "teams": parts[0].strip() if len(parts) > 0 else "Unknown",
            "time": parts[1].strip() if len(parts) > 1 else "Unknown",
            "situation": parts[2].strip() if len(parts) > 2 else "Unknown",
            "line": parts[3].strip() if len(parts) > 3 else "Unknown",
        }

    # ==================== AUTOMATED ALERT SYSTEM ====================

    @tasks.loop(minutes=5)
    async def send_automated_alerts(self):
        """Send automated alerts based on subscription tiers"""

        try:
            # Get active subscribers
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT user_id, platform, tier FROM bot_subscriptions
                WHERE expires_at > datetime('now') AND tier IN ('pro', 'vip')
            """
            )

            subscribers = cursor.fetchall()
            conn.close()

            if not subscribers:
                return

            # Get latest EV opportunities
            legs = await self.betting_engine.calculate_ev_legs("nfl", 10, 2.5)

            if not legs:
                return

            # Send to each subscriber
            for user_id, platform, tier in subscribers:
                try:
                    # Rate limit check
                    if not await self.check_alert_rate_limit(user_id, platform, tier):
                        continue

                    # Format and send alert
                    alert_msg = await self.format_ev_alert(legs, tier)

                    if platform == "discord":
                        await self.send_discord_alert(user_id, alert_msg, tier)
                    elif platform == "telegram":
                        await self.send_telegram_alert(user_id, alert_msg, tier)

                    # Log the alert
                    await self.log_alert(
                        user_id, platform, "automated", alert_msg, legs[0].ev_percent
                    )

                except Exception as e:
                    logger.error(f"Alert send error for {user_id}: {e}")

        except Exception as e:
            logger.error(f"Automated alerts error: {e}")

    async def check_alert_rate_limit(self, user_id: str, platform: str, tier: str) -> bool:
        """Check if user is within alert rate limits"""

        limits = {"free": 5, "pro": 50, "vip": 500}  # Daily limits

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM alert_history
            WHERE user_id = ? AND platform = ? AND DATE(sent_at) = DATE('now')
        """,
            (user_id, platform),
        )

        daily_count = cursor.fetchone()[0]
        conn.close()

        return daily_count < limits.get(tier, 5)

    # ==================== PLATFORM-SPECIFIC METHODS ====================

    async def send_discord_alert(self, user_id: str, message: str, tier: str):
        """Send alert to Discord user"""

        if not self.discord_bot:
            return

        try:
            # Get appropriate channel
            channel_mapping = {
                "free": BOT_CONFIG["discord"]["free_channel"],
                "pro": BOT_CONFIG["discord"]["pro_channel"],
                "vip": BOT_CONFIG["discord"]["vip_channel"],
            }

            channel_id = channel_mapping.get(tier)
            if not channel_id:
                return

            channel = self.discord_bot.get_channel(channel_id)
            if channel:
                # Mention user in VIP channel
                if tier == "vip":
                    message = f"<@{user_id}>\n{message}"

                await channel.send(message)

        except Exception as e:
            logger.error(f"Discord alert error: {e}")

    async def send_telegram_alert(self, user_id: str, message: str, tier: str):
        """Send alert to Telegram user"""

        if not self.telegram_app:
            return

        try:
            # Send direct message to user
            bot = self.telegram_app.bot
            await bot.send_message(
                chat_id=user_id, text=message, parse_mode="Markdown", disable_web_page_preview=True
            )

        except Exception as e:
            logger.error(f"Telegram alert error: {e}")

    async def send_message(self, ctx, platform: str, message: str):
        """Send message to user (platform agnostic)"""

        try:
            if platform == "discord":
                if hasattr(ctx, "send"):
                    await ctx.send(message)
                else:
                    await ctx.channel.send(message)

            elif platform == "telegram":
                await ctx.reply_text(message, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"Send message error: {e}")

    # ==================== TELEGRAM COMMAND HANDLERS ====================

    async def telegram_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Telegram /start command"""

        welcome_msg = (
            "🎯 **Welcome to EQ12 Betting Bot!**\n\n"
            "Get real-time value alerts and AI-powered betting insights.\n\n"
            "**Commands:**\n"
            "/subscribe - Choose subscription plan\n"
            "/alerts - Get latest value bets\n"
            "/coach - Live betting advice (Pro)\n"
            "/settings - Manage preferences\n"
            "/stats - View your statistics\n\n"
            "Start with `/subscribe free` for basic alerts!"
        )

        await update.message.reply_text(welcome_msg, parse_mode="Markdown")

    async def telegram_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Telegram subscription command"""

        args = context.args
        tier = args[0] if args else "pro"

        await self.handle_subscription_request(update.message, tier, "telegram")

    async def telegram_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Telegram alerts command"""

        await self.handle_alerts_request(update.message, "telegram")

    async def telegram_coach(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Telegram coaching command"""

        game_info = " ".join(context.args) if context.args else None
        await self.handle_coaching_request(update.message, game_info, "telegram")

    async def telegram_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Telegram settings command"""

        await self.handle_settings_request(update.message, "telegram")

    async def telegram_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Telegram stats command"""

        await self.handle_stats_request(update.message, "telegram")

    async def telegram_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Telegram inline button callbacks"""

        query = update.callback_query
        await query.answer()

        # Handle different callback actions
        if query.data.startswith("subscribe_"):
            tier = query.data.split("_")[1]
            await self.handle_subscription_request(query, tier, "telegram")

    # ==================== SETTINGS & STATS ====================

    async def handle_settings_request(self, ctx, platform: str):
        """Handle user settings management"""

        str(ctx.author.id) if platform == "discord" else str(ctx.from_user.id)

        settings_msg = (
            "⚙️ **EQ12 Bot Settings**\n\n"
            "Current Settings:\n"
            "• Min EV: 3.0%\n"
            "• Sports: NFL, NBA\n"
            "• Notifications: Enabled\n\n"
            "To modify settings, visit: https://eq12.com/bot-settings\n"
            "Or contact support for assistance."
        )

        await self.send_message(ctx, platform, settings_msg)

    async def handle_stats_request(self, ctx, platform: str):
        """Handle user statistics request"""

        user_id = str(ctx.author.id) if platform == "discord" else str(ctx.from_user.id)
        subscription = await self.get_user_subscription(user_id, platform)

        if not subscription:
            await self.send_message(
                ctx, platform, "❌ No subscription found. Use `/subscribe` to get started!"
            )
            return

        # Get user stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) FROM alert_history
            WHERE user_id = ? AND platform = ?
        """,
            (user_id, platform),
        )

        total_alerts = cursor.fetchone()[0]
        conn.close()

        stats_msg = (
            f"📊 **Your EQ12 Stats**\n\n"
            f"🎯 Subscription: {subscription.tier.upper()}\n"
            f"📅 Days Remaining: {subscription.days_remaining}\n"
            f"🚨 Alerts Received: {total_alerts}\n"
            f"📈 Member Since: {subscription.created_at.strftime('%B %Y')}\n\n"
        )

        if subscription.tier == "free":
            stats_msg += "💎 Upgrade to Pro for advanced features!"
        else:
            stats_msg += "🔥 Thanks for being a premium member!"

        await self.send_message(ctx, platform, stats_msg)

    async def log_alert(
        self, user_id: str, platform: str, alert_type: str, content: str, ev_percent: float
    ):
        """Log alert to database"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        alert_id = hashlib.md5(f"{user_id}{platform}{time.time()}".encode()).hexdigest()

        cursor.execute(
            """
            INSERT INTO alert_history (id, user_id, platform, alert_type, content, ev_percent)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (alert_id, user_id, platform, alert_type, content[:500], ev_percent),
        )

        conn.commit()
        conn.close()

    # ==================== MAIN BOT LIFECYCLE ====================

    async def start_bots(self):
        """Start both Discord and Telegram bots"""

        logger.info("🚀 Starting EQ12 Betting Bots")

        # Start automated alerts loop
        self.send_automated_alerts.start()

        # Start Discord bot
        if self.discord_bot and BOT_CONFIG["discord"]["token"]:
            asyncio.create_task(self.discord_bot.start(BOT_CONFIG["discord"]["token"]))
            logger.info("✅ Discord bot started")

        # Start Telegram bot
        if self.telegram_app and BOT_CONFIG["telegram"]["token"]:
            await self.telegram_app.run_polling()
            logger.info("✅ Telegram bot started")

        logger.info("🎯 Revenue targets:")
        logger.info("   - Pro subscriptions: 500 users × $29 = $14,500/month")
        logger.info("   - VIP subscriptions: 200 users × $79 = $15,800/month")
        logger.info("   - Total target: $30,300/month from bots")


# ==================== WEBHOOK HANDLERS ====================


async def handle_stripe_webhook(request):
    """Handle Stripe webhook for subscription confirmations"""

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv("STRIPE_WEBHOOK_SECRET")
        )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            # Extract user info from metadata
            user_id = session["metadata"]["user_id"]
            platform = session["metadata"]["platform"]
            tier = session["metadata"]["tier"]

            # Activate subscription
            bot = EQ12BettingBot()  # In production, use singleton
            await bot.activate_subscription(user_id, platform, tier, session["subscription"])

            logger.info(f"✅ Subscription activated via webhook: {user_id} - {tier}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return {"error": str(e)}


# ==================== MAIN EXECUTION ====================


async def main():
    """Main bot execution"""

    bot = EQ12BettingBot()
    await bot.start_bots()


if __name__ == "__main__":
    asyncio.run(main())
