"""
EQ12 Math Library - Monte Carlo Simulation Engine
================================================

Functions for Monte Carlo simulation of betting scenarios,
season outcomes, and portfolio analysis.

Functions:
- simulate_betting_session(): Simulate multiple bets over time
- simulate_kelly_growth(): Simulate bankroll growth with Kelly criterion
- monte_carlo_season(): Simulate full season outcomes
- simulate_arbitrage_opportunities(): Model arbitrage frequency
- calculate_risk_of_ruin(): Probability of bankroll depletion

Author: EQ12 Development Team
Version: 1.0.0
"""

import random

import numpy as np

try:
    from .elo import simulate_game_outcome
    from .odds import kelly_criterion
except ImportError:
    from elo import simulate_game_outcome
    from odds import kelly_criterion


def simulate_betting_session(
    initial_bankroll: float,
    bets: list[dict],
    num_simulations: int = 10000,
    random_seed: int | None = None,
) -> dict:
    """
    Simulate multiple betting sessions with given bet parameters.

    Args:
        initial_bankroll: Starting bankroll amount
        bets: List of bet dicts with 'probability', 'odds', 'stake_fraction'
        num_simulations: Number of simulation runs
        random_seed: Seed for reproducible results

    Returns:
        Dict with simulation statistics
    """
    if random_seed is not None:
        np.random.seed(random_seed)
        random.seed(random_seed)

    final_bankrolls = []
    max_drawdowns = []

    for _sim in range(num_simulations):
        bankroll = initial_bankroll
        peak_bankroll = initial_bankroll
        max_drawdown = 0.0

        for bet in bets:
            # Calculate bet size
            stake = bankroll * bet["stake_fraction"]

            if stake <= 0 or bankroll <= 0:
                break

            # Simulate bet outcome
            win_probability = bet["probability"]
            decimal_odds = bet["odds"]

            if random.random() < win_probability:
                # Win
                profit = stake * (decimal_odds - 1.0)
                bankroll += profit
            else:
                # Loss
                bankroll -= stake

            # Track drawdown
            if bankroll > peak_bankroll:
                peak_bankroll = bankroll

            current_drawdown = (peak_bankroll - bankroll) / peak_bankroll
            max_drawdown = max(max_drawdown, current_drawdown)

        final_bankrolls.append(bankroll)
        max_drawdowns.append(max_drawdown)

    # Calculate statistics
    final_bankrolls = np.array(final_bankrolls)
    max_drawdowns = np.array(max_drawdowns)

    return {
        "mean_final_bankroll": np.mean(final_bankrolls),
        "median_final_bankroll": np.median(final_bankrolls),
        "std_final_bankroll": np.std(final_bankrolls),
        "min_final_bankroll": np.min(final_bankrolls),
        "max_final_bankroll": np.max(final_bankrolls),
        "profit_probability": np.mean(final_bankrolls > initial_bankroll),
        "mean_return": np.mean(final_bankrolls / initial_bankroll - 1.0),
        "mean_max_drawdown": np.mean(max_drawdowns),
        "risk_of_ruin": np.mean(final_bankrolls <= 0),
        "percentile_5": np.percentile(final_bankrolls, 5),
        "percentile_95": np.percentile(final_bankrolls, 95),
    }


def simulate_kelly_growth(
    initial_bankroll: float,
    bet_frequency: int,
    edge: float,
    odds: float,
    num_simulations: int = 1000,
    time_periods: int = 100,
) -> dict:
    """
    Simulate bankroll growth using Kelly criterion betting.

    Args:
        initial_bankroll: Starting bankroll
        bet_frequency: Number of bets per time period
        edge: Betting edge (expected profit per dollar)
        odds: Decimal odds for bets
        num_simulations: Number of simulation runs
        time_periods: Number of time periods to simulate

    Returns:
        Dict with growth statistics
    """
    # Calculate Kelly fraction
    win_prob = 1.0 / odds + edge  # Implied prob + edge
    kelly_frac = kelly_criterion(win_prob, odds)

    # Limit Kelly fraction for safety
    kelly_frac = min(kelly_frac, 0.25)  # Never bet more than 25%

    bankroll_paths = []

    for _ in range(num_simulations):
        bankroll = initial_bankroll
        path = [bankroll]

        for period in range(time_periods):
            # Place multiple bets per period
            for _ in range(bet_frequency):
                if bankroll <= 0:
                    break

                # Kelly stake
                stake = bankroll * kelly_frac

                # Simulate outcome
                if random.random() < win_prob:
                    profit = stake * (odds - 1.0)
                    bankroll += profit
                else:
                    bankroll -= stake

            path.append(bankroll)

            if bankroll <= 0:
                # Fill rest of path with zeros
                path.extend([0] * (time_periods - period))
                break

        bankroll_paths.append(path)

    # Calculate statistics
    bankroll_paths = np.array(bankroll_paths)
    final_values = bankroll_paths[:, -1]

    return {
        "paths": bankroll_paths,
        "mean_final_value": np.mean(final_values),
        "median_final_value": np.median(final_values),
        "growth_rate": np.mean(np.log(final_values / initial_bankroll)) / time_periods,
        "volatility": np.std(np.log(final_values / initial_bankroll)),
        "risk_of_ruin": np.mean(final_values <= 0),
        "kelly_fraction_used": kelly_frac,
        "win_probability": win_prob,
    }


