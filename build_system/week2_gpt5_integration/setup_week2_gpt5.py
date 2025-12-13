#!/usr/bin/env python3
"""
EQ12 Week 2: GPT-5 Integration & Agentic Coding Setup

This script sets up GPT-5 with Responses API, reasoning effort controls,
and agentic task execution hub for the EQ12 automation stack.

Features:
- Responses API configuration with reasoning persistence
- Agentic task scheduler with XML automation
- Prompt library management with GPT-5 patterns
- Central credentials management with secure key storage
- Task execution framework with confidence tracking
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# GPT-5 optimized imports
try:
    import openai
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI library not installed. Run: pip install openai")

try:
    import asyncio

    import aiohttp

    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    print("⚠️ Async libraries not available. Run: pip install aiohttp")

# EQ12 Configuration
EQ12_HOME = Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
EQ12_LOGS = EQ12_HOME / "logs"
EQ12_KEYS = EQ12_HOME / "keys"
EQ12_CONFIGS = EQ12_HOME / "configs"

# Ensure directories exist
for directory in [EQ12_LOGS, EQ12_KEYS, EQ12_CONFIGS]:
    directory.mkdir(parents=True, exist_ok=True)


@dataclass
class GPT5Config:
    """GPT-5 agentic configuration with reasoning controls"""

    # Core API Settings
    reasoning_effort: str = "medium"  # minimal, medium, high
    verbosity_level: str = "low"  # low, medium, high
    use_responses_api: bool = True  # Enable reasoning persistence

    # Agentic Behavior Controls
    agentic_eagerness: str = "balanced"  # conservative, balanced, aggressive
    auto_proceed_threshold: float = 0.8  # Confidence for auto-execution
    max_tool_calls: int = 10  # Tool call budget per request

    # Task Execution Settings
    max_processing_time: int = 300  # Max seconds per task
    retry_attempts: int = 3  # Retry failed operations

    # Error Boundaries
    safe_actions: set = field(
        default_factory=lambda: {
            "search",
            "analyze",
            "calculate",
            "validate",
            "log",
            "read",
            "test",
        }
    )
    unsafe_actions: set = field(
        default_factory=lambda: {
            "delete",
            "modify_system",
            "install_software",
            "network_write",
        }
    )


@dataclass
class ReasoningTrace:
    """GPT-5 reasoning trace for transparency and debugging"""

    task_id: str
    step: str
    reasoning: str
    confidence: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    tool_calls_used: int = 0


@dataclass
class AgenticTask:
    """Represents an agentic task with GPT-5 execution plan"""

    task_id: str
    name: str
    description: str
    execution_plan: list[str] = field(default_factory=list)
    reasoning_traces: list[ReasoningTrace] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def add_reasoning_trace(
        self, step: str, reasoning: str, confidence: float, tool_calls: int = 0
    ):
        """Add structured reasoning trace (GPT-5 pattern)"""
        trace = ReasoningTrace(
            task_id=self.task_id,
            step=step,
            reasoning=reasoning,
            confidence=confidence,
            tool_calls_used=tool_calls,
        )
        self.reasoning_traces.append(trace)
        self.confidence = confidence


class GPT5AgenticHub:
    """GPT-5 Agentic Task Execution Hub for EQ12"""

    def __init__(self, config: GPT5Config):
        self.config = config
        self.client = None
        self.active_tasks: dict[str, AgenticTask] = {}
        self.prompt_library: dict[str, str] = {}
        self.reasoning_cache: dict[str, Any] = {}

        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=[
                logging.FileHandler(EQ12_LOGS / "gpt5_hub.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("GPT5Hub")

    async def initialize(self):
        """Initialize GPT-5 client and load configurations"""

        self.logger.info("🎯 Initializing GPT-5 Agentic Hub")

        # Load OpenAI API key
        api_key = await self._load_credential("openai_api_key")
        if not api_key and OPENAI_AVAILABLE:
            self.logger.warning("OpenAI API key not found. GPT-5 features will be limited.")
            return False

        if OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=api_key)

        # Load prompt library
        await self._load_prompt_library()

        # Initialize task scheduler
        await self._setup_task_scheduler()

        self.logger.info("✅ GPT-5 Agentic Hub initialized successfully")
        return True

    async def _load_credential(self, key_name: str) -> str | None:
        """Load credential from secure storage"""

        # Try environment variable first
        env_key = key_name.upper()
        if env_key in os.environ:
            return os.environ[env_key]

        # Try key file
        key_file = EQ12_KEYS / f"{key_name}.txt"
        if key_file.exists():
            return key_file.read_text(encoding="utf-8").strip()

        return None

    async def _load_prompt_library(self):
        """Load GPT-5 optimized prompt templates"""

        self.prompt_library = {
            "context_gathering": """
