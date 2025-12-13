#!/usr/bin/env python3
"""
EQ12 Apple TV Master Launcher

Comple        # Setup logging with safe encoding for Windows console
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            handlers=[
                logging.FileHandler(self.logs_dir / "master_launcher.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ],
            force=True
        )
        self.logger = logging.getLogger("AppleTVMaster")ration system for Apple TV command center:
- Automated startup of all Apple TV services
- Real-time content streaming coordination
- Telegram bot integration with live monitoring
- Smart home automation and HomeKit integration
- Performance monitoring and health checks
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
APPLETV_DIR = EQ12_HOME / "appletv_system"
MASTER_LOGS_DIR = EQ12_HOME / "logs" / "appletv_master"

# Ensure directories exist
MASTER_LOGS_DIR.mkdir(parents=True, exist_ok=True)


class EQ12AppleTVMasterController:
    """Master controller for complete Apple TV automation system"""

    def __init__(self):
        self.eq12_home = EQ12_HOME
        self.appletv_dir = APPLETV_DIR
        self.logs_dir = MASTER_LOGS_DIR

        # Component status tracking
        self.services_status = {
            "appletv_manager": {"status": "stopped", "process": None},
            "streaming_engine": {"status": "stopped", "process": None},
            "telegram_bot": {"status": "stopped", "process": None},
            "content_server": {"status": "stopped", "process": None},
            "websocket_server": {"status": "stopped", "process": None},
        }

        # Performance metrics
        self.performance_metrics = {
            "devices_discovered": 0,
            "content_streams": 0,
            "telegram_commands": 0,
            "homekit_triggers": 0,
            "uptime_start": None,
        }

        # Auto-streaming configuration
        self.auto_stream_config = {
            "parlay_notifications": True,
            "travel_deals_updates": True,
            "sales_dashboard_refresh": True,
            "homekit_automation": True,
            "stream_interval_minutes": 15,
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(self.logs_dir / "master_controller.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("AppleTVMaster")

    async def start_complete_system(self):
        """Start complete Apple TV command center system"""

        self.logger.info("[LAUNCH] Starting EQ12 Apple TV Command Center System")

        # Set uptime tracking
        self.performance_metrics["uptime_start"] = datetime.now(UTC)

        # Start services in order
        services_to_start = [
            ("content_server", self._start_content_server),
            ("websocket_server", self._start_websocket_server),
            ("streaming_engine", self._start_streaming_engine),
            ("appletv_manager", self._start_appletv_manager),
            ("telegram_bot", self._start_telegram_bot),
        ]

        for service_name, start_func in services_to_start:
            try:
                await start_func()
                self.services_status[service_name]["status"] = "running"
                self.logger.info(f"[SUCCESS] {service_name} started successfully")
                await asyncio.sleep(2)  # Brief delay between services

            except Exception as e:
                self.logger.error(f"[ERROR] Failed to start {service_name}: {e}")
                self.services_status[service_name]["status"] = "failed"

        # Start auto-streaming if configured
        if any(self.auto_stream_config.values()):
            asyncio.create_task(self._auto_streaming_loop())

        # Start health monitoring
        asyncio.create_task(self._health_monitoring_loop())

        self.logger.info("[TARGET] Apple TV Command Center System Ready!")
        await self._display_system_status()

    async def _start_content_server(self):
        """Start content server"""

        from eq12_streaming_engine import EQ12StreamingEngine

        engine = EQ12StreamingEngine()
        await engine.start_content_server()

        self.services_status["content_server"]["engine"] = engine

    async def _start_websocket_server(self):
        """Start WebSocket server"""

        if "engine" in self.services_status["content_server"]:
            engine = self.services_status["content_server"]["engine"]
            await engine.start_websocket_server()

            self.services_status["websocket_server"]["engine"] = engine

    async def _start_streaming_engine(self):
        """Start streaming engine with device discovery"""

        from eq12_streaming_engine import EQ12StreamingEngine

        if "engine" in self.services_status["content_server"]:
            engine = self.services_status["content_server"]["engine"]
        else:
            engine = EQ12StreamingEngine()

        await engine.start_streaming_services()

        # Wait for device discovery
        await asyncio.sleep(5)

        self.performance_metrics["devices_discovered"] = len(engine.discovered_devices)
        self.services_status["streaming_engine"]["engine"] = engine

    async def _start_appletv_manager(self):
        """Start Apple TV manager"""

        from eq12_appletv_manager import EQ12AppleTVManager

        manager = EQ12AppleTVManager()

        # Discover devices
        devices = manager.discover_apple_tvs()
        self.performance_metrics["devices_discovered"] = max(
            self.performance_metrics["devices_discovered"], len(devices)
        )

        self.services_status["appletv_manager"]["manager"] = manager

    async def _start_telegram_bot(self):
        """Start Telegram bot"""

        from eq12_telegram_appletv_bot import EQ12TelegramAppleTVBot

        bot = EQ12TelegramAppleTVBot()
        application = await bot.setup_bot_application()

        if application:
            # Start bot in background task
            bot_task = asyncio.create_task(application.run_polling(drop_pending_updates=True))

            self.services_status["telegram_bot"]["bot"] = bot
            self.services_status["telegram_bot"]["application"] = application
            self.services_status["telegram_bot"]["task"] = bot_task
        else:
            raise Exception("Failed to setup Telegram bot")

    async def _auto_streaming_loop(self):
        """Automated content streaming loop"""

        self.logger.info("[REFRESH] Starting auto-streaming loop")

        while True:
            try:
                current_time = datetime.now()

                # Check if it's time for scheduled content
                if current_time.minute % self.auto_stream_config["stream_interval_minutes"] == 0:
                    # Auto-stream parlay if available
                    if self.auto_stream_config["parlay_notifications"]:
                        await self._auto_stream_parlay()

                    # Auto-stream travel deals
                    if self.auto_stream_config["travel_deals_updates"]:
                        await self._auto_stream_travel_deals()

                    # Auto-stream sales dashboard
                    if self.auto_stream_config["sales_dashboard_refresh"]:
                        await self._auto_stream_sales_dashboard()

                # Wait 60 seconds before next check
                await asyncio.sleep(60)

            except Exception as e:
                self.logger.error(f"Auto-streaming error: {e}")
                await asyncio.sleep(60)

    async def _auto_stream_parlay(self):
        """Auto-stream parlay content"""

        try:
            if "manager" in self.services_status["appletv_manager"]:
                manager = self.services_status["appletv_manager"]["manager"]

                # Get latest parlay (mock for demo)
                parlay_data = {
                    "id": f"auto_parlay_{int(time.time())}",
                    "title": "🔥 EQ12 AUTO PARLAY",
                    "bet_count": 3,
                    "total_odds": 12.8,
                    "risk_amount": 100,
                    "potential_win": 1280,
                    "bets": [
                        {
                            "team": "Buffalo Bills",
                            "type": "Spread",
                            "selection": "Bills -6.5",
                            "odds": "+105",
                        },
                        {
                            "team": "Kansas City Chiefs",
                            "type": "Moneyline",
                            "selection": "Chiefs ML",
                            "odds": "-165",
                        },
                        {
                            "team": "Over 51.5",
                            "type": "Total",
                            "selection": "Over 51.5",
                            "odds": "-110",
                        },
                    ],
                }

                content = manager.generate_betting_slip_content(parlay_data)
                await manager.add_content_to_queue(content)

                self.performance_metrics["content_streams"] += 1
                self.logger.info("[TV] Auto-streamed parlay content")

        except Exception as e:
            self.logger.error(f"Auto-parlay streaming failed: {e}")

    async def _auto_stream_travel_deals(self):
        """Auto-stream travel deals"""

        try:
            if "manager" in self.services_status["appletv_manager"]:
                manager = self.services_status["appletv_manager"]["manager"]

                # Mock travel deals with time-based variety
                hour = datetime.now().hour
                deals_data = [
                    {
                        "departure": "Buffalo",
                        "destination": "Miami" if hour < 12 else "Los Angeles",
                        "price": 89 + (hour * 2),
                        "dates": "Dec 10-17",
                        "duration": "7 days",
                        "stops": "Nonstop",
                        "urgent": hour % 4 == 0,
                    },
                    {
                        "departure": "Buffalo",
                        "destination": "Las Vegas",
                        "price": 129 + (hour * 3),
                        "dates": "Nov 28-Dec 2",
                        "duration": "4 days",
                        "stops": "1 stop",
                        "urgent": False,
                    },
                ]

                content = manager.generate_travel_deals_content(deals_data)
                await manager.add_content_to_queue(content)

                self.performance_metrics["content_streams"] += 1
                self.logger.info("✈️ Auto-streamed travel deals")

        except Exception as e:
            self.logger.error(f"Auto-travel streaming failed: {e}")

    async def _auto_stream_sales_dashboard(self):
        """Auto-stream sales dashboard"""

        try:
            if "manager" in self.services_status["appletv_manager"]:
                manager = self.services_status["appletv_manager"]["manager"]

                # Generate dynamic sales data
                import random

                sales_data = {
                    "metrics": [
                        {
                            "label": "Daily Revenue",
                            "value": f"${random.randint(1500, 3500):,}",
                            "change": round(random.uniform(-10, 25), 1),
                        },
                        {
                            "label": "Active Listings",
                            "value": str(random.randint(35, 65)),
                            "change": round(random.uniform(-5, 15), 1),
                        },
                        {
                            "label": "Conversion Rate",
                            "value": f"{random.uniform(10, 20):.1f}%",
                            "change": round(random.uniform(-8, 12), 1),
                        },
                        {
                            "label": "eBay Sales",
                            "value": f"${random.randint(800, 2000):,}",
                            "change": round(random.uniform(-5, 30), 1),
                        },
                        {
                            "label": "Etsy Revenue",
                            "value": f"${random.randint(200, 800):,}",
                            "change": round(random.uniform(-10, 20), 1),
                        },
                        {
                            "label": "Turo Earnings",
                            "value": f"${random.randint(100, 400):,}",
                            "change": round(random.uniform(-15, 25), 1),
                        },
                    ],
                    "ticker_message": f"🔥 Hot item: Vintage Camera (+${random.randint(200, 500)}) • [METRICS] Trending: Electronics • [POWER] {random.randint(5, 25)} views in last hour",
                }

                content = manager.generate_sales_dashboard_content(sales_data)
                await manager.add_content_to_queue(content)

                self.performance_metrics["content_streams"] += 1
                self.logger.info("[METRICS] Auto-streamed sales dashboard")

        except Exception as e:
            self.logger.error(f"Auto-sales streaming failed: {e}")

    async def _health_monitoring_loop(self):
        """Monitor system health and performance"""

        self.logger.info("[HEALTH] Starting health monitoring")

        while True:
            try:
                # Check service status
                for service_name, service_info in self.services_status.items():
                    if service_info["status"] == "running":
                        # Perform service-specific health checks
                        if service_name == "telegram_bot" and "task" in service_info:
                            task = service_info["task"]
                            if task.done() or task.cancelled():
                                self.logger.warning(
                                    f"[WARNING] {service_name} task completed unexpectedly"
                                )
                                service_info["status"] = "failed"

                # Log performance metrics
                uptime = None
                if self.performance_metrics["uptime_start"]:
                    uptime = datetime.now(UTC) - self.performance_metrics["uptime_start"]

                health_report = {
                    "timestamp": datetime.now(UTC).isoformat(),
                    "services_running": sum(
                        1 for s in self.services_status.values() if s["status"] == "running"
                    ),
                    "total_services": len(self.services_status),
                    "uptime_seconds": uptime.total_seconds() if uptime else 0,
                    "performance_metrics": self.performance_metrics.copy(),
                }

                # Save health report
                health_file = (
                    self.logs_dir / f"health_report_{datetime.now().strftime('%Y%m%d')}.json"
                )
                with open(health_file, "a") as f:
                    f.write(json.dumps(health_report) + "\n")

                # Wait 5 minutes before next check
                await asyncio.sleep(300)

            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(300)

    async def _display_system_status(self):
        """Display comprehensive system status"""

        print("\n" + "=" * 60)
        print("[TARGET] EQ12 APPLE TV COMMAND CENTER - SYSTEM STATUS")
        print("=" * 60)

        # Services status
        print("\n[CHART] SERVICES STATUS:")
        for _service_name, service_info in self.services_status.items():
            (
                "[SUCCESS]"
                if service_info["status"] == "running"
                else "[ERROR]" if service_info["status"] == "failed" else "⏸️"
            )
            print(
                "   {status_emoji} {service_name.replace('_', ' ').title()}: {service_info['status']}"
            )

        # Performance metrics
        print("\n[METRICS] PERFORMANCE METRICS:")
        print("   [TV] Apple TVs Discovered: {self.performance_metrics['devices_discovered']}")
        print("   [STREAM] Content Streams: {self.performance_metrics['content_streams']}")
        print("   [TELEGRAM] Telegram Commands: {self.performance_metrics['telegram_commands']}")
        print("   [HOME] HomeKit Triggers: {self.performance_metrics['homekit_triggers']}")

        if self.performance_metrics["uptime_start"]:
            datetime.now(UTC) - self.performance_metrics["uptime_start"]
            print("   [TIME] Uptime: {str(uptime).split('.')[0]}")

        # Auto-streaming configuration
        print("\n[REFRESH] AUTO-STREAMING CONFIG:")
        for config_name, _enabled in self.auto_stream_config.items():
            if config_name != "stream_interval_minutes":
                print("   {status_emoji} {config_name.replace('_', ' ').title()}: {enabled}")

        print(
            "   [TIME] Stream Interval: {self.auto_stream_config['stream_interval_minutes']} minutes"
        )

        # System URLs
        print("\n[WEB] ACCESS URLS:")
        print("   [TV] Content Server: http://localhost:8080")
        print("   [SOCKET] WebSocket: ws://localhost:8081")
        print("   [TELEGRAM] Telegram Bot: Active (check your Telegram)")

        # Quick usage examples
        print("\n[LAUNCH] QUICK USAGE:")
        print("   Send to Telegram: /sendtv_parlay")
        print("   Check devices: /appletv_devices")
        print("   System status: /appletv_status")

        print("\n" + "=" * 60)
        print("[READY] System Ready! Send commands via Telegram or use API endpoints.")
        print("=" * 60 + "\n")

    async def shutdown_system(self):
        """Gracefully shutdown all services"""

        self.logger.info("🛑 Shutting down Apple TV Command Center system")

        # Stop services in reverse order
        for service_name in reversed(list(self.services_status.keys())):
            try:
                service_info = self.services_status[service_name]

                if service_name == "telegram_bot" and "task" in service_info:
                    service_info["task"].cancel()

                if "engine" in service_info:
                    await service_info["engine"].stop_streaming_services()

                service_info["status"] = "stopped"
                self.logger.info(f"[SUCCESS] Stopped {service_name}")

            except Exception as e:
                self.logger.error(f"Error stopping {service_name}: {e}")

        self.logger.info("[SUCCESS] System shutdown complete")


async def main():
    """Main entry point for Apple TV Command Center"""

    print("[LAUNCH] EQ12 Apple TV Command Center Master Launcher")
    print("   Complete automation system for Apple TV integration")

    # Check dependencies
    try:
        # Import required modules to check availability
        sys.path.append(str(APPLETV_DIR))
        from eq12_appletv_manager import EQ12AppleTVManager
        from eq12_streaming_engine import EQ12StreamingEngine
        from eq12_telegram_appletv_bot import EQ12TelegramAppleTVBot

    except ImportError:
        print("[ERROR] Missing dependencies: {e}")
        print(
            "   Run: pip install requests pystray pillow qrcode2 jinja2 websockets python-telegram-bot zeroconf netifaces"
        )
        return

    # Initialize master controller
    controller = EQ12AppleTVMasterController()

    try:
        # Start complete system
        await controller.start_complete_system()

        # Keep running
        while True:
            await asyncio.sleep(60)

    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception:
        print("[ERROR] System error: {e}")
    finally:
        await controller.shutdown_system()


if __name__ == "__main__":
    asyncio.run(main())
