#!/usr/bin/env python3
"""
EQ12 Production Launcher
Main entry point for the complete EQ12 stack.

Usage:
    python eq12_main.py --status          # Show system status
    python eq12_main.py --start-edge      # Start EdgeFinder service
    python eq12_main.py --demo            # Run demo mode
    python eq12_main.py --build-parlay    # Interactive parlay builder
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from eq12_edgefinder import EdgeFinderConfig, EdgeFinderService
    from eq12_parlay_builder import ParlayBuilder
    from eq12_status import EQ12StatusMonitor
    from eq12_timezone import utc_now

    from eq12_math import expected_value_percentage, kelly_fraction
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all EQ12 modules are in the scripts/ directory")
    sys.exit(1)


class EQ12Launcher:
    """Main launcher for EQ12 production stack."""

    def __init__(self):
        self.status_monitor = EQ12StatusMonitor()
        print("🚀 EQ12 Production Stack Launcher")
        print("=" * 50)

    def show_status(self):
        """Display system status."""
        report = self.status_monitor.generate_status_report()
        print(report)

        # Save snapshot
        self.status_monitor.save_status_snapshot()

    async def start_edgefinder(self):
        """Start the EdgeFinder service."""
        try:
            print("🔍 Starting EdgeFinder service...")
            config = EdgeFinderConfig()
            service = EdgeFinderService(config)

            print("✅ EdgeFinder initialized successfully")
            print("🎯 Monitoring DraftKings, FanDuel, BetMGM")
            print("📊 Building parlays with AI optimization")
            print()
            print("Press Ctrl+C to stop")

            await service.start_daemon()

        except KeyboardInterrupt:
            print("\n👋 EdgeFinder stopped by user")
        except Exception as e:
            print(f"❌ EdgeFinder failed: {e}")

    def demo_mode(self):
        """Run demo mode with sample data."""
        print("🎯 EQ12 Demo Mode")
        print("=" * 30)

        # Demo parlay building
        builder = ParlayBuilder(bankroll=1000.0)

        # Sample legs (normally from EdgeFinder)
        sample_legs = [
            {
                "game_id": "nfl_demo_chiefs_bills",
                "book": "draftkings",
                "market": "moneyline",
                "selection": "Kansas City Chiefs",
                "odds": -110,
                "model_prob": 0.55,
                "ev": expected_value_percentage(0.55, -110),
                "kelly": kelly_fraction(0.55, -110, kelly_cut=0.5),
                "commence_time": utc_now().isoformat(),
                "hook_flag": False,
            },
            {
                "game_id": "nfl_demo_packers_bears",
                "book": "fanduel",
                "market": "spread",
                "selection": "Green Bay Packers -3.5",
                "odds": -105,
                "point": -3.5,
                "model_prob": 0.53,
                "ev": expected_value_percentage(0.53, -105),
                "kelly": kelly_fraction(0.53, -105, kelly_cut=0.5),
                "commence_time": utc_now().isoformat(),
                "hook_flag": True,
            },
            {
                "game_id": "nfl_demo_cowboys_giants",
                "book": "betmgm",
                "market": "total",
                "selection": "Over 47.5",
                "odds": +100,
                "point": 47.5,
                "model_prob": 0.52,
                "ev": expected_value_percentage(0.52, +100),
                "kelly": kelly_fraction(0.52, +100, kelly_cut=0.5),
                "commence_time": utc_now().isoformat(),
                "hook_flag": True,
            },
        ]

        print(f"📊 Sample legs: {len(sample_legs)}")
        print()

        # Build parlays
        strategies = ["balanced", "conservative", "yolo"]
        parlays = builder.build_all_strategies(sample_legs, strategies)

        print(f"🎰 Built {len(parlays)} parlays:")
        print()

        for parlay in parlays:
            ev_pct = (parlay.expected_value_dollars / parlay.stake_dollars) * 100
            print(f"Strategy: {parlay.strategy}")
            print(f"  Legs: {len(parlay.legs)}")
            print(f"  Odds: {parlay.combined_odds:+d}")
            print(f"  Stake: ${parlay.stake_dollars:.0f}")
            print(f"  EV: {ev_pct:+.1f}% (${parlay.expected_value_dollars:+.2f})")
            print(f"  Risk: {parlay.risk_level}")
            print()

        print("✅ Demo completed successfully!")
        print("💡 Run with --start-edge to start live monitoring")

    def interactive_parlay_builder(self):
        """Interactive parlay building interface."""
        print("🎰 Interactive Parlay Builder")
        print("=" * 35)
        print()

        try:
            # Get user inputs
            bankroll = float(input("Enter bankroll ($): ") or "1000")

            print("\nEnter leg details (press Enter with empty odds to finish):")
            legs = []

            while True:
                print(f"\nLeg {len(legs) + 1}:")
                odds = input("  American odds (e.g., -110, +150): ").strip()

                if not odds:
                    break

                try:
                    odds_value = int(odds)
                    prob = float(input("  Model probability (0.0-1.0): ") or "0.5")
                    selection = (
                        input("  Selection (e.g., 'Chiefs ML'): ") or f"Selection {
                            len(legs) + 1}")

                    leg = {
                        "game_id": f"manual_{len(legs)}",
                        "book": "manual",
                        "market": "manual",
                        "selection": selection,
                        "odds": odds_value,
                        "model_prob": prob,
                        "ev": expected_value_percentage(prob, odds_value),
                        "kelly": kelly_fraction(prob, odds_value, kelly_cut=0.5),
                        "commence_time": utc_now().isoformat(),
                        "hook_flag": False,
                    }

                    legs.append(leg)
                    print(
                        f"  ✅ Added: {selection} @ {odds_value:+d} (EV: {leg['ev']:+.1%})")

                except ValueError:
                    print("  ❌ Invalid input, skipping leg")

            if len(legs) < 2:
                print("❌ Need at least 2 legs for parlays")
                return

            # Build parlays
            builder = ParlayBuilder(bankroll=bankroll)
            strategies = ["balanced", "conservative", "yolo"]
            parlays = builder.build_all_strategies(legs, strategies)

            print(f"\n🎰 Built {len(parlays)} parlays:")
            print()

            for parlay in parlays:
                ev_pct = (parlay.expected_value_dollars / parlay.stake_dollars) * 100
                print(
                    f"{parlay.strategy.title()}: {len(parlay.legs)} legs @ {parlay.combined_odds:+d}"
                )
                print(
                    f"  Stake: ${
                        parlay.stake_dollars:.0f} → EV: {
                        ev_pct:+.1f}% (${
                        parlay.expected_value_dollars:+.2f})")
                print()

        except KeyboardInterrupt:
            print("\n👋 Builder cancelled")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="EQ12 Production Stack Launcher")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="Show system status")
    group.add_argument(
        "--start-edge",
        action="store_true",
        help="Start EdgeFinder service")
    group.add_argument("--demo", action="store_true", help="Run demo mode")
    group.add_argument(
        "--build-parlay",
        action="store_true",
        help="Interactive parlay builder")

    args = parser.parse_args()
    launcher = EQ12Launcher()

    try:
        if args.status:
            launcher.show_status()

        elif args.start_edge:
            asyncio.run(launcher.start_edgefinder())

        elif args.demo:
            launcher.demo_mode()

        elif args.build_parlay:
            launcher.interactive_parlay_builder()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
