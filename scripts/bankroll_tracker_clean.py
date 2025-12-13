#!/usr/bin/env python3
"""
Clean Bankroll Tracker for EQ12 System
Professional bankroll management and tracking
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BankrollTracker:
    """
    Professional bankroll tracking and management system
    """

    def __init__(
        self,
        csv_file: str = "C:/EQ12/data/bankroll_history.csv",
        initial_bankroll: float = 1000.0,
    ):
        """
        Initialize bankroll tracker

        Args:
            csv_file: Path to CSV file for tracking
            initial_bankroll: Starting bankroll amount
        """
        self.csv_file = Path(csv_file)
        self.csv_file.parent.mkdir(parents=True, exist_ok=True)
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll

        # Initialize CSV if it doesn't exist
        if not self.csv_file.exists():
            self._initialize_csv()
        else:
            self._load_current_bankroll()

    def _initialize_csv(self) -> None:
        """Initialize CSV file with headers"""
        try:
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "balance",
                        "bet_amount",
                        "outcome",
                        "profit_loss",
                        "notes",
                    ]
                )

                # Write initial balance
                writer.writerow(
                    [
                        datetime.now().isoformat(),
                        self.initial_bankroll,
                        0.0,
                        "initial",
                        0.0,
                        "Starting bankroll",
                    ]
                )
            logger.info(f"Initialized bankroll tracking: {self.csv_file}")

        except Exception as e:
            logger.error(f"Failed to initialize CSV: {e}")

    def _load_current_bankroll(self) -> None:
        """Load current bankroll from last CSV entry"""
        try:
            with open(self.csv_file, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                if rows:
                    self.current_bankroll = float(rows[-1]["balance"])
                    logger.info(
                        f"Loaded current bankroll: ${
                            self.current_bankroll:.2f}")

        except Exception as e:
            logger.error(f"Failed to load bankroll: {e}")
            self.current_bankroll = self.initial_bankroll

    def record_bet(
        self, bet_amount: float, outcome: str, profit_loss: float, notes: str = ""
    ) -> None:
        """
        Record a bet outcome and update bankroll

        Args:
            bet_amount: Amount wagered
            outcome: 'win' or 'loss' or 'push'
            profit_loss: Net profit or loss amount
            notes: Optional notes about the bet
        """
        # Update current bankroll
        self.current_bankroll += profit_loss

        # Record in CSV
        try:
            with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        datetime.now().isoformat(),
                        round(self.current_bankroll, 2),
                        bet_amount,
                        outcome,
                        profit_loss,
                        notes,
                    ]
                )

            logger.info(
                f"Recorded {outcome}: ${profit_loss:+.2f}, "
                f"New balance: ${self.current_bankroll:.2f}"
            )

        except Exception as e:
            logger.error(f"Failed to record bet: {e}")

    def get_bankroll_stats(self) -> dict:
        """
        Get comprehensive bankroll statistics

        Returns:
            Dictionary with performance metrics
        """
        try:
            with open(self.csv_file, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                return {"error": "No data available"}

            # Calculate statistics
            balances = [float(row["balance"]) for row in rows]
            profits = [float(row["profit_loss"])
                       for row in rows if row["outcome"] in ["win", "loss"]]

            wins = [p for p in profits if p > 0]
            losses = [p for p in profits if p < 0]

            total_profit = sum(profits)
            total_bets = len([row for row in rows if row["outcome"] != "initial"])
            win_rate = (len(wins) / len(profits) * 100) if profits else 0

            # Max drawdown calculation
            peak = balances[0]
            max_drawdown = 0
            for balance in balances:
                if balance > peak:
                    peak = balance
                drawdown = (peak - balance) / peak
                max_drawdown = max(max_drawdown, drawdown)

            return {
                "current_balance": self.current_bankroll,
                "initial_balance": self.initial_bankroll,
                "total_profit": round(total_profit, 2),
                "total_bets": total_bets,
                "win_rate": round(win_rate, 1),
                "roi": round((total_profit / self.initial_bankroll) * 100, 2),
                "max_drawdown": round(max_drawdown * 100, 2),
                "average_win": round(sum(wins) / len(wins), 2) if wins else 0,
                "average_loss": round(sum(losses) / len(losses), 2) if losses else 0,
                "profit_factor": ((sum(wins) / abs(sum(losses))) if losses else float("inf")),
            }

        except Exception as e:
            logger.error(f"Failed to calculate stats: {e}")
            return {"error": str(e)}

    def export_report(self, output_file: str | None = None) -> str:
        """
        Export detailed bankroll report

        Args:
            output_file: Optional file path for export

        Returns:
            Report content as string
        """
        stats = self.get_bankroll_stats()

        if "error" in stats:
            return f"Error generating report: {stats['error']}"

        report = """
