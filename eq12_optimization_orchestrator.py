#!/usr/bin/env python3
"""
EQ12 Model Optimization Integration
Connects advanced optimizer with existing EQ12 systems for continuous improvement
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any

# Add EQ12 modules to path
sys.path.append(os.path.dirname(__file__))

try:
    from eq12_advanced_optimizer import (
        EQ12AdvancedOptimizer,
        EvalType,
        OptimizationMethod,
    )
    from eq12_openai_optimizer import AIProfile, EQ12OpenAIOptimizer
    from eq12_openai_status_monitor import EQ12OpenAIStatusMonitor
except ImportError as e:
    logging.error(f"Failed to import EQ12 modules: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class EQ12OptimizationOrchestrator:
    """
    Orchestrates model optimization across the EQ12 ecosystem
    Integrates with existing systems for continuous improvement
    """

    def __init__(self):
        """Initialize the optimization orchestrator"""
        self.advanced_optimizer = EQ12AdvancedOptimizer()
        self.legacy_optimizer = EQ12OpenAIOptimizer()
        self.status_monitor = EQ12OpenAIStatusMonitor()

        # EQ12 use case configurations
        self.eq12_use_cases = {
            "betting_analysis": {
                "description": "Analyze betting odds and generate insights",
                "profile": AIProfile.DATA_ANALYSIS,
                "eval_types": [
                    EvalType.ACCURACY,
                    EvalType.FACTUALITY,
                    EvalType.CONSISTENCY,
                ],
                "expected_accuracy": 0.85,
            },
            "cannabis_compliance": {
                "description": "Generate compliance reports for cannabis operations",
                "profile": AIProfile.COMPLIANCE,
                "eval_types": [EvalType.ACCURACY, EvalType.SAFETY, EvalType.COMPLIANCE],
                "expected_accuracy": 0.95,
            },
            "credit_assessment": {
                "description": "Assess credit risks and generate reports",
                "profile": AIProfile.RISK_ASSESSMENT,
                "eval_types": [EvalType.ACCURACY, EvalType.FACTUALITY, EvalType.SAFETY],
                "expected_accuracy": 0.90,
            },
            "governance_automation": {
                "description": "Automate governance and security workflows",
                "profile": AIProfile.GOVERNANCE,
                "eval_types": [EvalType.ACCURACY, EvalType.SAFETY, EvalType.COMPLIANCE],
                "expected_accuracy": 0.92,
            },
            "code_generation": {
                "description": "Generate and review code for EQ12 systems",
                "profile": AIProfile.CODE_GENERATION,
                "eval_types": [
                    EvalType.CODE_QUALITY,
                    EvalType.ACCURACY,
                    EvalType.CONSISTENCY,
                ],
                "expected_accuracy": 0.88,
            },
        }

        logger.info("EQ12 Optimization Orchestrator initialized")

    async def run_comprehensive_evaluation(self, use_case: str) -> dict[str, Any]:
        """
        Run comprehensive evaluation for a specific EQ12 use case

        Args:
            use_case: The use case to evaluate

        Returns:
            Evaluation results and recommendations
        """
        if use_case not in self.eq12_use_cases:
            raise ValueError(f"Unknown use case: {use_case}")

        config = self.eq12_use_cases[use_case]

        logger.info(f"Running comprehensive evaluation for {use_case}")

        # Check OpenAI service status before proceeding
        openai_status = await self.status_monitor.get_current_status()

        # Check if API service is available
        api_service = openai_status.get("API")
        if api_service and api_service.status not in [
            "operational",
            "degraded_performance",
        ]:
            logger.warning(
                f"OpenAI API service status: {api_service.status} - {api_service.description}"
            )
            return {
                "use_case": use_case,
                "status": "postponed",
                "reason": f"OpenAI API unavailable: {api_service.status}",
                "service_status": openai_status,
                "recommendations": [
                    "Wait for OpenAI API service to be restored",
                    "Use cached results if available",
                ],
                "evaluation_timestamp": datetime.utcnow().isoformat(),
            }

        # Generate evaluation examples based on use case
        examples = self._generate_eval_examples(use_case)

        # Create evaluation dataset
        eval_dataset = self.advanced_optimizer.create_eval_dataset(
            use_case, examples, config["eval_types"]
        )

        # Get optimized profile from legacy optimizer
        self.legacy_optimizer.get_profile(config["profile"])

        # Engineer prompt for the use case
        base_prompt = self._get_base_prompt(use_case)
        context_data = self._get_context_data(use_case)

        optimized_prompt = self.advanced_optimizer.engineer_prompt(
            base_prompt,
            context_data=context_data,
            examples=examples[:2],  # Use first 2 as few-shot examples
        )

        # Run evaluation with different models
        models_to_test = ["gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14"]

        all_results = {}

        for model in models_to_test:
            try:
                eval_results = await self.advanced_optimizer.run_eval(
                    model, optimized_prompt, eval_dataset, config["eval_types"]
                )

                # Calculate metrics
                avg_scores = {}
                for eval_type in config["eval_types"]:
                    type_scores = [r.score for r in eval_results if r.eval_type == eval_type]
                    avg_scores[eval_type.value] = (
                        sum(type_scores) / len(type_scores) if type_scores else 0.0
                    )

                all_results[model] = {
                    "avg_scores": avg_scores,
                    "overall_score": sum(avg_scores.values()) / len(avg_scores),
                    "eval_count": len(eval_results),
                    "meets_target": sum(avg_scores.values()) / len(avg_scores)
                    >= config["expected_accuracy"],
                }

            except Exception as e:
                logger.error(f"Evaluation failed for {model}: {e}")
                all_results[model] = {"error": str(e)}

        # Get optimization recommendations
        best_performance = max(
            [r.get("overall_score", 0) for r in all_results.values() if "error" not in r]
        )

        recommendations = self.advanced_optimizer.get_optimization_recommendations(
            use_case, {"overall": best_performance}
        )

        return {
            "use_case": use_case,
            "evaluation_results": all_results,
            "recommendations": recommendations,
            "target_accuracy": config["expected_accuracy"],
            "evaluation_timestamp": datetime.utcnow().isoformat(),
        }

    def _generate_eval_examples(self, use_case: str) -> list[dict[str, str]]:
        """Generate evaluation examples for specific use cases"""
        examples = {
            "betting_analysis": [
                {
                    "input": "Analyze the odds for Yankees ML -110 vs Red Sox +100. Current line movement shows 65% public money on Yankees.",
                    "expected_output": "The Yankees are favored at -110 (52.4% implied probability) while receiving 65% of public money, suggesting potential overvaluation. The 12.6% difference between public betting and implied odds indicates a possible value opportunity on the Red Sox at +100.",
                },
                {
                    "input": "What factors should I consider for NBA over/under betting on Lakers vs Warriors total 225.5?",
                    "expected_output": "Key factors: Both teams' pace of play, recent scoring trends, injury reports (especially key players), defensive efficiency, back-to-back situations, and historical head-to-head scoring patterns. Weather is not relevant for indoor NBA games.",
                },
            ],
            "cannabis_compliance": [
                {
                    "input": "Generate compliance report for 500 units of Blue Dream strain transferred from cultivation to dispensary.",
                    "expected_output": "METRC Transfer Report: 500 units Blue Dream (THC: 18-22%, CBD: 0.5-1%) transferred from License #C12345 to Dispensary License #D67890. Chain of custody maintained, all units tagged per state requirements. Transfer completed within required 24-hour window.",
                }
            ],
            "credit_assessment": [
                {
                    "input": "Assess credit risk for applicant: FICO 680, DTI 35%, income $75k, 2 late payments in past year.",
                    "expected_output": "Moderate credit risk profile. FICO 680 indicates fair creditworthiness, DTI 35% is within acceptable range but approaching upper limit. Recent late payments suggest payment reliability concerns. Recommend conditional approval with higher interest rate or additional documentation.",
                }
            ],
            "governance_automation": [
                {
                    "input": "Review security incident: Unauthorized access attempt on production database at 2:30 AM.",
                    "expected_output": "Security Alert: Potential breach attempt detected. Immediate actions required: 1) Isolate affected system, 2) Review access logs, 3) Notify security team, 4) Document incident per compliance requirements, 5) Initiate incident response protocol. Escalate to CISO within 1 hour.",
                }
            ],
            "code_generation": [
                {
                    "input": "Generate Python function to validate betting odds format and calculate implied probability.",
                    "expected_output": "```python\ndef validate_odds_and_probability(odds_str):\n    import re\n    # Handle American odds format\n    if re.match(r'^[+-]\\d+$', odds_str):\n        odds = int(odds_str)\n        if odds > 0:\n            return {'valid': True, 'implied_prob': 100 / (odds + 100)}\n        else:\n            return {'valid': True, 'implied_prob': abs(odds) / (abs(odds) + 100)}\n    return {'valid': False, 'error': 'Invalid odds format'}\n```",
                }
            ],
        }

        return examples.get(use_case, [])

    def _get_base_prompt(self, use_case: str) -> str:
        """Get base prompt for specific use case"""
        prompts = {
            "betting_analysis": "Analyze the provided betting information and provide accurate, data-driven insights with specific probabilities and recommendations.",
            "cannabis_compliance": "Generate accurate compliance documentation following all state regulations and METRC requirements.",
            "credit_assessment": "Assess credit risk based on provided financial information using standard banking criteria.",
            "governance_automation": "Analyze security incidents and provide appropriate response actions following established protocols.",
            "code_generation": "Generate clean, well-documented Python code that follows best practices and includes error handling.",
        }

        return prompts.get(use_case, "Provide accurate and helpful information based on the input.")

    def _get_context_data(self, use_case: str) -> list[str]:
        """Get relevant context data for use case"""
        context = {
            "betting_analysis": [
                "Use standard probability calculations for odds conversion",
                "Consider line movement and public betting percentages",
                "Factor in relevant team/player statistics and trends",
            ],
            "cannabis_compliance": [
                "Follow all state cannabis regulations and METRC requirements",
                "Ensure proper chain of custody documentation",
                "Include required tracking numbers and timestamps",
            ],
            "credit_assessment": [
                "Use standard banking risk assessment criteria",
                "Consider FICO score ranges and DTI ratio guidelines",
                "Factor in recent payment history and income stability",
            ],
            "governance_automation": [
                "Follow established security incident response protocols",
                "Prioritize containment and evidence preservation",
                "Ensure compliance with notification requirements",
            ],
            "code_generation": [
                "Follow Python PEP 8 style guidelines",
                "Include proper error handling and input validation",
                "Add clear documentation and type hints",
            ],
        }

        return context.get(use_case, [])

    async def optimize_production_system(self, use_case: str) -> dict[str, Any]:
        """
        Run optimization pipeline for production EQ12 system

        Args:
            use_case: The use case to optimize

        Returns:
            Optimization results and deployment recommendations
        """
        logger.info(f"Starting production optimization for {use_case}")

        # Step 1: Run comprehensive evaluation
        eval_results = await self.run_comprehensive_evaluation(use_case)

        # Step 2: Determine if fine-tuning is needed
        best_score = max(
            [
                r.get("overall_score", 0)
                for r in eval_results["evaluation_results"].values()
                if "error" not in r
            ]
        )

        config = self.eq12_use_cases[use_case]
        needs_fine_tuning = best_score < config["expected_accuracy"]

        optimization_plan = {
            "evaluation_summary": eval_results,
            "needs_fine_tuning": needs_fine_tuning,
            "recommended_actions": [],
            "deployment_ready": False,
        }

        if needs_fine_tuning:
            # Recommend fine-tuning approach
            if best_score < 0.7:
                optimization_plan["recommended_actions"].append(
                    {
                        "action": "supervised_fine_tuning",
                        "priority": "high",
                        "description": "Create training dataset with 100+ examples and fine-tune base model",
                        "estimated_improvement": "15-25%",
                    }
                )

            optimization_plan["recommended_actions"].append(
                {
                    "action": "prompt_engineering",
                    "priority": "medium",
                    "description": "Enhance prompts with better context and examples",
                    "estimated_improvement": "5-15%",
                }
            )
        else:
            optimization_plan["deployment_ready"] = True
            optimization_plan["recommended_actions"].append(
                {
                    "action": "deploy_optimized_model",
                    "priority": "high",
                    "description": "Current performance meets targets - ready for production deployment",
                }
            )

        # Step 3: Generate deployment configuration
        if optimization_plan["deployment_ready"]:
            optimization_plan["deployment_config"] = self._generate_deployment_config(
                use_case, eval_results
            )

        return optimization_plan

    def _generate_deployment_config(
        self, use_case: str, eval_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate deployment configuration for optimized model"""

        # Find best performing model
        best_model = max(
            eval_results["evaluation_results"].keys(),
            key=lambda m: eval_results["evaluation_results"][m].get("overall_score", 0),
        )

        config = self.eq12_use_cases[use_case]
        profile = self.legacy_optimizer.get_profile(config["profile"])

        return {
            "model": best_model,
            "parameters": profile.to_dict(),
            "use_case": use_case,
            "expected_performance": eval_results["evaluation_results"][best_model]["avg_scores"],
            "monitoring_thresholds": {
                "min_accuracy": config["expected_accuracy"]
                * 0.9,  # 10% below target triggers alert
                "eval_frequency": "weekly",
            },
            "deployment_timestamp": datetime.utcnow().isoformat(),
        }

    def generate_optimization_report(self, results: dict[str, Any]) -> str:
        """Generate human-readable optimization report"""
        report = f"""
# EQ12 Model Optimization Report

## Use Case: {results["use_case"]}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Performance Summary
"""

        for model, perf in results["evaluation_summary"]["evaluation_results"].items():
            if "error" not in perf:
                report += f"""
### {model}
- Overall Score: {perf["overall_score"]:.2%}
- Meets Target: {"✅ Yes" if perf["meets_target"] else "❌ No"}
- Evaluations Run: {perf["eval_count"]}

**Detailed Scores:**
"""
                for metric, score in perf["avg_scores"].items():
                    report += f"- {metric.title()}: {score:.2%}\n"

        report += f"""

## Recommendations
**Fine-tuning Needed:** {"Yes" if results["needs_fine_tuning"] else "No"}

**Priority Actions:**
"""

        for action in results["recommended_actions"]:
            report += f"""
- **{action["action"].replace("_", " ").title()}** ({action["priority"]} priority)
  {action["description"]}
  Expected improvement: {action.get("estimated_improvement", "TBD")}
"""

        if results.get("deployment_ready"):
            report += f"""

## ✅ Deployment Ready
The optimized model meets performance targets and is ready for production deployment.

**Recommended Configuration:**
- Model: {results["deployment_config"]["model"]}
- Expected Performance: {results["deployment_config"]["expected_performance"]}
"""

        return report


# CLI interface
async def main():
    """Main CLI interface for EQ12 optimization"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Model Optimization CLI")
    parser.add_argument(
        "use_case",
        choices=[
            "betting_analysis",
            "cannabis_compliance",
            "credit_assessment",
            "governance_automation",
            "code_generation",
        ],
    )
    parser.add_argument("--action", choices=["evaluate", "optimize", "report"], default="optimize")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    orchestrator = EQ12OptimizationOrchestrator()

    if args.action == "evaluate":
        results = await orchestrator.run_comprehensive_evaluation(args.use_case)
    elif args.action == "optimize":
        results = await orchestrator.optimize_production_system(args.use_case)

    # Generate report
    if args.action in ["optimize", "report"]:
        report = orchestrator.generate_optimization_report(results)

        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)

    # Save results as JSON
    results_file = (
        f"eq12_optimization_{args.use_case}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Detailed results saved to {results_file}")


if __name__ == "__main__":
    asyncio.run(main())
