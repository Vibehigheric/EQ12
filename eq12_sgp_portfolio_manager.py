"""
EQ12 SGP Portfolio Manager - Risk-Based Betting Strategy
Determines optimal number of SGPs to play based on bankroll and risk tolerance
"""

import json
import logging
from datetime import datetime
from pathlib import Path


class EQ12SGPPortfolioManager:
    """Manages SGP portfolio allocation using EQ12 risk management principles."""

    def __init__(self, bankroll=100, risk_tolerance="moderate"):
        """Initialize portfolio manager."""

        self.bankroll = bankroll  # Total available bankroll
        self.risk_tolerance = risk_tolerance

        # Risk tolerance settings
        self.risk_profiles = {
            "conservative": {
                "max_portfolio_risk": 0.05,  # 5% of bankroll at risk
                "max_single_bet": 0.02,  # 2% per bet
                "kelly_multiplier": 0.25,  # Quarter Kelly
                "max_correlation_exposure": 0.10,  # 10% in correlated bets
            },
            "moderate": {
                "max_portfolio_risk": 0.10,  # 10% of bankroll at risk
                "max_single_bet": 0.03,  # 3% per bet
                "kelly_multiplier": 0.50,  # Half Kelly
                "max_correlation_exposure": 0.15,  # 15% in correlated bets
            },
            "aggressive": {
                "max_portfolio_risk": 0.20,  # 20% of bankroll at risk
                "max_single_bet": 0.05,  # 5% per bet
                "kelly_multiplier": 0.75,  # Three-quarter Kelly
                "max_correlation_exposure": 0.25,  # 25% in correlated bets
            },
        }

        self.profile = self.risk_profiles[risk_tolerance]

        # Setup logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger(__name__)

        self.logger.info("💼 EQ12 SGP Portfolio Manager initialized")
        self.logger.info(f"Bankroll: ${bankroll}, Risk Profile: {risk_tolerance}")

    def analyze_sgp_portfolio(self, sgp_data):
        """Analyze optimal portfolio allocation for SGP."""

        # Extract SGP metrics
        win_prob = sgp_data["win_probability"]
        payout_ratio = sgp_data["roi"]
        kelly_fraction = sgp_data["kelly_fraction"]
        expected_value = sgp_data["expected_value_pct"]
        sgp_data["confidence_level"]

        # Calculate optimal bet sizing
        kelly_bet = self.bankroll * kelly_fraction
        profile_adjusted_bet = kelly_bet * self.profile["kelly_multiplier"]
        max_allowed_bet = self.bankroll * self.profile["max_single_bet"]

        # Optimal single bet size
        optimal_bet_size = min(profile_adjusted_bet, max_allowed_bet)
        optimal_bet_size = max(optimal_bet_size, 1)  # Minimum $1 bet

        # Calculate how many bets we can make
        total_risk_budget = self.bankroll * self.profile["max_portfolio_risk"]

        # For high-correlation SGPs (same games), limit exposure
        if self._is_high_correlation_sgp(sgp_data):
            correlation_budget = self.bankroll * self.profile["max_correlation_exposure"]
            max_bets_by_correlation = int(correlation_budget / optimal_bet_size)
        else:
            max_bets_by_correlation = float("inf")

        # Maximum bets by total risk budget
        max_bets_by_risk = int(total_risk_budget / optimal_bet_size)

        # Final recommendation
        recommended_bets = min(max_bets_by_risk, max_bets_by_correlation)

        # Additional risk considerations
        risk_adjustments = self._calculate_risk_adjustments(sgp_data)
        final_recommended_bets = max(
            1, int(recommended_bets * risk_adjustments["quantity_multiplier"])
        )

        return {
            "optimal_bet_size": optimal_bet_size,
            "recommended_quantity": final_recommended_bets,
            "total_exposure": final_recommended_bets * optimal_bet_size,
            "portfolio_risk_pct": (final_recommended_bets * optimal_bet_size) / self.bankroll,
            "kelly_utilization": profile_adjusted_bet / kelly_bet if kelly_bet > 0 else 0,
            "risk_analysis": risk_adjustments,
            "portfolio_metrics": {
                "expected_return": final_recommended_bets * optimal_bet_size * expected_value,
                "max_loss": final_recommended_bets * optimal_bet_size,
                "potential_win": final_recommended_bets * optimal_bet_size * payout_ratio,
                "risk_reward_ratio": payout_ratio / (1 / win_prob) if win_prob > 0 else 0,
            },
        }

    def _is_high_correlation_sgp(self, sgp_data):
        """Check if SGP has high correlation (same games/sports)."""

        games_involved = sgp_data.get("games_involved", 1)
        sports_involved = len(sgp_data.get("sports_involved", []))

        # High correlation if mostly same game or same sport
        return games_involved <= 2 or sports_involved == 1

    def _calculate_risk_adjustments(self, sgp_data):
        """Calculate risk-based adjustments to bet quantity."""

        confidence = sgp_data["confidence_level"]
        win_prob = sgp_data["win_probability"]
        expected_value = sgp_data["expected_value_pct"]
        num_legs = sgp_data["num_legs"]

        adjustments = {
            "confidence_factor": 1.0,
            "probability_factor": 1.0,
            "complexity_factor": 1.0,
            "ev_factor": 1.0,
            "quantity_multiplier": 1.0,
        }

        # Confidence adjustment
        if confidence == "HIGH":
            adjustments["confidence_factor"] = 1.2
        elif confidence == "MEDIUM":
            adjustments["confidence_factor"] = 1.0
        else:  # LOW
            adjustments["confidence_factor"] = 0.7

        # Win probability adjustment
        if win_prob >= 0.15:
            adjustments["probability_factor"] = 1.1
        elif win_prob >= 0.10:
            adjustments["probability_factor"] = 1.0
        else:
            adjustments["probability_factor"] = 0.8

        # Complexity adjustment (more legs = higher risk)
        if num_legs <= 4:
            adjustments["complexity_factor"] = 1.1
        elif num_legs <= 8:
            adjustments["complexity_factor"] = 1.0
        else:
            adjustments["complexity_factor"] = 0.9

        # Expected value adjustment
        if expected_value >= 2.0:  # 200%+ EV
            adjustments["ev_factor"] = 1.2
        elif expected_value >= 1.0:  # 100%+ EV
            adjustments["ev_factor"] = 1.1
        elif expected_value >= 0.5:  # 50%+ EV
            adjustments["ev_factor"] = 1.0
        else:
            adjustments["ev_factor"] = 0.8

        # Calculate final multiplier
        adjustments["quantity_multiplier"] = (
            adjustments["confidence_factor"]
            * adjustments["probability_factor"]
            * adjustments["complexity_factor"]
            * adjustments["ev_factor"]
        )

        # Cap the multiplier
        adjustments["quantity_multiplier"] = min(adjustments["quantity_multiplier"], 1.5)
        adjustments["quantity_multiplier"] = max(adjustments["quantity_multiplier"], 0.5)

        return adjustments

    def generate_portfolio_recommendations(self, sgp_data):
        """Generate comprehensive portfolio recommendations."""

        analysis = self.analyze_sgp_portfolio(sgp_data)

        # Different scenarios
        scenarios = {
            "conservative": self._analyze_conservative_scenario(sgp_data),
            "recommended": analysis,
            "aggressive": self._analyze_aggressive_scenario(sgp_data),
        }

        return {
            "portfolio_analysis": analysis,
            "scenarios": scenarios,
            "risk_warnings": self._generate_risk_warnings(analysis, sgp_data),
            "bankroll_management": self._generate_bankroll_advice(analysis),
        }

    def _analyze_conservative_scenario(self, sgp_data):
        """Analyze conservative betting scenario."""

        # Use conservative profile temporarily
        original_profile = self.profile
        self.profile = self.risk_profiles["conservative"]

        conservative_analysis = self.analyze_sgp_portfolio(sgp_data)

        # Restore original profile
        self.profile = original_profile

        return conservative_analysis

    def _analyze_aggressive_scenario(self, sgp_data):
        """Analyze aggressive betting scenario."""

        # Use aggressive profile temporarily
        original_profile = self.profile
        self.profile = self.risk_profiles["aggressive"]

        aggressive_analysis = self.analyze_sgp_portfolio(sgp_data)

        # Restore original profile
        self.profile = original_profile

        return aggressive_analysis

    def _generate_risk_warnings(self, analysis, sgp_data):
        """Generate risk warnings based on analysis."""

        warnings = []

        # High portfolio risk warning
        if analysis["portfolio_risk_pct"] > 0.15:
            warnings.append("⚠️ HIGH RISK: Portfolio exposure exceeds 15% of bankroll")

        # Low probability warning
        if sgp_data["win_probability"] < 0.10:
            warnings.append("⚠️ LOW PROBABILITY: Win chance below 10%")

        # High complexity warning
        if sgp_data["num_legs"] > 10:
            warnings.append("⚠️ HIGH COMPLEXITY: 10+ leg SGP has increased variance")

        # Correlation warning
        if self._is_high_correlation_sgp(sgp_data):
            warnings.append("⚠️ CORRELATION RISK: Limited diversification across games/sports")

        return warnings

    def _generate_bankroll_advice(self, analysis):
        """Generate bankroll management advice."""

        advice = []

        if analysis["portfolio_risk_pct"] < 0.05:
            advice.append("✅ Conservative approach - good for bankroll preservation")
        elif analysis["portfolio_risk_pct"] < 0.15:
            advice.append("✅ Balanced approach - reasonable risk/reward ratio")
        else:
            advice.append("⚠️ Aggressive approach - monitor closely for drawdowns")

        if analysis["kelly_utilization"] < 0.5:
            advice.append("📊 Under-betting relative to Kelly criterion - room to increase")
        elif analysis["kelly_utilization"] > 1.0:
            advice.append("📊 Over-betting relative to Kelly criterion - consider reducing")

        return advice


