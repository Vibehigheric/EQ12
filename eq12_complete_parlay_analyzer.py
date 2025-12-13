#!/usr/bin/env python3
"""
EQ12 Complete Parlay Display & AI Learning System
Comprehensive parlay slip display with exact picks and ChatGPT-powered analysis
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from eq12_betting_mathematics import EQ12BettingMathematics

# Import EQ12 components
from eq12_boolean_logic_engine import EQ12BooleanLogicEngine
from eq12_error_boundary import GPT5ErrorBoundary
from eq12_unicode_handler import safe_print


class BetType(Enum):
    """Enumeration for different bet types."""

    MONEYLINE = "ML"
    SPREAD = "SPREAD"
    OVER_UNDER = "O/U"
    PLAYER_PROP = "PROP"


class ParlayStatus(Enum):
    """Enumeration for parlay status."""

    PENDING = "PENDING"
    WON = "WON"
    LOST = "LOST"
    CANCELLED = "CANCELLED"


@dataclass
class DetailedParlayLeg:
    """Comprehensive parlay leg with all betting details."""

    game_id: str
    sport: str
    conference: str
    matchup: str
    home_team: str
    away_team: str

    # Bet Details
    bet_type: BetType
    selection: str  # Team name or O/U selection
    line: float | None  # Spread number or total
    odds: float

    # Analytics
    confidence: float
    edge_percentage: float
    kelly_percentage: float
    sentiment: float
    steam_detected: bool
    is_top25: bool

    # Market Data
    bookmaker: str
    market: str
    start_time: str

    # Results (populated after game completion)
    actual_result: str | None = None
    leg_status: ParlayStatus | None = None
    closing_odds: float | None = None


@dataclass
class CompleteParlaySlip:
    """Complete parlay slip with all details."""

    parlay_id: str
    conference: str
    parlay_type: str
    week: int
    generated_at: str

    # Legs
    legs: list[DetailedParlayLeg]

    # Parlay Metrics
    combined_odds: float
    win_probability: float
    expected_roi: float
    recommended_stake: float
    total_edge: float
    risk_score: float

    # Results (populated after completion)
    parlay_status: ParlayStatus | None = None
    actual_payout: float | None = None
    profit_loss: float | None = None
    completion_time: str | None = None

    # AI Analysis
    ai_confidence_score: float | None = None
    ai_recommendation: str | None = None
    learning_notes: str | None = None


class EQ12NCAASummaryDisplay:
    """NCAA Summary display renderer for parlay analysis"""

    def render(self, summary):
        """Render NCAA summary data safely"""
        print("=== NCAA SUMMARY ===")
        if not summary:
            print("No NCAA data available")
            return

        for row in summary:
            if isinstance(row, dict):
                row.get("matchup", "Unknown matchup")
                row.get("pick", "No pick")
                row.get("odds", "No odds")
                print("{matchup} | {pick} | {odds}")
            else:
                print("Row: {row}")


class EQ12CompleteParlayDisplaySystem:
    """Complete parlay display and AI learning system."""

    def __init__(self):
        self.error_boundary = GPT5ErrorBoundary()
        self.boolean_logic = EQ12BooleanLogicEngine()
        self.betting_math = EQ12BettingMathematics()
        self.summary_display = EQ12NCAASummaryDisplay()
        self.data_dir = Path("C:/EQ12")
        self.outputs_dir = self.data_dir / "outputs"
        self.results_dir = self.data_dir / "results"
        self.learning_dir = self.data_dir / "ai_learning"

        # Create directories
        self.results_dir.mkdir(exist_ok=True)
        self.learning_dir.mkdir(exist_ok=True)

        self.learning_prompts = self._initialize_learning_prompts()

    def _initialize_learning_prompts(self) -> dict[str, str]:
        """Initialize ChatGPT prompts for different analysis scenarios."""
        return {
            "win_analysis": """
            Analyze this WINNING parlay slip and identify key success factors:

            Parlay Details: {parlay_data}

            Please analyze:
            1. What made this parlay successful?
            2. Which legs contributed most to the win?
            3. What market conditions favored this selection?
            4. Steam movement impact on success
            5. Confidence vs actual performance correlation
            6. Conference-specific factors that helped
            7. Recommendations for similar future parlays

            Provide structured analysis with confidence scores and actionable insights.
            """,
            "loss_analysis": """
            Analyze this LOSING parlay slip and identify improvement opportunities:

            Parlay Details: {parlay_data}

            Please analyze:
            1. What caused this parlay to lose?
            2. Which legs failed and why?
            3. Were there warning signs we missed?
            4. How did steam movements affect the outcome?
            5. Was the confidence level appropriately calibrated?
            6. Conference-specific risks that materialized
            7. How to avoid similar losses in the future

            Provide structured analysis with risk assessments and prevention strategies.
            """,
            "pattern_analysis": """
            Analyze patterns across multiple parlay results:

            Historical Data: {historical_data}

            Please identify:
            1. Winning vs losing patterns by conference
            2. Optimal parlay leg counts for different risk levels
            3. Steam movement predictive value
            4. Confidence calibration accuracy
            5. Time/day performance patterns
            6. Market condition correlations
            7. Recommended system adjustments

            Provide data-driven insights for system optimization.
            """,
            "pre_game_validation": """
            Validate this parlay before placement using Boolean logic principles:

            Proposed Parlay: {parlay_data}
            Current Market Conditions: {market_conditions}
            System State: {system_state}

            Boolean Logic Validation:
            1. AND: All conditions must be met for recommendation
            2. OR: Alternative scenarios that support the bet
            3. NOT: Negative conditions that contradict the bet
            4. XOR: Mutually exclusive outcomes to consider

            Provide GO/NO-GO recommendation with confidence score.
            """,
        }

    def load_parlay_data(self) -> list[CompleteParlaySlip]:
        """Load and parse all parlay data into complete slip objects."""
        parlay_slips = []

        # Load from outputs directory
        for json_file in self.outputs_dir.glob("*week7_*.json"):
            if json_file.stat().st_mtime > (datetime.now().timestamp() - 86400):  # Last 24 hours
                try:
                    with open(json_file) as f:
                        data = json.load(f)

                    for parlay_data in data.get("parlays", []):
                        slip = self._parse_parlay_to_slip(
                            parlay_data, data.get("conference", "Unknown")
                        )
                        parlay_slips.append(slip)

                except Exception:
                    safe_print("Error loading {json_file}: {e}")

        return parlay_slips

    def _parse_parlay_to_slip(self, parlay_data: dict, conference: str) -> CompleteParlaySlip:
        """Parse JSON parlay data into detailed slip object."""
        legs = []

        for leg_data in parlay_data.get("legs", []):
            # Determine bet type from the bet string
            bet_string = leg_data.get("bet", "")
            bet_type, selection, line = self._parse_bet_string(bet_string)

            leg = DetailedParlayLeg(
                game_id=leg_data.get("game_id", ""),
                sport=leg_data.get("sport", "NCAA-FB"),
                conference=leg_data.get("conference", conference),
                matchup=leg_data.get("matchup", ""),
                home_team=leg_data.get("home_team", ""),
                away_team=leg_data.get("away_team", ""),
                bet_type=bet_type,
                selection=selection,
                line=line,
                odds=leg_data.get("odds", 0),
                confidence=leg_data.get("confidence", 0),
                edge_percentage=leg_data.get("edge_percentage", 0),
                kelly_percentage=leg_data.get("kelly_percentage", 0),
                sentiment=leg_data.get("sentiment", 0),
                steam_detected=leg_data.get("steam_detected", False),
                is_top25=leg_data.get("is_top25", False),
                bookmaker=leg_data.get("market_data", {}).get("bookmaker", "Unknown"),
                market=leg_data.get("market_data", {}).get("market", "h2h"),
                start_time=leg_data.get("start_time", ""),
            )
            legs.append(leg)

        slip = CompleteParlaySlip(
            parlay_id=parlay_data.get("parlay_id", ""),
            conference=conference,
            parlay_type=parlay_data.get("parlay_type", "unknown"),
            week=parlay_data.get("week", 7),
            generated_at=parlay_data.get("generated_at", datetime.now().isoformat()),
            legs=legs,
            combined_odds=parlay_data.get("combined_odds", 0),
            win_probability=parlay_data.get("win_probability", 0),
            expected_roi=parlay_data.get("expected_roi", 0),
            recommended_stake=parlay_data.get("recommended_stake", 0),
            total_edge=parlay_data.get("total_edge", 0),
            risk_score=parlay_data.get("risk_score", 0),
        )

        return slip

    def _parse_bet_string(self, bet_string: str) -> tuple[BetType, str, float | None]:
        """Parse bet string to determine type, selection, and line."""
        bet_string = bet_string.strip()

        if " ML" in bet_string or "Moneyline" in bet_string:
            selection = bet_string.replace(" ML", "").replace(" Moneyline", "")
            return BetType.MONEYLINE, selection, None

        if " +" in bet_string or " -" in bet_string:
            # Spread bet
            parts = bet_string.split()
            if len(parts) >= 2:
                selection = " ".join(parts[:-1])
                try:
                    line = float(parts[-1])
                    return BetType.SPREAD, selection, line
                except ValueError:
                    pass

        elif "Over " in bet_string or "Under " in bet_string:
            # Over/Under bet
            if "Over " in bet_string:
                line_str = bet_string.replace("Over ", "")
                try:
                    line = float(line_str)
                    return BetType.OVER_UNDER, "Over", line
                except ValueError:
                    pass
            else:
                line_str = bet_string.replace("Under ", "")
                try:
                    line = float(line_str)
                    return BetType.OVER_UNDER, "Under", line
                except ValueError:
                    pass

        # Default to moneyline if can't parse
        return BetType.MONEYLINE, bet_string, None

    def display_complete_parlay_slip(self, slip: CompleteParlaySlip) -> None:
        """Display complete parlay slip with all details."""
        safe_print("\n" + "=" * 100)
        safe_print("🎫 **COMPLETE PARLAY SLIP** - {slip.parlay_id}")
        safe_print("=" * 100)

        # Header Information
        safe_print("📅 Conference: {slip.conference.upper()}")
        safe_print("🎯 Type: {slip.parlay_type.upper()}")
        safe_print("📊 Week: {slip.week}")
        safe_print("⏰ Generated: {slip.generated_at}")

        if slip.parlay_status:
            safe_print("{status_emoji} Status: {slip.parlay_status.value}")

        # Parlay Metrics
        safe_print("\n💰 **PARLAY METRICS**")
        safe_print("🎰 Combined Odds: {slip.combined_odds:+,.0f}")
        safe_print("🎯 Win Probability: {slip.win_probability:.2%}")
        safe_print("📈 Expected ROI: {slip.expected_roi:.1%}")
        safe_print("💵 Recommended Stake: ${slip.recommended_stake:.2f}")
        safe_print("⚡ Total Edge: {slip.total_edge:.1%}")
        safe_print("⚠️ Risk Score: {slip.risk_score:.2f}")

        # Individual Legs
        safe_print("\n🏈 **INDIVIDUAL LEGS** ({len(slip.legs)} legs)")
        safe_print("-" * 100)

        for i, leg in enumerate(slip.legs, 1):
            self._display_leg_details(i, leg)

        # AI Analysis (if available)
        if slip.ai_confidence_score:
            safe_print("\n🤖 **AI ANALYSIS**")
            safe_print("🎯 AI Confidence: {slip.ai_confidence_score:.1%}")
            safe_print("💡 Recommendation: {slip.ai_recommendation}")
            if slip.learning_notes:
                safe_print("📝 Learning Notes: {slip.learning_notes}")

        safe_print("=" * 100)

    def _display_leg_details(self, leg_num: int, leg: DetailedParlayLeg) -> None:
        """Display detailed information for a single leg."""
        # Leg header
        safe_print("\n🏈 **LEG {leg_num}: {leg.matchup}**")

        # Bet details
        self._format_bet_display(leg)
        safe_print("🎯 Pick: {bet_display}")
        safe_print("💰 Odds: {leg.odds:+.0f}")

        # Analytics
        safe_print(
            f"📊 Confidence: {leg.confidence:.1%} | Edge: {leg.edge_percentage:.1f}% | Kelly: {leg.kelly_percentage:.1%}"
        )
        safe_print(
            f"📈 Sentiment: {leg.sentiment:.2f} | Steam: {'⚡YES' if leg.steam_detected else '❌NO'} | Top25: {'⭐YES' if leg.is_top25 else '❌NO'}"
        )
        safe_print("🏪 Book: {leg.bookmaker} | Market: {leg.market}")
        safe_print("⏰ Game Time: {leg.start_time}")

        # Results (if available)
        if leg.leg_status:
            status_emoji = "✅" if leg.leg_status == ParlayStatus.WON else "❌"
            safe_print(
                f"{status_emoji} Result: {leg.actual_result} | Status: {leg.leg_status.value}"
            )
            if leg.closing_odds:
                ((leg.closing_odds - leg.odds) / leg.odds) * 100
                safe_print("📊 CLV: {clv:+.1f}% (Closing: {leg.closing_odds:+.0f})")

    def _format_bet_display(self, leg: DetailedParlayLeg) -> str:
        """Format bet for clear display."""
        if leg.bet_type == BetType.MONEYLINE:
            return f"{leg.selection} MONEYLINE"
        if leg.bet_type == BetType.SPREAD:
            line_str = f"{leg.line:+.1f}" if leg.line else "PK"
            return f"{leg.selection} {line_str} (SPREAD)"
        if leg.bet_type == BetType.OVER_UNDER:
            return f"{leg.selection.upper()} {leg.line} (TOTAL)"
        return f"{leg.selection} ({leg.bet_type.value})"

    async def ai_analyze_parlay(
        self, slip: CompleteParlaySlip, analysis_type: str = "pre_game_validation"
    ) -> dict[str, Any]:
        """Use ChatGPT to analyze parlay with Boolean logic validation."""
        try:
            # Prepare parlay data for analysis
            parlay_data = {
                "id": slip.parlay_id,
                "conference": slip.conference,
                "type": slip.parlay_type,
                "odds": slip.combined_odds,
                "win_prob": slip.win_probability,
                "legs": [
                    {
                        "matchup": leg.matchup,
                        "bet": self._format_bet_display(leg),
                        "odds": leg.odds,
                        "confidence": leg.confidence,
                        "edge": leg.edge_percentage,
                        "steam": leg.steam_detected,
                        "sentiment": leg.sentiment,
                    }
                    for leg in slip.legs
                ],
            }

            # Boolean logic validation
            boolean_validation = self.boolean_logic.complex_parlay_validation()

            # Prepare system state
            system_state = {
                "boolean_authorized": boolean_validation.get("parlay_authorized", False),
                "confidence_score": boolean_validation.get("decision_score", 0),
                "risk_level": (
                    "high" if boolean_validation.get("high_risk_detected", False) else "normal"
                ),
            }

            # Select appropriate prompt
            prompt = self.learning_prompts.get(
                analysis_type, self.learning_prompts["pre_game_validation"]
            )

            # Format prompt with data
            formatted_prompt = prompt.format(
                parlay_data=json.dumps(parlay_data, indent=2),
                system_state=json.dumps(system_state, indent=2),
                market_conditions=json.dumps(
                    {"steam_count": sum(1 for leg in slip.legs if leg.steam_detected)}
                ),
            )

            # Get AI analysis
            response = await self.error_boundary.safe_call(formatted_prompt, max_tokens=800)

            analysis = {
                "analysis_type": analysis_type,
                "ai_response": response,
                "boolean_validation": boolean_validation,
                "confidence_score": boolean_validation.get("decision_score", 0),
                "timestamp": datetime.now().isoformat(),
            }

            # Save analysis
            await self._save_ai_analysis(slip.parlay_id, analysis)

            return analysis

        except Exception as e:
            safe_print("AI analysis failed: {e}")
            return {"error": str(e)}

    async def _save_ai_analysis(self, parlay_id: str, analysis: dict[str, Any]) -> None:
        """Save AI analysis to learning directory."""
        try:
            filename = f"ai_analysis_{parlay_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.learning_dir / filename

            with open(filepath, "w") as f:
                json.dump(analysis, f, indent=2)

        except Exception:
            safe_print("Failed to save AI analysis: {e}")

    async def learn_from_results(
        self, completed_parlays: list[CompleteParlaySlip]
    ) -> dict[str, Any]:
        """Learn from completed parlay results using AI analysis."""
        wins = [p for p in completed_parlays if p.parlay_status == ParlayStatus.WON]
        losses = [p for p in completed_parlays if p.parlay_status == ParlayStatus.LOST]

        learning_insights = {
            "total_analyzed": len(completed_parlays),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(completed_parlays) if completed_parlays else 0,
            "insights": {},
        }

        # Analyze winning patterns
        if wins:
            win_analysis = await self._analyze_parlay_group(wins, "win_analysis")
            learning_insights["insights"]["winning_patterns"] = win_analysis

        # Analyze losing patterns
        if losses:
            loss_analysis = await self._analyze_parlay_group(losses, "loss_analysis")
            learning_insights["insights"]["losing_patterns"] = loss_analysis

        # Overall pattern analysis
        if len(completed_parlays) >= 3:
            pattern_analysis = await self._analyze_overall_patterns(completed_parlays)
            learning_insights["insights"]["overall_patterns"] = pattern_analysis

        # Save learning insights
        await self._save_learning_insights(learning_insights)

        return learning_insights

    async def _analyze_parlay_group(
        self, parlays: list[CompleteParlaySlip], analysis_type: str
    ) -> dict[str, Any]:
        """Analyze a group of parlays (wins or losses)."""
        try:
            # Aggregate data for analysis
            group_data = {
                "count": len(parlays),
                "conferences": list({p.conference for p in parlays}),
                "avg_odds": sum(p.combined_odds for p in parlays) / len(parlays),
                "avg_legs": sum(len(p.legs) for p in parlays) / len(parlays),
                "steam_rate": sum(sum(1 for leg in p.legs if leg.steam_detected) for p in parlays)
                / sum(len(p.legs) for p in parlays),
                "top_picks": [
                    {
                        "parlay_id": p.parlay_id,
                        "conference": p.conference,
                        "odds": p.combined_odds,
                        "legs": len(p.legs),
                        "edge": p.total_edge,
                    }
                    for p in parlays[:3]  # Top 3 examples
                ],
            }

            prompt = self.learning_prompts[analysis_type].format(
                parlay_data=json.dumps(group_data, indent=2)
            )

            response = await self.error_boundary.safe_call(prompt, max_tokens=600)

            return {
                "analysis": response,
                "group_stats": group_data,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}

    async def _analyze_overall_patterns(self, parlays: list[CompleteParlaySlip]) -> dict[str, Any]:
        """Analyze overall patterns across all parlays."""
        try:
            historical_data = {
                "total_parlays": len(parlays),
                "by_conference": {},
                "by_type": {},
                "performance_metrics": {
                    "avg_win_prob": sum(p.win_probability for p in parlays) / len(parlays),
                    "avg_edge": sum(p.total_edge for p in parlays) / len(parlays),
                    "steam_correlation": 0,  # Calculate correlation between steam and wins
                    "confidence_accuracy": 0,  # How well confidence predicted outcomes
                },
            }

            # Group by conference
            for parlay in parlays:
                conf = parlay.conference
                if conf not in historical_data["by_conference"]:
                    historical_data["by_conference"][conf] = {"total": 0, "wins": 0}

                historical_data["by_conference"][conf]["total"] += 1
                if parlay.parlay_status == ParlayStatus.WON:
                    historical_data["by_conference"][conf]["wins"] += 1

            # Calculate win rates
            for conf_data in historical_data["by_conference"].values():
                conf_data["win_rate"] = (
                    conf_data["wins"] / conf_data["total"] if conf_data["total"] > 0 else 0
                )

            prompt = self.learning_prompts["pattern_analysis"].format(
                historical_data=json.dumps(historical_data, indent=2)
            )

            response = await self.error_boundary.safe_call(prompt, max_tokens=700)

            return {
                "analysis": response,
                "historical_data": historical_data,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}

    async def _save_learning_insights(self, insights: dict[str, Any]) -> None:
        """Save learning insights for future reference."""
        try:
            filename = f"learning_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.learning_dir / filename

            with open(filepath, "w") as f:
                json.dump(insights, f, indent=2)

            safe_print("💾 Learning insights saved to: {filepath}")

        except Exception:
            safe_print("Failed to save learning insights: {e}")

    async def run_complete_analysis(self) -> None:
        """Run complete parlay analysis and learning system."""
        safe_print("🚀 Starting EQ12 Complete Parlay Analysis & AI Learning System")
        safe_print("=" * 80)

        # Load all parlay data
        parlay_slips = self.load_parlay_data()

        if not parlay_slips:
            safe_print("⚠️ No parlay data found")
            return

        safe_print("📊 Loaded {len(parlay_slips)} parlay slips")

        # Display all complete parlay slips
        safe_print("\n🎫 **DISPLAYING COMPLETE PARLAY SLIPS**")
        for _i, slip in enumerate(parlay_slips[:5], 1):  # Show first 5
            safe_print("\n{'='*20} SLIP {i}/{min(5, len(parlay_slips))} {'='*20}")
            self.display_complete_parlay_slip(slip)

            # AI analysis for each slip
            safe_print("\n🤖 **AI ANALYSIS FOR SLIP {i}**")
            analysis = await self.ai_analyze_parlay(slip, "pre_game_validation")

            if "error" not in analysis:
                safe_print("🎯 AI Confidence: {analysis['confidence_score']:.1%}")
                safe_print(
                    f"💡 Boolean Authorization: {analysis['boolean_validation'].get('parlay_authorized', False)}"
                )
                safe_print("📝 AI Analysis: {analysis['ai_response'][:200]}...")

        # Overall learning analysis
        safe_print("\n🧠 **AI LEARNING ANALYSIS**")
        # For demo, create some sample completed parlays
        sample_completed = parlay_slips[:3]  # Use first 3 as examples
        for slip in sample_completed:
            slip.parlay_status = (
                ParlayStatus.WON if slip.combined_odds < 1000 else ParlayStatus.LOST
            )

        await self.learn_from_results(sample_completed)

        safe_print("📊 Learning Results:")
        safe_print("   Total Analyzed: {learning_results['total_analyzed']}")
        safe_print("   Win Rate: {learning_results['win_rate']:.1%}")
        safe_print("   Wins: {learning_results['wins']}")
        safe_print("   Losses: {learning_results['losses']}")

        safe_print("\n✅ EQ12 Complete Parlay Analysis & AI Learning System Complete!")


async def main():
    """Main execution function."""
    system = EQ12CompleteParlayDisplaySystem()
    await system.run_complete_analysis()


if __name__ == "__main__":
    asyncio.run(main())
