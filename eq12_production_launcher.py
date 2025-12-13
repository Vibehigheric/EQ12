#!/usr/bin/env python3
"""
EQ12 Security-Hardened Production Launcher

Complete production orchestrator for EQ12 multi-platform automation:
- Security-first credential management (encrypted keys)
- Multi-platform bot architecture (Telegram + Discord + Apple TV)
- Visual input processing (Snip Watcher with OCR)
- VPN/WireGuard automation and rotation
- Cross-platform compatibility (Windows + Ubuntu/WSL)
- Real-time health monitoring and auto-recovery

Security Features:
- Pre-launch security scanning
- Encrypted credential management
- No hardcoded secrets
- Automated vulnerability detection
- Secure API key rotation

Architecture Components:
- Telegram Master Bot (67+ commands across 5 categories)
- Discord Dual Server Bot (Ops + Community channels)
- Apple TV Command Center (AirPlay streaming)
- Visual OCR Pipeline (Screenshot → Data routing)
- WireGuard VPN Manager (Profile switching)
- PowerShell Admin/User Toolkits
- Ubuntu/WSL Integration Scripts

Usage:
    python eq12_production_launcher.py --launch
    python eq12_production_launcher.py --security-scan
    python eq12_production_launcher.py --status
    python eq12_production_launcher.py --stop-all
"""

import argparse
import asyncio
import json
import logging
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Security imports
try:
    from eq12_credential_manager import EQ12CredentialManager
    from eq12_security_scanner import EQ12SecurityScanner

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

try:
    import aiohttp
    import requests

    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
LOGS_DIR = EQ12_HOME / "logs"
KEYS_DIR = EQ12_HOME / "keys"
CONFIG_DIR = EQ12_HOME / "configs"

# Ensure critical directories exist
for directory in [LOGS_DIR, KEYS_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup secure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "eq12_production.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12Production")


class ComponentStatus:
    """Component status tracking"""

    AVAILABLE = "available"
    STARTING = "starting"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"
    UNKNOWN = "unknown"


