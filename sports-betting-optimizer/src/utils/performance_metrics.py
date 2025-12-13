#!/usr/bin/env python3
"""
Performance Metrics Module for Sports Betting Analysis
Professional-grade risk and return calculations
"""

import statistics


class PerformanceAnalyzer:
    """
    Professional Performance Analysis Class for Betting Systems
    """

    def __init__(self, returns: list[float], bet_amounts: list[float] | None = None):
        """
        Initialize analyzer with return data

        Args:
            returns: List of period returns (as decimals)
            bet_amounts: Optional list of bet amounts for each period
        """
        self.returns = returns
        self.bet_amounts = bet_amounts or [1.0] * len(returns)

    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio for the return series"""
        return calculate_sharpe_ratio(self.returns, risk_free_rate)

    def kelly_fraction(self, win_prob: float | None = None, avg_odds: float | None = None) -> float:
        """
        Calculate Kelly fraction for optimal bet sizing

        If win_prob and avg_odds not provided, estimates from returns
        """
        if win_prob is not None and avg_odds is not None:
            return kelly_fraction(win_prob, avg_odds)

        # Estimate from returns if not provided
        wins = [r for r in self.returns if r > 0]
        if not wins:
            return 0.0

        win_prob = len(wins) / len(self.returns)
        avg_odds = statistics.mean(wins) if wins else 1.0

        return kelly_fraction(win_prob, avg_odds)

    def value_at_risk(self, confidence: float = 0.95) -> float:
        """Calculate Value at Risk"""
        return calculate_value_at_risk(self.returns, confidence)

    def generate_report(self) -> dict:
        """Generate comprehensive performance report"""
        balance_history = []
        balance = 1000  # Starting balance

        for ret in self.returns:
            balance = balance * (1 + ret)
            balance_history.append(balance)

        return generate_performance_report(
            returns=self.returns,
            balance_history=balance_history,
            outcomes=["win" if r > 0 else "loss" for r in self.returns],
        )


def calculate_roi(
    initial_balance: float, final_balance: float, total_staked: float | None = None
) -> float:
    """
    Calculate Return on Investment (ROI)

    Args:
        initial_balance: Starting bankroll
        final_balance: Ending bankroll
        total_staked: Optional total amount wagered

    Returns:
        ROI as percentage
    """
    if total_staked and total_staked > 0:
        # ROI based on total staked amount
        net_profit = final_balance - initial_balance
        return (net_profit / total_staked) * 100
    # ROI based on initial investment
    return ((final_balance - initial_balance) / initial_balance) * 100


def calculate_sharpe_ratio(returns: list[float], risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe Ratio for risk-adjusted returns

    Args:
        returns: List of period returns (as decimals, not percentages)
        risk_free_rate: Annual risk-free rate (default 2%)

    Returns:
        Sharpe ratio (higher is better)
    """
    if len(returns) < 2:
        return 0.0

    # Convert annual risk-free rate to period rate
    period_rf_rate = risk_free_rate / len(returns)

    excess_returns = [r - period_rf_rate for r in returns]

    if statistics.stdev(returns) == 0:
        return 0.0

    return statistics.mean(excess_returns) / statistics.stdev(returns)


