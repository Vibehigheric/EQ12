#!/usr/bin/env python3
"""
EQ12 Ngrok Tunnel Stability Monitor
==================================

Advanced monitoring system for ngrok tunnel health, stability, and auto-recovery.
Provides comprehensive logging, metrics, and automated reconnection capabilities.

Features:
- Real-time tunnel status monitoring
- Health metrics and uptime tracking
- Automatic reconnection with exponential backoff
- Comprehensive logging and alerting
- Integration with EQ12 dashboard system
- Windows service compatibility

Author: EQ12 GODSTACK System
Version: 1.0.0
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import aiohttp
import psutil
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class TunnelStatus:
    """Data class for tunnel status information."""

    is_running: bool = False
    process_id: int | None = None
    public_url: str | None = None
    local_port: int = 8080
    api_port: int = 4040
    uptime_seconds: float = 0.0
    last_check: datetime | None = None
    error_count: int = 0
    reconnect_count: int = 0
    health_score: float = 100.0


@dataclass
class MonitorConfig:
    """Configuration for tunnel monitoring."""

    check_interval: int = 30  # seconds
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    max_error_count: int = 5
    restart_threshold: int = 10  # errors before restart
    log_level: str = "INFO"
    enable_alerts: bool = True
    dashboard_integration: bool = True


class NgrokTunnelMonitor:
    """
    Advanced ngrok tunnel monitoring and management system.

    Provides comprehensive tunnel health monitoring with automatic
    recovery, detailed logging, and integration with EQ12 systems.
    """

    def __init__(self, config: MonitorConfig | None = None):
        """Initialize the tunnel monitor with configuration."""
        self.config = config or MonitorConfig()
        self.status = TunnelStatus()
        self.eq12_root = Path(os.getenv("EQ12_ROOT", "C:/EQ12"))
        self.logs_dir = self.eq12_root / "logs"
        self.reports_dir = self.eq12_root / "reports"

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # Setup logging
        self.logger = self._setup_logging()
        self.session = self._setup_http_session()

        # Monitoring state
        self.monitoring = False
        self.start_time = datetime.now()
        self.last_restart_time: datetime | None = None

        self.logger.info("🚀 EQ12 Ngrok Tunnel Monitor initialized")
        self.logger.info(f"📁 EQ12 Root: {self.eq12_root}")
        self.logger.info(f"⚙️ Check interval: {self.config.check_interval}s")

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging for tunnel monitoring."""
        log_file = self.logs_dir / f"ngrok_monitor_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        logger = logging.getLogger(__name__)
        logger.info("📋 Ngrok tunnel monitoring logging initialized")
        logger.info(f"📄 Log file: {log_file}")

        return logger

    def _setup_http_session(self) -> requests.Session:
        """Setup HTTP session with retry logic for API calls."""
        session = requests.Session()

        retry_strategy = Retry(
            total=self.config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def check_ngrok_process(self) -> tuple[bool, int | None, float]:
        """
        Check if ngrok process is running and get uptime.

        Returns:
            Tuple of (is_running, process_id, uptime_seconds)
        """
        try:
            for proc in psutil.process_iter(["pid", "name", "create_time"]):
                if proc.info["name"] and "ngrok" in proc.info["name"].lower():
                    pid = proc.info["pid"]
                    create_time = proc.info["create_time"]
                    uptime = time.time() - create_time

                    self.logger.debug(f"✅ Ngrok process found: PID {pid}, uptime {uptime:.1f}s")
                    return True, pid, uptime

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        self.logger.debug("❌ Ngrok process not found")
        return False, None, 0.0

    async def check_tunnel_api(self) -> tuple[bool, str | None]:
        """
        Check ngrok API for active tunnels.

        Returns:
            Tuple of (api_accessible, public_url)
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(
                    f"http://localhost:{self.status.api_port}/api/tunnels"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        tunnels = data.get("tunnels", [])

                        if tunnels:
                            public_url = tunnels[0].get("public_url")
                            self.logger.debug(f"✅ API accessible, public URL: {public_url}")
                            return True, public_url
                        else:
                            self.logger.debug("⚠️ API accessible but no active tunnels")
                            return True, None
                    else:
                        self.logger.debug(f"❌ API returned status {response.status}")
                        return False, None

        except Exception as e:
            self.logger.debug(f"❌ API check failed: {e}")
            return False, None

    async def test_tunnel_connectivity(self, public_url: str) -> bool:
        """
        Test if the tunnel is accessible from the internet.

        Args:
            public_url: The public URL to test

        Returns:
            True if tunnel is accessible
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(public_url) as response:
                    accessible = response.status < 500
                    self.logger.debug(
                        f"🌐 Tunnel connectivity test: {accessible} (status {response.status})"
                    )
                    return accessible

        except Exception as e:
            self.logger.debug(f"🌐 Tunnel connectivity test failed: {e}")
            return False

    def calculate_health_score(self) -> float:
        """
        Calculate tunnel health score based on various metrics.

        Returns:
            Health score from 0.0 to 100.0
        """
        score = 100.0

        # Deduct points for errors
        if self.status.error_count > 0:
            score -= min(self.status.error_count * 10, 50)

        # Deduct points for recent reconnects
        if self.status.reconnect_count > 0:
            score -= min(self.status.reconnect_count * 5, 30)

        # Bonus for sustained uptime
        if self.status.uptime_seconds > 3600:  # 1 hour
            score = min(score + 5, 100)

        return max(score, 0.0)

    async def perform_health_check(self) -> bool:
        """
        Perform comprehensive tunnel health check.

        Returns:
            True if tunnel is healthy
        """
        self.status.last_check = datetime.now()

        # Check process
        is_running, pid, uptime = self.check_ngrok_process()
        self.status.is_running = is_running
        self.status.process_id = pid
        self.status.uptime_seconds = uptime

        if not is_running:
            self.status.error_count += 1
            self.logger.warning("❌ Ngrok process not running")
            return False

        # Check API
        api_ok, public_url = await self.check_tunnel_api()
        self.status.public_url = public_url

        if not api_ok:
            self.status.error_count += 1
            self.logger.warning("❌ Ngrok API not accessible")
            return False

        if not public_url:
            self.status.error_count += 1
            self.logger.warning("❌ No active tunnels found")
            return False

        # Test connectivity
        if not await self.test_tunnel_connectivity(public_url):
            self.status.error_count += 1
            self.logger.warning("❌ Tunnel not accessible from internet")
            return False

        # All checks passed
        self.status.health_score = self.calculate_health_score()
        self.logger.debug(f"✅ Health check passed (score: {self.status.health_score:.1f})")
        return True

    async def start_ngrok_tunnel(self) -> bool:
        """
        Start ngrok tunnel with EQ12 configuration.

        Returns:
            True if started successfully
        """
        try:
            self.logger.info("🚀 Starting ngrok tunnel...")

            # Kill existing ngrok processes
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] and "ngrok" in proc.info["name"].lower():
                    proc.terminate()
                    self.logger.info(f"🛑 Terminated existing ngrok process: {proc.info['pid']}")

            # Wait a moment for cleanup
            time.sleep(2)

            # Start new tunnel
            cmd = ["ngrok", "http", str(self.status.local_port), "--log=stdout"]

            # Start process in background
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0),
            )

            # Wait for startup
            await asyncio.sleep(5)

            # Verify it started
            is_running, pid, _ = self.check_ngrok_process()
            if is_running:
                self.status.reconnect_count += 1
                self.last_restart_time = datetime.now()
                self.logger.info(f"✅ Ngrok tunnel started successfully (PID: {pid})")
                return True
            else:
                self.logger.error("❌ Failed to start ngrok tunnel")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error starting ngrok tunnel: {e}")
            return False

    async def save_status_report(self) -> None:
        """Save current status to JSON report file."""
        try:
            report_file = (
                self.reports_dir / f"ngrok_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            report_data = {
                "timestamp": datetime.now().isoformat(),
                "monitor_uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "status": asdict(self.status),
                "config": asdict(self.config),
                "last_restart": (
                    self.last_restart_time.isoformat() if self.last_restart_time else None
                ),
            }

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, default=str)

            self.logger.debug(f"💾 Status report saved: {report_file}")

        except Exception as e:
            self.logger.error(f"❌ Failed to save status report: {e}")

    async def monitor_loop(self) -> None:
        """Main monitoring loop."""
        self.logger.info("🔄 Starting ngrok tunnel monitoring loop...")
        self.monitoring = True

        consecutive_failures = 0

        while self.monitoring:
            try:
                # Perform health check
                is_healthy = await self.perform_health_check()

                if is_healthy:
                    consecutive_failures = 0
                    if self.status.error_count > 0:
                        self.status.error_count = max(0, self.status.error_count - 1)

                    self.logger.info(
                        "✅ Tunnel healthy - "
                        f"URL: {self.status.public_url}, "
                        f"Uptime: {self.status.uptime_seconds/3600:.1f}h, "
                        f"Health: {self.status.health_score:.1f}%"
                    )
                else:
                    consecutive_failures += 1
                    self.logger.warning(
                        "⚠️ Tunnel unhealthy - "
                        f"Errors: {self.status.error_count}, "
                        f"Consecutive failures: {consecutive_failures}"
                    )

                    # Auto-restart if needed
                    if consecutive_failures >= self.config.restart_threshold:
                        self.logger.warning(
                            "🔄 Attempting tunnel restart due to persistent failures..."
                        )
                        if await self.start_ngrok_tunnel():
                            consecutive_failures = 0
                        else:
                            await asyncio.sleep(30)  # Wait longer after failed restart

                # Save periodic reports
                if self.status.last_check and self.status.last_check.minute % 10 == 0:
                    await self.save_status_report()

                # Wait for next check
                await asyncio.sleep(self.config.check_interval)

            except KeyboardInterrupt:
                self.logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(self.config.check_interval)

    async def start_monitoring(self) -> None:
        """Start the monitoring system."""
        self.logger.info("🚀 EQ12 Ngrok Tunnel Monitor starting...")

        # Initial health check
        is_healthy = await self.perform_health_check()
        if not is_healthy and not self.status.is_running:
            self.logger.info("🔄 No tunnel detected, starting new tunnel...")
            await self.start_ngrok_tunnel()

        # Start monitoring loop
        await self.monitor_loop()

    def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        self.logger.info("🛑 Stopping ngrok tunnel monitoring...")
        self.monitoring = False


async def main():
    """Main entry point for the monitor."""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Ngrok Tunnel Monitor")
    parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )
    parser.add_argument(
        "--no-restart", action="store_true", help="Disable automatic tunnel restart"
    )

    args = parser.parse_args()

    # Create configuration
    config = MonitorConfig(
        check_interval=args.interval,
        log_level=args.log_level,
        restart_threshold=999 if args.no_restart else 10,
    )

    # Create and start monitor
    monitor = NgrokTunnelMonitor(config)

    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\n🛑 Monitor stopped by user")


if __name__ == "__main__":
    asyncio.run(main())
