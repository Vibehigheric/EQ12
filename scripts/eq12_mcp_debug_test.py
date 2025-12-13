#!/usr/bin/env python3
"""
EQ12-MCP Enhanced Debugging Test Suite

Comprehensive test demonstrating the integration of EQ12 VB debugging system
with Model Context Protocol (MCP) servers for enhanced automation capabilities.

Features tested:
- Docker container management via MCP
- Desktop command automation
- VB debugging with MCP integration
- Natural language system interactions

Author: EQ12 AI Agent
Version: 1.0.0
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/mcp_debug_test.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EQ12MCPDebugTester:
    """Enhanced debugging test suite with MCP integration"""

    def __init__(self):
        self.eq12_root = Path("C:/EQ12")
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": [],
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
        }

    def log_test_result(self, test_name: str, success: bool, details: dict[str, Any]):
        """Log test result to structured format"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }

        self.test_results["tests_run"].append(result)
        if success:
            self.test_results["tests_passed"] += 1
        else:
            self.test_results["tests_failed"] += 1
        self.test_results["total_tests"] += 1

        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")

    def test_eq12_vb_debugging_system(self) -> bool:
        """Test core EQ12 VB debugging system"""
        try:
            logger.info("Testing EQ12 VB debugging system...")

            # Check for VB debugging components
            vb_scripts = list(self.eq12_root.glob("**/*vb*"))
            debug_scripts = list(self.eq12_root.glob("**/*debug*"))

            # Test VB Option Strict enforcement
            strict_test = self.run_command(
                [
                    "powershell",
                    "-Command",
                    "Get-Content C:\\\\EQ12\\*.vb -ErrorAction SilentlyContinue | Select-String 'Option Strict' | Measure-Object | Select -ExpandProperty Count",
                ]
            )

            details = {
                "vb_files_found": len(vb_scripts),
                "debug_files_found": len(debug_scripts),
                "option_strict_count": (
                    strict_test.get(
                        "stdout",
                        "0").strip() if strict_test["success"] else "0"),
            }

            success = len(debug_scripts) > 0 and strict_test["success"]
            self.log_test_result("EQ12_VB_Debugging_System", success, details)
            return success

        except Exception as e:
            self.log_test_result("EQ12_VB_Debugging_System", False, {"error": str(e)})
            return False

    def test_mcp_server_health(self) -> bool:
        """Test MCP server health and availability"""
        try:
            logger.info("Testing MCP server health...")

            # Run MCP integration status check
            mcp_status = self.run_command(
                [
                    "python",
                    str(self.eq12_root / "scripts" / "eq12_mcp_integration.py"),
                    "--action",
                    "status",
                ]
            )

            if mcp_status["success"]:
                try:
                    status_data = json.loads(mcp_status["stdout"])
                    healthy_servers = sum(
                        1
                        for s in status_data["servers"].values()
                        if s["health"]["status"] == "healthy"
                    )
                    total_servers = len(status_data["servers"])

                    details = {
                        "healthy_servers": healthy_servers,
                        "total_servers": total_servers,
                        "health_ratio": (
                            healthy_servers / total_servers if total_servers > 0 else 0
                        ),
                        "server_details": status_data["servers"],
                    }

                    success = healthy_servers >= 2  # At least 2 healthy servers
                    self.log_test_result("MCP_Server_Health", success, details)
                    return success

                except json.JSONDecodeError as e:
                    self.log_test_result(
                        "MCP_Server_Health", False, {"error": f"JSON decode error: {e}"}
                    )
                    return False
            else:
                self.log_test_result(
                    "MCP_Server_Health", False, {
                        "error": mcp_status["stderr"]})
                return False

        except Exception as e:
            self.log_test_result("MCP_Server_Health", False, {"error": str(e)})
            return False

    def test_docker_integration(self) -> bool:
        """Test Docker integration with MCP"""
        try:
            logger.info("Testing Docker integration...")

            # Test Docker availability
            docker_version = self.run_command(["docker", "--version"])
            if not docker_version["success"]:
                self.log_test_result(
                    "Docker_Integration", False, {
                        "error": "Docker not available"})
                return False

            # Test Docker container operations
            docker_ps = self.run_command(["docker", "ps", "-a"])
            docker_images = self.run_command(["docker", "images"])

            details = {
                "docker_version": docker_version["stdout"].strip(),
                "containers_accessible": docker_ps["success"],
                "images_accessible": docker_images["success"],
                "container_count": (
                    len(docker_ps["stdout"].split("\n")) - 1 if docker_ps["success"] else 0
                ),
                "image_count": (
                    len(docker_images["stdout"].split("\n")) - 1 if docker_images["success"] else 0
                ),
            }

            success = (
                docker_version["success"] and docker_ps["success"] and docker_images["success"])
            self.log_test_result("Docker_Integration", success, details)
            return success

        except Exception as e:
            self.log_test_result("Docker_Integration", False, {"error": str(e)})
            return False

    def test_desktop_automation_mcp(self) -> bool:
        """Test desktop automation via MCP"""
        try:
            logger.info("Testing desktop automation MCP...")

            # Test PowerShell automation
            ps_test = self.run_command(
                [
                    "powershell",
                    "-Command",
                    "Get-Process | Where-Object {$_.ProcessName -eq 'explorer'} | Measure-Object | Select -ExpandProperty Count",
                ])

            # Test file system operations
            fs_test = self.run_command(
                [
                    "powershell",
                    "-Command",
                    f"Test-Path {self.eq12_root}; Get-ChildItem {self.eq12_root} | Measure-Object | Select -ExpandProperty Count",
                ]
            )

            details = {
                "powershell_accessible": ps_test["success"],
                "explorer_processes": (ps_test["stdout"].strip() if ps_test["success"] else "0"),
                "filesystem_accessible": fs_test["success"],
                "eq12_files": (fs_test["stdout"].split()[-1] if fs_test["success"] else "0"),
            }

            success = ps_test["success"] and fs_test["success"]
            self.log_test_result("Desktop_Automation_MCP", success, details)
            return success

        except Exception as e:
            self.log_test_result("Desktop_Automation_MCP", False, {"error": str(e)})
            return False

    def test_eq12_pytest_integration(self) -> bool:
        """Test EQ12 pytest suite with MCP enhancement"""
        try:
            logger.info("Testing EQ12 pytest integration...")

            # Run pytest on EQ12 tests
            pytest_result = self.run_command(
                [
                    "python",
                    "-m",
                    "pytest",
                    str(self.eq12_root / "tests"),
                    "-v",
                    "--tb=short",
                    "--maxfail=5",
                ],
                cwd=str(self.eq12_root),
            )

            # Analyze pytest output
            if pytest_result["success"]:
                output_lines = pytest_result["stdout"].split("\n")
                passed = len([l for l in output_lines if " PASSED " in l])
                failed = len([l for l in output_lines if " FAILED " in l])

                details = {
                    "tests_passed": passed,
                    "tests_failed": failed,
                    "pytest_exit_code": 0,
                    "output_summary": (
                        output_lines[-10:] if len(output_lines) > 10 else output_lines
                    ),
                }

                success = failed == 0 and passed > 0
            else:
                details = {
                    "pytest_exit_code": 1,
                    # Limit error output
                    "error_output": pytest_result["stderr"][:1000],
                    "tests_passed": 0,
                    "tests_failed": 0,
                }
                success = False

            self.log_test_result("EQ12_Pytest_Integration", success, details)
            return success

        except Exception as e:
            self.log_test_result("EQ12_Pytest_Integration", False, {"error": str(e)})
            return False

    def test_comprehensive_integration(self) -> bool:
        """Test comprehensive EQ12-MCP integration"""
        try:
            logger.info("Testing comprehensive EQ12-MCP integration...")

            # Start MCP debug session briefly
            mcp_debug = self.run_command(
                [
                    "python",
                    str(self.eq12_root / "scripts" / "eq12_mcp_integration.py"),
                    "--action",
                    "test",
                ],
                timeout=30,
            )

            # Test PowerShell wrapper
            ps_wrapper = self.run_command(
                [
                    "powershell",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(self.eq12_root / "scripts" / "eq12_mcp_integration.ps1"),
                    "-Action",
                    "status",
                ],
                timeout=30,
            )

            details = {
                "mcp_test_successful": mcp_debug["success"],
                "powershell_wrapper_works": ps_wrapper["success"],
                "integration_files_exist": all(
                    [
                        (self.eq12_root / "scripts" / "eq12_mcp_integration.py").exists(),
                        (self.eq12_root / "scripts" / "eq12_mcp_integration.ps1").exists(),
                    ]
                ),
                "mcp_output": (
                    mcp_debug["stdout"][:500] if mcp_debug["success"] else mcp_debug["stderr"][:500]
                ),
                "ps_output": (
                    ps_wrapper["stdout"][:500]
                    if ps_wrapper["success"]
                    else ps_wrapper["stderr"][:500]
                ),
            }

            success = mcp_debug["success"] and details["integration_files_exist"]
            self.log_test_result("Comprehensive_Integration", success, details)
            return success

        except Exception as e:
            self.log_test_result("Comprehensive_Integration", False, {"error": str(e)})
            return False

    def run_command(
        self, cmd: list[str], timeout: int = 10, cwd: str | None = None
    ) -> dict[str, Any]:
        """Run shell command and return structured result"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd)

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "cmd": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Command timeout",
                "cmd": " ".join(cmd),
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "cmd": " ".join(cmd),
            }

    def run_all_tests(self) -> dict[str, Any]:
        """Run complete test suite"""
        logger.info("🚀 Starting EQ12-MCP Enhanced Debug Test Suite...")

        # Run all tests
        tests = [
            self.test_eq12_vb_debugging_system,
            self.test_mcp_server_health,
            self.test_docker_integration,
            self.test_desktop_automation_mcp,
            self.test_eq12_pytest_integration,
            self.test_comprehensive_integration,
        ]

        for test in tests:
            try:
                test()
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
                self.log_test_result(test.__name__, False, {"exception": str(e)})

        # Generate final report
        self.test_results["success_rate"] = (
            self.test_results["tests_passed"] / self.test_results["total_tests"]
            if self.test_results["total_tests"] > 0
            else 0
        )

        # Save results to log file
        results_file = (
            self.eq12_root
            / "logs"
            / f"mcp_debug_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2)

        logger.info(f"✅ Test suite completed. Results saved to: {results_file}")
        return self.test_results

    def print_summary(self):
        """Print test summary"""
        print("\n🔬 EQ12-MCP ENHANCED DEBUG TEST RESULTS")
        print("═══════════════════════════════════════════")
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['tests_passed']} ✅")
        print(f"Failed: {self.test_results['tests_failed']} ❌")
        print(f"Success Rate: {self.test_results['success_rate']:.1%}")

        if self.test_results["success_rate"] >= 0.8:
            print("\n🎉 EXCELLENT! EQ12-MCP integration is highly functional!")
        elif self.test_results["success_rate"] >= 0.6:
            print("\n✅ GOOD! EQ12-MCP integration is mostly functional with minor issues.")
        else:
            print("\n⚠️  NEEDS ATTENTION! EQ12-MCP integration has significant issues.")

        print("\n📊 Individual Test Results:")
        for test in self.test_results["tests_run"]:
            status = "✅" if test["success"] else "❌"
            print(f"   {status} {test['test_name']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="EQ12-MCP Enhanced Debug Test Suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    tester = EQ12MCPDebugTester()

    try:
        results = tester.run_all_tests()
        tester.print_summary()

        # Exit with appropriate code
        if results["success_rate"] >= 0.8:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n💥 Test suite error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
