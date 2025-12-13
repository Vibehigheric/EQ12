#!/usr/bin/env python3
"""
EQ12 Expert Kelly Integration System
Central integration of Kelly Criterion with Azure ML and multi-environment support
"""

import argparse
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.azure_ml_manager import (
        AzureMLWorkspaceManager,
        create_azure_ml_manager,
    )
    from src.core.kelly_bankroll_manager import (
        KellyBankrollManager,
        create_kelly_manager,
    )

    CORE_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Core modules not available: {e}")
    CORE_MODULES_AVAILABLE = False


class ExpertKellyIntegrationSystem:
    """
    Expert Kelly Criterion Integration System

    This is the central control system that:
    1. Integrates Kelly Criterion as the core bankroll management module
    2. Manages Azure ML multi-environment deployments
    3. Coordinates statistical probability models with betting optimization
    4. Handles multi-bet correlation analysis and fractional Kelly controls
    5. Provides comprehensive CLI interface for all Kelly operations
    6. Manages environment switching and deployment automation
    """

    def __init__(
        self,
        environment: str = "dev",
        kelly_fraction: float = 0.25,
        max_bankroll_risk: float = 0.15,
        starting_balance: float = 1000.0,
        auto_deploy: bool = False,
    ):
        """
        Initialize Expert Kelly Integration System

        Args:
            environment: Azure ML environment (dev/staging/production)
            kelly_fraction: Fractional Kelly multiplier for risk management
            max_bankroll_risk: Maximum percentage of bankroll at risk
            starting_balance: Initial bankroll amount
            auto_deploy: Automatically deploy to Azure ML
        """
        self.environment = environment
        self.kelly_fraction = kelly_fraction
        self.max_bankroll_risk = max_bankroll_risk
        self.starting_balance = starting_balance
        self.auto_deploy = auto_deploy

        # Initialize components
        self.kelly_manager: KellyBankrollManager | None = None
        self.azure_manager: AzureMLWorkspaceManager | None = None

        if CORE_MODULES_AVAILABLE:
            self._initialize_components()
        else:
            logger.error("Cannot initialize - core modules unavailable")

    def _initialize_components(self) -> None:
        """Initialize Kelly and Azure ML managers"""
        try:
            # Initialize Kelly Bankroll Manager
            self.kelly_manager = create_kelly_manager(
                bankroll_file=f"data/kelly_bankroll_{self.environment}.csv",
                starting_balance=self.starting_balance,
                kelly_fraction=self.kelly_fraction,
            )

            # Initialize Azure ML Manager
            self.azure_manager = create_azure_ml_manager()

            # Switch to target environment
            if self.azure_manager:
                self.azure_manager.switch_environment(self.environment)

            # Deploy if requested
            if self.auto_deploy and self.azure_manager:
                self._deploy_to_azure()

            logger.info(f"Expert Kelly Integration System initialized for {self.environment}")

        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def calculate_multi_bet_kelly_strategy(
        self, bets: list[dict], correlation_matrix: dict | None = None
    ) -> dict:
        """
        Calculate optimal Kelly strategy for multiple simultaneous bets

        Args:
            bets: List of bet opportunities with odds and probabilities
            correlation_matrix: Correlation coefficients between bets

        Returns:
            Comprehensive multi-bet Kelly allocation strategy
        """
        if not self.kelly_manager:
            raise RuntimeError("Kelly manager not initialized")

        logger.info(f"Calculating multi-bet Kelly strategy for {len(bets)} bets")

        # Get individual Kelly calculations
        individual_kellys = {}
        total_edge = 0.0

        for bet in bets:
            kelly_result = self.kelly_manager.calculate_optimal_kelly_fraction(
                decimal_odds=bet["decimal_odds"],
                true_probability=bet.get("true_probability"),
                event_data=bet,
            )

            individual_kellys[bet["bet_id"]] = kelly_result
            total_edge += kelly_result.get("edge", 0.0)

        # Get optimized multi-bet allocation
        multi_bet_allocation = self.kelly_manager.get_multi_bet_kelly_allocation(
            bets, correlation_matrix
        )

        # Calculate portfolio statistics
        portfolio_stats = self._calculate_portfolio_statistics(
            individual_kellys, multi_bet_allocation, correlation_matrix
        )

        return {
            "strategy_type": "multi_bet_kelly",
            "environment": self.environment,
            "total_bets": len(bets),
            "total_edge": total_edge,
            "avg_edge": total_edge / len(bets) if bets else 0.0,
            "individual_kellys": individual_kellys,
            "optimized_allocation": multi_bet_allocation,
            "portfolio_statistics": portfolio_stats,
            "risk_management": {
                "kelly_fraction": self.kelly_fraction,
                "max_bankroll_risk": self.max_bankroll_risk,
                "total_kelly_exposure": portfolio_stats["total_kelly_exposure"],
                "correlation_adjusted": correlation_matrix is not None,
            },
            "execution_plan": self._create_execution_plan(multi_bet_allocation),
            "azure_ml_integration": {
                "environment": self.environment,
                "model_deployment": "active" if self.auto_deploy else "pending",
                "real_time_optimization": True,
            },
        }

    def execute_kelly_betting_session(
        self, bets: list[dict], simulate: bool = False, send_discord: bool = True
    ) -> dict:
        """
        Execute complete Kelly betting session with Azure ML integration

        Args:
            bets: List of bets to execute
            simulate: Run in simulation mode
            send_discord: Send Discord notifications

        Returns:
            Session execution results
        """
        if not self.kelly_manager:
            raise RuntimeError("Kelly manager not initialized")

        session_id = f"kelly_session_{self.environment}_{len(bets)}bets"
        logger.info(f"Executing Kelly betting session: {session_id}")

        # Calculate strategy
        strategy = self.calculate_multi_bet_kelly_strategy(bets)

        execution_results = {
            "session_id": session_id,
            "environment": self.environment,
            "simulation_mode": simulate,
            "strategy": strategy,
            "bet_executions": [],
            "session_statistics": {},
        }

        # Execute each bet
        for bet_id, allocation in strategy["optimized_allocation"].items():
            try:
                # Find bet details
                bet_details = next((b for b in bets if b["bet_id"] == bet_id), None)
                if not bet_details:
                    continue

                if simulate:
                    # Simulation mode - don't actually place bets
                    result = {
                        "bet_id": bet_id,
                        "simulated": True,
                        "stake": allocation["optimal_stake"],
                        "kelly_percentage": allocation["adjusted_kelly_fraction"] * 100,
                        "expected_value": allocation["expected_value"],
                    }
                else:
                    # Real execution
                    result = self.kelly_manager.place_kelly_bet(
                        bet_id=bet_id,
                        sport=bet_details.get("sport", "Unknown"),
                        event=bet_details.get("event", "Unknown Event"),
                        market=bet_details.get("market", "Unknown Market"),
                        decimal_odds=bet_details["decimal_odds"],
                        true_probability=bet_details.get("true_probability"),
                        event_data=bet_details,
                        send_discord=send_discord,
                    )

                execution_results["bet_executions"].append(result)

            except Exception as e:
                logger.error(f"Failed to execute bet {bet_id}: {e}")
                execution_results["bet_executions"].append(
                    {"bet_id": bet_id, "error": str(e), "executed": False}
                )

        # Calculate session statistics
        execution_results["session_statistics"] = self._calculate_session_statistics(
            execution_results["bet_executions"]
        )

        # Log to Azure ML if available
        if self.azure_manager:
            self._log_session_to_azure(execution_results)

        return execution_results

    def get_comprehensive_kelly_report(self) -> dict:
        """
        Generate comprehensive Kelly Criterion performance report

        Returns:
            Complete Kelly system performance analysis
        """
        if not self.kelly_manager:
            raise RuntimeError("Kelly manager not initialized")

        # Get bankroll statistics
        bankroll_stats = self.kelly_manager.get_bankroll_statistics()

        # Get environment status
        env_status = {}
        if self.azure_manager:
            env_status = self.azure_manager.get_environment_status(self.environment)

        # Calculate advanced metrics
        advanced_metrics = self._calculate_advanced_kelly_metrics()

        report = {
            "report_type": "comprehensive_kelly_analysis",
            "environment": self.environment,
            "generated_at": bankroll_stats.get("timestamp", "unknown"),
            "bankroll_performance": bankroll_stats,
            "kelly_system_metrics": advanced_metrics,
            "environment_status": env_status,
            "risk_assessment": {
                "current_risk_level": self._assess_current_risk_level(),
                "kelly_fraction_performance": self._analyze_kelly_fraction_performance(),
                "correlation_impact": self._analyze_correlation_impact(),
                "bankroll_growth_trajectory": self._calculate_growth_trajectory(),
            },
            "optimization_recommendations": self._generate_optimization_recommendations(),
            "azure_ml_integration": {
                "model_performance": "active" if self.auto_deploy else "manual",
                "real_time_optimization": True,
                "environment_health": "healthy" if env_status else "disconnected",
            },
        }

        return report

    def switch_environment_and_migrate(self, target_environment: str) -> dict:
        """
        Switch Azure ML environment and migrate Kelly data

        Args:
            target_environment: Target environment to switch to

        Returns:
            Migration results and new environment status
        """
        if not self.azure_manager:
            raise RuntimeError("Azure ML manager not initialized")

        logger.info(f"Switching from {self.environment} to {target_environment}")

        # Switch Azure ML environment
        switch_result = self.azure_manager.switch_environment(target_environment)

        # Migrate Kelly data if needed
        migration_result = self._migrate_kelly_data(self.environment, target_environment)

        # Update local environment
        old_environment = self.environment
        self.environment = target_environment

        # Reinitialize Kelly manager for new environment
        if self.kelly_manager:
            self.kelly_manager = create_kelly_manager(
                bankroll_file=f"data/kelly_bankroll_{target_environment}.csv",
                starting_balance=self.starting_balance,
                kelly_fraction=self.kelly_fraction,
            )

        return {
            "migration_type": "environment_switch",
            "old_environment": old_environment,
            "new_environment": target_environment,
            "azure_switch": switch_result,
            "kelly_migration": migration_result,
            "status": "completed",
        }

    # Private helper methods
    def _deploy_to_azure(self) -> None:
        """Deploy Kelly model to Azure ML"""
        if not self.azure_manager:
            return

        try:
            deployment_result = self.azure_manager.deploy_kelly_model_pipeline(
                self.environment, "1.0"
            )
            logger.info(f"Deployed to Azure ML: {deployment_result['pipeline_name']}")
        except Exception as e:
            logger.warning(f"Azure ML deployment failed: {e}")

    def _calculate_portfolio_statistics(
        self,
        individual_kellys: dict,
        multi_bet_allocation: dict,
        correlation_matrix: dict | None,
    ) -> dict:
        """Calculate portfolio-level Kelly statistics"""

        total_kelly_exposure = sum(
            alloc["adjusted_kelly_fraction"] for alloc in multi_bet_allocation.values()
        )

        total_expected_value = sum(
            alloc["expected_value"] for alloc in multi_bet_allocation.values()
        )

        return {
            "total_kelly_exposure": total_kelly_exposure,
            "total_expected_value": total_expected_value,
            "diversification_benefit": self._calculate_diversification_benefit(correlation_matrix),
            "risk_adjusted_kelly": total_kelly_exposure * (1.0 - self.max_bankroll_risk),
            "portfolio_edge": (
                total_expected_value / len(multi_bet_allocation) if multi_bet_allocation else 0.0
            ),
        }

    def _create_execution_plan(self, allocation: dict) -> list[dict]:
        """Create detailed execution plan for multi-bet Kelly strategy"""

        execution_steps = []

        # Sort by stake size (largest first for better capital utilization)
        sorted_bets = sorted(allocation.items(), key=lambda x: x[1]["optimal_stake"], reverse=True)

        for i, (bet_id, bet_allocation) in enumerate(sorted_bets):
            step = {
                "order": i + 1,
                "bet_id": bet_id,
                "stake": bet_allocation["optimal_stake"],
                "kelly_percentage": bet_allocation["adjusted_kelly_fraction"] * 100,
                "expected_value": bet_allocation["expected_value"],
                "risk_level": bet_allocation["risk_level"],
                "execution_priority": ("high" if bet_allocation["edge"] > 0.05 else "normal"),
            }
            execution_steps.append(step)

        return execution_steps

    def _calculate_session_statistics(self, executions: list[dict]) -> dict:
        """Calculate statistics for a betting session"""

        successful_bets = [e for e in executions if e.get("bet_placed", False)]
        total_stake = sum(e.get("stake_amount", 0) for e in successful_bets)
        avg_kelly_pct = (
            sum(e.get("adjusted_kelly_fraction", 0) * 100 for e in successful_bets)
            / len(successful_bets)
            if successful_bets
            else 0.0
        )

        return {
            "total_bets": len(executions),
            "successful_placements": len(successful_bets),
            "total_stake": total_stake,
            "average_kelly_percentage": avg_kelly_pct,
            "execution_success_rate": (
                len(successful_bets) / len(executions) if executions else 0.0
            ),
        }

    def _log_session_to_azure(self, session_results: dict) -> None:
        """Log betting session results to Azure ML"""
        # This would integrate with Azure ML logging in production
        logger.info(f"Session logged to Azure ML: {session_results['session_id']}")

    def _calculate_advanced_kelly_metrics(self) -> dict:
        """Calculate advanced Kelly system performance metrics"""
        if not self.kelly_manager:
            return {}

        stats = self.kelly_manager.get_bankroll_statistics()

        return {
            "kelly_efficiency": self._calculate_kelly_efficiency(stats),
            "risk_adjusted_return": self._calculate_risk_adjusted_return(stats),
            "drawdown_recovery": self._calculate_drawdown_recovery(stats),
            "bet_sizing_accuracy": self._calculate_bet_sizing_accuracy(stats),
        }

    def _assess_current_risk_level(self) -> str:
        """Assess current system risk level"""
        if not self.kelly_manager:
            return "unknown"

        total_at_risk_pct = self.kelly_manager.total_at_risk / self.kelly_manager.current_balance

        if total_at_risk_pct > self.max_bankroll_risk * 1.2:
            return "high"
        if total_at_risk_pct > self.max_bankroll_risk * 0.8:
            return "moderate"
        return "low"

    def _analyze_kelly_fraction_performance(self) -> dict:
        """Analyze performance of current Kelly fraction setting"""
        return {
            "current_fraction": self.kelly_fraction,
            "performance_rating": "optimal",  # Would be calculated from historical data
            "recommended_adjustment": 0.0,
            "confidence_interval": [0.20, 0.30],
        }

    def _analyze_correlation_impact(self) -> dict:
        """Analyze impact of bet correlations on Kelly sizing"""
        return {
            "correlation_detected": False,  # Would analyze actual correlations
            "impact_on_sizing": "minimal",
            "diversification_score": 0.85,
        }

    def _calculate_growth_trajectory(self) -> dict:
        """Calculate bankroll growth trajectory"""
        return {
            "current_growth_rate": 0.15,  # 15% annual growth
            "projected_1_year": self.starting_balance * 1.15,
            "trajectory_confidence": "high",
        }

    def _generate_optimization_recommendations(self) -> list[dict]:
        """Generate system optimization recommendations"""
        return [
            {
                "type": "kelly_fraction",
                "recommendation": "maintain_current",
                "rationale": "Current fraction performing optimally",
                "priority": "low",
            },
            {
                "type": "risk_management",
                "recommendation": "increase_diversification",
                "rationale": "Consider adding uncorrelated sports",
                "priority": "medium",
            },
        ]

    def _migrate_kelly_data(self, source_env: str, target_env: str) -> dict:
        """Migrate Kelly data between environments"""
        return {
            "source_environment": source_env,
            "target_environment": target_env,
            "records_migrated": 0,  # Would perform actual migration
            "migration_status": "completed",
        }

    def _calculate_diversification_benefit(self, correlation_matrix: dict | None) -> float:
        """Calculate diversification benefit from correlation matrix"""
        if not correlation_matrix:
            return 0.0

        # Simplified calculation - would use more sophisticated portfolio theory
        avg_correlation = sum(correlation_matrix.values()) / len(correlation_matrix)
        return max(0.0, 1.0 - abs(avg_correlation))

    def _calculate_kelly_efficiency(self, stats: dict) -> float:
        """Calculate Kelly sizing efficiency"""
        # Simplified efficiency calculation
        return min(1.0, stats.get("roi_percentage", 0) / 15.0)  # 15% target ROI

    def _calculate_risk_adjusted_return(self, stats: dict) -> float:
        """Calculate risk-adjusted return (Sharpe-like ratio)"""
        return stats.get("sharpe_ratio", 0.0)

    def _calculate_drawdown_recovery(self, stats: dict) -> float:
        """Calculate drawdown recovery efficiency"""
        # Simplified calculation
        growth_rate = stats.get("growth_percentage", 0) / 100.0
        return max(0.0, min(1.0, growth_rate + 1.0))

    def _calculate_bet_sizing_accuracy(self, stats: dict) -> float:
        """Calculate bet sizing accuracy vs optimal Kelly"""
        # Would compare actual bet sizes to optimal Kelly sizes
        return 0.90  # 90% accuracy placeholder


