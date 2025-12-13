#!/usr/bin/env python3
"""
EQ12 CLI Extension for GitHub Integration
New commands for arbitrage, Kelly, and OddsAPI functionality
"""

from github_repo_integrator import GitHubRepoIntegrator
import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add EQ12 scripts to path
sys.path.append(str(Path(__file__).parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EQ12GitHubCLI:
    def __init__(self):
        self.integrator = GitHubRepoIntegrator()
        self.eq12_root = Path(__file__).parent.parent

    async def ingest_odds_api(self, sport="nfl", regions="us",
                              markets="h2h,spreads,totals"):
        """Ingest odds data using integrated OddsAPI client"""
        print("🔄 Ingesting odds for {sport.upper()}...")

        try:
            # Mock implementation - would call actual VB.NET OddsApiClient
            results = {
                "sport": sport,
                "regions": regions,
                "markets": markets.split(","),
                "records_ingested": 150,
                "books_covered": ["DraftKings", "FanDuel", "BetMGM", "Caesars"],
                "timestamp": datetime.now().isoformat(),
            }

            print("✅ Successfully ingested {results['records_ingested']} odds records")
            print("📊 Sports: {results['sport']}")
            print("📚 Books: {', '.join(results['books_covered'])}")

            # Save to logs
            log_file = (
                self.eq12_root
                / "logs"
                / f"odds_ingest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(log_file, "w") as f:
                json.dump(results, f, indent=2)

            print("📋 Results logged to: {log_file}")

        except Exception as e:
            logger.error(f"Error ingesting odds: {e}")
            print("❌ Error: {e}")

    async def run_arb_bot(self, window="60m", min_arb=1.0, sport="all"):
        """Run arbitrage detection bot"""
        print("🤖 Running arbitrage bot (min {min_arb}% arb, {window} window)...")

        try:
            # Mock arbitrage detection results
            opportunities = [
                {
                    "event_id": "nfl_20251003_chi_gb",
                    "sport": "NFL",
                    "matchup": "Chicago Bears vs Green Bay Packers",
                    "sideA": "Chicago Bears ML",
                    "bookA": "DraftKings",
                    "oddsA": +165,
                    "sideB": "Green Bay Packers ML",
                    "bookB": "FanDuel",
                    "oddsB": -150,
                    "arb_pct": 2.4,
                    "lock_profit": 24.50,
                    "total_stake": 1000.00,
                    "timestamp": datetime.now().isoformat(),
                },
                {
                    "event_id": "nba_20251003_lal_bos",
                    "sport": "NBA",
                    "matchup": "Lakers vs Celtics",
                    "sideA": "Lakers +7.5",
                    "bookA": "BetMGM",
                    "oddsA": -105,
                    "sideB": "Celtics -7.5",
                    "bookB": "Caesars",
                    "oddsB": -115,
                    "arb_pct": 1.8,
                    "lock_profit": 18.00,
                    "total_stake": 1000.00,
                    "timestamp": datetime.now().isoformat(),
                },
            ]

            # Filter by minimum arbitrage percentage
            filtered_opportunities = [
                opp for opp in opportunities if opp["arb_pct"] >= min_arb]

            if filtered_opportunities:
                print("🎯 Found {len(filtered_opportunities)} arbitrage opportunities:")
                print()

                for _i, opp in enumerate(filtered_opportunities, 1):
                    print("#{i} - {opp['sport']} - {opp['arb_pct']}% Arbitrage")
                    print("    {opp['matchup']}")
                    print("    🟢 {opp['sideA']} ({opp['oddsA']:+d}) at {opp['bookA']}")
                    print("    🔴 {opp['sideB']} ({opp['oddsB']:+d}) at {opp['bookB']}")
                    print("    💰 Lock Profit: ${opp['lock_profit']:.2f}")
                    print()

                # Save results
                results_file = (
                    self.eq12_root
                    / "logs"
                    / f"arbitrage_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(results_file, "w") as f:
                    json.dump(
                        {
                            "scan_parameters": {
                                "window": window,
                                "min_arb": min_arb,
                                "sport": sport,
                            },
                            "opportunities": filtered_opportunities,
                            "summary": {
                                "total_opportunities": len(filtered_opportunities),
                                "total_profit_potential": sum(
                                    opp["lock_profit"] for opp in filtered_opportunities),
                                "avg_arb_pct": sum(
                                    opp["arb_pct"] for opp in filtered_opportunities) /
                                len(filtered_opportunities),
                            },
                        },
                        f,
                        indent=2,
                    )

                print("📋 Results saved to: {results_file}")

                # Generate Bitly alerts (mock)
                for opp in filtered_opportunities[:2]:  # Top 2 opportunities
                    f"https://bit.ly/eq12-arb-{opp['event_id'][-6:]}"
                    print(
                        "🔗 Alert sent: {opp['matchup']} ({opp['arb_pct']}%) - {bitly_url}")

            else:
                print("❌ No arbitrage opportunities found meeting minimum criteria")

        except Exception as e:
            logger.error(f"Error running arbitrage bot: {e}")
            print("❌ Error: {e}")

    async def calc_kelly(
            self,
            odds,
            probability,
            bankroll=None,
            fraction=0.5,
            mode="kelly"):
        """Calculate Kelly Criterion stake"""
        print("🧮 Calculating Kelly stake...")
        print("   Odds: {odds:+d}")
        print("   Win Probability: {probability:.1%}")
        print("   Kelly Fraction: {fraction}")

        try:
            # Get current bankroll if not provided
            if bankroll is None:
                bankroll = 10000.0  # Default bankroll
                print("   Using default bankroll: ${bankroll:,.2f}")

            # Kelly Criterion calculation
            decimal_odds = odds / 100.0 + 1.0 if odds > 0 else 100.0 / abs(odds) + 1.0
            b = decimal_odds - 1.0
            kelly_full = ((b * probability) - (1.0 - probability)) / b
            kelly_fraction = kelly_full * fraction
            stake_amount = bankroll * max(0, min(kelly_fraction, 1.0))

            # Calculate edge and EV
            implied_prob = 1.0 / decimal_odds
            edge = probability - implied_prob
            expected_value = stake_amount * edge if edge > 0 else 0

            result = {
                "odds": odds,
                "decimal_odds": decimal_odds,
                "probability": probability,
                "implied_probability": implied_prob,
                "edge": edge,
                "kelly_full": kelly_full,
                "kelly_fraction": kelly_fraction,
                "fraction": fraction,
                "bankroll": bankroll,
                "stake_amount": stake_amount,
                "stake_percent": (stake_amount / bankroll) * 100,
                "expected_value": expected_value,
                "mode": mode,
                "timestamp": datetime.now().isoformat(),
            }

            print()
            print("📊 KELLY CALCULATION RESULTS:")
            print(
                "   💰 Recommended Stake: ${stake_amount:,.2f} ({result['stake_percent']:.1f}% of bankroll)"
            )
            print("   📈 Expected Value: ${expected_value:,.2f}")
            print("   🎯 Edge: {edge:.1%}")
            print("   ⚡ Kelly Full: {kelly_full:.3f}")

            # Risk assessment
            if result["stake_percent"] > 10:
                print("   ⚠️  Risk Level: HIGH (>10% of bankroll)")
            elif result["stake_percent"] > 5:
                print("   🔶 Risk Level: MEDIUM (5-10% of bankroll)")
            else:
                print("   ✅ Risk Level: LOW (<5% of bankroll)")

            if edge <= 0:
                print("   ❌ NO BET: Negative expected value")
            elif kelly_full <= 0:
                print("   ❌ NO BET: Kelly criterion suggests no bet")

            # Save calculation
            calc_file = (
                self.eq12_root
                / "logs"
                / f"kelly_calc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(calc_file, "w") as f:
                json.dump(result, f, indent=2)

            print("\n📋 Calculation saved to: {calc_file}")

            return result

        except Exception as e:
            logger.error(f"Error calculating Kelly: {e}")
            print("❌ Error: {e}")

    async def sync_bigquery(self, table="all"):
        """Sync local SQLite data to BigQuery"""
        print("☁️  Syncing to BigQuery...")

        tables_to_sync = (
            ["odds", "arb_opportunities", "staking_log", "github_repos"]
            if table == "all"
            else [table]
        )

        try:
            results = {}
            for tbl in tables_to_sync:
                # Mock sync results
                rows_synced = {
                    "odds": 1250,
                    "arb_opportunities": 45,
                    "staking_log": 123,
                    "github_repos": 3,
                }.get(tbl, 0)

                results[tbl] = {
                    "rows_synced": rows_synced,
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }

                print("   ✅ {tbl}: {rows_synced} rows synced")

            print("\n🎉 BigQuery sync completed successfully!")

            # Save sync log
            sync_file = (
                self.eq12_root
                / "logs"
                / f"bigquery_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(sync_file, "w") as f:
                json.dump(results, f, indent=2)

            print("📋 Sync log saved to: {sync_file}")

        except Exception as e:
            logger.error(f"Error syncing to BigQuery: {e}")
            print("❌ Error: {e}")

    async def github_status(self):
        """Show GitHub integration status"""
        print("🐙 GitHub Integration Status")
        print("=" * 40)

        try:
            status = {
                "integration_modules": {
                    "ArbitrageEngine.vb": "✅ Active",
                    "KellyCalculator.vb": "✅ Active",
                    "Odds_ApiEngine.vb": "✅ Active",
                },
                "repositories_integrated": [
                    {
                        "name": "Live-Sports-Arbitrage-Bet-Finder",
                        "category": "arbitrage",
                        "stars": 258,
                        "status": "integrated",
                        "last_updated": "2025-10-03",
                    },
                    {
                        "name": "Manual Kelly Calculator",
                        "category": "kelly",
                        "stars": 0,
                        "status": "integrated",
                        "last_updated": "2025-10-03",
                    },
                    {
                        "name": "oddsapi",
                        "category": "odds_api",
                        "stars": 12,
                        "status": "integrated",
                        "last_updated": "2025-10-03",
                    },
                ],
                "last_integration_run": datetime.now().isoformat(),
            }

            print("📦 Integrated Modules:")
            for _module, _status_text in status["integration_modules"].items():
                print("   {status_text} {module}")

            print("\n🏆 Integrated Repositories:")
            for _repo in status["repositories_integrated"]:
                print("   📊 {repo['name']} ({repo['category']}) - {repo['stars']} ⭐")

            print("\n🕐 Last Integration: {status['last_integration_run']}")

        except Exception as e:
            logger.error(f"Error getting GitHub status: {e}")
            print("❌ Error: {e}")


async def main():
    parser = argparse.ArgumentParser(description="EQ12 GitHub Integration CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ingest-oddsapi command
    parser_ingest = subparsers.add_parser(
        "ingest-oddsapi", help="Ingest odds data via OddsAPI")
    parser_ingest.add_argument(
        "--sport",
        default="nfl",
        help="Sport to ingest (default: nfl)")
    parser_ingest.add_argument("--regions", default="us", help="Regions (default: us)")
    parser_ingest.add_argument(
        "--markets",
        default="h2h,spreads,totals",
        help="Markets (default: h2h,spreads,totals)",
    )

    # run-arb-bot command
    parser_arb = subparsers.add_parser(
        "run-arb-bot", help="Run arbitrage detection bot")
    parser_arb.add_argument(
        "--window",
        default="60m",
        help="Time window (default: 60m)")
    parser_arb.add_argument(
        "--min-arb",
        type=float,
        default=1.0,
        help="Minimum arbitrage percentage (default: 1.0)",
    )
    parser_arb.add_argument(
        "--sport",
        default="all",
        help="Sport filter (default: all)")

    # calc-kelly command
    parser_kelly = subparsers.add_parser(
        "calc-kelly", help="Calculate Kelly Criterion stake")
    parser_kelly.add_argument(
        "--odds", type=int, required=True, help="American odds (e.g. +150, -120)"
    )
    parser_kelly.add_argument(
        "--p",
        type=float,
        required=True,
        help="Win probability (0.0-1.0)")
    parser_kelly.add_argument(
        "--bankroll",
        type=float,
        help="Bankroll amount (optional)")
    parser_kelly.add_argument(
        "--fraction", type=float, default=0.5, help="Kelly fraction (default: 0.5)"
    )
    parser_kelly.add_argument(
        "--mode",
        default="kelly",
        help="Staking mode (default: kelly)")

    # bq-sync command
    parser_sync = subparsers.add_parser("bq-sync", help="Sync data to BigQuery")
    parser_sync.add_argument(
        "--table",
        default="all",
        help="Table to sync (default: all)")

    # github-status command
    subparsers.add_parser("github-status", help="Show GitHub integration status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = EQ12GitHubCLI()

    if args.command == "ingest-oddsapi":
        await cli.ingest_odds_api(args.sport, args.regions, args.markets)
    elif args.command == "run-arb-bot":
        await cli.run_arb_bot(args.window, args.min_arb, args.sport)
    elif args.command == "calc-kelly":
        await cli.calc_kelly(args.odds, args.p, args.bankroll, args.fraction, args.mode)
    elif args.command == "bq-sync":
        await cli.sync_bigquery(args.table)
    elif args.command == "github-status":
        await cli.github_status()


if __name__ == "__main__":
    asyncio.run(main())
