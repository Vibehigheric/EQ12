# eq12_comprehensive_validation.py
"""
EQ12 Comprehensive System Validation and Upgrade Report
Tests all OpenAI integrations, configurations, and system health
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Set environment for testing
os.environ["EQ12_USE_LLM"] = "1"
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = (
        "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"
    )

try:
    from eq12_error_boundary import GPT5ErrorBoundary
    from eq12_llm_offline import LLMOffline
    from eq12_openai_client import ask_gpt_sync, get_openai_client
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Installing required modules...")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EQ12ValidationSuite:
    """Comprehensive validation and testing suite"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "summary": {},
            "recommendations": [],
        }

    async def run_full_validation(self):
        """Run complete validation suite"""
        print("🚀 EQ12 COMPREHENSIVE SYSTEM VALIDATION")
        print("=" * 50)

        # Test 1: Environment Configuration
        await self.test_environment()

        # Test 2: OpenAI Integration
        await self.test_openai_integration()

        # Test 3: Circuit Breaker System
        await self.test_circuit_breaker()

        # Test 4: Error Boundary System
        await self.test_error_boundary()

        # Test 5: Model Availability
        await self.test_model_availability()

        # Test 6: Configuration Files
        await self.test_configurations()

        # Test 7: File System Health
        await self.test_file_system()

        # Generate comprehensive report
        self.generate_report()

        return self.results

    async def test_environment(self):
        """Test environment configuration"""
        print("🔍 Testing Environment Configuration...")

        test_results = {}

        # Check API key
        api_key = os.getenv("OPENAI_API_KEY")
        test_results["openai_api_key"] = {
            "present": bool(api_key),
            "format_valid": api_key.startswith("sk-") if api_key else False,
            "length": len(api_key) if api_key else 0,
        }

        # Check EQ12 settings
        test_results["eq12_use_llm"] = {
            "value": os.getenv("EQ12_USE_LLM", "0"),
            "enabled": os.getenv("EQ12_USE_LLM") == "1",
        }

        # Check Python version
        test_results["python_version"] = {
            "version": sys.version,
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "compatible": sys.version_info >= (3, 8),
        }

        self.results["tests"]["environment"] = test_results

        if test_results["openai_api_key"]["present"]:
            print("  ✅ OpenAI API key configured")
        else:
            print("  ❌ OpenAI API key missing")

        if test_results["eq12_use_llm"]["enabled"]:
            print("  ✅ EQ12 LLM enabled")
        else:
            print("  ⚠️ EQ12 LLM disabled")

    async def test_openai_integration(self):
        """Test OpenAI client integration"""
        print("🤖 Testing OpenAI Integration...")

        test_results = {}

        try:
            # Test client creation
            client = get_openai_client()
            test_results["client_creation"] = {"success": True}

            # Test availability
            is_available = client.is_available()
            test_results["client_available"] = {"success": is_available}

            if is_available:
                print("  ✅ OpenAI client available")

                # Test simple completion
                try:
                    response = ask_gpt_sync(
                        "Test: Respond with just 'SUCCESS'", model="gpt-4o-mini"
                    )
                    test_results["simple_completion"] = {
                        "success": True,
                        "response": response[:100],
                    }
                    print(f"  ✅ Simple completion: {response[:50]}...")

                except Exception as e:
                    test_results["simple_completion"] = {
                        "success": False,
                        "error": str(e),
                    }
                    print(f"  ❌ Simple completion failed: {e}")
            else:
                print("  ❌ OpenAI client not available")
                test_results["simple_completion"] = {
                    "success": False,
                    "error": "Client not available",
                }

        except Exception as e:
            test_results["client_creation"] = {"success": False, "error": str(e)}
            print(f"  ❌ OpenAI client creation failed: {e}")

        self.results["tests"]["openai_integration"] = test_results

    async def test_circuit_breaker(self):
        """Test LLM circuit breaker system"""
        print("🛡️ Testing Circuit Breaker System...")

        test_results = {}

        try:
            # Test circuit breaker status
            is_offline = LLMOffline.is_offline()
            status = LLMOffline.status()

            test_results["circuit_breaker"] = {
                "offline": is_offline,
                "status": status,
                "functional": True,
            }

            if is_offline:
                print(f"  ⚠️ Circuit breaker active: {status}")
            else:
                print("  ✅ Circuit breaker ready")

        except Exception as e:
            test_results["circuit_breaker"] = {"functional": False, "error": str(e)}
            print(f"  ❌ Circuit breaker error: {e}")

        self.results["tests"]["circuit_breaker"] = test_results

    async def test_error_boundary(self):
        """Test error boundary system"""
        print("🔒 Testing Error Boundary System...")

        test_results = {}

        try:
            # Test error boundary creation
            boundary = GPT5ErrorBoundary()
            test_results["boundary_creation"] = {"success": True}

            # Test safe call
            try:
                response = await boundary.safe_call("Test prompt")
                test_results["safe_call"] = {
                    "success": True,
                    "response": response[:100],
                }
                print("  ✅ Error boundary safe call successful")

            except Exception as e:
                test_results["safe_call"] = {"success": False, "error": str(e)}
                print(f"  ❌ Safe call failed: {e}")

        except Exception as e:
            test_results["boundary_creation"] = {"success": False, "error": str(e)}
            print(f"  ❌ Error boundary creation failed: {e}")

        self.results["tests"]["error_boundary"] = test_results

    async def test_model_availability(self):
        """Test OpenAI model availability"""
        print("🎯 Testing Model Availability...")

        test_results = {}

        try:
            get_openai_client()

            # Test each model
            models_to_test = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4"]

            for model in models_to_test:
                try:
                    response = ask_gpt_sync("Say 'OK'", model=model)
                    test_results[model] = {"available": True, "response": response}
                    print(f"  ✅ {model} available")

                except Exception as e:
                    test_results[model] = {"available": False, "error": str(e)}
                    print(f"  ❌ {model} failed: {e}")

        except Exception as e:
            test_results["test_error"] = str(e)
            print(f"  ❌ Model testing failed: {e}")

        self.results["tests"]["model_availability"] = test_results

    async def test_configurations(self):
        """Test configuration files"""
        print("⚙️ Testing Configuration Files...")

        test_results = {}

        config_files = [
            "configs/ai_enhanced_config.json",
            "configs/copilot_system_config.json",
            ".env",
        ]

        for config_file in config_files:
            config_path = Path(config_file)

            test_results[config_file] = {
                "exists": config_path.exists(),
                "readable": False,
                "valid_json": False,
            }

            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        content = f.read()
                    test_results[config_file]["readable"] = True

                    if config_file.endswith(".json"):
                        try:
                            json.loads(content)
                            test_results[config_file]["valid_json"] = True
                            print(f"  ✅ {config_file} valid")
                        except json.JSONDecodeError:
                            print(f"  ❌ {config_file} invalid JSON")
                    else:
                        print(f"  ✅ {config_file} readable")

                except Exception as e:
                    print(f"  ❌ {config_file} read error: {e}")
            else:
                print(f"  ⚠️ {config_file} missing")

        self.results["tests"]["configurations"] = test_results

    async def test_file_system(self):
        """Test file system health"""
        print("📁 Testing File System Health...")

        test_results = {}

        # Check key directories
        directories = ["logs", "configs", "scripts", "dashboard"]

        for directory in directories:
            dir_path = Path(directory)
            test_results[directory] = {"exists": dir_path.exists(), "writable": False}

            if dir_path.exists():
                try:
                    test_file = dir_path / "test_write.tmp"
                    test_file.write_text("test")
                    test_file.unlink()
                    test_results[directory]["writable"] = True
                    print(f"  ✅ {directory} accessible")
                except Exception:
                    print(f"  ❌ {directory} not writable")
            else:
                print(f"  ⚠️ {directory} missing")

        self.results["tests"]["file_system"] = test_results

    def generate_report(self):
        """Generate comprehensive report"""
        print("\n📊 GENERATING COMPREHENSIVE REPORT...")

        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0

        for _test_category, tests in self.results["tests"].items():
            if isinstance(tests, dict):
                for _test_name, result in tests.items():
                    if isinstance(result, dict):
                        total_tests += 1
                        if (
                            result.get("success", False)
                            or result.get("available", False)
                            or result.get("exists", False)
                        ):
                            passed_tests += 1

        self.results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (
                round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 0
            ),
            "overall_health": (
                "EXCELLENT"
                if passed_tests / total_tests > 0.9
                else "GOOD" if passed_tests / total_tests > 0.7 else "NEEDS_ATTENTION"
            ),
        }

        # Generate recommendations
        if not self.results["tests"]["environment"]["openai_api_key"]["present"]:
            self.results["recommendations"].append("Configure OPENAI_API_KEY environment variable")

        if not self.results["tests"]["environment"]["eq12_use_llm"]["enabled"]:
            self.results["recommendations"].append("Enable EQ12_USE_LLM for full functionality")

        # Save detailed report
        report_path = Path(
            f"logs/eq12_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        # Print summary
        print("\n" + "=" * 50)
        print("🎉 EQ12 SYSTEM VALIDATION COMPLETE")
        print("=" * 50)
        print(f"📊 Tests Run: {self.results['summary']['total_tests']}")
        print(f"✅ Tests Passed: {self.results['summary']['passed_tests']}")
        print(f"📈 Success Rate: {self.results['summary']['success_rate']}%")
        print(f"🏥 System Health: {self.results['summary']['overall_health']}")
        print(f"📋 Report: {report_path}")
        print("=" * 50)

        if self.results["recommendations"]:
            print("💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"  • {rec}")


async def main():
    """Run validation suite"""
    validator = EQ12ValidationSuite()
    await validator.run_full_validation()


if __name__ == "__main__":
    asyncio.run(main())
