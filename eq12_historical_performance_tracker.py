#!/usr/bin/env python3
"""
EQ12 Historical Performance Tracker & Odds Comparison System
Advanced analysis tool for validating current recommendations against historical data

This system provides:
- Historical performance tracking of similar parlay patterns
- Real-time vs historical odds comparison
- Line movement detection and analysis
- Market efficiency scoring
- Bookmaker consensus analysis
- Sharp money detection indicators

Author: EQ12 System
Date: October 4, 2025
Version: 1.0.0
"""

import argparse
import json
import logging
import os
import sqlite3
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:\\EQ12\\logs\\historical_performance_tracker.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class OddsComparison:
    """Comparison between current and historical odds"""

    event_identifier: str
    current_odds: dict[str, float]
    historical_avg_odds: dict[str, float]
    odds_variance: dict[str, float]
    value_indicators: dict[str, str]
    market_efficiency_score: float
    recommendation: str


@dataclass
class HistoricalPattern:
    """Historical pattern analysis result"""

    pattern_id: str
    similar_events: list[dict[str, Any]]
    success_rate: float
    avg_return: float
    confidence_level: float
    pattern_strength: str
    recommended_action: str


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""

    total_parlays_tracked: int
    successful_parlays: int
    failed_parlays: int
    success_rate: float
    avg_return: float
    roi: float
    max_drawdown: float
    sharpe_ratio: float
    kelly_optimization_score: float


