#!/usr/bin/env python3
"""
EQ12 CI/CD Pipeline Integration Script
A            result = subprocess.run(
                [sys.executable, "-m", "ruf", "check", ".", "--fix"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=60
            )d testing, formatting, and deployment for professional sports betting automation
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s UTC - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class EQ12CIPipeline:
    """Professional CI/CD pipeline for EQ12 sports betting automation"""

    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or Path(__file__).parent.parent
        self.pipeline_results: dict[str, dict] = {}
        self.start_time = datetime.now(UTC)

    def format_code(self) -> bool:
        """Format code with ruff and black"""
        logger.info("🎨 Formatting code with ruff")

        try:
            # Run ruff format
            result = subprocess.run(
                [sys.executable, "-m", "ruf", "format", "."],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=60,
            )

            self.pipeline_results["format"] = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                logger.info("✅ Code formatting: COMPLETED")
                return True
            else:
                logger.error(f"❌ Code formatting: FAILED ({result.returncode})")
                return False

        except Exception as e:
            logger.error(f"❌ Code formatting: ERROR - {e}")
            self.pipeline_results["format"] = {"success": False, "error": str(e)}
            return False

    def fix_lint_issues(self) -> bool:
        """Fix linting issues with ruff --fix"""
        logger.info("🔧 Fixing lint issues with ruff")

        try:
            result = subprocess.run(
                [sys.executable, "-m", "ruf", "check", ".", "--fix"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            self.pipeline_results["lint_fix"] = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                logger.info("✅ Lint fixes: COMPLETED")
                return True
            else:
                logger.warning(
                    f"⚠️ Lint fixes: Some issues remain ({
                        result.returncode})")
                return False

        except Exception as e:
            logger.error(f"❌ Lint fixes: ERROR - {e}")
            self.pipeline_results["lint_fix"] = {"success": False, "error": str(e)}
            return False

    def update_dependencies(self) -> bool:
        """Update dependencies with uv"""
        logger.info("📦 Updating dependencies with uv")

        try:
            # Check if uv is available
            uv_check = subprocess.run(
                ["uv", "--version"], capture_output=True, text=True, timeout=10
            )

            if uv_check.returncode != 0:
                logger.warning("⚠️ uv not available, skipping dependency update")
                self.pipeline_results["dependencies"] = {
                    "success": True,
                    "skipped": True,
                }
                return True

            # Update dependencies
            result = subprocess.run(
                ["uv", "sync", "--all-extras"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )

            self.pipeline_results["dependencies"] = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                logger.info("✅ Dependencies: UPDATED")
                return True
            else:
                logger.error(f"❌ Dependencies: FAILED ({result.returncode})")
                return False

        except Exception as e:
            logger.error(f"❌ Dependencies: ERROR - {e}")
            self.pipeline_results["dependencies"] = {"success": False, "error": str(e)}
            return False

    def run_pre_commit(self) -> bool:
        """Run pre-commit hooks"""
        logger.info("🪝 Running pre-commit hooks")

        try:
            result = subprocess.run(
                ["pre-commit", "run", "--all-files"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300,
            )

            self.pipeline_results["pre_commit"] = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                logger.info("✅ Pre-commit hooks: PASSED")
                return True
            else:
                logger.warning("⚠️ Pre-commit hooks: Some checks failed")
                # Show key failures
                lines = result.stdout.split("\n")
                for line in lines[-10:]:  # Last 10 lines
                    if line.strip() and ("FAILED" in line or "ERROR" in line):
                        logger.warning(f"  {line}")
                return False

        except FileNotFoundError:
            logger.info("ℹ️ pre-commit not installed, skipping hooks")
            self.pipeline_results["pre_commit"] = {"success": True, "skipped": True}
            return True
        except Exception as e:
            logger.error(f"❌ Pre-commit hooks: ERROR - {e}")
            self.pipeline_results["pre_commit"] = {"success": False, "error": str(e)}
            return False

    def run_tests(self) -> bool:
        """Run test suite"""
        logger.info("🧪 Running test suite")

        try:
            # Use our professional test runner
            test_runner_path = self.workspace_root / "scripts" / "run_tests.py"

            if test_runner_path.exists():
                result = subprocess.run(
                    [sys.executable, str(test_runner_path), "--verbose"],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minutes
                )
            else:
                # Fallback to pytest
                result = subprocess.run(
                    [sys.executable, "-m", "pytest", "tests/", "-v"],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

            self.pipeline_results["tests"] = {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

            if result.returncode == 0:
                logger.info("✅ Test suite: PASSED")
                return True
            else:
                logger.error(f"❌ Test suite: FAILED ({result.returncode})")
                return False

        except Exception as e:
            logger.error(f"❌ Test suite: ERROR - {e}")
            self.pipeline_results["tests"] = {"success": False, "error": str(e)}
            return False

    def check_security(self) -> bool:
        """Run security checks"""
        logger.info("🔒 Running security checks")

        security_passed = True

        # Check for hardcoded secrets
        try:
            result = subprocess.run(
                [
                    "grep",
                    "-r",
                    "-E",
                    r"(api_key|token|secret|password)\s*=\s*['\"][^'\"]{10,}",
                    "scripts/",
                    "tests/",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0 and result.stdout.strip():
                logger.error("❌ Security: Potential hardcoded secrets found")
                security_passed = False
            else:
                logger.info("✅ Security: No hardcoded secrets detected")

        except FileNotFoundError:
            # grep not available on Windows
            logger.info("ℹ️ grep not available, skipping secret scan")
        except Exception as e:
            logger.warning(f"⚠️ Security check error: {e}")

        self.pipeline_results["security"] = {"success": security_passed}
        return security_passed

    def generate_pipeline_report(self) -> None:
        """Generate comprehensive pipeline report"""
        report = {
            "timestamp": self.start_time.isoformat(),
            "duration": (datetime.now(UTC) - self.start_time).total_seconds(),
            "workspace": str(self.workspace_root),
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd(),
            },
            "pipeline_results": self.pipeline_results,
            "summary": {
                "total_stages": len(self.pipeline_results),
                "passed": sum(1 for r in self.pipeline_results.values() if r.get("success", False)),
                "failed": sum(
                    1
                    for r in self.pipeline_results.values()
                    if not r.get("success", False) and not r.get("skipped", False)
                ),
                "skipped": sum(
                    1 for r in self.pipeline_results.values() if r.get("skipped", False)
                ),
            },
        }

        # Save report
        logs_dir = self.workspace_root / "logs"
        logs_dir.mkdir(exist_ok=True)

        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        report_path = logs_dir / f"ci_pipeline_{timestamp}.json"

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📊 Pipeline report saved: {report_path}")

    async def run_full_pipeline(
        self,
        skip_deps: bool = False,
        skip_format: bool = False,
        skip_tests: bool = False,
    ) -> bool:
        """Run complete CI/CD pipeline"""
        logger.info("🚀 Starting EQ12 CI/CD Pipeline")

        all_passed = True

        # Stage 1: Dependencies
        if not skip_deps and not self.update_dependencies():
            all_passed = False

        # Stage 2: Code formatting
        if not skip_format:
            if not self.format_code():
                all_passed = False
            if not self.fix_lint_issues():
                all_passed = False

        # Stage 3: Pre-commit hooks
        if not self.run_pre_commit():
            all_passed = False

        # Stage 4: Security checks
        if not self.check_security():
            all_passed = False

        # Stage 5: Test suite
        if not skip_tests and not self.run_tests():
            all_passed = False

        # Generate report
        self.generate_pipeline_report()

        # Summary
        duration = (datetime.now(UTC) - self.start_time).total_seconds()

        if all_passed:
            logger.info(f"🎉 CI/CD Pipeline PASSED in {duration:.1f}s")
        else:
            logger.error(f"❌ CI/CD Pipeline FAILED (completed in {duration:.1f}s)")

        return all_passed


async def main():
    """Main CI/CD pipeline entry point"""
    parser = argparse.ArgumentParser(description="EQ12 CI/CD Pipeline")
    parser.add_argument(
        "--format-only",
        action="store_true",
        help="Run only code formatting")
    parser.add_argument("--test-only", action="store_true", help="Run only tests")
    parser.add_argument(
        "--deps-only",
        action="store_true",
        help="Update dependencies only")
    parser.add_argument(
        "--skip-deps",
        action="store_true",
        help="Skip dependency updates")
    parser.add_argument(
        "--skip-format",
        action="store_true",
        help="Skip code formatting")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test execution")
    parser.add_argument("--workspace", type=Path, help="Workspace root directory")

    args = parser.parse_args()

    # Create pipeline
    pipeline = EQ12CIPipeline(workspace_root=args.workspace)

    # Run requested operations
    success = False

    if args.format_only:
        success = pipeline.format_code() and pipeline.fix_lint_issues()
    elif args.test_only:
        success = pipeline.run_tests()
    elif args.deps_only:
        success = pipeline.update_dependencies()
    else:
        # Run full pipeline
        success = await pipeline.run_full_pipeline(
            skip_deps=args.skip_deps,
            skip_format=args.skip_format,
            skip_tests=args.skip_tests,
        )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
