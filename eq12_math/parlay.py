"""
EQ12 Math Library - Parlay Calculations with Correlation Analysis
================================================================

Functions for parlay optimization, correlation detection, and
same-game parlay (SGP) analysis.

Functions:
- independent_parlay_probability(): Calculate parlay probability for independent events
- correlated_parlay_probability(): Calculate with correlation matrix
- detect_sgp_correlations(): Identify correlated SGP legs
- optimize_parlay_selection(): Select optimal parlay legs
- calculate_parlay_ev(): Calculate parlay expected value

Author: EQ12 Development Team
Version: 1.0.0
"""

import numpy as np
from scipy import stats

try:
    from .odds import calculate_ev, kelly_criterion
except ImportError:
    from odds import calculate_ev, kelly_criterion


def independent_parlay_probability(leg_probabilities: list[float]) -> float:
    """
    Calculate parlay probability assuming independent events.

    Args:
        leg_probabilities: List of individual leg probabilities

    Returns:
        Combined parlay probability
    """
    if not leg_probabilities:
        return 0.0

    result = 1.0
    for prob in leg_probabilities:
        if not (0.0 <= prob <= 1.0):
            raise ValueError(f"Invalid probability: {prob}")
        result *= prob

    return result


def correlated_parlay_probability(
    leg_probabilities: list[float], correlation_matrix: np.ndarray, n_simulations: int = 10000
) -> float:
    """
    Calculate parlay probability with correlations using Monte Carlo.

    Args:
        leg_probabilities: List of individual leg probabilities
        correlation_matrix: Correlation matrix between legs
        n_simulations: Number of Monte Carlo simulations

    Returns:
        Correlated parlay probability
    """
    n_legs = len(leg_probabilities)

    if correlation_matrix.shape != (n_legs, n_legs):
        raise ValueError("Correlation matrix size mismatch")

    # Convert probabilities to normal distribution thresholds
    normal_thresholds = [stats.norm.ppf(prob) for prob in leg_probabilities]

    # Generate correlated random variables
    successes = 0

    for _ in range(n_simulations):
        # Generate correlated normal variables
        random_normals = np.random.multivariate_normal(
            mean=np.zeros(n_legs), cov=correlation_matrix, size=1
        )[0]

        # Check if all legs hit
        all_hit = True
        for _i, (threshold, random_val) in enumerate(
            zip(normal_thresholds, random_normals, strict=False)
        ):
            if random_val <= threshold:
                all_hit = False
                break

        if all_hit:
            successes += 1

    return successes / n_simulations


def detect_sgp_correlations(leg_types: list[str]) -> np.ndarray:
    """
    Detect correlations between same-game parlay leg types.

    Args:
        leg_types: List of market types (e.g. ['moneyline', 'spread', 'total'])

    Returns:
        Correlation matrix
    """
    n_legs = len(leg_types)
    correlation_matrix = np.eye(n_legs)  # Start with identity matrix

    # Predefined correlation rules for common SGP combinations
    correlation_rules = {
        ("moneyline", "spread"): 0.85,  # Highly correlated
        ("moneyline", "team_total"): 0.70,  # Strong correlation
        ("spread", "total"): 0.15,  # Slight correlation
        ("player_points", "team_total"): 0.40,  # Moderate correlation
        ("first_half", "full_game"): 0.75,  # Strong correlation
        ("player_assists", "player_points"): 0.30,  # Some correlation
        ("team_total_over", "player_over"): 0.50,  # Moderate correlation
    }

    # Apply correlation rules
    for i in range(n_legs):
        for j in range(i + 1, n_legs):
            market_i = leg_types[i].lower().replace("_", "")
            market_j = leg_types[j].lower().replace("_", "")

            correlation = 0.0

            # Check each correlation rule
            for (type_a, type_b), corr_value in correlation_rules.items():
                type_a_norm = type_a.replace("_", "")
                type_b_norm = type_b.replace("_", "")

                if (type_a_norm in market_i and type_b_norm in market_j) or (
                    type_b_norm in market_i and type_a_norm in market_j
                ):
                    correlation = corr_value
                    break

            # Apply correlation symmetrically
            correlation_matrix[i, j] = correlation
            correlation_matrix[j, i] = correlation

    return correlation_matrix