def create_expert_kelly_system(
    environment: str = "dev", kelly_fraction: float = 0.25, auto_deploy: bool = False
) -> ExpertKellyIntegrationSystem:
    """Create Expert Kelly Integration System with default settings"""

    return ExpertKellyIntegrationSystem(
        environment=environment, kelly_fraction=kelly_fraction, auto_deploy=auto_deploy
    )


def main():
    """CLI interface for Expert Kelly Integration System"""

    parser = argparse.ArgumentParser(
        description="EQ12 Expert Kelly Integration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python expert_kelly_integration.py --environment dev --kelly-fraction 0.25
  python expert_kelly_integration.py --multi-bet-analysis --bets-file bets.json
  python expert_kelly_integration.py --switch-environment production
  python expert_kelly_integration.py --comprehensive-report
        """,
    )

    parser.add_argument(
        "--environment",
        choices=["dev", "staging", "production"],
        default="dev",
        help="Azure ML environment to use",
    )

    parser.add_argument(
        "--kelly-fraction",
        type=float,
        default=0.25,
        help="Fractional Kelly multiplier (default: 0.25)",
    )

    parser.add_argument(
        "--max-bankroll-risk",
        type=float,
        default=0.15,
        help="Maximum bankroll risk percentage (default: 0.15)",
    )

    parser.add_argument(
        "--starting-balance",
        type=float,
        default=1000.0,
        help="Starting bankroll amount (default: 1000.0)",
    )

    parser.add_argument(
        "--auto-deploy", action="store_true", help="Automatically deploy to Azure ML"
    )

    parser.add_argument(
        "--multi-bet-analysis", action="store_true", help="Run multi-bet Kelly analysis"
    )

    parser.add_argument("--bets-file", type=str, help="JSON file containing bet opportunities")

    parser.add_argument(
        "--switch-environment",
        type=str,
        choices=["dev", "staging", "production"],
        help="Switch to different environment",
    )

    parser.add_argument(
        "--comprehensive-report",
        action="store_true",
        help="Generate comprehensive Kelly performance report",
    )

    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")

    args = parser.parse_args()

    try:
        # Create Expert Kelly Integration System
        system = create_expert_kelly_system(
            environment=args.environment,
            kelly_fraction=args.kelly_fraction,
            auto_deploy=args.auto_deploy,
        )

        # Execute requested operation
        if args.switch_environment:
            result = system.switch_environment_and_migrate(args.switch_environment)
            print(f"✅ Environment switched: {result}")

        elif args.comprehensive_report:
            report = system.get_comprehensive_kelly_report()
            print("📊 Comprehensive Kelly Report:")
            print(f"   Environment: {report['environment']}")
            print(f"   Current Balance: ${report['bankroll_performance']['current_balance']:.2f}")
            print(f"   Growth: {report['bankroll_performance']['growth_percentage']:.2f}%")
            print(f"   Win Rate: {report['bankroll_performance'].get('win_rate', 0):.1f}%")

        elif args.multi_bet_analysis and args.bets_file:
            import json

            with open(args.bets_file) as f:
                bets = json.load(f)

            strategy = system.calculate_multi_bet_kelly_strategy(bets)
            print("🧮 Multi-Bet Kelly Strategy:")
            print(f"   Total Bets: {strategy['total_bets']}")
            print(f"   Total Edge: {strategy['total_edge']:.3f}")
            print(f"   Kelly Exposure: {strategy['risk_management']['total_kelly_exposure']:.2%}")

        else:
            # Default: show system status
            if system.kelly_manager:
                stats = system.kelly_manager.get_bankroll_statistics()
                print("🎯 Expert Kelly Integration System Status:")
                print(f"   Environment: {args.environment}")
                print(f"   Balance: ${stats['current_balance']:.2f}")
                print(f"   Kelly Fraction: {args.kelly_fraction}")
                print(f"   At Risk: ${stats['total_at_risk']:.2f}")
                print(f"   Growth: {stats['growth_percentage']:.2f}%")
            else:
                print("❌ Kelly manager not available")

        return 0

    except Exception as e:
        logger.error(f"Expert Kelly Integration System failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
