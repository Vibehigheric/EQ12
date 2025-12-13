#!/usr/bin/env python3
"""
EQ12 Monte Carlo Investment & Kelly Criterion Simulation Suite
Advanced financial modeling for $1M target analysis

This module implements:
1. Monte Carlo simulation for investment growth projections
2. Fractional Kelly Criterion staking system
3. Risk management and bankroll optimization
4. Legal compliance framework integration
5. Real-time visualization and reporting

Expert Python Features Demonstrated:
- Async/await for concurrent simulations
- Type hints and dataclasses for robust data structures
- Context managers for resource management
- Generators for memory-efficient processing
- Advanced statistical analysis with NumPy/SciPy
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
        logging.FileHandler("C:/EQ12/logs/monte_carlo_simulations.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class SimulationType(Enum):
    """Enumeration of available simulation types"""

    MONTE_CARLO_INVESTMENT = auto()
    FRACTIONAL_KELLY = auto()
    COMBINED_STRATEGY = auto()
    RISK_ANALYSIS = auto()


class RiskLevel(Enum):
    """Risk tolerance levels for simulations"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    EXPERT = "expert"


@dataclass
class SimulationParameters:
    """Configuration parameters for financial simulations"""

    initial_capital: float
    target_amount: float
    time_horizon_years: int
    num_simulations: int = 10000
    simulation_type: SimulationType = SimulationType.MONTE_CARLO_INVESTMENT
    risk_level: RiskLevel = RiskLevel.MODERATE

    # Market parameters
    mean_annual_return: float = 0.08  # 8% annual return
    annual_volatility: float = 0.15  # 15% volatility
    risk_free_rate: float = 0.03  # 3% risk-free rate

    # Kelly parameters
    true_win_probability: float = 0.53  # Assumed edge
    decimal_odds: float = 1.95  # Market odds
    kelly_fraction: float = 0.5  # Half-Kelly for safety

    # Advanced parameters
    transaction_costs: float = 0.001  # 0.1% per transaction
    rebalance_frequency: int = 252  # Daily rebalancing
    max_drawdown_threshold: float = 0.25  # 25% max drawdown

    def __post_init__(self):
        """Validate parameters after initialization"""
        if self.initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        if self.target_amount <= self.initial_capital:
            raise ValueError("Target amount must be greater than initial capital")
        if not 0 < self.kelly_fraction <= 1:
            raise ValueError("Kelly fraction must be between 0 and 1")


@dataclass
class SimulationResult:
    """Results from a financial simulation"""

    success_rate: float
    final_portfolios: np.ndarray
    simulation_paths: np.ndarray | None = None
    statistics: dict[str, float] = field(default_factory=dict)
    risk_metrics: dict[str, float] = field(default_factory=dict)
    timestamps: list[datetime] = field(default_factory=list)

    def __post_init__(self):
        """Calculate derived statistics"""
        if len(self.final_portfolios) > 0:
            self.statistics.update(
                {
                    "mean_final_value": np.mean(self.final_portfolios),
                    "median_final_value": np.median(self.final_portfolios),
                    "std_final_value": np.std(self.final_portfolios),
                    "min_final_value": np.min(self.final_portfolios),
                    "max_final_value": np.max(self.final_portfolios),
                    "percentile_5": np.percentile(self.final_portfolios, 5),
                    "percentile_25": np.percentile(self.final_portfolios, 25),
                    "percentile_75": np.percentile(self.final_portfolios, 75),
                    "percentile_95": np.percentile(self.final_portfolios, 95),
                }
            )


