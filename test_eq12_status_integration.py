#!/usr/bin/env python3
"""
EQ12 OpenAI Status Monitor Integration Test
Tests the status monitoring integration with optimization workflows
"""

import asyncio
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

# Add EQ12 modules to path
sys.path.append(os.path.dirname(__file__))

try:
    from eq12_openai_status_monitor import (
        EQ12OpenAIStatusMonitor,
        ServiceStatus,
        StatusIncident,
    )
    from eq12_optimization_orchestrator import EQ12OptimizationOrchestrator
except ImportError as e:
    print(f"Failed to import EQ12 modules: {e}")
    sys.exit(1)


class TestEQ12OpenAIStatusMonitor(unittest.TestCase):
    """Test suite for OpenAI status monitoring"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_status.db")
        self.monitor = EQ12OpenAIStatusMonitor(db_path=self.test_db_path)

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_database_initialization(self):
        """Test database initialization"""
        self.assertTrue(os.path.exists(self.test_db_path))

    @patch("requests.get")
    async def test_fetch_status_feed_success(self, mock_get):
        """Test successful RSS feed fetch"""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
        <rss>
            <channel>
                <item>
                    <title>API - Investigating</title>
                    <description>We are investigating issues with the API</description>
                    <pubDate>Thu, 27 Sep 2025 12:00:00 GMT</pubDate>
                    <link>https://status.openai.com/incidents/123</link>
                </item>
            </channel>
        </rss>"""
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = await self.monitor.fetch_status_feed("rss")
        self.assertIsNotNone(result)
        self.assertIn("API - Investigating", result)

    def test_rss_parsing(self):
        """Test RSS feed parsing"""
        rss_content = """<?xml version="1.0" encoding="UTF-8"?>
        <rss>
            <channel>
                <item>
                    <title>API - Major Outage</title>
                    <description>We are experiencing a major outage with the API service</description>
                    <pubDate>Thu, 27 Sep 2025 12:00:00 GMT</pubDate>
                    <link>https://status.openai.com/incidents/123</link>
                </item>
            </channel>
        </rss>"""

        incidents = self.monitor.parse_rss_feed(rss_content)
        self.assertEqual(len(incidents), 1)
        self.assertEqual(incidents[0].title, "API - Major Outage")
        self.assertEqual(incidents[0].impact, "major")
        self.assertIn("API", incidents[0].affected_services)

    def test_service_extraction(self):
        """Test affected service extraction"""
        text = "We are experiencing issues with the OpenAI API and fine-tuning service"
        affected = self.monitor._extract_affected_services(text)
        self.assertIn("API", affected)
        self.assertIn("Fine-tuning", affected)

    async def test_model_availability_check(self):
        """Test model availability checking"""
        # Mock service status with API issues
        with patch.object(self.monitor, "get_current_status") as mock_status:
            mock_status.return_value = {
                "API": ServiceStatus(
                    service_name="API",
                    status="partial_outage",
                    description="API experiencing issues",
                    last_updated=datetime.utcnow().isoformat(),
                    impact_level="major",
                    affected_models=["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14"],
                )
            }

            result = await self.monitor.check_model_availability("gpt-4.1-2025-04-14")
            self.assertFalse(result["available"])
            self.assertEqual(result["status"], "partial_outage")
            self.assertIn("API", result["affected_services"])

    def test_eq12_recommendations(self):
        """Test EQ12-specific recommendations generation"""
        statuses = {
            "API": ServiceStatus(
                service_name="API",
                status="major_outage",
                description="API completely unavailable",
                last_updated=datetime.utcnow().isoformat(),
                impact_level="critical",
                affected_models=["gpt-4.1-2025-04-14"],
            ),
            "Fine-tuning": ServiceStatus(
                service_name="Fine-tuning",
                status="operational",
                description="No issues",
                last_updated=datetime.utcnow().isoformat(),
                impact_level="none",
            ),
        }

        recommendations = self.monitor.generate_eq12_recommendations(statuses)

        # Should recommend pausing workflows due to API outage
        api_recs = [r for r in recommendations if r["service"] == "API"]
        self.assertTrue(len(api_recs) > 0)

        critical_recs = [r for r in recommendations if r["priority"] == "critical"]
        self.assertTrue(len(critical_recs) > 0)


