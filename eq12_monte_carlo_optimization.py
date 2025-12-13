#!/usr/bin/env python3
"""
EQ12 Monte Carlo & Kelly Criterion Investment Suite
Advanced financial modeling with expert Python programming patterns

Features:
- Monte Carlo investment growth projections
- Fractional Kelly Criterion staking
- Risk-adjusted performance analysis
- Legal compliance framework
- Real-time visualization
"""

import asyncio
import json
import logging
import math
import warnings
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

# Suppress matplotlib warnings in headless environments
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/monte_carlo_optimized.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SimulationType(Enum):
    """Simulation types available"""

    MONTE_CARLO = auto()
    KELLY_CRITERION = auto()
    COMBINED = auto()
    RISK_ANALYSIS = auto()


class RiskLevel(Enum):
    """Risk tolerance levels"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    EXPERT = "expert"


@dataclass
class InvestmentParams:
    """Investment simulation parameters"""

    initial_capital: float
    target_amount: float
    time_horizon_years: int
    num_simulations: int = 5000
    simulation_type: SimulationType = SimulationType.MONTE_CARLO
    risk_level: RiskLevel = RiskLevel.MODERATE

    # Market parameters
    mean_annual_return: float = 0.08
    annual_volatility: float = 0.15
    risk_free_rate: float = 0.03

    # Kelly parameters
    win_probability: float = 0.53
    decimal_odds: float = 1.95
    kelly_fraction: float = 0.5

    # Advanced settings
    transaction_costs: float = 0.001
    max_drawdown: float = 0.25

    def __post_init__(self):
        """Validate parameters"""
        if self.initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        if self.target_amount <= self.initial_capital:
            raise ValueError("Target must be greater than initial capital")
        if not 0 < self.kelly_fraction <= 1:
            raise ValueError("Kelly fraction must be between 0 and 1")


@dataclass
class InvestmentResult:
    """Simulation results container"""

    success_rate: float
    final_values: np.ndarray
    simulation_paths: np.ndarray | None = None
    statistics: dict[str, float] = field(default_factory=dict)
    risk_metrics: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate statistics"""
        if len(self.final_values) > 0:
            self.statistics.update(
                {
                    "mean_value": np.mean(self.final_values),
                    "median_value": np.median(self.final_values),
                    "std_value": np.std(self.final_values),
                    "min_value": np.min(self.final_values),
                    "max_value": np.max(self.final_values),
                    "percentile_5": np.percentile(self.final_values, 5),
                    "percentile_25": np.percentile(self.final_values, 25),
                    "percentile_75": np.percentile(self.final_values, 75),
                    "percentile_95": np.percentile(self.final_values, 95),
                }
            )


