#!/usr/bin/env python3
"""
EQ12 Groq Engine
High-speed inference controller with real-time performance monitoring.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from dataclasses import dataclass

# Groq SDK
try:
    from groq import Groq
except ImportError:
    Groq = None

# OpenAI fallback
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\groq_engine.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class InferenceMetrics:
    """Inference performance metrics"""
    model: str
    latency_ms: float
    tokens_input: int
    tokens_output: int
    cost_estimate: float
    timestamp: str
    success: bool
    error_message: str | None = None


class EQ12GroqEngine:
    """High-speed AI inference engine with intelligent routing"""
    
    def __init__(self, workspace_path: str = "C:\\EQ12"):
        self.workspace_path = Path(workspace_path)
        self.metrics_db_path = self.workspace_path / "data" / "groq_metrics.db"
        self.cache_path = self.workspace_path / "data" / "groq_cache.json"
        
        # Create directories
        for path in [
            self.workspace_path / "data",
            self.workspace_path / "logs" / "groq"
        ]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Initialize clients
        self.groq_client = None
        self.openai_client = None
        self.init_clients()
        
        # Performance tracking
        self.metrics_history = []
        self.model_performance = {}
        
        # Configuration
        self.config = {
            "groq_models": [
                "llama-3.1-8b-instant",
                "llama3-groq-70b-8192-tool-use-preview",
                "llama3-groq-8b-8192-tool-use-preview"
            ],
            "fallback_models": [
                "gpt-4o-mini",
                "gpt-3.5-turbo"
            ],
            "latency_threshold_ms": 1000,
            "max_retries": 3,
            "cache_ttl_hours": 6
        }
        
        # Load cached performance data
        self.load_performance_cache()
        
        logger.info("EQ12 Groq Engine initialized")

    def init_clients(self):
        """Initialize AI clients"""
        try:
            # Initialize Groq client
            groq_key = os.getenv("GROQ_API_KEY")
            if groq_key and Groq:
                self.groq_client = Groq(api_key=groq_key)
                logger.info("Groq client initialized")
            else:
                logger.warning("Groq client not available (missing key or SDK)")
            
            # Initialize OpenAI client
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key and OpenAI:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("OpenAI fallback client initialized")
            else:
                logger.warning("OpenAI fallback not available")
                
        except Exception as e:
            logger.error(f"Client initialization failed: {e}")

    def load_performance_cache(self):
        """Load cached model performance data"""
        try:
            if self.cache_path.exists():
                with open(self.cache_path, 'r') as f:
                    self.model_performance = json.load(f)
                logger.info("Performance cache loaded")
        except Exception as e:
            logger.warning(f"Failed to load performance cache: {e}")
            self.model_performance = {}

    def save_performance_cache(self):
        """Save model performance data to cache"""
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(self.model_performance, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save performance cache: {e}")

    def select_optimal_model(self, task_type: str = "general") -> str:
        """Select optimal model based on task type and performance history"""
        try:
            # Task-specific model selection
            if task_type in ["live_odds", "real_time", "streaming"]:
                # Prefer fastest models for real-time tasks
                candidates = [
                    "llama-3.1-8b-instant",
                    "llama3-groq-8b-8192-tool-use-preview"
                ]
            elif task_type in ["analysis", "complex_reasoning"]:
                # Prefer larger models for complex tasks
                candidates = [
                    "llama3-groq-70b-8192-tool-use-preview",
                    "llama-3.1-8b-instant"
                ]
            else:
                # Default candidates
                candidates = self.config["groq_models"]
            
            # Filter by availability and performance
            best_model = None
            best_score = float('inf')
            
            for model in candidates:
                if model in self.model_performance:
                    perf = self.model_performance[model]
                    
                    # Calculate performance score (lower is better)
                    avg_latency = perf.get("avg_latency_ms", 1000)
                    error_rate = perf.get("error_rate", 0.1)
                    
                    # Heavily penalize errors
                    score = avg_latency + (error_rate * 10000)
                    
                    if score < best_score:
                        best_score = score
                        best_model = model
            
            # Default to best general model if no performance data
            return best_model or "llama-3.1-8b-instant"
            
        except Exception as e:
            logger.error(f"Model selection failed: {e}")
            return "llama-3-70b-8192"

    async def groq_inference(
        self, prompt: str, model: str | None = None, **kwargs
    ):
        """Execute inference using Groq with performance tracking"""
        if not self.groq_client:
            raise Exception("Groq client not available")
        
        if not model:
            model = self.select_optimal_model(kwargs.get("task_type", "general"))
        
        start_time = time.time()
        
        try:
            # Prepare messages
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            else:
                messages = prompt
            
            # Execute inference
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1024),
                temperature=kwargs.get("temperature", 0.7),
                stream=kwargs.get("stream", False)
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response
            if kwargs.get("stream", False):
                # Handle streaming response
                content = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                
                result = {
                    "content": content,
                    "model": model,
                    "latency_ms": latency_ms,
                    "provider": "groq",
                    "success": True
                }
            else:
                # Handle regular response
                result = {
                    "content": response.choices[0].message.content,
                    "model": model,
                    "latency_ms": latency_ms,
                    "provider": "groq",
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "success": True
                }
            
            # Record metrics
            metrics = InferenceMetrics(
                model=model,
                latency_ms=latency_ms,
                tokens_input=result.get("usage", {}).get("prompt_tokens", 0),
                tokens_output=result.get("usage", {}).get("completion_tokens", 0),
                cost_estimate=self.estimate_cost(result.get("usage", {}), "groq"),
                timestamp=datetime.now(timezone.utc).isoformat(),
                success=True
            )
            
            self.record_metrics(metrics)
            
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            
            # Record failed metrics
            metrics = InferenceMetrics(
                model=model,
                latency_ms=latency_ms,
                tokens_input=0,
                tokens_output=0,
                cost_estimate=0.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
                success=False,
                error_message=str(e)
            )
            
            self.record_metrics(metrics)
            
            raise Exception(f"Groq inference failed: {e}")

    async def openai_fallback(
        self, prompt: str, model: str = "gpt-4o-mini", **kwargs
    ):
        """Fallback to OpenAI when Groq is unavailable"""
        if not self.openai_client:
            raise Exception("OpenAI fallback not available")
        
        start_time = time.time()
        
        try:
            # Prepare messages
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            else:
                messages = prompt
            
            # Execute inference
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1024),
                temperature=kwargs.get("temperature", 0.7)
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            result = {
                "content": response.choices[0].message.content,
                "model": model,
                "latency_ms": latency_ms,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "success": True
            }
            
            # Record metrics
            metrics = InferenceMetrics(
                model=model,
                latency_ms=latency_ms,
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                cost_estimate=self.estimate_cost(response.usage.__dict__, "openai"),
                timestamp=datetime.now(timezone.utc).isoformat(),
                success=True
            )
            
            self.record_metrics(metrics)
            
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            
            # Record failed metrics
            metrics = InferenceMetrics(
                model=model,
                latency_ms=latency_ms,
                tokens_input=0,
                tokens_output=0,
                cost_estimate=0.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
                success=False,
                error_message=str(e)
            )
            
            self.record_metrics(metrics)
            
            raise Exception(f"OpenAI fallback failed: {e}")

    async def smart_inference(
        self, prompt: str, task_type: str = "general", **kwargs
    ):
        """Intelligent inference with automatic provider selection and fallback"""
        try:
            # Try Groq first for speed-sensitive tasks
            if (task_type in ["live_odds", "real_time", "streaming"]
                    and self.groq_client):
                try:
                    return await self.groq_inference(
                        prompt, task_type=task_type, **kwargs
                    )
                except Exception as e:
                    logger.warning(
                        f"Groq inference failed, falling back to OpenAI: {e}"
                    )
            
            # For complex tasks, might prefer OpenAI
            elif (task_type in ["complex_analysis", "financial_modeling"]
                  and self.openai_client):
                try:
                    return await self.openai_fallback(
                        prompt, model="gpt-4o", **kwargs
                    )
                except Exception as e:
                    logger.warning(f"OpenAI primary failed, trying Groq: {e}")
                    return await self.groq_inference(
                        prompt, task_type=task_type, **kwargs
                    )
            
            # Default: try Groq first, fallback to OpenAI
            else:
                if self.groq_client:
                    try:
                        return await self.groq_inference(
                            prompt, task_type=task_type, **kwargs
                        )
                    except Exception as e:
                        logger.warning(
                            f"Groq failed, falling back to OpenAI: {e}"
                        )
                        return await self.openai_fallback(prompt, **kwargs)
                else:
                    return await self.openai_fallback(prompt, **kwargs)
                    
        except Exception as e:
            logger.error(f"All inference providers failed: {e}")
            raise

    def estimate_cost(self, usage, provider: str) -> float:
        """Estimate inference cost based on usage"""
        try:
            if provider == "groq":
                # Groq pricing (approximate)
                input_cost_per_1k = 0.0015
                output_cost_per_1k = 0.002
            else:  # openai
                # OpenAI pricing (approximate)
                input_cost_per_1k = 0.0015  # GPT-4o-mini
                output_cost_per_1k = 0.006
            
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            cost = (input_tokens / 1000 * input_cost_per_1k +
                    output_tokens / 1000 * output_cost_per_1k)
            
            return round(cost, 6)
            
        except Exception as e:
            logger.error(f"Cost estimation failed: {e}")
            return 0.0

    def record_metrics(self, metrics: InferenceMetrics):
        """Record performance metrics"""
        try:
            # Add to history
            self.metrics_history.append(metrics)
            
            # Keep only recent metrics (last 1000)
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            # Update model performance summary
            model = metrics.model
            if model not in self.model_performance:
                self.model_performance[model] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "total_latency_ms": 0,
                    "total_cost": 0,
                    "last_updated": metrics.timestamp
                }
            
            perf = self.model_performance[model]
            perf["total_requests"] += 1
            perf["total_latency_ms"] += metrics.latency_ms
            perf["total_cost"] += metrics.cost_estimate
            perf["last_updated"] = metrics.timestamp
            
            if metrics.success:
                perf["successful_requests"] += 1
            
            # Calculate derived metrics
            perf["avg_latency_ms"] = (
                perf["total_latency_ms"] / perf["total_requests"]
            )
            perf["error_rate"] = (
                1 - (perf["successful_requests"] / perf["total_requests"])
            )
            
            # Save to cache periodically
            if perf["total_requests"] % 10 == 0:
                self.save_performance_cache()
            
            # Log daily usage
            self.log_daily_usage(metrics)
            
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")

    def log_daily_usage(self, metrics: InferenceMetrics):
        """Log daily usage statistics"""
        try:
            date = datetime.now().strftime('%Y%m%d')
            log_file = self.workspace_path / "logs" / "groq" / f"usage_{date}.json"
            
            # Load existing log
            if log_file.exists():
                with open(log_file, 'r') as f:
                    daily_log = json.load(f)
            else:
                daily_log = {
                    "date": date,
                    "total_requests": 0,
                    "total_cost": 0,
                    "models": {}
                }
            
            # Update log
            daily_log["total_requests"] += 1
            daily_log["total_cost"] += metrics.cost_estimate
            
            if metrics.model not in daily_log["models"]:
                daily_log["models"][metrics.model] = {
                    "requests": 0,
                    "avg_latency": 0,
                    "total_cost": 0
                }
            
            model_stats = daily_log["models"][metrics.model]
            model_stats["requests"] += 1
            model_stats["total_cost"] += metrics.cost_estimate
            
            # Update average latency
            total_latency = model_stats["avg_latency"] * (model_stats["requests"] - 1) + metrics.latency_ms
            model_stats["avg_latency"] = total_latency / model_stats["requests"]
            
            # Save log
            with open(log_file, 'w') as f:
                json.dump(daily_log, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log daily usage: {e}")

    async def benchmark_models(self):
        """Benchmark all available models"""
        logger.info("Starting model benchmark...")
        
        test_prompt = (
            "Analyze this MLB game for betting value: "
            "Dodgers vs Yankees, Dodgers -150 ML."
        )
        benchmark_results = {}
        
        # Test Groq models
        if self.groq_client:
            for model in self.config["groq_models"]:
                try:
                    logger.info(f"Benchmarking {model}...")
                    result = await self.groq_inference(test_prompt, model=model)
                    
                    benchmark_results[model] = {
                        "provider": "groq",
                        "latency_ms": result["latency_ms"],
                        "success": True,
                        "response_length": len(result["content"])
                    }
                    
                except Exception as e:
                    benchmark_results[model] = {
                        "provider": "groq",
                        "success": False,
                        "error": str(e)
                    }
                
                # Small delay between tests
                await asyncio.sleep(1)
        
        # Test OpenAI fallback models
        if self.openai_client:
            for model in self.config["fallback_models"]:
                try:
                    logger.info(f"Benchmarking {model}...")
                    result = await self.openai_fallback(test_prompt, model=model)
                    
                    benchmark_results[model] = {
                        "provider": "openai",
                        "latency_ms": result["latency_ms"],
                        "success": True,
                        "response_length": len(result["content"])
                    }
                    
                except Exception as e:
                    benchmark_results[model] = {
                        "provider": "openai",
                        "success": False,
                        "error": str(e)
                    }
                
                await asyncio.sleep(1)
        
        # Save benchmark results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        benchmark_file = (
            self.workspace_path / "logs" / "groq" / f"benchmark_{timestamp}.json"
        )
        with open(benchmark_file, 'w') as f:
            json.dump(benchmark_results, f, indent=2)
        
        logger.info(f"Benchmark completed, results saved to {benchmark_file}")
        return benchmark_results

    def get_performance_report(self):
        """Generate comprehensive performance report"""
        try:
            report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "models": {},
                "summary": {
                    "total_requests": sum(len(self.metrics_history)),
                    "avg_latency_ms": 0,
                    "total_cost": 0,
                    "success_rate": 0
                }
            }
            
            # Model-specific performance
            for model, perf in self.model_performance.items():
                report["models"][model] = {
                    "requests": perf["total_requests"],
                    "avg_latency_ms": round(perf["avg_latency_ms"], 2),
                    "success_rate": round(1 - perf["error_rate"], 3),
                    "total_cost": round(perf["total_cost"], 4),
                    "last_used": perf["last_updated"]
                }
            
            # Overall summary
            if self.model_performance:
                total_requests = sum(p["total_requests"] for p in self.model_performance.values())
                total_latency = sum(p["total_latency_ms"] for p in self.model_performance.values())
                total_cost = sum(p["total_cost"] for p in self.model_performance.values())
                successful_requests = sum(p["successful_requests"] for p in self.model_performance.values())
                
                report["summary"] = {
                    "total_requests": total_requests,
                    "avg_latency_ms": round(total_latency / total_requests, 2) if total_requests > 0 else 0,
                    "total_cost": round(total_cost, 4),
                    "success_rate": round(successful_requests / total_requests, 3) if total_requests > 0 else 0
                }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return {"error": str(e)}

    async def health_monitor(self):
        """Continuous health monitoring"""
        logger.info("Starting Groq engine health monitoring...")
        
        while True:
            try:
                # Test a simple inference
                test_result = await self.smart_inference(
                    "Test message. Respond with 'OK'.",
                    task_type="health_check",
                    max_tokens=10
                )
                
                if test_result["success"]:
                    if test_result["latency_ms"] > self.config["latency_threshold_ms"]:
                        logger.warning(f"High latency detected: {test_result['latency_ms']:.0f}ms")
                        # Could send Telegram alert here
                else:
                    logger.error("Health check failed")
                
                # Generate performance report
                if datetime.now().hour == 9 and datetime.now().minute < 5:  # Daily at 9 AM
                    report = self.get_performance_report()
                    report_file = self.workspace_path / "reports" / f"groq_performance_{datetime.now().strftime('%Y%m%d')}.json"
                    report_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(report_file, 'w') as f:
                        json.dump(report, f, indent=2)
                
                # Sleep between health checks
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(600)  # Wait longer on error


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="EQ12 Groq Engine")
    parser.add_argument("--workspace", default="C:\\EQ12", help="Workspace path")
    parser.add_argument("--benchmark", action="store_true", help="Run model benchmark")
    parser.add_argument("--report", action="store_true", help="Generate performance report")
    parser.add_argument("--monitor", action="store_true", help="Run health monitoring")
    parser.add_argument("--test", help="Test inference with prompt")
    
    args = parser.parse_args()
    
    engine = EQ12GroqEngine(args.workspace)
    
    if args.benchmark:
        async def run_benchmark():
            results = await engine.benchmark_models()
            print(json.dumps(results, indent=2))
        asyncio.run(run_benchmark())
        return 0
    
    if args.report:
        report = engine.get_performance_report()
        print(json.dumps(report, indent=2))
        return 0
    
    if args.test:
        async def test_inference():
            result = await engine.smart_inference(args.test)
            print(json.dumps(result, indent=2))
        asyncio.run(test_inference())
        return 0
    
    if args.monitor:
        try:
            asyncio.run(engine.health_monitor())
        except KeyboardInterrupt:
            logger.info("Health monitoring stopped")
        except Exception as e:
            logger.error(f"Health monitoring failed: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())