#!/usr/bin/env python3
"""
EQ12 Kelly Criterion Calculator - Optimal stake sizing for sports betting
Calculates recommended bet sizes based on bankroll, odds, and expected value
"""


class KellyCriterion:
    """
    Advanced Kelly Criterion calculator for sports betting optimization.

    Features:
    - Full Kelly and fractional Kelly calculations
    - Risk management with maximum stake limits
    - Expected value validation and adjustment
    - Multi-outcome Kelly for complex bets
    - Bankroll percentage recommendations
    """

    def __init__(
        self,
        bankroll: float,
        max_stake_pct: float = 0.10,  # Maximum 10% of bankroll per bet
        kelly_fraction: float = 0.25,  # Use 25% of full Kelly (conservative)
        min_stake: float = 5.0,  # Minimum bet size
        max_stake: float = 500.0,  # Maximum bet size
    ):
        """
        Initialize Kelly calculator with risk parameters.

        Args:
            bankroll: Current bankroll amount
            max_stake_pct: Maximum percentage of bankroll to risk per bet
            kelly_fraction: Fraction of full Kelly to use (0.25 = 25%)
            min_stake: Minimum bet size in dollars
            max_stake: Maximum bet size in dollars
        """
        self.bankroll = bankroll
        self.max_stake_pct = max_stake_pct
        self.kelly_fraction = kelly_fraction
        self.min_stake = min_stake
        self.max_stake = max_stake

    def calculate_kelly_stake(
        self, decimal_odds: float, win_probability: float, edge: float | None = None
    ) -> dict:
        """
        Calculate optimal Kelly stake for a single bet.

        Args:
            decimal_odds: Decimal odds (e.g., 2.1 for +110)
            win_probability: True win probability (0.0 to 1.0)
            edge: Optional edge override (calculated if not provided)

        Returns:
            Dictionary with Kelly calculations and recommendations
        """
        # Validate inputs
        if decimal_odds <= 1.0:
            raise ValueError("Decimal odds must be greater than 1.0")
        if not 0 < win_probability < 1:
            raise ValueError("Win probability must be between 0 and 1")

        # Calculate edge if not provided
        if edge is None:
            implied_prob = 1.0 / decimal_odds
            edge = win_probability - implied_prob

        # Kelly formula: f = (bp - q) / b
        # Where: b = odds-1, p = win_prob, q = loss_prob
        b = decimal_odds - 1.0  # Net odds
        p = win_probability
        q = 1.0 - win_probability

        # Full Kelly percentage
        kelly_pct = (b * p - q) / b

        # Apply Kelly fraction for risk management
        adjusted_kelly_pct = kelly_pct * self.kelly_fraction

        # Calculate stake amounts
        full_kelly_stake = self.bankroll * kelly_pct
        adjusted_kelly_stake = self.bankroll * adjusted_kelly_pct

        # Apply risk limits
        max_allowed_stake = self.bankroll * self.max_stake_pct
        recommended_stake = min(
            max(adjusted_kelly_stake, self.min_stake),
            min(max_allowed_stake, self.max_stake),
        )

        # Calculate expected value
        expected_return = (decimal_odds * win_probability) - 1.0
        ev_percentage = expected_return * 100

        # Risk assessment
        risk_level = self._assess_risk_level(kelly_pct, edge)

        return {
            "decimal_odds": decimal_odds,
            "win_probability": win_probability,
            "edge": edge,
            "ev_percentage": ev_percentage,
            "kelly_percentage": kelly_pct * 100,
            "full_kelly_stake": full_kelly_stake,
            "adjusted_kelly_percentage": adjusted_kelly_pct * 100,
            "adjusted_kelly_stake": adjusted_kelly_stake,
            "recommended_stake": recommended_stake,
            "stake_as_bankroll_pct": (recommended_stake / self.bankroll) * 100,
            "risk_level": risk_level,
            "bankroll": self.bankroll,
            "max_stake_limit": max_allowed_stake,
            "expected_profit": recommended_stake * expected_return,
            "max_loss": recommended_stake,
        }

    def calculate_ev_kelly_stake(self, decimal_odds: float, ev_percentage: float) -> dict:
        """
        Calculate Kelly stake using Expected Value percentage.

        Args:
            decimal_odds: Decimal odds
            ev_percentage: Expected value as percentage (e.g., 4.2 for 4.2% EV)

        Returns:
            Dictionary with Kelly calculations
        """
        # Convert EV% back to win probability
        implied_prob = 1.0 / decimal_odds
        edge = ev_percentage / 100.0
        win_probability = implied_prob + edge

        # Validate calculated probability
        if win_probability <= 0 or win_probability >= 1:
            raise ValueError(f"Invalid EV results in probability: {win_probability:.3f}")

        return self.calculate_kelly_stake(decimal_odds, win_probability, edge)

    def calculate_parlay_kelly_stake(self, legs: list[dict]) -> dict:
        """
        Calculate Kelly stake for a parlay bet.

        Args:
            legs: List of leg dictionaries with 'odds' and 'win_prob' keys

        Returns:
            Dictionary with parlay Kelly calculations
        """
        if len(legs) < 2:
            raise ValueError("Parlay must have at least 2 legs")

        # Calculate combined odds and probability
        combined_odds = 1.0
        combined_prob = 1.0

        for leg in legs:
            combined_odds *= leg["odds"]
            combined_prob *= leg["win_prob"]

        return self.calculate_kelly_stake(combined_odds, combined_prob)

    def _assess_risk_level(self, kelly_pct: float, edge: float) -> str:
        """Assess risk level based on Kelly percentage and edge."""
        if kelly_pct <= 0:
            return "NO_BET"  # Negative or zero Kelly = don't bet
        if kelly_pct < 0.02:  # Less than 2%
            return "LOW"
        if kelly_pct < 0.05:  # 2-5%
            return "MEDIUM"
        if kelly_pct < 0.10:  # 5-10%
            return "HIGH"
        # Over 10%
        return "VERY_HIGH"

    def get_stake_recommendation(
        self, decimal_odds: float, ev_percentage: float, confidence_level: float = 1.0
    ) -> tuple[float, str]:
        """
        Get simple stake recommendation with confidence adjustment.

        Args:
            decimal_odds: Decimal odds
            ev_percentage: Expected value percentage
            confidence_level: Confidence in the edge (0.0 to 1.0)

        Returns:
            Tuple of (recommended_stake, reason)
        """
        try:
            # Calculate base Kelly stake
            kelly_result = self.calculate_ev_kelly_stake(decimal_odds, ev_percentage)

            # Adjust for confidence
            base_stake = kelly_result["recommended_stake"]
            adjusted_stake = base_stake * confidence_level

            # Apply minimum/maximum limits
            final_stake = max(self.min_stake, min(adjusted_stake, self.max_stake))

            # Generate recommendation reason
            risk_level = kelly_result["risk_level"]
            if risk_level == "NO_BET":
                return 0.0, "Negative expected value - skip bet"
            if ev_percentage < 1.0:
                return 0.0, "Expected value too low - skip bet"
            if final_stake == self.min_stake:
                return (
                    final_stake,
                    f"Minimum stake (Kelly: {kelly_result['adjusted_kelly_percentage']:.1f}%)",
                )
            if final_stake == self.max_stake:
                return (
                    final_stake,
                    f"Maximum stake limit reached (Kelly: {kelly_result['adjusted_kelly_percentage']:.1f}%)",
                )
            return (
                final_stake,
                f"Kelly-optimal stake ({kelly_result['stake_as_bankroll_pct']:.1f}% of bankroll)",
            )

        except Exception as e:
            return self.min_stake, f"Calculation error: {e}"