def monte_carlo_season(teams: dict, schedule: list[dict], num_simulations: int = 10000) -> dict:
    """
    Simulate full season using team ratings and schedule.

    Args:
        teams: Dict of team_name -> elo_rating
        schedule: List of game dicts with 'home', 'away', 'week' keys
        num_simulations: Number of season simulations

    Returns:
        Dict with season simulation results
    """
    team_names = list(teams.keys())
    season_results = {team: [] for team in team_names}

    for _ in range(num_simulations):
        # Initialize records
        team_wins = dict.fromkeys(team_names, 0)
        team_losses = dict.fromkeys(team_names, 0)

        # Simulate each game
        for game in schedule:
            home_team = game["home"]
            away_team = game["away"]

            if home_team not in teams or away_team not in teams:
                continue

            # Get ratings
            home_rating = teams[home_team]
            away_rating = teams[away_team]

            # Simulate game (home team gets advantage)
            result = simulate_game_outcome(home_rating, away_rating, 65.0)

            if result["team_a_wins"]:  # Home team wins
                team_wins[home_team] += 1
                team_losses[away_team] += 1
            else:  # Away team wins
                team_wins[away_team] += 1
                team_losses[home_team] += 1

        # Store season results
        for team in team_names:
            wins = team_wins[team]
            losses = team_losses[team]
            win_pct = wins / (wins + losses) if (wins + losses) > 0 else 0.0
            season_results[team].append({"wins": wins, "losses": losses, "win_percentage": win_pct})

    # Calculate team statistics
    team_stats = {}
    for team in team_names:
        results = season_results[team]
        wins_list = [r["wins"] for r in results]
        win_pcts = [r["win_percentage"] for r in results]

        team_stats[team] = {
            "mean_wins": np.mean(wins_list),
            "median_wins": np.median(wins_list),
            "std_wins": np.std(wins_list),
            "min_wins": np.min(wins_list),
            "max_wins": np.max(wins_list),
            "mean_win_pct": np.mean(win_pcts),
            "playoff_odds": np.mean([w >= 9 for w in wins_list]),  # 9+ wins
        }

    return {
        "team_stats": team_stats,
        "raw_results": season_results,
        "num_simulations": num_simulations,
    }


def simulate_arbitrage_opportunities(num_sims: int = 1000, arb_frequency: float = 0.02) -> dict:
    """
    Simulate arbitrage betting opportunities over time.

    Args:
        num_sims: Number of time periods to simulate
        arb_frequency: Probability of arbitrage per period

    Returns:
        Dict with arbitrage statistics
    """
    arbitrage_profits = []
    periods_with_arb = 0

    for _ in range(num_sims):
        # Check if arbitrage opportunity occurs
        if random.random() < arb_frequency:
            periods_with_arb += 1

            # Simulate arbitrage profit (typically 1-5%)
            profit_rate = random.uniform(0.005, 0.05)
            arbitrage_profits.append(profit_rate)
        else:
            arbitrage_profits.append(0.0)

    profits = np.array(arbitrage_profits)

    return {
        "total_opportunities": periods_with_arb,
        "opportunity_frequency": periods_with_arb / num_sims,
        "mean_profit_rate": np.mean(profits[profits > 0]) if periods_with_arb > 0 else 0.0,
        "total_profit_rate": np.sum(profits),
        "expected_weekly_profit": np.mean(profits) * 7,  # If daily frequency
        "profit_volatility": np.std(profits),
    }


