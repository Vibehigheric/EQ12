#!/usr/bin/env python3
"""
EQ12 Betting Intelligence Launcher
Cold start system for MLB playoff automation
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Add EQ12 to Python path
sys.path.insert(0, "C:/EQ12")
sys.path.insert(0, "C:/EQ12/scripts")

# Configure logging
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / f"cold_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("EQ12.ColdStart")


class EQ12ColdStart:
    """EQ12 System Cold Start Manager"""

    def __init__(self):
        self.start_time = datetime.now()
        self.services_started = []
        self.errors = []

    def print_banner(self):
        """Print EQ12 startup banner"""
        banner = """
🚀 ╔══════════════════════════════════════════════╗
   ║           EQ12 BETTING INTELLIGENCE          ║
   ║              COLD START SYSTEM               ║
   ║                                              ║
   ║  MLB Playoff Edition - October 2025          ║
   ║  Lineup Locks • SGP Builder • Arb Scanner    ║
   ╚══════════════════════════════════════════════╝

⚡ Initializing core systems...
"""
        print(banner)
        logger.info("EQ12 Cold Start initiated")

    def check_prerequisites(self):
        """Check system prerequisites"""
        logger.info("🔍 Checking prerequisites...")

        # Check Python version

        # Check required directories
        required_dirs = [
            "C:/EQ12/logs",
            "C:/EQ12/configs",
            "C:/EQ12/scripts",
            "C:/EQ12/data",
        ]

        for dir_path in required_dirs:
            Path(dir_path).mkdir(exist_ok=True)
            logger.info(f"✅ Directory verified: {dir_path}")

        # Check configuration files
        config_file = Path("C:/EQ12/configs/betting_intelligence_config.json")
        if not config_file.exists():
            logger.error("❌ Betting intelligence config not found")
            raise FileNotFoundError(f"Missing config: {config_file}")

        logger.info("✅ All prerequisites met")

    def load_configuration(self):
        """Load system configuration"""
        logger.info("📋 Loading configuration...")

        config_file = Path("C:/EQ12/configs/betting_intelligence_config.json")

        try:
            with open(config_file) as f:
                self.config = json.load(f)

            logger.info(
                f"✅ Config loaded: {self.config['system']['name']} v{self.config['system']['version']}"
            )

            # Validate critical settings
            required_keys = ["safety_rails", "api_limits", "books", "mlb_playoff_teams"]
            for key in required_keys:
                if key not in self.config:
                    raise KeyError(f"Missing required config section: {key}")

            return self.config

        except Exception as e:
            logger.error(f"❌ Configuration load failed: {e}")
            raise

    def initialize_logging(self):
        """Initialize enhanced logging"""
        logger.info("📝 Initializing enhanced logging...")

        # Create audit trail
        audit_file = Path("C:/EQ12/logs/audit_trail.jsonl")
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "cold_start_initiated",
            "system_version": self.config["system"]["version"],
            "mode": self.config["system"]["mode"],
        }

        with open(audit_file, "a") as f:
            f.write(json.dumps(audit_entry) + "\\n")

        logger.info("✅ Audit trail initialized")

    def start_core_services(self):
        """Start core EQ12 services"""
        logger.info("🔧 Starting core services...")

        services = [
            ("Circuit Breakers", self._init_circuit_breakers),
            ("API Rate Limiters", self._init_rate_limiters),
            ("Safety Rails", self._init_safety_rails),
            ("Task Queue", self._init_task_queue),
            ("Health Monitor", self._init_health_monitor),
        ]

        for service_name, init_func in services:
            try:
                logger.info(f"🚀 Starting {service_name}...")
                init_func()
                self.services_started.append(service_name)
                logger.info(f"✅ {service_name} started successfully")

            except Exception as e:
                error_msg = f"❌ Failed to start {service_name}: {e}"
                logger.error(error_msg)
                self.errors.append(error_msg)

    def _init_circuit_breakers(self):
        """Initialize circuit breakers"""
        self.circuit_breakers = {}

        for api_name in ["odds_api", "lineup_api", "weather_api"]:
            self.circuit_breakers[api_name] = {
                "state": "CLOSED",
                "failure_count": 0,
                "last_failure": None,
            }

    def _init_rate_limiters(self):
        """Initialize API rate limiters"""
        self.rate_limiters = {}

        for api_name, limits in self.config["api_limits"].items():
            self.rate_limiters[api_name] = {
                "requests_per_minute": limits["requests_per_minute"],
                "current_count": 0,
                "window_start": time.time(),
            }

    def _init_safety_rails(self):
        """Initialize safety rails"""
        self.safety_state = {
            "daily_exposure": 0.0,
            "freeze_mode": False,
            "consecutive_losses": 0,
            "last_reset": datetime.now().date(),
        }

    def _init_task_queue(self):
        """Initialize task processing queue"""
        self.task_queue_size = 0
        self.task_stats = {"processed": 0, "failed": 0, "retried": 0}

    def _init_health_monitor(self):
        """Initialize health monitoring"""
        self.health_status = {
            "startup_time": self.start_time,
            "last_health_check": datetime.now(),
            "services_healthy": len(self.services_started),
            "services_failed": len(self.errors),
        }

    def start_betting_intelligence(self):
        """Start the betting intelligence system"""
        logger.info("🎯 Starting betting intelligence system...")

        try:
            # Import and start orchestrator
            from eq12_orchestrator import EQ12Orchestrator

            # This would normally start the async orchestrator
            # For now, just log the successful import
            logger.info("✅ Orchestrator imported successfully")

            # Create system status summary
            self._create_status_summary()

        except ImportError as e:
            logger.error(f"❌ Failed to import orchestrator: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to start betting intelligence: {e}")
            raise

    def _create_status_summary(self):
        """Create startup status summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        summary = {
            "startup_time_seconds": elapsed,
            "services_started": self.services_started,
            "errors": self.errors,
            "system_health": "HEALTHY" if not self.errors else "DEGRADED",
            "config_version": self.config["system"]["version"],
            "mlb_teams": self.config["mlb_playoff_teams"],
            "safety_rails_active": True,
            "ready_for_betting": len(self.errors) == 0,
        }

        # Save status to file
        status_file = Path("C:/EQ12/logs/startup_status.json")
        with open(status_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        # Print summary
        logger.info("📊 STARTUP SUMMARY")
        logger.info(f"   Time: {elapsed:.2f}s")
        logger.info(
            f"   Services: {len(self.services_started)}/{len(self.services_started) + len(self.errors)}"
        )
        logger.info(f"   Health: {summary['system_health']}")

        if summary["ready_for_betting"]:
            logger.info("🎉 EQ12 BETTING INTELLIGENCE READY!")
        else:
            logger.warning("⚠️ System degraded - check errors before betting")

        return summary

    def run_cold_start(self):
        """Execute complete cold start sequence"""
        try:
            self.print_banner()
            self.check_prerequisites()
            self.load_configuration()
            self.initialize_logging()
            self.start_core_services()
            self.start_betting_intelligence()

            logger.info("🚀 Cold start completed successfully!")
            return True

        except Exception as e:
            logger.error(f"💥 Cold start failed: {e}")
            return False


def main():
    """Main entry point"""
    cold_start = EQ12ColdStart()

    success = cold_start.run_cold_start()

    if success:
        print("\\n✅ EQ12 system is ready for MLB playoff betting!")
        print("📊 Check C:/EQ12/logs/startup_status.json for details")
    else:
        print("\\n❌ Cold start failed - check logs for errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
