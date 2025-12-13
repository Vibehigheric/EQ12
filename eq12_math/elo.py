"""
EQ12 Math Library - Elo Rating System
====================================

Functions for Elo-based team rating calculations and strength analysis.

Functions:
- calculate_elo_probability(): Calculate win probability from Elo ratings
- update_elo_ratings(): Update ratings after match result
- calculate_home_field_advantage(): Factor in home field advantage
- elo_to_spread(): Convert Elo difference to point spread
- simulate_season(): Monte Carlo season simulation

Author: EQ12 Development Team
Version: 1.0.0
"""

import math


def calculate_elo_probability(
    rating_a: float, rating_b: float, home_advantage: float = 0.0
) -> float:
    """
    Calculate win probability for team A using Elo ratings.

    Args:
        rating_a: Elo rating for team A
        rating_b: Elo rating for team B
        home_advantage: Home field advantage in Elo points

    Returns:
        Win probability for team A (0.0 to 1.0)
    """
    # Adjust for home field advantage
    adjusted_rating_a = rating_a + home_advantage

    # Standard Elo probability formula
    rating_diff = adjusted_rating_a - rating_b
    probability = 1.0 / (1.0 + 10.0 ** (-rating_diff / 400.0))

    return probability


def update_elo_ratings(
    rating_a: float,
    rating_b: float,
    result: float,
    k_factor: float = 32.0,
    home_advantage: float = 0.0,
) -> tuple[float, float]:
    """
    Update Elo ratings after match result.

    Args:
        rating_a: Current Elo rating for team A
        rating_b: Current Elo rating for team B
        result: Match result (1.0 = A wins, 0.0 = B wins, 0.5 = draw)
        k_factor: K-factor determining update magnitude
        home_advantage: Home field advantage for team A

    Returns:
        Tuple of (new_rating_a, new_rating_b)
    """
    if not (0.0 <= result <= 1.0):
        raise ValueError(f"Invalid result: {result}")

    # Calculate expected probability
    expected_prob = calculate_elo_probability(rating_a, rating_b, home_advantage)

    # Calculate rating changes
    rating_change = k_factor * (result - expected_prob)

    new_rating_a = rating_a + rating_change
    new_rating_b = rating_b - rating_change

    return new_rating_a, new_rating_b


def calculate_home_field_advantage(sport: str) -> float:
    """
    Get typical home field advantage by sport (in Elo points).

    Args:
        sport: Sport name (e.g., 'nfl', 'nba', 'mlb')

    Returns:
        Home field advantage in Elo points
    """
    home_advantages = {
        "nfl": 65.0,  # ~3 point spread
        "nba": 100.0,  # ~3 point spread
        "mlb": 24.0,  # ~0.1 win probability
        "nhl": 35.0,  # ~0.05 win probability
        "soccer": 70.0,  # Significant home advantage
        "ncaaf": 85.0,  # College football higher than NFL
        "ncaab": 120.0,  # College basketball higher than NBA
    }

    return home_advantages.get(sport.lower(), 50.0)  # Default advantage


def elo_to_spread(rating_diff: float, points_per_100_elo: float = 2.85) -> float:
    """
    Convert Elo rating difference to point spread.

    Args:
        rating_diff: Difference in Elo ratings (favorite - underdog)
        points_per_100_elo: Points per 100 Elo rating difference

    Returns:
        Point spread (positive = favorite covers)
    """
    return (rating_diff / 100.0) * points_per_100_elo


def spread_to_elo(point_spread: float, points_per_100_elo: float = 2.85) -> float:
    """
    Convert point spread to Elo rating difference.

    Args:
        point_spread: Point spread
        points_per_100_elo: Points per 100 Elo rating difference

    Returns:
        Equivalent Elo rating difference
    """
    return (point_spread / points_per_100_elo) * 100.0


def calculate_elo_expected_margin(
    rating_a: float, rating_b: float, home_advantage: float = 0.0, points_per_100_elo: float = 2.85
) -> float:
    """
    Calculate expected scoring margin using Elo ratings.

    Args:
        rating_a: Team A Elo rating
        rating_b: Team B Elo rating
        home_advantage: Home field advantage for A
        points_per_100_elo: Scaling factor

    Returns:
        Expected margin for team A
    """
    rating_diff = (rating_a + home_advantage) - rating_b
    return elo_to_spread(rating_diff, points_per_100_elo)


def regression_to_mean(
    current_rating: float, baseline: float = 1500.0, regression_factor: float = 0.05
) -> float:
    """
    Apply regression to mean for off-season rating updates.

    Args:
        current_rating: Current team rating
        baseline: League average rating
        regression_factor: Fraction to regress (0.0 to 1.0)

    Returns:
        Regressed rating
    """
    if not (0.0 <= regression_factor <= 1.0):
        raise ValueError(f"Invalid regression factor: {regression_factor}")

    return current_rating * (1.0 - regression_factor) + baseline * regression_factor


