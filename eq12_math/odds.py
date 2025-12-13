"""
EQ12 Math Library - Core Odds and Edge Calculations
==================================================

Pure mathematical functions for sports betting calculations.
No dependencies on external APIs - deterministic math only.

Functions:
- american_to_decimal(): Convert American odds to decimal
- decimal_to_american(): Convert decimal odds to American
- implied_probability(): Calculate implied probability from odds
- remove_vig_two_way(): Remove vig from two-way markets
- calculate_ev(): Calculate expected value
- kelly_criterion(): Calculate Kelly optimal bet size

Author: EQ12 Development Team
Version: 1.0.0
"""


def american_to_decimal(american: int) -> float:
    """
    Convert American odds to decimal odds.

    Args:
        american: American odds (e.g. +150, -110)

    Returns:
        Decimal odds (e.g. 2.50, 1.91)

    Examples:
        >>> american_to_decimal(150)
        2.5
        >>> american_to_decimal(-110)
        1.909
    """
    if american > 0:
        return (american / 100.0) + 1.0
    else:
        return (100.0 / abs(american)) + 1.0


def decimal_to_american(decimal: float) -> int:
    """
    Convert decimal odds to American odds.

    Args:
        decimal: Decimal odds (e.g. 2.50, 1.91)

    Returns:
        American odds (e.g. +150, -110)

    Examples:
        >>> decimal_to_american(2.5)
        150
        >>> decimal_to_american(1.91)
        -110
    """
    if decimal >= 2.0:
        return int((decimal - 1.0) * 100)
    else:
        return int(-100.0 / (decimal - 1.0))


def implied_probability(decimal_odds: float) -> float:
    """
    Calculate implied probability from decimal odds.

    Args:
        decimal_odds: Decimal odds

    Returns:
        Implied probability (0.0 to 1.0)

    Examples:
        >>> implied_probability(2.0)
        0.5
        >>> implied_probability(4.0)
        0.25
    """
    return 1.0 / decimal_odds


def remove_vig_two_way(odds_a: int, odds_b: int) -> tuple[float, float]:
    """
    Remove vig from two-way betting market.

    Args:
        odds_a: American odds for side A
        odds_b: American odds for side B

    Returns:
        Tuple of (prob_a_no_vig, prob_b_no_vig)

    Examples:
        >>> remove_vig_two_way(-110, -110)
        (0.5, 0.5)
        >>> remove_vig_two_way(100, -120)
        (0.458, 0.542)
    """
    decimal_a = american_to_decimal(odds_a)
    decimal_b = american_to_decimal(odds_b)

    implied_a = implied_probability(decimal_a)
    implied_b = implied_probability(decimal_b)

    total_implied = implied_a + implied_b

    # Remove vig by normalizing
    prob_a_no_vig = implied_a / total_implied
    prob_b_no_vig = implied_b / total_implied

    return prob_a_no_vig, prob_b_no_vig


def calculate_ev(true_probability: float, decimal_odds: float) -> float:
    """
    Calculate expected value (EV) for a bet.

    Formula: EV = p * (odds - 1) - (1 - p)

    Args:
        true_probability: Your assessed probability (0.0 to 1.0)
        decimal_odds: Decimal odds offered by sportsbook

    Returns:
        Expected value per $1 bet

    Examples:
        >>> calculate_ev(0.6, 2.0)  # 60% chance at 2.0 odds
        0.2  # 20 cent profit per dollar
        >>> calculate_ev(0.4, 2.0)  # 40% chance at 2.0 odds
        -0.2  # 20 cent loss per dollar
    """
    return true_probability * (decimal_odds - 1.0) - (1.0 - true_probability)


def calculate_ev_percent(true_probability: float, decimal_odds: float) -> float:
    """
    Calculate EV as a percentage.

    Args:
        true_probability: Your assessed probability (0.0 to 1.0)
        decimal_odds: Decimal odds offered

    Returns:
        EV percentage (e.g. 5.0 for 5% edge)
    """
    return calculate_ev(true_probability, decimal_odds) * 100.0


def kelly_criterion(true_probability: float, decimal_odds: float) -> float:
    """
    Calculate Kelly Criterion optimal bet fraction.

    Formula: f* = (bp - q) / b
    Where b = decimal_odds - 1, p = true_probability, q = 1 - p

    Args:
        true_probability: Your assessed probability (0.0 to 1.0)
        decimal_odds: Decimal odds offered

    Returns:
        Optimal fraction of bankroll to bet (0.0 to 1.0)

    Examples:
        >>> kelly_criterion(0.6, 2.0)  # 60% chance at even odds
        0.2  # Bet 20% of bankroll
        >>> kelly_criterion(0.4, 2.0)  # 40% chance at even odds
        0.0  # Don't bet (negative EV)
    """
    if true_probability <= 0.0 or true_probability >= 1.0:
        return 0.0

    if decimal_odds <= 1.0:
        return 0.0

    b = decimal_odds - 1.0  # Net odds
    q = 1.0 - true_probability

    kelly_fraction = (b * true_probability - q) / b

    return max(0.0, kelly_fraction)  # Never bet negative EV


def fractional_kelly(true_probability: float, decimal_odds: float, fraction: float = 0.25) -> float:
    """
    Calculate fractional Kelly bet size for risk management.

    Args:
        true_probability: Your assessed probability
        decimal_odds: Decimal odds offered
        fraction: Kelly fraction to use (e.g. 0.25 for quarter Kelly)

    Returns:
        Fractional Kelly bet size
    """
    full_kelly = kelly_criterion(true_probability, decimal_odds)
    return full_kelly * fraction


