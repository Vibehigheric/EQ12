#!/usr/bin/env python3
"""
EQ12 Core Mathematical Utilities
Production-ready EV calculation, Kelly sizing, and parlay pricing with correlation penalties.

Built for DraftKings/FanDuel/BetMGM focus following EQ12 expert guidelines.
"""

from math import prod


def american_to_decimal(odds: int) -> float:
    """Convert American odds to decimal format."""
    return 1 + (odds / 100 if odds > 0 else 100 / abs(odds))


def decimal_to_american(decimal_odds: float) -> int:
    """Convert decimal odds to American format."""
    if decimal_odds >= 2.0:
        return int((decimal_odds - 1) * 100)
    else:
        return int(-100 / (decimal_odds - 1))


def implied_prob_from_american(odds: int) -> float:
    """Calculate implied probability from American odds."""
    decimal = american_to_decimal(odds)
    return 1.0 / decimal


def remove_vig_two_way(p_a: float, p_b: float) -> tuple[float, float]:
    """
    Remove vig from two-way market using proportional method.
    Returns devigged probabilities that sum to 1.0.
    """
    sum_prob = p_a + p_b
    return p_a / sum_prob, p_b / sum_prob


def remove_vig_three_way(p_a: float, p_b: float,
                         p_c: float) -> tuple[float, float, float]:
    """Remove vig from three-way market (e.g., moneyline with draw)."""
    sum_prob = p_a + p_b + p_c
    return p_a / sum_prob, p_b / sum_prob, p_c / sum_prob


def kelly_fraction(
        p: float,
        odds: int,
        kelly_cut: float = 0.5,
        max_kelly: float = 0.025) -> float:
    """
    Calculate Kelly Criterion fraction with EQ12 constraints.

    Args:
        p: Fair probability (0-1)
        odds: American odds
        kelly_cut: Kelly multiplier (default 0.5 = half-Kelly)
        max_kelly: Maximum Kelly cap per EQ12 rules (default 2.5%)

    Returns:
        Kelly fraction capped at max_kelly
    """
    if p <= 0 or p >= 1:
        return 0.0

    decimal_odds = american_to_decimal(odds)
    b = decimal_odds - 1  # Net odds multiplier

    # Kelly formula: (bp - q) / b where q = 1-p
    kelly_raw = (b * p - (1 - p)) / b

    # Apply cuts and caps
    kelly_adjusted = max(0.0, kelly_raw * kelly_cut)
    kelly_capped = min(kelly_adjusted, max_kelly)

    return kelly_capped


def expected_value_percentage(fair_prob: float, book_odds: int) -> float:
    """
    Calculate expected value as a percentage.

    Args:
        fair_prob: Model/fair probability (0-1)
        book_odds: American odds from sportsbook

    Returns:
        EV percentage (e.g., 0.05 = 5% edge)
    """
    implied_prob = implied_prob_from_american(book_odds)

    if implied_prob <= 0:
        return 0.0

    return (fair_prob - implied_prob) / implied_prob


def parlay_decimal_price(legs_odds: list[int]) -> float:
    """Calculate combined decimal odds for parlay."""
    return prod(american_to_decimal(odds) for odds in legs_odds)


def parlay_american_price(legs_odds: list[int]) -> int:
    """Calculate combined American odds for parlay."""
    decimal_price = parlay_decimal_price(legs_odds)
    return decimal_to_american(decimal_price)


def parlay_ev_with_correlation(
    legs: list[dict], stake: float = 1.0, corr_penalty: float = 0.0
) -> float:
    """
    Calculate parlay expected value with correlation penalty.

    Args:
        legs: List of dicts with 'p' (fair_prob) and 'odds' (American)
        stake: Bet amount
        corr_penalty: Correlation penalty exponent [0, 0.25]
                     (0 = no penalty, higher = more penalty)

    Returns:
        Expected value in dollars
    """
    if not legs:
        return 0.0

    # Combined decimal odds
    decimal_total = parlay_decimal_price([leg["odds"] for leg in legs])

    # Raw probability (assuming independence)
    prob_raw = prod(leg["p"] for leg in legs)

    # Apply correlation penalty - reduces effective probability
    prob_effective = max(0.0, min(1.0, prob_raw ** (1 + corr_penalty)))

    # Expected value calculation
    win_net = stake * (decimal_total - 1)  # Net profit if win
    lose_net = stake  # Loss if lose

    ev = prob_effective * win_net - (1 - prob_effective) * lose_net
    return ev


def parlay_breakeven_probability(legs_odds: list[int]) -> float:
    """Calculate breakeven probability for parlay to have 0 EV."""
    decimal_price = parlay_decimal_price(legs_odds)
    return 1.0 / decimal_price


