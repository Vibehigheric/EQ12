#!/usr/bin/env python3
"""
EQ12 Model Optimization Integration Test Suite
Comprehensive testing for the advanced optimization system
"""

import asyncio
import os
import shutil
import sqlite3
import sys
import tempfile

# Test framework imports
import unittest
from unittest.mock import Mock, patch

# Add EQ12 modules to path
sys.path.append(os.path.dirname(__file__))

try:
    from eq12_advanced_optimizer import (
        EQ12AdvancedOptimizer,
        EvalType,
        OptimizationMethod,
    )
    from eq12_optimization_orchestrator import EQ12OptimizationOrchestrator

    # Try to import legacy optimizer - may not exist in all environments
    try:
        from eq12_openai_optimizer import AIProfile, EQ12OpenAIOptimizer

        LEGACY_OPTIMIZER_AVAILABLE = True
    except ImportError:
        print("Legacy optimizer not available - using mock implementation")
        LEGACY_OPTIMIZER_AVAILABLE = False

        # Mock implementation for testing
        class AIProfile:
            DATA_ANALYSIS = "data_analysis"
            COMPLIANCE = "compliance"
            RISK_ASSESSMENT = "risk_assessment"
            GOVERNANCE = "governance"
            CODE_GENERATION = "code_generation"

        class EQ12OpenAIOptimizer:
            def get_profile(self, profile_type):
                return Mock(to_dict=lambda: {"temperature": 0.3, "max_tokens": 1000})

except ImportError as e:
    print(f"Failed to import EQ12 modules: {e}")
    sys.exit(1)


