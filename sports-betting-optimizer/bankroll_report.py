#!/usr/bin/env python3
"""
EQ12 Bankroll Report CLI - Generate comprehensive bankroll analytics
Usage: python bankroll_report.py [--format json|table] [--days N]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.bankroll_tracker import _last_balance, _read_rows


def load_bankroll_data(
    bankroll_file: str = "../betting-bridge/data/bankroll.csv",
) -> list[dict]:
    """Load and parse bankroll data from CSV"""
    path = Path(bankroll_file).resolve()

    if not path.exists():
        return []

    rows = _read_rows(path)
    if len(rows) <= 1:
        return []

    # Convert to structured data
    data = []
    for row in rows[1:]:  # Skip header
        if len(row) >= 9:
            try:
                entry = {
                    "timestamp": row[0],
                    "id": row[1],
                    "sport": row[2],
                    "stake": float(row[3]) if row[3] else 0.0,
                    "ev": float(row[4]) if row[4] else 0.0,
                    "result": row[5],
                    "balance": float(row[6]) if row[6] else 0.0,
                    "payout": float(row[7]) if row[7] else 0.0,
                    "note": row[8] if len(row) > 8 else "",
                }
                # Calculate profit/loss
                if entry["result"] in ["win", "loss", "push", "void"]:
                    entry["profit_loss"] = entry["payout"] - entry["stake"]
                else:
                    entry["profit_loss"] = 0.0

                data.append(entry)
            except (ValueError, IndexError):
                continue

    return data


def filter_by_days(data: list[dict], days: int) -> list[dict]:
    """Filter data to last N days"""
    if days <= 0:
        return data

    cutoff_date = datetime.now() - timedelta(days=days)
    filtered = []

    for entry in data:
        try:
            entry_date = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
            if entry_date.replace(tzinfo=None) >= cutoff_date:
                filtered.append(entry)
        except ValueError:
            continue

    return filtered


def generate_statistics(data: list[dict]) -> dict:
    """Generate comprehensive statistics from bankroll data"""
    if not data:
        return {}

    # Filter settled bets only
    settled_bets = [bet for bet in data if bet["result"] not in ["pending", "init"]]

    if not settled_bets:
        return {
            "total_entries": len(data),
            "settled_bets": 0,
            "pending_bets": len([b for b in data if b["result"] == "pending"]),
        }

    # Basic counts
    wins = [bet for bet in settled_bets if bet["result"] == "win"]
    losses = [bet for bet in settled_bets if bet["result"] == "loss"]
    pushes = [bet for bet in settled_bets if bet["result"] in ["push", "void"]]

    # Financial calculations
    total_staked = sum(abs(bet["stake"]) for bet in settled_bets)
    total_payout = sum(bet["payout"] for bet in settled_bets)
    total_profit_loss = sum(bet["profit_loss"] for bet in settled_bets)

    # Balance tracking
    starting_balance = 1000.0  # Default
    current_balance = _last_balance([[str(b["balance"]) for b in data[-5:]]], starting_balance)

    # Sport breakdown
    sports_stats = {}
    for bet in settled_bets:
        sport = bet["sport"]
        if sport not in sports_stats:
            sports_stats[sport] = {
                "bets": 0,
                "wins": 0,
                "losses": 0,
                "total_stake": 0.0,
                "total_payout": 0.0,
                "profit_loss": 0.0,
            }

        sports_stats[sport]["bets"] += 1
        sports_stats[sport]["total_stake"] += bet["stake"]
        sports_stats[sport]["total_payout"] += bet["payout"]
        sports_stats[sport]["profit_loss"] += bet["profit_loss"]

        if bet["result"] == "win":
            sports_stats[sport]["wins"] += 1
        elif bet["result"] == "loss":
            sports_stats[sport]["losses"] += 1

    # Calculate win rates and ROIs
    for sport_data in sports_stats.values():
        if sport_data["bets"] > 0:
            sport_data["win_rate"] = (sport_data["wins"] / sport_data["bets"]) * 100
        if sport_data["total_stake"] > 0:
            sport_data["roi"] = (sport_data["profit_loss"] / sport_data["total_stake"]) * 100

    return {
        "total_entries": len(data),
        "settled_bets": len(settled_bets),
        "pending_bets": len([b for b in data if b["result"] == "pending"]),
        "wins": len(wins),
        "losses": len(losses),
        "pushes": len(pushes),
        "win_rate": (len(wins) / len(settled_bets) * 100) if settled_bets else 0,
        "total_staked": total_staked,
        "total_payout": total_payout,
        "total_profit_loss": total_profit_loss,
        "roi": (total_profit_loss / total_staked * 100) if total_staked > 0 else 0,
        "starting_balance": starting_balance,
        "current_balance": current_balance,
        "net_change": current_balance - starting_balance,
        "sports_breakdown": sports_stats,
        "avg_stake": total_staked / len(settled_bets) if settled_bets else 0,
        "avg_profit_per_bet": (total_profit_loss / len(settled_bets) if settled_bets else 0),
    }


def format_table_report(stats: dict, data: list[dict]) -> str:
    """Format statistics as a readable table"""
    if not stats:
        return "📭 No data available"

    report = []
    report.append("🎯 EQ12 BANKROLL REPORT")
    report.append("=" * 50)

    # Overall stats
    report.append("\n📊 OVERALL STATISTICS")
    report.append(f"Current Balance:    ${stats['current_balance']:,.2f}")
    report.append(f"Starting Balance:   ${stats['starting_balance']:,.2f}")
    report.append(f"Net Change:         ${stats['net_change']:+,.2f}")
    report.append(f"Total P/L:          ${stats['total_profit_loss']:+,.2f}")
    report.append(f"ROI:                {stats['roi']:+.2f}%")

    # Betting activity
    report.append("\n🎲 BETTING ACTIVITY")
    report.append(f"Total Bets:         {stats['settled_bets']}")
    report.append(f"Wins:               {stats['wins']} ({stats['win_rate']:.1f}%)")
    report.append(f"Losses:             {stats['losses']}")
    report.append(f"Pushes/Voids:       {stats['pushes']}")
    report.append(f"Pending:            {stats['pending_bets']}")

    # Financial metrics
    report.append("\n💰 FINANCIAL METRICS")
    report.append(f"Total Staked:       ${stats['total_staked']:,.2f}")
    report.append(f"Total Payout:       ${stats['total_payout']:,.2f}")
    report.append(f"Average Stake:      ${stats['avg_stake']:,.2f}")
    report.append(f"Avg P/L per Bet:    ${stats['avg_profit_per_bet']:+,.2f}")

    # Sports breakdown
    if stats["sports_breakdown"]:
        report.append("\n🏈 SPORTS BREAKDOWN")
        report.append("-" * 70)
        report.append(
            f"{'Sport':<12} {'Bets':<6} {'Wins':<6} {'Rate':<8} {'Staked':<12} {'P/L':<12} {'ROI':<8}"
        )
        report.append("-" * 70)

        for sport, sport_stats in stats["sports_breakdown"].items():
            report.append(
                f"{sport:<12} {sport_stats['bets']:<6} {sport_stats['wins']:<6} "
                f"{sport_stats.get('win_rate', 0):<7.1f}% "
                f"${sport_stats['total_stake']:<11,.2f} "
                f"${sport_stats['profit_loss']:<+11.2f} "
                f"{sport_stats.get('roi', 0):<+7.1f}%"
            )

    # Recent activity
    recent_bets = [bet for bet in data if bet["result"] != "init"][-10:]
    if recent_bets:
        report.append(f"\n📈 RECENT ACTIVITY (Last {len(recent_bets)} bets)")
        report.append("-" * 70)
        for bet in recent_bets:
            timestamp = bet["timestamp"][:10]  # Date only
            result_emoji = (
                "✅" if bet["result"] == "win" else "❌" if bet["result"] == "loss" else "⏳"
            )
            report.append(
                f"{timestamp} {result_emoji} {bet['id']:<12} {bet['sport']:<8} "
                f"${bet['stake']:>7.2f} → ${bet['profit_loss']:>+8.2f}"
            )

    return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description="EQ12 Bankroll Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bankroll_report.py                    # Full report as table
  python bankroll_report.py --format json     # JSON output
  python bankroll_report.py --days 7          # Last 7 days only
  python bankroll_report.py --days 30 --format json  # Last 30 days as JSON
        """,
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--days", "-d", type=int, default=0, help="Filter to last N days (0 = all time)"
    )
    parser.add_argument(
        "--file",
        type=str,
        default="../betting-bridge/data/bankroll.csv",
        help="Bankroll CSV file path",
    )
    parser.add_argument("--output", "-o", type=str, help="Save output to file")

    args = parser.parse_args()

    # Load data
    try:
        data = load_bankroll_data(args.file)

        if args.days > 0:
            data = filter_by_days(data, args.days)

        stats = generate_statistics(data)

        # Format output
        if args.format == "json":
            output = json.dumps(
                {
                    "report_generated": datetime.now().isoformat(),
                    "filter_days": args.days if args.days > 0 else "all_time",
                    "statistics": stats,
                    "recent_bets": data[-20:] if data else [],
                },
                indent=2,
                default=str,
            )
        else:
            output = format_table_report(stats, data)

        # Output results
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"📁 Report saved to: {args.output}")
        else:
            print(output)

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