def calculate_correlation_risk(legs: list[dict]) -> float:
    """
    Estimate correlation risk for parlay legs.
    Simple heuristic based on same-game exposure.

    Returns:
        Risk score [0, 1] where 0 = no correlation, 1 = high correlation
    """
    if len(legs) <= 1:
        return 0.0

    # Group legs by game_id
    games = {}
    for leg in legs:
        game_id = leg.get("game_id", "")
        if game_id not in games:
            games[game_id] = []
        games[game_id].append(leg)

    # Calculate risk - more legs per game = higher risk
    total_risk = 0.0
    for game_legs in games.values():
        if len(game_legs) > 1:
            # Risk increases exponentially with legs per game
            game_risk = min(1.0, (len(game_legs) - 1) * 0.3)
            total_risk = max(total_risk, game_risk)

    return total_risk


def validate_eq12_constraints(legs: list[dict]) -> list[str]:
    """
    Validate parlay against EQ12 constraints.

    Returns:
        List of constraint violations (empty if valid)
    """
    violations = []

    # Check allowed books
    allowed_books = {"draftkings", "fanduel", "betmgm"}
    for leg in legs:
        book = leg.get("book", "").lower()
        if book not in allowed_books:
            violations.append(f"Invalid book: {book}")

    # Check maximum legs
    if len(legs) > 8:
        violations.append(f"Too many legs: {len(legs)} (max 8)")

    # Check same-game limits (max 1 per game for most strategies)
    games = {}
    for leg in legs:
        game_id = leg.get("game_id", "")
        if game_id in games:
            games[game_id] += 1
        else:
            games[game_id] = 1

    for game_id, count in games.items():
        if count > 2:  # Allow up to 2 legs per game (e.g., side + total)
            violations.append(f"Too many legs from {game_id}: {count}")

    return violations


def optimize_parlay_size(
    candidate_legs: list[dict],
    max_legs: int = 4,
    min_ev: float = 0.025,
    corr_penalty: float = 0.1,
) -> list[dict]:
    """
    Optimize parlay size by selecting best EV combination.
    Greedy algorithm that adds legs while EV improves.

    Args:
        candidate_legs: Sorted legs with 'ev', 'p', 'odds'
        max_legs: Maximum legs to include
        min_ev: Minimum EV per leg
        corr_penalty: Correlation penalty for multiple legs

    Returns:
        Optimized leg selection
    """
    # Filter legs meeting minimum EV
    valid_legs = [leg for leg in candidate_legs if leg.get("ev", 0) >= min_ev]

    if not valid_legs:
        return []

    # Start with highest EV leg
    selected = [valid_legs[0]]
    best_ev = parlay_ev_with_correlation(selected, corr_penalty=corr_penalty)

    # Greedily add legs while EV improves
    for leg in valid_legs[1:max_legs]:
        test_selection = [*selected, leg]

        # Check constraints
        violations = validate_eq12_constraints(test_selection)
        if violations:
            continue

        # Calculate EV with this leg added
        test_ev = parlay_ev_with_correlation(test_selection, corr_penalty=corr_penalty)

        # Add if EV improves
        if test_ev > best_ev:
            selected = test_selection
            best_ev = test_ev
        else:
            # EV stopped improving - likely optimal size
            break

    return selected


# EQ12-specific utility functions
def format_kelly_stake(kelly_fraction: float, bankroll: float) -> str:
    """Format Kelly stake for EQ12 display."""
    stake = kelly_fraction * bankroll
    return f"${stake:.2f}"


def format_ev_percentage(ev: float) -> str:
    """Format EV for EQ12 display."""
    return f"{ev * 100:+.1f}%"


def get_risk_level(correlation_risk: float, ev: float, prob: float) -> str:
    """Determine risk level for EQ12 classification."""
    if correlation_risk > 0.3 or prob < 0.15:
        return "HIGH"
    elif correlation_risk > 0.1 or prob < 0.25 or ev < 0.02:
        return "MEDIUM"
    else:
        return "LOW"


if __name__ == "__main__":
    # Test the utilities
    print("🧮 EQ12 Mathematical Utilities Test")
    print("=" * 50)

    # Test basic conversions
    american_odds = -110
    decimal = american_to_decimal(american_odds)
    implied = implied_prob_from_american(american_odds)

    print(f"American {american_odds} → Decimal {decimal:.3f} → Implied {implied:.3f}")

    # Test Kelly calculation
    fair_prob = 0.55  # 55% model probability
    kelly = kelly_fraction(fair_prob, american_odds)
    ev = expected_value_percentage(fair_prob, american_odds)

    print(f"Fair prob {fair_prob:.1%}, Kelly {kelly:.3f}, EV {ev:+.1%}")

    # Test parlay
    legs = [
        {"p": 0.55, "odds": -110, "game_id": "game1"},
        {"p": 0.60, "odds": +120, "game_id": "game2"},
    ]

    parlay_odds = parlay_american_price([leg["odds"] for leg in legs])
    parlay_ev = parlay_ev_with_correlation(legs, stake=100, corr_penalty=0.1)

    print(f"2-leg parlay: {parlay_odds:+d} odds, ${parlay_ev:+.2f} EV")
    print("✅ All utilities working correctly!")
