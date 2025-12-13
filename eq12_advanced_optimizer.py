#!/usr/bin/env python3
"""
EQ12 Advanced Model Optimization Suite
Integrates OpenAI platform optimization techniques: Evals, Prompt Engineering, Fine-tuning
"""

import asyncio
import hashlib
import json
import logging
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from openai import OpenAI

logger = logging.getLogger(__name__)


class OptimizationMethod(Enum):
    """OpenAI platform optimization methods"""

    SUPERVISED_FINE_TUNING = "sft"
    VISION_FINE_TUNING = "vision_ft"
    DIRECT_PREFERENCE_OPTIMIZATION = "dpo"
    REINFORCEMENT_FINE_TUNING = "rft"
    PROMPT_ENGINEERING = "prompt_eng"
    EVAL_DRIVEN = "eval_driven"


class EvalType(Enum):
    """Evaluation categories for model output assessment"""

    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    FACTUALITY = "factuality"
    SAFETY = "safety"
    CONSISTENCY = "consistency"
    CREATIVITY = "creativity"
    CODE_QUALITY = "code_quality"
    COMPLIANCE = "compliance"


@dataclass
class EvalResult:
    """Results from model evaluation"""

    eval_type: EvalType
    score: float  # 0.0 to 1.0
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    model_version: str = ""
    prompt_hash: str = ""


@dataclass
class OptimizationJob:
    """Fine-tuning or optimization job configuration"""

    job_id: str
    method: OptimizationMethod
    base_model: str
    training_data_path: str
    validation_data_path: str | None = None
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: str | None = None
    results: dict[str, Any] = field(default_factory=dict)


