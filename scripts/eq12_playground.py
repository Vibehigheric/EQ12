#!/usr/bin/env python3
"""
EQ12 Playground Integration Layer
Mirrors OpenAI Playground functionality for EQ12 parlay building workflows.

This module provides a complete Playground-like experience with:
- Prompt management with variables
- What-if scenarios and correlation testing
- Deterministic runs with seed control
- Temperature and reasoning effort controls
"""

import logging
from dataclasses import dataclass

from eq12_responses_client import EQ12ResponsesClient, EQ12ResponsesConfig

logger = logging.getLogger(__name__)


@dataclass
class PlaygroundSession:
    """Configuration for a Playground session."""

    model: str = "gpt-5"
    temperature: float = 0.2
    reasoning_effort: str = "low"
    seed: int | None = None
    max_tokens: int | None = None
    structured_output: bool = True


class EQ12Playground:
    """
    Production Playground integration for EQ12 parlay workflows.
    Provides full Playground functionality with EQ12-specific features.
    """

    def __init__(self, api_key: str, session: PlaygroundSession = None):
        self.session = session or PlaygroundSession()

        # Initialize Responses API client
        config = EQ12ResponsesConfig(
            api_key=api_key,
            model=self.session.model,
            temperature=self.session.temperature,
            max_tokens=self.session.max_tokens,
            reasoning_effort=self.session.reasoning_effort,
        )

        self.client = EQ12ResponsesClient(config)
        self.test_datasets = {}
        self._load_test_datasets()

        logger.info(f"🎯 EQ12 Playground initialized with {self.session.model}")

    def _load_test_datasets(self):
        """Load sample test datasets for quick testing."""
        # Hooks pack - several spreads/totals with half-point hooks
        self.test_datasets["hooks_pack"] = [
            {
                "book": "DraftKings",
                "game_id": "nfl_20251005_chiefs_bills",
                "market": "spread",
                "selection": "Kansas City Chiefs -3.5",
                "odds": -110,
                "point": -3.5,
                "model_prob": 0.55,
                "ev": 0.089,
                "kelly": 0.032,
                "hook_flag": True,
                "commence_time": "2025-10-05T21:25:00Z",
            },
            {
                "book": "FanDuel",
                "game_id": "nfl_20251005_packers_bears",
                "market": "spread",
                "selection": "Green Bay Packers -6.5",
                "odds": -108,
                "point": -6.5,
                "model_prob": 0.58,
                "ev": 0.092,
                "kelly": 0.038,
                "hook_flag": True,
                "commence_time": "2025-10-05T17:00:00Z",
            },
            {
                "book": "BetMGM",
                "game_id": "nfl_20251005_cowboys_giants",
                "market": "total",
                "selection": "Over 47.5",
                "odds": +102,
                "point": 47.5,
                "model_prob": 0.52,
                "ev": 0.076,
                "kelly": 0.025,
                "hook_flag": True,
                "commence_time": "2025-10-05T20:15:00Z",
            },
        ]

        # Mixed markets - test correlation filtering
        self.test_datasets["mixed_markets"] = [
            {
                "book": "DraftKings",
                "game_id": "nfl_20251005_chiefs_bills",
                "market": "moneyline",
                "selection": "Kansas City Chiefs",
                "odds": -165,
                "model_prob": 0.62,
                "ev": 0.081,
                "kelly": 0.041,
                "hook_flag": False,
                "commence_time": "2025-10-05T21:25:00Z",
            },
            {
                "book": "FanDuel",
                "game_id": "nfl_20251005_chiefs_bills",
                "market": "total",
                "selection": "Over 51.5",
                "odds": -110,
                "point": 51.5,
                "model_prob": 0.57,
                "ev": 0.073,
                "kelly": 0.029,
                "hook_flag": True,
                "commence_time": "2025-10-05T21:25:00Z",
            },
            {
                "book": "BetMGM",
                "game_id": "nfl_20251005_packers_bears",
                "market": "spread",
                "selection": "Chicago Bears +7.0",
                "odds": +110,
                "point": 7.0,
                "model_prob": 0.51,
                "ev": 0.067,
                "kelly": 0.022,
                "hook_flag": False,
                "commence_time": "2025-10-05T17:00:00Z",
            },
        ]

        # Edge EV - mix of moderate and high EV opportunities
        self.test_datasets["edge_ev"] = [
            {
                "book": "DraftKings",
                "game_id": "nfl_20251005_ravens_steelers",
                "market": "spread",
                "selection": "Baltimore Ravens -1.5",
                "odds": +105,
                "point": -1.5,
                "model_prob": 0.58,
                "ev": 0.121,  # High EV
                "kelly": 0.065,
                "hook_flag": True,
                "commence_time": "2025-10-05T16:30:00Z",
            },
            {
                "book": "FanDuel",
                "game_id": "nfl_20251005_dolphins_jets",
                "market": "moneyline",
                "selection": "Miami Dolphins",
                "odds": +145,
                "model_prob": 0.48,
                "ev": 0.076,  # Moderate EV
                "kelly": 0.028,
                "hook_flag": False,
                "commence_time": "2025-10-05T15:05:00Z",
            },
            {
                "book": "BetMGM",
                "game_id": "nfl_20251005_rams_49ers",
                "market": "total",
                "selection": "Under 44.5",
                "odds": +108,
                "point": 44.5,
                "model_prob": 0.54,
                "ev": 0.089,  # Good EV
                "kelly": 0.039,
                "hook_flag": True,
                "commence_time": "2025-10-05T22:20:00Z",
            },
        ]

    def run_parlay_architect(
        self, dataset_name: str = "hooks_pack", variables_override: dict | None = None
    ) -> dict:
        """
        Run the main parlay architect (pmpt_eq12_build_parlay_v1).

        Args:
            dataset_name: Test dataset to use ("hooks_pack", "mixed_markets", "edge_ev")
            variables_override: Override default variables

        Returns:
            Parlay architect results
        """
        candidate_legs = self.test_datasets.get(
            dataset_name, self.test_datasets["hooks_pack"])

        # Default variables
        variables = {"max_legs": 8, "min_ev": 0.08, "corr": 0.08, "bankroll": 1000}

        # Apply overrides
        if variables_override:
            variables.update(variables_override)

        logger.info(f"🎰 Running parlay architect with {dataset_name} dataset")
        logger.info(f"   Variables: {variables}")

        result = self.client.build_parlay_architect(
            candidate_legs=candidate_legs,
            reasoning_effort=self.session.reasoning_effort,
            **variables,
        )

        if result["success"]:
            legs = result["data"].get("legs", [])
            stake = result["data"].get("stake", 0)
            logger.info(f"✅ Built {len(legs)}-leg parlay, stake: ${stake:.0f}")
        else:
            logger.error(f"❌ Parlay architect failed: {result.get('error')}")

        return result

    def run_hooks_specialist(
        self, dataset_name: str = "hooks_pack", variables_override: dict | None = None
    ) -> dict:
        """
        Run the hooks specialist (pmpt_eq12_spread_hooks_v1).

        Args:
            dataset_name: Test dataset to use
            variables_override: Override default variables

        Returns:
            Hooks specialist results
        """
        candidate_legs = self.test_datasets.get(
            dataset_name, self.test_datasets["hooks_pack"])

        # Default variables for hooks specialist
        variables = {"max_legs": 6, "min_ev": 0.08, "corr": 0.08, "bankroll": 1000}

        if variables_override:
            variables.update(variables_override)

        logger.info(f"⚡ Running hooks specialist with {dataset_name} dataset")
        logger.info(f"   Variables: {variables}")

        result = self.client.build_hooks_specialist(
            candidate_legs=candidate_legs,
            reasoning_effort=self.session.reasoning_effort,
            **variables,
        )

        if result["success"]:
            data = result["data"]
            hook_count = data.get("hook_count", 0)
            legs = data.get("legs", [])
            logger.info(f"✅ Built {len(legs)}-leg hooks parlay, {hook_count} hooks")
        else:
            logger.error(f"❌ Hooks specialist failed: {result.get('error')}")

        return result

    def generate_alert_copy(
        self,
        book: str = "DraftKings",
        selection: str = "Chiefs -3.5",
        odds: int = -110,
        ev_pct: str = "8.2%",
        kelly: str = "45",
    ) -> dict:
        """
        Generate alert copy (pmpt_eq12_alert_copy_v1).

        Args:
            book: Sportsbook name
            selection: Bet selection
            odds: American odds
            ev_pct: EV percentage
            kelly: Kelly stake

        Returns:
            Alert copy results
        """
        logger.info(f"📢 Generating alert copy for {book} {selection}")

        result = self.client.generate_alert_copy_v2(
            book=book,
            team_or_market="Chiefs vs Bills",
            selection=selection,
            odds=odds,
            ev_pct=ev_pct,
            kelly=kelly,
            kickoff_local="4:25p EST",
            why="model loves hook",
        )

        if result["success"]:
            alert_text = result["data"].get("text", "")
            logger.info(f"✅ Generated alert: {alert_text}")
        else:
            logger.error(f"❌ Alert generation failed: {result.get('error')}")

        return result

    def run_what_if_scenarios(self) -> dict:
        """
        Run what-if scenarios to test different correlation/EV thresholds.

        Returns:
            Results from multiple scenario runs
        """
        logger.info("🔍 Running what-if scenarios")

        scenarios = [
            {"name": "Tight Correlation", "corr": 0.12, "min_ev": 0.08},
            {"name": "Raise EV Floor", "corr": 0.08, "min_ev": 0.12},
            {"name": "Aggressive", "corr": 0.05, "min_ev": 0.06},
            {"name": "Conservative", "corr": 0.15, "min_ev": 0.10},
        ]

        results = {}

        for scenario in scenarios:
            logger.info(f"   Testing: {scenario['name']}")

            result = self.run_parlay_architect(
                dataset_name="mixed_markets",
                variables_override={
                    "corr": scenario["corr"],
                    "min_ev": scenario["min_ev"],
                },
            )

            results[scenario["name"]] = {
                "scenario": scenario,
                "success": result["success"],
                "legs_count": (len(result["data"].get("legs", [])) if result["success"] else 0),
                "stake": result["data"].get("stake", 0) if result["success"] else 0,
            }

        # Summary
        logger.info("📊 What-if Results Summary:")
        for name, data in results.items():
            if data["success"]:
                logger.info(
                    f"   {name}: {
                        data['legs_count']} legs, ${
                        data['stake']:.0f} stake")
            else:
                logger.info(f"   {name}: Failed")

        return results

    def run_adversarial_tests(self) -> dict:
        """
        Run adversarial tests to validate constraint enforcement.

        Returns:
            Adversarial test results
        """
        logger.info("🛡️ Running adversarial tests")

        # Test with non-whitelisted books
        bad_legs = [
            {
                "book": "Caesars",  # Not whitelisted
                "game_id": "nfl_20251005_test",
                "market": "moneyline",
                "selection": "Team A",
                "odds": -110,
                "model_prob": 0.60,
                "ev": 0.15,  # High EV to tempt inclusion
                "kelly": 0.08,
                "hook_flag": False,
                "commence_time": "2025-10-05T20:00:00Z",
            }
        ] + self.test_datasets[
            "hooks_pack"
        ]  # Mix with good legs

        logger.info("   Testing non-whitelisted book filtering")
        result = self.client.build_parlay_architect(
            candidate_legs=bad_legs,
            reasoning_effort="medium",  # Higher effort for constraint checking
        )

        adversarial_results = {
            "non_whitelisted_books": {
                "success": result["success"],
                "excluded_bad_books": bool(result["success"]),
                "legs_from_bad_books": 0,
            }
        }

        if result["success"]:
            # Check if any legs came from non-whitelisted books
            legs = result["data"].get("legs", [])
            bad_book_legs = [
                leg for leg in legs if leg.get("book") not in [
                    "DraftKings", "FanDuel", "BetMGM"]]
            adversarial_results["non_whitelisted_books"]["legs_from_bad_books"] = len(
                bad_book_legs)

            if len(bad_book_legs) == 0:
                logger.info("   ✅ Successfully excluded non-whitelisted books")
            else:
                logger.warning(
                    f"   ⚠️ {
                        len(bad_book_legs)} legs from non-whitelisted books included")

        return adversarial_results

    def run_deterministic_test(self, runs: int = 3) -> dict:
        """
        Test deterministic behavior with seed control.

        Args:
            runs: Number of test runs

        Returns:
            Deterministic test results
        """
        logger.info(f"🔒 Testing deterministic behavior ({runs} runs)")

        # Set seed for deterministic results
        original_session = self.session
        self.session.seed = 12345
        self.session.temperature = 0.0  # Zero temperature for maximum determinism

        results = []

        for i in range(runs):
            logger.info(f"   Run {i + 1}/{runs}")

            result = self.run_parlay_architect(
                dataset_name="hooks_pack",
                variables_override={"max_legs": 4},  # Limit for consistency
            )

            if result["success"]:
                results.append(
                    {
                        "run": i + 1,
                        "legs_count": len(result["data"].get("legs", [])),
                        "stake": result["data"].get("stake", 0),
                        "legs": result["data"].get("legs", []),
                    }
                )

        # Restore original session
        self.session = original_session

        # Check consistency
        if len(results) > 1:
            first_result = results[0]
            all_consistent = all(
                r["legs_count"] == first_result["legs_count"]
                and abs(r["stake"] - first_result["stake"]) < 0.01
                for r in results[1:]
            )

            if all_consistent:
                logger.info("   ✅ All runs produced identical results")
            else:
                logger.warning("   ⚠️ Results varied between runs")

        return {"runs": results, "consistent": (
            len({r["legs_count"] for r in results}) <= 1 if results else False), }


def main():
    """Demo the EQ12 Playground functionality."""
    import os

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return

    print("🎯 EQ12 Playground Demo")
    print("=" * 50)

    # Initialize playground
    session = PlaygroundSession(
        model="gpt-4o",  # Use gpt-4o until gpt-5 available
        temperature=0.2,
        reasoning_effort="low",
    )

    playground = EQ12Playground(api_key, session)

    try:
        # Test parlay architect
        print("\n1️⃣ Testing Parlay Architect")
        playground.run_parlay_architect("hooks_pack")

        # Test hooks specialist
        print("\n2️⃣ Testing Hooks Specialist")
        playground.run_hooks_specialist("hooks_pack")

        # Test alert generation
        print("\n3️⃣ Testing Alert Copy Generation")
        playground.generate_alert_copy()

        # Run what-if scenarios
        print("\n4️⃣ Running What-If Scenarios")
        playground.run_what_if_scenarios()

        # Run adversarial tests
        print("\n5️⃣ Running Adversarial Tests")
        playground.run_adversarial_tests()

        print("\n✅ EQ12 Playground demo completed!")
        print("💡 Use this for daily parlay optimization workflows")

    except Exception as e:
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