def calculate_breakeven_probability(decimal_odds: float) -> float:
    """
    Calculate breakeven probability for given odds.

    Args:
        decimal_odds: Decimal odds

    Returns:
        Breakeven probability (0.0 to 1.0)
    """
    return implied_probability(decimal_odds)


def calculate_fair_odds(true_probability: float) -> float:
    """
    Calculate fair decimal odds for a given probability.

    Args:
        true_probability: True probability (0.0 to 1.0)

    Returns:
        Fair decimal odds
    """
    if true_probability <= 0.0:
        return float("inf")

    return 1.0 / true_probability


def calculate_vig_percentage(odds_a: int, odds_b: int) -> float:
    """
    Calculate vig percentage in two-way market.

    Args:
        odds_a: American odds for side A
        odds_b: American odds for side B

    Returns:
        Vig percentage (e.g. 4.55 for 4.55% vig)
    """
    decimal_a = american_to_decimal(odds_a)
    decimal_b = american_to_decimal(odds_b)

    implied_a = implied_probability(decimal_a)
    implied_b = implied_probability(decimal_b)

    total_implied = implied_a + implied_b

    # Vig is the excess over 100%
    vig_decimal = total_implied - 1.0

    return vig_decimal * 100.0


def optimal_arbitrage_stakes(
    decimal_odds_a: float, decimal_odds_b: float, total_stake: float
) -> tuple[float, float]:
    """
    Calculate optimal stakes for arbitrage opportunity.

    Args:
        decimal_odds_a: Decimal odds for bet A
        decimal_odds_b: Decimal odds for bet B
        total_stake: Total amount to stake

    Returns:
        Tuple of (stake_a, stake_b)
    """
    implied_a = implied_probability(decimal_odds_a)
    implied_b = implied_probability(decimal_odds_b)

    total_implied = implied_a + implied_b

    # Only works if arbitrage exists
    if total_implied >= 1.0:
        raise ValueError("No arbitrage opportunity exists")

    stake_a = total_stake * implied_a / total_implied
    stake_b = total_stake * implied_b / total_implied

    return stake_a, stake_b


def arbitrage_profit_percentage(decimal_odds_a: float, decimal_odds_b: float) -> float:
    """
    Calculate profit percentage from arbitrage.

    Args:
        decimal_odds_a: Decimal odds for bet A
        decimal_odds_b: Decimal odds for bet B

    Returns:
        Profit percentage (or 0.0 if no arbitrage)
    """
    implied_a = implied_probability(decimal_odds_a)
    implied_b = implied_probability(decimal_odds_b)

    total_implied = implied_a + implied_b

    if total_implied >= 1.0:
        return 0.0  # No arbitrage

    profit_margin = 1.0 - total_implied
    return profit_margin * 100.0


def closing_line_value_percent(entry_decimal: float, closing_decimal: float) -> float:
    """
    Calculate Closing Line Value (CLV) percentage.

    Args:
        entry_decimal: Decimal odds when bet was placed
        closing_decimal: Decimal odds at closing

    Returns:
        CLV percentage (positive = good CLV)
    """
    return ((closing_decimal - entry_decimal) / entry_decimal) * 100.0


# Validation functions
def validate_american_odds(american: int) -> bool:
    """Validate American odds format."""
    return american != 0  # American odds cannot be 0


def validate_decimal_odds(decimal: float) -> bool:
    """Validate decimal odds format."""
    return decimal > 1.0  # Decimal odds must be > 1.0


def validate_probability(prob: float) -> bool:
    """Validate probability is between 0 and 1."""
    return 0.0 <= prob <= 1.0


# Utility functions for common betting scenarios
def parlay_decimal_odds(individual_odds: list[float]) -> float:
    """
    Calculate decimal odds for parlay (independent events).

    Args:
        individual_odds: List of decimal odds for each leg

    Returns:
        Combined parlay decimal odds
    """
    result = 1.0
    for odds in individual_odds:
        result *= odds
    return result


def parlay_probability(individual_probs: list[float]) -> float:
    """
    Calculate probability for parlay (independent events).

    Args:
        individual_probs: List of probabilities for each leg

    Returns:
        Combined parlay probability
    """
    result = 1.0
    for prob in individual_probs:
        result *= prob
    return result


if __name__ == "__main__":
    # Quick tests
    print("EQ12 Odds Math Library Tests")
    print("============================")

    # Test American to decimal conversion
    print(f"American +150 to decimal: {american_to_decimal(150)}")
    print(f"American -110 to decimal: {american_to_decimal(-110)}")

    # Test EV calculation
    ev = calculate_ev_percent(0.55, 2.0)  # 55% chance at even odds
    print(f"EV for 55% chance at 2.0 odds: {ev:.2f}%")

    # Test Kelly criterion
    kelly = kelly_criterion(0.55, 2.0)
    print(f"Kelly fraction for 55% at 2.0 odds: {kelly:.3f}")

    # Test vig removal
    prob_a, prob_b = remove_vig_two_way(-110, -110)
    print(f"No-vig probabilities for -110/-110: {prob_a:.3f}, {prob_b:.3f}")

    print("All tests completed!")
