#!/usr/bin/env python3
"""
EQ12 Complete System Integration & Startup Manager
Full install and startup of all EQ12 GODSTACK programs
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging with detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("C:/EQ12/logs/system_startup.log"),
    ],
)
logger = logging.getLogger(__name__)


class EQ12SystemManager:
    """
    Complete EQ12 GODSTACK System Manager

    Coordinates startup and integration of:
    - Expert Kelly Integration System
    - Paper Trading Module
    - Historical Backtesting Engine
    - EdgeGod Parlay System
    - Chrome/Firefox Governance Automation
    - Discord/Telegram Integration
    - AI Governance Assistant
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        """Initialize EQ12 System Manager"""
        self.eq12_root = Path(eq12_root)
        self.logs_dir = self.eq12_root / "logs"
        self.scripts_dir = self.eq12_root / "scripts"
        self.config_dir = self.eq12_root / "configs"

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)

        # System status tracking
        self.system_status = {
            "startup_time": datetime.now().isoformat(),
            "components": {},
            "errors": [],
            "warnings": [],
        }

        logger.info("EQ12 System Manager initialized")
        logger.info(f"EQ12 Root: {self.eq12_root}")

    def _find_bankroll_tracker(self) -> Path:
        """Find bankroll tracker in possible locations"""
        possible_paths = [
            self.scripts_dir / "bankroll_tracker_clean.py",
            (
                self.eq12_root
                / "sports-betting-optimizer"
                / "src"
                / "core"
                / "bankroll_tracker_clean.py"
            ),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Return first path as default (will be created if needed)
        return possible_paths[0]

    def full_system_startup(
        self,
        skip_browser_setup: bool = False,
        skip_ai_components: bool = False,
        test_mode: bool = False,
    ) -> bool:
        """
        Complete EQ12 system startup sequence

        Args:
            skip_browser_setup: Skip browser automation setup
            skip_ai_components: Skip AI governance components
            test_mode: Run in test mode (no real services)

        Returns:
            True if successful, False if critical failures
        """
        logger.info("STARTING EQ12 GODSTACK COMPLETE SYSTEM")
        logger.info("=" * 60)

        startup_steps = [
            ("Environment Validation", self._validate_environment),
            ("Python Environment Setup", self._setup_python_environment),
            ("Expert Kelly System", self._start_kelly_system),
            ("Paper Trading Module", self._start_paper_trading),
            ("EdgeGod Parlay System", self._start_edgegod_system),
            ("Backtesting Engine", self._initialize_backtesting),
            ("Browser Automation", self._setup_browser_automation),
            ("Discord Integration", self._start_discord_integration),
            ("AI Governance Suite", self._start_ai_governance),
            ("System Health Check", self._system_health_check),
        ]

        if skip_browser_setup:
            startup_steps = [s for s in startup_steps if "Browser" not in s[0]]

        if skip_ai_components:
            startup_steps = [s for s in startup_steps if "AI" not in s[0]]

        success_count = 0
        total_steps = len(startup_steps)

        for step_name, step_func in startup_steps:
            logger.info(f"\nStep: {step_name}")
            logger.info("-" * 40)

            try:
                success = step_func(test_mode=test_mode)
                if success:
                    success_count += 1
                    self.system_status["components"][step_name] = {
                        "status": "SUCCESS",
                        "timestamp": datetime.now().isoformat(),
                    }
                    logger.info(f"✅ {step_name}: SUCCESS")
                else:
                    self.system_status["components"][step_name] = {
                        "status": "FAILED",
                        "timestamp": datetime.now().isoformat(),
                    }
                    logger.error(f"❌ {step_name}: FAILED")

            except Exception as e:
                self.system_status["components"][step_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
                logger.error(f"💥 {step_name}: ERROR - {e}")

        # Final system status
        success_rate = (success_count / total_steps) * 100
        logger.info("\n🎯 EQ12 SYSTEM STARTUP COMPLETE")
        logger.info(f"Success Rate: {success_count}/{total_steps} ({success_rate:.1f}%)")

        if success_rate >= 80:
            logger.info("🎉 SYSTEM READY FOR OPERATION")
            self._save_startup_log()
            return True
        logger.error("⚠️ SYSTEM STARTUP INCOMPLETE - Check errors")
        self._save_startup_log()
        return False

    def _validate_environment(self, test_mode: bool = False) -> bool:
        """Validate EQ12 environment and dependencies"""
        logger.info("Validating EQ12 environment...")

        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            logger.error(f"Python 3.8+ required, found {python_version}")
            return False

        # Check core directories
        required_dirs = [
            self.eq12_root,
            self.scripts_dir,
            self.logs_dir,
            self.config_dir,
        ]

        for directory in required_dirs:
            if not directory.exists():
                logger.warning(f"Creating missing directory: {directory}")
                directory.mkdir(parents=True, exist_ok=True)

        # Check critical files with flexible path resolution
        critical_files = [
            self._find_bankroll_tracker(),
            self.eq12_root / "sports-betting-optimizer" / "src" / "core" / "paper_trader.py",
        ]

        for file_path in critical_files:
            if not file_path.exists():
                logger.error(f"Critical file missing: {file_path}")
                return False

        logger.info("Environment validation complete")
        return True

    def _setup_python_environment(self, test_mode: bool = False) -> bool:
        """Setup Python environment and install dependencies"""
        logger.info("Setting up Python environment...")

        if test_mode:
            logger.info("Test mode: Skipping actual pip installations")
            return True

        # Install required packages
        required_packages = [
            "requests",
            "discord.py",
            "python-telegram-bot",
            "playwright",
            "beautifulsoup4",
            "pandas",
            "numpy",
            "scipy",
            "scikit-learn",
        ]

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                logger.info(f"✓ {package} already installed")
            except ImportError:
                logger.info(f"Installing {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    logger.error(f"Failed to install {package}: {result.stderr}")
                    return False

        return True

    def _start_kelly_system(self, test_mode: bool = False) -> bool:
        """Initialize Expert Kelly Integration System"""
        logger.info("Starting Expert Kelly Integration System...")

        try:
            # Import and initialize Kelly system
            sys.path.append(str(self.scripts_dir))

            # Check Kelly system files with flexible path resolution
            kelly_files = [
                ("kelly_bankroll_manager.py", "sports-betting-optimizer/src/core/"),
                ("azure_ml_manager.py", "sports-betting-optimizer/src/core/"),
                ("expert_kelly_integration.py", "sports-betting-optimizer/"),
            ]

            for kelly_file, subpath in kelly_files:
                file_path = self.eq12_root / subpath / kelly_file
                if not file_path.exists():
                    logger.error(f"Kelly system file missing: {kelly_file} at {file_path}")
                    return False
                logger.info(f"Found Kelly file: {kelly_file}")

            if not test_mode:
                # Run Kelly system setup
                setup_script = self.scripts_dir / "setup_expert_kelly.py"
                if setup_script.exists():
                    result = subprocess.run(
                        [sys.executable, str(setup_script)],
                        capture_output=True,
                        text=True,
                        cwd=str(self.scripts_dir),
                    )

                    if result.returncode != 0:
                        logger.error(f"Kelly setup failed: {result.stderr}")
                        return False

            logger.info("Expert Kelly System initialized")
            return True

        except Exception as e:
            logger.error(f"Kelly system startup failed: {e}")
            return False

    def _start_paper_trading(self, test_mode: bool = False) -> bool:
        """Initialize Paper Trading Module"""
        logger.info("Starting Paper Trading Module...")

        try:
            paper_trader_path = (
                self.eq12_root / "sports-betting-optimizer" / "src" / "core" / "paper_trader.py"
            )

            if not paper_trader_path.exists():
                logger.error("Paper trader module not found")
                return False

            if not test_mode:
                # Test paper trader import
                sys.path.append(str(paper_trader_path.parent))
                import paper_trader

                # Initialize with test balance
                trader = paper_trader.PaperTrader(starting_balance=1000.0, use_mock_results=True)
                logger.info(f"Paper trader initialized with ${trader.balance}")

            logger.info("Paper Trading Module ready")
            return True

        except Exception as e:
            logger.error(f"Paper trading startup failed: {e}")
            return False

    def _start_edgegod_system(self, test_mode: bool = False) -> bool:
        """Start EdgeGod Parlay System"""
        logger.info("Starting EdgeGod Parlay System...")

        try:
            # Look for EdgeGod system
            edgegod_script = None
            for pattern in [
                "edgegod_parlay_ai_v7_synergized_cron.py",
                "edgegod_*.py",
                "parlay_engine.py",
            ]:
                matches = list(self.scripts_dir.glob(pattern))
                if matches:
                    edgegod_script = matches[0]
                    break

            if not edgegod_script:
                logger.warning("EdgeGod system not found - creating placeholder")
                return True  # Non-critical

            if not test_mode:
                # Validate EdgeGod script can be imported
                try:
                    __import__(edgegod_script.stem)
                    logger.info(f"EdgeGod system validated: {edgegod_script.name}")
                except:
                    logger.warning(f"EdgeGod validation failed: {edgegod_script.name}")
                    return True  # Non-critical

            logger.info("EdgeGod Parlay System ready")
            return True

        except Exception as e:
            logger.error(f"EdgeGod system error: {e}")
            return True  # Non-critical system

    def _initialize_backtesting(self, test_mode: bool = False) -> bool:
        """Initialize Historical Backtesting Engine"""
        logger.info("Initializing Backtesting Engine...")

        try:
            backtester_path = (
                self.eq12_root / "sports-betting-optimizer" / "src" / "core" / "backtester.py"
            )

            if not backtester_path.exists():
                logger.error("Backtesting engine not found")
                return False

            # Create backtesting results directory
            backtest_dir = self.eq12_root / "betting-bridge" / "data" / "backtests"
            backtest_dir.mkdir(parents=True, exist_ok=True)

            if not test_mode:
                # Test backtester import
                sys.path.append(str(backtester_path.parent))
                import backtester

                # Initialize backtester
                backtester.HistoricalBacktester(
                    starting_balance=1000.0, results_dir=str(backtest_dir)
                )
                logger.info("Backtesting engine initialized")

            logger.info("Backtesting Engine ready")
            return True

        except Exception as e:
            logger.error(f"Backtesting initialization failed: {e}")
            return False

    def _setup_browser_automation(self, test_mode: bool = False) -> bool:
        """Setup browser automation (Chrome/Firefox)"""
        logger.info("Setting up browser automation...")

        try:
            # Check for browser automation scripts
            browser_scripts = [
                "chrome_governance_automation.py",
                "firefox_governance_automation.py",
            ]

            found_scripts = []
            for script in browser_scripts:
                script_path = self.eq12_root / script
                if script_path.exists():
                    found_scripts.append(script_path)

            if not found_scripts:
                logger.warning("No browser automation scripts found")
                return True  # Non-critical

            if not test_mode:
                # Run browser setup for found scripts
                for script_path in found_scripts:
                    logger.info(f"Running setup for {script_path.name}")
                    result = subprocess.run(
                        [sys.executable, str(script_path), "--setup-profile"],
                        capture_output=True,
                        text=True,
                        cwd=str(self.eq12_root),
                    )

                    if result.returncode == 0:
                        logger.info(f"✓ {script_path.name} setup complete")
                    else:
                        logger.warning(f"⚠ {script_path.name} setup warning: {result.stderr}")

            logger.info("Browser automation ready")
            return True

        except Exception as e:
            logger.error(f"Browser automation setup failed: {e}")
            return True  # Non-critical

    def _start_discord_integration(self, test_mode: bool = False) -> bool:
        """Start Discord integration services"""
        logger.info("Starting Discord integration...")

        try:
            # Check for Discord token
            discord_token = os.environ.get("DISCORD_BOT_TOKEN")
            if not discord_token:
                logger.warning("DISCORD_BOT_TOKEN not set - Discord disabled")
                return True  # Non-critical

            # Look for Discord integration in bankroll tracker
            bankroll_script = self.scripts_dir / "bankroll_tracker_clean.py"
            if bankroll_script.exists() and not test_mode:
                # Test Discord integration
                logger.info("Discord integration available in bankroll tracker")

            logger.info("Discord integration ready")
            return True

        except Exception as e:
            logger.error(f"Discord integration error: {e}")
            return True  # Non-critical

    def _start_ai_governance(self, test_mode: bool = False) -> bool:
        """Start AI Governance Suite"""
        logger.info("Starting AI Governance Suite...")

        try:
            # Check for OpenAI API key
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                logger.warning("OPENAI_API_KEY not set - AI features disabled")
                return True  # Non-critical

            # Look for AI governance scripts
            ai_scripts = [
                "eq12_governance_assistant.py",
                "eq12_openai_governance.py",
                "eq12_streaming_assistant.py",
            ]

            found_ai_scripts = []
            for script in ai_scripts:
                script_path = self.eq12_root / script
                if script_path.exists():
                    found_ai_scripts.append(script_path)

            if not found_ai_scripts:
                logger.warning("No AI governance scripts found")
                return True

            logger.info(f"Found {len(found_ai_scripts)} AI governance components")
            logger.info("AI Governance Suite ready")
            return True

        except Exception as e:
            logger.error(f"AI governance startup failed: {e}")
            return True  # Non-critical

    def _system_health_check(self, test_mode: bool = False) -> bool:
        """Final system health check"""
        logger.info("Performing system health check...")

        try:
            # Check critical components
            health_status = {
                "kelly_system": False,
                "paper_trading": False,
                "backtesting": False,
                "logs_directory": False,
                "config_directory": False,
            }

            # Check Kelly system
            kelly_integration = self.scripts_dir / "expert_kelly_integration.py"
            health_status["kelly_system"] = kelly_integration.exists()

            # Check paper trading
            paper_trader = (
                self.eq12_root / "sports-betting-optimizer" / "src" / "core" / "paper_trader.py"
            )
            health_status["paper_trading"] = paper_trader.exists()

            # Check backtesting
            backtester = (
                self.eq12_root / "sports-betting-optimizer" / "src" / "core" / "backtester.py"
            )
            health_status["backtesting"] = backtester.exists()

            # Check directories
            health_status["logs_directory"] = self.logs_dir.exists()
            health_status["config_directory"] = self.config_dir.exists()

            # Calculate health score
            healthy_components = sum(health_status.values())
            total_components = len(health_status)
            health_score = (healthy_components / total_components) * 100

            logger.info(f"System Health Score: {health_score:.1f}%")

            for component, status in health_status.items():
                status_icon = "✅" if status else "❌"
                logger.info(f"  {status_icon} {component}: {'OK' if status else 'MISSING'}")

            return health_score >= 80

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def _save_startup_log(self):
        """Save detailed startup log"""
        startup_log_path = (
            self.logs_dir / f"startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(startup_log_path, "w") as f:
            json.dump(self.system_status, f, indent=2)

        logger.info(f"Startup log saved: {startup_log_path}")

    def get_system_status(self) -> dict:
        """Get current system status"""
        return self.system_status.copy()

    def restart_component(self, component_name: str) -> bool:
        """Restart a specific system component"""
        logger.info(f"Restarting component: {component_name}")

        component_map = {
            "kelly": self._start_kelly_system,
            "paper_trading": self._start_paper_trading,
            "edgegod": self._start_edgegod_system,
            "backtesting": self._initialize_backtesting,
            "browser": self._setup_browser_automation,
            "discord": self._start_discord_integration,
            "ai": self._start_ai_governance,
        }

        if component_name not in component_map:
            logger.error(f"Unknown component: {component_name}")
            return False

        try:
            return component_map[component_name](test_mode=False)
        except Exception as e:
            logger.error(f"Component restart failed: {e}")
            return False


def main():
    """CLI interface for EQ12 System Manager"""
    parser = argparse.ArgumentParser(description="EQ12 GODSTACK Complete System Manager")

    parser.add_argument("--eq12-root", default="C:/EQ12", help="EQ12 root directory")

    parser.add_argument(
        "--test-mode", action="store_true", help="Run in test mode (no actual services)"
    )

    parser.add_argument("--skip-browser", action="store_true", help="Skip browser automation setup")

    parser.add_argument("--skip-ai", action="store_true", help="Skip AI governance components")

    parser.add_argument(
        "--restart-component",
        help="Restart specific component (kelly, paper_trading, etc.)",
    )

    parser.add_argument("--status", action="store_true", help="Show system status only")

    args = parser.parse_args()

    # Initialize system manager
    system_manager = EQ12SystemManager(eq12_root=args.eq12_root)

    try:
        if args.status:
            # Show status only
            status = system_manager.get_system_status()
            print(json.dumps(status, indent=2))
            return 0

        if args.restart_component:
            # Restart specific component
            success = system_manager.restart_component(args.restart_component)
            return 0 if success else 1

        # Full system startup
        success = system_manager.full_system_startup(
            skip_browser_setup=args.skip_browser,
            skip_ai_components=args.skip_ai,
            test_mode=args.test_mode,
        )

        if success:
            print("\n🎉 EQ12 GODSTACK SYSTEM READY!")
            print("All core components initialized and ready for operation.")
            return 0
        print("\n⚠️ EQ12 System startup completed with warnings/errors.")
        print("Check logs for details.")
        return 1

    except KeyboardInterrupt:
        logger.info("System startup interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"System startup failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
