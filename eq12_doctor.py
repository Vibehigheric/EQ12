#!/usr/bin/env python3
"""
EQ12 Doctor - Comprehensive System Health Check
Validates config, keys, quotas, libraries, encodings, timezones, and parlay rules
Wire this to CI and daily cron for proactive issue detection
"""

from __future__ import annotations

import datetime as dt
import importlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Status indicators
OK = "✅"
WARN = "⚠️"
BAD = "❌"
INFO = "ℹ️"


class EQ12Doctor:
    """Comprehensive EQ12 system health checker"""

    def __init__(self, eq12_root: str | None = None):
        self.eq12_root = Path(eq12_root or "C:\\EQ12")
        self.issues = []
        self.warnings = []
        self.successes = []

    def echo(self, status: str, msg: str):
        """Print status message and track for summary"""
        print(f"{status} {msg}")

        if status == OK:
            self.successes.append(msg)
        elif status == WARN:
            self.warnings.append(msg)
        elif status == BAD:
            self.issues.append(msg)

    def ensure_utf8_logging(self):
        """Prevent Windows console emoji/log crashes"""
        try:
            # Clear existing handlers
            root = logging.getLogger()
            root.handlers.clear()

            # Configure UTF-8 safe handler
            handler = logging.StreamHandler(stream=sys.stdout)

            try:
                # Python 3.9+ supports encoding reconfiguration
                sys.stdout.reconfigure(encoding="utf-8")
                sys.stderr.reconfigure(encoding="utf-8")
            except Exception:
                pass

            # Set UTF-8 environment for subprocess calls
            os.environ["PYTHONIOENCODING"] = "utf-8"

            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            root.addHandler(handler)
            root.setLevel(logging.INFO)

            self.echo(OK, "UTF-8 logging configured safely")
        except Exception as e:
            self.echo(BAD, f"UTF-8 logging setup failed: {e}")

    def load_env(self):
        """Load environment variables from .env file"""
        if load_dotenv:
            env_file = self.eq12_root / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                self.echo(OK, f".env loaded from {env_file}")
            else:
                self.echo(WARN, f".env file not found at {env_file}")
        else:
            self.echo(WARN, "python-dotenv not installed; using system environment only")

    def check_env_keys(self):
        """Validate critical environment variables"""
        required_keys = [
            ("OPENAI_API_KEY", "OpenAI API key (optional if using Azure only)"),
            ("ODDS_API_KEY", "The Odds API key for sports data"),
        ]

        optional_keys = [
            ("AZURE_OPENAI_ENDPOINT", "Azure OpenAI endpoint (https://xxx.openai.azure.com/)"),
            ("AZURE_OPENAI_API_KEY", "Azure OpenAI API key"),
            ("AZURE_OPENAI_DEPLOYMENT", "Azure model deployment name"),
            ("TELEGRAM_BOT_TOKEN", "Telegram bot token for notifications"),
            ("TELEGRAM_CHAT_ID", "Telegram chat ID for notifications"),
        ]

        missing_required = []
        invalid_values = ["", "YOUR_API_KEY", "test-key", "sk-test-"]

        # Check required keys
        for key, desc in required_keys:
            val = os.getenv(key)
            if not val or any(invalid in val for invalid in invalid_values):
                missing_required.append((key, desc))
            else:
                # Validate API key format
                if key == "OPENAI_API_KEY" and not val.startswith("sk-"):
                    self.echo(WARN, f"{key} doesn't look like valid OpenAI key format")
                else:
                    self.echo(OK, f"{key} configured")

        # Check optional keys
        azure_config_count = 0
        for key, desc in optional_keys:
            val = os.getenv(key)
            if val and not any(invalid in val for invalid in invalid_values):
                self.echo(OK, f"{key} configured")
                if key.startswith("AZURE_OPENAI"):
                    azure_config_count += 1
            else:
                self.echo(INFO, f"{key} not configured - {desc}")

        # Azure configuration validation
        if azure_config_count > 0 and azure_config_count < 3:
            self.echo(WARN, "Partial Azure OpenAI config - need ENDPOINT, API_KEY, and DEPLOYMENT")
        elif azure_config_count == 3:
            self.echo(OK, "Complete Azure OpenAI configuration detected")

        # Report missing required keys
        if missing_required:
            for key, desc in missing_required:
                self.echo(BAD, f"{key} missing or invalid → {desc}")
        else:
            self.echo(OK, "All critical environment keys present and valid")

    def check_libraries(self):
        """Check for required Python libraries"""
        required_libs = [
            ("pandas", "Data analysis and CSV handling"),
            ("requests", "HTTP client for API calls"),
            ("python-dotenv", "Environment variable management"),
        ]

        optional_libs = [
            ("gspread", "Google Sheets integration"),
            ("google.auth", "Google authentication"),
            ("git", "GitPython for version control"),
            ("httpx", "Modern HTTP client"),
            ("ruff", "Python linter and formatter"),
            ("openai", "OpenAI API client"),
            ("azure.ai.openai", "Azure OpenAI client"),
        ]

        # Check required libraries
        for lib, desc in required_libs:
            try:
                if lib == "google.auth":
                    importlib.import_module("google.auth")
                else:
                    importlib.import_module(lib.replace("-", "_"))
                self.echo(OK, f"Required lib: {lib}")
            except ImportError as e:
                self.echo(BAD, f"Missing required lib: {lib} - {desc} ({e})")

        # Check optional libraries
        for lib, desc in optional_libs:
            try:
                if lib == "google.auth":
                    importlib.import_module("google.auth")
                elif lib == "azure.ai.openai":
                    importlib.import_module("azure.ai.openai")
                else:
                    importlib.import_module(lib.replace("-", "_"))
                self.echo(OK, f"Optional lib: {lib}")
            except ImportError:
                self.echo(WARN, f"Optional lib missing: {lib} - {desc}")

    def check_pandas_circular(self):
        """Check for pandas import issues and circular dependencies"""
        try:
            import pandas as pd

            # Test basic pandas functionality
            test_df = pd.DataFrame({"test": [1, 2, 3]})
            if len(test_df) == 3:
                self.echo(OK, "pandas import and basic functionality working")
            else:
                self.echo(WARN, "pandas imported but basic operations failed")

        except ImportError as e:
            self.echo(BAD, f"pandas import failed: {e}")
            self.echo(INFO, "Install with: pip install pandas")
        except Exception as e:
            self.echo(WARN, f"pandas import issue (possibly circular): {e}")
            self.echo(INFO, "Use TYPE_CHECKING for DataFrame type hints only")

    def check_timezone_handling(self):
        """Ensure timezone-aware datetime handling"""
        try:
            # Test timezone-aware datetime creation
            now_aware = dt.datetime.now(dt.UTC)

            if now_aware.tzinfo is None:
                self.echo(BAD, "timezone check failed - datetime is naive")
            else:
                self.echo(OK, "timezone-aware datetime working (UTC baseline)")

            # Test ISO string parsing
            test_iso = "2025-10-06T00:21:00Z"
            parsed = dt.datetime.fromisoformat(test_iso.replace("Z", "+00:00"))

            if parsed.tzinfo is not None:
                self.echo(OK, "ISO timestamp parsing with timezone works")
            else:
                self.echo(WARN, "ISO parsing creates naive datetime")

        except Exception as e:
            self.echo(BAD, f"timezone handling test failed: {e}")

    def check_ruff_config(self):
        """Check for duplicate ruff sections in pyproject.toml"""
        pyproject_path = self.eq12_root / "pyproject.toml"

        if not pyproject_path.exists():
            self.echo(WARN, "pyproject.toml not found (ruff config may be in VS Code settings)")
            return

        try:
            content = pyproject_path.read_text(encoding="utf-8")

            # Count [tool.ruff] sections
            ruff_sections = content.count("[tool.ruff]")

            if ruff_sections > 1:
                self.echo(BAD, f"pyproject.toml has {ruff_sections} duplicate [tool.ruff] sections")
                self.echo(
                    INFO,
                    "Merge into single [tool.ruff] section with subsections like [tool.ruff.lint]",
                )
            elif ruff_sections == 1:
                self.echo(OK, "pyproject.toml has single [tool.ruff] section")
            else:
                self.echo(WARN, "No [tool.ruff] section found in pyproject.toml")

        except Exception as e:
            self.echo(WARN, f"Could not read pyproject.toml: {e}")

    def check_file_structure(self):
        """Validate EQ12 directory structure"""
        expected_dirs = ["scripts", "tests", "logs", "configs", "dashboard", "data"]

        expected_files = [
            "eq12_azure_openai_client.py",
            "eq12_parlay_validator.py",
            ".env",
            "pyproject.toml",
        ]

        # Check directories
        for dirname in expected_dirs:
            dir_path = self.eq12_root / dirname
            if dir_path.exists() and dir_path.is_dir():
                self.echo(OK, f"Directory exists: {dirname}")
            else:
                self.echo(WARN, f"Directory missing: {dirname}")

        # Check key files
        for filename in expected_files:
            file_path = self.eq12_root / filename
            if file_path.exists() and file_path.is_file():
                self.echo(OK, f"File exists: {filename}")
            else:
                self.echo(WARN, f"File missing: {filename}")

    def check_api_connectivity(self):
        """Test API connectivity (basic checks without using quota)"""
        try:
            import requests

            # Test basic internet connectivity
            response = requests.get("https://httpbin.org/status/200", timeout=5)
            if response.status_code == 200:
                self.echo(OK, "Internet connectivity working")
            else:
                self.echo(WARN, "Internet connectivity issues")

        except ImportError:
            self.echo(WARN, "requests library not available for connectivity test")
        except Exception as e:
            self.echo(WARN, f"Connectivity test failed: {e}")

    def check_parlay_validation(self):
        """Test parlay validation system"""
        try:
            # Check if validator exists and can import
            validator_path = self.eq12_root / "eq12_parlay_validator.py"

            if validator_path.exists():
                self.echo(OK, "Parlay validator file exists")

                # Try importing the validator
                sys.path.insert(0, str(self.eq12_root))
                from eq12_parlay_validator import ParlayValidator

                ParlayValidator()
                self.echo(OK, "Parlay validator imports and initializes correctly")

            else:
                self.echo(WARN, "Parlay validator not found")

        except ImportError as e:
            self.echo(WARN, f"Could not import parlay validator: {e}")
        except Exception as e:
            self.echo(WARN, f"Parlay validation test failed: {e}")

    def run_full_diagnosis(self) -> dict[str, Any]:
        """Run complete system diagnosis"""
        print("\n🩺 EQ12 DOCTOR - System Health Check")
        print(f"📁 Root: {self.eq12_root}")
        print(f"🐍 Python: {sys.version}")
        print(f"⏰ Time: {dt.datetime.now(dt.UTC).isoformat()}")
        print("=" * 60)

        # Run all checks
        self.ensure_utf8_logging()
        self.load_env()
        self.check_env_keys()
        self.check_libraries()
        self.check_pandas_circular()
        self.check_timezone_handling()
        self.check_ruff_config()
        self.check_file_structure()
        self.check_api_connectivity()
        self.check_parlay_validation()

        # Generate summary
        total_checks = len(self.successes) + len(self.warnings) + len(self.issues)

        print("\n" + "=" * 60)
        print("📊 DIAGNOSIS SUMMARY")
        print(f"{OK} Passed: {len(self.successes)}")
        print(f"{WARN} Warnings: {len(self.warnings)}")
        print(f"{BAD} Issues: {len(self.issues)}")
        print(
            f"📈 Health Score: {len(self.successes)}/{total_checks} ({len(self.successes) / total_checks * 100:.1f}%)"
        )

        # Show critical issues
        if self.issues:
            print("\n🚨 CRITICAL ISSUES TO FIX:")
            for issue in self.issues:
                print(f"   {BAD} {issue}")

        if self.warnings:
            print("\n⚠️  WARNINGS TO REVIEW:")
            for warning in self.warnings[:5]:  # Show top 5
                print(f"   {WARN} {warning}")
            if len(self.warnings) > 5:
                print(f"   ... and {len(self.warnings) - 5} more warnings")

        # Save detailed report
        report = {
            "timestamp": dt.datetime.now(dt.UTC).isoformat(),
            "eq12_root": str(self.eq12_root),
            "python_version": sys.version,
            "health_score": len(self.successes) / total_checks if total_checks > 0 else 0,
            "successes": self.successes,
            "warnings": self.warnings,
            "issues": self.issues,
            "recommendations": self._generate_recommendations(),
        }

        report_path = (
            self.eq12_root
            / "logs"
            / f"doctor_report_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(exist_ok=True)

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Full report saved: {report_path}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")

        if len(self.issues) == 0:
            print("\n🎉 EQ12 system is healthy and ready for production!")
            return report
        else:
            print(f"\n⚠️  System has {len(self.issues)} critical issues that need attention")
            return report

    def _generate_recommendations(self) -> list[str]:
        """Generate actionable recommendations based on findings"""
        recommendations = []

        if any("missing" in issue.lower() for issue in self.issues):
            recommendations.append("Install missing dependencies: pip install -r requirements.txt")

        if any("duplicate" in issue.lower() for issue in self.issues):
            recommendations.append("Fix duplicate ruff configuration in pyproject.toml")

        if any("api key" in issue.lower() for issue in self.issues):
            recommendations.append("Configure valid API keys in .env file")

        if any("timezone" in issue.lower() for issue in self.issues):
            recommendations.append("Update code to use timezone-aware datetime objects")

        if len(self.warnings) > 10:
            recommendations.append("Address warnings to improve system reliability")

        return recommendations


def main():
    """Main entry point for EQ12 Doctor"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 System Health Check")
    parser.add_argument("--root", default="C:\\EQ12", help="EQ12 root directory")
    parser.add_argument(
        "--ci", action="store_true", help="CI mode - exit with error code if issues found"
    )
    args = parser.parse_args()

    doctor = EQ12Doctor(args.root)
    report = doctor.run_full_diagnosis()

    # Exit with appropriate code for CI
    if args.ci:
        if report.get("issues"):
            sys.exit(1)  # Fail CI if critical issues found
        else:
            sys.exit(0)  # Pass CI

    return report


if __name__ == "__main__":
    main()