class TestEQ12AdvancedOptimizer(unittest.TestCase):
    """Test suite for EQ12AdvancedOptimizer"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_optimization.db")

        # Initialize optimizer with test database
        self.optimizer = EQ12AdvancedOptimizer(db_path=self.test_db_path)

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_database_initialization(self):
        """Test that database is properly initialized"""
        self.assertTrue(os.path.exists(self.test_db_path))

        # Check that tables exist
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        # Check eval_results table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eval_results'")
        self.assertIsNotNone(cursor.fetchone())

        # Check optimization_jobs table
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='optimization_jobs'"
        )
        self.assertIsNotNone(cursor.fetchone())

        conn.close()

    def test_eval_dataset_creation(self):
        """Test evaluation dataset creation"""
        examples = [
            {"input": "Test input 1", "expected_output": "Test output 1"},
            {"input": "Test input 2", "expected_output": "Test output 2"},
        ]

        eval_types = [EvalType.ACCURACY, EvalType.RELEVANCE]

        dataset = self.optimizer.create_eval_dataset("test_use_case", examples, eval_types)

        self.assertEqual(len(dataset), len(examples) * len(eval_types))
        self.assertTrue(all(item["use_case"] == "test_use_case" for item in dataset))

    def test_prompt_engineering(self):
        """Test prompt engineering functionality"""
        base_prompt = "Analyze the following data:"
        context_data = ["Context 1", "Context 2"]
        examples = [{"input": "Sample input", "expected_output": "Sample output"}]

        engineered_prompt = self.optimizer.engineer_prompt(
            base_prompt, context_data=context_data, examples=examples
        )

        # Check that all components are included
        self.assertIn(base_prompt, engineered_prompt)
        self.assertIn("Context 1", engineered_prompt)
        self.assertIn("Context 2", engineered_prompt)
        self.assertIn("Sample input", engineered_prompt)

    def test_optimization_recommendations(self):
        """Test optimization recommendations generation"""
        metrics = {"accuracy": 0.75, "relevance": 0.80}

        recommendations = self.optimizer.get_optimization_recommendations("test_use_case", metrics)

        self.assertIsInstance(recommendations, list)
        self.assertTrue(len(recommendations) > 0)

        # Check recommendation structure
        for rec in recommendations:
            self.assertIn("method", rec)
            self.assertIn("priority", rec)
            self.assertIn("description", rec)


class TestEQ12OptimizationOrchestrator(unittest.TestCase):
    """Test suite for EQ12OptimizationOrchestrator"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()

        # Mock the optimizers if needed
        with (
            patch("eq12_optimization_orchestrator.EQ12AdvancedOptimizer"),
            patch("eq12_optimization_orchestrator.EQ12OpenAIOptimizer"),
        ):
            self.orchestrator = EQ12OptimizationOrchestrator()

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_use_case_configuration(self):
        """Test that all use cases are properly configured"""
        expected_use_cases = [
            "betting_analysis",
            "cannabis_compliance",
            "credit_assessment",
            "governance_automation",
            "code_generation",
        ]

        for use_case in expected_use_cases:
            self.assertIn(use_case, self.orchestrator.eq12_use_cases)

            config = self.orchestrator.eq12_use_cases[use_case]
            self.assertIn("description", config)
            self.assertIn("eval_types", config)
            self.assertIn("expected_accuracy", config)

    def test_eval_examples_generation(self):
        """Test evaluation examples generation"""
        for use_case in self.orchestrator.eq12_use_cases:
            examples = self.orchestrator._generate_eval_examples(use_case)

            # Should return a list (may be empty for some use cases)
            self.assertIsInstance(examples, list)

            # If examples exist, check structure
            if examples:
                for example in examples:
                    self.assertIn("input", example)
                    self.assertIn("expected_output", example)

    def test_base_prompt_generation(self):
        """Test base prompt generation"""
        for use_case in self.orchestrator.eq12_use_cases:
            prompt = self.orchestrator._get_base_prompt(use_case)
            self.assertIsInstance(prompt, str)
            self.assertTrue(len(prompt) > 0)

    def test_context_data_generation(self):
        """Test context data generation"""
        for use_case in self.orchestrator.eq12_use_cases:
            context = self.orchestrator._get_context_data(use_case)
            self.assertIsInstance(context, list)

    @patch(
        "eq12_optimization_orchestrator.EQ12OptimizationOrchestrator.run_comprehensive_evaluation"
    )
    async def test_optimize_production_system_mock(self, mock_eval):
        """Test production optimization workflow with mocked evaluation"""

        # Mock evaluation results
        mock_eval_results = {
            "use_case": "betting_analysis",
            "evaluation_results": {
                "gpt-4.1-2025-04-14": {
                    "avg_scores": {"accuracy": 0.85, "relevance": 0.90},
                    "overall_score": 0.875,
                    "eval_count": 10,
                    "meets_target": True,
                }
            },
            "recommendations": [{"method": "prompt_engineering", "priority": "medium"}],
            "target_accuracy": 0.85,
        }

        mock_eval.return_value = mock_eval_results

        # Test optimization
        result = await self.orchestrator.optimize_production_system("betting_analysis")

        self.assertIn("evaluation_summary", result)
        self.assertIn("needs_fine_tuning", result)
        self.assertIn("recommended_actions", result)
        self.assertIn("deployment_ready", result)

    def test_deployment_config_generation(self):
        """Test deployment configuration generation"""
        mock_eval_results = {
            "evaluation_results": {
                "gpt-4.1-2025-04-14": {
                    "avg_scores": {"accuracy": 0.85, "relevance": 0.90},
                    "overall_score": 0.875,
                }
            }
        }

        config = self.orchestrator._generate_deployment_config(
            "betting_analysis", mock_eval_results
        )

        self.assertIn("model", config)
        self.assertIn("parameters", config)
        self.assertIn("use_case", config)
        self.assertIn("expected_performance", config)
        self.assertIn("monitoring_thresholds", config)

    def test_optimization_report_generation(self):
        """Test optimization report generation"""
        mock_results = {
            "use_case": "betting_analysis",
            "evaluation_summary": {
                "evaluation_results": {
                    "gpt-4.1-2025-04-14": {
                        "avg_scores": {"accuracy": 0.85, "relevance": 0.90},
                        "overall_score": 0.875,
                        "meets_target": True,
                        "eval_count": 10,
                    }
                }
            },
            "needs_fine_tuning": False,
            "recommended_actions": [
                {
                    "action": "deploy_optimized_model",
                    "priority": "high",
                    "description": "Ready for deployment",
                    "estimated_improvement": "N/A",
                }
            ],
            "deployment_ready": True,
            "deployment_config": {
                "model": "gpt-4.1-2025-04-14",
                "expected_performance": {"accuracy": 0.85, "relevance": 0.90},
            },
        }

        report = self.orchestrator.generate_optimization_report(mock_results)

        self.assertIsInstance(report, str)
        self.assertIn("EQ12 Model Optimization Report", report)
        self.assertIn("betting_analysis", report)
        self.assertIn("✅ Deployment Ready", report)


