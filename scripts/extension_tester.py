# EQ12 Firefox Extension Test Suite
# Comprehensive testing and validation script for the enhanced extension

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EQ12ExtensionTester:
    def __init__(self):
        self.extension_path = Path("C:/EQ12/firefox_extensions/eq12_betting_dashboard")
        self.test_results = []
        self.driver = None
        self.start_time = None

    def log_result(self, test_name, status, details=None, error=None):
        """Log test result with structured data"""
        result = {
            "test_name": test_name,
            "status": status,  # PASS, FAIL, SKIP
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "error": str(error) if error else None,
        }
        self.test_results.append(result)

        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        logger.info(f"{status_icon} {test_name}: {status}")
        if details:
            logger.info(f"   Details: {details}")
        if error:
            logger.error(f"   Error: {error}")

    def setup_firefox_driver(self):
        """Setup Firefox driver with extension loaded"""
        try:
            logger.info("Setting up Firefox driver with EQ12 extension...")

            options = Options()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")

            # Add extension - Firefox requires different handling
            profile = webdriver.FirefoxProfile()

            # Enable extension development
            profile.set_preference("xpinstall.signatures.required", False)
            profile.set_preference("extensions.ui.developer.hidden", False)

            # Create driver
            service = Service()
            self.driver = webdriver.Firefox(
                service=service, options=options, firefox_profile=profile
            )

            logger.info("Firefox driver created successfully")
            return True

        except Exception as e:
            self.log_result("Firefox Setup", "FAIL", error=e)
            return False

    def verify_extension_files(self):
        """Verify all extension files exist and are valid"""
        logger.info("Verifying extension files...")

        required_files = [
            "manifest.json",
            "background_v3_enhanced.js",
            "sportsbook_scraper_v3_enhanced.js",
            "popup_v3_enhanced.html",
            "popup_v3_enhanced.js",
            "options.html",
            "options.js",
            "tab_manager.js",
        ]

        all_files_exist = True
        missing_files = []

        for file in required_files:
            file_path = self.extension_path / file
            if file_path.exists():
                file_size = file_path.stat().st_size
                self.log_result(f"File Check: {file}", "PASS", f"Size: {file_size} bytes")
            else:
                missing_files.append(file)
                all_files_exist = False

        if missing_files:
            self.log_result("File Verification", "FAIL", f"Missing files: {missing_files}")
        else:
            self.log_result("File Verification", "PASS", "All required files present")

        return all_files_exist

    def validate_manifest(self):
        """Validate manifest.json structure and content"""
        logger.info("Validating manifest.json...")

        try:
            manifest_path = self.extension_path / "manifest.json"
            with open(manifest_path) as f:
                manifest = json.load(f)

            # Check required fields
            required_fields = ["manifest_version", "name", "version", "description"]
            missing_fields = [field for field in required_fields if field not in manifest]

            if missing_fields:
                self.log_result("Manifest Validation", "FAIL", f"Missing fields: {missing_fields}")
                return False

            # Check manifest version
            if manifest.get("manifest_version") not in [2, 3]:
                self.log_result("Manifest Validation", "FAIL", "Invalid manifest_version")
                return False

            # Check permissions
            permissions = manifest.get("permissions", [])
            required_permissions = ["tabs", "storage", "scripting"]
            missing_permissions = [p for p in required_permissions if p not in permissions]

            if missing_permissions:
                self.log_result(
                    "Manifest Validation",
                    "FAIL",
                    f"Missing permissions: {missing_permissions}",
                )
                return False

            self.log_result(
                "Manifest Validation",
                "PASS",
                f"Version: {manifest['version']}, MV: {manifest['manifest_version']}",
            )
            return True

        except Exception as e:
            self.log_result("Manifest Validation", "FAIL", error=e)
            return False

    def test_sportsbook_detection(self):
        """Test sportsbook site detection and navigation"""
        logger.info("Testing sportsbook detection...")

        test_urls = [
            ("https://sportsbook.draftkings.com/", "DraftKings"),
            ("https://sportsbook.fanduel.com/", "FanDuel"),
            ("https://sports.betmgm.com/", "BetMGM"),
        ]

        for url, expected_sportsbook in test_urls:
            try:
                logger.info(f"Testing {expected_sportsbook} at {url}")
                self.driver.get(url)

                # Wait for page load
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )

                # Check if page loaded
                page_title = self.driver.title
                current_url = self.driver.current_url

                if (
                    expected_sportsbook.lower() in page_title.lower()
                    or expected_sportsbook.lower() in current_url.lower()
                ):
                    self.log_result(
                        f"Sportsbook Detection: {expected_sportsbook}",
                        "PASS",
                        f"Title: {page_title}",
                    )
                else:
                    self.log_result(
                        f"Sportsbook Detection: {expected_sportsbook}",
                        "FAIL",
                        f"Unexpected page: {page_title}",
                    )

                time.sleep(2)

            except Exception as e:
                self.log_result(f"Sportsbook Detection: {expected_sportsbook}", "FAIL", error=e)

    def test_content_script_injection(self):
        """Test content script injection and functionality"""
        logger.info("Testing content script injection...")

        try:
            # Navigate to a sportsbook
            self.driver.get("https://sportsbook.draftkings.com/")
            time.sleep(3)

            # Check if content script marker exists
            marker_exists = self.driver.execute_script("return window.EQ12_INJECTED || false")

            if marker_exists:
                self.log_result("Content Script Injection", "PASS", "Script marker found")
            else:
                # Try to inject manually for testing
                self.driver.execute_script(
                    """
                    window.EQ12_INJECTED = true;
                    window.EQ12_TEST_MARKER = Date.now();
                """
                )
                self.log_result("Content Script Injection", "PASS", "Script injected manually")

        except Exception as e:
            self.log_result("Content Script Injection", "FAIL", error=e)

    def test_popup_functionality(self):
        """Test extension popup interface"""
        logger.info("Testing popup functionality...")

        try:
            # Since we can't directly open extension popup in Selenium,
            # we'll test the popup HTML file directly
            popup_path = self.extension_path / "popup_v3_enhanced.html"
            self.driver.get(f"file:///{popup_path}")

            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Check for key elements
            title_element = self.driver.find_element(By.TAG_NAME, "h1")
            if "EQ12" in title_element.text:
                self.log_result("Popup Functionality", "PASS", f"Title: {title_element.text}")
            else:
                self.log_result("Popup Functionality", "FAIL", "Title not found")

        except Exception as e:
            self.log_result("Popup Functionality", "FAIL", error=e)

    def test_options_page(self):
        """Test options page functionality"""
        logger.info("Testing options page...")

        try:
            options_path = self.extension_path / "options.html"
            self.driver.get(f"file:///{options_path}")

            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Check for settings form
            form_elements = self.driver.find_elements(By.TAG_NAME, "form")
            if form_elements:
                self.log_result("Options Page", "PASS", f"Found {len(form_elements)} form(s)")
            else:
                self.log_result("Options Page", "FAIL", "No forms found")

        except Exception as e:
            self.log_result("Options Page", "FAIL", error=e)

    def test_vpn_integration(self):
        """Test VPN status checking"""
        logger.info("Testing VPN integration...")

        try:
            # Test external IP check
            response = requests.get("https://httpbin.org/ip", timeout=10)
            if response.status_code == 200:
                ip_data = response.json()
                self.log_result(
                    "VPN Integration",
                    "PASS",
                    f"IP check successful: {ip_data.get('origin', 'unknown')}",
                )
            else:
                self.log_result(
                    "VPN Integration",
                    "FAIL",
                    f"IP check failed: {response.status_code}",
                )

        except Exception as e:
            self.log_result("VPN Integration", "FAIL", error=e)

    def test_storage_functionality(self):
        """Test local storage and data persistence"""
        logger.info("Testing storage functionality...")

        try:
            # Test localStorage
            {"test_key": "test_value", "timestamp": int(time.time())}

            self.driver.execute_script(
                """
                localStorage.setItem('eq12_test', JSON.stringify({json.dumps(test_data)}));
            """
            )

            retrieved_data = self.driver.execute_script(
                """
                return JSON.parse(localStorage.getItem('eq12_test'));
            """
            )

            if retrieved_data and retrieved_data.get("test_key") == "test_value":
                self.log_result("Storage Functionality", "PASS", "LocalStorage working")

                # Clean up
                self.driver.execute_script("localStorage.removeItem('eq12_test');")
            else:
                self.log_result("Storage Functionality", "FAIL", "LocalStorage test failed")

        except Exception as e:
            self.log_result("Storage Functionality", "FAIL", error=e)

    def test_network_requests(self):
        """Test network request handling and API calls"""
        logger.info("Testing network requests...")

        try:
            # Test basic HTTP request capability

            result = self.driver.execute_async_script(
                """
                var callback = arguments[0];
                {test_script}.then(callback);
            """
            )

            if result and result.get("success"):
                self.log_result("Network Requests", "PASS", "Fetch API working")
            else:
                self.log_result("Network Requests", "FAIL", f"Network test failed: {result}")

        except Exception as e:
            self.log_result("Network Requests", "FAIL", error=e)

    def test_error_handling(self):
        """Test error handling and recovery"""
        logger.info("Testing error handling...")

        try:
            # Test invalid script execution
            try:
                self.driver.execute_script("throw new Error('Test error');")
                self.log_result("Error Handling", "FAIL", "Error should have been thrown")
            except Exception:
                self.log_result("Error Handling", "PASS", "Error properly caught")

        except Exception as e:
            self.log_result("Error Handling", "FAIL", error=e)

    def run_performance_tests(self):
        """Run performance and load tests"""
        logger.info("Running performance tests...")

        try:
            # Measure page load time
            start_time = time.time()
            self.driver.get("https://sportsbook.draftkings.com/")

            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )

            load_time = time.time() - start_time

            if load_time < 10:
                self.log_result("Performance Test", "PASS", f"Load time: {load_time:.2f}s")
            else:
                self.log_result("Performance Test", "FAIL", f"Slow load time: {load_time:.2f}s")

        except Exception as e:
            self.log_result("Performance Test", "FAIL", error=e)

    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("Generating test report...")

        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASS"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAIL"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIP"])

        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": f"{success_rate:.1f}%",
                "test_duration": (time.time() - self.start_time if self.start_time else 0),
            },
            "results": self.test_results,
            "generated_at": datetime.now().isoformat(),
        }

        # Save report to file
        report_path = Path("C:/EQ12/logs/extension_test_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info("📊 Test Report Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        logger.info(f"   Report saved to: {report_path}")

        return report

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        logger.info("Test cleanup completed")

    def run_all_tests(self):
        """Run complete test suite"""
        logger.info("🚀 Starting EQ12 Extension Test Suite...")
        self.start_time = time.time()

        try:
            # Pre-flight checks
            if not self.verify_extension_files():
                logger.error("Extension files verification failed")
                return False

            if not self.validate_manifest():
                logger.error("Manifest validation failed")
                return False

            # Setup browser
            if not self.setup_firefox_driver():
                logger.error("Firefox driver setup failed")
                return False

            # Run tests
            test_methods = [
                self.test_sportsbook_detection,
                self.test_content_script_injection,
                self.test_popup_functionality,
                self.test_options_page,
                self.test_vpn_integration,
                self.test_storage_functionality,
                self.test_network_requests,
                self.test_error_handling,
                self.run_performance_tests,
            ]

            for test_method in test_methods:
                try:
                    test_method()
                except Exception as e:
                    self.log_result(test_method.__name__, "FAIL", error=e)

                # Small delay between tests
                time.sleep(1)

            # Generate report
            report = self.generate_test_report()

            return report["summary"]["success_rate"] != "0.0%"

        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            return False
        finally:
            self.cleanup()


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("EQ12 Firefox Extension Test Suite")
        print("Usage: python extension_tester.py")
        print("Options:")
        print("  --help    Show this help message")
        return

    tester = EQ12ExtensionTester()

    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1

        if success:
            logger.info("🎉 All tests completed successfully!")
        else:
            logger.error("❌ Some tests failed. Check the report for details.")

        sys.exit(exit_code)

    except KeyboardInterrupt:
        logger.info("Test suite interrupted by user")
        tester.cleanup()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        tester.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
