#!/usr/bin/env python3
"""
EQ12 Bankroll Settlement CLI - Interactive bet settlement tool
Usage: python bankroll_settle.py [bet_id] [result] [payout]
"""

import argparse
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.bankroll_tracker import _read_rows, settle_slip


def interactive_settlement():
    """Interactive mode for settling bets"""
    print("🎰 EQ12 Interactive Bet Settlement")
    print("=" * 40)

    while True:
        print("\nEnter bet details (or 'quit' to exit):")

        # Get bet ID
        bet_id = input("Bet ID: ").strip()
        if bet_id.lower() in ["quit", "exit", "q"]:
            break

        # Get result
        print("Result options: win, loss, push, void")
        result = input("Result: ").strip().lower()
        if result not in ["win", "loss", "push", "void"]:
            print("❌ Invalid result. Use: win, loss, push, void")
            continue

        # Get payout
        try:
            payout_str = input("Payout amount: $").strip()
            payout = float(payout_str)
        except ValueError:
            print("❌ Invalid payout amount")
            continue

        # Optional note
        note = input("Note (optional): ").strip()

        try:
            # Settle the bet
            bankroll_file, new_balance = settle_slip(
                bet_id=bet_id, result=result, payout=payout, note=note
            )

            print(f"✅ Bet {bet_id} settled successfully!")
            print(f"💰 New balance: ${new_balance:.2f}")
            print(f"📄 Updated: {bankroll_file}")

        except Exception as e:
            print(f"❌ Error settling bet: {e}")


def settle_single_bet(bet_id: str, result: str, payout: float, note: str = ""):
    """Settle a single bet non-interactively"""
    try:
        _bankroll_file, new_balance = settle_slip(
            bet_id=bet_id, result=result, payout=payout, note=note
        )

        print(f"✅ Bet {bet_id} settled: {result}")
        print(f"💰 Payout: ${payout:.2f}")
        print(f"💵 New balance: ${new_balance:.2f}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def show_pending_bets():
    """Show all pending bets"""
    bankroll_file = Path("../betting-bridge/data/bankroll.csv").resolve()

    if not bankroll_file.exists():
        print("❌ No bankroll file found")
        return

    try:
        rows = _read_rows(bankroll_file)
        if len(rows) <= 1:
            print("📭 No bets found")
            return

        # Find pending bets
        pending_bets = []
        for i, row in enumerate(rows[1:], 1):  # Skip header
            if len(row) >= 6 and row[5] == "pending":
                pending_bets.append(
                    {
                        "row": i,
                        "id": row[1],
                        "sport": row[2],
                        "stake": row[3],
                        "ev": row[4],
                    }
                )

        if not pending_bets:
            print("📭 No pending bets found")
            return

        print(f"\n🎲 Pending Bets ({len(pending_bets)}):")
        print("-" * 60)
        for bet in pending_bets:
            print(
                f"ID: {bet['id']:15} Sport: {bet['sport']:8} "
                f"Stake: ${float(bet['stake']):8.2f} EV: {bet['ev']:6}%"
            )

    except Exception as e:
        print(f"❌ Error reading pending bets: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="EQ12 Bankroll Settlement CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bankroll_settle.py                     # Interactive mode
  python bankroll_settle.py --pending          # Show pending bets
  python bankroll_settle.py bet123 win 150.50  # Settle specific bet
  python bankroll_settle.py bet456 loss 0      # Settle loss
        """,
    )

    parser.add_argument("bet_id", nargs="?", help="Bet ID to settle")
    parser.add_argument(
        "result", nargs="?", choices=["win", "loss", "push", "void"], help="Bet result"
    )
    parser.add_argument("payout", nargs="?", type=float, help="Payout amount")
    parser.add_argument("--note", "-n", default="", help="Optional settlement note")
    parser.add_argument("--pending", "-p", action="store_true", help="Show pending bets")
    parser.add_argument("--interactive", "-i", action="store_true", help="Force interactive mode")

    args = parser.parse_args()

    # Show pending bets
    if args.pending:
        show_pending_bets()
        return

    # Single bet settlement
    if args.bet_id and args.result and args.payout is not None:
        success = settle_single_bet(args.bet_id, args.result, args.payout, args.note)
        sys.exit(0 if success else 1)

    # Interactive mode (default or explicit)
    if args.interactive or not args.bet_id:
        show_pending_bets()
        interactive_settlement()
        print("👋 Goodbye!")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
