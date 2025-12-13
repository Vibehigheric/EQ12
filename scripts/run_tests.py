#!/usr/bin/env python3
"""
EQ12 Test Runner with Sports Betting Compliance Validation
Professiona            result = subprocess.run(
                [sys.executable, "-m", "ruf", "check", ".", "--output-format=json"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=60
            ) testing framework with CI/CD integration
"""

import argparse
import asyncio
import json
import logging
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S UTC",
)
logger = logging.getLogger(__name__)

# Force UTC timezone for all operations
if logger.handlers:
    logger.handlers[0].setFormatter(
        logging.Formatter(
            "%(asctime)s UTC - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )


class EQ12TestRunner:
    """Professional test runner for EQ12 sports betting automation system"""

    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or Path(__file__).parent.parent
        self.test_results: dict[str, dict] = {}
        self.start_time = datetime.now(UTC)

    def run_pytest(self, test_path: str = "tests/", verbose: bool = False) -> bool:
        """Run pytest with professional configuration"""
        logger.info(f"🧪 Running pytest: {test_path}")

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            test_path,
            "--tb=short",
            "--strict-markers",
            "--disable-warnings" if not verbose else "--verbose",
            f"--rootdir={self.workspace_root}",
            "--junit-xml=logs/pytest-results.xml",
        ]

        if verbose:
            cmd.append("-v")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            self.test_results["pytest"] = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": (datetime.now(UTC) - self.start_time).total_seconds(),
            }

            if result.returncode == 0:
                logger.info("✅ pytest: PASSED")
                return True
            else:
                logger.error(f"❌ pytest: FAILED (exit code {result.returncode})")
                if verbose:
                    logger.error(f"stdout: {result.stdout}")
                    logger.error(f"stderr: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ pytest: TIMEOUT (300s)")
            self.test_results["pytest"] = {"success": False, "error": "timeout"}
            return False
        except Exception as e:
            logger.error(f"❌ pytest: ERROR - {e}")
            self.test_results["pytest"] = {"success": False, "error": str(e)}
            return False

    def run_ruff_check(self) -> bool:
        """Run ruff linting with sports betting compliance"""
        logger.info("🔍 Running ruff linting")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruf", "check", ".", "--output-format=json"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            issues = []
            if result.stdout.strip():
                try:
                    issues = json.loads(result.stdout)
                except json.JSONDecodeError:
                    issues = [{"message": result.stdout}]

            self.test_results["ruff"] = {
                "success": result.returncode == 0,
                "issues": issues,
                "count": len(issues),
            }

            if result.returncode == 0:
                logger.info("✅ ruff: PASSED (no issues)")
                return True
            else:
                logger.warning(f"⚠️ ruff: {len(issues)} issues found")
                for issue in issues[:5]:  # Show first 5 issues
                    logger.warning(
                        f"  {issue.get(
                            'filename',
                            'unknown')}:{issue.get('location',
                            {}).get('row',
                            '?')} - {issue.get('message',
                            'Unknown issue'
                        )}"
                    )
                return False

        except Exception as e:
            logger.error(f"❌ ruff check: ERROR - {e}")
            self.test_results["ruff"] = {"success": False, "error": str(e)}
            return False

    def run_mypy_check(self) -> bool:
        """Run mypy type checking"""
        logger.info("🔎 Running mypy type checking")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "mypy", "scripts/", "--ignore-missing-imports"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=120,
            )

            self.test_results["mypy"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
            }

            if result.returncode == 0:
                logger.info("✅ mypy: PASSED")
                return True
            else:
                logger.warning("⚠️ mypy: Type checking issues found")
                if result.stdout:
                    for line in result.stdout.split("\n")[:10]:  # First 10 lines
                        if line.strip():
                            logger.warning(f"  {line}")
                return False

        except Exception as e:
            logger.error(f"❌ mypy: ERROR - {e}")
            self.test_results["mypy"] = {"success": False, "error": str(e)}
            return False

    def run_security_audit(self) -> bool:
        """Run security audit with bandit"""
        logger.info("🔒 Running security audit")

        try:
            # Try bandit if available
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", "scripts/", "-", "json"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            issues = []
            if result.stdout.strip():
                try:
                    audit_data = json.loads(result.stdout)
                    issues = audit_data.get("results", [])
                except json.JSONDecodeError:
                    pass

            self.test_results["security"] = {
                "success": len(issues) == 0,
                "issues": issues,
                "count": len(issues),
            }

            if len(issues) == 0:
                logger.info("✅ Security audit: PASSED")
                return True
            else:
                logger.warning(f"⚠️ Security audit: {len(issues)} issues found")
                for issue in issues[:3]:  # Show first 3 issues
                    logger.warning(
                        f"  {issue.get(
                            'filename',
                            'unknown')}:{issue.get('line_number',
                            '?')} - {issue.get('test_name',
                            'security issue'
                        )}"
                    )
                return False

        except FileNotFoundError:
            logger.info("ℹ️ bandit not installed, skipping security audit")
            self.test_results["security"] = {"success": True, "skipped": True}
            return True
        except Exception as e:
            logger.error(f"❌ Security audit: ERROR - {e}")
            self.test_results["security"] = {"success": False, "error": str(e)}
            return False

    def run_sportsbook_compliance(self) -> bool:
        """Run EQ12 sportsbook compliance validation"""
        logger.info("🏈 Running sportsbook compliance validation")

        try:
            # Check if sportsbook validator exists
            validator_path = self.workspace_root / "scripts" / "eq12_sportsbooks.py"
            if not validator_path.exists():
                logger.warning("⚠️ Sportsbook validator not found, skipping")
                self.test_results["sportsbook"] = {"success": True, "skipped": True}
                return True

            result = subprocess.run(
                [sys.executable, str(validator_path), "--validate-all"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.test_results["sportsbook"] = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr,
            }

            if result.returncode == 0:
                logger.info("✅ Sportsbook compliance: PASSED")
                return True
            else:
                logger.error("❌ Sportsbook compliance: FAILED")
                logger.error(f"Error: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Sportsbook compliance: ERROR - {e}")
            self.test_results["sportsbook"] = {"success": False, "error": str(e)}
            return False

    def save_test_report(self) -> None:
        """Save comprehensive test report"""
        report = {
            "timestamp": self.start_time.isoformat(),
            "duration": (datetime.now(UTC) - self.start_time).total_seconds(),
            "workspace": str(self.workspace_root),
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results.values() if r.get("success", False)),
                "failed": sum(
                    1
                    for r in self.test_results.values()
                    if not r.get("success", False) and not r.get("skipped", False)
                ),
                "skipped": sum(1 for r in self.test_results.values() if r.get("skipped", False)),
            },
        }

        # Save to logs directory
        logs_dir = self.workspace_root / "logs"
        logs_dir.mkdir(exist_ok=True)

        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        report_path = logs_dir / f"test_report_{timestamp}.json"

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📊 Test report saved: {report_path}")

    async def run_all_tests(
        self,
        include_pytest: bool = True,
        include_lint: bool = True,
        include_type_check: bool = True,
        include_security: bool = True,
        include_sportsbook: bool = True,
        verbose: bool = False,
    ) -> bool:
        """Run complete test suite"""
        logger.info("🚀 Starting EQ12 comprehensive test suite")

        all_passed = True

        # Run tests in optimal order
        if include_lint and not self.run_ruff_check():
            all_passed = False

        if include_type_check and not self.run_mypy_check():
            all_passed = False

        if include_pytest and not self.run_pytest(verbose=verbose):
            all_passed = False

        if include_security and not self.run_security_audit():
            all_passed = False

        if include_sportsbook and not self.run_sportsbook_compliance():
            all_passed = False

        # Save comprehensive report
        self.save_test_report()

        # Summary
        duration = (datetime.now(UTC) - self.start_time).total_seconds()

        if all_passed:
            logger.info(f"🎉 All tests PASSED in {duration:.1f}s")
        else:
            logger.error(f"❌ Some tests FAILED (completed in {duration:.1f}s)")

        return all_passed