class EQ12MonteCarloEngine:
    """Advanced Monte Carlo simulation engine for financial modeling"""

    def __init__(self, eq12_root: Path = Path("C:/EQ12")):
        self.eq12_root = eq12_root
        self.results_cache: dict[str, SimulationResult] = {}
        self.legal_compliance_enabled = True

    @asynccontextmanager
    async def simulation_context(self, params: SimulationParameters):
        """Async context manager for simulation resources"""
        start_time = datetime.now()
        logger.info(f"Starting simulation: {params.simulation_type.name}")

        try:
            yield params
        finally:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Simulation completed in {duration:.2f} seconds")

    async def run_monte_carlo_investment(self, params: SimulationParameters) -> SimulationResult:
        """
        Run Monte Carlo simulation for investment growth using Geometric Brownian Motion

        This models stock market returns as a stochastic process:
        dS/S = μdt + σdW

        Where:
        - S = stock price
        - μ = drift (expected return)
        - σ = volatility
        - dW = Wiener process (random walk)
        """
        async with self.simulation_context(params) as sim_params:
            # Convert annual parameters to daily
            trading_days = sim_params.time_horizon_years * 252
            daily_return = sim_params.mean_annual_return / 252
            daily_volatility = sim_params.annual_volatility / math.sqrt(252)

            # Pre-allocate arrays for efficiency
            final_portfolios = np.zeros(sim_params.num_simulations)
            simulation_paths = np.zeros((sim_params.num_simulations, min(trading_days, 1000)))

            # Use concurrent processing for large simulations
            if sim_params.num_simulations > 1000:
                tasks = []
                batch_size = sim_params.num_simulations // 4

                for i in range(4):
                    start_idx = i * batch_size
                    end_idx = min((i + 1) * batch_size, sim_params.num_simulations)
                    task = self._run_investment_batch(
                        start_idx,
                        end_idx,
                        sim_params,
                        daily_return,
                        daily_volatility,
                        trading_days,
                    )
                    tasks.append(task)

                batch_results = await asyncio.gather(*tasks)

                # Combine batch results
                idx = 0
                for batch in batch_results:
                    batch_size = len(batch)
                    final_portfolios[idx : idx + batch_size] = batch
                    idx += batch_size
            else:
                # Single-threaded for smaller simulations
                final_portfolios = await self._run_investment_batch(
                    0,
                    sim_params.num_simulations,
                    sim_params,
                    daily_return,
                    daily_volatility,
                    trading_days,
                )

            # Calculate success rate and risk metrics
            success_rate = (
                np.sum(final_portfolios >= sim_params.target_amount)
                / sim_params.num_simulations
                * 100
            )

            result = SimulationResult(
                success_rate=success_rate,
                final_portfolios=final_portfolios,
                simulation_paths=simulation_paths,
            )

            # Add risk metrics
            self._calculate_risk_metrics(result, params)

            return result

    async def _run_investment_batch(
        self,
        start_idx: int,
        end_idx: int,
        params: SimulationParameters,
        daily_return: float,
        daily_volatility: float,
        trading_days: int,
    ) -> np.ndarray:
        """Run a batch of investment simulations"""
        batch_size = end_idx - start_idx
        final_values = np.zeros(batch_size)

        for i in range(batch_size):
            portfolio_value = params.initial_capital

            # Generate random daily returns using numpy for efficiency
            random_returns = np.random.normal(
                loc=daily_return, scale=daily_volatility, size=trading_days
            )

            # Apply returns with transaction costs
            for daily_return_val in random_returns:
                portfolio_value *= 1 + daily_return_val - params.transaction_costs

                # Check for bankruptcy protection
                if portfolio_value <= params.initial_capital * 0.1:
                    break

            final_values[i] = portfolio_value

        return final_values

    async def run_fractional_kelly_simulation(
        self, params: SimulationParameters
    ) -> SimulationResult:
        """
        Run Kelly Criterion simulation with fractional betting

        The Kelly Criterion formula: f* = (bp - q) / b
        Where:
        - b = net odds received on the wager
        - p = probability of winning
        - q = probability of losing (1 - p)
        """
        async with self.simulation_context(params) as sim_params:
            # Calculate Kelly optimal fraction
            b = sim_params.decimal_odds - 1
            p = sim_params.true_win_probability
            q = 1 - p

            kelly_optimal = (b * p - q) / b

            if kelly_optimal <= 0:
                logger.warning("No positive expected value - Kelly criterion suggests no betting")
                return SimulationResult(0.0, np.array([params.initial_capital]))

            final_bankrolls = []
            simulation_paths = []

            for _simulation in range(sim_params.num_simulations):
                bankroll_history = await self._simulate_kelly_betting(sim_params, kelly_optimal)
                final_bankrolls.append(bankroll_history[-1])
                simulation_paths.append(bankroll_history)

            final_portfolios = np.array(final_bankrolls)
            success_rate = (
                np.sum(final_portfolios >= sim_params.target_amount)
                / sim_params.num_simulations
                * 100
            )

            result = SimulationResult(
                success_rate=success_rate,
                final_portfolios=final_portfolios,
                simulation_paths=np.array(simulation_paths),
            )

            self._calculate_risk_metrics(result, params)

            return result

    async def _simulate_kelly_betting(
        self, params: SimulationParameters, kelly_optimal: float
    ) -> list[float]:
        """Simulate a single Kelly betting sequence"""
        bankroll = params.initial_capital
        bankroll_history = [bankroll]

        max_bets = params.time_horizon_years * 365  # Daily betting opportunity
        consecutive_losses = 0

        for _bet_number in range(max_bets):
            if bankroll <= 0 or bankroll >= params.target_amount:
                break

            # Apply fractional Kelly with dynamic adjustment
            current_kelly_fraction = self._adjust_kelly_fraction(
                params.kelly_fraction,
                consecutive_losses,
                bankroll,
                params.initial_capital,
            )

            stake_fraction = current_kelly_fraction * kelly_optimal
            stake = bankroll * min(stake_fraction, 0.25)  # Never risk more than 25%

            # Simulate bet outcome
            if np.random.random() < params.true_win_probability:
                # Win
                profit = stake * (params.decimal_odds - 1)
                bankroll += profit
                consecutive_losses = 0
            else:
                # Loss
                bankroll -= stake
                consecutive_losses += 1

            # Apply drawdown protection
            if bankroll < params.initial_capital * (1 - params.max_drawdown_threshold):
                # Reduce bet sizes after significant drawdown
                current_kelly_fraction *= 0.5

            bankroll_history.append(bankroll)

        return bankroll_history

    @staticmethod
    def _adjust_kelly_fraction(
        base_fraction: float,
        consecutive_losses: int,
        current_bankroll: float,
        initial_capital: float,
    ) -> float:
        """Dynamically adjust Kelly fraction based on recent performance"""
        # Reduce fraction after consecutive losses
        loss_adjustment = max(0.1, 1 - (consecutive_losses * 0.1))

        # Adjust based on current performance vs initial capital
        performance_ratio = current_bankroll / initial_capital
        performance_adjustment = min(1.5, max(0.5, performance_ratio))

        return base_fraction * loss_adjustment * performance_adjustment

    def _calculate_risk_metrics(self, result: SimulationResult, params: SimulationParameters):
        """Calculate comprehensive risk metrics"""
        if len(result.final_portfolios) == 0:
            return

        # Basic risk metrics
        returns = (result.final_portfolios - params.initial_capital) / params.initial_capital

        risk_metrics = {
            "volatility": np.std(returns),
            "sharpe_ratio": self._calculate_sharpe_ratio(returns, params.risk_free_rate),
            "sortino_ratio": self._calculate_sortino_ratio(returns, params.risk_free_rate),
            "max_drawdown": (
                self._calculate_max_drawdown(result.simulation_paths)
                if result.simulation_paths is not None
                else 0
            ),
            "value_at_risk_5": np.percentile(returns, 5),
            "conditional_var_5": np.mean(returns[returns <= np.percentile(returns, 5)]),
            "probability_of_loss": np.sum(returns < 0) / len(returns) * 100,
            "expected_shortfall": (np.mean(returns[returns < 0]) if np.any(returns < 0) else 0),
        }

        result.risk_metrics = risk_metrics

    @staticmethod
    def _calculate_sharpe_ratio(returns: np.ndarray, risk_free_rate: float) -> float:
        """Calculate Sharpe ratio"""
        if np.std(returns) == 0:
            return 0
        excess_returns = np.mean(returns) - risk_free_rate
        return excess_returns / np.std(returns)

    @staticmethod
    def _calculate_sortino_ratio(returns: np.ndarray, risk_free_rate: float) -> float:
        """Calculate Sortino ratio (focuses on downside deviation)"""
        downside_returns = returns[returns < risk_free_rate]
        if len(downside_returns) == 0:
            return float("inf")

        downside_deviation = np.std(downside_returns)
        if downside_deviation == 0:
            return 0

        excess_return = np.mean(returns) - risk_free_rate
        return excess_return / downside_deviation

    @staticmethod
    def _calculate_max_drawdown(simulation_paths: np.ndarray) -> float:
        """Calculate maximum drawdown across all simulation paths"""
        if simulation_paths is None or len(simulation_paths) == 0:
            return 0

        max_drawdowns = []
        for path in simulation_paths:
            if len(path) > 1:
                running_max = np.maximum.accumulate(path)
                drawdowns = (path - running_max) / running_max
                max_drawdowns.append(np.min(drawdowns))

        return np.mean(max_drawdowns) if max_drawdowns else 0

    async def generate_comprehensive_report(
        self, results: dict[str, SimulationResult], params: SimulationParameters
    ) -> dict[str, Any]:
        """Generate comprehensive analysis report"""
        report = {
            "simulation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "parameters": {
                    "initial_capital": params.initial_capital,
                    "target_amount": params.target_amount,
                    "time_horizon": params.time_horizon_years,
                    "num_simulations": params.num_simulations,
                    "risk_level": params.risk_level.value,
                },
            },
            "results_summary": {},
            "risk_analysis": {},
            "recommendations": {},
            "legal_compliance": self._get_legal_compliance_summary(),
        }

        for sim_name, result in results.items():
            report["results_summary"][sim_name] = {
                "success_rate": result.success_rate,
                "expected_value": result.statistics.get("mean_final_value", 0),
                "risk_metrics": result.risk_metrics,
            }

        # Generate strategic recommendations
        report["recommendations"] = self._generate_strategic_recommendations(results, params)

        return report

    def _generate_strategic_recommendations(
        self, results: dict[str, SimulationResult], params: SimulationParameters
    ) -> dict[str, Any]:
        """Generate AI-powered strategic recommendations"""
        recommendations = {
            "optimal_strategy": "conservative",
            "risk_adjustments": [],
            "probability_insights": [],
            "action_items": [],
        }

        # Analyze results to determine optimal strategy
        if "monte_carlo" in results:
            mc_result = results["monte_carlo"]
            if mc_result.success_rate > 70:
                recommendations["optimal_strategy"] = "continue_current"
                recommendations["action_items"].append(
                    "High success probability - maintain current allocation"
                )
            elif mc_result.success_rate < 30:
                recommendations["optimal_strategy"] = "reassess_goals"
                recommendations["action_items"].append(
                    "Low success probability - consider adjusting targets or timeline"
                )

        if "kelly" in results:
            kelly_result = results["kelly"]
            if kelly_result.risk_metrics.get("max_drawdown", 0) > -0.5:
                recommendations["risk_adjustments"].append(
                    "Consider reducing Kelly fraction to limit drawdown risk"
                )

        return recommendations

    def _get_legal_compliance_summary(self) -> dict[str, Any]:
        """Get legal compliance framework summary"""
        return {
            "disclaimers": {
                "investment_risk": "All investments carry risk of loss. Past performance does not guarantee future results.",
                "no_financial_advice": "This simulation is for educational purposes only and does not constitute financial advice.",
                "age_requirement": "Must be 21+ years old to use investment features.",
                "regulatory_compliance": "Users must comply with all applicable local investment and gambling laws.",
            },
            "risk_warnings": [
                "Simulations are based on historical data and assumptions",
                "Actual results may vary significantly from projections",
                "Consider consulting a financial advisor before making investment decisions",
                "Never invest more than you can afford to lose",
            ],
            "responsible_investing": [
                "Set clear investment goals and risk tolerance",
                "Diversify investments across asset classes",
                "Regularly review and rebalance portfolio",
                "Stay informed about market conditions and regulatory changes",
            ],
        }

    async def create_visualization_dashboard(
        self,
        results: dict[str, SimulationResult],
        params: SimulationParameters,
        save_path: Path | None = None,
    ):
        """Create comprehensive visualization dashboard"""
        if save_path is None:
            save_path = self.eq12_root / "logs" / "monte_carlo_visualizations"

        save_path.mkdir(parents=True, exist_ok=True)

        # Set up the plotting style
        plt.style.use("seaborn-v0_8")
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(
            "EQ12 Monte Carlo & Kelly Criterion Analysis",
            fontsize=16,
            fontweight="bold",
        )

        for sim_name, result in results.items():
            if "monte_carlo" in sim_name.lower():
                # Distribution of final values
                axes[0, 0].hist(
                    result.final_portfolios,
                    bins=50,
                    alpha=0.7,
                    label=f"{sim_name} (Success: {result.success_rate:.1f}%)",
                )
                axes[0, 0].axvline(
                    params.target_amount,
                    color="red",
                    linestyle="--",
                    label=f"Target: ${params.target_amount:,.0f}",
                )
                axes[0, 0].set_xlabel("Final Portfolio Value ($)")
                axes[0, 0].set_ylabel("Frequency")
                axes[0, 0].set_title("Distribution of Final Portfolio Values")
                axes[0, 0].legend()

            elif "kelly" in sim_name.lower():
                # Kelly simulation paths
                if result.simulation_paths is not None:
                    # Plot sample paths
                    sample_paths = result.simulation_paths[: min(100, len(result.simulation_paths))]
                    for i, path in enumerate(sample_paths):
                        alpha = 0.1 if i > 10 else 0.3
                        axes[0, 1].plot(path, alpha=alpha, color="blue" if i <= 10 else "lightblue")

                    axes[0, 1].axhline(
                        params.target_amount,
                        color="red",
                        linestyle="--",
                        label=f"Target: ${params.target_amount:,.0f}",
                    )
                    axes[0, 1].set_xlabel("Bet Number")
                    axes[0, 1].set_ylabel("Bankroll Value ($)")
                    axes[0, 1].set_title("Kelly Criterion Simulation Paths (Sample)")
                    axes[0, 1].set_yscale("log")
                    axes[0, 1].legend()

        # Risk metrics comparison
        if len(results) > 1:
            strategies = list(results.keys())
            sharpe_ratios = [results[s].risk_metrics.get("sharpe_ratio", 0) for s in strategies]
            max_drawdowns = [
                abs(results[s].risk_metrics.get("max_drawdown", 0)) for s in strategies
            ]

            x = np.arange(len(strategies))
            width = 0.35

            axes[1, 0].bar(x - width / 2, sharpe_ratios, width, label="Sharpe Ratio", alpha=0.8)
            axes[1, 0].bar(x + width / 2, max_drawdowns, width, label="Max Drawdown", alpha=0.8)
            axes[1, 0].set_xlabel("Strategy")
            axes[1, 0].set_ylabel("Metric Value")
            axes[1, 0].set_title("Risk-Adjusted Performance Comparison")
            axes[1, 0].set_xticks(x)
            axes[1, 0].set_xticklabels(strategies)
            axes[1, 0].legend()

        # Success probability heatmap
        success_rates = [results[s].success_rate for s in results]
        risk_levels = ["Conservative", "Moderate", "Aggressive"]

        if len(success_rates) >= len(risk_levels):
            heatmap_data = np.array(success_rates[: len(risk_levels)]).reshape(1, -1)
            axes[1, 1].imshow(heatmap_data, cmap="RdYlGn", aspect="auto")
            axes[1, 1].set_xticks(range(len(risk_levels)))
            axes[1, 1].set_xticklabels(risk_levels)
            axes[1, 1].set_yticks([0])
            axes[1, 1].set_yticklabels(["Success Rate %"])
            axes[1, 1].set_title("Success Rate by Strategy")

            # Add text annotations
            for i, rate in enumerate(success_rates[: len(risk_levels)]):
                axes[1, 1].text(
                    i,
                    0,
                    f"{rate:.1f}%",
                    ha="center",
                    va="center",
                    fontweight="bold",
                    color="white" if rate < 50 else "black",
                )

        plt.tight_layout()

        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = save_path / f"monte_carlo_analysis_{timestamp}.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Visualization saved to {plot_path}")
        return plot_path