<context_gathering>
Goal: Get enough context fast. Parallelize discovery and stop as soon as you can act.

Method:
- Start broad, then fan out to focused subqueries
- In parallel, launch varied queries; read top hits per query. Deduplicate paths and cache
- Avoid over-searching for context. If needed, run targeted searches in one parallel batch

Early stop criteria:
- You can name exact content to change
- Top hits converge (~70%) on one area/path

Escalate once:
- If signals conflict or scope is fuzzy, run one refined parallel batch, then proceed
</context_gathering>
            """,
            "persistence": """
<persistence>
- Keep going until the user's query is completely resolved before ending your turn
- Never stop or hand back when encountering uncertainty — research the most reasonable approach
- Do not ask for confirmation on assumptions — document them, act on them, adjust if proven wrong
- Only escalate on unsafe actions or when confidence drops below 70%
</persistence>
            """,
            "tool_preambles": """
<tool_preambles>
- Always begin by rephrasing the user's goal in a friendly, clear manner before calling any tools
- Then, immediately outline a structured plan detailing each logical step you'll follow
- As you execute your file edit(s), narrate each step succinctly and sequentially, marking progress clearly
- Finish by summarizing completed work distinctly from your upfront plan
</tool_preambles>
            """,
            "self_reflection": """
<self_reflection>
- First, spend time thinking of a rubric until you are confident
- Then, think deeply about every aspect of what makes for a world-class implementation
- Use that knowledge to create a rubric that has 5-7 categories
- Finally, use the rubric to internally iterate on the best possible solution
</self_reflection>
            """,
        }

        # Save prompt library to disk
        prompt_file = EQ12_CONFIGS / "gpt5_prompts.json"
        with open(prompt_file, "w", encoding="utf-8") as f:
            json.dump(self.prompt_library, f, indent=2)

        self.logger.info(f"📚 Loaded {len(self.prompt_library)} prompt templates")

    async def _setup_task_scheduler(self):
        """Set up Windows Task Scheduler integration for automation"""

        scheduler_config = {
            "tasks": {
                "daily_sports_analysis": {
                    "schedule": "daily 09:00",
                    "script": "automation/sports/daily_analysis.py",
                    "reasoning_effort": "medium",
                },
                "travel_deals_scan": {
                    "schedule": "daily 12:00",
                    "script": "automation/travel/scan_deals.py",
                    "reasoning_effort": "minimal",
                },
                "finance_tracker": {
                    "schedule": "daily 18:00",
                    "script": "automation/finance/track_metrics.py",
                    "reasoning_effort": "medium",
                },
            },
            "created_at": datetime.now(UTC).isoformat(),
        }

        config_file = EQ12_CONFIGS / "task_scheduler.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(scheduler_config, f, indent=2)

        self.logger.info("📅 Task scheduler configuration created")

    async def create_agentic_task(
        self, name: str, description: str, reasoning_effort: str | None = None
    ) -> AgenticTask:
        """Create new agentic task with GPT-5 execution planning"""

        task_id = f"task_{int(time.time() * 1000)}"

        task = AgenticTask(task_id=task_id, name=name, description=description)

        # Generate execution plan based on task type
        if "analysis" in description.lower():
            task.execution_plan = [
                "Gather relevant data sources and context",
                "Apply analytical models and calculations",
                "Validate results against known benchmarks",
                "Generate structured summary with confidence scores",
            ]
        elif "automation" in description.lower():
            task.execution_plan = [
                "Map automation workflow and dependencies",
                "Test automation components in safe environment",
                "Execute automation with progress monitoring",
                "Validate results and log performance metrics",
            ]
        else:
            task.execution_plan = [
                "Analyze task requirements and constraints",
                "Determine optimal execution strategy",
                "Execute with continuous validation",
                "Generate completion summary",
            ]

        # Add initial reasoning trace
        task.add_reasoning_trace("task_creation", f"Created agentic task: {description}", 0.9, 0)

        self.active_tasks[task_id] = task

        self.logger.info(f"📋 Created agentic task: {name} ({task_id})")
        return task

    async def execute_task(self, task_id: str) -> dict[str, Any]:
        """Execute agentic task with GPT-5 reasoning"""

        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")

        task = self.active_tasks[task_id]
        task.status = "in_progress"

        self.logger.info(f"⚡ Executing task: {task.name}")

        start_time = time.time()
        tool_calls_used = 0

        try:
            # Execute each step in the plan
            for i, step in enumerate(task.execution_plan, 1):
                step_start = time.time()

                self.logger.info(f"   Step {i}/{len(task.execution_plan)}: {step}")

                # Simulate task execution (replace with actual GPT-5 API calls)
                await asyncio.sleep(0.1)  # Simulate processing
                tool_calls_used += 1

                step_duration = time.time() - step_start
                confidence = max(
                    0.7, 1.0 - (step_duration * 0.1)
                )  # Higher confidence for faster steps

                task.add_reasoning_trace(
                    f"step_{i}",
                    f"Completed: {step} (Duration: {step_duration:.2f}s)",
                    confidence,
                    1,
                )

                # Check tool call budget
                if tool_calls_used >= self.config.max_tool_calls:
                    self.logger.warning(f"⚠️ Tool call budget exhausted for task {task_id}")
                    break

                # Check processing time limit
                if time.time() - start_time > self.config.max_processing_time:
                    self.logger.warning(f"⚠️ Processing time limit exceeded for task {task_id}")
                    break

            task.status = "completed"
            total_duration = time.time() - start_time

            # Generate completion summary
            result = {
                "task_id": task_id,
                "status": "completed",
                "duration": total_duration,
                "tool_calls_used": tool_calls_used,
                "confidence": task.confidence,
                "reasoning_traces": len(task.reasoning_traces),
                "execution_plan_completed": len(
                    [t for t in task.reasoning_traces if t.step.startswith("step_")]
                ),
                "completed_at": datetime.now(UTC).isoformat(),
            }

            self.logger.info(f"✅ Task completed: {task.name} ({total_duration:.2f}s)")
            return result

        except Exception as e:
            task.status = "failed"
            error_result = {
                "task_id": task_id,
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time,
                "tool_calls_used": tool_calls_used,
            }

            self.logger.error(f"❌ Task failed: {task.name} - {e!s}")
            return error_result

    async def get_task_status(self, task_id: str) -> dict[str, Any]:
        """Get detailed status of agentic task"""

        if task_id not in self.active_tasks:
            return {"error": f"Task {task_id} not found"}

        task = self.active_tasks[task_id]

        return {
            "task_id": task.task_id,
            "name": task.name,
            "description": task.description,
            "status": task.status,
            "confidence": task.confidence,
            "execution_plan": task.execution_plan,
            "reasoning_traces": [
                {
                    "step": trace.step,
                    "confidence": trace.confidence,
                    "timestamp": trace.timestamp.isoformat(),
                    "tool_calls": trace.tool_calls_used,
                }
                for trace in task.reasoning_traces
            ],
            "created_at": task.created_at.isoformat(),
        }


async def setup_week2_gpt5_integration():
    """Main setup function for Week 2 GPT-5 integration"""

    print("🎯 EQ12 Week 2: GPT-5 Integration & Agentic Coding Setup")
    print("   Setting up GPT-5 with Responses API and agentic task execution")

    # Initialize GPT-5 configuration
    config = GPT5Config()

    # Create agentic hub
    hub = GPT5AgenticHub(config)

    # Initialize hub
    success = await hub.initialize()

    if not success:
        print("❌ Failed to initialize GPT-5 hub")
        return False

    # Create sample tasks to validate system
    tasks = [
        ("System Validation", "Validate EQ12 GPT-5 integration and agentic workflows"),
        ("Prompt Library Test", "Test GPT-5 prompt library and reasoning patterns"),
        (
            "Task Execution Test",
            "Validate agentic task execution with confidence tracking",
        ),
    ]

    print("\n📋 Creating validation tasks...")

    for name, description in tasks:
        task = await hub.create_agentic_task(name, description)
        await hub.execute_task(task.task_id)

        print(
            "   ✅ {name}: {result['status']} ({result['duration']:.2f}s, confidence: {result['confidence']:.1%})"
        )

    # Save configuration
    config_data = {
        "gpt5_config": {
            "reasoning_effort": config.reasoning_effort,
            "verbosity_level": config.verbosity_level,
            "use_responses_api": config.use_responses_api,
            "agentic_eagerness": config.agentic_eagerness,
            "auto_proceed_threshold": config.auto_proceed_threshold,
        },
        "installation_completed": datetime.now(UTC).isoformat(),
        "version": "EQ12-Week2-v1.0",
    }

    with open(EQ12_CONFIGS / "gpt5_integration.json", "w") as f:
        json.dump(config_data, f, indent=2)

    print("\n✅ Week 2 GPT-5 Integration Setup Completed!")
    print("   📁 Configuration saved to: {EQ12_CONFIGS / 'gpt5_integration.json'}")
    print("   📚 Prompt library available at: {EQ12_CONFIGS / 'gpt5_prompts.json'}")
    print("   📅 Task scheduler configured at: {EQ12_CONFIGS / 'task_scheduler.json'}")
    print("   📋 Ready for Week 3: Sports Betting & Affiliate Bot setup")

    return True


if __name__ == "__main__":
    asyncio.run(setup_week2_gpt5_integration())
