#!/usr/bin/env python3
"""
EQ12 Complete Integration Script

Integrates all components for the ultimate EQ12 automation platform:
- Security-hardened credential management
- Multi-platform bot architecture (Telegram + Discord + Apple TV)
- Visual input processing (OCR Snip Watcher)
- VPN/WireGuard automation
- Cross-platform support (Windows + Ubuntu/WSL)
- GitHub CI/CD integration
- VS Code + Copilot workspace setup

This script sets up the complete environment as a security expert would:
- Validates all security configurations
- Sets up encrypted credential storage
- Configures development environment
- Initializes multi-platform bot architecture
- Establishes monitoring and logging
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
LOGS_DIR = EQ12_HOME / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | EQ12Integration | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "integration.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12Integration")


class EQ12SecurityIntegrator:
    """Complete security-hardened EQ12 integration"""

    def __init__(self):
        self.eq12_home = EQ12_HOME
        self.platform = "windows" if os.name == "nt" else "ubuntu"

        # Component inventory
        self.components = {
            # Core Python Applications
            "eq12_production_launcher.py": "Production orchestrator",
            "eq12_telegram_master_bot.py": "Telegram bot (67+ commands)",
            "eq12_discord_bot.py": "Discord dual-server bot",
            "eq12_snip_watcher.py": "Visual OCR processor",
            "eq12_appletv_manager.py": "Apple TV command center",
            "eq12_appletv_streaming_engine.py": "AirPlay streaming engine",
            "eq12_credential_manager.py": "Encrypted credential storage",
            "eq12_security_scanner.py": "Vulnerability scanner",
            # PowerShell Toolkits (Windows)
            "eq12_admin.ps1": "Admin toolkit (firewall, services, tasks)",
            "eq12_user.ps1": "User toolkit (daily operations)",
            "eq12_wireguard_switcher.ps1": "VPN profile management",
            "eq12_telegram_master_bot.ps1": "Telegram wrapper",
            "eq12_discord_bot.ps1": "Discord wrapper",
            "eq12_snip_watcher.ps1": "Snip watcher wrapper",
            # Ubuntu Scripts
            "eq12_user.sh": "Ubuntu user toolkit",
            "eq12_admin.sh": "Ubuntu admin toolkit",
            "eq12_wireguard_manager.sh": "Linux VPN management",
            # Configuration
            ".gitignore": "Security-hardened exclusions",
            ".github/workflows/security-ci.yml": "Automated security scanning",
            "pre-commit-security-hook.sh": "Pre-commit validation",
            ".vscode/settings.json": "VS Code + Copilot configuration",
            ".vscode/launch_debug.json": "Debug configurations",
            ".vscode/tasks.json": "Build/run tasks",
            ".vscode/extensions.json": "Required extensions",
            # Documentation
            "README_GITHUB_SECURITY_BUNDLE.md": "Complete setup guide",
            "README_MULTI_PLATFORM_BOTS.md": "Bot architecture guide",
            "SECURITY_AUDIT_RESULTS.md": "Security audit report",
        }

        # Security validation results
        self.security_status = {}
        self.missing_components = []
        self.integration_report = {}

    def display_banner(self):
        """Display EQ12 integration banner"""
        banner = """
        ╔═══════════════════════════════════════════════════════════════════╗
        ║                    EQ12 SECURITY INTEGRATION                      ║
        ║                 Complete Automation Platform                      ║
        ╠═══════════════════════════════════════════════════════════════════╣
        ║  🤖 Multi-Platform Bots    │  🔐 Encrypted Credentials          ║
        ║  👁️  Visual Input (OCR)     │  🌐 VPN Automation                ║
        ║  📺 Apple TV Integration   │  🛡️  Security Hardened            ║
        ║  💻 Cross-Platform Support │  🚀 Production Ready              ║
        ╚═══════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        logger.info("EQ12 Security Integration Started")
        logger.info(f"Platform: {self.platform.title()}")
        logger.info(f"EQ12 Home: {self.eq12_home}")
        logger.info("=" * 70)

    def validate_components(self) -> bool:
        """Validate all components are present"""
        logger.info("🔍 Validating EQ12 Components...")

        self.missing_components = []

        for component, description in self.components.items():
            file_path = self.eq12_home / component

            if file_path.exists():
                logger.info(f"  ✅ {component}: {description}")
            else:
                self.missing_components.append(component)
                logger.error(f"  ❌ {component}: MISSING - {description}")

        if self.missing_components:
            logger.error(f"❌ Missing {len(self.missing_components)} components:")
            for component in self.missing_components:
                logger.error(f"    • {component}")
            return False

        logger.info(f"✅ All {len(self.components)} components validated")
        return True

    async def run_security_validation(self) -> bool:
        """Run comprehensive security validation"""
        logger.info("🔒 Running Security Validation...")

        try:
            # Import and run security scanner
            sys.path.append(str(self.eq12_home))

            try:
                from eq12_security_scanner import EQ12SecurityScanner

                scanner = EQ12SecurityScanner(str(self.eq12_home))

                # Run security scan
                issues = await asyncio.get_event_loop().run_in_executor(None, scanner.scan_files)

                # Check for critical issues
                critical_issues = [
                    issue
                    for issue in issues
                    if hasattr(issue, "severity") and issue.severity == "CRITICAL"
                ]

                if critical_issues:
                    logger.error(f"🚨 CRITICAL security issues found: {len(critical_issues)}")
                    for issue in critical_issues[:3]:  # Show first 3
                        logger.error(
                            f"  📁 {issue.file_path}:{issue.line_number} - {issue.description}"
                        )
                    self.security_status["scan"] = "FAILED"
                    return False

                logger.info(f"✅ Security scan passed - {len(issues)} total issues (no critical)")
                self.security_status["scan"] = "PASSED"

            except ImportError:
                logger.warning("⚠️ Security scanner not available - creating basic validation")
                self.security_status["scan"] = "SKIPPED"

            # Validate .gitignore security
            gitignore_file = self.eq12_home / ".gitignore"
            if gitignore_file.exists():
                with open(gitignore_file) as f:
                    gitignore_content = f.read()

                required_patterns = ["keys/", "credentials.*", ".env", "logs/", "data/"]
                missing_patterns = [p for p in required_patterns if p not in gitignore_content]

                if missing_patterns:
                    logger.error(f"❌ .gitignore missing security patterns: {missing_patterns}")
                    self.security_status["gitignore"] = "INCOMPLETE"
                else:
                    logger.info("✅ .gitignore security patterns validated")
                    self.security_status["gitignore"] = "SECURE"
            else:
                logger.error("❌ .gitignore file missing")
                self.security_status["gitignore"] = "MISSING"

            # Check for exposed secrets in current directory
            exposed_secrets = []
            for pattern in [".env", "credentials.json", "secrets.json", "config.json"]:
                if (self.eq12_home / pattern).exists():
                    exposed_secrets.append(pattern)

            if exposed_secrets:
                logger.error(f"🚨 EXPOSED secrets detected: {exposed_secrets}")
                logger.error("   Run: python eq12_credential_manager.py --encrypt")
                self.security_status["exposed_secrets"] = exposed_secrets
                return False
            logger.info("✅ No exposed secrets detected")
            self.security_status["exposed_secrets"] = []

            return True

        except Exception as e:
            logger.error(f"❌ Security validation failed: {e}")
            self.security_status["error"] = str(e)
            return False

    def setup_development_environment(self) -> bool:
        """Setup development environment"""
        logger.info("🛠️ Setting up Development Environment...")

        try:
            # Check Python version
            python_version = (
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )
            if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
                logger.info(f"  ✅ Python {python_version}: Compatible")
            else:
                logger.error(f"  ❌ Python {python_version}: Requires 3.8+")
                return False

            # Check required packages
            required_packages = [
                "requests",
                "aiohttp",
                "cryptography",
                "python-telegram-bot",
                "discord.py",
                "pillow",
                "pytesseract",
                "watchdog",
            ]

            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package.replace("-", "_"))
                    logger.info(f"  ✅ {package}: Installed")
                except ImportError:
                    missing_packages.append(package)
                    logger.warning(f"  ⚠️ {package}: Missing")

            if missing_packages:
                logger.info(f"📦 Installing missing packages: {missing_packages}")
                cmd = ["pip", "install", *missing_packages]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info("✅ Package installation completed")
                else:
                    logger.error(f"❌ Package installation failed: {result.stderr}")

            # Check VS Code workspace
            vscode_dir = self.eq12_home / ".vscode"
            if vscode_dir.exists():
                logger.info("✅ VS Code workspace configured")
            else:
                logger.warning("⚠️ VS Code workspace not found")

            # Check Git configuration
            git_dir = self.eq12_home / ".git"
            if git_dir.exists():
                logger.info("✅ Git repository initialized")
            else:
                logger.info("📝 Initialize Git repository with: git init")

            return True

        except Exception as e:
            logger.error(f"❌ Development environment setup failed: {e}")
            return False

    def setup_credential_management(self) -> bool:
        """Setup encrypted credential management"""
        logger.info("🔐 Setting up Credential Management...")

        try:
            # Check if credential manager exists
            cred_manager_file = self.eq12_home / "eq12_credential_manager.py"
            if not cred_manager_file.exists():
                logger.error("❌ eq12_credential_manager.py not found")
                return False

            # Check for existing credentials
            keys_dir = self.eq12_home / "keys"
            keys_dir.mkdir(exist_ok=True)

            encrypted_file = keys_dir / "credentials.enc"
            plaintext_file = keys_dir / "credentials.json"

            if encrypted_file.exists():
                logger.info("✅ Encrypted credentials found")
            elif plaintext_file.exists():
                logger.warning("⚠️ Plaintext credentials found - encryption recommended")
                logger.info("   Run: python eq12_credential_manager.py --encrypt")
            else:
                logger.info("ℹ️ No credentials found - setup required")
                logger.info("   Run: python eq12_credential_manager.py --setup")

            # Check environment variable
            if "EQ12_CREDENTIAL_PASSWORD" in os.environ:
                logger.info("✅ EQ12_CREDENTIAL_PASSWORD environment variable set")
            else:
                logger.warning("⚠️ EQ12_CREDENTIAL_PASSWORD not set")
                logger.info("   Set with: $env:EQ12_CREDENTIAL_PASSWORD='your_password'")

            return True

        except Exception as e:
            logger.error(f"❌ Credential management setup failed: {e}")
            return False

    def validate_multi_platform_architecture(self) -> bool:
        """Validate multi-platform bot architecture"""
        logger.info("🤖 Validating Multi-Platform Architecture...")

        try:
            # Check core bot components
            bot_components = {
                "eq12_telegram_master_bot.py": "Telegram Master Bot (67+ commands)",
                "eq12_discord_bot.py": "Discord Dual-Server Bot",
                "eq12_snip_watcher.py": "Visual OCR Processor",
                "eq12_appletv_manager.py": "Apple TV Command Center",
                "eq12_appletv_streaming_engine.py": "AirPlay Streaming Engine",
            }

            missing_bots = []
            for bot_file, description in bot_components.items():
                bot_path = self.eq12_home / bot_file
                if bot_path.exists():
                    logger.info(f"  ✅ {description}")
                else:
                    missing_bots.append(bot_file)
                    logger.error(f"  ❌ {description} - Missing: {bot_file}")

            # Check PowerShell wrappers (Windows)
            if self.platform == "windows":
                ps_wrappers = {
                    "eq12_telegram_master_bot.ps1": "Telegram Bot Wrapper",
                    "eq12_discord_bot.ps1": "Discord Bot Wrapper",
                    "eq12_snip_watcher.ps1": "Snip Watcher Wrapper",
                }

                for wrapper_file, description in ps_wrappers.items():
                    wrapper_path = self.eq12_home / wrapper_file
                    if wrapper_path.exists():
                        logger.info(f"  ✅ {description}")
                    else:
                        missing_bots.append(wrapper_file)
                        logger.error(f"  ❌ {description} - Missing: {wrapper_file}")

            if missing_bots:
                logger.error(f"❌ Missing {len(missing_bots)} bot components")
                return False

            logger.info("✅ Multi-platform architecture validated")
            return True

        except Exception as e:
            logger.error(f"❌ Architecture validation failed: {e}")
            return False

    def generate_integration_report(self) -> str:
        """Generate comprehensive integration report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "platform": self.platform,
            "eq12_home": str(self.eq12_home),
            "components": {
                "total": len(self.components),
                "validated": len(self.components) - len(self.missing_components),
                "missing": self.missing_components,
            },
            "security_status": self.security_status,
            "integration_status": (
                "COMPLETE" if len(self.missing_components) == 0 else "INCOMPLETE"
            ),
        }

        report_file = (
            LOGS_DIR / f"integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"📋 Integration report saved: {report_file}")
            return str(report_file)
        except Exception as e:
            logger.error(f"❌ Failed to save report: {e}")
            return ""

    def display_completion_status(self):
        """Display final completion status"""
        logger.info("=" * 70)
        logger.info("🎯 EQ12 INTEGRATION COMPLETE")
        logger.info("=" * 70)

        # Component status
        total_components = len(self.components)
        missing_count = len(self.missing_components)
        validated_count = total_components - missing_count

        logger.info(f"📦 Components: {validated_count}/{total_components} validated")
        if missing_count > 0:
            logger.warning(f"⚠️ Missing: {missing_count} components")

        # Security status
        logger.info("🔒 Security Status:")
        for check, status in self.security_status.items():
            if status == "PASSED" or status == "SECURE" or status == []:
                logger.info(f"  ✅ {check}: {status}")
            else:
                logger.warning(f"  ⚠️ {check}: {status}")

        # Next steps
        logger.info("🚀 Next Steps:")
        logger.info("  1. Set credential password: $env:EQ12_CREDENTIAL_PASSWORD='password'")
        logger.info("  2. Launch production: python eq12_production_launcher.py --launch")
        logger.info("  3. Open VS Code workspace for development")
        logger.info("  4. Configure bot tokens and API keys")

        logger.info("=" * 70)
        logger.info("🎉 EQ12 Security-Hardened Automation Platform Ready!")

        # Platform-specific instructions
        if self.platform == "windows":
            logger.info("💻 Windows Integration:")
            logger.info("  • PowerShell toolkits available (Admin/User modes)")
            logger.info("  • WireGuard VPN profile switching")
            logger.info("  • Task Scheduler automation")
        else:
            logger.info("🐧 Ubuntu Integration:")
            logger.info("  • Bash toolkits available")
            logger.info("  • Systemd service management")
            logger.info("  • WireGuard VPN automation")

        logger.info("=" * 70)

    async def run_complete_integration(self) -> bool:
        """Run complete EQ12 integration"""
        self.display_banner()

        success = True

        # Phase 1: Component Validation
        logger.info("Phase 1: Component Validation")
        if not self.validate_components():
            success = False

        # Phase 2: Security Validation
        logger.info("Phase 2: Security Validation")
        if not await self.run_security_validation():
            success = False

        # Phase 3: Development Environment
        logger.info("Phase 3: Development Environment")
        if not self.setup_development_environment():
            success = False

        # Phase 4: Credential Management
        logger.info("Phase 4: Credential Management")
        if not self.setup_credential_management():
            success = False

        # Phase 5: Architecture Validation
        logger.info("Phase 5: Architecture Validation")
        if not self.validate_multi_platform_architecture():
            success = False

        # Phase 6: Generate Report
        logger.info("Phase 6: Generate Integration Report")
        self.generate_integration_report()

        # Phase 7: Display Results
        self.display_completion_status()

        return success


async def main():
    """Main entry point for EQ12 integration"""
    integrator = EQ12SecurityIntegrator()

    try:
        success = await integrator.run_complete_integration()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("🛑 Integration interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"💥 Integration failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
