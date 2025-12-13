#!/usr/bin/env python3
"""
EQ12 Telegram Apple TV Integration

Complete Telegram bot integration for Apple TV command center:
- Real-time Telegram triggers for content streaming
- Voice command processing via Telegram
- Interactive content selection and device management
- Status monitoring and control via chat interface
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import requests
    import telegram
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
    from telegram.ext import (
        Application,
        CallbackQueryHandler,
        CommandHandler,
        ContextTypes,
    )

    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("[WARNING] Missing Telegram dependencies. Run: pip install python-telegram-bot")

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
APPLETV_DIR = EQ12_HOME / "appletv_system"
TELEGRAM_LOGS_DIR = EQ12_HOME / "logs" / "telegram"

# Ensure directories exist
TELEGRAM_LOGS_DIR.mkdir(parents=True, exist_ok=True)


class EQ12TelegramAppleTVBot:
    """Telegram bot for Apple TV command center control"""

    def __init__(self):
        self.eq12_home = EQ12_HOME
        self.appletv_dir = APPLETV_DIR
        self.logs_dir = TELEGRAM_LOGS_DIR

        # Setup logging FIRST
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(self.logs_dir / "telegram_bot.log", encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
            force=True,
        )
        self.logger = logging.getLogger("TelegramAppleTVBot")

        # Bot configuration (after logger is set)
        self.bot_token = self._get_bot_token()
        self.chat_id = self._get_chat_id()

        # Apple TV integration
        self.appletv_manager = None
        self.streaming_engine = None

        # Initialize Apple TV components
        self._initialize_appletv_components()

    def _get_bot_token(self) -> str | None:
        """Get Telegram bot token"""

        # Try environment variable first
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
            return token

        # Try keys file
        token_file = self.eq12_home / "keys" / "telegram_bot_token.txt"
        if token_file.exists():
            return token_file.read_text().strip()

        self.logger.warning("[WARNING] Telegram bot token not found")
        return None

    def _get_chat_id(self) -> str | None:
        """Get Telegram chat ID"""

        # Try environment variable first
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if chat_id:
            return chat_id

        # Try keys file
        chat_file = self.eq12_home / "keys" / "telegram_chat_id.txt"
        if chat_file.exists():
            return chat_file.read_text().strip()

        self.logger.warning("[WARNING] Telegram chat ID not found")
        return None

    def _initialize_appletv_components(self):
        """Initialize Apple TV manager and streaming engine"""

        try:
            # Import Apple TV components
            sys.path.append(str(self.appletv_dir))
            from eq12_appletv_manager import EQ12AppleTVManager
            from eq12_streaming_engine import EQ12StreamingEngine

            self.appletv_manager = EQ12AppleTVManager()
            self.streaming_engine = EQ12StreamingEngine()

            self.logger.info("[SUCCESS] Apple TV components initialized")

        except Exception as e:
            self.logger.error(f"[ERROR] Failed to initialize Apple TV components: {e}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""

        welcome_message = """
[TARGET] **EQ12 Apple TV Command Center**

Transform your Apple TV into a real-time dashboard for:
[TV] Betting slips and parlay tickets
✈️ Travel deals and flight alerts
[METRICS] Sales dashboards and commerce stats
[HOME] Smart home automation triggers

**Available Commands:**
/sendtv_parlay - Send latest parlay to Apple TV
/sendtv_deals - Stream travel deals slideshow
/sendtv_sales - Display sales dashboard
/appletv_devices - Show discovered Apple TVs
/appletv_status - Check streaming status
/homekit_lights <color> - Control HomeKit lights