def calculate_risk_of_ruin(
    bankroll: float,
    bet_size: float,
    win_probability: float,
    odds: float,
    ruin_threshold: float = 0.0,
) -> float:
    """
    Calculate theoretical risk of ruin for repeated betting.

    Args:
        bankroll: Current bankroll
        bet_size: Fixed bet size
        win_probability: Probability of winning each bet
        odds: Decimal odds for winning bet
        ruin_threshold: Bankroll level considered "ruin"

    Returns:
        Probability of ruin (0.0 to 1.0)
    """
    if bet_size >= bankroll:
        return 1.0  # Immediate ruin possible

    # Calculate bet parameters
    loss_prob = 1.0 - win_probability
    win_amount = bet_size * (odds - 1.0)
    loss_amount = bet_size

    # Expected value per bet
    expected_value = win_probability * win_amount - loss_prob * loss_amount

    if expected_value <= 0:
        return 1.0  # Negative expectation leads to eventual ruin

    # Gambler's ruin formula approximation
    # For positive expectation games with fixed bet sizes

    p = win_probability
    q = loss_prob

    if abs(p - q) < 1e-10:  # Fair game
        return 1.0

    # Calculate ruin probability using random walk theory
    # This is an approximation for the discrete case

    current_units = bankroll / bet_size
    ruin_units = ruin_threshold / bet_size

    if current_units <= ruin_units:
        return 1.0

    # Probability ratio
    prob_ratio = q / p

    if prob_ratio == 1.0:
        return 1.0

    # Ruin probability formula
    units_to_ruin = current_units - ruin_units

    # Calculate ruin probability
    ruin_prob = prob_ratio**units_to_ruin if prob_ratio < 1.0 else 1.0

    return min(ruin_prob, 1.0)


def simulate_portfolio_performance(
    bets: list[dict], num_simulations: int = 1000, correlation_matrix: np.ndarray | None = None
) -> dict:
    """
    Simulate performance of a betting portfolio with potential correlations.

    Args:
        bets: List of bet dicts with probability, odds, stake
        num_simulations: Number of portfolio simulations
        correlation_matrix: Optional correlation between bet outcomes

    Returns:
        Portfolio performance statistics
    """
    n_bets = len(bets)
    portfolio_returns = []

    for _ in range(num_simulations):
        total_stake = sum(bet["stake"] for bet in bets)
        total_return = 0.0

        if correlation_matrix is not None:
            # Generate correlated outcomes
            random_normals = np.random.multivariate_normal(np.zeros(n_bets), correlation_matrix)

            for i, bet in enumerate(bets):
                # Convert normal to uniform to binary outcome
                prob = bet["probability"]
                threshold = np.percentile(random_normals, prob * 100)
                wins = random_normals[i] >= threshold

                if wins:
                    profit = bet["stake"] * (bet["odds"] - 1.0)
                    total_return += profit
                else:
                    total_return -= bet["stake"]
        else:
            # Independent outcomes
            for bet in bets:
                if random.random() < bet["probability"]:
                    profit = bet["stake"] * (bet["odds"] - 1.0)
                    total_return += profit
                else:
                    total_return -= bet["stake"]

        portfolio_return = total_return / total_stake if total_stake > 0 else 0.0
        portfolio_returns.append(portfolio_return)

    returns = np.array(portfolio_returns)

    return {
        "mean_return": np.mean(returns),
        "median_return": np.median(returns),
        "std_return": np.std(returns),
        "min_return": np.min(returns),
        "max_return": np.max(returns),
        "profit_probability": np.mean(returns > 0),
        "sharpe_ratio": np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0,
        "percentile_5": np.percentile(returns, 5),
        "percentile_95": np.percentile(returns, 95),
        "value_at_risk_5pct": np.percentile(returns, 5),
    }


if __name__ == "__main__":
    # Test simulation functions
    print("EQ12 Monte Carlo Simulation Tests")
    print("=================================")

    # Test betting session simulation
    bets = [
        {"probability": 0.55, "odds": 1.9, "stake_fraction": 0.02},
        {"probability": 0.60, "odds": 1.8, "stake_fraction": 0.03},
        {"probability": 0.52, "odds": 2.0, "stake_fraction": 0.015},
    ]

    session_result = simulate_betting_session(1000, bets * 50, 1000)
    print(f"Mean final bankroll: ${session_result['mean_final_bankroll']:.0f}")
    print(f"Profit probability: {session_result['profit_probability']:.1%}")

    # Test Kelly growth simulation
    kelly_result = simulate_kelly_growth(1000, 5, 0.05, 1.9, 100, 50)
    print(f"Kelly growth rate: {kelly_result['growth_rate']:.1%} per period")
    print(f"Kelly risk of ruin: {kelly_result['risk_of_ruin']:.1%}")

    # Test risk of ruin calculation
    ruin_prob = calculate_risk_of_ruin(1000, 50, 0.55, 1.9)
    print(f"Risk of ruin: {ruin_prob:.1%}")

    print("Simulation tests completed!")