def calculate_sortino_ratio(returns: list[float], risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sortino Ratio (downside deviation only)

    Args:
        returns: List of period returns
        risk_free_rate: Annual risk-free rate

    Returns:
        Sortino ratio (higher is better)
    """
    if len(returns) < 2:
        return 0.0

    period_rf_rate = risk_free_rate / len(returns)
    excess_returns = [r - period_rf_rate for r in returns]

    # Only consider negative returns for downside deviation
    downside_returns = [r for r in excess_returns if r < 0]

    if not downside_returns:
        return float("inf")  # No downside risk

    downside_deviation = statistics.stdev(downside_returns)

    if downside_deviation == 0:
        return 0.0

    return statistics.mean(excess_returns) / downside_deviation


def calculate_max_drawdown(balance_history: list[float]) -> tuple[float, int, int]:
    """
    Calculate Maximum Drawdown from balance history

    Args:
        balance_history: List of bankroll balances over time

    Returns:
        Tuple of (max_drawdown_percentage, peak_index, trough_index)
    """
    if len(balance_history) < 2:
        return 0.0, 0, 0

    peak = balance_history[0]
    peak_index = 0
    max_drawdown = 0.0
    max_dd_peak_idx = 0
    max_dd_trough_idx = 0

    for i, balance in enumerate(balance_history):
        if balance > peak:
            peak = balance
            peak_index = i

        drawdown = (peak - balance) / peak if peak > 0 else 0

        if drawdown > max_drawdown:
            max_drawdown = drawdown
            max_dd_peak_idx = peak_index
            max_dd_trough_idx = i

    return max_drawdown * 100, max_dd_peak_idx, max_dd_trough_idx


def calculate_win_rate(outcomes: list[str]) -> dict[str, float]:
    """
    Calculate win rate and other outcome statistics

    Args:
        outcomes: List of bet outcomes ('win', 'loss', 'push', 'void')

    Returns:
        Dictionary with win rate and other statistics
    """
    if not outcomes:
        return {
            "win_rate": 0.0,
            "loss_rate": 0.0,
            "push_rate": 0.0,
            "void_rate": 0.0,
            "total_bets": 0,
        }

    total_bets = len(outcomes)
    wins = outcomes.count("win")
    losses = outcomes.count("loss")
    pushes = outcomes.count("push")
    voids = outcomes.count("void")

    return {
        "win_rate": (wins / total_bets) * 100,
        "loss_rate": (losses / total_bets) * 100,
        "push_rate": (pushes / total_bets) * 100,
        "void_rate": (voids / total_bets) * 100,
        "total_bets": total_bets,
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "voids": voids,
    }


def kelly_fraction(win_probability: float, odds: float) -> float:
    """
    Calculate optimal Kelly Criterion stake fraction

    Args:
        win_probability: Probability of winning (0.0 to 1.0)
        odds: Decimal odds (e.g., 2.0 for even money)

    Returns:
        Optimal fraction of bankroll to stake (0.0 to 1.0)
    """
    if odds <= 1.0 or win_probability <= 0.0 or win_probability >= 1.0:
        return 0.0

    # Kelly formula: f* = (bp - q) / b
    # where b = odds - 1, p = win probability, q = loss probability
    b = odds - 1
    p = win_probability
    q = 1 - win_probability

    kelly_f = (b * p - q) / b

    # Never recommend more than 25% of bankroll (fractional Kelly)
    return max(0.0, min(kelly_f, 0.25))


def calculate_calmar_ratio(returns: list[float], max_drawdown: float) -> float:
    """
    Calculate Calmar Ratio (Annual Return / Maximum Drawdown)

    Args:
        returns: List of period returns
        max_drawdown: Maximum drawdown as percentage

    Returns:
        Calmar ratio
    """
    if not returns or max_drawdown == 0:
        return 0.0

    annual_return = (statistics.mean(returns) * len(returns)) * 100
    return annual_return / max_drawdown


def calculate_value_at_risk(returns: list[float], confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) at given confidence level

    Args:
        returns: List of period returns
        confidence_level: Confidence level (e.g., 0.95 for 95% VaR)

    Returns:
        VaR as percentage
    """
    if not returns:
        return 0.0

    sorted_returns = sorted(returns)
    index = int((1 - confidence_level) * len(sorted_returns))

    if index >= len(sorted_returns):
        index = len(sorted_returns) - 1

    return abs(sorted_returns[index] * 100)


def calculate_expected_shortfall(returns: list[float], confidence_level: float = 0.95) -> float:
    """
    Calculate Expected Shortfall (Conditional VaR)

    Args:
        returns: List of period returns
        confidence_level: Confidence level

    Returns:
        Expected shortfall as percentage
    """
    if not returns:
        return 0.0

    sorted_returns = sorted(returns)
    cutoff_index = int((1 - confidence_level) * len(sorted_returns))

    if cutoff_index == 0:
        return 0.0

    tail_returns = sorted_returns[:cutoff_index]
    return abs(statistics.mean(tail_returns) * 100) if tail_returns else 0.0


def calculate_profit_factor(gross_profit: float, gross_loss: float) -> float:
    """
    Calculate Profit Factor (Gross Profit / Gross Loss)

    Args:
        gross_profit: Total profit from winning bets
        gross_loss: Total loss from losing bets

    Returns:
        Profit factor (>1.0 is profitable)
    """
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0

    return gross_profit / abs(gross_loss)


def generate_performance_report(
    balance_history: list[float],
    returns: list[float],
    outcomes: list[str],
    stakes: list[float],
    payouts: list[float],
    initial_balance: float,
    risk_free_rate: float = 0.02,
) -> dict:
    """
    Generate comprehensive performance report

    Args:
        balance_history: List of bankroll balances
        returns: List of period returns
        outcomes: List of bet outcomes
        stakes: List of stake amounts
        payouts: List of payout amounts
        initial_balance: Starting balance
        risk_free_rate: Risk-free rate for Sharpe calculation

    Returns:
        Comprehensive performance dictionary
    """
    final_balance = balance_history[-1] if balance_history else initial_balance
    total_staked = sum(stakes) if stakes else 0
    gross_profit = sum(p for p in payouts if p > 0) if payouts else 0
    gross_loss = (
        sum(abs(s) for s, p in zip(stakes, payouts, strict=False) if p == 0)
        if stakes and payouts
        else 0
    )

    # Basic metrics
    roi = calculate_roi(initial_balance, final_balance, total_staked)
    net_profit = final_balance - initial_balance

    # Risk metrics
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate) if returns else 0
    sortino = calculate_sortino_ratio(returns, risk_free_rate) if returns else 0
    max_dd, _peak_idx, _trough_idx = (
        calculate_max_drawdown(balance_history) if balance_history else (0, 0, 0)
    )
    calmar = calculate_calmar_ratio(returns, max_dd) if returns and max_dd > 0 else 0

    # Win rate metrics
    win_stats = calculate_win_rate(outcomes) if outcomes else {}

    # Risk measures
    var_95 = calculate_value_at_risk(returns, 0.95) if returns else 0
    expected_shortfall = calculate_expected_shortfall(returns, 0.95) if returns else 0

    # Profit metrics
    profit_factor = (
        calculate_profit_factor(gross_profit, gross_loss) if gross_profit and gross_loss else 0
    )

    # Kelly recommendation (using overall win rate and average odds)
    avg_win_rate = win_stats.get("win_rate", 0) / 100 if win_stats else 0
    # Estimate average odds from profit factor (simplified)
    estimated_avg_odds = 2.0  # Default assumption
    kelly_optimal = kelly_fraction(avg_win_rate, estimated_avg_odds) * 100

    return {
        "summary": {
            "initial_balance": initial_balance,
            "final_balance": final_balance,
            "net_profit": net_profit,
            "roi_percent": roi,
            "total_staked": total_staked,
            "number_of_bets": len(outcomes) if outcomes else 0,
        },
        "risk_metrics": {
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "calmar_ratio": calmar,
            "max_drawdown_percent": max_dd,
            "value_at_risk_95": var_95,
            "expected_shortfall_95": expected_shortfall,
            "volatility_percent": (statistics.stdev(returns) * 100 if len(returns) > 1 else 0),
        },
        "win_statistics": win_stats,
        "profit_metrics": {
            "profit_factor": profit_factor,
            "gross_profit": gross_profit,
            "gross_loss": gross_loss,
            "average_win": (
                gross_profit / win_stats.get("wins", 1) if win_stats.get("wins", 0) > 0 else 0
            ),
            "average_loss": (
                abs(gross_loss) / win_stats.get("losses", 1)
                if win_stats.get("losses", 0) > 0
                else 0
            ),
        },
        "recommendations": {
            "kelly_optimal_percent": kelly_optimal,
            "risk_assessment": _assess_risk_level(sharpe, max_dd, var_95),
            "strategy_rating": _rate_strategy(roi, sharpe, max_dd, win_stats.get("win_rate", 0)),
        },
    }


