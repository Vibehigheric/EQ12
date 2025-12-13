#!/usr/bin/env python3
"""
EQ12 Advanced Betting Mathematics - Odds Conversion & Kelly Criterion
Expert-level algorithms for sports betting calculations and optimal sizing
"""

import math
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class OddsFormat(Enum):
    """Enumeration for different odds formats."""

    DECIMAL = "DECIMAL"
    FRACTIONAL = "FRACTIONAL"
    MONEYLINE = "MONEYLINE"
    IMPLIED_PROBABILITY = "IMPLIED_PROB"


@dataclass
class OddsConversion:
    """Comprehensive odds conversion result."""

    decimal: float
    fractional: str
    moneyline: int
    implied_probability: float
    true_probability: float | None = None
    edge: float | None = None
    kelly_fraction: float | None = None


class EQ12BettingMathematics:
    """Expert-level betting mathematics and optimization algorithms."""

    def __init__(self):
        self.precision = 4  # Decimal precision for calculations

    def convert_odds(
        self,
        odds_value: float | int | str,
        from_format: OddsFormat,
        true_probability: float | None = None,
    ) -> OddsConversion:
        """
        Convert between all major odds formats with mathematical precision.

        Args:
            odds_value: The odds value to convert
            from_format: Source format of the odds
            true_probability: Optional true probability for edge calculation

        Returns:
            OddsConversion object with all formats and calculations
        """
        # First convert everything to decimal odds (universal format)
        decimal_odds = self._to_decimal_odds(odds_value, from_format)

        # Calculate all other formats from decimal
        fractional = self._decimal_to_fractional(decimal_odds)
        moneyline = self._decimal_to_moneyline(decimal_odds)
        implied_prob = self._decimal_to_implied_probability(decimal_odds)

        # Calculate edge and Kelly if true probability provided
        edge = None
        kelly_fraction = None
        if true_probability is not None:
            edge = self.calculate_betting_edge(decimal_odds, true_probability)
            kelly_fraction = self.kelly_criterion(decimal_odds, true_probability)

        return OddsConversion(
            decimal=round(decimal_odds, self.precision),
            fractional=fractional,
            moneyline=moneyline,
            implied_probability=round(implied_prob, self.precision),
            true_probability=true_probability,
            edge=edge,
            kelly_fraction=kelly_fraction,
        )

    def _to_decimal_odds(self, odds_value: float | int | str, from_format: OddsFormat) -> float:
        """Convert any odds format to decimal odds."""
        if from_format == OddsFormat.DECIMAL:
            return float(odds_value)

        if from_format == OddsFormat.MONEYLINE:
            odds_value = int(odds_value)
            if odds_value > 0:
                # Positive moneyline: (odds/100) + 1
                return (odds_value / 100.0) + 1.0
            # Negative moneyline: (100/abs(odds)) + 1
            return (100.0 / abs(odds_value)) + 1.0

        if from_format == OddsFormat.FRACTIONAL:
            # Handle fractional odds like "5/2" or "3/1"
            if isinstance(odds_value, str):
                if "/" in odds_value:
                    numerator, denominator = map(float, odds_value.split("/"))
                    return (numerator / denominator) + 1.0
                return float(odds_value) + 1.0
            return float(odds_value) + 1.0

        if from_format == OddsFormat.IMPLIED_PROBABILITY:
            # Convert probability to decimal odds: 1 / probability
            prob = float(odds_value)
            if prob <= 0 or prob >= 1:
                raise ValueError(f"Probability must be between 0 and 1, got {prob}")
            return 1.0 / prob

        raise ValueError(f"Unsupported odds format: {from_format}")

    def _decimal_to_fractional(self, decimal_odds: float) -> str:
        """Convert decimal odds to fractional format."""
        # Convert to fraction: decimal_odds - 1 = fraction
        fraction_decimal = decimal_odds - 1.0

        # Use Decimal for precise fraction conversion
        d = Decimal(str(fraction_decimal)).quantize(Decimal("0.0001"))

        # Simple cases
        if fraction_decimal == 0:
            return "0/1"
        if fraction_decimal == 1:
            return "1/1"

        # Convert to fraction using continued fractions for accuracy
        numerator, denominator = self._decimal_to_fraction(float(d))

        return f"{numerator}/{denominator}"

    def _decimal_to_fraction(
        self, decimal_val: float, max_denominator: int = 100
    ) -> tuple[int, int]:
        """Convert decimal to simplest fraction representation."""
        # Handle simple cases
        if decimal_val == 0:
            return (0, 1)
        if decimal_val == 1:
            return (1, 1)

        # Find best fraction approximation
        best_num, best_den = 0, 1
        min_error = float("inf")

        for den in range(1, max_denominator + 1):
            num = round(decimal_val * den)
            error = abs(decimal_val - (num / den))

            if error < min_error:
                min_error = error
                best_num, best_den = num, den

                # Perfect match found
                if error < 1e-10:
                    break

        # Simplify the fraction
        gcd = math.gcd(best_num, best_den)
        return (best_num // gcd, best_den // gcd)

    def _decimal_to_moneyline(self, decimal_odds: float) -> int:
        """Convert decimal odds to American moneyline format."""
        if decimal_odds >= 2.0:
            # Positive moneyline: (decimal_odds - 1) * 100
            return int((decimal_odds - 1.0) * 100)
        # Negative moneyline: -100 / (decimal_odds - 1)
        return int(-100.0 / (decimal_odds - 1.0))

    def _decimal_to_implied_probability(self, decimal_odds: float) -> float:
        """Convert decimal odds to implied probability."""
        return 1.0 / decimal_odds

    def calculate_betting_edge(self, decimal_odds: float, true_probability: float) -> float:
        """
        Calculate the betting edge (expected value).

        Edge = (true_probability * (decimal_odds - 1)) - (1 - true_probability)
        """
        if not (0 < true_probability < 1):
            raise ValueError("True probability must be between 0 and 1")

        edge = (true_probability * (decimal_odds - 1)) - (1 - true_probability)
        return round(edge, self.precision)

    def kelly_criterion(
        self,
        decimal_odds: float,
        true_probability: float,
        conservative_factor: float = 0.25,
    ) -> float:
        """
        Calculate optimal bet sizing using Kelly Criterion.

        Kelly% = (bp - q) / b
        Where:
        b = decimal_odds - 1 (net odds)
        p = true_probability
        q = 1 - true_probability

        Args:
            decimal_odds: Decimal odds offered
            true_probability: Your assessed true probability
            conservative_factor: Fraction of Kelly to bet (0.25 = quarter Kelly)
        """
        if not (0 < true_probability < 1):
            raise ValueError("True probability must be between 0 and 1")

        b = decimal_odds - 1.0  # Net odds
        p = true_probability
        q = 1.0 - true_probability

        # Kelly fraction: (bp - q) / b
        kelly_fraction = ((b * p) - q) / b

        # Only bet if Kelly is positive (positive expected value)
        if kelly_fraction <= 0:
            return 0.0

        # Apply conservative factor (typically 25% of full Kelly)
        conservative_kelly = kelly_fraction * conservative_factor

        # Cap at reasonable maximum (never bet more than 10% of bankroll)
        max_bet_fraction = 0.10

        return round(min(conservative_kelly, max_bet_fraction), self.precision)

    def calculate_parlay_odds(self, individual_odds: list[float]) -> float:
        """Calculate combined decimal odds for a parlay."""
        if not individual_odds:
            return 1.0

        combined_odds = 1.0
        for odds in individual_odds:
            combined_odds *= odds

        return round(combined_odds, self.precision)

    def calculate_parlay_probability(self, individual_probabilities: list[float]) -> float:
        """Calculate combined probability for independent events in a parlay."""
        if not individual_probabilities:
            return 0.0

        combined_prob = 1.0
        for prob in individual_probabilities:
            if not (0 <= prob <= 1):
                raise ValueError(f"Probability must be between 0 and 1, got {prob}")
            combined_prob *= prob

        return round(combined_prob, self.precision)

    def optimal_bankroll_allocation(
        self, opportunities: list[tuple[float, float]], total_bankroll: float
    ) -> dict[int, float]:
        """
        Calculate optimal bankroll allocation across multiple betting opportunities.

        Args:
            opportunities: List of (decimal_odds, true_probability) tuples
            total_bankroll: Total available bankroll

        Returns:
            Dictionary mapping opportunity index to bet amount
        """
        allocations = {}
        remaining_bankroll = total_bankroll

        for i, (odds, prob) in enumerate(opportunities):
            kelly_fraction = self.kelly_criterion(odds, prob)
            bet_amount = remaining_bankroll * kelly_fraction

            allocations[i] = round(bet_amount, 2)
            # Update remaining bankroll (conservative approach)
            remaining_bankroll = max(0, remaining_bankroll - bet_amount)

        return allocations


def test_betting_mathematics():
    """Test suite for betting mathematics algorithms."""
    math_engine = EQ12BettingMathematics()

    print("🧮 EQ12 Betting Mathematics Test Suite")
    print("=" * 50)

    # Test odds conversions
    test_cases = [
        (2.50, OddsFormat.DECIMAL),
        (150, OddsFormat.MONEYLINE),
        (-200, OddsFormat.MONEYLINE),
        ("3/2", OddsFormat.FRACTIONAL),
        (0.40, OddsFormat.IMPLIED_PROBABILITY),
    ]

    for odds, format_type in test_cases:
        try:
            conversion = math_engine.convert_odds(odds, format_type, 0.45)
            print("\n📊 Converting {odds} ({format_type.value}):")
            print("   Decimal: {conversion.decimal}")
            print("   Fractional: {conversion.fractional}")
            print("   Moneyline: {conversion.moneyline:+d}")
            print("   Implied Prob: {conversion.implied_probability:.1%}")
            if conversion.edge is not None:
                print("   Edge: {conversion.edge:+.3f}")
            if conversion.kelly_fraction is not None:
                print("   Kelly: {conversion.kelly_fraction:.1%}")
        except Exception:
            print("❌ Error converting {odds}: {e}")

    # Test parlay calculations
    parlay_odds = [2.0, 1.8, 2.2, 1.9]
    math_engine.calculate_parlay_odds(parlay_odds)
    print("\n🎯 Parlay Test:")
    print("   Individual odds: {parlay_odds}")
    print("   Combined odds: {combined}")
    print("   Payout on $10: ${(combined - 1) * 10:.2f}")


if __name__ == "__main__":
    test_betting_mathematics()