def has_forbidden_correlations(correlation_matrix: np.ndarray, threshold: float = 0.25) -> bool:
    """
    Check if parlay has correlations above threshold.

    Args:
        correlation_matrix: Correlation matrix
        threshold: Maximum allowed correlation

    Returns:
        True if forbidden correlations exist
    """
    n = correlation_matrix.shape[0]

    for i in range(n):
        for j in range(i + 1, n):
            if abs(correlation_matrix[i, j]) > threshold:
                return True

    return False


def optimize_parlay_selection(
    leg_data: list[dict], max_legs: int = 4, min_ev_threshold: float = 2.0
) -> list[dict]:
    """
    Select optimal legs for parlay based on EV and correlation.

    Args:
        leg_data: List of leg dictionaries with 'prob', 'odds', 'market_type'
        max_legs: Maximum number of legs in parlay
        min_ev_threshold: Minimum EV% required per leg

    Returns:
        Optimized list of legs for parlay
    """
    # Filter legs by minimum EV
    viable_legs = []
    for leg in leg_data:
        ev_percent = calculate_ev(leg["prob"], leg["odds"]) * 100
        if ev_percent >= min_ev_threshold:
            leg["ev_percent"] = ev_percent
            viable_legs.append(leg)

    if len(viable_legs) < 2:
        return []

    # Sort by EV descending
    viable_legs.sort(key=lambda x: x["ev_percent"], reverse=True)

    # Take top legs up to max_legs
    selected_legs = viable_legs[:max_legs]

    # Check for forbidden correlations if same game
    if _is_same_game_parlay(selected_legs):
        market_types = [leg["market_type"] for leg in selected_legs]
        correlation_matrix = detect_sgp_correlations(market_types)

        if has_forbidden_correlations(correlation_matrix):
            # Remove most correlated legs iteratively
            selected_legs = _remove_correlated_legs(selected_legs, correlation_matrix)

    return selected_legs


def calculate_parlay_ev(leg_data: list[dict], use_correlation: bool = True) -> dict:
    """
    Calculate expected value for parlay.

    Args:
        leg_data: List of leg data with 'prob', 'odds', 'market_type'
        use_correlation: Whether to account for correlations

    Returns:
        Dictionary with parlay EV analysis
    """
    if len(leg_data) < 2:
        raise ValueError("Parlay requires at least 2 legs")

    probabilities = [leg["prob"] for leg in leg_data]
    decimal_odds = [leg["odds"] for leg in leg_data]

    # Calculate parlay odds (multiply decimals)
    parlay_odds = 1.0
    for odds in decimal_odds:
        parlay_odds *= odds

    # Calculate joint probability
    if use_correlation and _is_same_game_parlay(leg_data):
        market_types = [leg["market_type"] for leg in leg_data]
        correlation_matrix = detect_sgp_correlations(market_types)
        joint_prob = correlated_parlay_probability(probabilities, correlation_matrix)
    else:
        joint_prob = independent_parlay_probability(probabilities)

    # Calculate EV
    parlay_ev = joint_prob * (parlay_odds - 1.0) - (1.0 - joint_prob)
    parlay_ev_percent = parlay_ev * 100.0

    # Calculate Kelly fraction
    kelly_frac = kelly_criterion(joint_prob, parlay_odds)

    return {
        "joint_probability": joint_prob,
        "parlay_odds": parlay_odds,
        "parlay_ev": parlay_ev,
        "parlay_ev_percent": parlay_ev_percent,
        "kelly_fraction": kelly_frac,
        "num_legs": len(leg_data),
        "is_same_game": _is_same_game_parlay(leg_data),
    }


