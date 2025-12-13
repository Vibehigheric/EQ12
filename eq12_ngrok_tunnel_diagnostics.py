# eq12_ngrok_tunnel_diagnostics.py
"""
EQ12 Ngrok Tunnel Diagnostics and Management System
Automated tunnel monitoring, health checks, and failover management
"""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil
import requests

from eq12_helpers import setup_utf8_logging

setup_utf8_logging()


@dataclass
class TunnelStatus:
    """Ngrok tunnel status information"""

    name: str
    public_url: str
    local_url: str
    proto: str
    status: str
    connections: int
    bytes_in: int
    bytes_out: int
    started_at: str
    last_check: str
    latency_ms: float = 0.0
    error_count: int = 0
    uptime_percentage: float = 100.0


@dataclass
class TunnelHealth:
    """Tunnel health metrics"""

    tunnel_name: str
    is_healthy: bool
    response_time_ms: float
    status_code: int
    last_success: str
    error_message: str | None = None
    consecutive_failures: int = 0
    uptime_minutes: float = 0.0


class NgrokDiagnostics:
    """Comprehensive Ngrok tunnel diagnostics"""

    def __init__(self, ngrok_config_path: str = "C:/EQ12/configs/ngrok.yml"):
        self.config_path = Path(ngrok_config_path)
        self.tunnels: dict[str, TunnelStatus] = {}
        self.health_history: list[TunnelHealth] = []
        self.monitoring = False
        self.ngrok_process = None

        # Load configuration
        self.config = self._load_ngrok_config()

    def _load_ngrok_config(self) -> dict[str, Any]:
        """Load Ngrok configuration"""
        try:
            if self.config_path.exists():
                import yaml

                with open(self.config_path) as f:
                    return yaml.safe_load(f)
            else:
                logging.warning(f"Ngrok config not found: {self.config_path}")
                return self._create_default_config()
        except Exception as e:
            logging.error(f"Failed to load Ngrok config: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> dict[str, Any]:
        """Create default Ngrok configuration"""
        return {
            "version": "2",
            "authtoken": "YOUR_NGROK_AUTHTOKEN",
            "tunnels": {
                "eq12-dashboard": {
                    "proto": "http",
                    "addr": 3000,
                    "bind_tls": True,
                    "inspect": True,
                },
                "eq12-api": {"proto": "http", "addr": 8081, "bind_tls": True},
                "eq12-websocket": {"proto": "http", "addr": 3001, "bind_tls": True},
            },
        }

    async def start_monitoring(self):
        """Start tunnel monitoring"""
        self.monitoring = True
        logging.info("🔍 Starting Ngrok tunnel monitoring")

        # Start Ngrok if not running
        if not self._is_ngrok_running():
            await self._start_ngrok()

        # Monitor loop
        while self.monitoring:
            try:
                await self._check_all_tunnels()
                await self._update_tunnel_health()
                await self._log_diagnostics()
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)

    async def stop_monitoring(self):
        """Stop tunnel monitoring"""
        self.monitoring = False
        logging.info("⏹️ Stopping Ngrok tunnel monitoring")

    def _is_ngrok_running(self) -> bool:
        """Check if Ngrok process is running"""
        for process in psutil.process_iter(["pid", "name", "cmdline"]):
            if "ngrok" in process.info["name"].lower():
                self.ngrok_process = process
                return True
        return False

    async def _start_ngrok(self):
        """Start Ngrok with configuration"""
        try:
            logging.info("🚀 Starting Ngrok tunnels")

            # Start Ngrok with config file
            cmd = ["ngrok", "start", "--all", "--config", str(self.config_path)]

            self.ngrok_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )

            # Wait for startup
            await asyncio.sleep(5)

            if self.ngrok_process.poll() is None:
                logging.info("✅ Ngrok started successfully")
            else:
                _stdout, stderr = self.ngrok_process.communicate()
                logging.error(f"Ngrok failed to start: {stderr.decode()}")

        except Exception as e:
            logging.error(f"Failed to start Ngrok: {e}")

    async def _check_all_tunnels(self):
        """Check status of all configured tunnels"""

        try:
            # Get tunnel info from Ngrok API
            tunnels_info = await self._get_ngrok_api_info()

            for tunnel_name in self.config.get("tunnels", {}):
                tunnel_info = tunnels_info.get(tunnel_name, {})

                if tunnel_info:
                    await self._check_tunnel_status(tunnel_name, tunnel_info)
                else:
                    # Tunnel not found - may be down
                    self.tunnels[tunnel_name] = TunnelStatus(
                        name=tunnel_name,
                        public_url="",
                        local_url="",
                        proto="",
                        status="offline",
                        connections=0,
                        bytes_in=0,
                        bytes_out=0,
                        started_at="",
                        last_check=datetime.utcnow().isoformat(),
                    )

        except Exception as e:
            logging.error(f"Failed to check tunnels: {e}")

    async def _get_ngrok_api_info(self) -> dict[str, Any]:
        """Get tunnel information from Ngrok local API"""

        try:
            # Ngrok API endpoint
            api_url = "http://localhost:4040/api/tunnels"

            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()

                # Parse tunnel information
                tunnels_info = {}
                for tunnel in data.get("tunnels", []):
                    name = tunnel.get("name", "unnamed")
                    tunnels_info[name] = {
                        "public_url": tunnel.get("public_url", ""),
                        "config": tunnel.get("config", {}),
                        "metrics": tunnel.get("metrics", {}),
                        "started_at": tunnel.get("started_at", ""),
                    }

                return tunnels_info

            logging.warning(f"Ngrok API returned {response.status_code}")
            return {}

        except Exception as e:
            logging.error(f"Failed to query Ngrok API: {e}")
            return {}

    async def _check_tunnel_status(self, tunnel_name: str, tunnel_info: dict[str, Any]):
        """Check individual tunnel status"""

        public_url = tunnel_info.get("public_url", "")
        config = tunnel_info.get("config", {})
        metrics = tunnel_info.get("metrics", {})

        # Create tunnel status
        tunnel_status = TunnelStatus(
            name=tunnel_name,
            public_url=public_url,
            local_url=f"http://localhost:{config.get('addr', 0)}",
            proto=config.get("proto", "http"),
            status="online" if public_url else "offline",
            connections=metrics.get("conns", {}).get("count", 0),
            bytes_in=metrics.get("http", {}).get("bytes_in", 0),
            bytes_out=metrics.get("http", {}).get("bytes_out", 0),
            started_at=tunnel_info.get("started_at", ""),
            last_check=datetime.utcnow().isoformat(),
        )

        # Test tunnel connectivity
        if public_url:
            latency = await self._test_tunnel_connectivity(public_url)
            tunnel_status.latency_ms = latency

        self.tunnels[tunnel_name] = tunnel_status

    async def _test_tunnel_connectivity(self, public_url: str) -> float:
        """Test tunnel connectivity and measure latency"""

        try:
            start_time = time.time()

            # Test with simple health check endpoint
            health_url = f"{public_url}/health"

            response = requests.get(health_url, timeout=10)
            latency = (time.time() - start_time) * 1000  # Convert to ms

            if response.status_code in [200, 404]:  # 404 is OK if no /health endpoint
                return latency
            return -1  # Indicate error

        except Exception as e:
            logging.debug(f"Tunnel connectivity test failed: {e}")
            return -1

    async def _update_tunnel_health(self):
        """Update tunnel health metrics"""

        current_time = datetime.utcnow().isoformat()

        for tunnel_name, tunnel_status in self.tunnels.items():
            is_healthy = (
                tunnel_status.status == "online"
                and tunnel_status.public_url
                and tunnel_status.latency_ms >= 0
                and tunnel_status.latency_ms < 5000  # 5 second timeout
            )

            health = TunnelHealth(
                tunnel_name=tunnel_name,
                is_healthy=is_healthy,
                response_time_ms=tunnel_status.latency_ms,
                status_code=200 if is_healthy else 0,
                last_success=current_time if is_healthy else "",
                error_message=None if is_healthy else "Tunnel unavailable",
                consecutive_failures=0,  # Would track in real implementation
                uptime_minutes=0.0,  # Would calculate from start time
            )

            self.health_history.append(health)

            # Keep only last 100 health checks
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]

    async def _log_diagnostics(self):
        """Log comprehensive tunnel diagnostics"""

        timestamp = datetime.utcnow().isoformat()

        diagnostics = {
            "timestamp": timestamp,
            "ngrok_running": self._is_ngrok_running(),
            "tunnel_count": len(self.tunnels),
            "healthy_tunnels": sum(1 for t in self.tunnels.values() if t.status == "online"),
            "tunnels": {
                name: {
                    "status": tunnel.status,
                    "public_url": tunnel.public_url,
                    "local_url": tunnel.local_url,
                    "latency_ms": tunnel.latency_ms,
                    "connections": tunnel.connections,
                    "bytes_transferred": tunnel.bytes_in + tunnel.bytes_out,
                }
                for name, tunnel in self.tunnels.items()
            },
            "overall_health": self._calculate_overall_health(),
        }

        # Save to log file
        logs_dir = Path("C:/EQ12/logs")
        logs_dir.mkdir(exist_ok=True)

        log_file = logs_dir / f"ngrok_diagnostics_{datetime.utcnow().strftime('%Y%m%d')}.json"

        try:
            # Append to daily log file
            if log_file.exists():
                with open(log_file) as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []

            existing_logs.append(diagnostics)

            # Keep only last 1000 entries
            if len(existing_logs) > 1000:
                existing_logs = existing_logs[-1000:]

            with open(log_file, "w") as f:
                json.dump(existing_logs, f, indent=2)

        except Exception as e:
            logging.error(f"Failed to save diagnostics log: {e}")

        # Log summary to console
        logging.info(
            f"🔍 Tunnel Status: {diagnostics['healthy_tunnels']}/{diagnostics['tunnel_count']} healthy"
        )

    def _calculate_overall_health(self) -> str:
        """Calculate overall tunnel health status"""

        if not self.tunnels:
            return "unknown"

        online_count = sum(1 for t in self.tunnels.values() if t.status == "online")
        total_count = len(self.tunnels)

        if online_count == 0:
            return "critical"
        if online_count < total_count:
            return "degraded"
        # Check latency
        avg_latency = sum(t.latency_ms for t in self.tunnels.values() if t.latency_ms > 0) / max(
            1, online_count
        )

        if avg_latency > 2000:  # 2 seconds
            return "degraded"
        return "healthy"

    async def restart_tunnel(self, tunnel_name: str) -> bool:
        """Restart specific tunnel"""

        try:
            logging.info(f"🔄 Restarting tunnel: {tunnel_name}")

            # Stop specific tunnel
            subprocess.run(["ngrok", "stop", tunnel_name], capture_output=True, timeout=10)

            await asyncio.sleep(2)

            # Start specific tunnel
            subprocess.Popen(["ngrok", "start", tunnel_name, "--config", str(self.config_path)])

            await asyncio.sleep(5)

            logging.info(f"✅ Tunnel restarted: {tunnel_name}")
            return True

        except Exception as e:
            logging.error(f"Failed to restart tunnel {tunnel_name}: {e}")
            return False

    async def restart_all_tunnels(self) -> bool:
        """Restart all Ngrok tunnels"""

        try:
            logging.info("🔄 Restarting all Ngrok tunnels")

            # Stop Ngrok
            if self.ngrok_process:
                self.ngrok_process.terminate()
                await asyncio.sleep(3)

            # Kill any remaining Ngrok processes
            for process in psutil.process_iter(["pid", "name"]):
                if "ngrok" in process.info["name"].lower():
                    process.terminate()

            await asyncio.sleep(2)

            # Restart Ngrok
            await self._start_ngrok()

            logging.info("✅ All tunnels restarted")
            return True

        except Exception as e:
            logging.error(f"Failed to restart all tunnels: {e}")
            return False

    async def get_status_report(self) -> dict[str, Any]:
        """Get comprehensive status report"""

        recent_health = self.health_history[-10:] if self.health_history else []

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "ngrok_running": self._is_ngrok_running(),
            "overall_health": self._calculate_overall_health(),
            "tunnel_summary": {
                "total": len(self.tunnels),
                "online": sum(1 for t in self.tunnels.values() if t.status == "online"),
                "offline": sum(1 for t in self.tunnels.values() if t.status != "online"),
            },
            "tunnels": [
                {
                    "name": tunnel.name,
                    "status": tunnel.status,
                    "public_url": tunnel.public_url,
                    "local_url": tunnel.local_url,
                    "latency_ms": tunnel.latency_ms,
                    "connections": tunnel.connections,
                    "data_transferred_mb": (tunnel.bytes_in + tunnel.bytes_out) / (1024 * 1024),
                }
                for tunnel in self.tunnels.values()
            ],
            "recent_health_checks": [
                {
                    "tunnel": health.tunnel_name,
                    "healthy": health.is_healthy,
                    "response_time_ms": health.response_time_ms,
                    "error": health.error_message,
                }
                for health in recent_health
            ],
            "recommendations": self._get_recommendations(),
        }

    def _get_recommendations(self) -> list[str]:
        """Get tunnel optimization recommendations"""

        recommendations = []

        if not self._is_ngrok_running():
            recommendations.append("Ngrok process is not running - start Ngrok service")

        for tunnel in self.tunnels.values():
            if tunnel.status != "online":
                recommendations.append(
                    f"Tunnel '{tunnel.name}' is offline - check configuration and restart"
                )

            if tunnel.latency_ms > 2000:
                recommendations.append(
                    f"Tunnel '{tunnel.name}' has high latency ({tunnel.latency_ms:.0f}ms) - check network connection"
                )

        if len([t for t in self.tunnels.values() if t.status == "online"]) == 0:
            recommendations.append("All tunnels are offline - restart Ngrok service immediately")

        return recommendations