def quick_kelly_stake(
    bankroll: float,
    decimal_odds: float,
    ev_percentage: float,
    kelly_fraction: float = 0.25,
    max_stake_pct: float = 0.10,
) -> float:
    """
    Quick Kelly stake calculation for simple use cases.

    Args:
        bankroll: Current bankroll
        decimal_odds: Decimal odds
        ev_percentage: Expected value percentage
        kelly_fraction: Fraction of Kelly to use
        max_stake_pct: Maximum percentage of bankroll

    Returns:
        Recommended stake amount
    """
    calculator = KellyCriterion(bankroll, max_stake_pct, kelly_fraction)
    result = calculator.calculate_ev_kelly_stake(decimal_odds, ev_percentage)
    return result["recommended_stake"]


def create_kelly_report(kelly_result: dict) -> str:
    """
    Create formatted report from Kelly calculation results.

    Args:
        kelly_result: Dictionary from KellyCriterion calculations

    Returns:
        Formatted string report
    """
    report = [
        "🧮 KELLY CRITERION ANALYSIS",
        "=" * 40,
        f"💰 Current Bankroll:     ${kelly_result['bankroll']:,.2f}",
        f"🎲 Decimal Odds:         {kelly_result['decimal_odds']:.2f}",
        f"📈 Expected Value:       {kelly_result['ev_percentage']:+.2f}%",
        f"🎯 Win Probability:      {kelly_result['win_probability']:.1%}",
        f"⚡ Edge:                 {kelly_result['edge']:+.3f}",
        "",
        "📊 KELLY CALCULATIONS",
        "-" * 40,
        f"📐 Full Kelly %:         {kelly_result['kelly_percentage']:.2f}%",
        f"🛡️  Adjusted Kelly %:     {kelly_result['adjusted_kelly_percentage']:.2f}%",
        f"💵 Full Kelly Stake:     ${kelly_result['full_kelly_stake']:.2f}",
        f"✅ Recommended Stake:    ${kelly_result['recommended_stake']:.2f}",
        f"📊 % of Bankroll:        {kelly_result['stake_as_bankroll_pct']:.2f}%",
        "",
        "⚠️  RISK ASSESSMENT",
        "-" * 40,
        f"🚨 Risk Level:           {kelly_result['risk_level']}",
        f"📉 Maximum Loss:         ${kelly_result['max_loss']:.2f}",
        f"📈 Expected Profit:      ${kelly_result['expected_profit']:.2f}",
        f"🔒 Max Allowed Stake:    ${kelly_result['max_stake_limit']:.2f}",
    ]

    return "\n".join(report)