def calculate_parlay_variance(leg_data: list[dict]) -> float:
    """
    Calculate variance of parlay outcomes.

    Args:
        leg_data: List of leg data

    Returns:
        Parlay variance
    """
    probabilities = [leg["prob"] for leg in leg_data]
    decimal_odds = [leg["odds"] for leg in leg_data]

    # For independent events, parlay variance calculation
    parlay_odds = 1.0
    for odds in decimal_odds:
        parlay_odds *= odds

    joint_prob = independent_parlay_probability(probabilities)

    # Variance = E[X^2] - E[X]^2
    # For betting: X = (parlay_odds - 1) with prob joint_prob, -1 with prob (1-joint_prob)

    win_outcome = parlay_odds - 1.0
    lose_outcome = -1.0

    expected_value = joint_prob * win_outcome + (1.0 - joint_prob) * lose_outcome
    expected_value_squared = joint_prob * (win_outcome**2) + (1.0 - joint_prob) * (lose_outcome**2)

    variance = expected_value_squared - (expected_value**2)

    return variance


def parlay_breakeven_probability(decimal_odds_list: list[float]) -> float:
    """
    Calculate breakeven probability for parlay.

    Args:
        decimal_odds_list: List of decimal odds for each leg

    Returns:
        Breakeven probability for parlay
    """
    parlay_odds = 1.0
    for odds in decimal_odds_list:
        parlay_odds *= odds

    return 1.0 / parlay_odds


def _is_same_game_parlay(leg_data: list[dict]) -> bool:
    """Check if legs are from the same game."""
    if not leg_data:
        return False

    # Extract game identifiers (simplified - would be more sophisticated in production)
    games = set()
    for leg in leg_data:
        game_id = leg.get("game_id", "unknown")
        if game_id == "unknown":
            # Try to infer from selection text
            selection = leg.get("selection", "")
            # Simple heuristic: extract team names
            parts = selection.split()
            game_id = f"{parts[0]}_{parts[1]}" if len(parts) >= 2 else selection
        games.add(game_id)

    return len(games) == 1


def _remove_correlated_legs(legs: list[dict], correlation_matrix: np.ndarray) -> list[dict]:
    """Remove legs with highest correlations iteratively."""

    while has_forbidden_correlations(correlation_matrix):
        n = len(legs)
        if n <= 2:
            break  # Keep minimum parlay size

        # Find pair with highest correlation
        max_correlation = 0.0
        remove_idx = -1

        for i in range(n):
            for j in range(i + 1, n):
                if abs(correlation_matrix[i, j]) > max_correlation:
                    max_correlation = abs(correlation_matrix[i, j])
                    # Remove the leg with lower EV
                    remove_idx = i if legs[i]["ev_percent"] < legs[j]["ev_percent"] else j

        if remove_idx >= 0:
            # Remove leg and update matrix
            legs.pop(remove_idx)
            correlation_matrix = np.delete(correlation_matrix, remove_idx, axis=0)
            correlation_matrix = np.delete(correlation_matrix, remove_idx, axis=1)
        else:
            break

    return legs


if __name__ == "__main__":
    # Test parlay calculations
    print("EQ12 Parlay Math Library Tests")
    print("==============================")

    # Test independent parlay
    probs = [0.6, 0.55, 0.7]
    joint_prob = independent_parlay_probability(probs)
    print(f"Independent parlay probability: {joint_prob:.3f}")

    # Test correlation detection
    markets = ["moneyline", "spread", "total"]
    corr_matrix = detect_sgp_correlations(markets)
    print(f"SGP correlations:\n{corr_matrix}")

    # Test parlay EV
    leg_data = [
        {"prob": 0.6, "odds": 1.8, "market_type": "moneyline", "game_id": "game1"},
        {"prob": 0.55, "odds": 2.0, "market_type": "total", "game_id": "game1"},
    ]

    parlay_result = calculate_parlay_ev(leg_data)
    print(f"Parlay EV: {parlay_result['parlay_ev_percent']:.2f}%")

    print("Parlay tests completed!")