class EQ12ProductionLauncher:
    """Security-hardened production launcher for EQ12 multi-platform automation"""

    def __init__(self):
        self.eq12_home = EQ12_HOME

        # Core Python components
        self.components = {
            "telegram_master_bot": {
                "file": "eq12_telegram_master_bot.py",
                "wrapper": "eq12_telegram_master_bot.ps1",
                "port": 8001,
                "health_endpoint": "http://localhost:8001/health",
            },
            "discord_bot": {
                "file": "eq12_discord_bot.py",
                "wrapper": "eq12_discord_bot.ps1",
                "port": 8002,
                "health_endpoint": "http://localhost:8002/health",
            },
            "snip_watcher": {
                "file": "eq12_snip_watcher.py",
                "wrapper": "eq12_snip_watcher.ps1",
                "port": 8003,
                "health_endpoint": "http://localhost:8003/health",
            },
            "appletv_manager": {
                "file": "eq12_appletv_manager.py",
                "wrapper": "eq12_appletv_manager.ps1",
                "port": 8080,
                "health_endpoint": "http://localhost:8080/health",
            },
            "appletv_streaming": {
                "file": "eq12_appletv_streaming_engine.py",
                "wrapper": "eq12_appletv_streaming.ps1",
                "port": 8081,
                "health_endpoint": "http://localhost:8081/health",
            },
            "credential_manager": {
                "file": "eq12_credential_manager.py",
                "wrapper": None,
                "port": None,
                "health_endpoint": None,
            },
            "security_scanner": {
                "file": "eq12_security_scanner.py",
                "wrapper": None,
                "port": None,
                "health_endpoint": None,
            },
        }

        # Platform detection
        self.platform_info = {
            "os": platform.system(),
            "is_windows": platform.system() == "Windows",
            "is_linux": platform.system() == "Linux",
            "is_wsl": self._detect_wsl(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }

        # Security components
        self.credential_manager = None
        self.security_scanner = None

        # Component tracking
        self.component_status = {}
        self.process_registry = {}  # PID tracking

        # Initialize security
        self._init_security()

        logger.info(f"EQ12 Production Launcher initialized on {self.platform_info['os']}")

    def _detect_wsl(self) -> bool:
        """Detect if running under WSL"""
        try:
            with open("/proc/version") as f:
                return "microsoft" in f.read().lower()
        except:
            return False

    def _init_security(self):
        """Initialize security components"""
        if not SECURITY_AVAILABLE:
            logger.warning("⚠️ Security components not available - install cryptography package")
            return

        try:
            self.credential_manager = EQ12CredentialManager()
            self.security_scanner = EQ12SecurityScanner(str(self.eq12_home))
            logger.info("🔒 Security components initialized")
        except Exception as e:
            logger.error(f"❌ Security initialization failed: {e}")
            self.credential_manager = None
            self.security_scanner = None

    async def run_security_scan(self) -> bool:
        """Run comprehensive security scan before launch"""
        logger.info("🔍 Running security scan...")

        if not self.security_scanner:
            logger.warning("⚠️ Security scanner not available - skipping")
            return True

        try:
            # Run all security checks
            issues = await asyncio.get_event_loop().run_in_executor(
                None, self.security_scanner.scan_files
            )

            # Check for critical issues
            critical_issues = [
                issue
                for issue in issues
                if hasattr(issue, "severity") and issue.severity == "CRITICAL"
            ]

            if critical_issues:
                logger.error(f"🚨 CRITICAL security issues found: {len(critical_issues)}")
                for issue in critical_issues[:5]:  # Show first 5
                    logger.error(
                        f"  📁 {issue.file_path}:{issue.line_number} - {issue.description}"
                    )
                return False

            logger.info(f"✅ Security scan complete - {len(issues)} total issues (no critical)")
            return True

        except Exception as e:
            logger.error(f"❌ Security scan failed: {e}")
            return False

    def validate_components(self) -> tuple[bool, list[str]]:
        """Validate all required components are available"""
        logger.info("📋 Validating EQ12 components...")

        missing_components = []

        for name, config in self.components.items():
            file_path = self.eq12_home / config["file"]

            if file_path.exists():
                self.component_status[name] = ComponentStatus.AVAILABLE
                logger.debug(f"  ✅ {name}: Available")
            else:
                missing_components.append(f"{name} ({config['file']})")
                self.component_status[name] = ComponentStatus.UNKNOWN
                logger.error(f"  ❌ {name}: Missing ({config['file']})")

        # Check PowerShell wrappers (Windows only)
        if self.platform_info["is_windows"]:
            for name, config in self.components.items():
                if config["wrapper"]:
                    wrapper_path = self.eq12_home / config["wrapper"]
                    if not wrapper_path.exists():
                        missing_components.append(f"{name} wrapper ({config['wrapper']})")

        success = len(missing_components) == 0
        if success:
            logger.info(f"✅ All {len(self.components)} components validated")
        else:
            logger.error(f"❌ Missing {len(missing_components)} components")

        return success, missing_components

    async def setup_secure_environment(self) -> bool:
        """Setup secure environment variables from encrypted storage"""
        logger.info("🔐 Setting up secure environment...")

        if not self.credential_manager:
            logger.warning("⚠️ No credential manager - using existing environment")
            return True

        try:
            # Get decryption password from environment
            password = os.getenv("EQ12_CREDENTIAL_PASSWORD")
            if not password:
                logger.error("❌ EQ12_CREDENTIAL_PASSWORD environment variable not set")
                logger.error("   Set with: $env:EQ12_CREDENTIAL_PASSWORD='your_password'")
                return False

            # Decrypt and load credentials
            credentials = await asyncio.get_event_loop().run_in_executor(
                None, self.credential_manager.decrypt_credentials, password
            )

            if not credentials:
                logger.error("❌ Failed to decrypt credentials")
                logger.error(
                    "   Check password or run: python eq12_credential_manager.py --encrypt"
                )
                return False

            # Set required environment variables
            required_keys = [
                "TELEGRAM_BOT_TOKEN",
                "DISCORD_BOT_TOKEN",
                "OPENAI_API_KEY",
                "ODDS_API_KEY",
                "NGROK_TOKEN",
                "TELEGRAM_CHAT_ID",
            ]

            loaded_count = 0
            for key in required_keys:
                if key in credentials:
                    os.environ[key] = credentials[key]
                    loaded_count += 1
                    logger.debug(f"  ✅ {key}: Loaded")
                else:
                    logger.warning(f"  ⚠️ {key}: Missing from credentials")

            logger.info(f"✅ Loaded {loaded_count}/{len(required_keys)} credentials securely")
            return loaded_count > 0

        except Exception as e:
            logger.error(f"❌ Environment setup failed: {e}")
            return False

    async def start_component(self, component_name: str) -> bool:
        """Start individual EQ12 component"""
        if component_name not in self.components:
            logger.error(f"❌ Unknown component: {component_name}")
            return False

        config = self.components[component_name]
        logger.info(f"🚀 Starting {component_name}...")

        self.component_status[component_name] = ComponentStatus.STARTING

        try:
            if self.platform_info["is_windows"] and config["wrapper"]:
                # Use PowerShell wrapper on Windows
                wrapper_path = self.eq12_home / config["wrapper"]
                cmd = [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(wrapper_path),
                    "-Start",
                ]
            else:
                # Direct Python execution
                script_path = self.eq12_home / config["file"]
                if self.platform_info["is_windows"]:
                    cmd = ["python", str(script_path)]
                else:
                    cmd = ["python3", str(script_path)]

            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=str(self.eq12_home),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if self.platform_info["is_windows"] else 0
                ),
            )

            # Register process
            self.process_registry[component_name] = process.pid
            self.component_status[component_name] = ComponentStatus.RUNNING

            logger.info(f"✅ {component_name} started [PID: {process.pid}]")

            # Wait a moment for startup
            await asyncio.sleep(2)

            # Check if still running
            if process.poll() is None:
                return True
            self.component_status[component_name] = ComponentStatus.FAILED
            _stdout, stderr = process.communicate()
            logger.error(f"❌ {component_name} failed to start")
            if stderr:
                logger.error(f"   Error: {stderr.decode()}")
            return False

        except Exception as e:
            logger.error(f"❌ Failed to start {component_name}: {e}")
            self.component_status[component_name] = ComponentStatus.FAILED
            return False

    async def health_check(self, component_name: str | None = None) -> dict[str, bool]:
        """Perform health checks on components"""
        if component_name:
            components_to_check = {component_name: self.components[component_name]}
        else:
            components_to_check = {
                name: config
                for name, config in self.components.items()
                if config["health_endpoint"]
            }

        health_status = {}

        if not NETWORK_AVAILABLE:
            logger.warning("⚠️ Network libraries not available - skipping health checks")
            return dict.fromkeys(components_to_check.keys(), False)

        for name, config in components_to_check.items():
            if not config["health_endpoint"]:
                continue

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(config["health_endpoint"], timeout=5) as response:
                        health_status[name] = response.status == 200
                        if health_status[name]:
                            logger.debug(f"  ✅ {name}: Healthy")
                        else:
                            logger.warning(f"  ⚠️ {name}: Unhealthy (status: {response.status})")

            except Exception as e:
                health_status[name] = False
                logger.warning(f"  ❌ {name}: Health check failed ({e})")

        return health_status

    async def launch_production_environment(self) -> bool:
        """Launch complete EQ12 production environment"""
        logger.info("🎯 EQ12 PRODUCTION LAUNCH INITIATED")
        logger.info("=" * 60)

        start_time = datetime.now()

        try:
            # Phase 1: Security Validation
            logger.info("Phase 1: Security Validation")
            if not await self.run_security_scan():
                logger.error("❌ Security validation failed - launch aborted")
                return False

            # Phase 2: Component Validation
            logger.info("Phase 2: Component Validation")
            success, missing = self.validate_components()
            if not success:
                logger.error(f"❌ Component validation failed - missing: {', '.join(missing)}")
                return False

            # Phase 3: Environment Setup
            logger.info("Phase 3: Secure Environment Setup")
            if not await self.setup_secure_environment():
                logger.error("❌ Environment setup failed")
                return False

            # Phase 4: Component Startup
            logger.info("Phase 4: Component Startup")

            # Start components in order
            startup_order = [
                "credential_manager",
                "security_scanner",
                "snip_watcher",
                "appletv_manager",
                "appletv_streaming",
                "telegram_master_bot",
                "discord_bot",
            ]

            failed_components = []
            for component_name in startup_order:
                if component_name in ["credential_manager", "security_scanner"]:
                    # These are libraries, not services
                    continue

                if not await self.start_component(component_name):
                    failed_components.append(component_name)

            if failed_components:
                logger.error(f"❌ Failed to start components: {', '.join(failed_components)}")

            # Phase 5: Startup Wait
            logger.info("Phase 5: Startup Stabilization")
            await asyncio.sleep(10)  # Allow components to fully initialize

            # Phase 6: Health Verification
            logger.info("Phase 6: Health Verification")
            health_status = await self.health_check()

            unhealthy_components = [name for name, healthy in health_status.items() if not healthy]

            # Phase 7: Generate Report
            duration = datetime.now() - start_time
            self.generate_launch_report(health_status, duration, len(failed_components) == 0)

            # Final status
            if len(failed_components) == 0 and len(unhealthy_components) == 0:
                logger.info("🎉 EQ12 PRODUCTION ENVIRONMENT READY!")
                logger.info(f"⏱️ Launch completed in {duration.total_seconds():.1f} seconds")
                self.display_status_dashboard()
                return True
            logger.warning("⚠️ Production launch completed with issues")
            logger.warning(f"   Failed startups: {failed_components}")
            logger.warning(f"   Unhealthy components: {unhealthy_components}")
            return False

        except Exception as e:
            logger.error(f"💥 Production launch failed: {e}")
            return False
        finally:
            logger.info("=" * 60)

    def display_status_dashboard(self):
        """Display current system status dashboard"""
        logger.info("📊 EQ12 STATUS DASHBOARD")
        logger.info("-" * 40)

        logger.info(
            f"Platform: {self.platform_info['os']} | Python: {self.platform_info['python_version']}"
        )
        logger.info(f"EQ12 Home: {self.eq12_home}")

        logger.info("\n🤖 Active Components:")
        for name, status in self.component_status.items():
            if name in self.process_registry:
                pid = self.process_registry[name]
                logger.info(f"  • {name}: {status} [PID: {pid}]")
            else:
                logger.info(f"  • {name}: {status}")

        logger.info("\n🌐 Health Endpoints:")
        for name, config in self.components.items():
            if config["health_endpoint"]:
                logger.info(f"  • {config['health_endpoint']}")

        logger.info("\n📋 Available Commands:")
        logger.info("  • Telegram: 67+ commands (/parlay, /deal, /finance, /sendtv, etc.)")
        logger.info("  • Discord: !eq12 status, !eq12 parlay, !eq12 deal, !eq12 sendtv")
        logger.info("  • Apple TV: AirPlay streaming, HomeKit integration")
        logger.info("  • Snip Watcher: Screenshot → OCR → API routing")
        logger.info("-" * 40)

    def generate_launch_report(self, health_status: dict[str, bool], duration, success: bool):
        """Generate detailed launch report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "launch_duration_seconds": duration.total_seconds(),
            "success": success,
            "platform": self.platform_info,
            "eq12_home": str(self.eq12_home),
            "component_status": self.component_status,
            "process_registry": self.process_registry,
            "health_status": health_status,
            "security_scan": "completed" if self.security_scanner else "skipped",
            "credentials": "encrypted" if self.credential_manager else "environment",
        }

        report_file = LOGS_DIR / f"launch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"📋 Launch report saved: {report_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save launch report: {e}")

    def stop_all_components(self):
        """Emergency stop all EQ12 components"""
        logger.info("🛑 Emergency stop - terminating all EQ12 components")

        try:
            if self.platform_info["is_windows"]:
                # Stop Python processes
                subprocess.run(
                    ["taskkill", "/f", "/im", "python.exe"],
                    capture_output=True,
                    stderr=subprocess.DEVNULL,
                )
                # Stop PowerShell EQ12 processes
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Get-Process | Where-Object {$_.ProcessName -eq 'powershell' -and $_.CommandLine -like '*eq12*'} | Stop-Process -Force",
                    ],
                    capture_output=True,
                    stderr=subprocess.DEVNULL,
                )
            else:
                # Stop Python processes on Linux
                subprocess.run(
                    ["pkill", "-f", "eq12"],
                    capture_output=True,
                    stderr=subprocess.DEVNULL,
                )

            # Update status
            for name in self.components:
                self.component_status[name] = ComponentStatus.STOPPED

            self.process_registry.clear()
            logger.info("✅ All components stopped")

        except Exception as e:
            logger.error(f"❌ Error during emergency stop: {e}")

    async def status_check(self):
        """Check and display current system status"""
        logger.info("🔍 EQ12 System Status Check")

        # Check running processes
        running_count = 0
        for name in self.components:
            if name in self.process_registry:
                pid = self.process_registry[name]
                try:
                    # Check if process still exists
                    if self.platform_info["is_windows"]:
                        result = subprocess.run(
                            ["tasklist", "/FI", f"PID eq {pid}"],
                            capture_output=True,
                            text=True,
                        )
                        is_running = str(pid) in result.stdout
                    else:
                        result = subprocess.run(["ps", "-p", str(pid)], capture_output=True)
                        is_running = result.returncode == 0

                    if is_running:
                        self.component_status[name] = ComponentStatus.RUNNING
                        running_count += 1
                    else:
                        self.component_status[name] = ComponentStatus.STOPPED
                        del self.process_registry[name]

                except Exception:
                    self.component_status[name] = ComponentStatus.UNKNOWN

        logger.info(f"Running Components: {running_count}/{len(self.components)}")

        # Health checks
        if running_count > 0:
            health_status = await self.health_check()
            healthy_count = sum(1 for healthy in health_status.values() if healthy)
            logger.info(f"Healthy Endpoints: {healthy_count}/{len(health_status)}")

        self.display_status_dashboard()


async def main():
    """Main async entry point"""
    parser = argparse.ArgumentParser(description="EQ12 Security-Hardened Production Launcher")
    parser.add_argument("--launch", action="store_true", help="Launch production environment")
    parser.add_argument("--security-scan", action="store_true", help="Run security scan only")
    parser.add_argument("--status", action="store_true", help="Check system status")
    parser.add_argument("--stop-all", action="store_true", help="Emergency stop all components")
    parser.add_argument("--component", help="Start specific component")

    args = parser.parse_args()

    launcher = EQ12ProductionLauncher()

    try:
        if args.launch:
            success = await launcher.launch_production_environment()
            if success:
                logger.info("✅ EQ12 Production environment is operational")

                # Keep running and monitor
                logger.info("🔄 Monitoring mode - Press Ctrl+C to stop")
                while True:
                    await asyncio.sleep(300)  # Check every 5 minutes
                    await launcher.status_check()
            else:
                logger.error("❌ Production launch failed")
                return 1

        elif args.security_scan:
            success = await launcher.run_security_scan()
            return 0 if success else 1

        elif args.status:
            await launcher.status_check()
            return 0

        elif args.stop_all:
            launcher.stop_all_components()
            return 0

        elif args.component:
            success = await launcher.start_component(args.component)
            return 0 if success else 1

        else:
            parser.print_help()
            return 0

    except KeyboardInterrupt:
        logger.info("🛑 Shutdown signal received...")
        launcher.stop_all_components()
        logger.info("👋 EQ12 Production Launcher stopped")
        return 0
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        launcher.stop_all_components()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