EQ12 BANKROLL PERFORMANCE REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
================================================

CURRENT STATUS:
- Current Balance: ${stats["current_balance"]:,.2f}
- Initial Balance: ${stats["initial_balance"]:,.2f}
- Total Profit/Loss: ${stats["total_profit"]:+,.2f}
- ROI: {stats["roi"]:+.2f}%

BETTING STATISTICS:
- Total Bets: {stats["total_bets"]}
- Win Rate: {stats["win_rate"]:.1f}%
- Average Win: ${stats["average_win"]:.2f}
- Average Loss: ${stats["average_loss"]:.2f}
- Profit Factor: {stats["profit_factor"]:.2f}

RISK METRICS:
- Maximum Drawdown: {stats["max_drawdown"]:.2f}%

Data Source: {self.csv_file}
"""

        if output_file:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(report)
                logger.info(f"Report exported to: {output_file}")
            except Exception as e:
                logger.error(f"Failed to export report: {e}")

        return report

    def get_current_balance(self) -> float:
        """Get current bankroll balance"""
        return self.current_bankroll

    def set_balance(
            self,
            new_balance: float,
            reason: str = "Manual adjustment") -> None:
        """
        Manually set bankroll balance

        Args:
            new_balance: New balance amount
            reason: Reason for adjustment
        """
        old_balance = self.current_bankroll
        adjustment = new_balance - old_balance

        self.record_bet(
            bet_amount=0.0,
            outcome="adjustment",
            profit_loss=adjustment,
            notes=reason)

        logger.info(f"Balance adjusted from ${old_balance:.2f} to ${new_balance:.2f}")


def main():
    """Example usage and testing"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Bankroll Tracker")
    parser.add_argument("--balance", action="store_true", help="Show current balance")
    parser.add_argument("--stats", action="store_true", help="Show detailed statistics")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    parser.add_argument(
        "--record-win",
        type=float,
        metavar="AMOUNT",
        help="Record a winning bet")
    parser.add_argument(
        "--record-loss",
        type=float,
        metavar="AMOUNT",
        help="Record a losing bet")
    parser.add_argument(
        "--bet-amount",
        type=float,
        default=100.0,
        help="Bet amount for recording (default: 100)",
    )
    parser.add_argument(
        "--csv-file", default="C:/EQ12/data/bankroll_history.csv", help="CSV file path"
    )

    args = parser.parse_args()

    # Initialize tracker
    tracker = BankrollTracker(csv_file=args.csv_file)

    if args.record_win:
        profit = args.record_win - args.bet_amount
        tracker.record_bet(args.bet_amount, "win", profit, "CLI recorded win")

    elif args.record_loss:
        tracker.record_bet(args.bet_amount, "loss", -
                           args.bet_amount, "CLI recorded loss")

    if args.balance:
        print(f"Current Balance: ${tracker.get_current_balance():.2f}")

    if args.stats:
        stats = tracker.get_bankroll_stats()
        print(json.dumps(stats, indent=2))

    if args.report:
        print(tracker.export_report())


if __name__ == "__main__":
    main()