Ready to stream! [TV]✨
        """

        await update.message.reply_text(welcome_message, parse_mode="Markdown")

        # Log command usage
        self._log_command_usage("start", update.effective_user.id, {})

    async def sendtv_parlay_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sendtv_parlay command"""

        await update.message.reply_text("[TARGET] Generating parlay for Apple TV...")

        try:
            # Get latest parlay data (mock for demo)
            parlay_data = await self._get_latest_parlay()

            if not parlay_data:
                await update.message.reply_text("[ERROR] No recent parlays found")
                return

            # Generate Apple TV content
            if self.appletv_manager:
                content = self.appletv_manager.generate_betting_slip_content(parlay_data)

                # Stream to Apple TVs
                success_count = await self._stream_to_all_devices(content)

                if success_count > 0:
                    await update.message.reply_text(
                        f"[TV] Parlay streamed to {success_count} Apple TV(s)!\n"
                        f"🎲 {parlay_data['bet_count']} legs • {parlay_data['total_odds']}x odds\n"
                        f"💰 Risk: ${parlay_data['risk_amount']} • Win: ${parlay_data['potential_win']}"
                    )
                else:
                    await update.message.reply_text("[ERROR] Failed to stream to Apple TV")
            else:
                await update.message.reply_text("[ERROR] Apple TV manager not available")

        except Exception as e:
            self.logger.error(f"Error in sendtv_parlay: {e}")
            await update.message.reply_text(f"[ERROR] Error: {e!s}")

        self._log_command_usage(
            "sendtv_parlay", update.effective_user.id, {"success": success_count > 0}
        )

    async def sendtv_deals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sendtv_deals command"""

        await update.message.reply_text("✈️ Loading travel deals for Apple TV...")

        try:
            # Get travel deals data
            deals_data = await self._get_travel_deals()

            if not deals_data:
                await update.message.reply_text("[ERROR] No travel deals found")
                return

            # Generate Apple TV content
            if self.appletv_manager:
                content = self.appletv_manager.generate_travel_deals_content(deals_data)

                # Stream to Apple TVs
                success_count = await self._stream_to_all_devices(content)

                if success_count > 0:
                    deals_summary = f"{len(deals_data)} deals found:\n"
                    for deal in deals_data[:3]:  # Show first 3
                        deals_summary += (
                            f"✈️ {deal['departure']} → {deal['destination']}: ${deal['price']}\n"
                        )

                    await update.message.reply_text(
                        f"[TV] Travel deals streamed to {success_count} Apple TV(s)!\n\n{deals_summary}"
                    )
                else:
                    await update.message.reply_text("[ERROR] Failed to stream to Apple TV")
            else:
                await update.message.reply_text("[ERROR] Apple TV manager not available")

        except Exception as e:
            self.logger.error(f"Error in sendtv_deals: {e}")
            await update.message.reply_text(f"[ERROR] Error: {e!s}")

        self._log_command_usage(
            "sendtv_deals",
            update.effective_user.id,
            {"deals_count": len(deals_data) if deals_data else 0},
        )

    async def sendtv_sales_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sendtv_sales command"""

        await update.message.reply_text("[METRICS] Loading sales dashboard for Apple TV...")

        try:
            # Get sales data
            sales_data = await self._get_sales_dashboard_data()

            if not sales_data:
                await update.message.reply_text("[ERROR] No sales data available")
                return

            # Generate Apple TV content
            if self.appletv_manager:
                content = self.appletv_manager.generate_sales_dashboard_content(sales_data)

                # Stream to Apple TVs
                success_count = await self._stream_to_all_devices(content)

                if success_count > 0:
                    # Calculate summary stats
                    total_revenue = sum(
                        float(metric["value"].replace("$", "").replace(",", ""))
                        for metric in sales_data.get("metrics", [])
                        if "$" in metric["value"]
                    )

                    await update.message.reply_text(
                        f"[TV] Sales dashboard streamed to {success_count} Apple TV(s)!\n"
                        f"💰 Total Revenue: ${total_revenue:,.2f}\n"
                        f"[CHART] {len(sales_data.get('metrics', []))} metrics displayed"
                    )
                else:
                    await update.message.reply_text("[ERROR] Failed to stream to Apple TV")
            else:
                await update.message.reply_text("[ERROR] Apple TV manager not available")

        except Exception as e:
            self.logger.error(f"Error in sendtv_sales: {e}")
            await update.message.reply_text(f"[ERROR] Error: {e!s}")

        self._log_command_usage("sendtv_sales", update.effective_user.id, {})

    async def appletv_devices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /appletv_devices command"""

        try:
            if not self.streaming_engine:
                await update.message.reply_text("[ERROR] Streaming engine not available")
                return

            # Discover devices
            await self.streaming_engine.start_device_discovery()
            await asyncio.sleep(3)  # Wait for discovery

            devices = self.streaming_engine.discovered_devices

            if devices:
                device_list = "[TV] **Discovered Apple TVs:**\n\n"
                for _device_id, device in devices.items():
                    status_emoji = (
                        "🟢"
                        if device.status == "available"
                        else "🔴" if device.status == "streaming" else "🟡"
                    )
                    device_list += f"{status_emoji} **{device.name}**\n"
                    device_list += f"   📍 IP: {device.ip_address}\n"
                    device_list += f"   [SOCKET] Status: {device.status}\n"
                    device_list += f"   [POWER] Capabilities: {', '.join(device.capabilities)}\n\n"

                await update.message.reply_text(device_list, parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    "[ERROR] No Apple TVs found on network.\n"
                    "Make sure Apple TVs are on same network and AirPlay is enabled."
                )

        except Exception as e:
            self.logger.error(f"Error in appletv_devices: {e}")
            await update.message.reply_text(f"[ERROR] Error discovering devices: {e!s}")

        self._log_command_usage(
            "appletv_devices",
            update.effective_user.id,
            {"devices_found": len(devices) if devices else 0},
        )

    async def appletv_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /appletv_status command"""

        try:
            if not self.streaming_engine:
                await update.message.reply_text("[ERROR] Streaming engine not available")
                return

            # Get status info
            devices_count = len(self.streaming_engine.discovered_devices)
            sessions_count = len(self.streaming_engine.active_sessions)

            status_message = f"""
[TV] **EQ12 Apple TV Status**

[SEARCH] **Discovered Devices:** {devices_count}
[STREAM] **Active Sessions:** {sessions_count}
[WEB] **Content Server:** http://localhost:{self.streaming_engine.content_server_port}
[SOCKET] **WebSocket Server:** ws://localhost:{self.streaming_engine.websocket_port}

**Recent Activity:**
            """

            # Add recent sessions
            if self.streaming_engine.active_sessions:
                for _session_id, session in list(self.streaming_engine.active_sessions.items())[
                    -3:
                ]:
                    status_message += f"\n[TARGET] {session.content_type} → {session.device.name}"
                    status_message += (
                        f"\n   [TIME] Started: {session.start_time.strftime('%H:%M:%S')}"
                    )
                    status_message += f"\n   [CHART] Status: {session.status}\n"
            else:
                status_message += "\n_No recent streaming activity_"

            await update.message.reply_text(status_message, parse_mode="Markdown")

        except Exception as e:
            self.logger.error(f"Error in appletv_status: {e}")
            await update.message.reply_text(f"[ERROR] Error getting status: {e!s}")

        self._log_command_usage("appletv_status", update.effective_user.id, {})

    async def homekit_lights_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /homekit_lights command"""

        if not context.args:
            await update.message.reply_text(
                "💡 Usage: /homekit_lights <color>\n"
                "Available colors: red, green, blue, purple, yellow, white, off"
            )
            return

        color = context.args[0].lower()
        valid_colors = ["red", "green", "blue", "purple", "yellow", "white", "off"]

        if color not in valid_colors:
            await update.message.reply_text(
                f"[ERROR] Invalid color. Use: {', '.join(valid_colors)}"
            )
            return

        try:
            # Trigger HomeKit automation
            if self.appletv_manager:
                await self.appletv_manager._trigger_homekit_automation(
                    f"manual_lights_{color}", {"color": color, "source": "telegram"}
                )

                await update.message.reply_text(f"💡 HomeKit lights set to {color}")
            else:
                await update.message.reply_text("[ERROR] Apple TV manager not available")

        except Exception as e:
            self.logger.error(f"Error in homekit_lights: {e}")
            await update.message.reply_text(f"[ERROR] Error controlling lights: {e!s}")

        self._log_command_usage("homekit_lights", update.effective_user.id, {"color": color})

    async def _stream_to_all_devices(self, content) -> int:
        """Stream content to all available Apple TVs"""

        if not self.streaming_engine:
            return 0

        success_count = 0

        for device in self.streaming_engine.discovered_devices.values():
            if device.status == "available":
                try:
                    success = await self.streaming_engine.stream_content_to_device(
                        device, content.content_type, content.data
                    )

                    if success:
                        success_count += 1

                except Exception as e:
                    self.logger.error(f"Failed to stream to {device.name}: {e}")

        return success_count

    async def _get_latest_parlay(self) -> dict[str, Any] | None:
        """Get latest parlay data from EQ12 backend"""

        try:
            # Try to get from EQ12 API
            response = requests.get("http://localhost:8000/api/parlay?size=3", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {
                    "id": data.get("id", f"parlay_{int(time.time())}"),
                    "title": "EQ12 LIVE PARLAY",
                    "bet_count": len(data.get("bets", [])),
                    "total_odds": data.get("total_odds", 0),
                    "risk_amount": data.get("risk_amount", 100),
                    "potential_win": data.get("potential_win", 0),
                    "bets": data.get("bets", []),
                }
        except:
            pass

        # Fallback to mock data
        return {
            "id": f"parlay_{int(time.time())}",
            "title": "EQ12 DEMO PARLAY",
            "bet_count": 3,
            "total_odds": 8.5,
            "risk_amount": 100,
            "potential_win": 850,
            "bets": [
                {
                    "team": "Buffalo Bills",
                    "type": "Spread",
                    "selection": "Bills -3.5",
                    "odds": "-110",
                },
                {
                    "team": "Kansas City Chiefs",
                    "type": "Moneyline",
                    "selection": "Chiefs ML",
                    "odds": "-140",
                },
                {
                    "team": "Over 49.5",
                    "type": "Total",
                    "selection": "Over 49.5",
                    "odds": "-105",
                },
            ],
        }

    async def _get_travel_deals(self) -> list[dict[str, Any]]:
        """Get travel deals data"""

        # Mock travel deals data
        return [
            {
                "departure": "Buffalo",
                "destination": "Miami",
                "price": 89,
                "dates": "Nov 15-22",
                "duration": "7 days",
                "stops": "Nonstop",
                "urgent": True,
            },
            {
                "departure": "Buffalo",
                "destination": "Las Vegas",
                "price": 129,
                "dates": "Dec 1-5",
                "duration": "4 days",
                "stops": "1 stop",
                "urgent": False,
            },
            {
                "departure": "Buffalo",
                "destination": "Orlando",
                "price": 67,
                "dates": "Nov 8-15",
                "duration": "7 days",
                "stops": "Nonstop",
                "urgent": True,
            },
        ]

    async def _get_sales_dashboard_data(self) -> dict[str, Any]:
        """Get sales dashboard data"""

        # Mock sales data
        return {
            "metrics": [
                {"label": "Daily Revenue", "value": "$2,347", "change": 18.5},
                {"label": "Active Listings", "value": "47", "change": 12.3},
                {"label": "Conversion Rate", "value": "15.7%", "change": -3.2},
                {"label": "eBay Sales", "value": "$1,456", "change": 25.1},
                {"label": "Etsy Revenue", "value": "$623", "change": 8.9},
                {"label": "Turo Earnings", "value": "$268", "change": -5.7},
            ],
            "ticker_message": "🔥 Top seller: Vintage Lens Set (+$450) • [METRICS] eBay trending: Photography Equipment • [POWER] Flash sale: 25% off electronics",
        }

    def _log_command_usage(self, command: str, user_id: int, metadata: dict[str, Any]):
        """Log command usage for analytics"""

        log_entry = {
            "command": command,
            "user_id": user_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "metadata": metadata,
        }

        log_file = self.logs_dir / "command_usage.json"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    async def setup_bot_application(self) -> Application | None:
        """Setup Telegram bot application with handlers"""

        if not self.bot_token:
            self.logger.error("[ERROR] Bot token not available")
            return None

        # Create application
        application = Application.builder().token(self.bot_token).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("sendtv_parlay", self.sendtv_parlay_command))
        application.add_handler(CommandHandler("sendtv_deals", self.sendtv_deals_command))
        application.add_handler(CommandHandler("sendtv_sales", self.sendtv_sales_command))
        application.add_handler(CommandHandler("appletv_devices", self.appletv_devices_command))
        application.add_handler(CommandHandler("appletv_status", self.appletv_status_command))
        application.add_handler(CommandHandler("homekit_lights", self.homekit_lights_command))

        self.logger.info("[SUCCESS] Telegram bot handlers configured")
        return application


async def run_telegram_appletv_bot():
    """Run the Telegram Apple TV bot"""

    print("🤖 EQ12 Telegram Apple TV Bot")
    print("   Real-time Apple TV control via Telegram")

    # Initialize bot
    bot = EQ12TelegramAppleTVBot()

    # Setup application
    application = await bot.setup_bot_application()

    if not application:
        print("[ERROR] Failed to setup Telegram bot")
        return

    # Start streaming services
    if bot.streaming_engine:
        await bot.streaming_engine.start_streaming_services()

    print("[SUCCESS] Telegram bot ready!")
    print(f"   [TELEGRAM] Bot token: {bot.bot_token[:10]}...")
    print(f"   💬 Chat ID: {bot.chat_id}")
    print(f"   [TV] Apple TV integration: {'[SUCCESS]' if bot.appletv_manager else '[ERROR]'}")

    print("\n[LAUNCH] Available Commands:")
    commands = [
        "/start - Welcome message and command list",
        "/sendtv_parlay - Stream betting parlay to Apple TV",
        "/sendtv_deals - Stream travel deals slideshow",
        "/sendtv_sales - Stream sales dashboard",
        "/appletv_devices - Show discovered Apple TVs",
        "/appletv_status - Check streaming status",
        "/homekit_lights <color> - Control HomeKit lights",
    ]

    for command in commands:
        print(f"   {command}")

    # Run bot
    try:
        await application.run_polling(drop_pending_updates=True)
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"[ERROR] Bot error: {e}")
    finally:
        if bot.streaming_engine:
            await bot.streaming_engine.stop_streaming_services()


if __name__ == "__main__":
    if not TELEGRAM_AVAILABLE:
        print("[ERROR] Missing Telegram dependencies. Install with:")
        print("   pip install python-telegram-bot")
        sys.exit(1)

    asyncio.run(run_telegram_appletv_bot())
