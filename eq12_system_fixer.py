"""
EQ12 System Issues Fixer
Addresses Apache port conflicts, Python import paths, timezone handling, and parlay data compatibility
"""

import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class EQ12SystemFixer:
    """Fixes common EQ12 system issues for production deployment"""

    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.issues_found = []
        self.fixes_applied = []

    def run_full_diagnostic(self) -> dict[str, any]:
        """Run comprehensive system diagnostic"""
        logger.info("Starting EQ12 system diagnostic...")

        results = {
            "apache_conflicts": self._check_apache_conflicts(),
            "python_paths": self._check_python_paths(),
            "timezone_handling": self._check_timezone_handling(),
            "parlay_data_format": self._check_parlay_data_format(),
            "file_permissions": self._check_file_permissions(),
            "environment_vars": self._check_environment_vars(),
        }

        # Determine overall health
        results["overall_status"] = (
            "healthy"
            if not any(result.get("issues", []) for result in results.values())
            else "issues_found"
        )

        return results

    def _check_apache_conflicts(self) -> dict[str, any]:
        """Check for Apache port 80 conflicts"""
        issues = []
        recommendations = []

        try:
            # Check if port 80 is in use
            result = subprocess.run(
                ["netstat", "-an", "|", "findstr", ":80"],
                capture_output=True,
                text=True,
                shell=True,
            )

            if result.returncode == 0 and result.stdout.strip():
                issues.append("Port 80 is in use - potential Apache conflict")
                recommendations.extend(
                    [
                        "Configure Apache to use alternate port (8080, 8888)",
                        "Update XAMPP Apache config to avoid IIS conflicts",
                        "Use 'netstat -ano | findstr :80' to identify blocking process",
                    ]
                )

            # Check XAMPP Apache service status
            xampp_apache = Path("C:/xampp/apache/bin/httpd.exe")
            if xampp_apache.exists():
                try:
                    result = subprocess.run(
                        ["sc", "query", "Apache2.4"], capture_output=True, text=True
                    )
                    if "RUNNING" in result.stdout:
                        recommendations.append(
                            "XAMPP Apache is running - ensure proper configuration"
                        )
                except Exception:
                    pass

        except Exception as e:
            issues.append(f"Could not check Apache status: {e}")

        return {
            "status": "ok" if not issues else "issues",
            "issues": issues,
            "recommendations": recommendations,
        }

    def _check_python_paths(self) -> dict[str, any]:
        """Check Python import paths and module resolution"""
        issues = []
        recommendations = []

        # Check if EQ12 is in Python path
        eq12_in_path = str(self.eq12_root) in sys.path
        if not eq12_in_path:
            issues.append("EQ12 directory not in Python path - imports may fail")
            recommendations.append("Add C:/EQ12 to PYTHONPATH or sys.path")

        # Check critical module imports
        critical_modules = [
            "eq12_ai_client",
            "eq12_cost_guards",
            "eq12_parlay_sanitizer",
            "eq12_odds_ingestor",
        ]

        for module in critical_modules:
            try:
                # Try importing from EQ12 directory
                sys.path.insert(0, str(self.eq12_root))
                __import__(module)
            except ImportError as e:
                issues.append(f"Cannot import {module}: {e}")
                recommendations.append(f"Fix {module}.py import errors or dependencies")
            except Exception as e:
                issues.append(f"Error testing {module} import: {e}")

        # Check scripts directory structure
        scripts_dir = self.eq12_root / "scripts"
        if not scripts_dir.exists():
            issues.append("Missing scripts/ directory")
            recommendations.append("Create scripts/ directory with __init__.py")
        elif not (scripts_dir / "__init__.py").exists():
            issues.append("Missing scripts/__init__.py")
            recommendations.append("Create __init__.py in scripts/ directory")

        return {
            "status": "ok" if not issues else "issues",
            "issues": issues,
            "recommendations": recommendations,
            "python_path": sys.path[:5],  # First 5 paths for debugging
        }

    def _check_timezone_handling(self) -> dict[str, any]:
        """Check for timezone handling consistency"""
        issues = []
        recommendations = []

        # Check for naive datetime usage in log files
        logs_dir = self.eq12_root / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.json"):
                try:
                    with open(log_file) as f:
                        content = f.read()
                        # Look for potential naive datetime patterns
                        if '"timestamp": "2025-' in content and "+00:00" not in content:
                            issues.append(f"Potential naive datetime in {log_file.name}")
                            recommendations.append("Ensure all timestamps use UTC timezone")
                except Exception:
                    continue

        # Test current timezone handling
        try:
            # Test UTC datetime creation
            utc_now = datetime.now(UTC)
            local_now = datetime.now()

            if utc_now.tzinfo is None or local_now.tzinfo is not None:
                issues.append("Inconsistent timezone awareness in datetime objects")
                recommendations.append("Always use datetime.now(UTC) for UTC times")

        except Exception as e:
            issues.append(f"Timezone test failed: {e}")
            recommendations.append("Check datetime import: from datetime import datetime, UTC")

        return {
            "status": "ok" if not issues else "issues",
            "issues": issues,
            "recommendations": recommendations,
            "current_utc": datetime.now(UTC).isoformat(),
            "local_offset": str(datetime.now().astimezone().utcoffset()),
        }

    def _check_parlay_data_format(self) -> dict[str, any]:
        """Check parlay data format compatibility"""
        issues = []
        recommendations = []

        # Check for parlay data files
        data_files = [
            self.eq12_root / "data" / "current_parlays.json",
            self.eq12_root / "logs" / "parlay_analysis.json",
        ]

        for data_file in data_files:
            if data_file.exists():
                try:
                    with open(data_file) as f:
                        data = json.load(f)

                    # Check for impossible parlay patterns
                    if isinstance(data, list):
                        for parlay in data:
                            if self._is_impossible_parlay(parlay):
                                issues.append(f"Impossible parlay detected in {data_file.name}")
                                recommendations.append("Run parlay sanitizer to clean data")

                except json.JSONDecodeError as e:
                    issues.append(f"Invalid JSON in {data_file.name}: {e}")
                    recommendations.append(f"Fix JSON syntax in {data_file.name}")
                except Exception as e:
                    issues.append(f"Error reading {data_file.name}: {e}")

        return {
            "status": "ok" if not issues else "issues",
            "issues": issues,
            "recommendations": recommendations,
        }

    def _is_impossible_parlay(self, parlay: dict) -> bool:
        """Check if parlay contains impossible combinations"""
        if not isinstance(parlay, dict) or "legs" not in parlay:
            return False

        legs = parlay.get("legs", [])
        if len(legs) < 2:
            return False

        # Check for same game opposite outcomes
        game_outcomes = {}
        for leg in legs:
            game_id = leg.get("game_id") or f"{leg.get('home_team')}_vs_{leg.get('away_team')}"
            outcome = leg.get("outcome") or leg.get("bet_type")

            if game_id in game_outcomes:
                existing_outcome = game_outcomes[game_id]
                # Check for conflicting outcomes
                conflicts = [
                    (outcome == "over" and existing_outcome == "under"),
                    (outcome == "under" and existing_outcome == "over"),
                    (outcome == "home_win" and existing_outcome == "away_win"),
                    (outcome == "away_win" and existing_outcome == "home_win"),
                ]
                if any(conflicts):
                    return True

            game_outcomes[game_id] = outcome

        return False

    def _check_file_permissions(self) -> dict[str, any]:
        """Check file and directory permissions"""
        issues = []
        recommendations = []

        critical_paths = [
            self.eq12_root / "logs",
            self.eq12_root / "data",
            self.eq12_root / "configs",
        ]

        for path in critical_paths:
            if not path.exists():
                issues.append(f"Missing directory: {path}")
                recommendations.append(f"Create directory: {path}")
                continue

            # Test write permissions
            try:
                test_file = path / "permission_test.tmp"
                with open(test_file, "w") as f:
                    f.write("test")
                test_file.unlink()  # Delete test file
            except PermissionError:
                issues.append(f"No write permission to {path}")
                recommendations.append(f"Grant write permissions to {path}")
            except Exception as e:
                issues.append(f"Permission check failed for {path}: {e}")

        return {
            "status": "ok" if not issues else "issues",
            "issues": issues,
            "recommendations": recommendations,
        }

    def _check_environment_vars(self) -> dict[str, any]:
        """Check critical environment variables"""
        issues = []
        recommendations = []

        required_vars = ["OPENAI_API_KEY", "ODDS_API_KEY"]

        optional_vars = [
            "TELEGRAM_BOT_TOKEN",
            "TELEGRAM_CHAT_ID",
            "AZURE_OPENAI_KEY",
            "AZURE_OPENAI_ENDPOINT",
        ]

        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"Missing required environment variable: {var}")
                recommendations.append(f"Set {var} in environment or .env file")

        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        if missing_optional:
            recommendations.append(f"Optional vars not set: {', '.join(missing_optional)}")

        return {
            "status": "ok" if not issues else "issues",
            "issues": issues,
            "recommendations": recommendations,
            "vars_set": [var for var in required_vars + optional_vars if os.getenv(var)],
        }

    def apply_fixes(self, issues_to_fix: list[str] | None = None) -> dict[str, any]:
        """Apply automatic fixes for detected issues"""
        fixes_applied = []
        fixes_failed = []

        diagnostic = self.run_full_diagnostic()

        # Fix 1: Add EQ12 to Python path
        if any(
            "Python path" in issue for issue in diagnostic.get("python_paths", {}).get("issues", [])
        ):
            try:
                self._fix_python_path()
                fixes_applied.append("Added EQ12 to Python path")
            except Exception as e:
                fixes_failed.append(f"Python path fix failed: {e}")

        # Fix 2: Create missing directories
        for check_name, check_result in diagnostic.items():
            if check_name == "overall_status":
                continue
            if isinstance(check_result, dict) and check_result.get("issues"):
                for issue in check_result["issues"]:
                    if "Missing directory" in issue:
                        try:
                            dir_path = issue.split(": ")[-1]
                            os.makedirs(dir_path, exist_ok=True)
                            fixes_applied.append(f"Created directory: {dir_path}")
                        except Exception as e:
                            fixes_failed.append(f"Directory creation failed: {e}")

        # Fix 3: Create __init__.py files
        scripts_init = self.eq12_root / "scripts" / "__init__.py"
        if not scripts_init.exists():
            try:
                scripts_init.touch()
                fixes_applied.append("Created scripts/__init__.py")
            except Exception as e:
                fixes_failed.append(f"__init__.py creation failed: {e}")

        return {
            "fixes_applied": fixes_applied,
            "fixes_failed": fixes_failed,
            "next_steps": self._get_manual_fix_instructions(diagnostic),
        }

    def _fix_python_path(self):
        """Add EQ12 to Python path"""
        if str(self.eq12_root) not in sys.path:
            sys.path.insert(0, str(self.eq12_root))

    def _get_manual_fix_instructions(self, diagnostic: dict) -> list[str]:
        """Get manual fix instructions for issues that can't be auto-fixed"""
        instructions = []

        # Apache conflicts
        apache_issues = diagnostic.get("apache_conflicts", {}).get("issues", [])
        if apache_issues:
            instructions.extend(
                [
                    "APACHE FIXES:",
                    "1. Stop conflicting services: net stop iisadmin",
                    "2. Change XAMPP Apache port in C:/xampp/apache/conf/httpd.conf",
                    "3. Update Listen directive: Listen 8080",
                    "4. Restart XAMPP Apache service",
                ]
            )

        # Environment variables
        env_issues = diagnostic.get("environment_vars", {}).get("issues", [])
        if env_issues:
            instructions.extend(
                [
                    "ENVIRONMENT FIXES:",
                    "1. Create .env file in C:/EQ12/",
                    "2. Add required keys: OPENAI_API_KEY=your_key_here",
                    "3. Add ODDS_API_KEY=your_odds_key_here",
                    "4. Restart services to pick up new environment",
                ]
            )

        return instructions


