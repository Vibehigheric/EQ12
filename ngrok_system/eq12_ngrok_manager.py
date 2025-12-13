#!/usr/bin/env python3
"""
EQ12 Ngrok Management System

Complete ngrok tunnel management for EQ12 automation stack:
- Automatic tunnel startup and monitoring
- Health checks and reconnection logic
- Integration with EQ12 services (betting, travel, commerce, finance)
- Secure webhook management for Telegram bots
- Remote access tunnels with authentication
- Performance monitoring and logging
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import requests
    import yaml

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️ Missing dependencies. Run: pip install requests pyyaml")

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
NGROK_DIR = EQ12_HOME / "ngrok_system"
NGROK_LOGS_DIR = EQ12_HOME / "logs" / "ngrok"
NGROK_CONFIG_FILE = NGROK_DIR / "ngrok.yml"

# Ensure directories exist
for directory in [NGROK_DIR, NGROK_LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class NgrokTunnel:
    """Represents an ngrok tunnel configuration"""

    name: str
    port: int
    protocol: str = "http"
    subdomain: str | None = None
    auth: str | None = None
    public_url: str | None = None
    status: str = "stopped"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EQ12Service:
    """Represents an EQ12 service that needs tunnel exposure"""

    name: str
    description: str
    port: int
    tunnel_name: str
    health_check_path: str = "/health"
    auto_start: bool = True
    auth_required: bool = True


class EQ12NgrokManager:
    """Ngrok tunnel manager for EQ12 automation stack"""

    def __init__(self):
        self.ngrok_dir = NGROK_DIR
        self.logs_dir = NGROK_LOGS_DIR
        self.config_file = NGROK_CONFIG_FILE
        self.ngrok_process = None
        self.active_tunnels: dict[str, NgrokTunnel] = {}

        # EQ12 Services configuration
        self.eq12_services = {
            "eq12_backend": EQ12Service(
                name="EQ12 Backend API",
                description="Main FastAPI backend with betting analytics",
                port=8000,
                tunnel_name="eq12-api",
                health_check_path="/api/health",
            ),
            "sports_betting": EQ12Service(
                name="Sports Betting Bot",
                description="Automated sports betting with odds analysis",
                port=8001,
                tunnel_name="sports-webhook",
                health_check_path="/webhook/health",
            ),
            "travel_deals": EQ12Service(
                name="Travel Deals Scanner",
                description="Flight and travel deal automation",
                port=8002,
                tunnel_name="travel-api",
                health_check_path="/api/status",
            ),
            "commerce_automation": EQ12Service(
                name="Commerce Automation",
                description="eBay, Etsy, and marketplace automation",
                port=8003,
                tunnel_name="commerce-api",
                health_check_path="/automation/status",
            ),
            "finance_tracker": EQ12Service(
                name="Finance Dashboard",
                description="Credit, bankroll, and investment tracking",
                port=8004,
                tunnel_name="finance-dashboard",
                health_check_path="/dashboard/health",
            ),
            "telegram_bot": EQ12Service(
                name="Telegram Bot Webhook",
                description="Telegram bot for EQ12 commands and notifications",
                port=8005,
                tunnel_name="telegram-webhook",
                health_check_path="/telegram/webhook/health",
            ),
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(self.logs_dir / "ngrok_manager.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("NgrokManager")

    def install_ngrok(self) -> bool:
        """Install ngrok if not present"""

        try:
            # Check if ngrok is already installed
            result = subprocess.run(["ngrok", "version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.logger.info(f"✅ Ngrok already installed: {result.stdout.strip()}")
                return True

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        self.logger.info("📦 Installing ngrok...")

        try:
            # Download and install ngrok via Chocolatey (Windows)
            if os.name == "nt":
                subprocess.run(["choco", "install", "ngrok", "-y"], check=True)
            else:
                # Linux/WSL installation
                subprocess.run(
                    [
                        "curl",
                        "-s",
                        "https://ngrok-agent.s3.amazonaws.com/ngrok.asc",
                        "|",
                        "sudo",
                        "tee",
                        "/etc/apt/trusted.gpg.d/ngrok.asc",
                        ">/dev/null",
                    ],
                    shell=True,
                    check=True,
                )

                subprocess.run(
                    [
                        "echo",
                        "deb https://ngrok-agent.s3.amazonaws.com buster main",
                        "|",
                        "sudo",
                        "tee",
                        "/etc/apt/sources.list.d/ngrok.list",
                    ],
                    shell=True,
                    check=True,
                )

                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(["sudo", "apt", "install", "ngrok"], check=True)

            self.logger.info("✅ Ngrok installation completed")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Ngrok installation failed: {e}")
            return False

    def setup_ngrok_config(self, auth_token: str | None = None) -> bool:
        """Setup ngrok configuration file"""

        self.logger.info("⚙️ Setting up ngrok configuration...")

        if auth_token:
            # Set auth token
            try:
                subprocess.run(["ngrok", "config", "add-authtoken", auth_token], check=True)
                self.logger.info("✅ Ngrok auth token configured")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"❌ Failed to set auth token: {e}")
                return False

        # Copy config file to ngrok config directory
        ngrok_config_dir = Path.home() / ".ngrok2"
        ngrok_config_dir.mkdir(exist_ok=True)

        ngrok_config_path = ngrok_config_dir / "ngrok.yml"

        if self.config_file.exists():
            import shutil

            shutil.copy2(self.config_file, ngrok_config_path)
            self.logger.info(f"✅ Ngrok config copied to: {ngrok_config_path}")
        else:
            self.logger.warning(f"⚠️ Config file not found: {self.config_file}")

        return True

    async def start_tunnel(self, tunnel_name: str) -> bool:
        """Start specific ngrok tunnel"""

        self.logger.info(f"🚀 Starting tunnel: {tunnel_name}")

        try:
            # Start tunnel in background
            subprocess.Popen(
                ["ngrok", "start", tunnel_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for startup
            await asyncio.sleep(3)

            # Check if tunnel is active
            tunnel_info = await self.get_tunnel_info(tunnel_name)
            if tunnel_info:
                self.active_tunnels[tunnel_name] = tunnel_info
                self.logger.info(f"✅ Tunnel active: {tunnel_name} -> {tunnel_info.public_url}")
                return True
            self.logger.error(f"❌ Tunnel failed to start: {tunnel_name}")
            return False

        except Exception as e:
            self.logger.error(f"❌ Error starting tunnel {tunnel_name}: {e}")
            return False

    async def start_all_tunnels(self) -> dict[str, bool]:
        """Start all configured tunnels"""

        self.logger.info("🚀 Starting all EQ12 ngrok tunnels...")

        results = {}

        # Start ngrok with all tunnels
        try:
            self.ngrok_process = subprocess.Popen(
                ["ngrok", "start", "--all"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for startup
            await asyncio.sleep(5)

            # Check each tunnel
            for _service_name, service in self.eq12_services.items():
                if service.auto_start:
                    tunnel_info = await self.get_tunnel_info(service.tunnel_name)
                    if tunnel_info:
                        self.active_tunnels[service.tunnel_name] = tunnel_info
                        results[service.tunnel_name] = True
                        self.logger.info(f"✅ {service.name}: {tunnel_info.public_url}")
                    else:
                        results[service.tunnel_name] = False
                        self.logger.error(f"❌ Failed to start: {service.name}")

            return results

        except Exception as e:
            self.logger.error(f"❌ Error starting tunnels: {e}")
            return dict.fromkeys(self.eq12_services.keys(), False)

    async def get_tunnel_info(self, tunnel_name: str) -> NgrokTunnel | None:
        """Get tunnel information from ngrok API"""

        try:
            # Query ngrok local API
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels_data = response.json()

                for tunnel_data in tunnels_data.get("tunnels", []):
                    if tunnel_data.get("name") == tunnel_name:
                        return NgrokTunnel(
                            name=tunnel_data["name"],
                            port=tunnel_data["config"]["addr"].split(":")[-1],
                            protocol=tunnel_data["proto"],
                            public_url=tunnel_data["public_url"],
                            status="active",
                            metadata=tunnel_data.get("metadata", {}),
                        )

        except Exception as e:
            self.logger.debug(f"Could not get tunnel info for {tunnel_name}: {e}")

        return None

    async def health_check_services(self) -> dict[str, bool]:
        """Health check all EQ12 services"""

        self.logger.info("🏥 Running health checks on EQ12 services...")

        results = {}

        for service_name, service in self.eq12_services.items():
            try:
                # Get tunnel for this service
                tunnel = self.active_tunnels.get(service.tunnel_name)
                if not tunnel:
                    results[service_name] = False
                    continue

                # Build health check URL
                health_url = f"{tunnel.public_url}{service.health_check_path}"

                # Make health check request
                response = requests.get(health_url, timeout=10, auth=self._parse_auth(tunnel.auth))

                if response.status_code == 200:
                    results[service_name] = True
                    self.logger.info(f"✅ {service.name}: Healthy")
                else:
                    results[service_name] = False
                    self.logger.warning(
                        f"⚠️ {service.name}: Unhealthy (HTTP {response.status_code})"
                    )

            except Exception as e:
                results[service_name] = False
                self.logger.error(f"❌ {service.name}: Health check failed - {e}")

        return results

    def _parse_auth(self, auth_string: str | None) -> tuple | None:
        """Parse auth string into tuple for requests"""
        if auth_string and ":" in auth_string:
            username, password = auth_string.split(":", 1)
            return (username, password)
        return None

    def get_tunnel_urls(self) -> dict[str, str]:
        """Get public URLs for all active tunnels"""

        urls = {}
        for tunnel_name, tunnel in self.active_tunnels.items():
            if tunnel.public_url:
                urls[tunnel_name] = tunnel.public_url

        return urls

    async def stop_tunnels(self):
        """Stop all ngrok tunnels"""

        self.logger.info("🛑 Stopping ngrok tunnels...")

        if self.ngrok_process:
            self.ngrok_process.terminate()
            try:
                self.ngrok_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.ngrok_process.kill()

            self.logger.info("✅ Ngrok tunnels stopped")

        self.active_tunnels.clear()

    def generate_telegram_webhook_commands(self) -> list[str]:
        """Generate curl commands to set Telegram webhook URLs"""

        commands = []

        telegram_tunnel = self.active_tunnels.get("telegram-webhook")
        if telegram_tunnel:
            webhook_url = f"{telegram_tunnel.public_url}/telegram/webhook"

            # Get Telegram bot token from environment or keys
            bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not bot_token:
                token_file = EQ12_HOME / "keys" / "telegram_bot_token.txt"
                if token_file.exists():
                    bot_token = token_file.read_text().strip()

            if bot_token:
                commands.append(
                    f"""
