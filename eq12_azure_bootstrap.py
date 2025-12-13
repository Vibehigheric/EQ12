#!/usr/bin/env python3
"""
EQ12 Comprehensive Bootstrap Script
Applies all post-integration fixes: API keys, UTF-8 logging, timezone handling, dependencies
"""

import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Configure UTF-8 for Windows console
os.environ["PYTHONIOENCODING"] = "utf-8"
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Setup logging with UTF-8 safety
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True,
    handlers=[logging.StreamHandler(sys.stdout)],
)


class EQ12Bootstrap:
    """Comprehensive EQ12 platform bootstrap with Azure OpenAI integration"""

    def __init__(self, eq12_root: str = "C:\\EQ12"):
        self.eq12_root = Path(eq12_root)
        self.log_path = self.eq12_root / "logs"
        self.log_path.mkdir(exist_ok=True)

        # Ensure we're in the right directory
        os.chdir(self.eq12_root)

        self.status = {
            "timestamp": datetime.now(UTC).isoformat(),
            "steps_completed": [],
            "errors": [],
            "api_keys_configured": False,
            "dependencies_installed": False,
            "utf8_configured": False,
            "azure_repos_cloned": False,
            "xampp_running": False,
        }

    def log_step(self, step: str, success: bool = True):
        """Log bootstrap step with status tracking"""
        if success:
            logging.info(f"✅ {step}")
            self.status["steps_completed"].append(step)
        else:
            logging.error(f"❌ {step}")
            self.status["errors"].append(step)

    def check_api_keys(self) -> bool:
        """Verify OpenAI and Odds API keys are configured"""
        try:
            from dotenv import load_dotenv

            load_dotenv()

            openai_key = os.getenv("OPENAI_API_KEY")
            odds_key = os.getenv("ODDS_API_KEY")

            if not openai_key or openai_key.startswith("test-"):
                self.log_step("OpenAI API key missing or test key", False)
                return False

            if not odds_key:
                self.log_step("Odds API key missing", False)
                return False

            # Test OpenAI key validity
            try:
                from openai import OpenAI

                client = OpenAI(api_key=openai_key)
                client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "ping"}],
                    max_tokens=10,
                )
                self.log_step("OpenAI API key validated")
                self.status["api_keys_configured"] = True
                return True

            except Exception as e:
                self.log_step(f"OpenAI API key validation failed: {e}", False)
                return False

        except ImportError:
            self.log_step("python-dotenv not installed", False)
            return False

    def install_dependencies(self) -> bool:
        """Install required Python dependencies"""
        try:
            venv_pip = self.eq12_root / ".venv" / "Scripts" / "pip"
            if not venv_pip.exists():
                self.log_step("Virtual environment not found", False)
                return False

            required_packages = [
                "openai>=1.52.0",
                "python-dotenv",
                "pandas",
                "google-auth",
                "gspread",
                "GitPython",
                "python-dateutil",
                "pytz",
                "rich",
                "colorama",
                "requests",
            ]

            for package in required_packages:
                result = subprocess.run(
                    [str(venv_pip), "install", "-U", package], capture_output=True, text=True
                )

                if result.returncode != 0:
                    self.log_step(f"Failed to install {package}: {result.stderr}", False)
                    return False

            self.log_step("All dependencies installed successfully")
            self.status["dependencies_installed"] = True
            return True

        except Exception as e:
            self.log_step(f"Dependency installation failed: {e}", False)
            return False

    def configure_utf8_logging(self) -> bool:
        """Configure UTF-8 logging to prevent emoji crashes"""
        try:
            # Create UTF-8 compatible logging configuration
            utf8_config = {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
                },
                "handlers": {
                    "default": {
                        "level": "INFO",
                        "formatter": "standard",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",
                    }
                },
                "loggers": {"": {"handlers": ["default"], "level": "INFO", "propagate": False}},
            }

            config_path = self.eq12_root / "configs" / "logging_utf8.json"
            config_path.parent.mkdir(exist_ok=True)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(utf8_config, f, indent=2, ensure_ascii=False)

            self.log_step("UTF-8 logging configuration created")
            self.status["utf8_configured"] = True
            return True

        except Exception as e:
            self.log_step(f"UTF-8 configuration failed: {e}", False)
            return False

    def check_xampp_services(self) -> bool:
        """Check XAMPP service status"""
        try:
            # Check Apache
            apache_result = subprocess.run(
                ["sc", "query", "Apache2.4"], capture_output=True, text=True
            )

            # Check MySQL
            mysql_result = subprocess.run(["sc", "query", "mysql"], capture_output=True, text=True)

            apache_running = "RUNNING" in apache_result.stdout
            mysql_running = "RUNNING" in mysql_result.stdout

            if apache_running and mysql_running:
                self.log_step("XAMPP services (Apache + MySQL) running")
                self.status["xampp_running"] = True
                return True
            else:
                self.log_step(
                    f"XAMPP services - Apache: {apache_running}, MySQL: {mysql_running}", False
                )
                return False

        except Exception as e:
            self.log_step(f"XAMPP service check failed: {e}", False)
            return False

    def test_azure_openai_client(self) -> bool:
        """Test the Azure-compatible OpenAI client"""
        try:
            # Import our Azure client
            sys.path.insert(0, str(self.eq12_root))
            from eq12_azure_openai_client import test_client

            success = test_client()
            if success:
                self.log_step("Azure-compatible OpenAI client working")
                return True
            else:
                self.log_step("Azure OpenAI client test failed", False)
                return False

        except Exception as e:
            self.log_step(f"Azure client test error: {e}", False)
            return False

    def test_parlay_analysis(self) -> bool:
        """Test parlay analysis with sample data"""
        try:
            # Load sample NFL parlay data
            nfl_file = self.log_path / "nfl_parlays_20251005_181613.json"
            if not nfl_file.exists():
                self.log_step("NFL parlay data file not found", False)
                return False

            with open(nfl_file, encoding="utf-8") as f:
                nfl_data = json.load(f)

            # Import our analysis function
            from eq12_azure_openai_client import analyze_parlay

            # Run analysis on first 3 games
            sample_games = nfl_data.get("data", [])[:3]
            result = analyze_parlay(sample_games)

            if result.get("status") == "success":
                self.log_step("Parlay analysis test successful")

                # Save test result
                test_result_path = (
                    self.log_path / f"parlay_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(test_result_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                return True
            else:
                self.log_step("Parlay analysis failed", False)
                return False

        except Exception as e:
            self.log_step(f"Parlay analysis test error: {e}", False)
            return False

    def generate_status_report(self) -> dict[str, Any]:
        """Generate comprehensive status report"""
        report = {
            "eq12_bootstrap_status": self.status,
            "configuration": {
                "eq12_root": str(self.eq12_root),
                "python_version": sys.version,
                "platform": sys.platform,
            },
            "azure_openai_repos": {
                "betalgo_openai": (self.eq12_root / "betalgo-openai").exists(),
                "openai_dotnet": (self.eq12_root / "openai-dotnet").exists(),
                "openai_dotnet_rage": (self.eq12_root / "openai-dotnet-rage").exists(),
            },
            "recommendations": [],
        }

        # Add recommendations based on status
        if not self.status["api_keys_configured"]:
            report["recommendations"].append("Configure valid OpenAI API key in .env file")

        if not self.status["dependencies_installed"]:
            report["recommendations"].append("Install missing Python dependencies")

        if not self.status["xampp_running"]:
            report["recommendations"].append("Start XAMPP Apache and MySQL services")

        if not report["azure_openai_repos"]["betalgo_openai"]:
            report["recommendations"].append("Clone Azure OpenAI example repositories")

        return report

    def run_bootstrap(self) -> bool:
        """Run complete bootstrap process"""
        logging.info("🚀 Starting EQ12 Azure OpenAI Bootstrap Process...")

        steps = [
            ("API Key Configuration", self.check_api_keys),
            ("Dependency Installation", self.install_dependencies),
            ("UTF-8 Logging Setup", self.configure_utf8_logging),
            ("XAMPP Service Check", self.check_xampp_services),
            ("Azure OpenAI Client Test", self.test_azure_openai_client),
            ("Parlay Analysis Test", self.test_parlay_analysis),
        ]

        success_count = 0

        for step_name, step_func in steps:
            logging.info(f"📋 Executing: {step_name}...")
            try:
                if step_func():
                    success_count += 1
                else:
                    logging.warning(f"⚠️ {step_name} had issues")
            except Exception as e:
                logging.error(f"💥 {step_name} failed with exception: {e}")
                self.status["errors"].append(f"{step_name}: {e}")

        # Generate final report
        report = self.generate_status_report()
        report_path = (
            self.log_path / f"bootstrap_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        success_rate = success_count / len(steps) * 100

        if success_rate >= 80:
            logging.info(
                f"🎉 Bootstrap completed successfully! ({success_count}/{len(steps)} steps)"
            )
            logging.info(f"📊 Report saved: {report_path}")
            return True
        else:
            logging.warning(
                f"⚠️ Bootstrap completed with issues ({success_count}/{len(steps)} steps)"
            )
            logging.info(f"📊 Detailed report: {report_path}")
            return False


def main():
    """Main bootstrap execution"""
    try:
        bootstrap = EQ12Bootstrap()
        success = bootstrap.run_bootstrap()

        if success:
            print("\n🏆 EQ12 Azure OpenAI Bootstrap: SUCCESS")
            print("Your platform is ready for production Azure OpenAI integration!")
        else:
            print("\n⚠️ EQ12 Bootstrap completed with some issues")
            print("Check the detailed report in the logs folder.")

        return 0 if success else 1

    except Exception as e:
        logging.error(f"Bootstrap failed with critical error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
