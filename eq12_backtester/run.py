"""
EQ12 Backtester CLI Runner
Time-machine profit loop for historic backtesting

This is the main entry point for running EQ12 backtests:
- CLI interface for all backtest operations
- Integration with EQ12 task system
- Automated profit optimization loops
- ROI calculations and reporting
- Kelly sizing and bankroll management
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Add the eq12_backtester to Python path for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))

try:
    # Try absolute imports first
    from eq12_backtester.core.engine import Bet, EQ12BacktesterEngine, MarketType
    from eq12_backtester.data.loader import EQ12DataLoader
    from eq12_backtester.optimizers.parlay_optimizer import (
        EQ12ParlayOptimizer,
        ParlayType,
    )
except ImportError:
    # Fallback to relative imports
    from optimizers.parlay_optimizer import EQ12ParlayOptimizer, ParlayType

    from core.engine import Bet, EQ12BacktesterEngine, MarketType
    from data.loader import EQ12DataLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_recent_scores(sport: str, days: int) -> list[dict[str, Any]]:
    """
    Get recent game scores for a sport

    Args:
        sport: Sport name (e.g., 'NFL', 'NBA', 'MLB')
        days: Number of days back to look

    Returns:
        List of recent game data
    """
    logger.info(f"Fetching recent scores for {sport} (last {days} days)")

    # This is a stub implementation - in production this would
    # connect to a sports API or database
    sample_games = [
        {
            "date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
            "home_team": f"Team{i}_Home",
            "away_team": f"Team{i}_Away",
            "home_score": 20 + i,
            "away_score": 18 + i,
            "sport": sport,
        }
        for i in range(min(days, 10))  # Limit to 10 games for demo
    ]

    return sample_games


def load_eq12_prop_data(prop_type: str) -> dict[str, Any]:
    """
    Load EQ12 prop betting data

    Args:
        prop_type: Type of prop (e.g., 'MLB_HR', 'NFL_TD', 'NBA_PTS')

    Returns:
        Dictionary containing prop data and statistics
    """
    logger.info(f"Loading EQ12 prop data for {prop_type}")

    # This is a stub implementation - in production this would
    # load from EQ12's proprietary data sources
    prop_data = {
        "type": prop_type,
        "total_props": 150,
        "avg_odds": -110,
        "hit_rate": 0.55,
        "expected_value": 0.02,
        "last_updated": datetime.now().isoformat(),
        "sample_props": [
            {
                "player": "Sample Player 1",
                "line": 1.5,
                "over_odds": -115,
                "under_odds": -105,
                "recommendation": "OVER",
                "confidence": 0.72,
            },
            {
                "player": "Sample Player 2",
                "line": 2.5,
                "over_odds": -120,
                "under_odds": +100,
                "recommendation": "UNDER",
                "confidence": 0.68,
            },
        ],
    }

    return prop_data


class EQ12BacktestRunner:
    """
    Main runner for EQ12 backtesting operations

    Features:
    - Historic backtesting with real data
    - Paper trading simulation
    - Parlay optimization
    - ROI and profit tracking
    - Integration with EQ12 godmode
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = Path(eq12_root)

        # Initialize components
        self.engine = EQ12BacktesterEngine(eq12_root=str(self.eq12_root))
        self.data_loader = EQ12DataLoader(eq12_root=str(self.eq12_root))
        self.parlay_optimizer = EQ12ParlayOptimizer(eq12_root=str(self.eq12_root))

        # Configuration
        self.config = {
            "default_bankroll": 1000.0,
            "default_daily_budget": 100.0,
            "kelly_max": 0.25,  # Max 25% Kelly
            "min_confidence": 0.6,
            "telegram_notifications": True,
        }

        logger.info("EQ12 Backtest Runner initialized")

    def run_historical_backtest(
        self,
        sport: str,
        market: str,
        start_date: str,
        end_date: str,
        stake: float = 50.0,
    ) -> dict[str, Any]:
        """
        Run historical backtest for specific sport/market

        Args:
            sport: MLB, NFL, NBA, UFC
            market: HR, TB, ML, Spread, Total, etc.
            start_date: YYYY-MM-DD format
            end_date: YYYY-MM-DD format
            stake: Default stake per bet

        Returns:
            Dict with backtest results
        """
        logger.info(f"Running historical backtest: {sport} {market} ({start_date} to {end_date})")

        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # Load historical data
        historical_bets = self._load_historical_bets(sport, market, start_dt, end_dt, stake)

        if not historical_bets:
            logger.warning(f"No historical bets found for {sport} {market}")
            return {}

        # Add bets to engine
        for bet in historical_bets:
            self.engine.add_bet(bet)

        # Run backtest
        results = self.engine.run_backtest(start_dt, end_dt, daily_budget=stake * 5)

        # Export results
        report_file = self.engine.export_results(f"{sport}_{market}_backtest")

        # Generate summary
        summary = {
            "sport": sport,
            "market": market,
            "period": f"{start_date} to {end_date}",
            "total_bets": results.get("total_bets", 0),
            "win_rate": f"{results.get('win_rate', 0) * 100:.1f}%",
            "roi": f"{results.get('roi_percent', 0):+.2f}%",
            "profit": f"${results.get('total_profit', 0):+.2f}",
            "max_drawdown": f"{results.get('max_drawdown', 0) * 100:.1f}%",
            "sharpe_ratio": f"{results.get('sharpe_ratio', 0):.2f}",
            "report_file": report_file,
        }

        logger.info(f"Backtest completed: {summary['win_rate']} win rate, {summary['roi']} ROI")
        return summary

    def run_parlay_optimization(
        self, sport: str = "MLB", parlay_type: str = "multi_game"
    ) -> dict[str, Any]:
        """
        Run parlay optimization for current opportunities

        Args:
            sport: Target sport for parlays
            parlay_type: same_game, multi_game, multi_sport, moonshot

        Returns:
            Dict with optimized parlays
        """
        logger.info(f"Running parlay optimization: {sport} {parlay_type}")

        # Load current betting opportunities
        available_bets = self._load_current_betting_opportunities(sport)

        if not available_bets:
            logger.warning(f"No current betting opportunities for {sport}")
            return {}

        # Map parlay type
        parlay_type_enum = {
            "same_game": ParlayType.SAME_GAME,
            "multi_game": ParlayType.MULTI_GAME,
            "multi_sport": ParlayType.MULTI_SPORT,
            "moonshot": ParlayType.MOONSHOT,
        }.get(parlay_type, ParlayType.MULTI_GAME)

        # Optimize parlays
        parlay_candidates = self.parlay_optimizer.optimize_parlay(available_bets, parlay_type_enum)

        # Get auto-lock parlays
        auto_locks = self.parlay_optimizer.get_auto_lock_parlays(available_bets)

        # Export recommendations
        if parlay_candidates:
            recommendations_file = self.parlay_optimizer.export_parlay_recommendations(
                parlay_candidates
            )
        else:
            recommendations_file = None

        summary = {
            "sport": sport,
            "parlay_type": parlay_type,
            "available_bets": len(available_bets),
            "parlay_candidates": len(parlay_candidates),
            "auto_locks": len(auto_locks),
            "best_parlay": None,
            "recommendations_file": recommendations_file,
        }

        # Get best parlay details
        if parlay_candidates:
            best = parlay_candidates[0]
            summary["best_parlay"] = {
                "legs": best.leg_count,
                "odds": f"{best.combined_odds:+g}",
                "expected_value": f"${best.expected_value:.2f}",
                "confidence": f"{best.confidence_score:.2f}",
                "quality_score": f"{best.quality_score:.2f}",
            }

        logger.info(
            f"Parlay optimization completed: {len(parlay_candidates)} candidates, {len(auto_locks)} auto-locks"
        )
        return summary

    def run_paper_trading_simulation(self, days: int = 30) -> dict[str, Any]:
        """
        Run paper trading simulation for specified number of days

        Args:
            days: Number of days to simulate

        Returns:
            Dict with simulation results
        """
        logger.info(f"Running paper trading simulation: {days} days")

        # Set up simulation period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Load recent game data
        sports = ["MLB", "NFL", "NBA"]
        all_bets = []

        for sport in sports:
            recent_games = get_recent_scores(sport, days)
            sport_bets = self._generate_bets_from_games(recent_games)
            all_bets.extend(sport_bets)

        if not all_bets:
            logger.warning("No bets generated for paper trading")
            return {}

        # Add bets to engine
        for bet in all_bets:
            self.engine.add_bet(bet)

        # Run simulation
        results = self.engine.run_backtest(start_date, end_date)

        # Generate summary
        summary = {
            "simulation_period": f"{days} days",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_bets": results.get("total_bets", 0),
            "win_rate": f"{results.get('win_rate', 0) * 100:.1f}%",
            "profit": f"${results.get('total_profit', 0):+.2f}",
            "roi": f"{results.get('roi_percent', 0):+.2f}%",
            "final_bankroll": f"${results.get('final_bankroll', 0):.2f}",
        }

        logger.info(f"Paper trading simulation completed: {summary['win_rate']} win rate")
        return summary

    def run_daily_edge_scan(self) -> dict[str, Any]:
        """
        Run daily edge scanning for betting opportunities

        Returns:
            Dict with edge opportunities found
        """
        logger.info("Running daily edge scan")

        # Get today's games and odds
        current_opportunities = []
        sports = ["MLB", "NFL", "NBA"]

        for sport in sports:
            # Load today's games
            today_games = self.data_loader.get_espn_scores(sport)

            # Load prop sheets if available
            prop_data = load_eq12_prop_data(f"{sport}_HR")

            # Generate betting opportunities
            sport_opportunities = self._generate_betting_opportunities(today_games, prop_data)
            current_opportunities.extend(sport_opportunities)

        if not current_opportunities:
            logger.warning("No betting opportunities found")
            return {}

        # Calculate expected values
        edge_opportunities = []
        for bet in current_opportunities:
            ev = self.engine.calculate_expected_value(
                true_prob=0.55,  # Simplified - would use model prediction
                odds=bet.odds,
                stake=bet.stake,
            )

            if ev > 0:  # Positive EV
                edge_opportunities.append(
                    {
                        "bet": bet,
                        "expected_value": ev,
                        "ev_percent": (ev / bet.stake) * 100,
                    }
                )

        # Sort by EV%
        edge_opportunities.sort(key=lambda x: x["ev_percent"], reverse=True)

        # Generate auto-lock parlays
        if len(current_opportunities) >= 2:
            auto_locks = self.parlay_optimizer.get_auto_lock_parlays(current_opportunities)
        else:
            auto_locks = []

        summary = {
            "scan_date": datetime.now().strftime("%Y-%m-%d"),
            "opportunities_found": len(current_opportunities),
            "positive_ev_bets": len(edge_opportunities),
            "auto_lock_parlays": len(auto_locks),
            "best_edges": [],
        }

        # Add top 5 best edges
        for edge in edge_opportunities[:5]:
            bet = edge["bet"]
            summary["best_edges"].append(
                {
                    "selection": bet.selection,
                    "odds": f"{bet.odds:+g}",
                    "ev": f"${edge['expected_value']:.2f}",
                    "ev_percent": f"{edge['ev_percent']:+.1f}%",
                }
            )

        logger.info(f"Edge scan completed: {len(edge_opportunities)} positive EV opportunities")
        return summary

    def _load_historical_bets(
        self,
        sport: str,
        market: str,
        start_date: datetime,
        end_date: datetime,
        stake: float,
    ) -> list[Bet]:
        """Load historical bets for backtesting"""
        # In production, this would load from prop sheets and historical data
        # For now, generate sample bets

        sample_bets = []
        current_date = start_date
        bet_id = 1

        while current_date <= end_date:
            # Generate 1-3 bets per day
            daily_bet_count = min(3, max(1, int(abs(hash(current_date) % 3))))

            for _i in range(daily_bet_count):
                # Sample market types
                market_mapping = {
                    "HR": MarketType.MLB_HR,
                    "TB": MarketType.MLB_TB,
                    "ML": MarketType.MLB_MONEYLINE,
                    "Spread": MarketType.MLB_SPREAD,
                }

                market_type = market_mapping.get(market, MarketType.MLB_HR)

                bet = Bet(
                    bet_id=f"{sport}_{market}_{bet_id}",
                    sport=sport,
                    market_type=market_type,
                    selection=f"Sample {market} bet {bet_id}",
                    odds=120 + (bet_id % 200),  # Vary odds
                    stake=stake,
                    timestamp=current_date,
                )
                sample_bets.append(bet)
                bet_id += 1

            current_date += timedelta(days=1)

        logger.info(f"Generated {len(sample_bets)} historical bets for backtesting")
        return sample_bets

    def _load_current_betting_opportunities(self, sport: str) -> list[Bet]:
        """Load current betting opportunities"""
        # In production, would load from live odds feeds
        # For now, generate sample opportunities

        opportunities = []

        if sport == "MLB":
            opportunities = [
                Bet(
                    bet_id="mlb_1",
                    sport="MLB",
                    market_type=MarketType.MLB_HR,
                    selection="Aaron Judge Over 0.5 HR",
                    odds=150,
                    stake=50,
                ),
                Bet(
                    bet_id="mlb_2",
                    sport="MLB",
                    market_type=MarketType.MLB_TB,
                    selection="Mookie Betts Over 1.5 TB",
                    odds=120,
                    stake=50,
                ),
                Bet(
                    bet_id="mlb_3",
                    sport="MLB",
                    market_type=MarketType.MLB_HITS,
                    selection="Vladimir Guerrero Jr Over 0.5 Hits",
                    odds=110,
                    stake=50,
                ),
            ]
        elif sport == "NFL":
            opportunities = [
                Bet(
                    bet_id="nfl_1",
                    sport="NFL",
                    market_type=MarketType.NFL_PROPS,
                    selection="Josh Allen Over 1.5 Passing TDs",
                    odds=130,
                    stake=50,
                ),
                Bet(
                    bet_id="nfl_2",
                    sport="NFL",
                    market_type=MarketType.NFL_PROPS,
                    selection="Christian McCaffrey Over 0.5 Rushing TD",
                    odds=140,
                    stake=50,
                ),
            ]

        logger.info(f"Loaded {len(opportunities)} current opportunities for {sport}")
        return opportunities

    def _generate_bets_from_games(self, games) -> list[Bet]:
        """Generate bets from game data"""
        # Simplified bet generation
        bets = []

        for i, game in enumerate(games[:10]):  # Limit to 10 games
            bet = Bet(
                bet_id=f"sim_{i}",
                sport=game.sport,
                market_type=MarketType.MLB_MONEYLINE,
                selection=f"{game.away_team} ML",
                odds=110,
                stake=50,
                timestamp=game.date,
            )
            bets.append(bet)

        return bets

    def _generate_betting_opportunities(self, games, prop_data) -> list[Bet]:
        """Generate betting opportunities from games and prop data"""
        opportunities = []

        # Simplified opportunity generation
        for i, game in enumerate(games[:5]):  # Limit to 5 games
            bet = Bet(
                bet_id=f"opp_{i}",
                sport=game.sport,
                market_type=MarketType.MLB_HR,
                selection=f"Sample HR bet {i}",
                odds=150,
                stake=50,
            )
            opportunities.append(bet)

        return opportunities


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="EQ12 Historic Backtester")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Historical backtest command
    backtest_parser = subparsers.add_parser("backtest", help="Run historical backtest")
    backtest_parser.add_argument(
        "--sport",
        required=True,
        choices=["MLB", "NFL", "NBA", "UFC"],
        help="Sport to backtest",
    )
    backtest_parser.add_argument(
        "--market", required=True, help="Market type (HR, TB, ML, Spread, etc.)"
    )
    backtest_parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    backtest_parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    backtest_parser.add_argument(
        "--stake", type=float, default=50.0, help="Stake per bet (default: $50)"
    )

    # Parlay optimization command
    parlay_parser = subparsers.add_parser("parlay", help="Optimize parlays")
    parlay_parser.add_argument("--sport", default="MLB", help="Target sport (default: MLB)")
    parlay_parser.add_argument(
        "--type",
        default="multi_game",
        choices=["same_game", "multi_game", "multi_sport", "moonshot"],
        help="Parlay type (default: multi_game)",
    )

    # Paper trading command
    paper_parser = subparsers.add_parser("paper", help="Run paper trading simulation")
    paper_parser.add_argument(
        "--days", type=int, default=30, help="Simulation period in days (default: 30)"
    )

    # Edge scan command
    subparsers.add_parser("scan", help="Daily edge scan")

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize runner
    runner = EQ12BacktestRunner()

    try:
        if args.command == "backtest":
            results = runner.run_historical_backtest(
                sport=args.sport,
                market=args.market,
                start_date=args.start,
                end_date=args.end,
                stake=args.stake,
            )

            print("\n🎯 EQ12 Historical Backtest Results")
            print("=" * 50)
            print(f"Sport/Market: {results['sport']} {results['market']}")
            print(f"Period: {results['period']}")
            print(f"Total Bets: {results['total_bets']}")
            print(f"Win Rate: {results['win_rate']}")
            print(f"ROI: {results['roi']}")
            print(f"Profit: {results['profit']}")
            print(f"Max Drawdown: {results['max_drawdown']}")
            print(f"Sharpe Ratio: {results['sharpe_ratio']}")
            print(f"Report: {results['report_file']}")

        elif args.command == "parlay":
            results = runner.run_parlay_optimization(sport=args.sport, parlay_type=args.type)

            print("\n🎯 EQ12 Parlay Optimization Results")
            print("=" * 50)
            print(f"Sport: {results['sport']}")
            print(f"Parlay Type: {results['parlay_type']}")
            print(f"Available Bets: {results['available_bets']}")
            print(f"Parlay Candidates: {results['parlay_candidates']}")
            print(f"Auto-Lock Parlays: {results['auto_locks']}")

            if results["best_parlay"]:
                best = results["best_parlay"]
                print("\nBest Parlay:")
                print(f"  Legs: {best['legs']}")
                print(f"  Odds: {best['odds']}")
                print(f"  Expected Value: {best['expected_value']}")
                print(f"  Confidence: {best['confidence']}")
                print(f"  Quality Score: {best['quality_score']}")

            if results["recommendations_file"]:
                print(f"\nRecommendations: {results['recommendations_file']}")

        elif args.command == "paper":
            results = runner.run_paper_trading_simulation(days=args.days)

            print("\n🎯 EQ12 Paper Trading Results")
            print("=" * 50)
            print(f"Period: {results['simulation_period']}")
            print(f"Dates: {results['start_date']} to {results['end_date']}")
            print(f"Total Bets: {results['total_bets']}")
            print(f"Win Rate: {results['win_rate']}")
            print(f"Profit: {results['profit']}")
            print(f"ROI: {results['roi']}")
            print(f"Final Bankroll: {results['final_bankroll']}")

        elif args.command == "scan":
            results = runner.run_daily_edge_scan()

            print("\n🎯 EQ12 Daily Edge Scan Results")
            print("=" * 50)
            print(f"Scan Date: {results['scan_date']}")
            print(f"Opportunities Found: {results['opportunities_found']}")
            print(f"Positive EV Bets: {results['positive_ev_bets']}")
            print(f"Auto-Lock Parlays: {results['auto_lock_parlays']}")

            if results["best_edges"]:
                print("\nTop Edge Opportunities:")
                for i, edge in enumerate(results["best_edges"]):
                    print(f"  {i + 1}. {edge['selection']}")
                    print(f"     Odds: {edge['odds']} | EV: {edge['ev']} ({edge['ev_percent']})")

    except Exception as e:
        logger.error(f"Error running command: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
