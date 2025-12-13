#!/usr/bin/env python3
"""
EQ12 Job Scheduler & Runner
===========================

Production scheduler implementing the tight runbook cadence:
- Odds polling: 30-60s (tighten to 10-15s inside T-10m)
- Steam scan & alerts: 30s
- Settlement & CLV: 15-30m; full sweep post-slate
- Health/data quality: 1-5m

YAML/JSON configurable with exact parameters from runbook.
"""

import asyncio
import json
import logging
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from models.eq12_client import EQ12Config, EQ12ModelClient

from eq12_api_client import BookMaker, create_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/eq12_scheduler.log"),
        logging.StreamHandler(),
    ],
)


@dataclass
class JobConfig:
    """Job configuration from YAML/JSON"""

    name: str
    enabled: bool
    interval_seconds: int
    function: str
    params: dict[str, Any]
    description: str
    priority: int = 1
    timeout_seconds: int = 60
    retry_count: int = 3
    retry_delay: int = 5


@dataclass
class JobResult:
    """Job execution result"""

    job_name: str
    success: bool
    duration_ms: int
    timestamp: datetime
    data: dict | None = None
    error: str | None = None


class EQ12Scheduler:
    """
    Production job scheduler for EQ12 runbook
    Handles multiple job types with different cadences and priorities
    """

    def __init__(self, config_path: str):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.jobs: dict[str, JobConfig] = {}
        self.job_states: dict[str, dict] = {}
        self.running = False
        self.client = None
        self.executor = ThreadPoolExecutor(max_workers=8)

        # Load configuration
        self.load_config()

        # Initialize API client
        try:
            self.client = create_client()
            self.logger.info("✅ EQ12 API client initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize API client: {e}")
            raise

        # Initialize AI model client with EQ12 constraints
        try:
            model_config = EQ12Config(
                allowed_books=["draftkings", "fanduel", "betmgm"],
                min_ev_threshold=0.025,  # 2.5% minimum edge
                kelly_cap_per_leg=0.025,  # 2.5% Kelly cap per leg
                max_correlation_risk=0.15,  # Low correlation tolerance
                stale_data_threshold_minutes=15,  # Fresh data only
            )
            self.model_client = EQ12ModelClient(model_config)
            self.logger.info("🤖 EQ12 AI model client initialized")
        except Exception as e:
            self.logger.warning(f"⚠️ AI model client initialization failed: {e}")
            self.model_client = None

        # Job execution tracking
        self.job_results: list[JobResult] = []
        self.max_results_history = 10000

        # Steam detection state
        self.previous_odds_data = {}
        self.steam_alerts = []

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def load_config(self):
        """Load job configuration from YAML/JSON"""
        config_file = Path(self.config_path)

        if not config_file.exists():
            self.logger.warning(f"Config file not found: {self.config_path}")
            self._create_default_config()
            return

        try:
            with open(config_file) as f:
                if config_file.suffix.lower() == ".yaml" or config_file.suffix.lower() == ".yml":
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)

            # Parse job configurations
            for job_data in config_data.get("jobs", []):
                job = JobConfig(**job_data)
                self.jobs[job.name] = job
                self.job_states[job.name] = {
                    "last_run": None,
                    "next_run": datetime.now(UTC),
                    "run_count": 0,
                    "error_count": 0,
                    "last_duration_ms": 0,
                }

            self.logger.info(f"📋 Loaded {len(self.jobs)} job configurations")

        except Exception as e:
            self.logger.error(f"❌ Failed to load config: {e}")
            raise

    def _create_default_config(self):
        """Create default configuration following runbook specs"""
        default_config = {
            "jobs": [
                {
                    "name": "api_heartbeat",
                    "enabled": True,
                    "interval_seconds": 300,  # 5m
                    "function": "heartbeat_check",
                    "params": {},
                    "description": "API health and quota monitoring",
                    "priority": 1,
                    "timeout_seconds": 30,
                },
                {
                    "name": "clock_sanity",
                    "enabled": True,
                    "interval_seconds": 60,  # 1m
                    "function": "clock_sanity_check",
                    "params": {},
                    "description": "Timezone and clock accuracy check",
                    "priority": 1,
                    "timeout_seconds": 15,
                },
                {
                    "name": "book_availability",
                    "enabled": True,
                    "interval_seconds": 180,  # 3m
                    "function": "book_availability_snapshot",
                    "params": {},
                    "description": "DK/FD/BetMGM availability monitoring",
                    "priority": 2,
                    "timeout_seconds": 45,
                },
                {
                    "name": "odds_polling_standard",
                    "enabled": True,
                    "interval_seconds": 45,  # 45s standard
                    "function": "odds_polling",
                    "params": {
                        "markets": ["h2h", "spreads", "totals"],
                        "time_window": "24h",
                    },
                    "description": "Standard odds polling (30-60s)",
                    "priority": 3,
                    "timeout_seconds": 60,
                },
                {
                    "name": "odds_polling_steam_window",
                    "enabled": True,
                    "interval_seconds": 15,  # 15s for games <10m to kickoff
                    "function": "steaming_window_polling",
                    "params": {
                        "markets": ["h2h", "spreads", "totals"],
                        "steam_window_minutes": 10,
                    },
                    "description": "High-frequency polling for steaming window",
                    "priority": 5,
                    "timeout_seconds": 30,
                },
                {
                    "name": "steam_detection",
                    "enabled": True,
                    "interval_seconds": 30,  # 30s steam scanning
                    "function": "steam_detection",
                    "params": {
                        "price_threshold": 10,
                        "point_threshold": 0.5,
                        "time_window_minutes": 10,
                    },
                    "description": "Line movement and steam alerts",
                    "priority": 4,
                    "timeout_seconds": 45,
                },
                {
                    "name": "value_hunting_moneylines",
                    "enabled": True,
                    "interval_seconds": 90,  # 1.5m
                    "function": "hunt_moneylines",
                    "params": {"min_ev_percent": 2.0},
                    "description": "Moneyline value opportunities",
                    "priority": 3,
                    "timeout_seconds": 60,
                },
                {
                    "name": "value_hunting_spread_hooks",
                    "enabled": True,
                    "interval_seconds": 120,  # 2m
                    "function": "hunt_spread_hooks",
                    "params": {
                        "min_ev_percent": 2.5,
                        "hook_numbers": [
                            -10.5,
                            -9.5,
                            -7.5,
                            -6.5,
                            -3.5,
                            -2.5,
                            -1.5,
                            -0.5,
                            0.5,
                            1.5,
                            2.5,
                            3.5,
                            6.5,
                            7.5,
                            9.5,
                            10.5,
                        ],
                    },
                    "description": "Spread hooks value hunting",
                    "priority": 3,
                    "timeout_seconds": 60,
                },
                {
                    "name": "value_hunting_total_hooks",
                    "enabled": True,
                    "interval_seconds": 120,  # 2m
                    "function": "hunt_total_hooks",
                    "params": {
                        "min_ev_percent": 2.5,
                        "hook_numbers": [
                            37.5,
                            38.5,
                            39.5,
                            40.5,
                            41.5,
                            42.5,
                            43.5,
                            44.5,
                            45.5,
                            46.5,
                            47.5,
                            48.5,
                            49.5,
                            50.5,
                            51.5,
                            52.5,
                        ],
                    },
                    "description": "Total hooks value hunting",
                    "priority": 3,
                    "timeout_seconds": 60,
                },
                {
                    "name": "parlay_builder_draftkings",
                    "enabled": True,
                    "interval_seconds": 180,  # 3m
                    "function": "build_book_parlays",
                    "params": {
                        "book": "draftkings",
                        "strategies": [
                            "balanced",
                            "conservative",
                            "spreads_only",
                            "totals_only",
                        ],
                    },
                    "description": "DraftKings parlay construction",
                    "priority": 2,
                    "timeout_seconds": 90,
                },
                {
                    "name": "parlay_builder_fanduel",
                    "enabled": True,
                    "interval_seconds": 180,  # 3m
                    "function": "build_book_parlays",
                    "params": {
                        "book": "fanduel",
                        "strategies": [
                            "balanced",
                            "conservative",
                            "spreads_only",
                            "totals_only",
                        ],
                    },
                    "description": "FanDuel parlay construction",
                    "priority": 2,
                    "timeout_seconds": 90,
                },
                {
                    "name": "parlay_builder_betmgm",
                    "enabled": True,
                    "interval_seconds": 180,  # 3m
                    "function": "build_book_parlays",
                    "params": {
                        "book": "betmgm",
                        "strategies": [
                            "balanced",
                            "conservative",
                            "spreads_only",
                            "totals_only",
                        ],
                    },
                    "description": "BetMGM parlay construction",
                    "priority": 2,
                    "timeout_seconds": 90,
                },
                {
                    "name": "settlement_and_clv",
                    "enabled": True,
                    "interval_seconds": 1200,  # 20m
                    "function": "settlement_and_clv",
                    "params": {"days_back": 2},
                    "description": "Settlement grading and CLV calculation",
                    "priority": 1,
                    "timeout_seconds": 120,
                },
                {
                    "name": "data_quality_check",
                    "enabled": True,
                    "interval_seconds": 180,  # 3m
                    "function": "data_quality_check",
                    "params": {
                        "stale_threshold_minutes": 3,
                        "missing_market_alert": True,
                    },
                    "description": "Data quality and ops monitoring",
                    "priority": 1,
                    "timeout_seconds": 60,
                },
            ]
        }

        # Save default config
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            if config_file.suffix.lower() in [".yaml", ".yml"]:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
            else:
                json.dump(default_config, f, indent=2)

        self.logger.info(f"📝 Created default configuration: {self.config_path}")

        # Load the default config
        for job_data in default_config["jobs"]:
            job = JobConfig(**job_data)
            self.jobs[job.name] = job
            self.job_states[job.name] = {
                "last_run": None,
                "next_run": datetime.now(UTC),
                "run_count": 0,
                "error_count": 0,
                "last_duration_ms": 0,
            }

    async def start(self):
        """Start the scheduler"""
        self.running = True
        self.logger.info("🚀 EQ12 Scheduler starting...")

        # Create tasks for each enabled job
        tasks = []
        for job_name, job in self.jobs.items():
            if job.enabled:
                task = asyncio.create_task(self._job_loop(job_name))
                tasks.append(task)

        self.logger.info(f"📊 Started {len(tasks)} job loops")

        # Run all jobs concurrently
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"❌ Scheduler error: {e}")
        finally:
            self.logger.info("🛑 Scheduler stopped")

    def stop(self):
        """Stop the scheduler gracefully"""
        self.running = False
        self.executor.shutdown(wait=True)
        self.logger.info("⏹️  Scheduler stop requested")

    async def _job_loop(self, job_name: str):
        """Main loop for individual jobs"""
        self.jobs[job_name]

        while self.running:
            try:
                now = datetime.now(UTC)
                next_run = self.job_states[job_name]["next_run"]

                if now >= next_run:
                    await self._execute_job(job_name)

                # Sleep for a short interval to avoid busy waiting
                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"❌ Job loop error for {job_name}: {e}")
                await asyncio.sleep(5)  # Back off on error

    async def _execute_job(self, job_name: str):
        """Execute a single job"""
        job = self.jobs[job_name]
        start_time = time.time()

        try:
            self.logger.info(f"▶️  Executing {job_name}")

            # Get job function and execute
            job_function = getattr(self, job.function, None)
            if not job_function:
                raise ValueError(f"Job function '{job.function}' not found")

            # Execute with timeout
            result_data = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(self.executor, job_function, job.params),
                timeout=job.timeout_seconds,
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Record successful execution
            result = JobResult(
                job_name=job_name,
                success=True,
                duration_ms=duration_ms,
                timestamp=datetime.now(UTC),
                data=result_data,
            )

            self._record_job_result(job_name, result)

            self.logger.info(f"✅ {job_name} completed in {duration_ms}ms")

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)

            # Record failed execution
            result = JobResult(
                job_name=job_name,
                success=False,
                duration_ms=duration_ms,
                timestamp=datetime.now(UTC),
                error=str(e),
            )

            self._record_job_result(job_name, result, error=True)

            self.logger.error(f"❌ {job_name} failed in {duration_ms}ms: {e}")

        # Update next run time
        self._schedule_next_run(job_name)

    def _record_job_result(self, job_name: str, result: JobResult, error: bool = False):
        """Record job execution result"""
        # Update job state
        self.job_states[job_name]["last_run"] = result.timestamp
        self.job_states[job_name]["run_count"] += 1
        self.job_states[job_name]["last_duration_ms"] = result.duration_ms

        if error:
            self.job_states[job_name]["error_count"] += 1

        # Add to results history
        self.job_results.append(result)

        # Trim history if too large
        if len(self.job_results) > self.max_results_history:
            self.job_results = self.job_results[-self.max_results_history :]

        # Save result to disk for important jobs
        if job_name in [
            "odds_polling_standard",
            "steam_detection",
            "settlement_and_clv",
        ]:
            self._save_job_result(result)

    def _schedule_next_run(self, job_name: str):
        """Schedule next run for a job"""
        job = self.jobs[job_name]
        now = datetime.now(UTC)

        # Adjust interval based on game timing for odds polling
        interval = job.interval_seconds

        if job_name == "odds_polling_steam_window":
            # Check if any games are in steaming window
            steaming_games = self._get_steaming_games()
            if not steaming_games:
                interval = 60  # Slower polling if no steaming games

        next_run = now + timedelta(seconds=interval)
        self.job_states[job_name]["next_run"] = next_run

    def _save_job_result(self, result: JobResult):
        """Save important job results to disk"""
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"C:/EQ12/logs/{result.job_name}_{timestamp}.json"

        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w") as f:
                json.dump(asdict(result), f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save job result: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"📡 Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    # =============================================================================
    # JOB IMPLEMENTATION FUNCTIONS
    # =============================================================================

    def heartbeat_check(self, params: dict) -> dict:
        """API heartbeat and quota check"""
        return self.client.heartbeat()

    def clock_sanity_check(self, params: dict) -> dict:
        """Clock and timezone sanity check"""
        return self.client.clock_sanity_check()

    def book_availability_snapshot(self, params: dict) -> dict:
        """Book availability monitoring"""
        return self.client.book_availability_snapshot()

    def odds_polling(self, params: dict) -> dict:
        """Standard odds polling for 24h slate with AI-powered odds normalization"""
        markets = params.get("markets", ["h2h", "spreads", "totals"])
        games = self.client.get_24h_slate()

        # Store current odds for movement detection
        current_odds = {}
        ai_normalized_odds = {}

        for game in games:
            current_odds[game.id] = game.bookmakers

            # AI-powered odds extraction and normalization
            if self.model_client:
                try:
                    # Convert raw bookmaker data to text format for AI processing
                    raw_odds_text = self._format_odds_for_ai(game)

                    # Extract and normalize odds using gpt-4o-mini
                    extraction_result = self.model_client.extract_odds(raw_odds_text)

                    if extraction_result["success"]:
                        ai_normalized_odds[game.id] = {
                            "extracted_odds": extraction_result["data"]["rows"],
                            "books_found": extraction_result["data"]["books_found"],
                            "model_info": {
                                "model_used": extraction_result["model_used"],
                                "tokens": extraction_result["tokens"],
                                "execution_time": extraction_result.get("execution_time", 0),
                            },
                        }
                        self.logger.debug(
                            f"🤖 AI extracted {len(extraction_result['data']['rows'])} odds for {game.id}"
                        )
                    else:
                        self.logger.warning(
                            f"⚠️ AI extraction failed for {game.id}: {extraction_result['error']}"
                        )

                except Exception as e:
                    self.logger.error(f"❌ AI odds processing error for {game.id}: {e}")

        # Update previous odds data for steam detection
        if hasattr(self, "previous_odds_data"):
            self.previous_odds_data.update(current_odds)
        else:
            self.previous_odds_data = current_odds

        # Include AI processing results in return data
        result = {
            "games_count": len(games),
            "markets": markets,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if ai_normalized_odds:
            result["ai_processing"] = {
                "games_processed": len(ai_normalized_odds),
                "total_odds_extracted": sum(
                    len(data["extracted_odds"]) for data in ai_normalized_odds.values()
                ),
                "normalized_odds": ai_normalized_odds,
            }
            self.logger.info(
                f"🤖 AI processed {len(ai_normalized_odds)} games with normalized odds"
            )

        return result

    def _format_odds_for_ai(self, game) -> str:
        """Format game odds data for AI processing"""
        odds_text = f"""
        {game.away_team} @ {game.home_team}
        Game Time: {game.commence_time.strftime("%Y-%m-%d %H:%M:%S UTC")}
        
        """

        for bookmaker in game.bookmakers:
            odds_text += f"{bookmaker.title}:\n"

            for market in bookmaker.markets:
                if market.key == "h2h":  # Moneyline
                    for outcome in market.outcomes:
                        odds_text += f"  {outcome.name}: {outcome.price:+d}\n"
                elif market.key == "spreads":  # Point spreads
                    for outcome in market.outcomes:
                        point = outcome.point if hasattr(outcome, "point") else 0
                        odds_text += f"  {outcome.name} {point:+.1f}: {outcome.price:+d}\n"
                elif market.key == "totals":  # Over/Under
                    for outcome in market.outcomes:
                        point = outcome.point if hasattr(outcome, "point") else 0
                        odds_text += f"  {outcome.name} {point}: {outcome.price:+d}\n"

            odds_text += "\n"

        return odds_text.strip()

    def _build_ai_parlays(
        self,
        odds_data: list,
        strategies: list,
        bankroll: float,
        min_ev: float,
        max_legs: int,
    ) -> dict:
        """Build parlays using AI reasoning with EQ12 constraints"""
        parlays = {}

        if not self.model_client or not odds_data:
            return {}

        for strategy in strategies:
            try:
                # AI-powered parlay construction using gpt-4o
                parlay_result = self.model_client.build_parlays(
                    odds_data=odds_data,
                    bankroll=bankroll,
                    min_ev=min_ev,
                    max_legs=max_legs,
                )

                if parlay_result["success"] and parlay_result["data"]["parlays"]:
                    strategy_parlays = parlay_result["data"]["parlays"]

                    # Filter based on strategy
                    if strategy == "conservative":
                        strategy_parlays = [
                            p
                            for p in strategy_parlays
                            if p.get("risk_assessment", {}).get("overall_risk") == "LOW"
                        ]
                    elif strategy == "spreads_only":
                        strategy_parlays = [
                            p
                            for p in strategy_parlays
                            if all(
                                "spread" in leg.get("market", "").lower()
                                for leg in p.get("legs", [])
                            )
                        ]
                    elif strategy == "totals_only":
                        strategy_parlays = [
                            p
                            for p in strategy_parlays
                            if all(
                                "total" in leg.get("market", "").lower()
                                for leg in p.get("legs", [])
                            )
                        ]

                    # Generate AI explanations for each parlay
                    for parlay in strategy_parlays:
                        try:
                            explanation_result = self.model_client.explain_parlay(parlay)
                            if explanation_result["success"]:
                                parlay["ai_explanation"] = explanation_result["explanation"]
                                parlay["explanation_model"] = explanation_result["model_used"]
                        except Exception as e:
                            self.logger.warning(f"AI explanation failed: {e}")

                    parlays[strategy] = {
                        "parlays": strategy_parlays,
                        "ai_model_info": {
                            "construction_model": parlay_result["model_used"],
                            "tokens_used": parlay_result["tokens"],
                            "execution_time": parlay_result.get("execution_time", 0),
                        },
                    }

                    self.logger.info(f"🤖 AI built {len(strategy_parlays)} {strategy} parlays")

                else:
                    self.logger.warning(
                        f"AI parlay construction failed for {strategy}: {parlay_result.get('error', 'Unknown error')}"
                    )

            except Exception as e:
                self.logger.error(f"❌ AI parlay construction error for {strategy}: {e}")

        return parlays

    def _build_traditional_parlays(self, book: BookMaker, strategies: list) -> dict:
        """Fallback to traditional parlay construction methods"""
        parlays = {}

        for strategy in strategies:
            try:
                if strategy == "balanced":
                    parlay = self.client.build_balanced_risk_parlay(book)
                elif strategy == "conservative":
                    parlay = self.client.build_conservative_high_ev_parlay(book)
                elif strategy == "spreads_only":
                    parlay = self.client.build_spreads_only_parlay(book)
                elif strategy == "totals_only":
                    parlay = self.client.build_totals_only_parlay(book)
                else:
                    continue

                parlays[strategy] = {
                    "parlays": [parlay] if parlay else [],
                    "method": "traditional_api",
                }

            except Exception as e:
                self.logger.error(f"Traditional parlay construction failed for {strategy}: {e}")

        return parlays

    def steaming_window_polling(self, params: dict) -> dict:
        """High-frequency polling for steaming window games"""
        steam_window_minutes = params.get("steam_window_minutes", 10)
        games = self.client.get_steaming_window()

        return {
            "steaming_games_count": len(games),
            "steam_window_minutes": steam_window_minutes,
            "games": [
                {
                    "id": g.id,
                    "home_team": g.home_team,
                    "away_team": g.away_team,
                    "commence_time": g.commence_time.isoformat(),
                }
                for g in games
            ],
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def steam_detection(self, params: dict) -> dict:
        """Detect line movements and steam"""
        price_threshold = params.get("price_threshold", 10)
        point_threshold = params.get("point_threshold", 0.5)

        # This would implement actual steam detection logic
        # For now, return placeholder structure

        steam_alerts = []  # Would be populated with actual steam detection

        return {
            "steam_alerts_count": len(steam_alerts),
            "price_threshold": price_threshold,
            "point_threshold": point_threshold,
            "alerts": steam_alerts,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def hunt_moneylines(self, params: dict) -> dict:
        """Hunt for moneyline value opportunities"""
        min_ev = params.get("min_ev_percent", 2.0)
        opportunities = self.client.get_moneylines_only()

        # Would apply model probabilities and filter by EV
        high_ev_opportunities = []  # Placeholder

        return {
            "total_opportunities": len(opportunities),
            "high_ev_opportunities": len(high_ev_opportunities),
            "min_ev_threshold": min_ev,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def hunt_spread_hooks(self, params: dict) -> dict:
        """Hunt for spread hook opportunities"""
        min_ev = params.get("min_ev_percent", 2.5)
        hook_numbers = params.get("hook_numbers", self.client.SPREAD_HOOKS)

        opportunities = self.client.get_spreads_with_hooks()

        return {
            "total_spread_opportunities": len(opportunities),
            "hook_numbers_tracked": len(hook_numbers),
            "min_ev_threshold": min_ev,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def hunt_total_hooks(self, params: dict) -> dict:
        """Hunt for total hook opportunities"""
        min_ev = params.get("min_ev_percent", 2.5)
        hook_numbers = params.get("hook_numbers", self.client.TOTAL_HOOKS)

        opportunities = self.client.get_totals_with_hooks()

        return {
            "total_opportunities": len(opportunities),
            "hook_numbers_tracked": len(hook_numbers),
            "min_ev_threshold": min_ev,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def build_book_parlays(self, params: dict) -> dict:
        """Build parlays for specific book with AI-powered reasoning"""
        book_name = params.get("book")
        strategies = params.get("strategies", ["balanced"])
        bankroll = params.get("bankroll", 1000)
        min_ev = params.get("min_ev", 0.025)
        max_legs = params.get("max_legs", 4)

        if not book_name:
            return {"error": "Book name required"}

        try:
            book = BookMaker(book_name)
        except ValueError:
            return {"error": f"Invalid book: {book_name}"}

        # Get current odds data for AI processing
        games = self.client.get_24h_slate()
        all_odds_data = []

        # Collect odds data from recent polling results
        for game in games:
            game_odds = self._format_odds_for_ai(game)
            if self.model_client:
                try:
                    extraction_result = self.model_client.extract_odds(game_odds)
                    if extraction_result["success"]:
                        all_odds_data.extend(extraction_result["data"]["rows"])
                except Exception as e:
                    self.logger.error(f"AI extraction error: {e}")

        # Filter odds for the specific book
        book_odds = [
            odds for odds in all_odds_data if odds.get("book", "").lower() == book_name.lower()
        ]

        if not book_odds:
            self.logger.warning(f"No odds found for book: {book_name}")
            # Fallback to original API method
            parlays = self._build_traditional_parlays(book, strategies)
        else:
            # AI-powered parlay construction
            parlays = self._build_ai_parlays(book_odds, strategies, bankroll, min_ev, max_legs)

        return {
            "book": book_name,
            "strategies_built": list(parlays.keys()),
            "parlays": parlays,
            "odds_data_points": len(book_odds),
            "ai_processing": bool(book_odds and self.model_client),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def settlement_and_clv(self, params: dict) -> dict:
        """Settlement grading and CLV calculation"""
        days_back = params.get("days_back", 2)
        scores_data = self.client.get_scores_for_settlement(days_back)

        # Would implement actual settlement logic

        return {
            "games_settled": scores_data.get("games_count", 0),
            "days_back": days_back,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def data_quality_check(self, params: dict) -> dict:
        """Data quality and operations monitoring"""
        stale_threshold = params.get("stale_threshold_minutes", 3)

        # Would implement stale data detection, missing markets, etc.

        return {
            "stale_threshold_minutes": stale_threshold,
            "issues_found": 0,  # Placeholder
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def _get_steaming_games(self) -> list:
        """Helper to get games in steaming window"""
        try:
            return self.client.get_steaming_window()
        except:
            return []

    def get_status(self) -> dict:
        """Get scheduler status and job statistics"""
        now = datetime.now(UTC)

        job_status = {}
        for job_name, state in self.job_states.items():
            job_status[job_name] = {
                "enabled": self.jobs[job_name].enabled,
                "last_run": state["last_run"].isoformat() if state["last_run"] else None,
                "next_run": state["next_run"].isoformat() if state["next_run"] else None,
                "run_count": state["run_count"],
                "error_count": state["error_count"],
                "last_duration_ms": state["last_duration_ms"],
                "time_until_next_run": (
                    (state["next_run"] - now).total_seconds() if state["next_run"] else None
                ),
            }

        return {
            "scheduler_running": self.running,
            "total_jobs": len(self.jobs),
            "enabled_jobs": len([j for j in self.jobs.values() if j.enabled]),
            "total_executions": sum(state["run_count"] for state in self.job_states.values()),
            "total_errors": sum(state["error_count"] for state in self.job_states.values()),
            "job_status": job_status,
            "timestamp": now.isoformat(),
        }


async def main():
    """Main entry point for scheduler"""
    config_path = "C:/EQ12/configs/eq12_scheduler_config.yaml"

    try:
        scheduler = EQ12Scheduler(config_path)
        await scheduler.start()
    except KeyboardInterrupt:
        print("\n🛑 Scheduler interrupted by user")
    except Exception as e:
        print(f"❌ Scheduler failed: {e}")
        logging.error(f"Fatal scheduler error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