if __name__ == "__main__":
    # Test the Kelly Criterion calculator
    print("🧪 Testing Kelly Criterion Calculator...")

    # Test case: NFL game with 4.2% EV
    calculator = KellyCriterion(bankroll=1000.0)

    # Example: Chiefs -7 at +110 (2.1 decimal odds) with 4.2% EV
    result = calculator.calculate_ev_kelly_stake(decimal_odds=2.1, ev_percentage=4.2)

    print(create_kelly_report(result))

    # Quick recommendation test
    stake, reason = calculator.get_stake_recommendation(2.1, 4.2, confidence_level=0.8)
    print(f"\n💡 Quick Recommendation: ${stake:.2f} - {reason}")

    # Parlay test
    parlay_legs = [
        {"odds": 1.91, "win_prob": 0.55},  # Leg 1: -110 with 55% chance
        {"odds": 1.83, "win_prob": 0.60},  # Leg 2: -120 with 60% chance
    ]

    parlay_result = calculator.calculate_parlay_kelly_stake(parlay_legs)
    print(f"\n🔗 Parlay Kelly Recommendation: ${parlay_result['recommended_stake']:.2f}")
    print(f"   Combined Odds: {parlay_result['decimal_odds']:.2f}")
    print(f"   Win Probability: {parlay_result['win_probability']:.1%}")
    print(f"   Expected Value: {parlay_result['ev_percentage']:+.2f}%")
