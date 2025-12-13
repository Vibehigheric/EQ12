#!/usr/bin/env python3
"""
EQ12 Production Betting Analysis Pipeline
Complete automated betting system with multi-API integration and weather analysis
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Import EQ12 systems
try:
    from eq12_api_data_normalization_engine import (
        EQ12DataNormalizationEngine,
    )
    from eq12_multi_sports_api_client import EQ12MultiSportsAPIClient
    from eq12_weather_enhanced_betting_system import (
        EQ12WeatherEnhancedBettingSystem,
        WeatherEnhancedBetting,
    )
except ImportError as e:
    logging.warning(f"Some EQ12 modules not found: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BettingSignal:
    """Final betting recommendation with confidence and analysis"""

    game_id: str
    sport: str
    teams: str
    venue: str
    game_time: datetime

    # Primary recommendation
    primary_bet: str
    bet_confidence: float  # 0-1
    expected_value: float  # -1 to +1

    # Supporting analysis
    weather_factor: float
    odds_quality: float
    venue_advantage: str

    # Specific bets
    moneyline_rec: str | None = None
    spread_rec: str | None = None
    total_rec: str | None = None
    prop_bets: list[str] = None

    # Risk assessment
    risk_level: str = "medium"  # low, medium, high
    bankroll_allocation: float = 0.02  # % of bankroll

    # Analysis metadata
    data_sources: list[str] = None
    analysis_timestamp: datetime = None


@dataclass
class PipelineReport:
    """Comprehensive pipeline execution report"""

    execution_timestamp: datetime
    total_games_analyzed: int
    weather_games: int
    high_confidence_bets: int
    total_signals_generated: int
    expected_daily_ev: float
    pipeline_health_score: float
    data_quality_avg: float
    processing_time_seconds: float


class EQ12ProductionBettingPipeline:
    """
    Complete production pipeline for automated betting analysis
    Integrates all EQ12 systems for comprehensive betting intelligence
    """

    def __init__(self):
        """Initialize all EQ12 subsystems"""
        self.sports_client = EQ12MultiSportsAPIClient()
        self.weather_system = EQ12WeatherEnhancedBettingSystem()
        self.normalization_engine = EQ12DataNormalizationEngine()

        # Pipeline configuration
        self.confidence_threshold = 0.7
        self.min_expected_value = 0.02
        self.max_daily_exposure = 0.20  # 20% of bankroll max

        # Betting parameters
        self.kelly_fraction = 0.25  # Conservative Kelly
        self.max_single_bet = 0.05  # 5% max per bet

        # Output directories
        self.logs_dir = Path("C:/EQ12/logs")
        self.reports_dir = Path("C:/EQ12/reports")
        self.signals_dir = Path("C:/EQ12/signals")

        # Ensure directories exist
        for dir_path in [self.logs_dir, self.reports_dir, self.signals_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    async def run_complete_pipeline(
        self, sports: list[str] | None = None
    ) -> tuple[list[BettingSignal], PipelineReport]:
        """
        Execute complete betting analysis pipeline
        Returns: (betting_signals, pipeline_report)
        """
        start_time = datetime.now()

        if sports is None:
            sports = ["MLB", "NFL", "NCAAF"]

        logger.info("🚀 Starting EQ12 Production Betting Pipeline...")
        logger.info(f"Target sports: {', '.join(sports)}")

        # Step 1: Get comprehensive weather-enhanced analysis
        logger.info("📊 Step 1: Multi-API sports data + weather analysis")
        weather_analyses = await self.weather_system.analyze_all_outdoor_games(sports)

        # Step 2: Normalize and cross-validate data
        logger.info("🔧 Step 2: Data normalization and validation")
        normalized_analyses = self._normalize_betting_data(weather_analyses)

        # Step 3: Generate betting signals
        logger.info("🎯 Step 3: Generate actionable betting signals")
        betting_signals = self._generate_betting_signals(normalized_analyses)

        # Step 4: Risk management and portfolio optimization
        logger.info("⚖️ Step 4: Risk management and position sizing")
        optimized_signals = self._optimize_betting_portfolio(betting_signals)

        # Step 5: Generate execution report
        logger.info("📈 Step 5: Generate pipeline report")
        processing_time = (datetime.now() - start_time).total_seconds()
        pipeline_report = self._generate_pipeline_report(
            weather_analyses, optimized_signals, processing_time
        )

        # Step 6: Save outputs
        logger.info("💾 Step 6: Save signals and reports")
        self._save_pipeline_outputs(optimized_signals, pipeline_report)

        logger.info(
            f"✅ Pipeline complete! Generated {
                len(optimized_signals)} betting signals")

        return optimized_signals, pipeline_report

    def _normalize_betting_data(
        self, weather_analyses: list[WeatherEnhancedBetting]
    ) -> list[WeatherEnhancedBetting]:
        """Normalize and validate betting data using the normalization engine"""

        normalized_analyses = []

        for analysis in weather_analyses:
            try:
                # Cross-validate data quality
                game_data = analysis.game_data

                # Check for minimum data requirements
                has_odds = bool(game_data.odds and game_data.odds.get("bookmakers"))
                has_venue = bool(game_data.venue)
                has_weather = bool(analysis.weather_analysis)

                # Calculate data completeness score
                completeness_factors = [has_odds, has_venue, has_weather]
                completeness_score = sum(completeness_factors) / \
                    len(completeness_factors)

                # Only include games with sufficient data
                if completeness_score >= 0.6:  # At least 60% data completeness
                    analysis.confidence_score *= completeness_score  # Adjust confidence
                    normalized_analyses.append(analysis)
                else:
                    logger.debug(
                        f"Excluding low-quality data: {game_data.away_team} @ {game_data.home_team}"
                    )

            except Exception as e:
                logger.error(f"Error normalizing betting data: {e}")
                continue

        logger.info(
            f"Normalized {
                len(normalized_analyses)} games (from {
                len(weather_analyses)} total)")
        return normalized_analyses

    def _generate_betting_signals(
        self, normalized_analyses: list[WeatherEnhancedBetting]
    ) -> list[BettingSignal]:
        """Generate actionable betting signals from normalized analysis"""

        signals = []

        for analysis in normalized_analyses:
            try:
                game = analysis.game_data
                bet_rec = analysis.betting_recommendation

                # Skip if below confidence threshold
                if analysis.confidence_score < self.confidence_threshold:
                    continue

                # Calculate expected value
                expected_value = self._calculate_expected_value(analysis)

                # Skip if below EV threshold
                if expected_value < self.min_expected_value:
                    continue

                # Determine position sizing
                bankroll_allocation = self._calculate_position_size(
                    analysis.confidence_score, expected_value
                )

                # Create betting signal
                signal = BettingSignal(
                    game_id=game.game_id,
                    sport=game.sport,
                    teams=f"{game.away_team} @ {game.home_team}",
                    venue=game.venue,
                    game_time=game.game_time,
                    primary_bet=bet_rec["primary_bet"],
                    bet_confidence=analysis.confidence_score,
                    expected_value=expected_value,
                    weather_factor=analysis.weather_impact_score,
                    odds_quality=self._assess_odds_quality(game.odds),
                    venue_advantage=self._assess_venue_advantage(game.venue, game.sport),
                    moneyline_rec=self._extract_moneyline_rec(bet_rec),
                    spread_rec=self._extract_spread_rec(bet_rec),
                    total_rec=self._extract_total_rec(bet_rec),
                    prop_bets=bet_rec.get("specific_bets", []),
                    risk_level=self._assess_risk_level(analysis),
                    bankroll_allocation=bankroll_allocation,
                    data_sources=[
                        s.value if hasattr(s, "value") else str(s)
                        for s in getattr(game, "data_sources", ["multi_api"])
                    ],
                    analysis_timestamp=datetime.now(UTC),
                )

                signals.append(signal)

            except Exception as e:
                logger.error(
                    f"Error generating signal for {game.away_team} @ {game.home_team}: {e}"
                )
                continue

        logger.info(f"Generated {len(signals)} betting signals")
        return signals

    def _optimize_betting_portfolio(
            self, signals: list[BettingSignal]) -> list[BettingSignal]:
        """Optimize betting portfolio for risk management"""

        if not signals:
            return signals

        # Sort by expected value
        sorted_signals = sorted(signals, key=lambda s: s.expected_value, reverse=True)

        # Track daily exposure
        total_allocation = 0.0
        optimized_signals = []

        for signal in sorted_signals:
            # Check if we can add this bet without exceeding daily exposure
            if total_allocation + signal.bankroll_allocation <= self.max_daily_exposure:

                # Ensure individual bet doesn't exceed maximum
                signal.bankroll_allocation = min(
                    signal.bankroll_allocation, self.max_single_bet)

                optimized_signals.append(signal)
                total_allocation += signal.bankroll_allocation
            else:
                # Scale down remaining bets to fit within exposure limit
                remaining_budget = self.max_daily_exposure - total_allocation
                if remaining_budget > 0.005:  # Minimum 0.5% bet size
                    signal.bankroll_allocation = remaining_budget
                    optimized_signals.append(signal)
                    break

        logger.info(
            f"Portfolio optimization: {
                len(optimized_signals)} signals, {
                total_allocation:.1%} exposure")
        return optimized_signals

    def _calculate_expected_value(self, analysis: WeatherEnhancedBetting) -> float:
        """Calculate expected value of betting opportunity"""

        # Base EV from confidence above random (50%)
        confidence_edge = (analysis.confidence_score - 0.5) * 2  # Scale to 0-1

        # Weather impact modifier
        weather_modifier = abs(analysis.weather_impact_score -
                               5) / 10  # Scale weather impact

        # Odds quality bonus (if multiple bookmakers agree)
        odds_bonus = 0.1 if len(
            analysis.game_data.odds.get(
                "bookmakers", [])) > 1 else 0

        # Calculate base EV
        base_ev = confidence_edge * 0.5 + weather_modifier * 0.3 + odds_bonus

        # Apply conservative scaling
        expected_value = min(base_ev * 0.3, 0.15)  # Cap at 15% EV

        return expected_value

    def _calculate_position_size(
            self,
            confidence: float,
            expected_value: float) -> float:
        """Calculate optimal position size using modified Kelly criterion"""

        # Kelly fraction: f = (bp - q) / b
        # Where: b = odds, p = win probability, q = lose probability

        # Assume fair odds (implied probability = confidence)
        win_prob = confidence
        lose_prob = 1 - confidence

        # Conservative odds assumption (even money)
        odds = 1.0

        # Kelly fraction
        kelly_fraction = (odds * win_prob - lose_prob) / odds

        # Apply conservative scaling
        conservative_kelly = kelly_fraction * self.kelly_fraction

        # Ensure within bounds
        position_size = max(0.005, min(conservative_kelly, self.max_single_bet))

        return position_size

    def _assess_odds_quality(self, odds_data: dict[str, Any]) -> float:
        """Assess quality of odds data (0-1)"""

        bookmakers = odds_data.get("bookmakers", [])

        if not bookmakers:
            return 0.2

        # More bookmakers = better odds quality
        if len(bookmakers) >= 3:
            return 0.9
        elif len(bookmakers) == 2:
            return 0.7
        else:
            return 0.5

    def _assess_venue_advantage(self, venue: str, sport: str) -> str:
        """Assess venue-specific advantages"""

        # Venue-specific factors
        weather_venues = {
            "Lambeau Field": "Cold Weather Advantage",
            "Soldier Field": "Wind Factor",
            "Arrowhead Stadium": "Noise + Weather",
            "Coors Field": "Altitude Advantage",
            "Fenway Park": "Wind Patterns",
        }

        return weather_venues.get(venue, "Standard Venue")

    def _extract_moneyline_rec(self, bet_rec: dict[str, Any]) -> str | None:
        """Extract moneyline recommendation"""
        primary = bet_rec.get("primary_bet", "")
        if "moneyline" in primary.lower() or "ml" in primary.lower():
            return primary
        return None

    def _extract_spread_rec(self, bet_rec: dict[str, Any]) -> str | None:
        """Extract spread recommendation"""
        primary = bet_rec.get("primary_bet", "")
        if "spread" in primary.lower() or "pts" in primary.lower():
            return primary
        return None

    def _extract_total_rec(self, bet_rec: dict[str, Any]) -> str | None:
        """Extract totals recommendation"""
        primary = bet_rec.get("primary_bet", "")
        if any(word in primary.lower() for word in ["over", "under", "total"]):
            return primary
        return None

    def _assess_risk_level(self, analysis: WeatherEnhancedBetting) -> str:
        """Assess overall risk level of betting opportunity"""

        # High confidence + strong weather signal = low risk
        if analysis.confidence_score > 0.8 and abs(
                analysis.weather_impact_score - 5) > 3:
            return "low"

        # Medium confidence or moderate weather impact
        elif analysis.confidence_score > 0.7 or abs(analysis.weather_impact_score - 5) > 2:
            return "medium"

        # Lower confidence or minimal edge
        else:
            return "high"

    def _generate_pipeline_report(
        self,
        weather_analyses: list[WeatherEnhancedBetting],
        signals: list[BettingSignal],
        processing_time: float,
    ) -> PipelineReport:
        """Generate comprehensive pipeline execution report"""

        # Calculate metrics
        total_games = len(weather_analyses)
        weather_games = sum(
            1 for a in weather_analyses if a.weather_analysis.get("source") != "mock_data")
        high_confidence_bets = sum(1 for s in signals if s.bet_confidence > 0.8)

        # Expected daily EV
        expected_daily_ev = sum(
            s.expected_value *
            s.bankroll_allocation for s in signals)

        # Pipeline health score
        data_quality_scores = [a.confidence_score for a in weather_analyses]
        avg_data_quality = (sum(data_quality_scores) /
                            len(data_quality_scores) if data_quality_scores else 0)

        # Health factors
        api_health = 0.9 if total_games > 0 else 0.3
        weather_coverage = weather_games / max(total_games, 1)
        signal_generation = len(signals) / max(total_games, 1) * 10  # Scale up

        pipeline_health = (api_health + weather_coverage +
                           min(signal_generation, 1)) / 3

        return PipelineReport(
            execution_timestamp=datetime.now(UTC),
            total_games_analyzed=total_games,
            weather_games=weather_games,
            high_confidence_bets=high_confidence_bets,
            total_signals_generated=len(signals),
            expected_daily_ev=expected_daily_ev,
            pipeline_health_score=pipeline_health,
            data_quality_avg=avg_data_quality,
            processing_time_seconds=processing_time,
        )

    def _save_pipeline_outputs(
            self,
            signals: list[BettingSignal],
            report: PipelineReport):
        """Save pipeline outputs to files"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Save betting signals
            signals_file = self.signals_dir / f"betting_signals_{timestamp}.json"
            signals_data = {
                "timestamp": datetime.now().isoformat(),
                "total_signals": len(signals),
                "signals": [asdict(signal) for signal in signals],
            }

            with open(signals_file, "w") as f:
                json.dump(signals_data, f, indent=2, default=str)

            logger.info(f"💾 Betting signals saved: {signals_file}")

            # Save pipeline report
            report_file = self.reports_dir / f"pipeline_report_{timestamp}.json"
            report_data = asdict(report)

            with open(report_file, "w") as f:
                json.dump(report_data, f, indent=2, default=str)

            logger.info(f"📊 Pipeline report saved: {report_file}")

            # Save daily summary
            summary_file = (
                self.reports_dir /
                f"daily_summary_{
                    datetime.now().strftime('%Y%m%d')}.json")

            summary_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "pipeline_executions": 1,
                "total_signals": len(signals),
                "high_confidence_signals": sum(
                    1 for s in signals if s.bet_confidence > 0.8),
                "total_exposure": sum(
                    s.bankroll_allocation for s in signals),
                "expected_daily_roi": report.expected_daily_ev,
                "pipeline_health": report.pipeline_health_score,
                "last_execution": datetime.now().isoformat(),
            }

            # Append to daily summary (for multiple executions per day)
            if summary_file.exists():
                with open(summary_file) as f:
                    existing_data = json.load(f)
                existing_data["pipeline_executions"] += 1
                existing_data["total_signals"] += summary_data["total_signals"]
                existing_data["last_execution"] = summary_data["last_execution"]
                summary_data = existing_data

            with open(summary_file, "w") as f:
                json.dump(summary_data, f, indent=2, default=str)

            logger.info(f"📋 Daily summary updated: {summary_file}")

        except Exception as e:
            logger.error(f"Error saving pipeline outputs: {e}")

    def get_top_betting_opportunities(
        self, signals: list[BettingSignal], limit: int = 5
    ) -> list[BettingSignal]:
        """Get top betting opportunities sorted by expected value"""

        return sorted(signals, key=lambda s: s.expected_value, reverse=True)[:limit]

    def generate_betting_summary(
            self,
            signals: list[BettingSignal],
            report: PipelineReport) -> str:
        """Generate human-readable betting summary"""

        if not signals:
            return "No betting opportunities found in current analysis."

        summary_lines = [
            "🎯 EQ12 BETTING ANALYSIS SUMMARY",
            "=" * 50,
            f"Analysis Time: {report.execution_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Games Analyzed: {report.total_games_analyzed}",
            f"Weather Coverage: {report.weather_games}/{report.total_games_analyzed}",
            f"Betting Signals: {len(signals)}",
            f"Expected Daily ROI: {report.expected_daily_ev:.1%}",
            f"Pipeline Health: {report.pipeline_health_score:.1%}",
            "",
            "🏆 TOP BETTING OPPORTUNITIES:",
        ]

        top_signals = self.get_top_betting_opportunities(signals, 5)

        for i, signal in enumerate(top_signals, 1):
            summary_lines.extend(
                [
                    "",
                    f"{i}. {signal.teams} ({signal.sport})",
                    f"   Venue: {signal.venue}",
                    f"   Primary Bet: {signal.primary_bet}",
                    f"   Confidence: {signal.bet_confidence:.1%}",
                    f"   Expected Value: {signal.expected_value:.1%}",
                    f"   Position Size: {signal.bankroll_allocation:.1%}",
                    f"   Risk Level: {signal.risk_level.title()}",
                    f"   Weather Factor: {signal.weather_factor:.1f}/10",
                ]
            )

        summary_lines.extend(
            [
                "",
                "💰 PORTFOLIO SUMMARY:",
                f"Total Exposure: {sum(s.bankroll_allocation for s in signals):.1%}",
                f"Avg Confidence: {sum(s.bet_confidence for s in signals) / len(signals):.1%}",
                f"High Confidence Bets: {sum(1 for s in signals if s.bet_confidence > 0.8)}",
                "",
                "⚠️ RISK MANAGEMENT:",
                f"Low Risk: {sum(1 for s in signals if s.risk_level == 'low')} signals",
                f"Medium Risk: {sum(1 for s in signals if s.risk_level == 'medium')} signals",
                f"High Risk: {sum(1 for s in signals if s.risk_level == 'high')} signals",
            ]
        )

        return "\n".join(summary_lines)


async def main():
    """Test the complete production pipeline"""
    print("🚀 EQ12 PRODUCTION BETTING PIPELINE")
    print("=" * 60)
    print("Complete automated betting analysis with multi-API integration")

    # Initialize pipeline
    pipeline = EQ12ProductionBettingPipeline()

    print("\n🎯 EXECUTING COMPLETE PIPELINE...")
    print("Integrating: Sports APIs + Weather + Risk Management")

    # Run complete pipeline
    signals, report = await pipeline.run_complete_pipeline(["MLB", "NFL", "NCAAF"])

    # Display summary
    summary = pipeline.generate_betting_summary(signals, report)
    print(f"\n{summary}")

    print("\n📈 PIPELINE PERFORMANCE:")
    print(f"   Processing Time: {report.processing_time_seconds:.1f} seconds")
    print(f"   Data Quality: {report.data_quality_avg:.1%}")
    print(f"   System Health: {report.pipeline_health_score:.1%}")

    print("\n🎉 PRODUCTION PIPELINE COMPLETE!")
    print(f"Generated {len(signals)} actionable betting signals")
    print(f"Expected daily ROI: {report.expected_daily_ev:.1%}")


if __name__ == "__main__":
    asyncio.run(main())
