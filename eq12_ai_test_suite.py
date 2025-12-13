#!/usr/bin/env python3
"""
EQ12 AI System Comprehensive Test Suite
Validates all components of the enhanced AI integration system including
OpenAI API, prompt engineering, conversation management, and unified orchestration.

Features:
- Complete system integration testing
- Performance benchmarking and validation
- Error handling and edge case testing
- Production readiness assessment
- Deployment validation checklist

Author: EQ12 GODSTACK Team
Version: 1.0.0
License: MIT
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Test imports - handle gracefully if modules not available
try:
    from eq12_conversation_manager import ConversationManager
    from eq12_openai_enhanced_v2 import EQ12OpenAIEnhanced, TaskComplexity
    from eq12_prompt_engineering_framework import PromptTemplateManager
    from eq12_unified_ai_system import EQ12AIOrchestrator

    AI_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ AI modules not available: {e}")
    AI_MODULES_AVAILABLE = False


class EQ12AITestSuite:
    """Comprehensive test suite for EQ12 AI system"""

    def __init__(self):
        self.results = {
            "test_start": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_results": [],
            "performance_metrics": {},
            "system_info": {},
        }

        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Setup test logging"""
        log_dir = Path("C:/EQ12/logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"eq12_ai_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        return logging.getLogger(f"{__name__}.EQ12AITestSuite")

    def record_test(
        self,
        test_name: str,
        success: bool,
        details: str = "",
        metrics: dict[str, Any] | None = None,
    ):
        """Record test result"""
        self.results["tests_run"] += 1

        if success:
            self.results["tests_passed"] += 1
            status = "PASS"
            self.logger.info(f"✅ {test_name}: PASSED")
        else:
            self.results["tests_failed"] += 1
            status = "FAIL"
            self.logger.error(f"❌ {test_name}: FAILED - {details}")

        test_result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "metrics": metrics or {},
        }

        self.results["test_results"].append(test_result)

    async def test_environment_setup(self):
        """Test basic environment setup"""
        print("\n🔧 Testing Environment Setup...")

        # Test 1: Check required directories
        try:
            required_dirs = [
                "C:/EQ12",
                "C:/EQ12/logs",
                "C:/EQ12/prompts",
                "C:/EQ12/conversations",
            ]

            for dir_path in required_dirs:
                if not Path(dir_path).exists():
                    Path(dir_path).mkdir(parents=True, exist_ok=True)

            self.record_test(
                "Environment Directories",
                True,
                f"Created/verified {len(required_dirs)} directories",
            )

        except Exception as e:
            self.record_test("Environment Directories", False, str(e))

        # Test 2: Check API key availability
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and len(api_key) > 20:
                self.record_test("OpenAI API Key", True, "API key found and valid format")
            else:
                self.record_test("OpenAI API Key", False, "API key not found or invalid")

        except Exception as e:
            self.record_test("OpenAI API Key", False, str(e))

        # Test 3: Module imports
        try:
            if AI_MODULES_AVAILABLE:
                self.record_test("Module Imports", True, "All AI modules imported successfully")
            else:
                self.record_test("Module Imports", False, "Some AI modules unavailable")

        except Exception as e:
            self.record_test("Module Imports", False, str(e))

    async def test_openai_enhanced_client(self):
        """Test enhanced OpenAI client"""
        print("\n🤖 Testing Enhanced OpenAI Client...")

        if not AI_MODULES_AVAILABLE:
            self.record_test("OpenAI Enhanced Client", False, "Modules not available")
            return

        try:
            # Initialize client
            client = EQ12OpenAIEnhanced()

            # Test 1: Client initialization
            self.record_test(
                "Client Initialization",
                True,
                f"Client initialized with {len(client.models)} models",
            )

            # Test 2: Model selection
            try:
                model = client.select_optimal_model(TaskComplexity.MODERATE)
                self.record_test("Model Selection", True, f"Selected model: {model}")
            except Exception as e:
                self.record_test("Model Selection", False, str(e))

            # Test 3: Token counting
            try:
                text = "This is a test message for token counting."
                tokens = client.count_tokens(text)
                self.record_test("Token Counting", tokens > 0, f"Counted {tokens} tokens")
            except Exception as e:
                self.record_test("Token Counting", False, str(e))

            # Test 4: Cost estimation
            try:
                cost = client.estimate_cost(100, 50, "gpt-4o")
                self.record_test("Cost Estimation", cost > 0, f"Estimated cost: ${cost:.6f}")
            except Exception as e:
                self.record_test("Cost Estimation", False, str(e))

        except Exception as e:
            self.record_test("OpenAI Enhanced Client", False, f"Client creation failed: {e}")

    async def test_prompt_templates(self):
        """Test prompt engineering framework"""
        print("\n📝 Testing Prompt Engineering Framework...")

        if not AI_MODULES_AVAILABLE:
            self.record_test("Prompt Templates", False, "Modules not available")
            return

        try:
            manager = PromptTemplateManager()

            # Test 1: Template loading
            templates = manager.list_templates()
            self.record_test(
                "Template Loading",
                len(templates) > 0,
                f"Loaded {len(templates)} templates",
            )

            # Test 2: Sports betting template
            try:
                messages = manager.generate_conversation(
                    "sports_betting_expert",
                    game_info="Test Game",
                    bet_type="Moneyline",
                    odds="-150",
                    estimated_probability="60.0",
                    bankroll="1000.00",
                )
                self.record_test(
                    "Sports Betting Template",
                    len(messages) == 2,
                    f"Generated {len(messages)} messages",
                )
            except Exception as e:
                self.record_test("Sports Betting Template", False, str(e))

            # Test 3: Code review template
            try:
                messages = manager.generate_conversation(
                    "code_review_expert",
                    language="Python",
                    code="def test(): pass",
                    file_path="test.py",
                )
                self.record_test(
                    "Code Review Template",
                    len(messages) >= 2,
                    f"Generated {len(messages)} messages",
                )
            except Exception as e:
                self.record_test("Code Review Template", False, str(e))

        except Exception as e:
            self.record_test("Prompt Templates", False, f"Framework initialization failed: {e}")

    async def test_conversation_manager(self):
        """Test conversation management system"""
        print("\n💬 Testing Conversation Management...")

        if not AI_MODULES_AVAILABLE:
            self.record_test("Conversation Manager", False, "Modules not available")
            return

        try:
            from eq12_conversation_manager import (
                ConversationManager,
                ConversationRole,
                MessageType,
            )

            manager = ConversationManager()

            # Test 1: Conversation creation
            conv_id = manager.create_conversation(title="Test Conversation")
            self.record_test(
                "Conversation Creation",
                conv_id is not None,
                f"Created conversation: {conv_id}",
            )

            # Test 2: Message adding
            message = manager.add_message(
                conv_id,
                ConversationRole.USER,
                "Test message for conversation",
                MessageType.QUERY,
            )
            self.record_test(
                "Message Adding",
                message.message_id is not None,
                f"Added message: {message.message_id}",
            )

            # Test 3: Memory system
            manager.add_memory(conv_id, "test_key", "test_value", "testing")
            self.record_test("Memory System", True, "Added memory item successfully")

            # Test 4: Message retrieval
            messages = manager.get_conversation_messages(conv_id)
            self.record_test(
                "Message Retrieval",
                len(messages) > 0,
                f"Retrieved {len(messages)} messages",
            )

            # Test 5: Metrics
            metrics = manager.get_metrics()
            self.record_test(
                "Metrics Collection",
                isinstance(metrics, dict),
                f"Collected {len(metrics)} metrics",
            )

        except Exception as e:
            self.record_test("Conversation Manager", False, f"Manager testing failed: {e}")

    async def test_unified_ai_system(self):
        """Test unified AI orchestrator"""
        print("\n🚀 Testing Unified AI System...")

        if not AI_MODULES_AVAILABLE:
            self.record_test("Unified AI System", False, "Modules not available")
            return

        try:
            # Initialize orchestrator with low budget for testing
            ai = EQ12AIOrchestrator(budget_limit=5.0, enable_memory=False)

            # Test 1: System initialization
            self.record_test("AI Orchestrator Init", True, "Orchestrator initialized successfully")

            # Test 2: System status
            try:
                status = ai.get_system_status()
                self.record_test(
                    "System Status",
                    isinstance(status, dict),
                    f"Status contains {len(status)} sections",
                )
            except Exception as e:
                self.record_test("System Status", False, str(e))

            # Test 3: Connectivity test (if API key available)
            try:
                connectivity = await ai.test_system_connectivity()
                working_components = sum(1 for comp in connectivity.values() if "error" not in comp)
                total_components = len(connectivity)

                self.record_test(
                    "System Connectivity",
                    working_components > 0,
                    f"{working_components}/{total_components} components working",
                )
            except Exception as e:
                self.record_test("System Connectivity", False, str(e))

            # Test 4: Budget management
            try:
                budget_ok = ai._check_budget(1.0)  # Check $1 request
                self.record_test(
                    "Budget Management",
                    budget_ok,
                    f"Budget check: {'OK' if budget_ok else 'Exceeded'}",
                )
            except Exception as e:
                self.record_test("Budget Management", False, str(e))

            await ai.shutdown()

        except Exception as e:
            self.record_test("Unified AI System", False, f"System testing failed: {e}")

    async def test_performance_benchmarks(self):
        """Test system performance characteristics"""
        print("\n📊 Running Performance Benchmarks...")

        if not AI_MODULES_AVAILABLE:
            self.record_test("Performance Benchmarks", False, "Modules not available")
            return

        try:
            # Benchmark 1: Template generation speed
            start_time = time.time()
            manager = PromptTemplateManager()

            for i in range(10):
                manager.generate_conversation(
                    "sports_betting_expert",
                    game_info=f"Game {i}",
                    bet_type="Moneyline",
                    odds="-150",
                    estimated_probability="60.0",
                    bankroll="1000.00",
                )

            template_time = time.time() - start_time
            templates_per_sec = 10 / template_time

            self.record_test(
                "Template Generation Speed",
                templates_per_sec > 5,
                f"{templates_per_sec:.1f} templates/sec",
                {"templates_per_second": templates_per_sec},
            )

            # Benchmark 2: Conversation operations
            start_time = time.time()
            conv_manager = ConversationManager()

            conv_id = conv_manager.create_conversation()
            for i in range(50):
                from eq12_conversation_manager import ConversationRole, MessageType

                conv_manager.add_message(
                    conv_id,
                    ConversationRole.USER,
                    f"Test message {i}",
                    MessageType.QUERY,
                )

            conversation_time = time.time() - start_time
            messages_per_sec = 50 / conversation_time

            self.record_test(
                "Conversation Speed",
                messages_per_sec > 10,
                f"{messages_per_sec:.1f} messages/sec",
                {"messages_per_second": messages_per_sec},
            )

            # Record performance metrics
            self.results["performance_metrics"] = {
                "template_generation_speed": templates_per_sec,
                "message_processing_speed": messages_per_sec,
                "test_completion_time": time.time(),
            }

        except Exception as e:
            self.record_test("Performance Benchmarks", False, f"Benchmark testing failed: {e}")

    async def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n⚠️ Testing Error Handling...")

        if not AI_MODULES_AVAILABLE:
            self.record_test("Error Handling", False, "Modules not available")
            return

        try:
            # Test 1: Invalid template parameters
            try:
                manager = PromptTemplateManager()
                manager.generate_conversation(
                    "sports_betting_expert",
                    game_info="Test",
                    # Missing required parameters
                )
                self.record_test("Invalid Template Params", False, "Should have raised error")
            except Exception:
                self.record_test(
                    "Invalid Template Params",
                    True,
                    "Correctly handled invalid parameters",
                )

            # Test 2: Budget exceeded simulation
            try:
                ai = EQ12AIOrchestrator(budget_limit=0.01)  # Very low budget
                within_budget = ai._check_budget(1.0)  # Request $1
                self.record_test(
                    "Budget Exceeded Handling",
                    not within_budget,
                    "Correctly rejected over-budget request",
                )
            except Exception as e:
                self.record_test("Budget Exceeded Handling", False, str(e))

            # Test 3: Non-existent conversation
            try:
                conv_manager = ConversationManager()
                conv_manager._load_conversation_from_db("nonexistent_id")
                self.record_test("Invalid Conversation ID", False, "Should have raised error")
            except Exception:
                self.record_test(
                    "Invalid Conversation ID",
                    True,
                    "Correctly handled invalid conversation ID",
                )

        except Exception as e:
            self.record_test("Error Handling", False, f"Error handling tests failed: {e}")

    def generate_deployment_report(self) -> dict[str, Any]:
        """Generate comprehensive deployment readiness report"""
        total_tests = self.results["tests_run"]
        passed_tests = self.results["tests_passed"]
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        # Categorize test results
        critical_tests = [
            "Environment Directories",
            "Module Imports",
            "Client Initialization",
            "Template Loading",
            "Conversation Creation",
            "AI Orchestrator Init",
        ]

        critical_passed = sum(
            1
            for test in self.results["test_results"]
            if test["test_name"] in critical_tests and test["status"] == "PASS"
        )

        deployment_status = (
            "READY"
            if success_rate >= 80 and critical_passed == len(critical_tests)
            else "NOT READY"
        )

        report = {
            "deployment_status": deployment_status,
            "overall_success_rate": success_rate,
            "critical_tests_passed": f"{critical_passed}/{len(critical_tests)}",
            "test_summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": self.results["tests_failed"],
            },
            "performance_metrics": self.results.get("performance_metrics", {}),
            "failed_tests": [
                test["test_name"]
                for test in self.results["test_results"]
                if test["status"] == "FAIL"
            ],
            "recommendations": [],
        }

        # Add recommendations based on failures
        if success_rate < 80:
            report["recommendations"].append("Fix failing tests before deployment")
        if critical_passed < len(critical_tests):
            report["recommendations"].append("Address critical system component failures")
        if not os.getenv("OPENAI_API_KEY"):
            report["recommendations"].append("Configure OpenAI API key for production")

        if deployment_status == "READY":
            report["recommendations"].append("System ready for production deployment")

        return report

    def save_results(self):
        """Save test results to file"""
        results_file = (
            Path("C:/EQ12/logs")
            / f"ai_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        # Add completion info
        self.results["test_end"] = datetime.now().isoformat()
        self.results["deployment_report"] = self.generate_deployment_report()

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Test results saved to: {results_file}")
        return results_file

    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 EQ12 AI System Comprehensive Test Suite")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run all test categories
        await self.test_environment_setup()
        await self.test_openai_enhanced_client()
        await self.test_prompt_templates()
        await self.test_conversation_manager()
        await self.test_unified_ai_system()
        await self.test_performance_benchmarks()
        await self.test_error_handling()

        # Generate report
        print("\n📋 DEPLOYMENT READINESS REPORT")
        print("=" * 40)

        report = self.generate_deployment_report()

        print(f"🎯 Status: {report['deployment_status']}")
        print(f"📊 Success Rate: {report['overall_success_rate']:.1f}%")
        print(
            f"✅ Tests Passed: {report['test_summary']['passed']}/{report['test_summary']['total']}"
        )
        print(f"🔧 Critical Tests: {report['critical_tests_passed']}")

        if report["failed_tests"]:
            print("\n❌ Failed Tests:")
            for test in report["failed_tests"]:
                print(f"   • {test}")

        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"   • {rec}")

        if report.get("performance_metrics"):
            print("\n⚡ Performance Metrics:")
            for metric, value in report["performance_metrics"].items():
                print(f"   • {metric}: {value}")

        # Save results
        self.save_results()

        print(f"\n🏁 Test suite completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return report


async def main():
    """Main test execution"""
    test_suite = EQ12AITestSuite()

    try:
        report = await test_suite.run_all_tests()

        # Exit with appropriate code
        if report["deployment_status"] == "READY":
            print("\n🚀 System is READY for production deployment!")
            sys.exit(0)
        else:
            print("\n⚠️ System requires fixes before deployment.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️ Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
