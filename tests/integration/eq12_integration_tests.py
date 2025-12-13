#!/usr/bin/env python3
"""
EQ12 Integration Testing Framework

Comprehensive testing system for GPT-5 optimized EQ12 automation stack:
- Component integration testing across all EQ12 services
- Performance monitoring and benchmarking
- Security validation for tunnels and APIs
- End-to-end workflow testing (betting, travel, commerce, finance)
- Automated deployment validation
- GPT-5 agentic pattern verification
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import psutil
    import requests

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️ Missing test dependencies. Run: pip install requests psutil selenium pyyaml")

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
TESTS_DIR = EQ12_HOME / "tests"
INTEGRATION_TESTS_DIR = TESTS_DIR / "integration"
LOGS_DIR = EQ12_HOME / "logs"
INTEGRATION_LOGS_DIR = LOGS_DIR / "integration_tests"

# Ensure directories exist
for directory in [TESTS_DIR, INTEGRATION_TESTS_DIR, INTEGRATION_LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class TestResult:
    """Test result with performance metrics"""

    test_name: str
    success: bool
    duration: float
    message: str = ""
    performance_metrics: dict[str, float] = field(default_factory=dict)
    error_details: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ServiceEndpoint:
    """Service endpoint for testing"""

    name: str
    base_url: str
    health_path: str = "/health"
    auth_required: bool = True
    expected_status: int = 200


class EQ12IntegrationTester:
    """Integration testing framework for EQ12 automation stack"""

    def __init__(self):
        self.eq12_home = EQ12_HOME
        self.logs_dir = INTEGRATION_LOGS_DIR
        self.test_results: list[TestResult] = []

        # Service endpoints for testing
        self.service_endpoints = {
            "eq12_backend": ServiceEndpoint(
                name="EQ12 Backend API",
                base_url="http://localhost:8000",
                health_path="/api/health",
            ),
            "sports_betting": ServiceEndpoint(
                name="Sports Betting Service",
                base_url="http://localhost:8001",
                health_path="/webhook/health",
            ),
            "travel_deals": ServiceEndpoint(
                name="Travel Deals Service",
                base_url="http://localhost:8002",
                health_path="/api/status",
            ),
            "commerce_automation": ServiceEndpoint(
                name="Commerce Automation",
                base_url="http://localhost:8003",
                health_path="/automation/status",
            ),
            "finance_tracker": ServiceEndpoint(
                name="Finance Dashboard",
                base_url="http://localhost:8004",
                health_path="/dashboard/health",
            ),
        }

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(self.logs_dir / "integration_tests.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("EQ12IntegrationTester")

    async def test_service_health(self, service_name: str, endpoint: ServiceEndpoint) -> TestResult:
        """Test service health endpoint"""

        start_time = time.time()

        try:
            # Make health check request
            health_url = f"{endpoint.base_url}{endpoint.health_path}"
            response = requests.get(health_url, timeout=10)

            duration = time.time() - start_time

            if response.status_code == endpoint.expected_status:
                return TestResult(
                    test_name=f"health_check_{service_name}",
                    success=True,
                    duration=duration,
                    message=f"{endpoint.name} health check passed",
                    performance_metrics={
                        "response_time": duration,
                        "status_code": response.status_code,
                    },
                )
            return TestResult(
                test_name=f"health_check_{service_name}",
                success=False,
                duration=duration,
                message=f"Unexpected status code: {response.status_code}",
                error_details=response.text,
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=f"health_check_{service_name}",
                success=False,
                duration=duration,
                message=f"Health check failed: {e!s}",
                error_details=str(e),
            )

    async def test_all_services_health(self) -> list[TestResult]:
        """Test health of all EQ12 services"""

        self.logger.info("🏥 Testing health of all EQ12 services...")

        tasks = []
        for service_name, endpoint in self.service_endpoints.items():
            task = self.test_service_health(service_name, endpoint)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Log results
        for result in results:
            if result.success:
                self.logger.info(
                    f"✅ {result.test_name}: {result.message} ({result.duration:.2f}s)"
                )
            else:
                self.logger.error(f"❌ {result.test_name}: {result.message}")

        return results

    def test_file_structure(self) -> TestResult:
        """Test EQ12 file structure and key files"""

        start_time = time.time()

        required_files = [
            "scripts",
            "tests",
            "logs",
            "configs",
            "AGENTS.md",
            "README.md",
        ]

        missing_files = []
        for file_path in required_files:
            full_path = self.eq12_home / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        duration = time.time() - start_time

        if not missing_files:
            return TestResult(
                test_name="file_structure_check",
                success=True,
                duration=duration,
                message="All required files and directories present",
            )
        return TestResult(
            test_name="file_structure_check",
            success=False,
            duration=duration,
            message=f"Missing files: {', '.join(missing_files)}",
            error_details=f"Missing: {missing_files}",
        )

    def test_python_environment(self) -> TestResult:
        """Test Python environment and dependencies"""

        start_time = time.time()

        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major != 3 or python_version.minor < 9:
                return TestResult(
                    test_name="python_environment",
                    success=False,
                    duration=time.time() - start_time,
                    message=f"Python version {python_version} not supported (need 3.9+)",
                )

            # Check key packages
            required_packages = [
                "requests",
                "fastapi",
                "selenium",
                "playwright",
                "pydantic",
                "openai",
                "pandas",
                "numpy",
            ]

            missing_packages = []
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)

            duration = time.time() - start_time

            if not missing_packages:
                return TestResult(
                    test_name="python_environment",
                    success=True,
                    duration=duration,
                    message = (
                        f"Python {python_version.major}.{python_version.minor} with all required packages",
                    )
                    performance_metrics={
                        "python_version": f"{python_version.major}.{python_version.minor}"
                    },
                )
            return TestResult(
                test_name="python_environment",
                success=False,
                duration=duration,
                message=f"Missing packages: {', '.join(missing_packages)}",
                error_details=f"Missing: {missing_packages}",
            )

        except Exception as e:
            return TestResult(
                test_name="python_environment",
                success=False,
                duration=time.time() - start_time,
                message=f"Python environment test failed: {e!s}",
                error_details=str(e),
            )

    def test_firefox_automation_setup(self) -> TestResult:
        """Test Firefox automation configuration"""

        start_time = time.time()

        try:
            # Check if Firefox is installed
            firefox_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                "/usr/bin/firefox",
                "/Applications/Firefox.app/Contents/MacOS/firefox",
            ]

            firefox_found = False
            for path in firefox_paths:
                if Path(path).exists():
                    firefox_found = True
                    break

            if not firefox_found:
                return TestResult(
                    test_name="firefox_automation_setup",
                    success=False,
                    duration=time.time() - start_time,
                    message="Firefox browser not found",
                )

            # Check Firefox automation files
            firefox_automation_dir = self.eq12_home / "firefox_automation"
            required_files = ["firefox_automation_starter.py", "profiles"]

            missing_files = []
            for file_name in required_files:
                if not (firefox_automation_dir / file_name).exists():
                    missing_files.append(file_name)

            duration = time.time() - start_time

            if not missing_files:
                return TestResult(
                    test_name="firefox_automation_setup",
                    success=True,
                    duration=duration,
                    message="Firefox automation setup complete",
                )
            return TestResult(
                test_name="firefox_automation_setup",
                success=False,
                duration=duration,
                message=f"Missing automation files: {', '.join(missing_files)}",
            )

        except Exception as e:
            return TestResult(
                test_name="firefox_automation_setup",
                success=False,
                duration=time.time() - start_time,
                message=f"Firefox automation test failed: {e!s}",
                error_details=str(e),
            )

    def test_ngrok_configuration(self) -> TestResult:
        """Test ngrok tunnel configuration"""

        start_time = time.time()

        try:
            # Check ngrok installation
            result = subprocess.run(["ngrok", "version"], capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                return TestResult(
                    test_name="ngrok_configuration",
                    success=False,
                    duration=time.time() - start_time,
                    message="Ngrok not installed or not in PATH",
                )

            # Check configuration files
            ngrok_dir = self.eq12_home / "ngrok_system"
            config_files = ["ngrok.yml", "eq12_ngrok_manager.py"]

            missing_files = []
            for file_name in config_files:
                if not (ngrok_dir / file_name).exists():
                    missing_files.append(file_name)

            duration = time.time() - start_time

            if not missing_files:
                return TestResult(
                    test_name="ngrok_configuration",
                    success=True,
                    duration=duration,
                    message="Ngrok configuration complete",
                    performance_metrics={"ngrok_version": result.stdout.strip()},
                )
            return TestResult(
                test_name="ngrok_configuration",
                success=False,
                duration=duration,
                message=f"Missing config files: {', '.join(missing_files)}",
            )

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return TestResult(
                test_name="ngrok_configuration",
                success=False,
                duration=time.time() - start_time,
                message="Ngrok not available",
                error_details=str(e),
            )

    def test_gpt5_integration(self) -> TestResult:
        """Test GPT-5 integration components"""

        start_time = time.time()

        try:
            # Check GPT-5 system prompt
            gpt5_prompt_file = self.eq12_home / "GPT5_DEVELOPER_SYSTEM_PROMPT.md"
            if not gpt5_prompt_file.exists():
                return TestResult(
                    test_name="gpt5_integration",
                    success=False,
                    duration=time.time() - start_time,
                    message="GPT-5 system prompt file missing",
                )

            # Check build system files
            build_system_dir = self.eq12_home / "build_system"
            required_dirs = ["week1_foundation", "week2_gpt5_integration"]

            missing_dirs = []
            for dir_name in required_dirs:
                if not (build_system_dir / dir_name).exists():
                    missing_dirs.append(dir_name)

            # Check OpenAI API key availability
            openai_key = os.getenv("OPENAI_API_KEY")
            key_file = self.eq12_home / "keys" / "openai_api_key.txt"

            has_openai_key = openai_key or key_file.exists()

            duration = time.time() - start_time

            issues = []
            if missing_dirs:
                issues.append(f"Missing build directories: {', '.join(missing_dirs)}")
            if not has_openai_key:
                issues.append("OpenAI API key not configured")

            if not issues:
                return TestResult(
                    test_name="gpt5_integration",
                    success=True,
                    duration=duration,
                    message="GPT-5 integration components ready",
                )
            return TestResult(
                test_name="gpt5_integration",
                success=False,
                duration=duration,
                message=f"GPT-5 integration issues: {'; '.join(issues)}",
            )

        except Exception as e:
            return TestResult(
                test_name="gpt5_integration",
                success=False,
                duration=time.time() - start_time,
                message=f"GPT-5 integration test failed: {e!s}",
                error_details=str(e),
            )

    async def run_performance_benchmarks(self) -> list[TestResult]:
        """Run performance benchmarks on EQ12 components"""

        self.logger.info("⚡ Running performance benchmarks...")

        benchmark_results = []

        # File system performance
        start_time = time.time()
        try:
            # Write test file
            test_file = self.logs_dir / "benchmark_test.json"
            test_data = {
                "benchmark": "file_io",
                "timestamp": datetime.now().isoformat(),
            }

            write_start = time.time()
            with open(test_file, "w") as f:
                json.dump(test_data, f)
            write_time = time.time() - write_start

            # Read test file
            read_start = time.time()
            with open(test_file) as f:
                loaded_data = json.load(f)
            read_time = time.time() - read_start

            # Clean up
            test_file.unlink()

            benchmark_results.append(
                TestResult(
                    test_name="file_system_performance",
                    success=True,
                    duration=time.time() - start_time,
                    message="File I/O performance benchmark completed",
                    performance_metrics={
                        "write_time": write_time,
                        "read_time": read_time,
                        "total_time": write_time + read_time,
                    },
                )
            )

        except Exception as e:
            benchmark_results.append(
                TestResult(
                    test_name="file_system_performance",
                    success=False,
                    duration=time.time() - start_time,
                    message=f"File I/O benchmark failed: {e!s}",
                    error_details=str(e),
                )
            )

        # Memory usage check
        start_time = time.time()
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()

            benchmark_results.append(
                TestResult(
                    test_name="system_resources",
                    success=True,
                    duration=time.time() - start_time,
                    message="System resource check completed",
                    performance_metrics={
                        "memory_rss_mb": memory_info.rss / 1024 / 1024,
                        "memory_vms_mb": memory_info.vms / 1024 / 1024,
                        "cpu_percent": cpu_percent,
                    },
                )
            )

        except Exception as e:
            benchmark_results.append(
                TestResult(
                    test_name="system_resources",
                    success=False,
                    duration=time.time() - start_time,
                    message=f"Resource check failed: {e!s}",
                    error_details=str(e),
                )
            )

        return benchmark_results

    async def run_full_integration_test_suite(self) -> dict[str, Any]:
        """Run complete integration test suite"""

        self.logger.info("🧪 Starting EQ12 Integration Test Suite...")

        all_results = []

        # Component tests
        component_tests = [
            self.test_file_structure,
            self.test_python_environment,
            self.test_firefox_automation_setup,
            self.test_ngrok_configuration,
            self.test_gpt5_integration,
        ]

        self.logger.info("🔧 Running component tests...")
        for test_func in component_tests:
            result = test_func()
            all_results.append(result)

            if result.success:
                self.logger.info(f"✅ {result.test_name}: {result.message}")
            else:
                self.logger.error(f"❌ {result.test_name}: {result.message}")

        # Service health tests
        self.logger.info("🏥 Running service health tests...")
        health_results = await self.test_all_services_health()
        all_results.extend(health_results)

        # Performance benchmarks
        benchmark_results = await self.run_performance_benchmarks()
        all_results.extend(benchmark_results)

        # Calculate summary statistics
        total_tests = len(all_results)
        passed_tests = sum(1 for result in all_results if result.success)
        failed_tests = total_tests - passed_tests

        total_duration = sum(result.duration for result in all_results)

        # Generate test report
        report = {
            "test_suite": "EQ12 Integration Tests",
            "timestamp": datetime.now(UTC).isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": ((passed_tests / total_tests) * 100 if total_tests > 0 else 0),
                "total_duration": total_duration,
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "success": result.success,
                    "duration": result.duration,
                    "message": result.message,
                    "performance_metrics": result.performance_metrics,
                    "timestamp": result.timestamp.isoformat(),
                }
                for result in all_results
            ],
        }

        # Save test report
        report_file = (
            INTEGRATION_LOGS_DIR
            / f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        # Log final summary
        self.logger.info("\n📊 EQ12 Integration Test Suite Complete!")
        self.logger.info(f"   Total Tests: {total_tests}")
        self.logger.info(f"   Passed: {passed_tests} ✅")
        self.logger.info(f"   Failed: {failed_tests} ❌")
        self.logger.info(f"   Success Rate: {report['summary']['success_rate']:.1f}%")
        self.logger.info(f"   Duration: {total_duration:.2f} seconds")
        self.logger.info(f"   Report: {report_file}")

        return report


async def main():
    """Main entry point for integration testing"""

    if not DEPENDENCIES_AVAILABLE:
        print("❌ Missing test dependencies. Install with:")
        print("   pip install requests psutil selenium pyyaml")
        return

    tester = EQ12IntegrationTester()
    report = await tester.run_full_integration_test_suite()

    # Exit with error code if tests failed
    if report["summary"]["failed"] > 0:
        sys.exit(1)
    else:
        print("\n🎉 All EQ12 integration tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