def main():
    """Run system diagnostic and fixes"""
    fixer = EQ12SystemFixer()

    print("🔧 EQ12 System Health Check & Fixer")
    print("=" * 50)

    # Run diagnostic
    diagnostic = fixer.run_full_diagnostic()

    # Display results
    for check_name, result in diagnostic.items():
        if check_name == "overall_status":
            continue

        status_emoji = "✅" if result["status"] == "ok" else "❌"
        print(f"{status_emoji} {check_name.replace('_', ' ').title()}")

        if result.get("issues"):
            for issue in result["issues"]:
                print(f"   • {issue}")

        if result.get("recommendations"):
            for rec in result["recommendations"]:
                print(f"   → {rec}")

        print()

    # Apply automatic fixes
    print("🔨 Applying Automatic Fixes...")
    fix_results = fixer.apply_fixes()

    for fix in fix_results["fixes_applied"]:
        print(f"✅ {fix}")

    for failure in fix_results["fixes_failed"]:
        print(f"❌ {failure}")

    # Show manual instructions
    if fix_results["next_steps"]:
        print("\n📋 Manual Fix Instructions:")
        for instruction in fix_results["next_steps"]:
            print(f"   {instruction}")

    # Final status
    overall = diagnostic["overall_status"]
    status_msg = (
        "🎉 System is healthy!" if overall == "healthy" else "⚠️ Issues found - see fixes above"
    )
    print(f"\n{status_msg}")


if __name__ == "__main__":
    main()