def calculate_strength_of_schedule(team_games: list[dict], team_ratings: dict[str, float]) -> float:
    """
    Calculate strength of schedule based on opponent Elo ratings.

    Args:
        team_games: List of game dicts with 'opponent' and 'is_home' keys
        team_ratings: Dict mapping team names to Elo ratings

    Returns:
        Average opponent Elo rating
    """
    if not team_games:
        return 1500.0  # League average

    total_opponent_rating = 0.0
    valid_games = 0

    for game in team_games:
        opponent = game.get("opponent")
        if opponent in team_ratings:
            total_opponent_rating += team_ratings[opponent]
            valid_games += 1

    if valid_games == 0:
        return 1500.0

    return total_opponent_rating / valid_games


def simulate_game_outcome(
    rating_a: float, rating_b: float, home_advantage: float = 0.0, random_seed: int | None = None
) -> dict:
    """
    Simulate single game outcome using Elo probabilities.

    Args:
        rating_a: Team A Elo rating
        rating_b: Team B Elo rating
        home_advantage: Home advantage for A
        random_seed: Random seed for reproducibility

    Returns:
        Dict with simulation results
    """
    import random

    if random_seed is not None:
        random.seed(random_seed)

    win_prob = calculate_elo_probability(rating_a, rating_b, home_advantage)

    # Simulate win/loss
    random_value = random.random()
    team_a_wins = random_value < win_prob

    # Simulate score margin
    expected_margin = calculate_elo_expected_margin(rating_a, rating_b, home_advantage)

    # Add randomness to margin (normal distribution)
    import random

    margin_std = 14.0  # Standard deviation for score margins
    actual_margin = random.gauss(expected_margin, margin_std)

    return {
        "team_a_wins": team_a_wins,
        "win_probability": win_prob,
        "expected_margin": expected_margin,
        "actual_margin": actual_margin,
        "random_value": random_value,
    }


def calculate_playoff_odds(
    current_rating: float, games_remaining: int, playoff_threshold_rating: float = 1600.0
) -> float:
    """
    Estimate playoff odds based on current Elo and games remaining.

    Args:
        current_rating: Current team Elo rating
        games_remaining: Number of games left in season
        playoff_threshold_rating: Estimated rating needed for playoffs

    Returns:
        Playoff probability (0.0 to 1.0)
    """
    # Simplified model: probability improves with better rating
    # and decreases with games remaining (less time to improve)

    rating_advantage = current_rating - playoff_threshold_rating

    # Base probability from current rating
    base_prob = 1.0 / (1.0 + math.exp(-rating_advantage / 100.0))

    # Adjust for games remaining (more games = more opportunity)
    games_factor = min(1.0, games_remaining / 10.0)  # Cap at 10 games

    return base_prob * (0.5 + 0.5 * games_factor)


def get_elo_rating_percentile(rating: float, league_ratings: list[float]) -> float:
    """
    Calculate percentile rank of Elo rating within league.

    Args:
        rating: Team's Elo rating
        league_ratings: List of all team ratings in league

    Returns:
        Percentile rank (0.0 to 100.0)
    """
    if not league_ratings:
        return 50.0

    sorted_ratings = sorted(league_ratings)
    n = len(sorted_ratings)

    # Count teams with lower ratings
    lower_count = sum(1 for r in sorted_ratings if r < rating)

    # Handle ties
    equal_count = sum(1 for r in sorted_ratings if r == rating)

    # Calculate percentile using interpolation for ties
    percentile = (lower_count + equal_count / 2.0) / n * 100.0

    return percentile


if __name__ == "__main__":
    # Test Elo calculations
    print("EQ12 Elo Rating System Tests")
    print("============================")

    # Test win probability
    rating_chiefs = 1650
    rating_broncos = 1550
    home_adv = calculate_home_field_advantage("nfl")

    prob = calculate_elo_probability(rating_chiefs, rating_broncos, home_adv)
    print(f"Chiefs win probability: {prob:.1%}")

    # Test spread conversion
    spread = elo_to_spread(rating_chiefs - rating_broncos + home_adv)
    print(f"Implied spread: {spread:.1f}")

    # Test rating update
    new_chiefs, new_broncos = update_elo_ratings(
        rating_chiefs, rating_broncos, 1.0, home_advantage=home_adv
    )
    print(f"Updated ratings: Chiefs {new_chiefs:.0f}, Broncos {new_broncos:.0f}")

    # Test simulation
    sim_result = simulate_game_outcome(rating_chiefs, rating_broncos, home_adv)
    print(f"Simulation: A wins = {sim_result['team_a_wins']}")

    print("Elo tests completed!")