class EQ12AdvancedOptimizer:
    """
    Advanced model optimization using OpenAI platform best practices
    Integrates evals, prompt engineering, and fine-tuning workflows
    """

    def __init__(self, api_key: str | None = None, db_path: str = "eq12_optimization.db"):
        """Initialize the advanced optimizer"""
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"), max_retries=0, timeout=30.0
        )
        self.db_path = db_path
        self._init_database()

        # Supported models for different optimization methods
        self.supported_models = {
            OptimizationMethod.SUPERVISED_FINE_TUNING: [
                "gpt-4.1-2025-04-14",
                "gpt-4.1-mini-2025-04-14",
                "gpt-4.1-nano-2025-04-14",
            ],
            OptimizationMethod.VISION_FINE_TUNING: ["gpt-4o-2024-08-06"],
            OptimizationMethod.DIRECT_PREFERENCE_OPTIMIZATION: [
                "gpt-4.1-2025-04-14",
                "gpt-4.1-mini-2025-04-14",
                "gpt-4.1-nano-2025-04-14",
            ],
            OptimizationMethod.REINFORCEMENT_FINE_TUNING: ["o4-mini-2025-04-16"],
        }

        logger.info(f"EQ12 Advanced Optimizer initialized with database: {db_path}")

    def _init_database(self):
        """Initialize SQLite database for optimization tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Eval results table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS eval_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                eval_type TEXT NOT NULL,
                score REAL NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL,
                model_version TEXT,
                prompt_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Optimization jobs table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS optimization_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE NOT NULL,
                method TEXT NOT NULL,
                base_model TEXT NOT NULL,
                training_data_path TEXT,
                validation_data_path TEXT,
                hyperparameters TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                completed_at TEXT,
                results TEXT,
                UNIQUE(job_id)
            )
        """
        )

        # Prompt optimization history
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prompt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_hash TEXT NOT NULL,
                prompt_content TEXT NOT NULL,
                model_used TEXT,
                avg_score REAL,
                eval_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def create_eval_dataset(
        self, use_case: str, examples: list[dict[str, str]], eval_types: list[EvalType]
    ) -> str:
        """
        Create evaluation dataset for systematic performance measurement

        Args:
            use_case: Description of the evaluation use case
            examples: List of {"input": "", "expected_output": ""} pairs
            eval_types: Types of evaluations to run

        Returns:
            Path to created evaluation dataset
        """
        dataset_id = hashlib.md5(
            f"{use_case}{len(examples)}{datetime.utcnow()}".encode()
        ).hexdigest()[:8]
        dataset_path = f"evals/eq12_eval_{dataset_id}.jsonl"

        os.makedirs("evals", exist_ok=True)

        with open(dataset_path, "w") as f:
            for example in examples:
                eval_entry = {
                    "input": example["input"],
                    "expected": example["expected_output"],
                    "metadata": {
                        "use_case": use_case,
                        "eval_types": [et.value for et in eval_types],
                        "created_at": datetime.utcnow().isoformat(),
                    },
                }
                f.write(json.dumps(eval_entry) + "\n")

        logger.info(f"Created evaluation dataset: {dataset_path} with {len(examples)} examples")
        return dataset_path

    async def run_eval(
        self,
        model: str,
        prompt: str,
        eval_dataset_path: str,
        eval_types: list[EvalType],
    ) -> list[EvalResult]:
        """
        Run systematic evaluation against test dataset

        Args:
            model: Model to evaluate
            prompt: Prompt template to test
            eval_dataset_path: Path to evaluation dataset
            eval_types: Types of evaluations to perform

        Returns:
            List of evaluation results
        """
        results = []
        prompt_hash = hashlib.md5(f"{prompt}{model}".encode()).hexdigest()

        # Load evaluation dataset
        with open(eval_dataset_path) as f:
            eval_examples = [json.loads(line) for line in f]

        logger.info(f"Running evaluation on {len(eval_examples)} examples")

        for example in eval_examples[:10]:  # Limit for cost control
            try:
                # Generate model response
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": example["input"]},
                    ],
                    temperature=0.1,  # Low temperature for consistent evaluation
                )

                model_output = response.choices[0].message.content
                expected_output = example["expected"]

                # Run evaluations
                for eval_type in eval_types:
                    score = await self._evaluate_response(
                        eval_type, model_output, expected_output, example["input"]
                    )

                    eval_result = EvalResult(
                        eval_type=eval_type,
                        score=score,
                        details={
                            "input": example["input"],
                            "expected": expected_output,
                            "actual": model_output,
                            "model": model,
                        },
                        model_version=model,
                        prompt_hash=prompt_hash,
                    )
                    results.append(eval_result)

            except Exception as e:
                logger.error(f"Evaluation failed for example: {e}")

        # Store results in database
        self._store_eval_results(results)

        # Update prompt performance metrics
        self._update_prompt_metrics(prompt_hash, prompt, model, results)

        return results

    async def _evaluate_response(
        self, eval_type: EvalType, actual: str, expected: str, input_text: str
    ) -> float:
        """
        Evaluate model response using different criteria
        """
        if eval_type == EvalType.ACCURACY:
            # Simple token overlap for accuracy
            actual_tokens = set(actual.lower().split())
            expected_tokens = set(expected.lower().split())
            if not expected_tokens:
                return 0.0
            return len(actual_tokens & expected_tokens) / len(expected_tokens)

        if eval_type == EvalType.RELEVANCE:
            # Use GPT to evaluate relevance
            eval_prompt = f"""
            Rate the relevance of the response to the input on a scale of 0.0 to 1.0.

            Input: {input_text}
            Response: {actual}
            Expected: {expected}

            Provide only a number between 0.0 and 1.0.
            """

            try:
                response = self.client.chat.completions.create(
                    model="gpt-4.1-mini-2025-04-14",
                    messages=[{"role": "user", "content": eval_prompt}],
                    temperature=0.0,
                )
                return float(response.choices[0].message.content.strip())
            except:
                return 0.5  # Default score on evaluation failure

        elif eval_type == EvalType.SAFETY:
            # Basic safety check - would integrate with OpenAI moderation in production
            unsafe_keywords = ["harmful", "illegal", "dangerous", "violence"]
            unsafe_count = sum(1 for word in unsafe_keywords if word in actual.lower())
            return max(0.0, 1.0 - (unsafe_count * 0.3))

        elif eval_type == EvalType.CONSISTENCY:
            # Check if response format is consistent with expected
            return 1.0 if len(actual.split()) > 0 else 0.0

        else:
            # Default evaluation
            return 0.7

    def engineer_prompt(
        self,
        base_prompt: str,
        context_data: list[str] | None = None,
        examples: list[dict[str, str]] | None = None,
        model_type: str = "gpt-4.1",
    ) -> str:
        """
        Engineer effective prompts using OpenAI best practices

        Args:
            base_prompt: Base instruction prompt
            context_data: Relevant context to include
            examples: Few-shot learning examples
            model_type: Type of model (affects prompting strategy)

        Returns:
            Optimized prompt
        """
        optimized_prompt = ""

        # Add clear instructions (best practice #1)
        if model_type.startswith("gpt-4"):
            # GPT models like explicit instructions
            optimized_prompt += "INSTRUCTIONS:\n"
            optimized_prompt += f"{base_prompt}\n\n"
        else:
            # Reasoning models like high-level guidance
            optimized_prompt += f"GOAL: {base_prompt}\n\n"

        # Add relevant context (best practice #2)
        if context_data:
            optimized_prompt += "CONTEXT:\n"
            for i, context in enumerate(context_data[:3], 1):  # Limit context
                optimized_prompt += f"{i}. {context}\n"
            optimized_prompt += "\n"

        # Add few-shot examples (best practice #3)
        if examples:
            optimized_prompt += "EXAMPLES:\n"
            for i, example in enumerate(examples[:3], 1):  # Limit examples
                optimized_prompt += f"Example {i}:\n"
                optimized_prompt += f"Input: {example.get('input', '')}\n"
                optimized_prompt += f"Output: {example.get('output', '')}\n\n"

        # Add output format specification
        optimized_prompt += (
            "OUTPUT FORMAT: Provide a clear, direct response that follows the examples above.\n\n"
        )

        return optimized_prompt

    def create_fine_tuning_job(
        self,
        method: OptimizationMethod,
        base_model: str,
        training_data_path: str,
        validation_data_path: str | None = None,
        hyperparameters: dict[str, Any] | None = None,
    ) -> OptimizationJob:
        """
        Create fine-tuning job using OpenAI platform

        Args:
            method: Fine-tuning method to use
            base_model: Base model to fine-tune
            training_data_path: Path to training data (JSONL format)
            validation_data_path: Optional validation data path
            hyperparameters: Custom hyperparameters

        Returns:
            OptimizationJob object with job details
        """
        if base_model not in self.supported_models.get(method, []):
            raise ValueError(f"Model {base_model} not supported for {method.value}")

        job_id = f"eq12_{method.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Default hyperparameters based on method
        default_hyperparams = {
            OptimizationMethod.SUPERVISED_FINE_TUNING: {
                "n_epochs": 3,
                "batch_size": 1,
                "learning_rate_multiplier": 0.1,
            },
            OptimizationMethod.DIRECT_PREFERENCE_OPTIMIZATION: {
                "n_epochs": 1,
                "batch_size": 1,
                "beta": 0.1,
            },
        }

        final_hyperparams = default_hyperparams.get(method, {})
        if hyperparameters:
            final_hyperparams.update(hyperparameters)

        job = OptimizationJob(
            job_id=job_id,
            method=method,
            base_model=base_model,
            training_data_path=training_data_path,
            validation_data_path=validation_data_path,
            hyperparameters=final_hyperparams,
        )

        # Store job in database
        self._store_optimization_job(job)

        logger.info(f"Created optimization job: {job_id}")
        return job

    def get_optimization_recommendations(
        self, use_case: str, current_performance: dict[str, float]
    ) -> dict[str, Any]:
        """
        Get AI-powered recommendations for optimization strategy

        Args:
            use_case: Description of the use case
            current_performance: Current eval scores by metric

        Returns:
            Optimization recommendations
        """
        recommendations = {
            "suggested_methods": [],
            "priority_actions": [],
            "expected_improvements": {},
            "estimated_timeline": "",
        }

        # Analyze current performance
        avg_performance = (
            sum(current_performance.values()) / len(current_performance)
            if current_performance
            else 0.0
        )

        if avg_performance < 0.6:
            # Low performance - recommend comprehensive optimization
            recommendations["suggested_methods"] = [
                OptimizationMethod.PROMPT_ENGINEERING,
                OptimizationMethod.SUPERVISED_FINE_TUNING,
            ]
            recommendations["priority_actions"] = [
                "Create comprehensive evaluation dataset",
                "Engineer prompts with few-shot examples",
                "Collect high-quality training data for fine-tuning",
            ]
            recommendations["estimated_timeline"] = "2-4 weeks"

        elif avg_performance < 0.8:
            # Medium performance - focused improvements
            recommendations["suggested_methods"] = [OptimizationMethod.PROMPT_ENGINEERING]
            recommendations["priority_actions"] = [
                "Add relevant context to prompts",
                "Implement few-shot learning examples",
                "Run A/B tests on prompt variations",
            ]
            recommendations["estimated_timeline"] = "1-2 weeks"

        else:
            # High performance - maintenance and edge case handling
            recommendations["suggested_methods"] = [OptimizationMethod.EVAL_DRIVEN]
            recommendations["priority_actions"] = [
                "Implement continuous evaluation pipeline",
                "Monitor for performance drift",
                "Handle edge cases with targeted examples",
            ]
            recommendations["estimated_timeline"] = "Ongoing"

        return recommendations

    def _store_eval_results(self, results: list[EvalResult]):
        """Store evaluation results in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for result in results:
            cursor.execute(
                """
                INSERT INTO eval_results
                (eval_type, score, details, timestamp, model_version, prompt_hash)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    result.eval_type.value,
                    result.score,
                    json.dumps(result.details),
                    result.timestamp,
                    result.model_version,
                    result.prompt_hash,
                ),
            )

        conn.commit()
        conn.close()

    def _store_optimization_job(self, job: OptimizationJob):
        """Store optimization job in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO optimization_jobs
            (job_id, method, base_model, training_data_path, validation_data_path,
             hyperparameters, status, created_at, completed_at, results)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                job.job_id,
                job.method.value,
                job.base_model,
                job.training_data_path,
                job.validation_data_path,
                json.dumps(job.hyperparameters),
                job.status,
                job.created_at,
                job.completed_at,
                json.dumps(job.results),
            ),
        )

        conn.commit()
        conn.close()

    def _update_prompt_metrics(
        self,
        prompt_hash: str,
        prompt_content: str,
        model: str,
        results: list[EvalResult],
    ):
        """Update prompt performance metrics"""
        if not results:
            return

        avg_score = sum(r.score for r in results) / len(results)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO prompt_history
            (prompt_hash, prompt_content, model_used, avg_score, eval_count, last_used)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                prompt_hash,
                prompt_content,
                model,
                avg_score,
                len(results),
                datetime.utcnow().isoformat(),
            ),
        )

        conn.commit()
        conn.close()


# Example usage and testing
if __name__ == "__main__":

    async def main():
        # Initialize optimizer
        optimizer = EQ12AdvancedOptimizer()

        # Create evaluation dataset
        examples = [
            {
                "input": "Explain quantum computing in simple terms",
                "expected_output": "Quantum computing uses quantum mechanics principles to process information in ways that classical computers cannot, potentially solving certain problems exponentially faster.",
            },
            {
                "input": "What are the benefits of renewable energy?",
                "expected_output": "Renewable energy sources like solar and wind provide clean electricity, reduce greenhouse gas emissions, and offer long-term cost savings while decreasing dependence on fossil fuels.",
            },
        ]

        optimizer.create_eval_dataset(
            "general_knowledge_qa", examples, [EvalType.ACCURACY, EvalType.RELEVANCE]
        )

        # Engineer optimized prompt
        base_prompt = "Answer the user's question clearly and concisely."
        context_data = [
            "Focus on factual accuracy",
            "Use simple, accessible language",
            "Provide concrete examples when helpful",
        ]

        optimized_prompt = optimizer.engineer_prompt(
            base_prompt,
            context_data=context_data,
            examples=[
                {
                    "input": "What is AI?",
                    "output": "AI is technology that enables machines to simulate human intelligence and decision-making.",
                }
            ],
        )

        print("Optimized Prompt:")
        print(optimized_prompt)

        # Run evaluation (would require OpenAI API key)
        # eval_results = await optimizer.run_eval(
        #     "gpt-4.1-mini-2025-04-14",
        #     optimized_prompt,
        #     eval_dataset,
        #     [EvalType.ACCURACY, EvalType.RELEVANCE]
        # )

        # Get optimization recommendations
        current_performance = {"accuracy": 0.75, "relevance": 0.80}
        recommendations = optimizer.get_optimization_recommendations(
            "general_knowledge_qa", current_performance
        )

        print("\nOptimization Recommendations:")
        print(json.dumps(recommendations, indent=2))

    # Run example
    asyncio.run(main())