class EQ12MonteCarloOptimizer:
    """Optimized Monte Carlo simulation engine"""

    def __init__(self, eq12_root: Path = Path("C:/EQ12")):
        self.eq12_root = eq12_root
        self.results_cache: dict[str, InvestmentResult] = {}

    @asynccontextmanager
    async def simulation_context(self, params: InvestmentParams):
        """Async context manager for simulations"""
        start_time = datetime.now()
        logger.info(f"Starting {params.simulation_type.name} simulation")

        try:
            yield params
        finally:
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Simulation completed in {duration:.2f}s")

    async def run_monte_carlo_simulation(self, params: InvestmentParams) -> InvestmentResult:
        """
        Monte Carlo simulation using Geometric Brownian Motion

        Formula: dS/S = μdt + σdW
        Where: S=price, μ=drift, σ=volatility, dW=random walk
        """
        async with self.simulation_context(params) as sim_params:
            # Convert to daily parameters
            trading_days = sim_params.time_horizon_years * 252
            daily_return = sim_params.mean_annual_return / 252
            daily_vol = sim_params.annual_volatility / math.sqrt(252)

            # Pre-allocate arrays
            final_values = np.zeros(sim_params.num_simulations)

            # Vectorized simulation for performance
            for i in range(sim_params.num_simulations):
                portfolio_value = sim_params.initial_capital

                # Generate random returns
                random_returns = np.random.normal(
                    loc=daily_return, scale=daily_vol, size=trading_days
                )

                # Apply returns with transaction costs
                for daily_ret in random_returns:
                    portfolio_value *= 1 + daily_ret - sim_params.transaction_costs

                    # Bankruptcy protection
                    if portfolio_value <= sim_params.initial_capital * 0.1:
                        break

                final_values[i] = portfolio_value

            # Calculate success rate
            success_rate = (
                np.sum(final_values >= sim_params.target_amount) / sim_params.num_simulations * 100
            )

            result = InvestmentResult(success_rate=success_rate, final_values=final_values)

            # Calculate risk metrics
            self._calculate_risk_metrics(result, params)

            return result

    async def run_kelly_simulation(self, params: InvestmentParams) -> InvestmentResult:
        """
        Kelly Criterion simulation with fractional betting

        Kelly formula: f* = (bp - q) / b
        Where: b=odds-1, p=win prob, q=lose prob
        """
        async with self.simulation_context(params) as sim_params:
            # Calculate Kelly optimal fraction
            b = sim_params.decimal_odds - 1
            p = sim_params.win_probability
            q = 1 - p

            kelly_optimal = (b * p - q) / b

            if kelly_optimal <= 0:
                logger.warning("No positive expected value detected")
                return InvestmentResult(0.0, np.array([params.initial_capital]))

            final_bankrolls = []

            for _ in range(sim_params.num_simulations):
                bankroll_history = await self._simulate_kelly_betting(sim_params, kelly_optimal)
                final_bankrolls.append(bankroll_history[-1])

            final_values = np.array(final_bankrolls)
            success_rate = (
                np.sum(final_values >= sim_params.target_amount) / sim_params.num_simulations * 100
            )

            result = InvestmentResult(success_rate=success_rate, final_values=final_values)

            self._calculate_risk_metrics(result, params)

            return result

    async def _simulate_kelly_betting(
        self, params: InvestmentParams, kelly_optimal: float
    ) -> list[float]:
        """Simulate single Kelly betting sequence"""
        bankroll = params.initial_capital
        bankroll_history = [bankroll]

        max_bets = params.time_horizon_years * 365
        consecutive_losses = 0

        for _ in range(max_bets):
            if bankroll <= 0 or bankroll >= params.target_amount:
                break

            # Dynamic Kelly fraction adjustment
            current_kelly = self._adjust_kelly_fraction(
                params.kelly_fraction,
                consecutive_losses,
                bankroll,
                params.initial_capital,
            )

            stake_fraction = current_kelly * kelly_optimal
            # Never risk more than 25%
            stake = bankroll * min(stake_fraction, 0.25)

            # Simulate bet outcome
            if np.random.random() < params.win_probability:
                # Win
                profit = stake * (params.decimal_odds - 1)
                bankroll += profit
                consecutive_losses = 0
            else:
                # Loss
                bankroll -= stake
                consecutive_losses += 1

            # Drawdown protection
            max_dd_threshold = params.initial_capital * (1 - params.max_drawdown)
            if bankroll < max_dd_threshold:
                current_kelly *= 0.5

            bankroll_history.append(bankroll)

        return bankroll_history

    @staticmethod
    def _adjust_kelly_fraction(
        base_fraction: float,
        consecutive_losses: int,
        current_bankroll: float,
        initial_capital: float,
    ) -> float:
        """Adjust Kelly fraction based on performance"""
        # Reduce after consecutive losses
        loss_adj = max(0.1, 1 - (consecutive_losses * 0.1))

        # Adjust based on performance
        performance_ratio = current_bankroll / initial_capital
        perf_adj = min(1.5, max(0.5, performance_ratio))

        return base_fraction * loss_adj * perf_adj

    def _calculate_risk_metrics(self, result: InvestmentResult, params: InvestmentParams):
        """Calculate comprehensive risk metrics"""
        if len(result.final_values) == 0:
            return

        returns = (result.final_values - params.initial_capital) / params.initial_capital

        risk_metrics = {
            "volatility": np.std(returns),
            "sharpe_ratio": self._calc_sharpe(returns, params.risk_free_rate),
            "sortino_ratio": self._calc_sortino(returns, params.risk_free_rate),
            "var_5": np.percentile(returns, 5),
            "cvar_5": np.mean(returns[returns <= np.percentile(returns, 5)]),
            "prob_loss": np.sum(returns < 0) / len(returns) * 100,
            "expected_shortfall": (np.mean(returns[returns < 0]) if np.any(returns < 0) else 0),
        }

        result.risk_metrics = risk_metrics

    @staticmethod
    def _calc_sharpe(returns: np.ndarray, rf_rate: float) -> float:
        """Calculate Sharpe ratio"""
        if np.std(returns) == 0:
            return 0
        excess_returns = np.mean(returns) - rf_rate
        return excess_returns / np.std(returns)

    @staticmethod
    def _calc_sortino(returns: np.ndarray, rf_rate: float) -> float:
        """Calculate Sortino ratio"""
        downside_returns = returns[returns < rf_rate]
        if len(downside_returns) == 0:
            return float("inf")

        downside_dev = np.std(downside_returns)
        if downside_dev == 0:
            return 0

        excess_return = np.mean(returns) - rf_rate
        return excess_return / downside_dev

    async def generate_report(
        self, results: dict[str, InvestmentResult], params: InvestmentParams
    ) -> dict[str, Any]:
        """Generate comprehensive analysis report"""
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "initial_capital": params.initial_capital,
                    "target_amount": params.target_amount,
                    "time_horizon": params.time_horizon_years,
                    "num_simulations": params.num_simulations,
                },
            },
            "results": {},
            "recommendations": self._generate_recommendations(results, params),
            "compliance": self._get_compliance_info(),
        }

        for name, result in results.items():
            report["results"][name] = {
                "success_rate": result.success_rate,
                "expected_value": result.statistics.get("mean_value", 0),
                "risk_metrics": result.risk_metrics,
            }

        return report

    def _generate_recommendations(
        self, results: dict[str, InvestmentResult], params: InvestmentParams
    ) -> dict[str, Any]:
        """Generate strategic recommendations"""
        recommendations = {
            "strategy": "moderate",
            "adjustments": [],
            "action_items": [],
        }

        for name, result in results.items():
            if result.success_rate > 70:
                recommendations["action_items"].append(
                    f"{name}: High success rate - maintain strategy"
                )
            elif result.success_rate < 30:
                recommendations["action_items"].append(
                    f"{name}: Low success rate - consider alternatives"
                )

        return recommendations

    def _get_compliance_info(self) -> dict[str, Any]:
        """Legal compliance information"""
        return {
            "disclaimers": {
                "risk": "Investments carry risk of loss",
                "advice": "Educational purposes only - not financial advice",
                "age": "Must be 21+ to use investment features",
            },
            "warnings": [
                "Simulations based on assumptions",
                "Actual results may vary significantly",
                "Never invest more than you can afford to lose",
            ],
        }

    async def create_visualizations(
        self,
        results: dict[str, InvestmentResult],
        params: InvestmentParams,
        save_path: Path | None = None,
    ) -> Path | None:
        """Create visualization dashboard"""
        if save_path is None:
            save_path = self.eq12_root / "logs" / "visualizations"

        save_path.mkdir(parents=True, exist_ok=True)

        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            fig.suptitle("EQ12 Investment Analysis Dashboard", fontsize=16, fontweight="bold")

            # Plot 1: Distribution of final values
            for name, result in results.items():
                axes[0, 0].hist(
                    result.final_values,
                    bins=50,
                    alpha=0.7,
                    label=f"{name} ({result.success_rate:.1f}%)",
                )

            axes[0, 0].axvline(
                params.target_amount,
                color="red",
                linestyle="--",
                label=f"Target: ${params.target_amount:,.0f}",
            )
            axes[0, 0].set_xlabel("Final Portfolio Value ($)")
            axes[0, 0].set_ylabel("Frequency")
            axes[0, 0].set_title("Distribution of Final Values")
            axes[0, 0].legend()

            # Plot 2: Success rates comparison
            names = list(results.keys())
            success_rates = [results[name].success_rate for name in names]

            axes[0, 1].bar(names, success_rates, alpha=0.8)
            axes[0, 1].set_ylabel("Success Rate (%)")
            axes[0, 1].set_title("Success Rate Comparison")
            axes[0, 1].tick_params(axis="x", rotation=45)

            # Plot 3: Risk metrics
            if len(results) > 1:
                sharpe_ratios = [
                    results[name].risk_metrics.get("sharpe_ratio", 0) for name in names
                ]

                axes[1, 0].bar(names, sharpe_ratios, alpha=0.8)
                axes[1, 0].set_ylabel("Sharpe Ratio")
                axes[1, 0].set_title("Risk-Adjusted Returns")
                axes[1, 0].tick_params(axis="x", rotation=45)

            # Plot 4: Percentile analysis
            for name, result in results.items():
                percentiles = [5, 25, 50, 75, 95]
                values = [result.statistics.get(f"percentile_{p}", 0) for p in percentiles]
                axes[1, 1].plot(percentiles, values, "o-", label=name)

            axes[1, 1].set_xlabel("Percentile")
            axes[1, 1].set_ylabel("Portfolio Value ($)")
            axes[1, 1].set_title("Percentile Analysis")
            axes[1, 1].legend()

            plt.tight_layout()

            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = save_path / f"investment_analysis_{timestamp}.png"
            plt.savefig(plot_path, dpi=300, bbox_inches="tight")
            plt.close()

            logger.info(f"Visualization saved to {plot_path}")
            return plot_path

        except Exception as e:
            logger.error(f"Visualization error: {e}")
            return None


