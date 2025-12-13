#!/usr/bin/env python3
"""
EQ12 CLI Runner & Examples
==========================

Command-line interface and example usage for the EQ12 system.
Demonstrates all runbook queries with real examples you can run.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from eq12_api_client import BookMaker, Market, create_client
from eq12_scheduler import EQ12Scheduler


def setup_logging():
    """Setup logging for CLI usage"""
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_json(data, title: str | None = None):
    """Print formatted JSON output"""
    if title:
        print(f"\n📊 {title}:")
    print(json.dumps(data, indent=2, default=str))


async def run_health_checks(client):
    """Run all health check functions from runbook"""
    print_section("INGEST & HEALTH (PRE-FLIGHT)")

    # API heartbeat
    print("\n🔍 API Heartbeat & Quota Check...")
    heartbeat = client.heartbeat()
    print_json(heartbeat, "Heartbeat Result")

    # Clock sanity check
    print("\n⏰ Clock Sanity Check...")
    clock_check = client.clock_sanity_check()
    print_json(clock_check, "Clock Check Result")

    # Book availability snapshot
    print("\n📚 Book Availability Snapshot (DK/FD/BetMGM)...")
    availability = client.book_availability_snapshot()
    print_json(availability, "Book Availability")


async def run_core_market_pulls(client):
    """Run core market pull functions"""
    print_section("CORE MARKET PULLS (GAME ODDS)")

    # Today + next 24h slate
    print("\n📅 Getting 24h Slate...")
    games_24h = client.get_24h_slate()
    print(f"Found {len(games_24h)} games in next 24 hours")

    if games_24h:
        sample_game = games_24h[0]
        print(f"Sample: {sample_game.away_team} @ {sample_game.home_team}")
        print(f"Kickoff: {sample_game.commence_time}")

    # Steaming window
    print("\n🔥 Getting Steaming Window (≤60m to kickoff)...")
    steaming_games = client.get_steaming_window()
    print(f"Found {len(steaming_games)} games in steaming window")

    # Line movement polling (demonstration)
    print("\n📈 Line Movement Polling Demo...")
    print("(In production, this runs every 30-60s with diff detection)")


async def run_targeted_hunting(client):
    """Run targeted market value hunting"""
    print_section("TARGETED MARKET PULLS (VALUE HUNTING)")

    # Moneylines only
    print("\n💰 Hunting Moneylines...")
    moneylines = client.get_moneylines_only()
    print(f"Found {len(moneylines)} moneyline opportunities")

    # Spreads with hooks
    print("\n🎣 Hunting Spread Hooks...")
    spread_hooks = client.get_spreads_with_hooks()
    print(f"Found {len(spread_hooks)} spread hook opportunities")
    print(f"Key numbers: {client.SPREAD_HOOKS}")

    # Totals with hooks
    print("\n🎯 Hunting Total Hooks...")
    total_hooks = client.get_totals_with_hooks()
    print(f"Found {len(total_hooks)} total hook opportunities")
    print(f"Key numbers: {client.TOTAL_HOOKS}")


async def run_parlay_builders(client):
    """Demonstrate parlay builders for each book"""
    print_section("PARLAY BUILDERS (BOOK-SPECIFIC)")

    for book in BookMaker:
        print(f"\n🎰 Building Parlays for {book.value.upper()}...")

        # Balanced risk parlay
        print("  📊 Balanced Risk Parlay...")
        balanced = client.build_balanced_risk_parlay(book)
        if "error" not in balanced:
            print(f"     Legs: {balanced.get('leg_count', 0)}")
            print(f"     Odds: {balanced.get('combined_odds', 'N/A')}")

        # Conservative high-EV parlay
        print("  🛡️  Conservative High-EV Parlay...")
        conservative = client.build_conservative_high_ev_parlay(book)
        if "error" not in conservative:
            print(f"     Legs: {conservative.get('leg_count', 0)}")
            print(f"     Avg EV: {conservative.get('total_edge_percent', 0):.2f}%")

        # Spreads only
        print("  📏 Spreads-Only Parlay...")
        spreads_only = client.build_spreads_only_parlay(book)
        if "error" not in spreads_only:
            print(f"     Legs: {spreads_only.get('leg_count', 0)}")

        # Totals only
        print("  🎯 Totals-Only Parlay...")
        totals_only = client.build_totals_only_parlay(book)
        if "error" not in totals_only:
            print(f"     Legs: {totals_only.get('leg_count', 0)}")


async def run_settlement_demo(client):
    """Demonstrate settlement and results functions"""
    print_section("RESULTS & SETTLEMENT")

    print("\n🏆 Getting Scores for Settlement...")
    scores = client.get_scores_for_settlement(days_back=2)

    if "error" not in scores:
        print(f"Found {scores.get('games_count', 0)} completed games")
        print("(Settlement grading and CLV calculation would happen here)")
    else:
        print(f"Error: {scores['error']}")


async def demo_scheduler_config():
    """Demonstrate scheduler configuration"""
    print_section("SCHEDULER CONFIGURATION DEMO")

    config_path = "C:/EQ12/configs/eq12_scheduler_config.yaml"

    print(f"\n⚙️  Creating scheduler with config: {config_path}")

    try:
        scheduler = EQ12Scheduler(config_path)
        status = scheduler.get_status()
        print_json(status, "Scheduler Status")

        print("\n📋 Job Summary:")
        for job_name, job in scheduler.jobs.items():
            enabled = "✅" if job.enabled else "❌"
            print(f"  {enabled} {job_name:<30} {job.interval_seconds:>3}s - {job.description}")

        print(
            f"\n🔄 Scheduler would run {len([j for j in scheduler.jobs.values() if j.enabled])} jobs"
        )
        print("   Use 'python eq12_cli.py --run-scheduler' to start")

    except Exception as e:
        print(f"❌ Scheduler demo failed: {e}")


async def run_full_demo():
    """Run complete demonstration of all runbook features"""
    print("🚀 EQ12 COMPLETE RUNBOOK DEMONSTRATION")
    print("=====================================")
    print("This demo runs through all query types from the tight runbook.")
    print("Scoped to DraftKings, FanDuel, BetMGM only.")

    try:
        # Initialize client
        print("\n🔧 Initializing API Client...")
        client = create_client()
        print("✅ Client initialized")

        # Run all demo sections
        await run_health_checks(client)
        await run_core_market_pulls(client)
        await run_targeted_hunting(client)
        await run_parlay_builders(client)
        await run_settlement_demo(client)
        await demo_scheduler_config()

        print_section("DEMO COMPLETE")
        print("✅ All runbook query types demonstrated")
        print("📖 See eq12_api_client.py and eq12_scheduler.py for full implementation")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1

    return 0


async def run_scheduler():
    """Run the full scheduler"""
    print("🚀 Starting EQ12 Production Scheduler...")
    print("=======================================")

    config_path = "C:/EQ12/configs/eq12_scheduler_config.yaml"

    try:
        scheduler = EQ12Scheduler(config_path)
        print("✅ Scheduler initialized")

        print("\n📊 Job Configuration:")
        for job_name, job in scheduler.jobs.items():
            if job.enabled:
                print(f"  ▶️  {job_name:<30} every {job.interval_seconds:>3}s")
            else:
                print(f"  ⏸️  {job_name:<30} (disabled)")

        print(
            f"\n🔄 Starting {len([j for j in scheduler.jobs.values() if j.enabled])} job loops..."
        )
        print("Press Ctrl+C to stop")

        await scheduler.start()

    except KeyboardInterrupt:
        print("\n🛑 Scheduler stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Scheduler failed: {e}")
        return 1


def create_example_config():
    """Create example configuration files"""
    print("📝 Creating Example Configuration Files...")

    # Create directories
    Path("C:/EQ12/configs").mkdir(parents=True, exist_ok=True)
    Path("C:/EQ12/logs").mkdir(parents=True, exist_ok=True)

    # Example model probabilities (placeholder)
    model_probs = {
        "game1_h2h_Team A_None": 0.55,
        "game1_spreads_Team A_-3.5": 0.52,
        "game1_totals_Over_47.5": 0.51,
        # Add more examples...
    }

    with open("C:/EQ12/configs/example_model_probabilities.json", "w") as f:
        json.dump(model_probs, f, indent=2)

    # Example betting limits
    limits = {
        "draftkings": {"max_parlay_legs": 20, "max_stake": 500},
        "fanduel": {"max_parlay_legs": 15, "max_stake": 300},
        "betmgm": {"max_parlay_legs": 12, "max_stake": 200},
    }

    with open("C:/EQ12/configs/betting_limits.json", "w") as f:
        json.dump(limits, f, indent=2)

    print("✅ Example configurations created in C:/EQ12/configs/")


def main():
    """Main CLI entry point"""
    setup_logging()

    parser = argparse.ArgumentParser(
        description="EQ12 NFL Betting System - Tight Runbook Implementation"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run complete demonstration of all runbook features",
    )

    parser.add_argument(
        "--run-scheduler",
        action="store_true",
        help="Start the production scheduler with all jobs",
    )

    parser.add_argument("--health-check", action="store_true", help="Run API health checks only")

    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create example configuration files",
    )

    parser.add_argument(
        "--book",
        choices=[b.value for b in BookMaker],
        help="Target specific bookmaker for operations",
    )

    parser.add_argument(
        "--market",
        choices=[m.value for m in Market],
        help="Target specific market for operations",
    )

    args = parser.parse_args()

    if args.create_config:
        create_example_config()
        return 0

    if args.run_scheduler:
        return asyncio.run(run_scheduler())

    if args.health_check:

        async def health_only():
            client = create_client()
            await run_health_checks(client)

        return asyncio.run(health_only())

    if args.demo:
        return asyncio.run(run_full_demo())

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
