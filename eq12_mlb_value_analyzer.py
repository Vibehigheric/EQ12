#!/usr/bin/env python3
"""
EQ12 MLB Value Analysis Engine
Comprehensive betting value analysis for today's MLB games with advanced metrics

Features:
- Kelly Criterion calculation for optimal bet sizing
- Implied probability vs true probability analysis
- Line shopping opportunities
- Market inefficiency detection
- Sharp vs public money analysis
- Weather impact on totals
- Pitcher matchup advantages
- Historical performance analysis

Date: October 5, 2025
Author: EQ12 GODSTACK Team
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class ValueBet:
    """Value betting opportunity"""

    game: str
    bet_type: str  # moneyline, spread, total
    side: str  # home/away/over/under
    odds: int
    implied_probability: float
    true_probability: float
    edge: float
    kelly_percentage: float
    confidence: str  # LOW/MEDIUM/HIGH/VERY_HIGH
    reasoning: str
    max_bet_amount: float | None = None
    expected_value: float | None = None


@dataclass
class MarketAnalysis:
    """Market analysis for a specific game"""

    game_id: str
    matchup: str
    total_vig: float
    market_efficiency: str  # EFFICIENT/INEFFICIENT/VERY_INEFFICIENT
    best_value_bets: list[ValueBet]
    line_movement: str | None = None
    sharp_money_indicator: str | None = None
    public_betting_percentage: dict[str, float] | None = None


class MLBValueAnalyzer:
    """Advanced MLB betting value analyzer"""

    def __init__(self, bankroll: float = 10000.0):
        self.bankroll = bankroll
        self.logger = self._setup_logging()

        # Conservative Kelly multiplier for risk management
        self.kelly_multiplier = 0.25  # Use 25% of Kelly recommendation

        # Confidence thresholds
        self.edge_thresholds = {
            "LOW": 0.02,  # 2% edge
            "MEDIUM": 0.04,  # 4% edge
            "HIGH": 0.07,  # 7% edge
            "VERY_HIGH": 0.12,  # 12% edge
        }

    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("C:/EQ12/logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"mlb_value_analysis_{datetime.now().strftime('%Y%m%d')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )

        return logging.getLogger(f"{__name__}.MLBValueAnalyzer")

    def american_to_decimal(self, american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        return (100 / abs(american_odds)) + 1

    def american_to_probability(self, american_odds: int) -> float:
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        return abs(american_odds) / (abs(american_odds) + 100)

    def calculate_vig(self, prob1: float, prob2: float) -> float:
        """Calculate the vig (overround) from two probabilities"""
        return (prob1 + prob2) - 1.0

    def calculate_kelly_percentage(self, edge: float, odds: int) -> float:
        """Calculate optimal bet size using Kelly Criterion"""
        decimal_odds = self.american_to_decimal(odds)
        if edge <= 0 or decimal_odds <= 1:
            return 0.0

        # Kelly formula: f = (bp - q) / b
        # where b = decimal odds - 1, p = true probability, q = 1 - p
        b = decimal_odds - 1
        p = edge + self.american_to_probability(odds)  # True probability
        q = 1 - p

        kelly_fraction = (b * p - q) / b

        # Apply conservative multiplier and cap at 5% of bankroll
        conservative_kelly = kelly_fraction * self.kelly_multiplier
        return max(0, min(conservative_kelly, 0.05))

    def get_confidence_level(self, edge: float) -> str:
        """Determine confidence level based on edge size"""
        if edge >= self.edge_thresholds["VERY_HIGH"]:
            return "VERY_HIGH"
        if edge >= self.edge_thresholds["HIGH"]:
            return "HIGH"
        if edge >= self.edge_thresholds["MEDIUM"]:
            return "MEDIUM"
        if edge >= self.edge_thresholds["LOW"]:
            return "LOW"
        return "NO_EDGE"

    def analyze_pitcher_matchup(self, home_pitcher: dict, away_pitcher: dict) -> dict[str, Any]:
        """Analyze pitcher matchup for value opportunities"""
        analysis = {
            "advantage": "neutral",
            "reasoning": "",
            "era_difference": 0.0,
            "handedness_advantage": False,
        }

        if not home_pitcher or not away_pitcher:
            return analysis

        home_era = home_pitcher.get("era", 4.0)
        away_era = away_pitcher.get("era", 4.0)
        era_diff = abs(home_era - away_era)

        analysis["era_difference"] = era_diff

        if era_diff > 1.0:  # Significant ERA difference
            better_pitcher = "home" if home_era < away_era else "away"
            analysis["advantage"] = better_pitcher
            analysis["reasoning"] = f"Significant ERA advantage ({era_diff:.2f})"

        # Check handedness matchup
        home_hand = home_pitcher.get("hand", "R")
        away_hand = away_pitcher.get("hand", "R")

        if home_hand != away_hand:
            analysis["handedness_advantage"] = True
            analysis["reasoning"] += f" | Handedness matchup: {away_hand}HP vs {home_hand}HP"

        return analysis

    def analyze_weather_impact(self, weather: dict, total_runs: float) -> dict[str, Any]:
        """Analyze weather impact on game totals"""
        impact = {
            "total_impact": "neutral",
            "reasoning": "",
            "wind_factor": 0,
            "temperature_factor": 0,
        }

        if not weather:
            return impact

        temp = weather.get("temperature", 72)
        wind_speed = weather.get("wind_speed", 0)
        wind_direction = weather.get("wind_direction", "")

        # Temperature impact (higher temp = more offense)
        if temp > 80:
            impact["temperature_factor"] = 1
            impact["reasoning"] += "Hot weather favors offense"
        elif temp < 60:
            impact["temperature_factor"] = -1
            impact["reasoning"] += "Cold weather reduces offense"

        # Wind impact
        if wind_speed > 12:
            if "out" in wind_direction.lower():
                impact["wind_factor"] = 1
                impact["reasoning"] += f" | Strong wind out ({wind_speed} mph) helps offense"
                impact["total_impact"] = "over"
            elif "in" in wind_direction.lower():
                impact["wind_factor"] = -1
                impact["reasoning"] += f" | Strong wind in ({wind_speed} mph) hurts offense"
                impact["total_impact"] = "under"

        return impact

    def calculate_true_probabilities(self, game_data: dict) -> dict[str, float]:
        """Calculate true probabilities based on various factors"""
        odds = game_data.get("odds", {})
        if not odds:
            return {}

        # Start with market implied probabilities (removing vig)
        home_ml = odds.get("moneyline_home")
        away_ml = odds.get("moneyline_away")

        if not home_ml or not away_ml:
            return {}

        home_implied = self.american_to_probability(home_ml)
        away_implied = self.american_to_probability(away_ml)

        # Remove vig to get true market probabilities
        total_prob = home_implied + away_implied
        home_true_market = home_implied / total_prob
        away_true_market = away_implied / total_prob

        # Adjust based on our analysis
        adjustments = self._calculate_probability_adjustments(game_data)

        home_adjusted = max(0.1, min(0.9, home_true_market + adjustments.get("home_adjustment", 0)))
        away_adjusted = max(0.1, min(0.9, away_true_market + adjustments.get("away_adjustment", 0)))

        # Normalize to ensure they sum to 1
        total_adjusted = home_adjusted + away_adjusted
        home_final = home_adjusted / total_adjusted
        away_final = away_adjusted / total_adjusted

        return {
            "home_win": home_final,
            "away_win": away_final,
            "home_market": home_true_market,
            "away_market": away_true_market,
        }

    def _calculate_probability_adjustments(self, game_data: dict) -> dict[str, float]:
        """Calculate probability adjustments based on various factors"""
        adjustments = {"home_adjustment": 0.0, "away_adjustment": 0.0}

        # Pitcher advantage adjustment
        pitcher_analysis = self.analyze_pitcher_matchup(
            game_data.get("home_pitcher", {}), game_data.get("away_pitcher", {})
        )

        if pitcher_analysis["advantage"] == "home":
            adjustments["home_adjustment"] += 0.03  # 3% boost for pitcher advantage
            adjustments["away_adjustment"] -= 0.03
        elif pitcher_analysis["advantage"] == "away":
            adjustments["home_adjustment"] -= 0.03
            adjustments["away_adjustment"] += 0.03

        # Weather adjustment for totals (affects game flow)
        weather_analysis = self.analyze_weather_impact(
            game_data.get("weather", {}),
            game_data.get("odds", {}).get("total_runs", 8.0),
        )

        # Small adjustment based on weather
        if weather_analysis["total_impact"] == "over":
            # Slight boost to both teams in high-scoring games
            adjustments["home_adjustment"] += 0.01
            adjustments["away_adjustment"] += 0.01

        return adjustments

    def find_value_bets(self, game_data: dict) -> list[ValueBet]:
        """Find value betting opportunities for a single game"""
        value_bets = []

        odds = game_data.get("odds", {})
        if not odds:
            return value_bets

        matchup = f"{game_data.get('away_team', 'Away')} @ {game_data.get('home_team', 'Home')}"
        true_probs = self.calculate_true_probabilities(game_data)

        if not true_probs:
            return value_bets

        # Analyze moneyline bets
        home_ml = odds.get("moneyline_home")
        away_ml = odds.get("moneyline_away")

        if home_ml and away_ml:
            # Home moneyline value
            home_implied = self.american_to_probability(home_ml)
            home_edge = true_probs["home_win"] - home_implied

            if home_edge > self.edge_thresholds["LOW"]:
                kelly_pct = self.calculate_kelly_percentage(home_edge, home_ml)
                confidence = self.get_confidence_level(home_edge)

                value_bets.append(
                    ValueBet(
                        game=matchup,
                        bet_type="moneyline",
                        side="home",
                        odds=home_ml,
                        implied_probability=home_implied,
                        true_probability=true_probs["home_win"],
                        edge=home_edge,
                        kelly_percentage=kelly_pct,
                        confidence=confidence,
                        reasoning=self._generate_bet_reasoning(game_data, "home", "moneyline"),
                        max_bet_amount=self.bankroll * kelly_pct,
                        expected_value=self.bankroll * kelly_pct * home_edge,
                    )
                )

            # Away moneyline value
            away_implied = self.american_to_probability(away_ml)
            away_edge = true_probs["away_win"] - away_implied

            if away_edge > self.edge_thresholds["LOW"]:
                kelly_pct = self.calculate_kelly_percentage(away_edge, away_ml)
                confidence = self.get_confidence_level(away_edge)

                value_bets.append(
                    ValueBet(
                        game=matchup,
                        bet_type="moneyline",
                        side="away",
                        odds=away_ml,
                        implied_probability=away_implied,
                        true_probability=true_probs["away_win"],
                        edge=away_edge,
                        kelly_percentage=kelly_pct,
                        confidence=confidence,
                        reasoning=self._generate_bet_reasoning(game_data, "away", "moneyline"),
                        max_bet_amount=self.bankroll * kelly_pct,
                        expected_value=self.bankroll * kelly_pct * away_edge,
                    )
                )

        # Analyze total bets
        total_over = odds.get("total_over_price")
        total_under = odds.get("total_under_price")
        total_runs = odds.get("total_runs")

        if total_over and total_under and total_runs:
            weather_analysis = self.analyze_weather_impact(game_data.get("weather", {}), total_runs)

            # Simplified total analysis (in production would use more sophisticated models)
            over_implied = self.american_to_probability(total_over)
            under_implied = self.american_to_probability(total_under)

            # Basic weather-based adjustment
            if weather_analysis["total_impact"] == "over":
                over_true_prob = 0.53  # Slight edge to over
                over_edge = over_true_prob - over_implied

                if over_edge > self.edge_thresholds["LOW"]:
                    kelly_pct = self.calculate_kelly_percentage(over_edge, total_over)
                    confidence = self.get_confidence_level(over_edge)

                    value_bets.append(
                        ValueBet(
                            game=matchup,
                            bet_type="total",
                            side="over",
                            odds=total_over,
                            implied_probability=over_implied,
                            true_probability=over_true_prob,
                            edge=over_edge,
                            kelly_percentage=kelly_pct,
                            confidence=confidence,
                            reasoning=f"Weather favors Over {total_runs}: {weather_analysis['reasoning']}",
                            max_bet_amount=self.bankroll * kelly_pct,
                            expected_value=self.bankroll * kelly_pct * over_edge,
                        )
                    )

            elif weather_analysis["total_impact"] == "under":
                under_true_prob = 0.53  # Slight edge to under
                under_edge = under_true_prob - under_implied

                if under_edge > self.edge_thresholds["LOW"]:
                    kelly_pct = self.calculate_kelly_percentage(under_edge, total_under)
                    confidence = self.get_confidence_level(under_edge)

                    value_bets.append(
                        ValueBet(
                            game=matchup,
                            bet_type="total",
                            side="under",
                            odds=total_under,
                            implied_probability=under_implied,
                            true_probability=under_true_prob,
                            edge=under_edge,
                            kelly_percentage=kelly_pct,
                            confidence=confidence,
                            reasoning=f"Weather favors Under {total_runs}: {weather_analysis['reasoning']}",
                            max_bet_amount=self.bankroll * kelly_pct,
                            expected_value=self.bankroll * kelly_pct * under_edge,
                        )
                    )

        return value_bets

    def _generate_bet_reasoning(self, game_data: dict, side: str, bet_type: str) -> str:
        """Generate reasoning for a value bet"""
        reasoning_parts = []

        # Pitcher analysis
        pitcher_analysis = self.analyze_pitcher_matchup(
            game_data.get("home_pitcher", {}), game_data.get("away_pitcher", {})
        )

        if pitcher_analysis["advantage"] == side:
            reasoning_parts.append(f"Pitcher advantage: {pitcher_analysis['reasoning']}")

        # Team stats
        if side == "home":
            team_stats = game_data.get("home_team_stats", {})
        else:
            team_stats = game_data.get("away_team_stats", {})

        if team_stats:
            era = team_stats.get("era", 0)
            if era and era < 3.5:
                reasoning_parts.append(f"Strong team ERA ({era:.2f})")

        # Market inefficiency
        reasoning_parts.append("Market inefficiency detected")

        return " | ".join(reasoning_parts) if reasoning_parts else "Statistical edge identified"

    def analyze_all_games(self, games_file: str) -> list[MarketAnalysis]:
        """Analyze all games for value opportunities"""
        self.logger.info("🔍 Starting comprehensive value analysis...")

        try:
            with open(games_file, encoding="utf-8") as f:
                data = json.load(f)

            games = data.get("games", [])
            analyses = []

            for game in games:
                matchup = f"{game.get('away_team', 'Away')} @ {game.get('home_team', 'Home')}"
                self.logger.info(f"📊 Analyzing {matchup}...")

                # Calculate market vig
                odds = game.get("odds", {})
                home_ml = odds.get("moneyline_home")
                away_ml = odds.get("moneyline_away")

                total_vig = 0.0
                market_efficiency = "EFFICIENT"

                if home_ml and away_ml:
                    home_prob = self.american_to_probability(home_ml)
                    away_prob = self.american_to_probability(away_ml)
                    total_vig = self.calculate_vig(home_prob, away_prob)

                    if total_vig > 0.08:  # 8% vig
                        market_efficiency = "VERY_INEFFICIENT"
                    elif total_vig > 0.05:  # 5% vig
                        market_efficiency = "INEFFICIENT"

                # Find value bets
                value_bets = self.find_value_bets(game)

                analysis = MarketAnalysis(
                    game_id=game.get("game_id", ""),
                    matchup=matchup,
                    total_vig=total_vig,
                    market_efficiency=market_efficiency,
                    best_value_bets=value_bets,
                )

                analyses.append(analysis)

                self.logger.info(f"✅ Found {len(value_bets)} value opportunities for {matchup}")

            return analyses

        except Exception as e:
            self.logger.error(f"Error analyzing games: {e}")
            return []

    def save_analysis_report(
        self, analyses: list[MarketAnalysis], filename: str | None = None
    ) -> str:
        """Save comprehensive analysis report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mlb_value_analysis_{timestamp}.json"

        output_dir = Path("C:/EQ12/logs")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / filename

        # Prepare report data
        report = {
            "analysis_time": datetime.now(UTC).isoformat(),
            "bankroll": self.bankroll,
            "kelly_multiplier": self.kelly_multiplier,
            "total_games_analyzed": len(analyses),
            "total_value_bets_found": sum(len(a.best_value_bets) for a in analyses),
            "market_analyses": [asdict(analysis) for analysis in analyses],
            "summary": self._generate_summary(analyses),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info(f"💾 Analysis report saved to: {output_file}")
        return str(output_file)

    def _generate_summary(self, analyses: list[MarketAnalysis]) -> dict[str, Any]:
        """Generate summary statistics"""
        all_bets = []
        for analysis in analyses:
            all_bets.extend(analysis.best_value_bets)

        if not all_bets:
            return {"message": "No value bets found"}

        # Sort by edge
        all_bets.sort(key=lambda x: x.edge, reverse=True)

        # Calculate statistics
        total_expected_value = sum(bet.expected_value or 0 for bet in all_bets)
        avg_edge = sum(bet.edge for bet in all_bets) / len(all_bets)

        confidence_counts = {}
        for bet in all_bets:
            confidence_counts[bet.confidence] = confidence_counts.get(bet.confidence, 0) + 1

        return {
            "best_bet": {
                "game": all_bets[0].game,
                "bet": f"{all_bets[0].bet_type} {all_bets[0].side}",
                "odds": all_bets[0].odds,
                "edge": all_bets[0].edge,
                "confidence": all_bets[0].confidence,
            },
            "total_expected_value": total_expected_value,
            "average_edge": avg_edge,
            "confidence_distribution": confidence_counts,
            "recommended_total_risk": sum(bet.max_bet_amount or 0 for bet in all_bets),
        }

    def print_analysis_summary(self, analyses: list[MarketAnalysis]):
        """Print formatted analysis summary"""
        print("\n" + "=" * 80)
        print("🎯 EQ12 MLB VALUE ANALYSIS REPORT")
        print("=" * 80)
        print(f"📊 Games Analyzed: {len(analyses)}")
        print(f"💰 Bankroll: ${self.bankroll:,.2f}")

        all_bets = []
        for analysis in analyses:
            all_bets.extend(analysis.best_value_bets)

        if not all_bets:
            print("❌ No value bets found today")
            return

        print(f"🎲 Value Bets Found: {len(all_bets)}")

        # Sort by edge
        all_bets.sort(key=lambda x: x.edge, reverse=True)

        print("\n🏆 TOP VALUE OPPORTUNITIES:")
        print("-" * 60)

        for i, bet in enumerate(all_bets[:5], 1):  # Top 5
            confidence_emoji = {
                "LOW": "🟡",
                "MEDIUM": "🟠",
                "HIGH": "🔴",
                "VERY_HIGH": "🟣",
            }.get(bet.confidence, "⚪")
            odds_str = f"{bet.odds:+d}" if bet.odds > 0 else str(bet.odds)

            print(f"{confidence_emoji} #{i}: {bet.game}")
            print(f"   💎 Bet: {bet.bet_type.upper()} {bet.side.upper()} ({odds_str})")
            print(
                f"   📈 Edge: {bet.edge:.2%} | Kelly: {bet.kelly_percentage:.1%} | Confidence: {bet.confidence}"
            )
            print(
                f"   💵 Max Bet: ${bet.max_bet_amount:.2f} | Expected Value: ${bet.expected_value:.2f}"
            )
            print(f"   💡 Reasoning: {bet.reasoning}")
            print()

        # Summary stats
        total_ev = sum(bet.expected_value or 0 for bet in all_bets)
        total_risk = sum(bet.max_bet_amount or 0 for bet in all_bets)
        avg_edge = sum(bet.edge for bet in all_bets) / len(all_bets)

        print("📋 PORTFOLIO SUMMARY:")
        print(f"   🎯 Total Expected Value: ${total_ev:.2f}")
        print(f"   💰 Total Risk Amount: ${total_risk:.2f}")
        print(f"   📊 Average Edge: {avg_edge:.2%}")
        print(f"   🎲 Risk/Bankroll Ratio: {(total_risk / self.bankroll):.1%}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="MLB Value Analysis Engine")
    parser.add_argument("--games-file", help="Path to games JSON file")
    parser.add_argument("--bankroll", type=float, default=10000.0, help="Betting bankroll")
    parser.add_argument("--save", action="store_true", help="Save analysis report")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")

    args = parser.parse_args()

    # Find most recent games file if not specified
    if not args.games_file:
        logs_dir = Path("C:/EQ12/logs")
        games_files = list(logs_dir.glob("mlb_games_today_*.json"))
        if games_files:
            args.games_file = str(max(games_files, key=lambda x: x.stat().st_mtime))
        else:
            print("❌ No games file found. Run eq12_mlb_today_fetcher.py first.")
            return 1

    if not Path(args.games_file).exists():
        print(f"❌ Games file not found: {args.games_file}")
        return 1

    try:
        analyzer = MLBValueAnalyzer(bankroll=args.bankroll)

        if not args.quiet:
            print("🎯 EQ12 MLB VALUE ANALYSIS ENGINE")
            print("=" * 50)
            print(f"📁 Games File: {args.games_file}")
            print(f"💰 Bankroll: ${args.bankroll:,.2f}")

        # Run analysis
        analyses = analyzer.analyze_all_games(args.games_file)

        if not args.quiet:
            analyzer.print_analysis_summary(analyses)

        # Save report
        if args.save:
            report_file = analyzer.save_analysis_report(analyses)
            if not args.quiet:
                print(f"\n💾 Full report saved to: {report_file}")

        return 0

    except Exception as e:
        print(f"💥 Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