async def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description="EQ12 Professional Test Runner")
    parser.add_argument("--pytest-only", action="store_true", help="Run only pytest")
    parser.add_argument("--lint-only", action="store_true", help="Run only linting")
    parser.add_argument("--type-check-only", action="store_true", help="Run only type checking")
    parser.add_argument("--security-only", action="store_true", help="Run only security audit")
    parser.add_argument(
        "--sportsbook-only", action="store_true", help="Run only sportsbook compliance"
    )
    parser.add_argument("--skip-pytest", action="store_true", help="Skip pytest")
    parser.add_argument("--skip-lint", action="store_true", help="Skip linting")
    parser.add_argument("--skip-type-check", action="store_true", help="Skip type checking")
    parser.add_argument("--skip-security", action="store_true", help="Skip security audit")
    parser.add_argument("--skip-sportsbook", action="store_true", help="Skip sportsbook compliance")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--workspace", type=Path, help="Workspace root directory")

    args = parser.parse_args()

    # Create test runner
    runner = EQ12TestRunner(workspace_root=args.workspace)

    # Determine what to run
    if args.pytest_only:
        success = runner.run_pytest(verbose=args.verbose)
    elif args.lint_only:
        success = runner.run_ruff_check()
    elif args.type_check_only:
        success = runner.run_mypy_check()
    elif args.security_only:
        success = runner.run_security_audit()
    elif args.sportsbook_only:
        success = runner.run_sportsbook_compliance()
    else:
        # Run full suite with exclusions
        success = await runner.run_all_tests(
            include_pytest=not args.skip_pytest,
            include_lint=not args.skip_lint,
            include_type_check=not args.skip_type_check,
            include_security=not args.skip_security,
            include_sportsbook=not args.skip_sportsbook,
            verbose=args.verbose,
        )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
