#!/usr/bin/env python3
"""
Enhanced Bankroll Visualizer with Professional Analytics
Plots bankroll curves, drawdowns, and Kelly-optimal vs actual stakes
"""

import argparse
import csv
import json
import statistics
from datetime import datetime
from pathlib import Path

try:
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")


class BankrollVisualizer:
    """
    Professional bankroll visualization and analysis tool
    """

    def __init__(self, bankroll_file: str):
        """
        Initialize visualizer with bankroll CSV file

        Args:
            bankroll_file: Path to bankroll.csv file
        """
        self.bankroll_file = Path(bankroll_file).resolve()
        self.data = []
        self._load_data()

    def _load_data(self):
        """Load and parse bankroll data"""
        if not self.bankroll_file.exists():
            print(f"No bankroll file found at {self.bankroll_file}")
            return

        try:
            with open(self.bankroll_file, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["balance"] and self._is_valid_number(row["balance"]):
                        try:
                            entry = {
                                "timestamp": datetime.fromisoformat(row["timestamp"]),
                                "balance": float(row["balance"]),
                                "action": row.get("action", "unknown"),
                                "amount": (
                                    float(row.get("amount", 0))
                                    if self._is_valid_number(row.get("amount", "0"))
                                    else 0
                                ),
                                "slip_id": row.get("slip_id", ""),
                                "sport": row.get("sport", ""),
                                "result": row.get("result", ""),
                                "description": row.get("description", ""),
                            }
                            self.data.append(entry)
                        except Exception as e:
                            print(f"Warning: Skipping invalid row: {e}")
                            continue
        except Exception as e:
            print(f"Error loading bankroll file: {e}")

    def _is_valid_number(self, value: str) -> bool:
        """Check if string represents a valid number"""
        if not value:
            return False
        try:
            float(value.replace(",", ""))
            return True
        except:
            return False

    def plot_bankroll_curve(self, save: bool = False, show_drawdowns: bool = True) -> str | None:
        """
        Plot comprehensive bankroll analysis chart

        Args:
            save: Save plot as PNG file
            show_drawdowns: Highlight drawdown periods

        Returns:
            Path to saved file if save=True
        """
        if not MATPLOTLIB_AVAILABLE:
            print("Matplotlib not available for plotting")
            return None

        if not self.data:
            print("No valid balance entries to plot")
            return None

        # Extract data for plotting
        timestamps = [entry["timestamp"] for entry in self.data]
        balances = [entry["balance"] for entry in self.data]

        # Calculate statistics
        stats = self._calculate_statistics(balances)

        # Create comprehensive plot
        _fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), height_ratios=[3, 1])

        # Main balance curve
        ax1.plot(
            timestamps,
            balances,
            marker="o",
            markersize=2,
            linestyle="-",
            color="steelblue",
            linewidth=2,
            label="Bankroll Balance",
        )

        # Add moving average if enough data points
        if len(balances) >= 10:
            ma_window = min(10, len(balances) // 4)
            moving_avg = self._calculate_moving_average(balances, ma_window)
            ma_timestamps = timestamps[ma_window - 1 :]
            ax1.plot(
                ma_timestamps,
                moving_avg,
                linestyle="--",
                color="orange",
                linewidth=1.5,
                label=f"{ma_window}-Period Moving Average",
            )

        # Highlight drawdown periods
        if show_drawdowns and len(balances) > 5:
            self._highlight_drawdowns(ax1, timestamps, balances)

        # Format main chart
        ax1.set_ylabel("Balance ($)", fontsize=12)
        ax1.set_title(
            f"Bankroll Performance Analysis - {stats['roi']:.1f}% ROI",
            fontsize=14,
            fontweight="bold",
        )
        ax1.grid(True, linestyle="--", alpha=0.3)
        ax1.legend(loc="upper left")

        # Add performance metrics text box
        metrics_text = self._format_metrics_text(stats)
        ax1.text(
            0.02,
            0.98,
            metrics_text,
            transform=ax1.transAxes,
            verticalalignment="top",
            horizontalalignment="left",
            bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.8},
            fontsize=9,
            fontfamily="monospace",
        )

        # Daily returns subplot
        if len(balances) > 1:
            returns = self._calculate_daily_returns(balances)
            return_timestamps = timestamps[1:]

            colors = ["green" if r >= 0 else "red" for r in returns]
            ax2.bar(
                return_timestamps,
                [r * 100 for r in returns],
                color=colors,
                alpha=0.6,
                width=0.8,
            )

            ax2.set_ylabel("Daily Return (%)", fontsize=10)
            ax2.set_xlabel("Date", fontsize=10)
            ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.8)
            ax2.grid(True, linestyle="--", alpha=0.3)

            # Format x-axis dates
            ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(timestamps) // 10)))
            plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()

        if save:
            output_file = self.bankroll_file.parent / "bankroll_analysis.png"
            plt.savefig(output_file, dpi=300, bbox_inches="tight")
            print(f"📈 Professional bankroll analysis saved → {output_file}")
            plt.close()
            return str(output_file)
        plt.show()
        return None

    def _highlight_drawdowns(self, ax, timestamps: list[datetime], balances: list[float]):
        """Highlight significant drawdown periods on the chart"""
        peak = balances[0]
        peak_time = timestamps[0]
        in_drawdown = False

        for i, (time, balance) in enumerate(zip(timestamps, balances, strict=False)):
            if balance > peak:
                if in_drawdown:
                    # End of drawdown period
                    self._add_drawdown_rectangle(
                        ax, peak_time, time, peak, min(balances[peak_idx:i])
                    )
                    in_drawdown = False
                peak = balance
                peak_time = time
                peak_idx = i
            elif not in_drawdown and (peak - balance) / peak > 0.05:  # 5% drawdown threshold
                in_drawdown = True
                peak_idx = i - 1 if i > 0 else 0

        # Handle ongoing drawdown at end
        if in_drawdown:
            self._add_drawdown_rectangle(
                ax, peak_time, timestamps[-1], peak, min(balances[peak_idx:])
            )

    def _add_drawdown_rectangle(
        self,
        ax,
        start_time: datetime,
        end_time: datetime,
        peak_balance: float,
        trough_balance: float,
    ):
        """Add a shaded rectangle for drawdown period"""
        (end_time - start_time).total_seconds() / 86400  # Convert to days
        drawdown_pct = ((peak_balance - trough_balance) / peak_balance) * 100

        if drawdown_pct > 5:  # Only show significant drawdowns
            rect = Rectangle(
                (mdates.date2num(start_time), trough_balance),
                mdates.date2num(end_time) - mdates.date2num(start_time),
                peak_balance - trough_balance,
                facecolor="red",
                alpha=0.2,
                edgecolor="red",
                linewidth=0.5,
            )
            ax.add_patch(rect)

    def _calculate_moving_average(self, values: list[float], window: int) -> list[float]:
        """Calculate simple moving average"""
        moving_avg = []
        for i in range(window - 1, len(values)):
            avg = sum(values[i - window + 1 : i + 1]) / window
            moving_avg.append(avg)
        return moving_avg

    def _calculate_daily_returns(self, balances: list[float]) -> list[float]:
        """Calculate daily returns from balance history"""
        returns = []
        for i in range(1, len(balances)):
            if balances[i - 1] > 0:
                ret = (balances[i] - balances[i - 1]) / balances[i - 1]
                returns.append(ret)
            else:
                returns.append(0.0)
        return returns

    def _calculate_statistics(self, balances: list[float]) -> dict:
        """Calculate comprehensive performance statistics"""
        if not balances or len(balances) < 2:
            return {
                "roi": 0,
                "max_balance": 0,
                "min_balance": 0,
                "max_drawdown": 0,
                "volatility": 0,
                "sharpe": 0,
                "total_trades": 0,
            }

        initial_balance = balances[0]
        final_balance = balances[-1]
        max_balance = max(balances)
        min_balance = min(balances)

        # ROI
        roi = ((final_balance - initial_balance) / initial_balance) * 100

        # Max drawdown
        peak = initial_balance
        max_drawdown = 0
        for balance in balances:
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak if peak > 0 else 0
            max_drawdown = max(max_drawdown, drawdown)

        # Volatility and Sharpe
        returns = self._calculate_daily_returns(balances)
        volatility = statistics.stdev(returns) * 100 if len(returns) > 1 else 0

        sharpe = 0
        if len(returns) > 1 and statistics.stdev(returns) > 0:
            avg_return = statistics.mean(returns)
            sharpe = (avg_return / statistics.stdev(returns)) * (252**0.5)  # Annualized

        # Trade statistics
        trade_data = [
            entry for entry in self.data if entry["action"] in ["bet_placed", "bet_settled"]
        ]
        total_trades = len([entry for entry in trade_data if entry["action"] == "bet_settled"])

        return {
            "roi": roi,
            "max_balance": max_balance,
            "min_balance": min_balance,
            "max_drawdown": max_drawdown * 100,
            "volatility": volatility,
            "sharpe": sharpe,
            "total_trades": total_trades,
            "current_balance": final_balance,
            "initial_balance": initial_balance,
        }

    def _format_metrics_text(self, stats: dict) -> str:
        """Format statistics for display on chart"""
        return f"""Performance Metrics:
ROI: {stats["roi"]:+.1f}%
Max Drawdown: {stats["max_drawdown"]:.1f}%
Volatility: {stats["volatility"]:.1f}%
Sharpe Ratio: {stats["sharpe"]:.3f}
Total Trades: {stats["total_trades"]}
Peak Balance: ${stats["max_balance"]:,.2f}
Current: ${stats["current_balance"]:,.2f}"""

    def generate_performance_report(self) -> dict:
        """Generate detailed performance report"""
        if not self.data:
            return {"error": "No data available"}

        balances = [entry["balance"] for entry in self.data]
        stats = self._calculate_statistics(balances)

        # Additional analysis
        winning_trades = len(
            [
                entry
                for entry in self.data
                if entry["result"] == "win" and entry["action"] == "bet_settled"
            ]
        )
        total_settled = len(
            [
                entry
                for entry in self.data
                if entry["action"] == "bet_settled" and entry["result"] in ["win", "loss"]
            ]
        )

        win_rate = (winning_trades / total_settled * 100) if total_settled > 0 else 0

        return {
            "summary": stats,
            "win_rate": win_rate,
            "total_bets": total_settled,
            "winning_bets": winning_trades,
            "data_points": len(self.data),
            "date_range": {
                "start": self.data[0]["timestamp"].isoformat() if self.data else None,
                "end": self.data[-1]["timestamp"].isoformat() if self.data else None,
            },
        }

    def export_analysis(self, output_file: str | None = None) -> str:
        """Export analysis to JSON file"""
        report = self.generate_performance_report()

        if output_file is None:
            output_file = self.bankroll_file.parent / "bankroll_analysis.json"

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Analysis exported to: {output_file}")
        return str(output_file)