class TunnelFailover:
    """Automated tunnel failover management"""

    def __init__(self, diagnostics: NgrokDiagnostics):
        self.diagnostics = diagnostics
        self.failover_active = False
        self.retry_attempts = {}

    async def start_failover_monitoring(self):
        """Start automated failover monitoring"""

        logging.info("🛡️ Starting tunnel failover monitoring")

        while True:
            try:
                await self._check_for_failures()
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logging.error(f"Failover monitoring error: {e}")
                await asyncio.sleep(30)

    async def _check_for_failures(self):
        """Check for tunnel failures and initiate recovery"""

        for tunnel_name, tunnel in self.diagnostics.tunnels.items():
            if tunnel.status != "online":
                await self._handle_tunnel_failure(tunnel_name, tunnel)

            elif tunnel.latency_ms > 5000:  # 5 second timeout
                await self._handle_tunnel_degradation(tunnel_name, tunnel)

    async def _handle_tunnel_failure(self, tunnel_name: str, tunnel: TunnelStatus):
        """Handle tunnel failure with automated recovery"""

        if tunnel_name not in self.retry_attempts:
            self.retry_attempts[tunnel_name] = 0

        self.retry_attempts[tunnel_name] += 1
        max_retries = 3

        logging.warning(
            f"🚨 Tunnel failure detected: {tunnel_name} (attempt {self.retry_attempts[tunnel_name]}/{max_retries})"
        )

        if self.retry_attempts[tunnel_name] <= max_retries:
            # Attempt restart
            success = await self.diagnostics.restart_tunnel(tunnel_name)

            if success:
                logging.info(f"✅ Tunnel recovery successful: {tunnel_name}")
                self.retry_attempts[tunnel_name] = 0
            else:
                logging.error(f"❌ Tunnel recovery failed: {tunnel_name}")

        else:
            # Max retries exceeded - try full restart
            logging.critical(
                f"🚨 Max retries exceeded for {tunnel_name} - attempting full Ngrok restart"
            )

            await self.diagnostics.restart_all_tunnels()
            self.retry_attempts = {}  # Reset all retry counts

    async def _handle_tunnel_degradation(self, tunnel_name: str, tunnel: TunnelStatus):
        """Handle tunnel performance degradation"""

        logging.warning(
            f"⚠️ Tunnel degradation detected: {tunnel_name} (latency: {tunnel.latency_ms:.0f}ms)"
        )

        # For now, just log - could implement more sophisticated recovery


async def main():
    """Main diagnostic runner"""

    setup_utf8_logging()
    logging.info("🔍 Starting EQ12 Ngrok Tunnel Diagnostics")

    # Initialize diagnostics
    diagnostics = NgrokDiagnostics()
    failover = TunnelFailover(diagnostics)

    # Start monitoring tasks
    monitoring_task = asyncio.create_task(diagnostics.start_monitoring())
    failover_task = asyncio.create_task(failover.start_failover_monitoring())

    try:
        # Run indefinitely
        await asyncio.gather(monitoring_task, failover_task)

    except KeyboardInterrupt:
        logging.info("⏹️ Stopping Ngrok diagnostics...")
        await diagnostics.stop_monitoring()
        monitoring_task.cancel()
        failover_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