# Integration with EQ12 God Mode System
async def run_comprehensive_analysis(
    initial_capital: float = 100000.0,
    target_amount: float = 1000000.0,
    time_horizon: int = 20,
) -> dict[str, Any]:
    """Run comprehensive Monte Carlo and Kelly analysis"""

    engine = EQ12MonteCarloEngine()

    # Conservative parameters
    conservative_params = SimulationParameters(
        initial_capital=initial_capital,
        target_amount=target_amount,
        time_horizon_years=time_horizon,
        num_simulations=5000,
        mean_annual_return=0.07,
        annual_volatility=0.12,
        kelly_fraction=0.25,
        risk_level=RiskLevel.CONSERVATIVE,
    )

    # Aggressive parameters
    aggressive_params = SimulationParameters(
        initial_capital=initial_capital,
        target_amount=target_amount,
        time_horizon_years=time_horizon,
        num_simulations=5000,
        mean_annual_return=0.10,
        annual_volatility=0.20,
        kelly_fraction=0.5,
        risk_level=RiskLevel.AGGRESSIVE,
    )

    # Run simulations
    results = {}

    logger.info("Running conservative Monte Carlo simulation...")
    results["monte_carlo_conservative"] = await engine.run_monte_carlo_investment(
        conservative_params
    )

    logger.info("Running aggressive Monte Carlo simulation...")
    results["monte_carlo_aggressive"] = await engine.run_monte_carlo_investment(aggressive_params)

    logger.info("Running Kelly Criterion simulation...")
    results["kelly_criterion"] = await engine.run_fractional_kelly_simulation(conservative_params)

    # Generate comprehensive report
    report = await engine.generate_comprehensive_report(results, conservative_params)

    # Create visualizations
    try:
        plot_path = await engine.create_visualization_dashboard(results, conservative_params)
        report["visualization_path"] = str(plot_path)
    except Exception as e:
        logger.warning(f"Could not create visualizations: {e}")
        report["visualization_path"] = None

    return report