class IntegrationTestSuite:
    """Integration test suite for end-to-end testing"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.results = []

    def cleanup(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    async def run_mock_evaluation_test(self):
        """Test evaluation pipeline with mocked OpenAI calls"""

        print("Running mock evaluation test...")

        with patch("openai.ChatCompletion.acreate") as mock_openai:
            # Mock OpenAI response
            mock_openai.return_value = {
                "choices": [{"message": {"content": "Test response with good accuracy"}}]
            }

            orchestrator = EQ12OptimizationOrchestrator()

            try:
                # This would normally call OpenAI - we're mocking it
                examples = orchestrator._generate_eval_examples("betting_analysis")

                self.results.append(
                    {
                        "test": "mock_evaluation",
                        "status": "PASS",
                        "message": f"Generated {len(examples)} examples for betting_analysis",
                    }
                )

            except Exception as e:
                self.results.append(
                    {
                        "test": "mock_evaluation",
                        "status": "FAIL",
                        "message": f"Mock evaluation failed: {e}",
                    }
                )

    def test_database_operations(self):
        """Test database operations"""

        print("Testing database operations...")

        try:
            test_db = os.path.join(self.temp_dir, "test.db")
            EQ12AdvancedOptimizer(db_path=test_db)

            # Test database creation
            self.results.append(
                {
                    "test": "database_creation",
                    "status": "PASS" if os.path.exists(test_db) else "FAIL",
                    "message": f"Database created at {test_db}",
                }
            )

        except Exception as e:
            self.results.append(
                {
                    "test": "database_operations",
                    "status": "FAIL",
                    "message": f"Database operations failed: {e}",
                }
            )

    def test_configuration_validation(self):
        """Test configuration validation"""

        print("Testing configuration validation...")

        try:
            orchestrator = EQ12OptimizationOrchestrator()

            # Test all use cases have required configuration
            for use_case, config in orchestrator.eq12_use_cases.items():
                required_keys = ["description", "eval_types", "expected_accuracy"]
                missing_keys = [key for key in required_keys if key not in config]

                if missing_keys:
                    raise ValueError(f"Use case {use_case} missing keys: {missing_keys}")

            self.results.append(
                {
                    "test": "configuration_validation",
                    "status": "PASS",
                    "message": f"All {len(orchestrator.eq12_use_cases)} use cases properly configured",
                }
            )

        except Exception as e:
            self.results.append(
                {
                    "test": "configuration_validation",
                    "status": "FAIL",
                    "message": f"Configuration validation failed: {e}",
                }
            )

    async def run_all_tests(self):
        """Run all integration tests"""

        print("=== EQ12 Optimization Integration Tests ===")

        # Run sync tests
        self.test_database_operations()
        self.test_configuration_validation()

        # Run async tests
        await self.run_mock_evaluation_test()

        # Generate summary
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])

        print("\n=== Test Results Summary ===")
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

    # Create test suite
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTest(unittest.makeSuite(TestEQ12AdvancedOptimizer))
    suite.addTest(unittest.makeSuite(TestEQ12OptimizationOrchestrator))

    # Run unit tests
    runner = unittest.TextTestRunner(verbosity=2)
    unit_test_result = runner.run(suite)

    print("\n=== Unit Test Results ===")
    print(f"Tests run: {unit_test_result.testsRun}")
    print(f"Failures: {len(unit_test_result.failures)}")
    print(f"Errors: {len(unit_test_result.errors)}")

    # Run integration tests
    print("\n" + "=" * 50)
    integration_suite = IntegrationTestSuite()

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
