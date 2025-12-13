#!/usr/bin/env python3
"""
EQ12 Kelly Calculator CLI - Interactive Kelly Criterion calculator
Usage: python kelly_calculator.py [bankroll] [odds] [ev_percentage]
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.core.bankroll_tracker_clean import _last_balance, _read_rows
    from src.utils.kelly_criterion import KellyCriterion, create_kelly_report

    KELLY_AVAILABLE = True
except ImportError as e:
    print(f"❌ Kelly calculator not available: {e}")
    KELLY_AVAILABLE = False


def get_current_bankroll(
    bankroll_file: str = "../betting-bridge/data/bankroll.csv",
) -> float:
    """Get current bankroll from CSV file"""
    try:
        path = Path(bankroll_file).resolve()
        if not path.exists():
            return 1000.0  # Default

        rows = _read_rows(path)
        return _last_balance(rows, 1000.0)
    except Exception:
        return 1000.0


def interactive_kelly():
    """Interactive Kelly calculator mode"""
    print("🧮 EQ12 Interactive Kelly Calculator")
    print("=" * 45)

    # Get current bankroll
    current_bankroll = get_current_bankroll()
    print(f"💰 Current Bankroll: ${current_bankroll:,.2f}")

    while True:
        print("\nEnter bet details (or 'quit' to exit):")

        # Get bankroll (allow override)
        bankroll_input = input(f"Bankroll [${current_bankroll:,.2f}]: ").strip()
        if bankroll_input.lower() in ["quit", "exit", "q"]:
            break

        try:
            bankroll = float(bankroll_input) if bankroll_input else current_bankroll
        except ValueError:
            print("❌ Invalid bankroll amount")
            continue

        # Get decimal odds
        try:
            odds_input = input("Decimal odds (e.g., 2.1 for +110): ").strip()
            if not odds_input:
                continue
            decimal_odds = float(odds_input)
            if decimal_odds <= 1.0:
                print("❌ Odds must be greater than 1.0")
                continue
        except ValueError:
            print("❌ Invalid odds format")
            continue

        # Get expected value
        try:
            ev_input = input("Expected Value % (e.g., 4.2 for 4.2%): ").strip()
            if not ev_input:
                continue
            ev_percentage = float(ev_input)
        except ValueError:
            print("❌ Invalid EV format")
            continue

        # Optional confidence adjustment
        try:
            confidence_input = input("Confidence level [1.0]: ").strip()
            confidence = float(confidence_input) if confidence_input else 1.0
            confidence = max(0.1, min(1.0, confidence))  # Clamp between 0.1 and 1.0
        except ValueError:
            confidence = 1.0

        # Calculate Kelly stake
        try:
            calculator = KellyCriterion(bankroll)
            result = calculator.calculate_ev_kelly_stake(decimal_odds, ev_percentage)

            # Apply confidence adjustment
            if confidence < 1.0:
                result["recommended_stake"] *= confidence
                result["stake_as_bankroll_pct"] *= confidence

            print("\n" + create_kelly_report(result))

            if confidence < 1.0:
                print(f"\n🔻 Confidence Adjusted: {confidence:.1%}")
                print(f"   Final Recommendation: ${result['recommended_stake']:.2f}")

            # Quick recommendation
            stake, reason = calculator.get_stake_recommendation(
                decimal_odds, ev_percentage, confidence
            )
            print(f"\n💡 Quick Recommendation: ${stake:.2f}")
            print(f"   Reason: {reason}")

        except Exception as e:
            print(f"❌ Calculation error: {e}")


def calculate_single_bet(bankroll: float, odds: float, ev_pct: float) -> None:
    """Calculate Kelly for a single bet non-interactively"""
    try:
        calculator = KellyCriterion(bankroll)
        result = calculator.calculate_ev_kelly_stake(odds, ev_pct)

        print(create_kelly_report(result))

        stake, reason = calculator.get_stake_recommendation(odds, ev_pct)
        print(f"\n💡 Recommendation: ${stake:.2f} - {reason}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def test_kelly_scenarios():
    """Test various Kelly scenarios"""
    print("🧪 Kelly Calculator Test Scenarios")
    print("=" * 40)

    scenarios = [
        {"name": "NFL Moneyline +EV", "bankroll": 1000, "odds": 2.1, "ev": 4.2},
        {"name": "NBA Spread Low EV", "bankroll": 1000, "odds": 1.91, "ev": 1.5},
        {"name": "High EV Boost", "bankroll": 1000, "odds": 3.5, "ev": 12.0},
        {"name": "Small Bankroll", "bankroll": 100, "odds": 2.0, "ev": 3.0},
        {"name": "Large Bankroll", "bankroll": 10000, "odds": 1.95, "ev": 2.5},
        {"name": "Negative EV", "bankroll": 1000, "odds": 1.85, "ev": -2.0},
    ]

    calculator = KellyCriterion(bankroll=1000)

    for scenario in scenarios:
        print(f"\n📊 {scenario['name']}")
        print("-" * 30)

        try:
            # Update bankroll for this scenario
            calculator.bankroll = scenario["bankroll"]

            result = calculator.calculate_ev_kelly_stake(scenario["odds"], scenario["ev"])

            stake, reason = calculator.get_stake_recommendation(scenario["odds"], scenario["ev"])

            print(f"Bankroll: ${scenario['bankroll']:,.2f}")
            print(f"Odds: {scenario['odds']:.2f}")
            print(f"EV: {scenario['ev']:+.1f}%")
            print(f"Kelly %: {result['adjusted_kelly_percentage']:.2f}%")
            print(f"Stake: ${stake:.2f}")
            print(f"Risk: {result['risk_level']}")
            print(f"Reason: {reason}")

        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    if not KELLY_AVAILABLE:
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="EQ12 Kelly Criterion Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python kelly_calculator.py                    # Interactive mode
  python kelly_calculator.py 1000 2.1 4.2     # Single calculation
  python kelly_calculator.py --test            # Test scenarios
        """,
    )

    parser.add_argument("bankroll", nargs="?", type=float, help="Current bankroll amount")
    parser.add_argument("odds", nargs="?", type=float, help="Decimal odds (e.g., 2.1)")
    parser.add_argument("ev_percentage", nargs="?", type=float, help="Expected value percentage")
    parser.add_argument("--test", "-t", action="store_true", help="Run test scenarios")
    parser.add_argument("--interactive", "-i", action="store_true", help="Force interactive mode")

    args = parser.parse_args()

    # Test scenarios
    if args.test:
        test_kelly_scenarios()
        return

    # Single calculation
    if args.bankroll and args.odds and args.ev_percentage is not None:
        calculate_single_bet(args.bankroll, args.odds, args.ev_percentage)
        return

    # Interactive mode (default)
    interactive_kelly()
    print("👋 Goodbye!")


if __name__ == "__main__":
    main()