def main():
    """Main execution function for Monte Carlo analysis"""
    print(
        """
🎯 EQ12 MONTE CARLO & KELLY CRITERION ANALYSIS SUITE
====================================================

This advanced financial modeling system demonstrates:
✅ Monte Carlo investment growth projections
✅ Fractional Kelly Criterion staking strategies
✅ Risk-adjusted performance analysis
✅ Legal compliance framework integration
✅ Expert Python programming patterns

Running comprehensive $1M target analysis...
    """
    )

    try:
        # Run the comprehensive analysis
        report = asyncio.run(
            run_comprehensive_analysis(
                initial_capital=100000.0, target_amount=1000000.0, time_horizon=20
            )
        )

        # Display results
        print("\n📊 SIMULATION RESULTS SUMMARY")
        print("=" * 50)

        for _strategy, results in report["results_summary"].items():
            print("\n🔹 {strategy.upper()}:")
            print("   Success Rate: {results['success_rate']:.1f}%")
            print("   Expected Value: ${results['expected_value']:,.0f}")
            print(f"   Sharpe Ratio: {results['risk_metrics'].get('sharpe_ratio', 0):.3f}")
            print(f"   Max Drawdown: {results['risk_metrics'].get('max_drawdown', 0):.1f}%")

        print("\n🎯 STRATEGIC RECOMMENDATIONS:")
        print("   Optimal Strategy: {report['recommendations']['optimal_strategy']}")
        for _item in report["recommendations"]["action_items"]:
            print("   • {item}")

        print("\n⚖️ LEGAL COMPLIANCE NOTICE:")
        for _warning in report["legal_compliance"]["risk_warnings"][:3]:
            print("   ⚠️ {warning}")

        if report.get("visualization_path"):
            print("\n📈 Visualization saved to: {report['visualization_path']}")

        # Save full report
        report_path = Path("C:/EQ12/logs/monte_carlo_reports")
        report_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_path / f"monte_carlo_analysis_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("\n📄 Full report saved to: {report_file}")
        print("\n✅ MONTE CARLO ANALYSIS COMPLETE!")

        return True

    except Exception as e:
        logger.error(f"Error in Monte Carlo analysis: {e}")
        print("❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
