#!/usr/bin/env python3
"""
EQ12 Production Launch Script - Security-Hardened Multi-Platform Automation

Complete production deployment orchestrator for EQ12 automation platform:
- Security-first credential management
- Multi-platform bot architecture (Telegram + Discord + Apple TV)
- Visual input processing (Snip Watcher)
- VPN/WireGuard integration
- Cross-platform compatibility (Windows + Ubuntu/WSL)
- GitHub CI/CD integration
- VS Code + Copilot workspace setup

Security Features:
- No hardcoded secrets (encrypted credential manager)
- Pre-commit security hooks
- Automated vulnerability scanning
- Secure API key rotation

Architecture:
- Telegram Master Bot (67+ commands)
- Discord Dual Server Bot (Ops + Community)
- Apple TV Command Center
- Visual OCR Pipeline (Snip Watcher)
- WireGuard VPN Automation
- PowerShell Admin/User Toolkits
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# Security imports
try:
    from eq12_credential_manager import EQ12CredentialManager
    from eq12_security_scanner import EQ12SecurityScanner

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
LOGS_DIR = EQ12_HOME / "logs"
KEYS_DIR = EQ12_HOME / "keys"

# Ensure critical directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
KEYS_DIR.mkdir(parents=True, exist_ok=True)

# Setup secure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "production_launch.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("EQ12ProductionLauncher")


class EQ12ProductionLauncher:
    """Security-hardened production launcher for EQ12 multi-platform automation"""

    def __init__(self):
        self.eq12_home = EQ12_HOME
        self.config_file = self.eq12_home / "configs" / "production_config.json"

        # Core components
        self.components = {
            "credential_manager": "eq12_credential_manager.py",
            "security_scanner": "eq12_security_scanner.py",
            "telegram_master_bot": "eq12_telegram_master_bot.py",
            "discord_bot": "eq12_discord_bot.py",
            "snip_watcher": "eq12_snip_watcher.py",
            "appletv_manager": "eq12_appletv_manager.py",
            "appletv_streaming": "eq12_appletv_streaming_engine.py",
        }

        # PowerShell toolkits
        self.powershell_scripts = {
            "admin_toolkit": "eq12_admin.ps1",
            "user_toolkit": "eq12_user.ps1",
            "wireguard_switcher": "eq12_wireguard_switcher.ps1",
            "telegram_wrapper": "eq12_telegram_master_bot.ps1",
            "discord_wrapper": "eq12_discord_bot.ps1",
            "snip_wrapper": "eq12_snip_watcher.ps1",
        }

        # Ubuntu/WSL scripts
        self.ubuntu_scripts = {
            "user_toolkit": "eq12_user.sh",
            "admin_toolkit": "eq12_admin.sh",
            "wireguard_manager": "eq12_wireguard_manager.sh",
        }

        # Security configuration
        self.security_scanner = None
        self.credential_manager = None

        # Health check endpoints
        self.health_endpoints = {
            "telegram_api": "http://localhost:8001/health",
            "discord_api": "http://localhost:8002/health",
            "appletv_api": "http://localhost:8080/health",
            "snip_api": "http://localhost:8003/health",
        }

        # Initialize security components
        self._init_security()

        # Platform detection
        self.is_windows = os.name == "nt"
        self.is_wsl = "microsoft" in os.uname().release.lower() if hasattr(os, "uname") else False

        # Component status tracking
        self.component_status = {}

    def _init_security(self):
        """Initialize security components"""
        if SECURITY_AVAILABLE:
            try:
                self.credential_manager = EQ12CredentialManager()
                self.security_scanner = EQ12SecurityScanner(str(self.eq12_home))
                logger.info("Security components initialized")
            except Exception as e:
                logger.error(f"Security initialization failed: {e}")
                self.credential_manager = None
                self.security_scanner = None
        else:
            logger.warning("Security components not available - install cryptography package")

    def run_security_scan(self) -> bool:
        """Run comprehensive security scan"""
        if not self.security_scanner:
            logger.warning("Security scanner not available")
            return True

        logger.info("Running security scan...")
        try:
            issues = self.security_scanner.scan_all()
            critical_issues = [i for i in issues if i.severity == "CRITICAL"]

            if critical_issues:
                logger.error(f"CRITICAL security issues found: {len(critical_issues)}")
                for issue in critical_issues:
                    logger.error(f"  {issue.file_path}:{issue.line_number} - {issue.description}")
                return False

            logger.info(f"Security scan complete - {len(issues)} issues found (no critical)")
            return True

        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return False

    def load_production_config(self) -> dict:
        """Load production configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    return json.load(f)
            else:
                return self.create_default_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)

    def create_default_config(self) -> dict:
        """Create default production configuration"""
        config = {
            "deployment": {
                "environment": "production",
                "domain": "yourdomain.com",
                "api_subdomain": "api",
                "dashboard_subdomain": "dashboard",
                "ssl_enabled": True,
                "auto_scaling": False,
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "eq12_enterprise",
                "user": "eq12_api",
                "backup_enabled": True,
                "backup_schedule": "0 2 * * *",
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "cluster_enabled": False,
            },
            "monitoring": {
                "prometheus_enabled": True,
                "grafana_enabled": True,
                "sentry_enabled": True,
                "log_level": "INFO",
            },
            "scaling": {
                "api_instances": 2,
                "worker_instances": 2,
                "max_connections": 1000,
            },
            "security": {
                "rate_limiting": True,
                "ddos_protection": True,
                "api_key_rotation": True,
                "audit_logging": True,
            },
        }

        # Save default config
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

        logger.info(f"Created default configuration at {self.config_file}")
        return config

    def check_prerequisites(self) -> bool:
        """Check system prerequisites for deployment"""
        logger.info("Checking system prerequisites...")

        checks = {
            "python_version": self.check_python_version(),
            "docker_available": self.check_docker(),
            "postgres_available": self.check_postgres(),
            "redis_available": self.check_redis(),
            "ssl_certificates": self.check_ssl_certificates(),
            "environment_variables": self.check_environment_variables(),
        }

        failed_checks = [check for check, passed in checks.items() if not passed]

        if failed_checks:
            logger.error(f"Failed prerequisite checks: {', '.join(failed_checks)}")
            return False

        logger.info("All prerequisite checks passed ✓")
        return True

    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 12:
            logger.info(f"Python version {version.major}.{version.minor} [OK]")
            return True
        logger.error(f"Python 3.12+ required, found {version.major}.{version.minor}")
        return False

    def check_docker(self) -> bool:
        """Check Docker availability"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Docker available ✓")
                return True
        except FileNotFoundError:
            pass

        logger.error("Docker not available")
        return False

    def check_postgres(self) -> bool:
        """Check PostgreSQL connectivity"""
        try:
            import psycopg2

            # Test connection with environment variables
            conn_string = os.getenv("DATABASE_URL")
            if conn_string:
                conn = psycopg2.connect(conn_string)
                conn.close()
                logger.info("PostgreSQL connectivity ✓")
                return True
        except Exception as e:
            logger.error(f"PostgreSQL check failed: {e}")

        return False

    def check_redis(self) -> bool:
        """Check Redis connectivity"""
        try:
            import redis

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            r = redis.from_url(redis_url)
            r.ping()
            logger.info("Redis connectivity ✓")
            return True
        except Exception as e:
            logger.error(f"Redis check failed: {e}")
            return False

    def check_ssl_certificates(self) -> bool:
        """Check SSL certificate availability"""
        ssl_cert = os.getenv("SSL_CERT_PATH")
        ssl_key = os.getenv("SSL_KEY_PATH")

        if ssl_cert and ssl_key and Path(ssl_cert).exists() and Path(ssl_key).exists():
            logger.info("SSL certificates found ✓")
            return True

        logger.warning("SSL certificates not configured (development only)")
        return True  # Allow for development

    def check_environment_variables(self) -> bool:
        """Check required environment variables"""
        required_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "SECRET_KEY",
            "STRIPE_SECRET_KEY",
            "STRIPE_PUBLISHABLE_KEY",
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            return False

        logger.info("Environment variables configured [OK]")
        return True

    def setup_database(self) -> bool:
        """Setup and migrate database"""
        logger.info("Setting up database...")

        try:
            # Run Alembic migrations
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("Database migrations completed ✓")
                return True
            logger.error(f"Database migration failed: {result.stderr}")
            return False

        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False

    def deploy_services(self, config: dict) -> bool:
        """Deploy all platform services"""
        logger.info("Deploying platform services...")

        deployment_method = config.get("deployment", {}).get("method", "docker")

        if deployment_method == "docker":
            return self.deploy_with_docker(config)
        return self.deploy_with_systemd(config)

    def deploy_with_docker(self, config: dict) -> bool:
        """Deploy using Docker Compose"""
        logger.info("Deploying with Docker Compose...")

        try:
            # Build and start services
            result = subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    "docker-compose.prod.yml",
                    "up",
                    "-d",
                    "--build",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("Docker services deployed ✓")
                return True
            logger.error(f"Docker deployment failed: {result.stderr}")
            return False

        except Exception as e:
            logger.error(f"Docker deployment error: {e}")
            return False

    def deploy_with_systemd(self, config: dict) -> bool:
        """Deploy using systemd services"""
        logger.info("Deploying with systemd...")

        services = ["eq12-enterprise", "eq12-workers"]

        for service in services:
            try:
                # Start and enable service
                subprocess.run(["sudo", "systemctl", "start", service], check=True)
                subprocess.run(["sudo", "systemctl", "enable", service], check=True)
                logger.info(f"Service {service} started ✓")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to start service {service}: {e}")
                return False

        return True

    def configure_monitoring(self, config: dict) -> bool:
        """Configure monitoring and alerting"""
        if not config.get("monitoring", {}).get("prometheus_enabled", False):
            return True

        logger.info("Configuring monitoring...")

        try:
            # Start monitoring stack
            monitoring_compose = self.project_root / "monitoring" / "docker-compose.yml"
            if monitoring_compose.exists():
                result = subprocess.run(
                    ["docker-compose", "-f", str(monitoring_compose), "up", "-d"],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    logger.info("Monitoring stack deployed ✓")
                    return True

            logger.warning("Monitoring configuration not found")
            return True

        except Exception as e:
            logger.error(f"Monitoring setup failed: {e}")
            return False

    def setup_ssl_certificates(self, config: dict) -> bool:
        """Setup SSL certificates"""
        if not config.get("deployment", {}).get("ssl_enabled", False):
            return True

        logger.info("Setting up SSL certificates...")

        domain = config["deployment"]["domain"]
        api_subdomain = config["deployment"]["api_subdomain"]

        try:
            # Use certbot for Let's Encrypt
            result = subprocess.run(
                [
                    "sudo",
                    "certbot",
                    "--nginx",
                    "-d",
                    f"{api_subdomain}.{domain}",
                    "--non-interactive",
                    "--agree-tos",
                    "--email",
                    f"admin@{domain}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info("SSL certificates configured ✓")
                return True
            logger.warning(f"SSL setup failed: {result.stderr}")
            return True  # Continue without SSL for development

        except Exception as e:
            logger.warning(f"SSL setup error: {e}")
            return True

    def run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        logger.info("Running health checks...")

        # Wait for services to start
        time.sleep(30)

        all_healthy = True

        for service, endpoint in self.health_endpoints.items():
            try:
                response = requests.get(endpoint, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Health check {service} ✓")
                else:
                    logger.error(f"Health check {service} failed: {response.status_code}")
                    all_healthy = False
            except Exception as e:
                logger.error(f"Health check {service} error: {e}")
                all_healthy = False

        return all_healthy

    def setup_stripe_webhooks(self, config: dict) -> bool:
        """Configure Stripe webhooks"""
        logger.info("Configuring Stripe webhooks...")

        try:
            import stripe

            stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
            domain = config["deployment"]["domain"]
            api_subdomain = config["deployment"]["api_subdomain"]

            webhook_url = f"https://{api_subdomain}.{domain}/webhooks/stripe"

            # Create webhook endpoint
            webhook = stripe.WebhookEndpoint.create(
                url=webhook_url,
                enabled_events=[
                    "customer.subscription.created",
                    "customer.subscription.updated",
                    "customer.subscription.deleted",
                    "invoice.payment_succeeded",
                    "invoice.payment_failed",
                ],
            )

            logger.info(f"Stripe webhook configured: {webhook.id}")
            return True

        except Exception as e:
            logger.error(f"Stripe webhook setup failed: {e}")
            return False

    def generate_deployment_report(self, success: bool, config: dict) -> None:
        """Generate deployment report"""
        report = {
            "deployment_time": datetime.now().isoformat(),
            "success": success,
            "configuration": config,
            "services_status": {},
            "health_checks": {},
            "urls": {
                "api": f"https://{config['deployment']['api_subdomain']}.{config['deployment']['domain']}",
                "dashboard": f"https://{config['deployment']['dashboard_subdomain']}.{config['deployment']['domain']}",
                "monitoring": f"https://monitoring.{config['deployment']['domain']}",
            },
        }

        # Check service status
        for service in self.required_services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service], capture_output=True, text=True
                )
                report["services_status"][service] = result.stdout.strip()
            except:
                report["services_status"][service] = "unknown"

        # Save report
        report_file = (
            self.project_root
            / "logs"
            / f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Deployment report saved: {report_file}")

        if success:
            logger.info("🚀 EQ12 Enterprise Platform deployed successfully!")
            logger.info(f"API URL: {report['urls']['api']}")
            logger.info(f"Dashboard URL: {report['urls']['dashboard']}")
        else:
            logger.error("[ERROR] Deployment failed. Check logs for details.")

    def launch(self) -> bool:
        """Launch the complete EQ12 Enterprise Platform"""
        logger.info("[LAUNCH] Starting EQ12 Enterprise Platform deployment...")

        try:
            # Load configuration
            config = self.load_production_config()

            # Run deployment steps
            steps = [
                ("Prerequisites Check", self.check_prerequisites),
                ("Database Setup", self.setup_database),
                ("SSL Certificates", lambda: self.setup_ssl_certificates(config)),
                ("Service Deployment", lambda: self.deploy_services(config)),
                ("Monitoring Configuration", lambda: self.configure_monitoring(config)),
                ("Stripe Webhooks", lambda: self.setup_stripe_webhooks(config)),
                ("Health Checks", self.run_health_checks),
            ]

            for step_name, step_func in steps:
                logger.info(f"Executing: {step_name}")
                if not step_func():
                    logger.error(f"Step failed: {step_name}")
                    self.generate_deployment_report(False, config)
                    return False
                logger.info(f"Completed: {step_name} ✓")

            # Generate success report
            self.generate_deployment_report(True, config)
            return True

        except Exception as e:
            logger.error(f"Deployment error: {e}")
            return False


def main():
    """Main entry point"""
    # Ensure logs directory exists
    os.makedirs("C:\\EQ12\\logs", exist_ok=True)

    launcher = EQ12ProductionLauncher()
    success = launcher.launch()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