class TestStatusIntegrationWithOptimization(unittest.TestCase):
    """Test integration between status monitoring and optimization"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        # Mock the optimizers to avoid actual API calls
        with (
            patch("eq12_optimization_orchestrator.EQ12AdvancedOptimizer"),
            patch("eq12_optimization_orchestrator.EQ12OpenAIOptimizer"),
            patch("eq12_optimization_orchestrator.EQ12OpenAIStatusMonitor") as mock_monitor,
        ):
            self.orchestrator = EQ12OptimizationOrchestrator()
            self.mock_status_monitor = mock_monitor.return_value

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    async def test_evaluation_with_api_outage(self):
        """Test evaluation behavior when API is down"""

        # Mock API outage status
        outage_status = {
            "API": ServiceStatus(
                service_name="API",
                status="major_outage",
                description="Complete API failure",
                last_updated=datetime.utcnow().isoformat(),
                impact_level="critical",
            )
        }

        self.mock_status_monitor.get_current_status.return_value = outage_status

        # Run evaluation - should be postponed
        result = await self.orchestrator.run_comprehensive_evaluation("betting_analysis")

        self.assertEqual(result["status"], "postponed")
        self.assertIn("OpenAI API unavailable", result["reason"])
        self.assertIn("service_status", result)

    async def test_evaluation_with_degraded_performance(self):
        """Test evaluation behavior with degraded API performance"""

        # Mock degraded performance
        degraded_status = {
            "API": ServiceStatus(
                service_name="API",
                status="degraded_performance",
                description="API slow response times",
                last_updated=datetime.utcnow().isoformat(),
                impact_level="minor",
            )
        }

        self.mock_status_monitor.get_current_status.return_value = degraded_status

        # Mock successful evaluation completion
        with (
            patch.object(self.orchestrator, "_generate_eval_examples") as mock_examples,
            patch.object(
                self.orchestrator.advanced_optimizer, "create_eval_dataset"
            ) as mock_dataset,
            patch.object(self.orchestrator.advanced_optimizer, "engineer_prompt") as mock_prompt,
            patch.object(self.orchestrator.advanced_optimizer, "run_eval") as mock_eval,
        ):
            mock_examples.return_value = [{"input": "test", "expected_output": "test"}]
            mock_dataset.return_value = []
            mock_prompt.return_value = "test prompt"
            mock_eval.return_value = []

            # Should proceed with evaluation despite degraded performance
            result = await self.orchestrator.run_comprehensive_evaluation("betting_analysis")

            # Should not be postponed
            self.assertNotEqual(result.get("status"), "postponed")


class StatusMonitoringIntegrationSuite:
    """Integration test suite for status monitoring"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.results = []

    def cleanup(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    async def test_end_to_end_monitoring(self):
        """Test complete monitoring workflow"""

        print("Testing end-to-end status monitoring...")

        try:
            # Create status monitor
            monitor = EQ12OpenAIStatusMonitor(db_path=os.path.join(self.temp_dir, "test_status.db"))

            # Mock RSS feed response
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
                <rss>
                    <channel>
                        <item>
                            <title>All systems operational</title>
                            <description>No current issues</description>
                            <pubDate>Thu, 27 Sep 2025 12:00:00 GMT</pubDate>
                        </item>
                    </channel>
                </rss>"""
                mock_response.raise_for_status.return_value = None
                mock_get.return_value = mock_response

                # Test status fetching
                statuses = await monitor.get_current_status()
                self.results.append(
                    {
                        "test": "status_fetching",
                        "status": "PASS" if statuses else "FAIL",
                        "message": f"Retrieved status for {len(statuses)} services",
                    }
                )

                # Test recommendations generation
                recommendations = monitor.generate_eq12_recommendations(statuses)
                self.results.append(
                    {
                        "test": "recommendations_generation",
                        "status": "PASS",
                        "message": f"Generated {len(recommendations)} recommendations",
                    }
                )

                # Test status summary
                summary = monitor.get_status_summary()
                self.results.append(
                    {
                        "test": "status_summary",
                        "status": "PASS" if "overall_health" in summary else "FAIL",
                        "message": f"Health score: {summary.get('overall_health', 'N/A')}%",
                    }
                )

        except Exception as e:
            self.results.append(
                {
                    "test": "end_to_end_monitoring",
                    "status": "FAIL",
                    "message": f"Integration test failed: {e}",
                }
            )

    async def test_optimization_integration(self):
        """Test integration with optimization workflows"""

        print("Testing optimization integration...")

        try:
            # This would require mocking the optimization components
            # For now, just test that the integration points exist

            with (
                patch("eq12_optimization_orchestrator.EQ12AdvancedOptimizer"),
                patch("eq12_optimization_orchestrator.EQ12OpenAIOptimizer"),
                patch("eq12_optimization_orchestrator.EQ12OpenAIStatusMonitor"),
            ):
                orchestrator = EQ12OptimizationOrchestrator()

                # Verify status monitor is initialized
                has_status_monitor = hasattr(orchestrator, "status_monitor")

                self.results.append(
                    {
                        "test": "optimization_integration",
                        "status": "PASS" if has_status_monitor else "FAIL",
                        "message": "Status monitor integration verified",
                    }
                )

        except Exception as e:
            self.results.append(
                {
                    "test": "optimization_integration",
                    "status": "FAIL",
                    "message": f"Integration test failed: {e}",
                }
            )

    async def run_all_tests(self):
        """Run all integration tests"""

        print("=== EQ12 OpenAI Status Monitor Integration Tests ===")

        await self.test_end_to_end_monitoring()
        await self.test_optimization_integration()

        # Generate summary
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])

        print("\n=== Integration Test Results ===")
        print(f"Total tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        print("\nDetailed Results:")
        for result in self.results:
            status_symbol = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_symbol} {result['test']}: {result['message']}")

        return failed == 0


async def main():
    """Main test runner"""

    # Run unit tests
    print("Running unit tests...")

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEQ12OpenAIStatusMonitor))
    suite.addTest(unittest.makeSuite(TestStatusIntegrationWithOptimization))

    runner = unittest.TextTestRunner(verbosity=2)
    unit_test_result = runner.run(suite)

    print("\n=== Unit Test Results ===")
    print(f"Tests run: {unit_test_result.testsRun}")
    print(f"Failures: {len(unit_test_result.failures)}")
    print(f"Errors: {len(unit_test_result.errors)}")

    # Run integration tests
    print("\n" + "=" * 50)
    integration_suite = StatusMonitoringIntegrationSuite()

    try:
        integration_success = await integration_suite.run_all_tests()

        # Overall summary
        print("\n" + "=" * 50)
        print("=== OVERALL TEST SUMMARY ===")

        unit_success = len(unit_test_result.failures) == 0 and len(unit_test_result.errors) == 0

        print(f"Unit Tests: {'PASS' if unit_success else 'FAIL'}")
        print(f"Integration Tests: {'PASS' if integration_success else 'FAIL'}")

        overall_success = unit_success and integration_success
        print(
            f"Overall Status: {'ALL TESTS PASSED ✅' if overall_success else 'SOME TESTS FAILED ❌'}"
        )

        return 0 if overall_success else 1

    finally:
        integration_suite.cleanup()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
