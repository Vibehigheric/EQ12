#!/usr/bin/env python3
"""
EQ12 Prompt Evaluation Harness
Automated testing suite for prompt stability and compliance.
Version: 1.0 | Created: 2025-10-05
"""

import argparse
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any

import jsonschema
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """Individual test case from eval suite."""

    id: str
    name: str
    category: str
    description: str
    input: dict[str, Any]
    expected_behavior: str
    validation_rules: list[str]
    pass_criteria: str
    fail_indicators: list[str]


@dataclass
class TestResult:
    """Result from running a single test case."""

    test_id: str
    status: str  # PASS, FAIL, ERROR
    score: float  # 0.0 to 1.0
    errors: list[str]
    warnings: list[str]
    execution_time: float
    model_output: str | None


class EQ12PromptEvaluator:
    """Main evaluation harness for EQ12 prompts."""

    def __init__(self, eval_config_path: str = "C:/EQ12/evals/eq12_prompt_eval_suite.yaml"):
        """Initialize evaluator with test suite configuration."""
        self.config_path = Path(eval_config_path)
        self.load_config()
        self.setup_schemas()

    def load_config(self):
        """Load evaluation configuration from YAML."""
        try:
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)

            # Parse test cases
            self.test_cases = []
            for case_data in self.config["test_cases"]:
                test_case = TestCase(
                    id=case_data["id"],
                    name=case_data["name"],
                    category=case_data["category"],
                    description=case_data["description"],
                    input=case_data["input"],
                    expected_behavior=case_data["expected_behavior"],
                    validation_rules=case_data["validation_rules"],
                    pass_criteria=case_data["pass_criteria"],
                    fail_indicators=case_data["fail_indicators"],
                )
                self.test_cases.append(test_case)

            logger.info(f"Loaded {len(self.test_cases)} test cases")

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def setup_schemas(self):
        """Load JSON schemas for validation."""
        schema_dir = Path("C:/EQ12/prompts/v1.0")
        self.schemas = {}

        schema_files = {
            "parlay": "parlay_schema.json",
            "odds_extract": "odds_extract_schema.json",
            "validation": "validation_schema.json",
        }

        for schema_name, filename in schema_files.items():
            try:
                schema_path = schema_dir / filename
                with open(schema_path) as f:
                    self.schemas[schema_name] = json.load(f)
                logger.info(f"Loaded {schema_name} schema")
            except Exception as e:
                logger.warning(f"Could not load {schema_name} schema: {e}")

    def validate_json_schema(self, data: Any, schema_name: str) -> list[str]:
        """Validate data against JSON schema."""
        errors = []

        if schema_name not in self.schemas:
            errors.append(f"Schema {schema_name} not available")
            return errors

        try:
            jsonschema.validate(data, self.schemas[schema_name])
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        except Exception as e:
            errors.append(f"Schema validation failed: {e}")

        return errors

    def check_policy_compliance(self, output: dict[str, Any]) -> list[str]:
        """Check output for EQ12 policy compliance."""
        violations = []

        # Check allowed books
        if "book" in output:
            allowed_books = ["draftkings", "fanduel", "betmgm"]
            if output["book"] not in allowed_books:
                violations.append(f"Prohibited book: {output['book']}")

        # Check one leg per game rule
        if "legs" in output and isinstance(output["legs"], list):
            game_ids = [leg.get("game_id") for leg in output["legs"] if "game_id" in leg]
            if len(game_ids) != len(set(game_ids)):
                violations.append("Multiple legs from same game (correlation violation)")

        # Check UTC timezone format
        utc_fields = ["start_time_utc", "extracted_at_utc"]
        for field in utc_fields:
            if field in output:
                timestamp = output[field]
                if not isinstance(timestamp, str) or not (
                    timestamp.endswith("Z") or "+" in timestamp
                ):
                    violations.append(f"Invalid UTC format in {field}: {timestamp}")

        # Check risk flags present
        if "legs" in output and isinstance(output["legs"], list):
            for i, leg in enumerate(output["legs"]):
                if "risk_flag" not in leg:
                    violations.append(f"Missing risk_flag in leg {i}")
                elif leg["risk_flag"] not in ["LOW", "MEDIUM", "HIGH"]:
                    violations.append(f"Invalid risk_flag in leg {i}: {leg['risk_flag']}")

        return violations

    def check_math_accuracy(self, output: dict[str, Any], tolerance: float = 0.001) -> list[str]:
        """Verify mathematical calculations in output."""
        errors = []

        # Check implied probability calculations
        if "legs" in output and isinstance(output["legs"], list):
            for i, leg in enumerate(output["legs"]):
                if all(k in leg for k in ["american_odds", "implied_prob"]):
                    odds = leg["american_odds"]
                    stated_prob = leg["implied_prob"]

                    # Calculate expected implied probability
                    if odds > 0:
                        expected_prob = 100 / (odds + 100)
                    else:
                        expected_prob = abs(odds) / (abs(odds) + 100)

                    if abs(stated_prob - expected_prob) > tolerance:
                        errors.append(
                            f"Implied probability error in leg {i}: expected {expected_prob:.3f}, got {stated_prob}"
                        )

        # Check Kelly fraction caps
        if "legs" in output and isinstance(output["legs"], list):
            max_kelly = 0.025  # 2.5% default cap
            for i, leg in enumerate(output["legs"]):
                if "kelly_fraction" in leg:
                    kelly = leg["kelly_fraction"]
                    if kelly > max_kelly:
                        errors.append(
                            f"Kelly fraction exceeds cap in leg {i}: {kelly} > {max_kelly}"
                        )

        # Check probability ranges
        prob_fields = ["model_prob", "implied_prob", "parlay_prob"]
        for field in prob_fields:
            if field in output:
                prob = output[field]
                if not (0.0 <= prob <= 1.0):
                    errors.append(f"Probability out of range for {field}: {prob}")

        return errors

    def check_safety_compliance(self, output: Any) -> list[str]:
        """Check for prohibited language and safety violations."""
        violations = []

        # Convert output to string for text analysis
        output_text = json.dumps(output) if isinstance(output, dict) else str(output)
        output_lower = output_text.lower()

        # Check for prohibited financial advice language
        prohibited_words = [
            "guaranteed",
            "sure thing",
            "can't lose",
            "lock",
            "guarantee",
            "sit tight",
            "wait for me",
            "trust me",
            "i will do that later",
        ]

        for word in prohibited_words:
            if word in output_lower:
                violations.append(f"Prohibited language detected: '{word}'")

        # Check for appropriate risk disclaimers in parlay outputs
        if isinstance(output, dict) and "legs" in output:
            has_risk_flags = any("risk_flag" in leg for leg in output.get("legs", []))
            if not has_risk_flags:
                violations.append("Missing risk assessment in parlay output")

        return violations

    def simulate_model_response(self, test_case: TestCase) -> str:
        """
        Simulate model response for testing purposes.
        In production, this would call actual LLM API.
        """
        # For demo purposes, return structured responses based on test case
        if test_case.category == "schema_adherence":
            if "parlay" in test_case.name.lower():
                return json.dumps(
                    {
                        "strategy": "hook_spread",
                        "book": "draftkings",
                        "confidence": "MEDIUM",
                        "legs": [
                            {
                                "game_id": "nfl_20251005_chiefs_bills",
                                "market": "spread",
                                "selection": "Chiefs -3.0",
                                "point": -3.0,
                                "american_odds": -110,
                                "model_prob": 0.55,
                                "implied_prob": 0.524,
                                "ev_percent": 4.8,
                                "kelly_fraction": 0.02,
                                "start_time_utc": "2025-10-05T20:00:00Z",
                                "risk_flag": "MEDIUM",
                                "why": "Strong road team vs weak home defense",
                            }
                        ],
                        "parlay_odds": -110,
                        "parlay_prob": 0.55,
                        "parlay_ev": 4.8,
                        "stake_recommendation": 20.0,
                        "max_loss": 20.0,
                        "max_win": 18.18,
                        "notes": "Single leg parlay with moderate edge",
                    }
                )
            else:
                return json.dumps(
                    {
                        "extracted_at_utc": "2025-10-05T19:30:00Z",
                        "games": [],
                        "stale_data_warning": False,
                        "missing_books": [],
                    }
                )
        elif test_case.category == "policy_compliance":
            # Test policy violations based on test case
            return json.dumps({"book": "draftkings", "legs": []})
        else:
            return json.dumps({"status": "test_response"})

    def run_test_case(self, test_case: TestCase) -> TestResult:
        """Run a single test case and return results."""
        start_time = time.time()
        errors = []
        warnings = []
        score = 0.0

        try:
            # Simulate model call (in production, use actual LLM API)
            model_output_raw = self.simulate_model_response(test_case)

            # Try to parse as JSON
            try:
                model_output = json.loads(model_output_raw)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON output: {e}")
                model_output = None

            if model_output is not None:
                # Run validation checks based on category
                if test_case.category == "schema_adherence":
                    # Determine schema type from test case
                    schema_type = "parlay" if "parlay" in test_case.name.lower() else "odds_extract"
                    schema_errors = self.validate_json_schema(model_output, schema_type)
                    errors.extend(schema_errors)

                elif test_case.category == "policy_compliance":
                    policy_violations = self.check_policy_compliance(model_output)
                    errors.extend(policy_violations)

                elif test_case.category == "math_accuracy":
                    math_errors = self.check_math_accuracy(model_output)
                    errors.extend(math_errors)

                elif test_case.category == "safety_guardrails":
                    safety_violations = self.check_safety_compliance(model_output)
                    errors.extend(safety_violations)

                # Check for fail indicators
                for fail_indicator in test_case.fail_indicators:
                    if fail_indicator.lower() in model_output_raw.lower():
                        errors.append(f"Fail indicator detected: {fail_indicator}")

            # Calculate score based on errors
            if not errors:
                score = 1.0
                status = "PASS"
            elif len(errors) <= 2:
                score = 0.5
                status = "PARTIAL"
            else:
                score = 0.0
                status = "FAIL"

        except Exception as e:
            errors.append(f"Test execution error: {e}")
            score = 0.0
            status = "ERROR"
            model_output_raw = None

        execution_time = time.time() - start_time

        return TestResult(
            test_id=test_case.id,
            status=status,
            score=score,
            errors=errors,
            warnings=warnings,
            execution_time=execution_time,
            model_output=model_output_raw,
        )

    def run_full_suite(self) -> dict[str, Any]:
        """Run the complete evaluation suite."""
        logger.info("Starting full evaluation suite")
        start_time = time.time()

        results = []
        category_scores = {}

        for test_case in self.test_cases:
            logger.info(f"Running test {test_case.id}: {test_case.name}")
            result = self.run_test_case(test_case)
            results.append(result)

            # Track category scores
            if test_case.category not in category_scores:
                category_scores[test_case.category] = []
            category_scores[test_case.category].append(result.score)

        # Calculate aggregate metrics
        total_score = mean([r.score for r in results]) if results else 0.0
        total_time = time.time() - start_time

        # Calculate category averages
        category_averages = {category: mean(scores) for category, scores in category_scores.items()}

        # Determine pass/fail based on thresholds
        metrics_config = self.config.get("metrics", {})
        overall_pass = True

        for category, avg_score in category_averages.items():
            threshold = metrics_config.get(category, {}).get("passing_threshold", 0.95)
            if avg_score < threshold:
                overall_pass = False
                logger.warning(
                    f"Category {category} below threshold: {avg_score:.3f} < {threshold}"
                )

        suite_result = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_tests": len(results),
            "passed_tests": len([r for r in results if r.status == "PASS"]),
            "failed_tests": len([r for r in results if r.status in ["FAIL", "ERROR"]]),
            "total_score": total_score,
            "category_scores": category_averages,
            "execution_time": total_time,
            "overall_pass": overall_pass,
            "individual_results": [
                {
                    "test_id": r.test_id,
                    "status": r.status,
                    "score": r.score,
                    "errors": r.errors,
                    "execution_time": r.execution_time,
                }
                for r in results
            ],
        }

        logger.info(
            f"Evaluation complete: {suite_result['passed_tests']}/{suite_result['total_tests']} passed"
        )
        logger.info(f"Overall score: {total_score:.3f}")

        return suite_result

    def save_results(self, results: dict[str, Any], output_path: str):
        """Save evaluation results to file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                json.dump(results, f, indent=2)

            logger.info(f"Results saved to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save results: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="EQ12 Prompt Evaluation Harness")
    parser.add_argument(
        "--config",
        default="C:/EQ12/evals/eq12_prompt_eval_suite.yaml",
        help="Path to evaluation config file",
    )
    parser.add_argument(
        "--output",
        default="C:/EQ12/logs/eval_results.json",
        help="Path to save results",
    )
    parser.add_argument("--category", help="Run only tests from specific category")
    parser.add_argument("--test-id", help="Run only specific test by ID")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        evaluator = EQ12PromptEvaluator(args.config)

        # Filter test cases if requested
        if args.category:
            evaluator.test_cases = [
                tc for tc in evaluator.test_cases if tc.category == args.category
            ]
            logger.info(
                f"Filtered to {len(evaluator.test_cases)} tests in category '{args.category}'"
            )

        if args.test_id:
            evaluator.test_cases = [tc for tc in evaluator.test_cases if tc.id == args.test_id]
            logger.info(f"Filtered to test '{args.test_id}'")

        if not evaluator.test_cases:
            logger.error("No test cases to run")
            return 1

        # Run evaluation
        results = evaluator.run_full_suite()

        # Save results
        evaluator.save_results(results, args.output)

        # Print summary
        print("\n🎯 EQ12 Prompt Evaluation Results")
        print(f"{'=' * 50}")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed_tests']}")
        print(f"Failed: {results['failed_tests']}")
        print(f"Overall Score: {results['total_score']:.1%}")
        print(f"Overall Result: {'✅ PASS' if results['overall_pass'] else '❌ FAIL'}")

        print("\n📊 Category Breakdown:")
        for category, score in results["category_scores"].items():
            print(f"  {category}: {score:.1%}")

        # Return appropriate exit code
        return 0 if results["overall_pass"] else 1

    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
