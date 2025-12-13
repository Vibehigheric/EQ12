#!/usr/bin/env python3
"""
EQ12 Spread Builder - Hooks Specialist
Professional half-point advantage system for spreads and totals.

This module focuses on exploiting hook advantages in NFL betting:
- Half-point spreads near key numbers (3, 7, 10, 14)
- Total hooks with weather/pace considerations
- Correlation penalty optimization for hook parlays
"""

from eq12_responses_client import EQ12ResponsesClient
from eq12_timezone import minutes_until_kickoff, parse_commence_time, utc_now
import asyncio
import json
import logging
import sys
import traceback
from pathlib import Path

# Add EQ12 modules to path
sys.path.insert(0, str(Path(__file__).parent))


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class EQ12HooksSpecialist:
    """
    Professional hooks specialist for spread and total betting.
    Focuses on half-point advantages and key number proximity.
    """

    def __init__(self):
        self.responses_client = EQ12ResponsesClient()

        # NFL Key Numbers (professional edge)
        self.nfl_key_numbers = [3, 7, 10, 14, 17, 21]
        self.total_key_numbers = [41.5, 44.5, 47.5, 51.5]  # Common total ranges

        # Hook thresholds
        self.min_hook_ev = 0.06  # 6% minimum for hooks
        self.perfect_hook_bonus = 0.08  # 8% bonus for perfect hooks
        self.near_key_bonus = 0.04  # 4% bonus near key numbers

        # Correlation limits
        self.max_same_game_hooks = 2  # Max hooks from same game
        self.max_correlation_penalty = 0.03  # 3% max penalty

        self.logs_dir = Path("C:/EQ12/logs")

        logger.info("🎣 EQ12 Hooks Specialist initialized")
        logger.info(f"   Key numbers: {self.nfl_key_numbers}")
        logger.info(f"   Perfect hook bonus: {self.perfect_hook_bonus:.1%}")

    async def build_hooks_parlays(self, odds_legs_file: str | None = None) -> dict:
        """
        Build hooks-focused parlays from latest odds data.
        Returns detailed analysis and parlay recommendations.
        """
        try:
            # Load odds data
            legs_data = await self.load_odds_data(odds_legs_file)
            if not legs_data:
                return {"error": "No odds data available"}

            # Filter to hook legs only
            hook_legs = self.filter_hook_legs(legs_data["legs"])
            logger.info(
                f"🎯 Found {len(hook_legs)} hook legs from {len(legs_data['legs'])} total")

            if len(hook_legs) < 2:
                return {
                    "hook_legs_count": len(hook_legs),
                    "message": "Insufficient hook legs for parlay building",
                    "minimum_required": 2,
                }

            # Analyze hook advantages
            enriched_hooks = self.analyze_hook_advantages(hook_legs)

            # Build hook parlays using specialist prompt
            parlays = await self.build_specialist_parlays(enriched_hooks)

            # Generate hook analysis report
            analysis = self.generate_hook_analysis(enriched_hooks, parlays)

            # Persist results
            await self.persist_hook_results(analysis)

            return analysis

        except Exception as e:
            logger.error(f"❌ Hooks parlay building failed: {e}")
            logger.error(traceback.format_exc())
            return {"error": str(e)}

    async def load_odds_data(self, file_path: str | None = None) -> dict | None:
        """Load odds data from file or latest snapshot."""
        try:
            if not file_path:
                file_path = self.logs_dir / "latest_odds_legs.json"

            with open(file_path) as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Failed to load odds data: {e}")
            return None

    def filter_hook_legs(self, legs: list[dict]) -> list[dict]:
        """Filter to hook legs with quality criteria."""
        hook_legs = []

        for leg in legs:
            # Must be a hook (half-point)
            if not leg.get("hook_flag", False):
                continue

            # Must be spread or total
            market = leg.get("market", "")
            if market not in ["spread", "total"]:
                continue

            # Must meet EV threshold
            ev = leg.get("ev", 0)
            if ev < self.min_hook_ev:
                continue

            # Must be upcoming game
            commence_time = leg.get("commence_time_utc", "")
            if not self.is_valid_game_time(commence_time):
                continue

            hook_legs.append(leg)

        return hook_legs

    def is_valid_game_time(self, commence_time_str: str) -> bool:
        """Check if game time is valid for hook betting."""
        try:
            commence_time = parse_commence_time(commence_time_str)
            minutes = minutes_until_kickoff(commence_time)

            # 30 minutes to 6 hours window (professional timing)
            return 30 <= minutes <= 360

        except Exception:
            return False

    def analyze_hook_advantages(self, hook_legs: list[dict]) -> list[dict]:
        """Analyze and enrich hook legs with advantage calculations."""
        enriched = []

        for leg in hook_legs:
            try:
                point = leg.get("point")
                market = leg.get("market", "")

                # Calculate hook advantage
                hook_advantage = self.calculate_hook_advantage(point, market)

                # Adjust EV with hook bonus
                original_ev = leg.get("ev", 0)
                adjusted_ev = original_ev + hook_advantage

                # Add enrichment data
                enriched_leg = leg.copy()
                enriched_leg.update(
                    {
                        "hook_advantage": hook_advantage,
                        "adjusted_ev": adjusted_ev,
                        "key_number_distance": self.distance_to_key_number(
                            point,
                            market),
                        "hook_grade": self.grade_hook_quality(
                            point,
                            market,
                            original_ev),
                    })

                enriched.append(enriched_leg)

            except Exception as e:
                logger.warning(f"⚠️ Failed to analyze hook for leg: {e}")
                enriched.append(leg)

        return enriched

    def calculate_hook_advantage(self, point: float | None, market: str) -> float:
        """Calculate numerical advantage for a hook."""
        if point is None or abs(point % 1) != 0.5:
            return 0.0

        if market == "spread":
            # Distance to NFL key numbers
            distance = self.distance_to_key_number(point, market)

            if distance == 0.5:  # Perfect hook (e.g., 2.5 vs key 3)
                return self.perfect_hook_bonus
            elif distance <= 1.5:  # Near key number
                return self.near_key_bonus
            else:
                return 0.02  # Generic hook bonus

        elif market == "total":
            # Total hooks have different value
            distance = self.distance_to_key_number(point, market)

            if distance <= 1.0:  # Near total key number
                return 0.05  # 5% bonus for total hooks
            else:
                return 0.03  # Generic total hook bonus

        return 0.0

    def distance_to_key_number(self, point: float | None, market: str) -> float:
        """Calculate distance to nearest key number."""
        if point is None:
            return float("inf")

        abs_point = abs(point)

        if market == "spread":
            key_numbers = self.nfl_key_numbers
        elif market == "total":
            key_numbers = self.total_key_numbers
        else:
            return float("inf")

        return min(abs(abs_point - kn) for kn in key_numbers)

    def grade_hook_quality(self, point: float | None, market: str, ev: float) -> str:
        """Grade hook quality: A, B, C, D."""
        if point is None or abs(point % 1) != 0.5:
            return "F"

        distance = self.distance_to_key_number(point, market)

        # Grade based on distance to key numbers and EV
        if distance == 0.5 and ev >= 0.10:  # Perfect hook + high EV
            return "A+"
        elif distance == 0.5 and ev >= 0.08:  # Perfect hook + good EV
            return "A"
        elif distance <= 1.0 and ev >= 0.08:  # Near key + good EV
            return "B+"
        elif distance <= 1.0 and ev >= 0.06:  # Near key + decent EV
            return "B"
        elif ev >= 0.06:  # Any hook with decent EV
            return "C"
        else:
            return "D"

    async def build_specialist_parlays(self, hook_legs: list[dict]) -> list[dict]:
        """Build parlays using hooks specialist prompt."""
        try:
            # Prepare data for specialist prompt
            hooks_data = {
                "legs": hook_legs,
                "focus": "hooks_specialist",
                "key_numbers": self.nfl_key_numbers,
                "total_key_numbers": self.total_key_numbers,
                "hook_bonus_multiplier": 1.15,
                "max_correlation_penalty": self.max_correlation_penalty,
                "strategy_notes": [
                    "Prioritize perfect hooks (0.5 distance to key numbers)",
                    "Avoid same-game correlations beyond 2 legs",
                    "Weight hook grade (A+ > A > B+ > B > C)",
                    "Consider game flow and pace for totals",
                ],
            }

            # Call specialist prompt
            logger.info("🎯 Building hooks parlays with pmpt_eq12_spread_hooks_v1")

            response = await self.responses_client.build_hooks_with_prompt_id(
                prompt_id="pmpt_eq12_spread_hooks_v1",
                variables={"hooks_data": json.dumps(hooks_data, indent=2)},
                reasoning_effort="high",  # Use high reasoning for specialist analysis
            )

            # Parse and validate response
            parlays = self.parse_specialist_response(response)

            logger.info(f"✨ Generated {len(parlays)} specialist hooks parlays")
            return parlays

        except Exception as e:
            logger.error(f"❌ Specialist parlay building failed: {e}")
            return []

    def parse_specialist_response(self, response: dict) -> list[dict]:
        """Parse specialist prompt response into parlay structures."""
        try:
            # Extract parlays from structured response
            choices = response.get("choices", [])
            if not choices:
                return []

            message = choices[0].get("message", {})
            content = message.get("content", "")

            # Parse structured JSON from content
            # This will depend on your prompt's output format
            # For now, return empty list - implement based on your prompt design

            logger.info(f"📝 Parsed specialist response: {len(content)} chars")
            return []

        except Exception as e:
            logger.error(f"Failed to parse specialist response: {e}")
            return []

    def generate_hook_analysis(
            self,
            hook_legs: list[dict],
            parlays: list[dict]) -> dict:
        """Generate comprehensive hooks analysis report."""
        now = utc_now()

        # Leg analysis
        grade_counts = {}
        total_hook_advantage = 0

        for leg in hook_legs:
            grade = leg.get("hook_grade", "F")
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
            total_hook_advantage += leg.get("hook_advantage", 0)

        # Perfect hooks (Grade A+/A)
        perfect_hooks = [
            leg for leg in hook_legs if leg.get(
                "hook_grade",
                "").startswith("A")]

        # Same-game analysis
        game_groups = {}
        for leg in hook_legs:
            game_id = leg.get("game_id", "unknown")
            if game_id not in game_groups:
                game_groups[game_id] = []
            game_groups[game_id].append(leg)

        multi_hook_games = {gid: legs for gid,
                            legs in game_groups.items() if len(legs) >= 2}

        analysis = {
            "timestamp_utc": now.isoformat(),
            "analysis_type": "hooks_specialist",
            "summary": {
                "total_hook_legs": len(hook_legs),
                "parlays_generated": len(parlays),
                "total_hook_advantage": round(total_hook_advantage, 4),
                "average_hook_advantage": round(total_hook_advantage / max(1, len(hook_legs)), 4),
            },
            "hook_grades": grade_counts,
            "perfect_hooks": {
                "count": len(perfect_hooks),
                # Top 5
                "legs": [self.format_leg_display(leg) for leg in perfect_hooks[:5]],
            },
            "multi_hook_games": {
                "games_count": len(multi_hook_games),
                "total_legs": sum(len(legs) for legs in multi_hook_games.values()),
                "games": {
                    gid: [self.format_leg_display(leg) for leg in legs]
                    for gid, legs in list(multi_hook_games.items())[:3]
                },  # Top 3 games
            },
            "parlays": parlays,
            "recommendations": self.generate_hook_recommendations(hook_legs, parlays),
        }

        return analysis

    def format_leg_display(self, leg: dict) -> dict:
        """Format leg for display in analysis."""
        return {
            "book": leg.get("book", ""),
            "selection": leg.get("selection", ""),
            "odds": leg.get("odds", 0),
            "point": leg.get("point"),
            "adjusted_ev": round(leg.get("adjusted_ev", 0), 3),
            "hook_grade": leg.get("hook_grade", "F"),
            "hook_advantage": round(leg.get("hook_advantage", 0), 3),
        }

    def generate_hook_recommendations(
        self, hook_legs: list[dict], parlays: list[dict]
    ) -> list[str]:
        """Generate actionable recommendations for hooks betting."""
        recommendations = []

        # Perfect hooks analysis
        perfect_count = len(
            [leg for leg in hook_legs if leg.get("hook_grade", "").startswith("A")])
        if perfect_count >= 3:
            recommendations.append(
                f"🎯 {perfect_count} perfect hooks available - prioritize A+ grades"
            )

        # Multi-game opportunities
        game_groups = {}
        for leg in hook_legs:
            game_id = leg.get("game_id", "")
            if game_id not in game_groups:
                game_groups[game_id] = []
            game_groups[game_id].append(leg)

        multi_games = [gid for gid, legs in game_groups.items() if len(legs) >= 2]
        if multi_games:
            recommendations.append(
                f"⚖️ {len(multi_games)} games with multiple hooks - watch correlations"
            )

        # EV distribution
        high_ev_count = len(
            [leg for leg in hook_legs if leg.get("adjusted_ev", 0) >= 0.10])
        if high_ev_count >= 2:
            recommendations.append(
                f"💰 {high_ev_count} hooks with 10%+ adjusted EV - build 2-leg parlays"
            )

        # Market distribution
        spread_hooks = len([leg for leg in hook_legs if leg.get("market") == "spread"])
        total_hooks = len([leg for leg in hook_legs if leg.get("market") == "total"])

        if spread_hooks >= 3 and total_hooks >= 2:
            recommendations.append("🔄 Mix spread and total hooks to reduce correlation")

        if not recommendations:
            recommendations.append(
                "📊 Standard hooks analysis - no special opportunities detected")

        return recommendations

    async def persist_hook_results(self, analysis: dict):
        """Persist hooks analysis to structured logs."""
        try:
            timestamp = utc_now().strftime("%Y%m%d_%H%M%S")

            # Detailed analysis file
            analysis_file = self.logs_dir / f"hooks_analysis_{timestamp}.json"
            with open(analysis_file, "w") as f:
                json.dump(analysis, f, indent=2)

            # Latest snapshot
            latest_file = self.logs_dir / "latest_hooks_analysis.json"
            with open(latest_file, "w") as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"💾 Persisted hooks analysis to {analysis_file.name}")

            # Log key stats
            summary = analysis.get("summary", {})
            logger.info(
                f"📊 Hooks Summary: {summary.get('total_hook_legs', 0)} legs, "
                f"{summary.get('average_hook_advantage', 0):.1%} avg advantage"
            )

        except Exception as e:
            logger.error(f"Failed to persist hook results: {e}")


async def main():
    """Main entry point for hooks specialist."""
    logger.info("🎣 EQ12 Hooks Specialist Starting")
    logger.info("=" * 50)

    try:
        specialist = EQ12HooksSpecialist()
        result = await specialist.build_hooks_parlays()

        if "error" in result:
            logger.error(f"❌ Hooks analysis failed: {result['error']}")
        else:
            summary = result.get("summary", {})
            logger.info("✅ Hooks analysis complete:")
            logger.info(f"   📊 {summary.get('total_hook_legs', 0)} hook legs analyzed")
            logger.info(f"   🎯 {summary.get('parlays_generated', 0)} parlays generated")
            logger.info(
                f"   💰 {
                    summary.get(
                        'average_hook_advantage',
                        0):.1%} average hook advantage")

    except KeyboardInterrupt:
        logger.info("\n👋 Hooks specialist stopped by user")
    except Exception as e:
        logger.error(f"❌ Hooks specialist failed: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
