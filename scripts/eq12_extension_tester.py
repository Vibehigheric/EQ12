#!/usr/bin/env python3
"""
EQ12 Extension Development & Testing Suite
Advanced testing, validation, and development tools for the enhanced Firefox extension

This module provides comprehensive testing and validation capabilities for the EQ12
betting dashboard extension, including all security, privacy, developer tools,
UI enhancements, and proxy management features.

Features:
- Extension structure validation
- Security feature testing
- Privacy protection verification
- Developer tools validation
- UI enhancement testing
- Proxy/VPN management testing
- Performance analysis
- Automated testing suite
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f"C:\\\\EQ12\\logs\\\\extension_tester_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class EQ12ExtensionTester:
    """Comprehensive testing suite for EQ12 enhanced Firefox extension"""

    def __init__(self, extension_path: str, test_mode: str = "full"):
        self.extension_path = Path(extension_path)
        self.test_mode = test_mode
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "extension_path": str(self.extension_path),
            "test_mode": test_mode,
            "tests": {},
            "summary": {},
            "errors": [],
        }
        self.driver = None

        # Test configuration
        self.test_sportsbooks = [
            "https://sportsbook.draftkings.com",
            "https://sportsbook.fanduel.com",
            "https://www.bet365.com",
            "https://www.betmgm.com",
        ]

        logger.info(
            f"EQ12 Extension Tester initialized - Path: {self.extension_path}, Mode: {test_mode}"
        )

    def validate_extension_structure(self) -> dict[str, Any]:
        """Validate extension file structure and manifest"""
        logger.info("Validating extension structure...")

        test_result = {
            "name": "Extension Structure Validation",
            "status": "failed",
            "details": {},
            "errors": [],
        }

        # Required files check
        required_files = [
            "manifest.json",
            "background_v3_enhanced.js",
            "sportsbook_scraper_v3_enhanced.js",
            "popup_v3_enhanced.html",
            "popup_v3_enhanced.js",
            "options.html",
            "options.js",
            "privacy_manager.js",
            "developer_tools.js",
            "ui_enhancer.js",
            "proxy_manager.js",
            "tab_manager.js",
            "testing_dashboard.html",
        ]

        missing_files = []
        file_sizes = {}

        for file in required_files:
            file_path = self.extension_path / file
            if not file_path.exists():
                missing_files.append(file)
            else:
                file_sizes[file] = file_path.stat().st_size

        test_result["details"]["required_files"] = {
            "total": len(required_files),
            "found": len(required_files) - len(missing_files),
            "missing": missing_files,
            "file_sizes": file_sizes,
        }

        # Manifest validation
        manifest_path = self.extension_path / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, encoding="utf-8") as f:
                    manifest = json.load(f)

                # Validate required manifest fields
                required_fields = [
                    "manifest_version",
                    "name",
                    "version",
                    "description",
                    "permissions",
                ]
                missing_fields = [
                    field for field in required_fields if field not in manifest]

                test_result["details"]["manifest"] = {
                    "valid": True,
                    "version": manifest.get("manifest_version"),
                    "name": manifest.get("name"),
                    "extension_version": manifest.get("version"),
                    "permissions_count": len(manifest.get("permissions", [])),
                    "missing_fields": missing_fields,
                }

                # Validate enhanced features configuration
                enhanced_features = {
                    "privacy_protection": "declarativeNetRequest"
                    in manifest.get("permissions", []),
                    "proxy_management": "proxy" in manifest.get("permissions", []),
                    "developer_tools": "cookies" in manifest.get("permissions", []),
                    "ui_enhancement": "browsingData" in manifest.get("permissions", []),
                }

                test_result["details"]["enhanced_features"] = enhanced_features

            except json.JSONDecodeError as e:
                test_result["errors"].append(f"Manifest JSON error: {e}")
        else:
            test_result["errors"].append("Manifest file not found")

        # Set test status
        if not missing_files and not test_result["errors"]:
            test_result["status"] = "passed"

        self.results["tests"]["structure_validation"] = test_result
        logger.info(f"Structure validation: {test_result['status']}")
        return test_result

    def test_privacy_features(self) -> dict[str, Any]:
        """Test privacy and security features"""
        logger.info("Testing privacy and security features...")

        test_result = {
            "name": "Privacy & Security Features",
            "status": "failed",
            "details": {},
            "errors": [],
        }

        privacy_manager_path = self.extension_path / "privacy_manager.js"
        if not privacy_manager_path.exists():
            test_result["errors"].append("Privacy manager module not found")
            self.results["tests"]["privacy_features"] = test_result
            return test_result

        try:
            with open(privacy_manager_path, encoding="utf-8") as f:
                privacy_code = f.read()

            # Check for key security features
            security_features = {
                "tracker_blocking": "setupRequestBlocking" in privacy_code,
                "fingerprint_protection": "setupFingerprintingProtection" in privacy_code,
                "webrtc_protection": "setupWebRTCProtection" in privacy_code,
                "user_agent_spoofing": "setupUserAgentProtection" in privacy_code,
                "port_scan_protection": "PORT_SCAN_PROTECTION" in privacy_code,
                "dns_protection": "checkDNSLeak" in privacy_code,
            }

            # Validate tracker database
            tracker_db_present = "trackerDatabase" in privacy_code
            request_blocking_rules = privacy_code.count("addRules")

            test_result["details"] = {
                "security_features": security_features,
                "tracker_database": tracker_db_present,
                "blocking_rules_count": request_blocking_rules,
                "code_size": len(privacy_code),
            }

            # Check if all key features are present
            if all(security_features.values()) and tracker_db_present:
                test_result["status"] = "passed"
            else:
                missing_features = [k for k, v in security_features.items() if not v]
                test_result["errors"].append(
                    f"Missing security features: {missing_features}")

        except Exception as e:
            test_result["errors"].append(f"Privacy features test error: {e}")

        self.results["tests"]["privacy_features"] = test_result
        logger.info(f"Privacy features test: {test_result['status']}")
        return test_result

    def test_developer_tools(self) -> dict[str, Any]:
        """Test developer tools functionality"""
        logger.info("Testing developer tools...")

        test_result = {
            "name": "Developer Tools",
            "status": "failed",
            "details": {},
            "errors": [],
        }

        dev_tools_path = self.extension_path / "developer_tools.js"
        if not dev_tools_path.exists():
            test_result["errors"].append("Developer tools module not found")
            self.results["tests"]["developer_tools"] = test_result
            return test_result

        try:
            with open(dev_tools_path, encoding="utf-8") as f:
                dev_tools_code = f.read()

            # Check for developer features
            developer_features = {
                "debug_console": "setupDebugConsole" in dev_tools_code,
                "performance_monitoring": "setupPerformanceMonitoring" in dev_tools_code,
                "network_monitoring": "setupNetworkMonitoring" in dev_tools_code,
                "measurement_tools": "setupMeasurementTools" in dev_tools_code,
                "cache_management": "setupCacheManager" in dev_tools_code,
                "error_tracking": "trackError" in dev_tools_code,
                "remote_debugging": "remoteLogging" in dev_tools_code,
            }

            # Check for performance monitoring capabilities
            performance_metrics = dev_tools_code.count("performance.measure")
            network_wrapping = "originalFetch" in dev_tools_code

            test_result["details"] = {
                "developer_features": developer_features,
                "performance_metrics": performance_metrics,
                "network_interception": network_wrapping,
                "code_size": len(dev_tools_code),
            }

            if all(developer_features.values()):
                test_result["status"] = "passed"
            else:
                missing_features = [k for k, v in developer_features.items() if not v]
                test_result["errors"].append(
                    f"Missing developer features: {missing_features}")

        except Exception as e:
            test_result["errors"].append(f"Developer tools test error: {e}")

        self.results["tests"]["developer_tools"] = test_result
        logger.info(f"Developer tools test: {test_result['status']}")
        return test_result

    def test_ui_enhancements(self) -> dict[str, Any]:
        """Test UI enhancement features"""
        logger.info("Testing UI enhancements...")

        test_result = {
            "name": "UI Enhancements",
            "status": "failed",
            "details": {},
            "errors": [],
        }

        ui_enhancer_path = self.extension_path / "ui_enhancer.js"
        if not ui_enhancer_path.exists():
            test_result["errors"].append("UI enhancer module not found")
            self.results["tests"]["ui_enhancements"] = test_result
            return test_result

        try:
            with open(ui_enhancer_path, encoding="utf-8") as f:
                ui_code = f.read()

            # Check for UI features
            ui_features = {
                "dark_mode": "setupDarkMode" in ui_code,
                "auto_reload": "setupAutoReload" in ui_code,
                "custom_styles": "setupCustomStyles" in ui_code,
                "animations": "setupAnimations" in ui_code,
                "accessibility": "setupAccessibility" in ui_code,
                "theme_management": "applyTheme" in ui_code,
            }

            # Check for advanced UI capabilities
            css_injection = ui_code.count("insertCSS")
            animation_system = "transition-duration" in ui_code
            accessibility_features = ui_code.count("aria-")

            test_result["details"] = {
                "ui_features": ui_features,
                "css_injections": css_injection,
                "animation_system": animation_system,
                "accessibility_enhancements": accessibility_features,
                "code_size": len(ui_code),
            }

            if all(ui_features.values()):
                test_result["status"] = "passed"
            else:
                missing_features = [k for k, v in ui_features.items() if not v]
                test_result["errors"].append(f"Missing UI features: {missing_features}")

        except Exception as e:
            test_result["errors"].append(f"UI enhancements test error: {e}")

        self.results["tests"]["ui_enhancements"] = test_result
        logger.info(f"UI enhancements test: {test_result['status']}")
        return test_result

    def test_proxy_management(self) -> dict[str, Any]:
        """Test proxy and VPN management features"""
        logger.info("Testing proxy and VPN management...")

        test_result = {
            "name": "Proxy & VPN Management",
            "status": "failed",
            "details": {},
            "errors": [],
        }

        proxy_manager_path = self.extension_path / "proxy_manager.js"
        if not proxy_manager_path.exists():
            test_result["errors"].append("Proxy manager module not found")
            self.results["tests"]["proxy_management"] = test_result
            return test_result

        try:
            with open(proxy_manager_path, encoding="utf-8") as f:
                proxy_code = f.read()

            # Check for proxy features
            proxy_features = {
                "proxy_configuration": "loadProxyConfiguration" in proxy_code,
                "vpn_integration": "setupVPNProviders" in proxy_code,
                "connection_monitoring": "setupConnectionMonitoring" in proxy_code,
                "leak_detection": "checkDNSLeak" in proxy_code,
                "health_monitoring": "monitorVPNHealth" in proxy_code,
                "rule_management": "proxyRules" in proxy_code,
            }

            # Check for advanced proxy capabilities
            vpn_protocols = proxy_code.count("wireguard") + proxy_code.count("openvpn")
            leak_tests = proxy_code.count("leak")
            connection_health = proxy_code.count("healthCheck")

            test_result["details"] = {
                "proxy_features": proxy_features,
                "vpn_protocol_support": vpn_protocols,
                "leak_detection_tests": leak_tests,
                "health_monitoring": connection_health,
                "code_size": len(proxy_code),
            }

            if all(proxy_features.values()):
                test_result["status"] = "passed"
            else:
                missing_features = [k for k, v in proxy_features.items() if not v]
                test_result["errors"].append(
                    f"Missing proxy features: {missing_features}")

        except Exception as e:
            test_result["errors"].append(f"Proxy management test error: {e}")

        self.results["tests"]["proxy_management"] = test_result
        logger.info(f"Proxy management test: {test_result['status']}")
        return test_result

    def setup_selenium_driver(self) -> bool:
        """Set up Selenium WebDriver with extension"""
        logger.info("Setting up Selenium WebDriver with extension...")

        try:
            # Firefox options
            options = FirefoxOptions()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

            # Create Firefox profile
            from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

            profile = FirefoxProfile()

            # Configure profile for extension testing
            profile.set_preference("xpinstall.signatures.required", False)
            profile.set_preference("extensions.ui.developer.hidden", False)
            profile.set_preference("devtools.chrome.enabled", True)

            # Initialize driver
            self.driver = webdriver.Firefox(options=options, firefox_profile=profile)

            # Install extension (temporary)
            # Note: Selenium doesn't directly support temporary extension installation
            # This would require manual installation or using Firefox's debugging
            # protocol

            logger.info("WebDriver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"WebDriver setup failed: {e}")
            self.results["errors"].append(f"WebDriver setup error: {e}")
            return False

    def test_sportsbook_integration(self) -> dict[str, Any]:
        """Test integration with sportsbooks"""
        logger.info("Testing sportsbook integration...")

        test_result = {
            "name": "Sportsbook Integration",
            "status": "failed",
            "details": {},
            "errors": [],
        }

        if not self.setup_selenium_driver():
            test_result["errors"].append("Failed to setup WebDriver")
            self.results["tests"]["sportsbook_integration"] = test_result
            return test_result

        integration_results = {}

        try:
            for sportsbook in self.test_sportsbooks[:2]:  # Test first 2 for speed
                logger.info(f"Testing integration with {sportsbook}")

                sportsbook_test = {
                    "url": sportsbook,
                    "loaded": False,
                    "extension_active": False,
                    "scraper_working": False,
                    "response_time": 0,
                }

                try:
                    start_time = time.time()
                    self.driver.get(sportsbook)

                    # Wait for page load
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )

                    sportsbook_test["loaded"] = True
                    sportsbook_test["response_time"] = time.time() - start_time

                    # Check if extension is active (would need to inject detection script)
                    # This is a simplified check - in reality, you'd inject JavaScript
                    # to check for extension presence

                    time.sleep(2)  # Allow extension to initialize

                    # Check for extension indicators
                    try:
                        # Look for extension-injected elements or modified page behavior
                        extension_elements = self.driver.find_elements(
                            By.CSS_SELECTOR, "[data-eq12-extension]"
                        )
                        sportsbook_test["extension_active"] = len(
                            extension_elements) > 0
                    except BaseException:
                        pass

                    integration_results[sportsbook] = sportsbook_test

                except Exception as e:
                    sportsbook_test["error"] = str(e)
                    integration_results[sportsbook] = sportsbook_test
                    logger.warning(f"Integration test failed for {sportsbook}: {e}")

            test_result["details"] = {
                "tested_sportsbooks": len(integration_results),
                "successful_loads": sum(
                    1 for r in integration_results.values() if r["loaded"]),
                "results": integration_results,
            }

            # Determine overall status
            successful_tests = sum(
                1 for r in integration_results.values() if r["loaded"])
            if successful_tests > 0:
                test_result["status"] = (
                    "passed" if successful_tests == len(integration_results) else "partial")

        except Exception as e:
            test_result["errors"].append(f"Sportsbook integration test error: {e}")

        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None

        self.results["tests"]["sportsbook_integration"] = test_result
        logger.info(f"Sportsbook integration test: {test_result['status']}")
        return test_result

    def run_performance_analysis(self) -> dict[str, Any]:
        """Run performance analysis on extension components"""
        logger.info("Running performance analysis...")

        test_result = {
            "name": "Performance Analysis",
            "status": "failed",
            "details": {},
            "errors": [],
        }

        try:
            # Analyze file sizes and complexity
            component_analysis = {}

            js_files = list(self.extension_path.glob("*.js"))
            for js_file in js_files:
                with open(js_file, encoding="utf-8") as f:
                    content = f.read()

                analysis = {
                    "file_size": len(content),
                    "line_count": len(content.splitlines()),
                    "function_count": content.count("function "),
                    "event_listeners": content.count("addEventListener"),
                    "api_calls": content.count("chrome.") + content.count("browser."),
                    "complexity_score": self._calculate_complexity(content),
                }

                component_analysis[js_file.name] = analysis

            # Calculate overall metrics
            total_size = sum(a["file_size"] for a in component_analysis.values())
            total_functions = sum(a["function_count"]
                                  for a in component_analysis.values())
            total_listeners = sum(a["event_listeners"]
                                  for a in component_analysis.values())
            avg_complexity = sum(a["complexity_score"]
                                 for a in component_analysis.values()) / len(component_analysis)

            test_result["details"] = {
                "component_analysis": component_analysis,
                "overall_metrics": {
                    "total_code_size": total_size,
                    "total_functions": total_functions,
                    "total_event_listeners": total_listeners,
                    "average_complexity": avg_complexity,
                    "components_count": len(component_analysis),
                },
                "performance_recommendations": self._generate_performance_recommendations(
                    component_analysis
                ),
            }

            test_result["status"] = "passed"

        except Exception as e:
            test_result["errors"].append(f"Performance analysis error: {e}")

        self.results["tests"]["performance_analysis"] = test_result
        logger.info(f"Performance analysis: {test_result['status']}")
        return test_result

    def _calculate_complexity(self, code: str) -> float:
        """Calculate code complexity score"""
        # Simple complexity metrics
        complexity = 0
        complexity += code.count("if ") * 1
        complexity += code.count("for ") * 2
        complexity += code.count("while ") * 2
        complexity += code.count("switch ") * 3
        complexity += code.count("catch ") * 2
        complexity += code.count("async ") * 1
        complexity += code.count("Promise") * 2

        # Normalize by lines of code
        lines = len(code.splitlines())
        return complexity / max(lines, 1)

    def _generate_performance_recommendations(self, analysis: dict) -> list[str]:
        """Generate performance recommendations"""
        recommendations = []

        # Check for large files
        large_files = [
            name for name,
            data in analysis.items() if data["file_size"] > 50000]
        if large_files:
            recommendations.append(
                f"Consider splitting large files: {
                    ', '.join(large_files)}")

        # Check for high complexity
        complex_files = [
            name for name,
            data in analysis.items() if data["complexity_score"] > 5]
        if complex_files:
            recommendations.append(
                f"High complexity detected in: {
                    ', '.join(complex_files)}")

        # Check for excessive event listeners
        listener_heavy = [
            name for name,
            data in analysis.items() if data["event_listeners"] > 10]
        if listener_heavy:
            recommendations.append(
                f"Many event listeners in: {
                    ', '.join(listener_heavy)} - consider event delegation")

        if not recommendations:
            recommendations.append("Extension performance looks good!")

        return recommendations

    def run_all_tests(self) -> dict[str, Any]:
        """Run all available tests"""
        logger.info(f"Running all tests in {self.test_mode} mode...")

        # Core tests (always run)
        self.validate_extension_structure()
        self.test_privacy_features()
        self.test_developer_tools()
        self.test_ui_enhancements()
        self.test_proxy_management()
        self.run_performance_analysis()

        # Integration tests (full mode only)
        if self.test_mode == "full":
            self.test_sportsbook_integration()

        # Generate summary
        passed_tests = sum(
            1 for test in self.results["tests"].values() if test["status"] == "passed"
        )
        partial_tests = sum(
            1 for test in self.results["tests"].values() if test["status"] == "partial"
        )
        total_tests = len(self.results["tests"])

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "partial_tests": partial_tests,
            "failed_tests": total_tests - passed_tests - partial_tests,
            "success_rate": (passed_tests + partial_tests * 0.5) / total_tests * 100,
            "overall_status": (
                "passed"
                if passed_tests == total_tests
                else "partial" if passed_tests + partial_tests > 0 else "failed"
            ),
        }

        logger.info(
            f"Test suite completed: {
                self.results['summary']['success_rate']:.1f}% success rate")
        return self.results

    def save_results(self, output_file: str | None = None) -> str:
        """Save test results to JSON file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"C:\\\\EQ12\\logs\\\\extension_test_results_{timestamp}.json"

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Test results saved to: {output_file}")
        return output_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="EQ12 Extension Development & Testing Suite")
    parser.add_argument(
        "--extension-path",
        "-p",
        default="C:\\\\EQ12\\firefox_extensions\\\\eq12_betting_dashboard",
        help="Path to extension directory",
    )
    parser.add_argument(
        "--test-mode",
        "-m",
        choices=["quick", "full"],
        default="quick",
        help="Test mode: quick (structure only) or full (includes integration)",
    )
    parser.add_argument("--output", "-o", help="Output file for test results")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate extension path
    if not Path(args.extension_path).exists():
        logger.error(f"Extension path not found: {args.extension_path}")
        sys.exit(1)

    # Run tests
    tester = EQ12ExtensionTester(args.extension_path, args.test_mode)
    results = tester.run_all_tests()

    # Save results
    output_file = tester.save_results(args.output)

    # Print summary
    summary = results["summary"]
    print(f"\n{'=' * 60}")
    print("EQ12 Extension Test Results")
    print(f"{'=' * 60}")
    print(f"Tests Run: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']}")
    print(f"Partial: {summary['partial_tests']}")
    print(f"Failed: {summary['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status'].upper()}")
    print(f"\nDetailed results: {output_file}")
    print(f"{'=' * 60}")

    # Exit with appropriate code
    if summary["overall_status"] == "failed":
        sys.exit(1)
    elif summary["overall_status"] == "partial":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
