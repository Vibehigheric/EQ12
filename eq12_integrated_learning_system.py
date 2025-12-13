#!/usr/bin/env python3
"""
EQ12 Integrated Learning System
Connects AI learning engine to full EQ12 betting system for continuous improvement
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from eq12_boolean_logic_engine import EQ12BooleanLogicEngine

# EQ12 Imports
from eq12_complete_parlay_analyzer import (
    CompleteParlaySlip,
    EQ12CompleteParlayDisplaySystem,
    ParlayStatus,
)
from eq12_error_boundary import GPT5ErrorBoundary
from eq12_unicode_simple import safe_print


class EQ12IntegratedLearningSystem:
    """Complete EQ12 integration with AI learning and feedback loops."""

    def __init__(self):
        self.analyzer = EQ12CompleteParlayDisplaySystem()
        self.boolean_logic = EQ12BooleanLogicEngine()
        self.error_boundary = GPT5ErrorBoundary()

        self.data_dir = Path("C:/EQ12")
        self.db_path = self.data_dir / "database" / "sports_betting.db"
        self.learning_db_path = self.data_dir / "database" / "eq12_learning.db"

        self._setup_learning_database()
        self._setup_logging()

        # Learning parameters
        self.learning_weights = {
            "confidence_accuracy": 0.3,
            "edge_performance": 0.25,
            "steam_correlation": 0.2,
            "conference_patterns": 0.15,
            "parlay_size_optimization": 0.1,
        }

    def _setup_learning_database(self):
        """Setup database for learning and performance tracking."""
        try:
            with sqlite3.connect(self.learning_db_path) as conn:
                cursor = conn.cursor()

                # Parlay results table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS parlay_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        parlay_id TEXT UNIQUE NOT NULL,
                        conference TEXT,
                        parlay_type TEXT,
                        generated_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        status TEXT,

                        -- Prediction metrics
                        predicted_win_prob REAL,
                        predicted_roi REAL,
                        predicted_edge REAL,
                        ai_confidence REAL,
                        boolean_score REAL,

                        -- Actual results
                        actual_result TEXT,
                        actual_payout REAL,
                        actual_roi REAL,

                        -- Performance metrics
                        accuracy_score REAL,
                        edge_realized REAL,
                        clv_total REAL,

                        -- Learning data
                        ai_analysis TEXT,
                        lessons_learned TEXT,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Leg performance table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS leg_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        parlay_id TEXT,
                        leg_index INTEGER,

                        -- Leg details
                        matchup TEXT,
                        bet_type TEXT,
                        selection TEXT,
                        line_value REAL,
                        odds REAL,

                        -- Predictions
                        confidence REAL,
                        edge_percentage REAL,
                        sentiment REAL,
                        steam_detected BOOLEAN,

                        -- Results
                        leg_result TEXT,
                        closing_odds REAL,
                        clv REAL,

                        -- Performance
                        accuracy REAL,
                        edge_realized REAL,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (parlay_id) REFERENCES parlay_results(parlay_id)
                    )
                """
                )

                # Learning insights table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS learning_insights (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        insight_type TEXT,
                        conference TEXT,
                        pattern_description TEXT,
                        confidence_level REAL,
                        sample_size INTEGER,

                        -- Actionable recommendations
                        recommendation TEXT,
                        adjustment_type TEXT,
                        adjustment_value REAL,

                        -- Validation
                        validation_score REAL,
                        implementation_date TIMESTAMP,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # System performance tracking
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS system_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        period_start TIMESTAMP,
                        period_end TIMESTAMP,

                        -- Volume metrics
                        total_parlays INTEGER,
                        total_legs INTEGER,

                        -- Performance metrics
                        win_rate REAL,
                        avg_roi REAL,
                        total_profit REAL,
                        sharpe_ratio REAL,
                        max_drawdown REAL,

                        -- Accuracy metrics
                        confidence_calibration REAL,
                        edge_accuracy REAL,
                        steam_hit_rate REAL,

                        -- Learning metrics
                        learning_score REAL,
                        adaptation_rate REAL,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                conn.commit()
                safe_print("✅ Learning database initialized")

        except Exception:
            safe_print("❌ Learning database setup failed: {e}")

    def _setup_logging(self):
        """Setup comprehensive logging for learning system."""
        log_dir = self.data_dir / "logs" / "learning"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"eq12_learning_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8", errors="replace"),
                logging.StreamHandler(),
            ],
        )

        self.logger = logging.getLogger("EQ12Learning")
        self.logger.info("EQ12 Learning System initialized")

    async def process_completed_parlays(self) -> dict[str, Any]:
        """Process completed parlays and extract learning insights."""
        try:
            # Load recent completed parlays from main database
            completed_parlays = await self._load_completed_parlays()

            if not completed_parlays:
                return {"status": "no_data", "message": "No completed parlays found"}

            results = {
                "processed_count": len(completed_parlays),
                "learning_insights": [],
                "performance_updates": {},
                "system_adjustments": [],
            }

            # Process each completed parlay
            for parlay in completed_parlays:
                # Get AI analysis of the result
                analysis = await self._analyze_parlay_result(parlay)

                # Store results in learning database
                await self._store_parlay_result(parlay, analysis)

                # Extract insights
                insights = await self._extract_learning_insights(parlay, analysis)
                results["learning_insights"].extend(insights)

            # Update system performance metrics
            performance = await self._calculate_system_performance()
            results["performance_updates"] = performance

            # Generate system adjustments
            adjustments = await self._generate_system_adjustments(results["learning_insights"])
            results["system_adjustments"] = adjustments

            # Apply approved adjustments
            await self._apply_system_adjustments(adjustments)

            return results

        except Exception as e:
            self.logger.error(f"Failed to process completed parlays: {e}")
            return {"status": "error", "message": str(e)}

    async def _load_completed_parlays(self) -> list[CompleteParlaySlip]:
        """Load completed parlays from the main sports betting database."""
        completed_parlays = []

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get completed parlays from last 7 days
                cursor.execute(
                    """
                    SELECT * FROM ncaa_week7_parlays
                    WHERE created_at >= datetime('now', '-7 days')
                    AND parlay_id NOT IN (
                        SELECT parlay_id FROM parlay_results
                        WHERE parlay_id = ncaa_week7_parlays.parlay_id
                    )
                """
                )

                rows = cursor.fetchall()

                for _row in rows:
                    # Convert database row to CompleteParlaySlip
                    # This would need actual result data from sportsbooks
                    # For demo, we'll simulate some completed parlays
                    pass

        except Exception as e:
            self.logger.error(f"Failed to load completed parlays: {e}")

        return completed_parlays

    async def _analyze_parlay_result(self, parlay: CompleteParlaySlip) -> dict[str, Any]:
        """Analyze a completed parlay result using AI."""
        analysis_type = (
            "win_analysis" if parlay.parlay_status == ParlayStatus.WON else "loss_analysis"
        )

        analysis = await self.analyzer.ai_analyze_parlay(parlay, analysis_type)

        # Calculate accuracy metrics
        accuracy_metrics = self._calculate_accuracy_metrics(parlay)
        analysis["accuracy_metrics"] = accuracy_metrics

        return analysis

    def _calculate_accuracy_metrics(self, parlay: CompleteParlaySlip) -> dict[str, float]:
        """Calculate how accurate our predictions were."""
        metrics = {}

        # Confidence calibration (how well predicted probability matched outcome)
        if parlay.parlay_status == ParlayStatus.WON:
            metrics["confidence_accuracy"] = parlay.win_probability
        else:
            metrics["confidence_accuracy"] = 1 - parlay.win_probability

        # Edge realization (did we capture the predicted edge?)
        if parlay.parlay_status == ParlayStatus.WON:
            actual_roi = (
                parlay.actual_payout - parlay.recommended_stake
            ) / parlay.recommended_stake
            metrics["edge_realization"] = (
                min(actual_roi / parlay.expected_roi, 2.0) if parlay.expected_roi > 0 else 0
            )
        else:
            metrics["edge_realization"] = -1.0  # Lost all edge

        # CLV performance
        total_clv = sum(
            leg.closing_odds - leg.odds for leg in parlay.legs if leg.closing_odds
        ) / len(parlay.legs)
        metrics["clv_performance"] = total_clv / abs(parlay.combined_odds) * 100

        return metrics

    async def _store_parlay_result(
        self, parlay: CompleteParlaySlip, analysis: dict[str, Any]
    ) -> None:
        """Store parlay result in learning database."""
        try:
            with sqlite3.connect(self.learning_db_path) as conn:
                cursor = conn.cursor()

                # Store main parlay result
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO parlay_results (
                        parlay_id, conference, parlay_type, generated_at, completed_at, status,
                        predicted_win_prob, predicted_roi, predicted_edge, ai_confidence, boolean_score,
                        actual_result, actual_payout, actual_roi,
                        accuracy_score, edge_realized, clv_total,
                        ai_analysis, lessons_learned
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        parlay.parlay_id,
                        parlay.conference,
                        parlay.parlay_type,
                        parlay.generated_at,
                        parlay.completion_time,
                        parlay.parlay_status.value,
                        parlay.win_probability,
                        parlay.expected_roi,
                        parlay.total_edge,
                        parlay.ai_confidence_score or 0,
                        analysis.get("confidence_score", 0),
                        parlay.parlay_status.value,
                        parlay.actual_payout or 0,
                        parlay.profit_loss or 0,
                        analysis.get("accuracy_metrics", {}).get("confidence_accuracy", 0),
                        analysis.get("accuracy_metrics", {}).get("edge_realization", 0),
                        analysis.get("accuracy_metrics", {}).get("clv_performance", 0),
                        json.dumps(analysis),
                        parlay.learning_notes or "",
                    ),
                )

                # Store individual leg performance
                for i, leg in enumerate(parlay.legs):
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO leg_performance (
                            parlay_id, leg_index, matchup, bet_type, selection, line_value, odds,
                            confidence, edge_percentage, sentiment, steam_detected,
                            leg_result, closing_odds, clv, accuracy, edge_realized
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            parlay.parlay_id,
                            i,
                            leg.matchup,
                            leg.bet_type.value,
                            leg.selection,
                            leg.line,
                            leg.odds,
                            leg.confidence,
                            leg.edge_percentage,
                            leg.sentiment,
                            leg.steam_detected,
                            leg.actual_result or "",
                            leg.closing_odds or 0,
                            (leg.closing_odds - leg.odds) if leg.closing_odds else 0,
                            1.0 if leg.leg_status == ParlayStatus.WON else 0.0,
                            (
                                leg.edge_percentage
                                if leg.leg_status == ParlayStatus.WON
                                else -leg.edge_percentage
                            ),
                        ),
                    )

                conn.commit()
                self.logger.info(f"Stored results for parlay {parlay.parlay_id}")

        except Exception as e:
            self.logger.error(f"Failed to store parlay result: {e}")

    async def _extract_learning_insights(
        self, parlay: CompleteParlaySlip, analysis: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Extract actionable learning insights from parlay analysis."""
        insights = []

        # Conference-specific insights
        if parlay.conference not in ["Unknown", ""]:
            conf_insight = {
                "type": "conference_pattern",
                "conference": parlay.conference,
                "pattern": f"{parlay.parlay_status.value} for {parlay.parlay_type} parlay",
                "confidence": analysis.get("confidence_score", 0),
                "sample_size": 1,
                "recommendation": f"Adjust {parlay.conference} {parlay.parlay_type} strategy",
            }
            insights.append(conf_insight)

        # Steam correlation insights
        steam_legs = [leg for leg in parlay.legs if leg.steam_detected]
        if steam_legs:
            steam_insight = {
                "type": "steam_correlation",
                "conference": parlay.conference,
                "pattern": f"Steam correlation: {len(steam_legs)} steam legs, result: {parlay.parlay_status.value}",
                "confidence": len(steam_legs) / len(parlay.legs),
                "sample_size": len(steam_legs),
                "recommendation": "Adjust steam weight in selection algorithm",
            }
            insights.append(steam_insight)

        # Parlay size optimization
        size_insight = {
            "type": "parlay_size_optimization",
            "conference": parlay.conference,
            "pattern": f"{len(parlay.legs)}-leg {parlay.parlay_type} parlay {parlay.parlay_status.value}",
            "confidence": parlay.win_probability,
            "sample_size": 1,
            "recommendation": f"Optimize {parlay.parlay_type} parlay leg count",
        }
        insights.append(size_insight)

        return insights

    async def _calculate_system_performance(self) -> dict[str, Any]:
        """Calculate overall system performance metrics."""
        try:
            with sqlite3.connect(self.learning_db_path) as conn:
                cursor = conn.cursor()

                # Get performance metrics for last 30 days
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_parlays,
                        SUM(CASE WHEN status = 'WON' THEN 1 ELSE 0 END) as wins,
                        AVG(accuracy_score) as avg_accuracy,
                        AVG(edge_realized) as avg_edge_realized,
                        AVG(clv_total) as avg_clv
                    FROM parlay_results
                    WHERE created_at >= datetime('now', '-30 days')
                """
                )

                result = cursor.fetchone()

                if result and result[0] > 0:
                    performance = {
                        "total_parlays": result[0],
                        "win_rate": result[1] / result[0] if result[0] > 0 else 0,
                        "accuracy_score": result[2] or 0,
                        "edge_realization": result[3] or 0,
                        "avg_clv": result[4] or 0,
                        "learning_score": (
                            (result[2] + result[3]) / 2 if result[2] and result[3] else 0
                        ),
                    }
                else:
                    performance = {
                        "total_parlays": 0,
                        "win_rate": 0,
                        "accuracy_score": 0,
                        "edge_realization": 0,
                        "avg_clv": 0,
                        "learning_score": 0,
                    }

                return performance

        except Exception as e:
            self.logger.error(f"Failed to calculate performance: {e}")
            return {}

    async def _generate_system_adjustments(
        self, insights: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Generate system adjustments based on learning insights."""
        adjustments = []

        # Group insights by type
        insight_groups = {}
        for insight in insights:
            insight_type = insight.get("type", "unknown")
            if insight_type not in insight_groups:
                insight_groups[insight_type] = []
            insight_groups[insight_type].append(insight)

        # Generate adjustments for each type
        for insight_type, group_insights in insight_groups.items():
            if insight_type == "conference_pattern":
                adjustment = await self._generate_conference_adjustment(group_insights)
                if adjustment:
                    adjustments.append(adjustment)

            elif insight_type == "steam_correlation":
                adjustment = await self._generate_steam_adjustment(group_insights)
                if adjustment:
                    adjustments.append(adjustment)

            elif insight_type == "parlay_size_optimization":
                adjustment = await self._generate_size_adjustment(group_insights)
                if adjustment:
                    adjustments.append(adjustment)

        return adjustments

    async def _generate_conference_adjustment(
        self, insights: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Generate conference-specific adjustments."""
        if not insights:
            return None

        # Aggregate conference performance
        conference_performance = {}
        for insight in insights:
            conf = insight.get("conference", "Unknown")
            if conf not in conference_performance:
                conference_performance[conf] = {"wins": 0, "total": 0}

            conference_performance[conf]["total"] += 1
            if "WON" in insight.get("pattern", ""):
                conference_performance[conf]["wins"] += 1

        # Find underperforming conferences
        for conf, perf in conference_performance.items():
            win_rate = perf["wins"] / perf["total"] if perf["total"] > 0 else 0

            if win_rate < 0.3 and perf["total"] >= 3:  # Underperforming conference
                adjustment = {
                    "type": "conference_weight_reduction",
                    "conference": conf,
                    "current_performance": win_rate,
                    "adjustment_factor": 0.8,  # Reduce weight by 20%
                    "confidence": min(perf["total"] / 10, 1.0),
                    "implementation": "reduce_conference_parlay_allocation",
                }
                return adjustment

        return None

    async def _generate_steam_adjustment(
        self, insights: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Generate steam correlation adjustments."""
        if not insights:
            return None

        steam_performance = {"wins": 0, "total": 0}
        for insight in insights:
            steam_performance["total"] += insight.get("sample_size", 1)
            if "WON" in insight.get("pattern", ""):
                steam_performance["wins"] += insight.get("sample_size", 1)

        win_rate = (
            steam_performance["wins"] / steam_performance["total"]
            if steam_performance["total"] > 0
            else 0
        )

        if win_rate > 0.6:  # Steam is performing well
            return {
                "type": "steam_weight_increase",
                "current_performance": win_rate,
                "adjustment_factor": 1.2,  # Increase steam weight by 20%
                "confidence": min(steam_performance["total"] / 20, 1.0),
                "implementation": "increase_steam_selection_priority",
            }
        if win_rate < 0.4:  # Steam is underperforming
            return {
                "type": "steam_weight_decrease",
                "current_performance": win_rate,
                "adjustment_factor": 0.8,  # Decrease steam weight by 20%
                "confidence": min(steam_performance["total"] / 20, 1.0),
                "implementation": "decrease_steam_selection_priority",
            }

        return None

    async def _generate_size_adjustment(
        self, insights: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Generate parlay size optimization adjustments."""
        if not insights:
            return None

        # Analyze optimal parlay sizes
        size_performance = {}
        for insight in insights:
            pattern = insight.get("pattern", "")
            if "-leg" in pattern:
                size_str = pattern.split("-leg")[0].split()[-1]
                try:
                    size = int(size_str)
                    if size not in size_performance:
                        size_performance[size] = {"wins": 0, "total": 0}

                    size_performance[size]["total"] += 1
                    if "WON" in pattern:
                        size_performance[size]["wins"] += 1
                except ValueError:
                    continue

        # Find optimal size range
        best_sizes = []
        for size, perf in size_performance.items():
            win_rate = perf["wins"] / perf["total"] if perf["total"] > 0 else 0
            if win_rate > 0.5 and perf["total"] >= 2:
                best_sizes.append((size, win_rate, perf["total"]))

        if best_sizes:
            best_sizes.sort(key=lambda x: x[1], reverse=True)  # Sort by win rate
            optimal_size = best_sizes[0][0]

            return {
                "type": "parlay_size_optimization",
                "optimal_size": optimal_size,
                "performance": best_sizes[0][1],
                "confidence": min(best_sizes[0][2] / 10, 1.0),
                "implementation": "adjust_parlay_leg_count_targets",
            }

        return None

    async def _apply_system_adjustments(self, adjustments: list[dict[str, Any]]) -> None:
        """Apply approved system adjustments."""
        for adjustment in adjustments:
            try:
                if adjustment.get("confidence", 0) > 0.7:  # Only apply high-confidence adjustments
                    await self._implement_adjustment(adjustment)
                    self.logger.info(f"Applied adjustment: {adjustment['type']}")
                else:
                    self.logger.info(f"Queued low-confidence adjustment: {adjustment['type']}")

            except Exception as e:
                self.logger.error(f"Failed to apply adjustment: {e}")

    async def _implement_adjustment(self, adjustment: dict[str, Any]) -> None:
        """Implement a specific system adjustment."""
        # This would modify the actual EQ12 system parameters
        # For now, just log the adjustment
        adjustment_log = {
            "timestamp": datetime.now().isoformat(),
            "adjustment": adjustment,
            "status": "implemented",
        }

        # Save adjustment log
        log_file = self.data_dir / "logs" / "learning" / "adjustments.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(adjustment_log) + "\n")

    async def run_learning_cycle(self) -> dict[str, Any]:
        """Run complete learning cycle for EQ12 system."""
        safe_print("🧠 Starting EQ12 Integrated Learning Cycle")
        safe_print("=" * 60)

        try:
            # Process completed parlays
            results = await self.process_completed_parlays()

            safe_print("📊 Learning Cycle Results:")
            safe_print("   Processed Parlays: {results.get('processed_count', 0)}")
            safe_print(f"   Learning Insights: {len(results.get('learning_insights', []))}")
            safe_print(f"   System Adjustments: {len(results.get('system_adjustments', []))}")

            # Display key insights
            for insight in results.get("learning_insights", [])[:3]:
                safe_print(
                    f"💡 {insight.get('type', 'Unknown')}: {insight.get('recommendation', 'No recommendation')}"
                )

            # Display performance
            performance = results.get("performance_updates", {})
            if performance:
                safe_print("\n📈 System Performance:")
                safe_print("   Win Rate: {performance.get('win_rate', 0):.1%}")
                safe_print(f"   Learning Score: {performance.get('learning_score', 0):.1%}")
                safe_print(f"   Edge Realization: {performance.get('edge_realization', 0):.1%}")

            safe_print("\n✅ EQ12 Learning Cycle Complete!")
            return results

        except Exception as e:
            safe_print("❌ Learning cycle failed: {e}")
            return {"status": "error", "message": str(e)}


async def main():
    """Main execution function."""
    learning_system = EQ12IntegratedLearningSystem()

    # Run the complete analysis system first
    safe_print("🚀 Running Complete Parlay Analysis System")
    analyzer = EQ12CompleteParlayDisplaySystem()
    await analyzer.run_complete_analysis()

    safe_print("\n" + "=" * 80)

    # Run the learning cycle
    safe_print("🧠 Running Integrated Learning System")
    await learning_system.run_learning_cycle()

    safe_print("\n🏆 EQ12 COMPLETE SYSTEM WITH AI LEARNING READY!")


if __name__ == "__main__":
    asyncio.run(main())