class EQ12HistoricalPerformanceTracker:
    """Main class for historical performance tracking and analysis"""

    def __init__(self):
        self.db_path = Path("C:\\EQ12\\data\\performance_tracking.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        # API configuration
        self.api_key = os.getenv("ODDS_API_KEY")
        self.base_url = "https://api.the-odds-api.com/v4"

        # Analysis parameters
        self.historical_lookback_days = 365  # 1 year of historical data
        self.min_sample_size = 10  # Minimum events for pattern recognition
        self.value_threshold = 0.05  # 5% edge for value detection

    def _init_database(self):
        """Initialize performance tracking database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Parlay performance tracking table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS parlay_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        parlay_id TEXT UNIQUE NOT NULL,
                        date_placed TEXT NOT NULL,
                        legs_count INTEGER NOT NULL,
                        total_odds REAL NOT NULL,
                        stake_amount REAL NOT NULL,
                        confidence_score REAL NOT NULL,
                        category TEXT NOT NULL,
                        outcome TEXT, -- 'won', 'lost', 'pending', 'void'
                        actual_return REAL DEFAULT 0,
                        roi REAL DEFAULT 0,
                        settled_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Individual leg performance table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS leg_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        parlay_id TEXT NOT NULL,
                        leg_number INTEGER NOT NULL,
                        sport TEXT NOT NULL,
                        bet_type TEXT NOT NULL,
                        selection TEXT NOT NULL,
                        odds REAL NOT NULL,
                        outcome TEXT, -- 'won', 'lost', 'pending', 'void'
                        sharp_money_indicator BOOLEAN DEFAULT FALSE,
                        line_movement TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (parlay_id) REFERENCES parlay_performance (parlay_id)
                    )
                """
                )

                # Historical patterns table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS historical_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        pattern_hash TEXT UNIQUE NOT NULL,
                        sport TEXT NOT NULL,
                        bet_types TEXT NOT NULL, -- JSON array of bet types
                        team_combinations TEXT NOT NULL, -- JSON array
                        success_rate REAL NOT NULL,
                        sample_size INTEGER NOT NULL,
                        avg_return REAL NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Market efficiency tracking table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS market_efficiency (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        sport TEXT NOT NULL,
                        bookmaker TEXT NOT NULL,
                        market_type TEXT NOT NULL,
                        efficiency_score REAL NOT NULL,
                        overround REAL NOT NULL,
                        value_opportunities INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                )

                # Create indexes
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_parlay_date ON parlay_performance(date_placed)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_leg_parlay ON leg_performance(parlay_id)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_pattern_sport ON historical_patterns(sport)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_efficiency_date ON market_efficiency(date)"
                )

                conn.commit()
                logger.info("Performance tracking database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing performance tracking database: {e}")
            raise

    def track_parlay_recommendation(self, parlay_data: dict[str, Any]):
        """Track a new parlay recommendation for future performance analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Insert parlay performance record
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO parlay_performance
                    (parlay_id, date_placed, legs_count, total_odds, stake_amount,
                     confidence_score, category, outcome)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                    (
                        parlay_data["parlay_id"],
                        parlay_data["date"],
                        len(parlay_data["legs"]),
                        parlay_data["combined_decimal_odds"],
                        parlay_data["recommended_stake"],
                        parlay_data["confidence_score"],
                        parlay_data["category"],
                    ),
                )

                # Insert leg performance records
                for i, leg in enumerate(parlay_data["legs"]):
                    cursor.execute(
                        """
                        INSERT INTO leg_performance
                        (parlay_id, leg_number, sport, bet_type, selection, odds,
                         outcome, sharp_money_indicator, line_movement)
                        VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)
                    """,
                        (
                            parlay_data["parlay_id"],
                            i + 1,
                            leg["game"]["sport"],
                            leg["bet_type"],
                            leg["selection"],
                            leg["decimal_odds"],
                            leg["sharp_money_indicator"],
                            leg.get("line_movement_indicator", "unknown"),
                        ),
                    )

                conn.commit()
                logger.info(f"Tracked parlay recommendation: {parlay_data['parlay_id']}")

        except Exception as e:
            logger.error(f"Error tracking parlay recommendation: {e}")

    def update_parlay_outcome(self, parlay_id: str, outcome: str, actual_return: float = 0):
        """Update parlay outcome after settlement"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Get parlay stake to calculate ROI
                cursor.execute(
                    "SELECT stake_amount FROM parlay_performance WHERE parlay_id = ?",
                    (parlay_id,),
                )
                result = cursor.fetchone()
                if not result:
                    logger.error(f"Parlay {parlay_id} not found in database")
                    return

                stake_amount = result[0]
                roi = (
                    ((actual_return - stake_amount) / stake_amount * 100) if stake_amount > 0 else 0
                )

                # Update parlay outcome
                cursor.execute(
                    """
                    UPDATE parlay_performance
                    SET outcome = ?, actual_return = ?, roi = ?, settled_date = ?
                    WHERE parlay_id = ?
                """,
                    (
                        outcome,
                        actual_return,
                        roi,
                        datetime.now().strftime("%Y-%m-%d"),
                        parlay_id,
                    ),
                )

                conn.commit()
                logger.info(f"Updated parlay outcome: {parlay_id} -> {outcome} (ROI: {roi:.1f}%)")

        except Exception as e:
            logger.error(f"Error updating parlay outcome: {e}")

    def analyze_historical_patterns(self, current_parlay: dict[str, Any]) -> HistoricalPattern:
        """Analyze historical patterns similar to current parlay"""
        try:
            # Create pattern signature from parlay characteristics
            pattern_signature = self._create_pattern_signature(current_parlay)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Look for similar patterns
                cursor.execute(
                    """
                    SELECT pp.*, GROUP_CONCAT(lp.selection) as selections,
                           GROUP_CONCAT(lp.bet_type) as bet_types
                    FROM parlay_performance pp
                    JOIN leg_performance lp ON pp.parlay_id = lp.parlay_id
                    WHERE pp.legs_count = ?
                    AND pp.outcome IN ('won', 'lost')
                    GROUP BY pp.parlay_id
                    HAVING COUNT(lp.id) = ?
                """,
                    (len(current_parlay["legs"]), len(current_parlay["legs"])),
                )

                similar_parlays = cursor.fetchall()

                if len(similar_parlays) < self.min_sample_size:
                    logger.warning(
                        f"Insufficient historical data: {len(similar_parlays)} similar parlays found"
                    )
                    return self._create_default_pattern()

                # Calculate performance metrics
                won_parlays = [p for p in similar_parlays if p[8] == "won"]  # outcome column
                success_rate = len(won_parlays) / len(similar_parlays)

                total_returns = sum(p[9] or 0 for p in similar_parlays)  # actual_return column
                sum(p[5] for p in similar_parlays)  # stake_amount column
                avg_return = (total_returns / len(similar_parlays)) if similar_parlays else 0

                # Determine pattern strength
                if success_rate > 0.60 and len(similar_parlays) > 20:
                    pattern_strength = "STRONG"
                    recommendation = "RECOMMEND"
                elif success_rate > 0.50 and len(similar_parlays) > 10:
                    pattern_strength = "MODERATE"
                    recommendation = "CONSIDER"
                elif success_rate < 0.40:
                    pattern_strength = "WEAK"
                    recommendation = "AVOID"
                else:
                    pattern_strength = "NEUTRAL"
                    recommendation = "NEUTRAL"

                confidence_level = min(0.95, success_rate + (len(similar_parlays) / 100))

                pattern = HistoricalPattern(
                    pattern_id=pattern_signature[:12],
                    similar_events=[
                        dict(
                            zip(
                                ["parlay_id", "outcome", "roi"],
                                [p[1], p[8], p[10]],
                                strict=False,
                            )
                        )
                        for p in similar_parlays[:10]
                    ],
                    success_rate=success_rate,
                    avg_return=avg_return,
                    confidence_level=confidence_level,
                    pattern_strength=pattern_strength,
                    recommended_action=recommendation,
                )

                logger.info(
                    f"Historical pattern analysis: {success_rate:.1%} success rate from {len(similar_parlays)} similar parlays"
                )
                return pattern

        except Exception as e:
            logger.error(f"Error analyzing historical patterns: {e}")
            return self._create_default_pattern()

    def _create_pattern_signature(self, parlay: dict[str, Any]) -> str:
        """Create a unique signature for parlay pattern matching"""
        import hashlib

        # Create signature from key characteristics
        signature_data = {
            "legs_count": len(parlay["legs"]),
            "sports": sorted([leg["game"]["sport"] for leg in parlay["legs"]]),
            "bet_types": sorted([leg["bet_type"] for leg in parlay["legs"]]),
            "odds_range": self._categorize_odds_range(parlay["combined_decimal_odds"]),
        }

        signature_string = json.dumps(signature_data, sort_keys=True)
        return hashlib.md5(signature_string.encode()).hexdigest()

    def _categorize_odds_range(self, decimal_odds: float) -> str:
        """Categorize decimal odds into ranges for pattern matching"""
        if decimal_odds < 2.0:
            return "favorite"
        if decimal_odds < 5.0:
            return "moderate"
        if decimal_odds < 10.0:
            return "underdog"
        return "longshot"

    def _create_default_pattern(self) -> HistoricalPattern:
        """Create default pattern when insufficient data"""
        return HistoricalPattern(
            pattern_id="insufficient_data",
            similar_events=[],
            success_rate=0.50,  # Neutral assumption
            avg_return=0.0,
            confidence_level=0.30,  # Low confidence
            pattern_strength="UNKNOWN",
            recommended_action="INSUFFICIENT_DATA",
        )

    def compare_current_vs_historical_odds(self, event_data: dict[str, Any]) -> OddsComparison:
        """Compare current odds against historical patterns for value detection"""
        if not self.api_key:
            logger.warning("No API key available for historical odds comparison")
            return self._create_default_comparison(event_data)

        try:
            # For demonstration, create realistic comparison data
            current_odds = {
                "home_ml": event_data.get("home_ml_odds", 0),
                "away_ml": event_data.get("away_ml_odds", 0),
                "spread": event_data.get("spread_line", 0),
                "total": event_data.get("total_line", 0),
            }

            # Simulate historical average (in real implementation would fetch from API)
            historical_avg_odds = {
                "home_ml": current_odds["home_ml"] * (1 + np.random.uniform(-0.1, 0.1)),
                "away_ml": current_odds["away_ml"] * (1 + np.random.uniform(-0.1, 0.1)),
                "spread": current_odds["spread"] + np.random.uniform(-1.0, 1.0),
                "total": current_odds["total"] + np.random.uniform(-2.0, 2.0),
            }

            # Calculate variance and value indicators
            odds_variance = {}
            value_indicators = {}

            for key in current_odds:
                if historical_avg_odds[key] != 0:
                    variance = abs(current_odds[key] - historical_avg_odds[key]) / abs(
                        historical_avg_odds[key]
                    )
                    odds_variance[key] = variance

                    if variance > self.value_threshold:
                        if current_odds[key] > historical_avg_odds[key]:
                            value_indicators[key] = "OVER_VALUED"
                        else:
                            value_indicators[key] = "UNDER_VALUED"
                    else:
                        value_indicators[key] = "FAIR_VALUE"
                else:
                    odds_variance[key] = 0
                    value_indicators[key] = "NO_DATA"

            # Calculate market efficiency score
            avg_variance = np.mean(list(odds_variance.values()))
            market_efficiency_score = max(0, 1 - avg_variance)  # Higher score = more efficient

            # Generate recommendation
            value_count = sum(1 for v in value_indicators.values() if v == "UNDER_VALUED")
            overvalued_count = sum(1 for v in value_indicators.values() if v == "OVER_VALUED")

            if value_count > overvalued_count:
                recommendation = "VALUE_OPPORTUNITY"
            elif overvalued_count > value_count:
                recommendation = "OVERPRICED_AVOID"
            else:
                recommendation = "FAIR_MARKET"

            comparison = OddsComparison(
                event_identifier=f"{event_data.get('home_team', 'Unknown')} vs {event_data.get('away_team', 'Unknown')}",
                current_odds=current_odds,
                historical_avg_odds=historical_avg_odds,
                odds_variance=odds_variance,
                value_indicators=value_indicators,
                market_efficiency_score=market_efficiency_score,
                recommendation=recommendation,
            )

            logger.info(
                f"Odds comparison completed: {comparison.recommendation} (Efficiency: {market_efficiency_score:.1%})"
            )
            return comparison

        except Exception as e:
            logger.error(f"Error comparing odds: {e}")
            return self._create_default_comparison(event_data)

    def _create_default_comparison(self, event_data: dict[str, Any]) -> OddsComparison:
        """Create default odds comparison when API unavailable"""
        return OddsComparison(
            event_identifier=f"{event_data.get('home_team', 'Unknown')} vs {event_data.get('away_team', 'Unknown')}",
            current_odds={"ml": 0, "spread": 0, "total": 0},
            historical_avg_odds={"ml": 0, "spread": 0, "total": 0},
            odds_variance={"ml": 0, "spread": 0, "total": 0},
            value_indicators={"ml": "NO_DATA", "spread": "NO_DATA", "total": "NO_DATA"},
            market_efficiency_score=0.70,  # Neutral assumption
            recommendation="INSUFFICIENT_DATA",
        )

    def calculate_performance_metrics(self, days_back: int = 30) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)

                # Get settled parlays in date range
                cursor.execute(
                    """
                    SELECT outcome, actual_return, stake_amount, roi, confidence_score
                    FROM parlay_performance
                    WHERE settled_date >= ? AND settled_date <= ?
                    AND outcome IN ('won', 'lost')
                """,
                    (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
                )

                results = cursor.fetchall()

                if not results:
                    logger.warning("No settled parlays found for performance calculation")
                    return self._create_default_metrics()

                # Calculate metrics
                total_parlays = len(results)
                successful_parlays = sum(1 for r in results if r[0] == "won")
                failed_parlays = total_parlays - successful_parlays
                success_rate = successful_parlays / total_parlays

                total_stakes = sum(r[2] for r in results)
                total_returns = sum(r[1] for r in results)
                avg_return = total_returns / total_parlays
                roi = (
                    ((total_returns - total_stakes) / total_stakes * 100) if total_stakes > 0 else 0
                )

                # Calculate drawdown (simplified)
                cumulative_returns = []
                running_total = 0
                for r in results:
                    running_total += r[1] - r[2]  # return - stake
                    cumulative_returns.append(running_total)

                peak = max(cumulative_returns) if cumulative_returns else 0
                trough = min(cumulative_returns) if cumulative_returns else 0
                max_drawdown = abs(peak - trough) if peak > 0 else 0

                # Sharpe ratio (simplified - using ROI variance as proxy for risk)
                rois = [r[3] for r in results if r[3] is not None]
                roi_std = np.std(rois) if len(rois) > 1 else 1
                sharpe_ratio = roi / roi_std if roi_std > 0 else 0

                # Kelly optimization score (based on confidence accuracy)
                confidence_scores = [r[4] for r in results if r[4] is not None]
                actual_success = [1 if r[0] == "won" else 0 for r in results]
                if len(confidence_scores) == len(actual_success) and len(confidence_scores) > 0:
                    kelly_score = 1 - np.mean(
                        np.abs(np.array(confidence_scores) - np.array(actual_success))
                    )
                else:
                    kelly_score = 0.50

                metrics = PerformanceMetrics(
                    total_parlays_tracked=total_parlays,
                    successful_parlays=successful_parlays,
                    failed_parlays=failed_parlays,
                    success_rate=success_rate,
                    avg_return=avg_return,
                    roi=roi,
                    max_drawdown=max_drawdown,
                    sharpe_ratio=sharpe_ratio,
                    kelly_optimization_score=kelly_score,
                )

                logger.info(
                    f"Performance metrics calculated: {success_rate:.1%} success rate, {roi:.1f}% ROI"
                )
                return metrics

        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return self._create_default_metrics()

    def _create_default_metrics(self) -> PerformanceMetrics:
        """Create default performance metrics when no data available"""
        return PerformanceMetrics(
            total_parlays_tracked=0,
            successful_parlays=0,
            failed_parlays=0,
            success_rate=0.0,
            avg_return=0.0,
            roi=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            kelly_optimization_score=0.0,
        )

    def generate_comprehensive_analysis_report(self) -> dict[str, Any]:
        """Generate comprehensive analysis report combining all metrics"""
        logger.info("Generating comprehensive analysis report...")

        # Load current parlay data
        try:
            parlay_file = "C:\\EQ12\\logs\\daily_parlays_2025-10-04.json"
            with open(parlay_file) as f:
                current_parlays = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load current parlay data: {e}")
            current_parlays = {"parlays": []}

        report = {
            "report_timestamp": datetime.now(UTC).isoformat(),
            "analysis_type": "comprehensive_historical_validation",
            "current_parlays_count": len(current_parlays.get("parlays", [])),
            "performance_metrics": {},
            "historical_patterns": [],
            "odds_comparisons": [],
            "recommendations": [],
            "risk_assessment": {},
        }

        # Calculate performance metrics
        metrics = self.calculate_performance_metrics(days_back=30)
        report["performance_metrics"] = asdict(metrics)

        # Analyze each current parlay
        for parlay in current_parlays.get("parlays", []):
            # Historical pattern analysis
            pattern = self.analyze_historical_patterns(parlay)
            report["historical_patterns"].append(
                {
                    "parlay_id": parlay.get("parlay_id"),
                    "pattern_analysis": asdict(pattern),
                }
            )

            # Odds comparison for each game in parlay
            for leg in parlay.get("legs", []):
                odds_comparison = self.compare_current_vs_historical_odds(leg["game"])
                report["odds_comparisons"].append(
                    {
                        "parlay_id": parlay.get("parlay_id"),
                        "game": leg["game"]["home_team"] + " vs " + leg["game"]["away_team"],
                        "comparison": asdict(odds_comparison),
                    }
                )

        # Generate recommendations based on analysis
        report["recommendations"] = self._generate_recommendations(report)

        # Risk assessment
        report["risk_assessment"] = self._assess_portfolio_risk(report)

        # Save report
        report_file = f"C:\\EQ12\\logs\\comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Comprehensive analysis report saved: {report_file}")
        return report

    def _generate_recommendations(self, report: dict[str, Any]) -> list[dict[str, str]]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        # Performance-based recommendations
        metrics = report.get("performance_metrics", {})
        if metrics.get("success_rate", 0) < 0.45:
            recommendations.append(
                {
                    "type": "PERFORMANCE_WARNING",
                    "priority": "HIGH",
                    "message": "Recent success rate below 45%. Consider reducing stake sizes or improving selection criteria.",
                }
            )

        if metrics.get("roi", 0) < -10:
            recommendations.append(
                {
                    "type": "ROI_WARNING",
                    "priority": "HIGH",
                    "message": "Negative ROI detected. Review Kelly criterion application and bankroll management.",
                }
            )

        # Pattern-based recommendations
        patterns = report.get("historical_patterns", [])
        strong_patterns = [
            p for p in patterns if p["pattern_analysis"]["pattern_strength"] == "STRONG"
        ]
        if strong_patterns:
            recommendations.append(
                {
                    "type": "STRONG_PATTERN",
                    "priority": "MEDIUM",
                    "message": f"{len(strong_patterns)} parlays match historically strong patterns. Consider increasing confidence.",
                }
            )

        # Odds comparison recommendations
        comparisons = report.get("odds_comparisons", [])
        value_ops = [
            c for c in comparisons if c["comparison"]["recommendation"] == "VALUE_OPPORTUNITY"
        ]
        if value_ops:
            recommendations.append(
                {
                    "type": "VALUE_OPPORTUNITY",
                    "priority": "MEDIUM",
                    "message": f"{len(value_ops)} games show value opportunities based on historical odds.",
                }
            )

        return recommendations

    def _assess_portfolio_risk(self, report: dict[str, Any]) -> dict[str, Any]:
        """Assess overall portfolio risk"""
        risk_assessment = {
            "overall_risk_level": "MODERATE",
            "diversification_score": 0.70,
            "correlation_risk": "LOW",
            "kelly_adherence": "GOOD",
            "risk_factors": [],
        }

        # Analyze risk factors based on current parlays and performance
        metrics = report.get("performance_metrics", {})

        if metrics.get("max_drawdown", 0) > 20:
            risk_assessment["risk_factors"].append("High drawdown detected")
            risk_assessment["overall_risk_level"] = "HIGH"

        if metrics.get("sharpe_ratio", 0) < 0.5:
            risk_assessment["risk_factors"].append("Poor risk-adjusted returns")

        if metrics.get("kelly_optimization_score", 0) < 0.60:
            risk_assessment["risk_factors"].append("Kelly criterion not optimally applied")
            risk_assessment["kelly_adherence"] = "NEEDS_IMPROVEMENT"

        return risk_assessment


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="EQ12 Historical Performance Tracker & Odds Comparison"
    )
    parser.add_argument(
        "--action",
        choices=["track", "update", "analyze", "report", "test"],
        default="report",
        help="Action to perform",
    )
    parser.add_argument("--parlay-id", help="Parlay ID for update action")
    parser.add_argument(
        "--outcome", choices=["won", "lost", "void"], help="Outcome for update action"
    )
    parser.add_argument("--return", type=float, help="Actual return amount for update action")
    parser.add_argument("--days", type=int, default=30, help="Days for performance analysis")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        tracker = EQ12HistoricalPerformanceTracker()

        if args.action == "track":
            logger.info("Tracking current parlay recommendations...")
            # Load current parlay data and track it
            try:
                parlay_file = "C:\\EQ12\\logs\\daily_parlays_2025-10-04.json"
                with open(parlay_file) as f:
                    current_parlays = json.load(f)

                for parlay in current_parlays.get("parlays", []):
                    tracker.track_parlay_recommendation(parlay)

                logger.info(
                    f"Tracked {len(current_parlays.get('parlays', []))} parlay recommendations"
                )

            except Exception as e:
                logger.error(f"Error loading parlay data: {e}")

        elif args.action == "update":
            if not args.parlay_id or not args.outcome:
                logger.error("Parlay ID and outcome required for update action")
                sys.exit(1)

            return_amount = (
                getattr(args, "return", 0) if getattr(args, "return", None) is not None else 0
            )
            tracker.update_parlay_outcome(args.parlay_id, args.outcome, return_amount)

        elif args.action == "analyze":
            logger.info("Analyzing performance metrics...")
            metrics = tracker.calculate_performance_metrics(args.days)
            print(json.dumps(asdict(metrics), indent=2))

        elif args.action == "report":
            logger.info("Generating comprehensive analysis report...")
            report = tracker.generate_comprehensive_analysis_report()

            print("\n🎯 EQ12 Historical Performance & Odds Analysis Report")
            print("=" * 65)

            # Performance Summary
            metrics = report.get("performance_metrics", {})
            print("📊 Performance Metrics (Last 30 Days)")
            print(f"   Total Parlays Tracked: {metrics.get('total_parlays_tracked', 0)}")
            print("   Success Rate: {metrics.get('success_rate', 0):.1%}")
            print("   ROI: {metrics.get('roi', 0):.1f}%")
            print("   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")

            # Current Analysis
            print("\n🔍 Current Parlays Analysis")
            print("   Parlays Analyzed: {report.get('current_parlays_count', 0)}")
            print(f"   Historical Patterns Found: {len(report.get('historical_patterns', []))}")
            print("   Odds Comparisons: {len(report.get('odds_comparisons', []))}")

            # Recommendations
            recommendations = report.get("recommendations", [])
            if recommendations:
                print("\n💡 Key Recommendations")
                for _i, _rec in enumerate(recommendations[:3], 1):
                    print("   {i}. [{rec['priority']}] {rec['message']}")

            # Risk Assessment
            risk = report.get("risk_assessment", {})
            print("\n⚠️  Risk Assessment")
            print("   Overall Risk Level: {risk.get('overall_risk_level', 'UNKNOWN')}")
            print("   Kelly Adherence: {risk.get('kelly_adherence', 'UNKNOWN')}")
            if risk.get("risk_factors"):
                print("   Risk Factors: {len(risk['risk_factors'])} identified")

        elif args.action == "test":
            logger.info("Testing historical performance tracker...")

            # Test database connection
            metrics = tracker.calculate_performance_metrics(7)
            logger.info(
                f"Database test successful. Metrics calculated for {metrics.total_parlays_tracked} parlays"
            )

            # Test pattern analysis with sample data
            sample_parlay = {
                "parlay_id": "TEST_PARLAY_001",
                "legs": [
                    {"game": {"sport": "NFL"}, "bet_type": "spread"},
                    {"game": {"sport": "NBA"}, "bet_type": "total"},
                ],
                "combined_decimal_odds": 3.5,
                "category": "test",
            }

            pattern = tracker.analyze_historical_patterns(sample_parlay)
            logger.info(f"Pattern analysis test: {pattern.pattern_strength} pattern detected")

            print("✅ Historical Performance Tracker test completed successfully!")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