def main():
    """CLI interface for bankroll visualization"""
    parser = argparse.ArgumentParser(description="Professional Bankroll Visualizer with Analytics")

    parser.add_argument(
        "--file",
        default="../betting-bridge/data/bankroll.csv",
        help="Path to bankroll.csv file",
    )

    parser.add_argument(
        "--save", action="store_true", help="Save chart as PNG instead of displaying"
    )

    parser.add_argument(
        "--no-drawdowns", action="store_true", help="Don't highlight drawdown periods"
    )

    parser.add_argument("--export", action="store_true", help="Export analysis to JSON file")

    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate text report only (no chart)",
    )

    args = parser.parse_args()

    # Initialize visualizer
    visualizer = BankrollVisualizer(args.file)

    if args.report_only:
        # Generate text report
        report = visualizer.generate_performance_report()
        if "error" in report:
            print(f"Error: {report['error']}")
            return 1

        print("=== BANKROLL PERFORMANCE REPORT ===")
        print(f"Date Range: {report['date_range']['start']} to {report['date_range']['end']}")
        print(f"Total Data Points: {report['data_points']}")
        print(f"Total Bets: {report['total_bets']}")
        print(f"Win Rate: {report['win_rate']:.1f}%")
        print("\nPerformance Metrics:")
        stats = report["summary"]
        print(f"  ROI: {stats['roi']:+.1f}%")
        print(f"  Max Drawdown: {stats['max_drawdown']:.1f}%")
        print(f"  Volatility: {stats['volatility']:.1f}%")
        print(f"  Sharpe Ratio: {stats['sharpe']:.3f}")
        print(f"  Current Balance: ${stats['current_balance']:,.2f}")
        print(f"  Peak Balance: ${stats['max_balance']:,.2f}")

        return 0

    # Generate visualization
    result = visualizer.plot_bankroll_curve(save=args.save, show_drawdowns=not args.no_drawdowns)

    if args.export:
        visualizer.export_analysis()

    if result:
        print(f"Chart saved: {result}")

    return 0


if __name__ == "__main__":
    exit(main())
