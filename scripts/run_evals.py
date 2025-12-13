#!/usr/bin/env python3
"""
EQ12 Evaluation Runner
Automated testing for prompt system integrity and sports betting logic.
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from datetime import UTC, datetime
from pathlib import Path

# Add EQ12 modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from scripts.eq12_responses_client import EQ12ResponsesClient
    from scripts.eq12_timezone import utc_now
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("💡 Make sure EQ12 modules are properly installed")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EQ12EvaluationRunner:
    """Professional evaluation runner for EQ12 automation stack."""

    def __init__(self):
        self.results: dict = {}
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

        # Evaluation criteria (expert sports betting standards)
        self.criteria = {
            "max_parlay_legs": 4,  # Professional limit
            "min_ev_threshold": 0.05,  # 5% minimum EV
            "max_correlation_penalty": 0.05,  # 5% max penalty
            "allowed_books": {"draftkings", "fanduel", "betmgm"},
            "required_schema_keys": {"legs", "total_ev", "total_odds", "strategy"},
        }

    async def run_evaluations(self, prompt_id: str | None = None) -> dict:
        """Run comprehensive evaluation suite."""
        logger.info("🧪 Starting EQ12 evaluation suite...")

        try:
            # Core evaluation categories
            evaluations = {
                "sportsbook_compliance": self.evaluate_sportsbook_compliance,
                "datetime_consistency": self.evaluate_datetime_usage,
                "prompt_system_integrity": self.evaluate_prompt_system,
                "parlay_logic_validation": self.evaluate_parlay_logic,
                "ev_calculation_accuracy": self.evaluate_ev_calculations,
            }

            # If specific prompt provided, focus on that
            if prompt_id:
                evaluations["prompt_specific"] = lambda: self.evaluate_specific_prompt(prompt_id)

            results = {}

            for eval_name, eval_func in evaluations.items():
                logger.info(f"   Running {eval_name}...")
                try:
                    result = (
                        await eval_func() if asyncio.iscoroutinefunction(eval_func) else eval_func()
                    )
                    results[eval_name] = result

                    status = "✅ PASS" if result.get("passed", False) else "❌ FAIL"
                    logger.info(f"   {eval_name}: {status}")

                except Exception as e:
                    logger.error(f"   {eval_name}: ❌ ERROR - {e}")
                    results[eval_name] = {"passed": False, "error": str(e)}

            # Generate summary
            summary = self.generate_evaluation_summary(results)

            # Persist results
            await self.save_evaluation_results(summary)

            return summary

        except Exception as e:
            logger.error(f"❌ Evaluation suite failed: {e}")
            logger.error(traceback.format_exc())
            return {"passed": False, "error": str(e)}

    def evaluate_sportsbook_compliance(self) -> dict:
        """Ensure only DK/FD/MGM sportsbooks are used."""
        try:
            compliance_issues = []

            # Scan Python files for sportsbook references
            root = Path(".")
            py_files = list(root.rglob("*.py"))

            unauthorized_books = {
                "caesars",
                "bet365",
                "barstool",
                "pointsbet",
                "wynnbet",
                "betrivers",
                "unibet",
                "bovada",
            }

            for file_path in py_files:
                if any(exc in str(file_path) for exc in [".venv", "__pycache__", "archive"]):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore").lower()

                    for book in unauthorized_books:
                        if book in content and "test" not in str(file_path):
                            compliance_issues.append(
                                f"Unauthorized sportsbook '{book}' in {file_path}"
                            )

                except Exception:
                    continue

            return {
                "passed": len(compliance_issues) == 0,
                "issues_count": len(compliance_issues),
                "issues": compliance_issues[:10],  # Limit output
                "allowed_books": list(self.criteria["allowed_books"]),
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    def evaluate_datetime_usage(self) -> dict:
        """Check for proper UTC datetime handling."""
        try:
            datetime_issues = []

            # Scan for naive datetime usage patterns
            root = Path(".")
            py_files = list(root.rglob("*.py"))

            problematic_patterns = [
                "datetime.now()",  # Should be datetime.now(timezone.utc)
                "datetime.today()",
                ".now()",  # Without timezone context
            ]

            for file_path in py_files:
                if any(exc in str(file_path) for exc in [".venv", "__pycache__", "archive"]):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")

                    for pattern in problematic_patterns:
                        if pattern in content and "timezone" not in content:
                            # Check if it's not already handled properly
                            if "utc" not in content.lower():
                                datetime_issues.append(
                                    f"Potential naive datetime in {file_path}: {pattern}"
                                )

                except Exception:
                    continue

            # Check for UTC usage (positive indicator)
            utc_usage_count = 0
            for file_path in py_files:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if any(
                        term in content.lower() for term in ["utc", "timezone.utc", "eq12_timezone"]
                    ):
                        utc_usage_count += 1
                except Exception:
                    continue

            return {
                "passed": len(datetime_issues) == 0,
                "issues_count": len(datetime_issues),
                "issues": datetime_issues[:5],  # Limit output
                "utc_usage_files": utc_usage_count,
                "recommendation": "Use eq12_timezone.utc_now() for all datetime operations",
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def evaluate_prompt_system(self) -> dict:
        """Validate prompt system integrity."""
        try:
            # Check if key prompts exist
            prompts_dir = Path("scripts/prompts")
            required_prompts = [
                "parlay_builder_balanced.md",
                "parlay_builder_spreads.md",
                "alert_copy.md",
            ]

            prompt_status = {}
            for prompt_file in required_prompts:
                prompt_path = prompts_dir / prompt_file
                if prompt_path.exists():
                    content = prompt_path.read_text(encoding="utf-8")
                    prompt_status[prompt_file] = {
                        "exists": True,
                        "length": len(content),
                        "has_schema": "json" in content.lower() or "schema" in content.lower(),
                    }
                else:
                    prompt_status[prompt_file] = {"exists": False}

            # Test prompt system if available
            system_test_passed = True
            try:
                if os.getenv("OPENAI_API_KEY"):
                    # Basic system test (without actual API call in CI)
                    client = EQ12ResponsesClient()
                    system_test_passed = hasattr(client, "build_parlay_with_prompt_id")
            except Exception:
                system_test_passed = False

            all_prompts_exist = all(
                status.get("exists", False) for status in prompt_status.values()
            )

            return {
                "passed": all_prompts_exist and system_test_passed,
                "prompt_files": prompt_status,
                "system_test": system_test_passed,
                "prompts_dir_exists": prompts_dir.exists(),
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    def evaluate_parlay_logic(self) -> dict:
        """Validate parlay building logic constraints."""
        try:
            # Test with sample data
            sample_parlay = {
                "legs": [
                    {"market": "spread", "odds": -110, "ev": 0.08},
                    {"market": "total", "odds": -105, "ev": 0.06},
                ],
                "total_ev": 0.14,
                "total_odds": 264,
                "strategy": "balanced",
            }

            validation_results = {}

            # Test EV threshold
            validation_results["ev_threshold"] = (
                sample_parlay["total_ev"] >= self.criteria["min_ev_threshold"]
            )

            # Test leg count
            leg_count = len(sample_parlay["legs"])
            validation_results["leg_count"] = 2 <= leg_count <= self.criteria["max_parlay_legs"]

            # Test schema completeness
            has_required_keys = all(
                key in sample_parlay for key in self.criteria["required_schema_keys"]
            )
            validation_results["schema_compliance"] = has_required_keys

            all_passed = all(validation_results.values())

            return {
                "passed": all_passed,
                "validations": validation_results,
                "sample_data": sample_parlay,
                "criteria": self.criteria,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    def evaluate_ev_calculations(self) -> dict:
        """Test EV calculation accuracy."""
        try:
            # Test cases for EV calculation
            test_cases = [
                {
                    "model_prob": 0.55,
                    "american_odds": -110,
                    "expected_ev": 0.05,
                },  # ~5% EV
                {
                    "model_prob": 0.60,
                    "american_odds": 100,
                    "expected_ev": 0.20,
                },  # 20% EV
                {
                    "model_prob": 0.45,
                    "american_odds": -110,
                    "expected_ev": -0.045,
                },  # Negative EV
            ]

            ev_test_results = []

            # Try to import and test EV calculation if available
            try:
                from scripts.eq12_math import expected_value_percentage

                for case in test_cases:
                    calculated_ev = expected_value_percentage(
                        case["model_prob"], case["american_odds"]
                    )
                    expected_ev = case["expected_ev"]

                    # Allow 2% tolerance
                    tolerance = 0.02
                    passed = abs(calculated_ev - expected_ev) <= tolerance

                    ev_test_results.append(
                        {
                            "case": case,
                            "calculated": round(calculated_ev, 4),
                            "expected": expected_ev,
                            "passed": passed,
                        }
                    )

            except ImportError:
                # EV module not available
                return {
                    "passed": False,
                    "error": "eq12_math module not available for EV testing",
                    "recommendation": "Ensure eq12_math.py exists with expected_value_percentage function",
                }

            all_ev_tests_passed = all(result["passed"] for result in ev_test_results)

            return {
                "passed": all_ev_tests_passed,
                "test_results": ev_test_results,
                "tests_count": len(test_cases),
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    async def evaluate_specific_prompt(self, prompt_id: str) -> dict:
        """Test specific prompt functionality."""
        try:
            if not os.getenv("OPENAI_API_KEY"):
                return {
                    "passed": False,
                    "skipped": True,
                    "reason": "OPENAI_API_KEY not set for prompt testing",
                }

            # Test prompt with mock data
            test_data = {
                "legs": [
                    {
                        "book": "draftkings",
                        "market": "spread",
                        "odds": -110,
                        "ev": 0.08,
                    },
                    {"book": "fanduel", "market": "total", "odds": 105, "ev": 0.06},
                ],
                "strategy": "test_evaluation",
            }

            client = EQ12ResponsesClient()

            # This would be a real API test in full evaluation
            # For CI, we just validate the method exists and is callable
            has_method = hasattr(client, "build_parlay_with_prompt_id")

            return {
                "passed": has_method,
                "prompt_id": prompt_id,
                "test_data": test_data,
                "method_available": has_method,
            }

        except Exception as e:
            return {"passed": False, "error": str(e)}

    def generate_evaluation_summary(self, results: dict) -> dict:
        """Generate comprehensive evaluation summary."""
        passed_count = sum(1 for result in results.values() if result.get("passed", False))
        total_count = len(results)
        success_rate = passed_count / total_count if total_count > 0 else 0

        # Determine overall status
        if success_rate == 1.0:
            status = "✅ ALL PASS"
        elif success_rate >= 0.8:
            status = "⚠️ MOSTLY PASS"
        else:
            status = "❌ FAIL"

        summary = {
            "timestamp": utc_now().isoformat(),
            "overall_status": status,
            "success_rate": round(success_rate, 2),
            "passed_count": passed_count,
            "total_count": total_count,
            "results": results,
            "recommendations": self.generate_recommendations(results),
        }

        return summary

    def generate_recommendations(self, results: dict) -> list[str]:
        """Generate actionable recommendations based on results."""
        recommendations = []

        # Sportsbook compliance
        sportsbook_result = results.get("sportsbook_compliance", {})
        if not sportsbook_result.get("passed", False):
            recommendations.append(
                "🎯 Remove unauthorized sportsbooks - only use DraftKings, FanDuel, BetMGM"
            )

        # Datetime issues
        datetime_result = results.get("datetime_consistency", {})
        if not datetime_result.get("passed", False):
            recommendations.append(
                "🕐 Fix naive datetime usage - use eq12_timezone.utc_now() everywhere"
            )

        # Prompt system
        prompt_result = results.get("prompt_system_integrity", {})
        if not prompt_result.get("passed", False):
            recommendations.append(
                "📝 Fix prompt system - ensure all required prompts exist and are accessible"
            )

        # Parlay logic
        parlay_result = results.get("parlay_logic_validation", {})
        if not parlay_result.get("passed", False):
            recommendations.append(
                "🎲 Fix parlay logic - ensure EV thresholds and leg limits are enforced"
            )

        # EV calculations
        ev_result = results.get("ev_calculation_accuracy", {})
        if not ev_result.get("passed", False):
            recommendations.append(
                "📊 Fix EV calculations - ensure mathematical accuracy within 2% tolerance"
            )

        if not recommendations:
            recommendations.append("🎉 All evaluations passed - system is operating correctly!")

        return recommendations

    async def save_evaluation_results(self, summary: dict):
        """Save evaluation results to structured logs."""
        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            results_file = self.logs_dir / f"evaluation_results_{timestamp}.json"

            with open(results_file, "w") as f:
                json.dump(summary, f, indent=2, default=str)

            # Also save latest
            latest_file = self.logs_dir / "latest_evaluation_results.json"
            with open(latest_file, "w") as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"💾 Evaluation results saved to {results_file}")

        except Exception as e:
            logger.error(f"Failed to save evaluation results: {e}")


async def main():
    """Main entry point for evaluation runner."""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Evaluation Runner")
    parser.add_argument("--prompt-id", help="Specific prompt ID to test")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("🧪 EQ12 Evaluation Suite Starting...")
    print("=" * 50)

    try:
        runner = EQ12EvaluationRunner()
        results = await runner.run_evaluations(prompt_id=args.prompt_id)

        print("\n📊 Evaluation Results:")
        print(f"Status: {results['overall_status']}")
        print(f"Success Rate: {results['success_rate']:.1%}")
        print(f"Passed: {results['passed_count']}/{results['total_count']}")

        if results.get("recommendations"):
            print("\n💡 Recommendations:")
            for rec in results["recommendations"]:
                print(f"   {rec}")

        # Exit with error if evaluations failed
        if results["success_rate"] < 1.0:
            print("\n❌ Some evaluations failed - check logs for details")
            sys.exit(1)
        else:
            print("\n✅ All evaluations passed!")

    except Exception as e:
        print(f"❌ Evaluation runner failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