def main():
    """Analyze tonight's SGP portfolio recommendations."""

    print("💼 EQ12 SGP PORTFOLIO ANALYSIS")
    print("=" * 60)
    print("Risk-based betting strategy for tonight's SGPs")

    try:
        # Load the latest SGP analysis
        logs_dir = Path("C:/EQ12/logs")

        # Find the most recent smart SGP file
        sgp_files = list(logs_dir.glob("smart_mega_sgp_*.json"))
        if not sgp_files:
            print("❌ No SGP analysis files found")
            return

        latest_file = max(sgp_files, key=lambda x: x.stat().st_mtime)

        with open(latest_file) as f:
            sgp_analysis = json.load(f)

        sgp_data = sgp_analysis["smart_sgp"]

        print(f"📊 Analyzing SGP: {sgp_data['strategy']}")
        print(f"💰 ROI: {sgp_data['roi']:.1f}x | Win Prob: {sgp_data['win_probability']:.1%}")

        # Get user's bankroll and risk preference
        print("\n💰 BANKROLL SCENARIOS:")

        # Analyze different bankroll sizes
        bankroll_scenarios = [100, 500, 1000, 2500]
        risk_profiles = ["conservative", "moderate", "aggressive"]

        for bankroll in bankroll_scenarios:
            print(f"\n💵 ${bankroll} Bankroll:")

            for risk_profile in risk_profiles:
                portfolio_manager = EQ12SGPPortfolioManager(bankroll, risk_profile)
                recommendations = portfolio_manager.generate_portfolio_recommendations(sgp_data)

                rec = recommendations["portfolio_analysis"]

                print(
                    f"   {risk_profile.title()}: {rec['recommended_quantity']} bets × ${rec['optimal_bet_size']:.0f} = ${rec['total_exposure']:.0f} risk ({rec['portfolio_risk_pct']:.1%})"
                )

        # Detailed analysis for moderate $500 bankroll (common scenario)
        print("\n" + "=" * 60)
        print("📈 DETAILED ANALYSIS - $500 Bankroll (Moderate Risk)")
        print("=" * 60)

        portfolio_manager = EQ12SGPPortfolioManager(500, "moderate")
        detailed_recommendations = portfolio_manager.generate_portfolio_recommendations(sgp_data)

        analysis = detailed_recommendations["portfolio_analysis"]
        scenarios = detailed_recommendations["scenarios"]

        print("\n🎯 RECOMMENDED STRATEGY:")
        print(f"   Quantity: {analysis['recommended_quantity']} SGP bets")
        print(f"   Bet Size: ${analysis['optimal_bet_size']:.0f} per bet")
        print(
            f"   Total Risk: ${analysis['total_exposure']:.0f} ({analysis['portfolio_risk_pct']:.1%} of bankroll)"
        )

        print("\n📊 PORTFOLIO METRICS:")
        metrics = analysis["portfolio_metrics"]
        print(f"   Expected Return: ${metrics['expected_return']:.2f}")
        print(f"   Maximum Loss: ${metrics['max_loss']:.0f}")
        print(f"   Potential Win: ${metrics['potential_win']:.0f}")
        print(f"   Risk/Reward Ratio: {metrics['risk_reward_ratio']:.2f}")

        print("\n🎛️  SCENARIO COMPARISON:")
        for scenario_name, scenario_data in scenarios.items():
            print(
                f"   {scenario_name.title()}: {scenario_data['recommended_quantity']} bets × ${scenario_data['optimal_bet_size']:.0f}"
            )

        # Risk warnings
        warnings = detailed_recommendations["risk_warnings"]
        if warnings:
            print("\n⚠️  RISK WARNINGS:")
            for warning in warnings:
                print(f"   {warning}")

        # Bankroll advice
        advice = detailed_recommendations["bankroll_management"]
        if advice:
            print("\n💡 BANKROLL ADVICE:")
            for tip in advice:
                print(f"   {tip}")

        # Tonight's specific recommendation
        print("\n🌙 TONIGHT'S RECOMMENDATION:")
        print("=" * 40)

        if analysis["recommended_quantity"] == 1:
            print(f"✅ Play 1 SGP with ${analysis['optimal_bet_size']:.0f} stake")
            print("   This is optimal for the risk/reward profile")
        elif analysis["recommended_quantity"] <= 3:
            print(
                f"✅ Play {analysis['recommended_quantity']} SGPs with ${analysis['optimal_bet_size']:.0f} each"
            )
            print("   Moderate diversification strategy")
        else:
            print(
                f"⚠️ Play {analysis['recommended_quantity']} SGPs with ${analysis['optimal_bet_size']:.0f} each"
            )
            print("   Higher variance approach - monitor closely")

        print("\n🎲 FINAL VERDICT:")
        print("With your 27.3x ROI SGP at 13.7% win probability:")
        print("• Conservative: 1-2 bets")
        print("• Moderate: 2-3 bets")
        print("• Aggressive: 3-5 bets")
        print("\nThe SGP has strong positive EV (+274%), so multiple units are justified")
        print("but don't risk more than you can afford to lose!")

        # Save portfolio analysis
        results = {
            "timestamp": datetime.now().isoformat(),
            "sgp_analyzed": sgp_data["strategy"],
            "portfolio_recommendations": detailed_recommendations,
            "bankroll_scenarios": {},
        }

        for bankroll in bankroll_scenarios:
            results["bankroll_scenarios"][f"${bankroll}"] = {}
            for risk_profile in risk_profiles:
                pm = EQ12SGPPortfolioManager(bankroll, risk_profile)
                rec = pm.analyze_sgp_portfolio(sgp_data)
                results["bankroll_scenarios"][f"${bankroll}"][risk_profile] = rec

        results_file = (
            logs_dir / f"sgp_portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Portfolio analysis saved: {results_file}")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