def _assess_risk_level(sharpe: float, max_drawdown: float, var_95: float) -> str:
    """Assess overall risk level of the strategy"""
    risk_score = 0

    # Sharpe ratio assessment
    if sharpe > 1.0:
        risk_score += 1
    elif sharpe > 0.5:
        risk_score += 0.5

    # Drawdown assessment
    if max_drawdown < 10:
        risk_score += 1
    elif max_drawdown < 20:
        risk_score += 0.5

    # VaR assessment
    if var_95 < 5:
        risk_score += 1
    elif var_95 < 10:
        risk_score += 0.5

    if risk_score >= 2.5:
        return "LOW"
    if risk_score >= 1.5:
        return "MODERATE"
    return "HIGH"


def _rate_strategy(roi: float, sharpe: float, max_drawdown: float, win_rate: float) -> str:
    """Rate the overall strategy quality"""
    score = 0

    # ROI assessment
    if roi > 20:
        score += 2
    elif roi > 10:
        score += 1
    elif roi > 0:
        score += 0.5

    # Sharpe assessment
    if sharpe > 1.5:
        score += 2
    elif sharpe > 1.0:
        score += 1
    elif sharpe > 0.5:
        score += 0.5

    # Drawdown penalty
    if max_drawdown > 30:
        score -= 1
    elif max_drawdown > 20:
        score -= 0.5

    # Win rate bonus
    if win_rate > 60:
        score += 1
    elif win_rate > 55:
        score += 0.5

    if score >= 4:
        return "EXCELLENT"
    if score >= 3:
        return "GOOD"
    if score >= 2:
        return "ACCEPTABLE"
    if score >= 1:
        return "POOR"
    return "UNACCEPTABLE"


if __name__ == "__main__":
    # Example usage
    sample_returns = [0.02, -0.01, 0.03, -0.005, 0.015, -0.02, 0.01]
    sample_balance = [1000, 1020, 1009.8, 1040.294, 1035.09, 1050.54, 1029.53, 1039.82]
    sample_outcomes = ["win", "loss", "win", "loss", "win", "loss", "win"]

    print("=== Performance Metrics Example ===")
    print(f"ROI: {calculate_roi(1000, 1039.82):.2f}%")
    print(f"Sharpe Ratio: {calculate_sharpe_ratio(sample_returns):.3f}")
    print(f"Max Drawdown: {calculate_max_drawdown(sample_balance)[0]:.2f}%")
    print(f"Win Rate: {calculate_win_rate(sample_outcomes)['win_rate']:.1f}%")
    print(f"Kelly Optimal: {kelly_fraction(0.6, 2.1) * 100:.1f}%")