# Set Telegram webhook for EQ12 bot
curl -X POST "https://api.telegram.org/bot{bot_token}/setWebhook" \\
     -H "Content-Type: application/json" \\
     -d '{{"url": "{webhook_url}"}}'
                """.strip()
                )

        return commands


async def setup_eq12_ngrok_system():
    """Main setup function for EQ12 ngrok system"""

    print("🎯 EQ12 Ngrok Gateway System Setup")
    print("   Setting up secure tunnels for EQ12 automation services")

    # Initialize ngrok manager
    manager = EQ12NgrokManager()

    # Install ngrok if needed
    if not manager.install_ngrok():
        print("❌ Failed to install ngrok")
        return False

    # Setup configuration
    auth_token = os.getenv("NGROK_AUTH_TOKEN")
    if auth_token:
        manager.setup_ngrok_config(auth_token)
    else:
        print("⚠️ NGROK_AUTH_TOKEN not set. Some features may not work.")
        manager.setup_ngrok_config()

    # Create example services info
    services_info = {
        "ngrok_manager_version": "1.0.0",
        "services_configured": len(manager.eq12_services),
        "service_details": {
            name: {
                "description": service.description,
                "port": service.port,
                "tunnel_name": service.tunnel_name,
                "auto_start": service.auto_start,
            }
            for name, service in manager.eq12_services.items()
        },
        "setup_completed": datetime.now(UTC).isoformat(),
    }

    # Save configuration
    config_file = NGROK_DIR / "eq12_ngrok_config.json"
    with open(config_file, "w") as f:
        json.dump(services_info, f, indent=2)

    print("\n✅ EQ12 Ngrok System Setup Complete!")
    print(f"   📁 Configuration: {config_file}")
    print(f"   🔧 Ngrok config: {manager.config_file}")
    print(f"   📋 Services configured: {len(manager.eq12_services)}")
    print(
        '\n🚀 To start tunnels: python -c "import asyncio; from eq12_ngrok_manager import EQ12NgrokManager; asyncio.run(EQ12NgrokManager().start_all_tunnels())"'
    )

    return manager


if __name__ == "__main__":
    asyncio.run(setup_eq12_ngrok_system())