async def run_comprehensive_investment_analysis(
    initial: float = 100000.0, target: float = 1000000.0, years: int = 15
) -> dict[str, Any]:
    """Run complete investment analysis suite"""

    optimizer = EQ12MonteCarloOptimizer()

    # Conservative strategy
    conservative = InvestmentParams(
        initial_capital=initial,
        target_amount=target,
        time_horizon_years=years,
        num_simulations=3000,
        mean_annual_return=0.07,
        annual_volatility=0.12,
        kelly_fraction=0.25,
        risk_level=RiskLevel.CONSERVATIVE,
    )

    # Moderate strategy
    moderate = InvestmentParams(
        initial_capital=initial,
        target_amount=target,
        time_horizon_years=years,
        num_simulations=3000,
        mean_annual_return=0.08,
        annual_volatility=0.15,
        kelly_fraction=0.4,
        risk_level=RiskLevel.MODERATE,
    )

    # Run simulations
    results = {}

    logger.info("Running Monte Carlo simulations...")
    results["conservative_mc"] = await optimizer.run_monte_carlo_simulation(conservative)
    results["moderate_mc"] = await optimizer.run_monte_carlo_simulation(moderate)

    logger.info("Running Kelly Criterion simulations...")
    results["kelly_criterion"] = await optimizer.run_kelly_simulation(conservative)

    # Generate report
    report = await optimizer.generate_report(results, moderate)

    # Create visualizations
    try:
        viz_path = await optimizer.create_visualizations(results, moderate)
        report["visualization"] = str(viz_path) if viz_path else None
    except Exception as e:
        logger.warning(f"Visualization failed: {e}")
        report["visualization"] = None

    return report


