#!/usr/bin/env python3
"""
EQ12 Complete Development Container Verification System
Purpose: Verify all EQ12 tools working correctly in containerized environment
Agent: GitHub Copilot with EQ12 expertise
Timestamp: 2025-10-10T22:30:00Z

Features:
- Complete EQ12 toolchain verification
- VB debugging system validation
- Python code quality tools testing
- .NET tools integration check
- Security and linting validation
- Performance and health monitoring
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class EQ12DevContainerValidator:
    """Complete validation of EQ12 development container"""

    def __init__(self, workspace: str = "/workspace"):
        # Handle both Windows and Linux paths
        self.workspace = Path(workspace if workspace.startswith("/") else "C:\\\\EQ12")
        self.logs_dir = self.workspace / "logs" / "container_validation"
        self.validation_results = {}

        # Create directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.setup_logging()

        # Tool validation configuration
        self.tools_config = {
            "python": {
                "command": ["python3", "--version"],
                "expected_pattern": r"Python 3\.1[2-9]",
                "required": True,
            },
            "dotnet": {
                "command": ["dotnet", "--version"],
                "expected_pattern": r"[8-9]\.\d+\.\d+",
                "required": True,
            },
            "node": {
                "command": ["node", "--version"],
                "expected_pattern": r"v(2[4-9]|[3-9]\d)\.\d+\.\d+",
                "required": True,
            },
            "git": {
                "command": ["git", "--version"],
                "expected_pattern": r"git version \d+\.\d+",
                "required": True,
            },
            "mono": {
                "command": ["mono", "--version"],
                "expected_pattern": r"Mono JIT compiler version",
                "required": False,  # Optional for VB debugging
            },
        }

    def setup_logging(self):
        """Configure container validation logging"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"container_validation_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🐳 EQ12 Dev Container Validator initialized")

    def validate_system_tools(self) -> dict[str, Any]:
        """Validate core system tools and versions"""
        self.logger.info("🔧 Validating system tools")

        tool_results = {}

        for tool_name, config in self.tools_config.items():
            self.logger.info(f"  Testing {tool_name}...")

            try:
                result = subprocess.run(
                    config["command"], capture_output=True, text=True, timeout=10
                )

                if result.returncode == 0:
                    output = result.stdout.strip()
                    version_match = re.search(config["expected_pattern"], output)

                    if version_match:
                        tool_results[tool_name] = {
                            "status": "✅ PASS",
                            "version": output,
                            "required": config["required"],
                        }
                        self.logger.info(f"    ✅ {tool_name}: {output}")
                    else:
                        tool_results[tool_name] = {
                            "status": "⚠️ VERSION_MISMATCH",
                            "version": output,
                            "expected_pattern": config["expected_pattern"],
                            "required": config["required"],
                        }
                        self.logger.warning(
                            f"    ⚠️ {tool_name}: Version mismatch - {output}")
                else:
                    tool_results[tool_name] = {
                        "status": "❌ FAIL",
                        "error": result.stderr,
                        "required": config["required"],
                    }
                    self.logger.error(f"    ❌ {tool_name}: Failed - {result.stderr}")

            except subprocess.TimeoutExpired:
                tool_results[tool_name] = {
                    "status": "❌ TIMEOUT",
                    "error": "Command timed out",
                    "required": config["required"],
                }
                self.logger.error(f"    ❌ {tool_name}: Timeout")

            except Exception as e:
                tool_results[tool_name] = {
                    "status": "❌ ERROR",
                    "error": str(e),
                    "required": config["required"],
                }
                self.logger.error(f"    ❌ {tool_name}: Error - {e}")

        return tool_results

    def validate_eq12_scripts(self) -> dict[str, Any]:
        """Validate EQ12 automation scripts"""
        self.logger.info("🧪 Validating EQ12 automation scripts")

        script_results = {}

        # EQ12 scripts to validate
        scripts_to_test = {
            "vb_debugging_system": {
                "path": "scripts/eq12_vb_debugging_system.py",
                "test_args": ["--help"],
                "expected_in_output": "EQ12 Advanced VB Debugging System",
            },
            "vb_debug_logger": {
                "path": "scripts/eq12_vb_debug_logger.py",
                "test_args": ["--help"],
                "expected_in_output": "EQ12 Advanced VB Debug Logging",
            },
            "vb_testing_framework": {
                "path": "scripts/eq12_vb_testing_framework.py",
                "test_args": ["--help"],
                "expected_in_output": "EQ12 VB Unit Testing Integration",
            },
            "flake8_autofix": {
                "path": "scripts/eq12_flake8_autofix.py",
                "test_args": ["--help"],
                "expected_in_output": "EQ12 Enhanced Flake8 Auto-Fix System",
            },
            "gitleaks_guardian": {
                "path": "scripts/eq12_gitleaks_guardian.py",
                "test_args": ["--help"],
                "expected_in_output": "EQ12 GitLeaks Guardian System",
            },
        }

        for script_name, config in scripts_to_test.items():
            script_path = self.workspace / config["path"]

            if not script_path.exists():
                script_results[script_name] = {
                    "status": "❌ MISSING",
                    "error": f"Script not found: {script_path}",
                }
                self.logger.error(f"    ❌ {script_name}: Missing - {script_path}")
                continue

            try:
                result = subprocess.run(
                    ["python3", str(script_path)] + config["test_args"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.workspace),
                )

                if result.returncode == 0:
                    output = result.stdout
                    if config["expected_in_output"] in output:
                        script_results[script_name] = {
                            "status": "✅ PASS",
                            "path": str(script_path),
                        }
                        self.logger.info(f"    ✅ {script_name}: Working correctly")
                    else:
                        script_results[script_name] = {
                            "status": "⚠️ OUTPUT_MISMATCH",
                            "path": str(script_path),
                            "output": (output[:200] + "..." if len(output) > 200 else output),
                        }
                        self.logger.warning(f"    ⚠️ {script_name}: Unexpected output")
                else:
                    script_results[script_name] = {
                        "status": "❌ FAIL",
                        "path": str(script_path),
                        "error": result.stderr,
                        "exit_code": result.returncode,
                    }
                    self.logger.error(
                        f"    ❌ {script_name}: Failed with exit code {
                            result.returncode}")

            except Exception as e:
                script_results[script_name] = {
                    "status": "❌ ERROR",
                    "path": str(script_path),
                    "error": str(e),
                }
                self.logger.error(f"    ❌ {script_name}: Error - {e}")

        return script_results

    def validate_python_packages(self) -> dict[str, Any]:
        """Validate Python packages and dependencies"""
        self.logger.info("🐍 Validating Python packages")

        required_packages = [
            "pytest",
            "black",
            "flake8",
            "mypy",
            "pylint",
            "requests",
            "beautifulsoup4",
            "selenium",
            "playwright",
        ]

        package_results = {}

        try:
            # Get installed packages
            result = subprocess.run(
                ["python3", "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                installed_packages = json.loads(result.stdout)
                installed_names = {pkg["name"].lower() for pkg in installed_packages}

                for package in required_packages:
                    if package.lower() in installed_names:
                        # Get version info
                        pkg_info = next(
                            (p for p in installed_packages if p["name"].lower() == package.lower()), None, )
                        package_results[package] = {
                            "status": "✅ INSTALLED",
                            "version": pkg_info["version"] if pkg_info else "unknown",
                        }
                        self.logger.info(
                            f"    ✅ {package}: {
                                pkg_info['version'] if pkg_info else 'installed'}")
                    else:
                        package_results[package] = {
                            "status": "❌ MISSING",
                            "required": True,
                        }
                        self.logger.error(f"    ❌ {package}: Not installed")

            else:
                package_results["pip_list"] = {
                    "status": "❌ FAIL",
                    "error": result.stderr,
                }
                self.logger.error(f"    ❌ Failed to list packages: {result.stderr}")

        except Exception as e:
            package_results["validation"] = {"status": "❌ ERROR", "error": str(e)}
            self.logger.error(f"    ❌ Package validation error: {e}")

        return package_results

    def validate_dotnet_tools(self) -> dict[str, Any]:
        """Validate .NET tools and project templates"""
        self.logger.info("⚙️ Validating .NET tools")

        dotnet_results = {}

        # Check .NET SDKs
        try:
            result = subprocess.run(
                ["dotnet", "--list-sdks"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                sdks = result.stdout.strip().split("\n")
                dotnet_results["sdks"] = {
                    "status": "✅ AVAILABLE",
                    "count": len(sdks),
                    "versions": sdks[:3],  # Show first 3 SDKs
                }
                self.logger.info(f"    ✅ .NET SDKs: {len(sdks)} available")
            else:
                dotnet_results["sdks"] = {"status": "❌ FAIL", "error": result.stderr}

        except Exception as e:
            dotnet_results["sdks"] = {"status": "❌ ERROR", "error": str(e)}

        # Check project templates
        try:
            result = subprocess.run(
                ["dotnet", "new", "--list"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                templates = result.stdout
                mstest_available = "mstest" in templates.lower()

                dotnet_results["templates"] = {
                    "status": "✅ AVAILABLE" if mstest_available else "⚠️ LIMITED",
                    "mstest_available": mstest_available,
                    # Subtract header lines
                    "template_count": len(templates.split("\n")) - 2,
                }
                self.logger.info(
                    f"    ✅ .NET Templates: {
                        'MSTest available' if mstest_available else 'Limited templates'}")
            else:
                dotnet_results["templates"] = {
                    "status": "❌ FAIL",
                    "error": result.stderr,
                }

        except Exception as e:
            dotnet_results["templates"] = {"status": "❌ ERROR", "error": str(e)}

        return dotnet_results

    def run_integration_test(self) -> dict[str, Any]:
        """Run integration test of the complete EQ12 system"""
        self.logger.info("🔗 Running EQ12 integration test")

        integration_results = {}

        # Test 1: VB Debug Logger Demo
        try:
            self.logger.info("  Testing VB debug logger...")
            result = subprocess.run(
                ["python3", "scripts/eq12_vb_debug_logger.py", "--demo"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.workspace),
            )

            integration_results["vb_debug_logger"] = {
                "status": "✅ PASS" if result.returncode == 0 else "❌ FAIL",
                "exit_code": result.returncode,
                "has_output": len(result.stdout) > 100,
            }

        except Exception as e:
            integration_results["vb_debug_logger"] = {
                "status": "❌ ERROR",
                "error": str(e),
            }

        # Test 2: VB Testing Framework Discovery
        try:
            self.logger.info("  Testing VB test discovery...")
            result = subprocess.run(
                ["python3", "scripts/eq12_vb_testing_framework.py", "--discover-tests"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workspace),
            )

            integration_results["vb_test_discovery"] = {
                "status": "✅ PASS" if result.returncode == 0 else "❌ FAIL",
                "exit_code": result.returncode,
                "found_tests": "Found" in result.stdout,
            }

        except Exception as e:
            integration_results["vb_test_discovery"] = {
                "status": "❌ ERROR",
                "error": str(e),
            }

        # Test 3: Flake8 system check
        try:
            self.logger.info("  Testing Flake8 auto-fix system...")
            result = subprocess.run(
                [
                    "python3",
                    "scripts/eq12_flake8_autofix.py",
                    "--workspace",
                    str(self.workspace),
                    "--check-only",
                ],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.workspace),
            )

            integration_results["flake8_autofix"] = {
                "status": "✅ PASS" if result.returncode == 0 else "⚠️ ISSUES_FOUND",
                "exit_code": result.returncode,
                "has_output": len(result.stdout) > 50,
            }

        except Exception as e:
            integration_results["flake8_autofix"] = {
                "status": "❌ ERROR",
                "error": str(e),
            }

        return integration_results

    def generate_validation_report(self) -> Path:
        """Generate comprehensive container validation report"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        report_file = self.logs_dir / f"container_validation_report_{timestamp}.json"

        # Calculate overall health score
        all_results = []
        for category_results in self.validation_results.values():
            if isinstance(category_results, dict):
                for result in category_results.values():
                    if isinstance(result, dict) and "status" in result:
                        if "✅" in result["status"]:
                            all_results.append("PASS")
                        elif "⚠️" in result["status"]:
                            all_results.append("WARNING")
                        else:
                            all_results.append("FAIL")

        passes = all_results.count("PASS")
        warnings = all_results.count("WARNING")
        fails = all_results.count("FAIL")
        total = len(all_results)

        health_score = (passes + warnings * 0.5) / total * 100 if total > 0 else 0

        validation_report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "workspace": str(self.workspace),
            "container_type": "EQ12 Advanced Development Container",
            "validation_results": self.validation_results,
            "summary": {
                "total_checks": total,
                "passed": passes,
                "warnings": warnings,
                "failed": fails,
                "health_score": round(health_score, 2),
            },
            "recommendations": self.generate_recommendations(),
        }

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)

        # Also create markdown report
        md_report = self.generate_markdown_report(validation_report)

        self.logger.info(f"📊 Validation report saved: {report_file}")
        self.logger.info(f"📋 Markdown report saved: {md_report}")

        return report_file

    def generate_recommendations(self) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Check for missing required tools
        if "system_tools" in self.validation_results:
            for tool_name, result in self.validation_results["system_tools"].items():
                if result.get("required") and "❌" in result.get("status", ""):
                    recommendations.append(
                        f"Install or fix {tool_name} - required for EQ12 development"
                    )

        # Check for missing Python packages
        if "python_packages" in self.validation_results:
            missing_packages = []
            for pkg_name, result in self.validation_results["python_packages"].items():
                if "❌" in result.get("status", ""):
                    missing_packages.append(pkg_name)
            if missing_packages:
                recommendations.append(
                    f"Install missing Python packages: {', '.join(missing_packages)}"
                )

        # Check EQ12 scripts
        if "eq12_scripts" in self.validation_results:
            failed_scripts = []
            for script_name, result in self.validation_results["eq12_scripts"].items():
                if "❌" in result.get("status", ""):
                    failed_scripts.append(script_name)
            if failed_scripts:
                recommendations.append(
                    f"Fix or reinstall EQ12 scripts: {', '.join(failed_scripts)}"
                )

        # General recommendations
        if not recommendations:
            recommendations.extend(
                [
                    "✅ Container validation passed - all systems operational",
                    "🚀 EQ12 development environment is ready for advanced VB debugging",
                    "📊 Run regular validation checks to maintain system health",
                    "🔄 Consider setting up automated health monitoring",
                ]
            )

        return recommendations

    def generate_markdown_report(self, report_data: dict) -> Path:
        """Generate human-readable markdown validation report"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        md_file = self.logs_dir / f"container_validation_report_{timestamp}.md"

        report_data["summary"]

        md_content = """# EQ12 Development Container Validation Report

**Generated**: {report_data['timestamp']}
**Workspace**: {report_data['workspace']}
**Container Type**: {report_data['container_type']}

## Health Summary

**Overall Health Score**: {summary['health_score']}%

- ✅ **Passed**: {summary['passed']} checks
- ⚠️ **Warnings**: {summary['warnings']} checks
- ❌ **Failed**: {summary['failed']} checks
- 📊 **Total**: {summary['total_checks']} checks

## System Status

### System Tools
"""

        # Add system tools results
        if "system_tools" in report_data["validation_results"]:
            for tool_name, result in report_data["validation_results"]["system_tools"].items(
            ):
                status = result.get("status", "Unknown")
                version = result.get("version", "")
                md_content += f"- **{tool_name}**: {status} {version}\n"

        # Add Python packages results
        md_content += "\n### Python Packages\n"
        if "python_packages" in report_data["validation_results"]:
            for pkg_name, result in report_data["validation_results"]["python_packages"].items(
            ):
                status = result.get("status", "Unknown")
                version = result.get("version", "")
                md_content += f"- **{pkg_name}**: {status} {version}\n"

        # Add EQ12 scripts results
        md_content += "\n### EQ12 Automation Scripts\n"
        if "eq12_scripts" in report_data["validation_results"]:
            for script_name, result in report_data["validation_results"]["eq12_scripts"].items(
            ):
                status = result.get("status", "Unknown")
                md_content += f"- **{script_name}**: {status}\n"

        # Add recommendations
        md_content += "\n## Recommendations\n\n"
        for i, rec in enumerate(report_data["recommendations"], 1):
            md_content += f"{i}. {rec}\n"

        md_content += """

## Container Capabilities

This EQ12 development container provides:

- **VB Debugging**: Advanced VB.NET debugging with Option Strict/Explicit enforcement
- **Unit Testing**: MSTest framework integration with automated discovery
- **Code Quality**: Flake8, Black, Pylint integration for Python code
- **Security**: GitLeaks scanning and secret detection
- **Browser Automation**: Playwright and Selenium for web scraping
- **Containerization**: WSL2 and Docker development support

---
*Generated by EQ12 Container Validation System*
"""

        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        return md_file

    def run_complete_validation(self) -> dict[str, Any]:
        """Run complete validation of EQ12 development container"""
        self.logger.info("🚀 Starting complete EQ12 container validation")

        start_time = time.time()

        # Run all validation categories
        self.validation_results["system_tools"] = self.validate_system_tools()
        self.validation_results["python_packages"] = self.validate_python_packages()
        self.validation_results["dotnet_tools"] = self.validate_dotnet_tools()
        self.validation_results["eq12_scripts"] = self.validate_eq12_scripts()
        self.validation_results["integration_tests"] = self.run_integration_test()

        end_time = time.time()
        self.validation_results["execution_time"] = f"{
            end_time - start_time:.2f} seconds"

        # Generate comprehensive report
        self.generate_validation_report()

        self.logger.info(
            f"🎉 Container validation completed in {end_time - start_time:.2f} seconds"
        )

        return self.validation_results


def main():
    """Main entry point for EQ12 Container Validator"""
    parser = argparse.ArgumentParser(
        description="EQ12 Complete Development Container Verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --validate-all                    # Run complete container validation
  %(prog)s --check-tools                     # Check system tools only
  %(prog)s --check-scripts                   # Check EQ12 scripts only
  %(prog)s --integration-test                # Run integration tests only
        """,
    )

    parser.add_argument(
        "--workspace",
        default="/workspace",
        help="Workspace directory (default: /workspace for containers, C:\\\\EQ12 for Windows)",
    )
    parser.add_argument(
        "--validate-all", action="store_true", help="Run complete container validation"
    )
    parser.add_argument(
        "--check-tools",
        action="store_true",
        help="Validate system tools only")
    parser.add_argument(
        "--check-scripts",
        action="store_true",
        help="Validate EQ12 scripts only")
    parser.add_argument(
        "--integration-test", action="store_true", help="Run integration tests only"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Auto-detect Windows vs container environment
    if not args.workspace.startswith("/") and not Path(args.workspace).exists():
        args.workspace = "C:\\\\EQ12" if os.name == "nt" else "/workspace"

    try:
        validator = EQ12DevContainerValidator(args.workspace)

        if args.validate_all:
            print("🚀 EQ12 Complete Container Validation")
            print("=" * 50)
            results = validator.run_complete_validation()
            summary = results.get("summary", {})
            print("🎉 Validation completed!")
            print(f"📊 Health Score: {summary.get('health_score', 0)}%")
            print(
                f"✅ Passed: {
                    summary.get(
                        'passed',
                        0)} | ⚠️ Warnings: {
                    summary.get(
                        'warnings',
                        0)} | ❌ Failed: {
                    summary.get(
                        'failed',
                        0)}")

        elif args.check_tools:
            print("🔧 Checking System Tools")
            results = validator.validate_system_tools()
            for tool, result in results.items():
                print(f"  {tool}: {result['status']}")

        elif args.check_scripts:
            print("🧪 Checking EQ12 Scripts")
            results = validator.validate_eq12_scripts()
            for script, result in results.items():
                print(f"  {script}: {result['status']}")

        elif args.integration_test:
            print("🔗 Running Integration Tests")
            results = validator.run_integration_test()
            for test, result in results.items():
                print(f"  {test}: {result['status']}")

        else:
            parser.print_help()

    except Exception as e:
        logging.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