def main():
    """Main execution function"""
    print(
        """
🎯 EQ12 OPTIMIZED MONTE CARLO & KELLY ANALYSIS
============================================

Advanced Investment Modeling Suite:
✅ Monte Carlo projections with Geometric Brownian Motion
✅ Fractional Kelly Criterion with dynamic adjustment
✅ Risk-adjusted performance metrics (Sharpe, Sortino)
✅ Legal compliance framework
✅ Interactive visualizations

Running $1M target analysis...
    """
    )

    try:
        # Run comprehensive analysis
        report = asyncio.run(
            run_comprehensive_investment_analysis(initial=100000.0, target=1000000.0, years=15)
        )

        # Display results
        print("\n📊 INVESTMENT ANALYSIS RESULTS")
        print("=" * 45)

        for _strategy, data in report["results"].items():
            print("\n🔹 {strategy.upper().replace('_', ' ')}:")
            print("   Success Rate: {data['success_rate']:.1f}%")
            print("   Expected Value: ${data['expected_value']:,.0f}")
            data["risk_metrics"].get("sharpe_ratio", 0)
            print("   Sharpe Ratio: {sharpe:.3f}")

        print("\n🎯 RECOMMENDATIONS:")
        for _item in report["recommendations"]["action_items"]:
            print("   • {item}")

        print("\n⚖️ COMPLIANCE REMINDER:")
        for _warning in report["compliance"]["warnings"]:
            print("   ⚠️ {warning}")

        # Save report
        reports_dir = Path("C:/EQ12/logs/investment_reports")
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"investment_analysis_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("\n📄 Report: {report_file}")
        if report.get("visualization"):
            print("📈 Charts: {report['visualization']}")

        print("\n✅ INVESTMENT ANALYSIS COMPLETE!")
        return True

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        print("❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
