"""
EQ12 Backtester Reporting & Integration
Comprehensive reporting, charts, and EQ12 godmode integration

Features:
1. CSV exports with detailed analytics
2. Telegram bot integration for notifications
3. Matplotlib charts and visualizations
4. EQ12 task scheduler integration
5. Automated daily reports
6. Performance dashboards
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns

logger = logging.getLogger(__name__)

# Set matplotlib style for professional charts
plt.style.use("seaborn-v0_8")
sns.set_palette("husl")


class EQ12ReportGenerator:
    """
    Advanced reporting system for EQ12 backtester results

    Generates:
    - Performance reports (CSV, PDF)
    - Visual charts and graphs
    - Telegram notifications
    - Dashboard HTML pages
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = Path(eq12_root)
        self.reports_dir = self.eq12_root / "eq12_backtester" / "reports"
        self.charts_dir = self.reports_dir / "charts"

        # Create directories
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.charts_dir.mkdir(parents=True, exist_ok=True)

        # Telegram configuration
        self.telegram_config = {
            "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "chat_id": os.getenv("TELEGRAM_CHAT_ID", ""),
            "enabled": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
        }

        logger.info("EQ12 Report Generator initialized")

    def generate_backtest_report(
        self, results: dict[str, Any], title: str = "EQ12 Backtest Report"
    ) -> str:
        """
        Generate comprehensive backtest report

        Args:
            results: Backtest results from engine
            title: Report title

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"backtest_report_{timestamp}.html"

        # Generate charts
        charts = self._generate_performance_charts(results, timestamp)

        # Create HTML report
        html_content = self._create_html_report(results, charts, title)

        # Write report file
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Generated backtest report: {report_file}")

        # Send Telegram notification if enabled
        if self.telegram_config["enabled"]:
            self._send_telegram_report(results, title)

        return str(report_file)

    def _generate_performance_charts(
        self, results: dict[str, Any], timestamp: str
    ) -> dict[str, str]:
        """Generate performance visualization charts"""
        charts = {}

        # Chart 1: Equity Curve
        if "daily_pnl" in results:
            equity_chart = self._create_equity_curve_chart(results, timestamp)
            charts["equity_curve"] = equity_chart

        # Chart 2: Market Breakdown
        if "market_breakdown" in results:
            market_chart = self._create_market_breakdown_chart(results, timestamp)
            charts["market_breakdown"] = market_chart

        # Chart 3: Win Rate Analysis
        winrate_chart = self._create_winrate_analysis_chart(results, timestamp)
        charts["winrate_analysis"] = winrate_chart

        # Chart 4: Drawdown Analysis
        if "daily_pnl" in results:
            drawdown_chart = self._create_drawdown_chart(results, timestamp)
            charts["drawdown"] = drawdown_chart

        return charts

    def _create_equity_curve_chart(self, results: dict[str, Any], timestamp: str) -> str:
        """Create equity curve visualization"""
        _fig, ax = plt.subplots(figsize=(12, 6))

        # Calculate cumulative P&L
        daily_pnl = results.get("daily_pnl", {})
        if daily_pnl:
            dates = sorted(daily_pnl.keys())
            cumulative_pnl = []
            running_total = results.get("initial_bankroll", 1000)

            for date in dates:
                running_total += daily_pnl[date]
                cumulative_pnl.append(running_total)

            # Plot equity curve
            ax.plot(dates, cumulative_pnl, linewidth=2, color="#2E86AB", label="Bankroll")
            ax.axhline(
                y=results.get("initial_bankroll", 1000),
                color="red",
                linestyle="--",
                alpha=0.7,
                label="Starting Bankroll",
            )

            # Formatting
            ax.set_title("EQ12 Equity Curve", fontsize=16, fontweight="bold")
            ax.set_xlabel("Date")
            ax.set_ylabel("Bankroll ($)")
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

        # Save chart
        chart_file = self.charts_dir / f"equity_curve_{timestamp}.png"
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches="tight")
        plt.close()

        return str(chart_file)

    def _create_market_breakdown_chart(self, results: dict[str, Any], timestamp: str) -> str:
        """Create market performance breakdown chart"""
        _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

        market_data = results.get("market_breakdown", {})
        if market_data:
            markets = list(market_data.keys())
            profits = [market_data[m].get("profit", 0) for m in markets]
            win_rates = [
                market_data[m].get("wins", 0) / max(1, market_data[m].get("bets", 1))
                for m in markets
            ]

            # Chart 1: Profit by Market
            colors = sns.color_palette("husl", len(markets))
            bars1 = ax1.bar(markets, profits, color=colors)
            ax1.set_title("Profit by Market", fontsize=14, fontweight="bold")
            ax1.set_ylabel("Profit ($)")
            ax1.tick_params(axis="x", rotation=45)

            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"${height:.0f}",
                    ha="center",
                    va="bottom",
                )

            # Chart 2: Win Rate by Market
            bars2 = ax2.bar(markets, [wr * 100 for wr in win_rates], color=colors)
            ax2.set_title("Win Rate by Market", fontsize=14, fontweight="bold")
            ax2.set_ylabel("Win Rate (%)")
            ax2.tick_params(axis="x", rotation=45)
            ax2.set_ylim(0, 100)

            # Add percentage labels
            for bar, wr in zip(bars2, win_rates, strict=False):
                height = bar.get_height()
                ax2.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height,
                    f"{wr * 100:.1f}%",
                    ha="center",
                    va="bottom",
                )

        # Save chart
        chart_file = self.charts_dir / f"market_breakdown_{timestamp}.png"
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches="tight")
        plt.close()

        return str(chart_file)

    def _create_winrate_analysis_chart(self, results: dict[str, Any], timestamp: str) -> str:
        """Create win rate analysis visualization"""
        _fig, ax = plt.subplots(figsize=(10, 6))

        # Create win rate gauge
        win_rate = results.get("win_rate", 0.5)

        # Gauge chart
        theta = np.linspace(0, np.pi, 100)
        r1 = np.ones_like(theta)

        # Background arc
        ax.fill_between(theta, 0, r1, alpha=0.3, color="lightgray")

        # Win rate arc
        win_theta = theta[theta <= win_rate * np.pi]
        win_r1 = np.ones_like(win_theta)

        if win_rate >= 0.6:
            color = "green"
        elif win_rate >= 0.5:
            color = "orange"
        else:
            color = "red"

        ax.fill_between(win_theta, 0, win_r1, alpha=0.7, color=color)

        # Add percentage text
        ax.text(
            0.5,
            0.3,
            f"{win_rate * 100:.1f}%",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=24,
            fontweight="bold",
        )

        ax.text(
            0.5,
            0.2,
            "Win Rate",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=14,
        )

        ax.set_xlim(0, np.pi)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title("Win Rate Analysis", fontsize=16, fontweight="bold", pad=20)

        # Save chart
        chart_file = self.charts_dir / f"winrate_analysis_{timestamp}.png"
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches="tight")
        plt.close()

        return str(chart_file)

    def _create_drawdown_chart(self, results: dict[str, Any], timestamp: str) -> str:
        """Create drawdown analysis chart"""
        _fig, ax = plt.subplots(figsize=(12, 6))

        daily_pnl = results.get("daily_pnl", {})
        if daily_pnl:
            dates = sorted(daily_pnl.keys())
            running_bankroll = results.get("initial_bankroll", 1000)
            max_bankroll = running_bankroll
            drawdowns = []

            for date in dates:
                running_bankroll += daily_pnl[date]
                max_bankroll = max(max_bankroll, running_bankroll)
                drawdown = (max_bankroll - running_bankroll) / max_bankroll
                drawdowns.append(-drawdown * 100)  # Negative for visual effect

            # Plot drawdown
            ax.fill_between(dates, drawdowns, 0, alpha=0.7, color="red", label="Drawdown")
            ax.plot(dates, drawdowns, color="darkred", linewidth=2)

            # Formatting
            ax.set_title("Drawdown Analysis", fontsize=16, fontweight="bold")
            ax.set_xlabel("Date")
            ax.set_ylabel("Drawdown (%)")
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Add max drawdown annotation
            max_dd = results.get("max_drawdown", 0) * 100
            ax.text(
                0.02,
                0.95,
                f"Max Drawdown: {max_dd:.1f}%",
                transform=ax.transAxes,
                fontsize=12,
                fontweight="bold",
                bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
            )

        # Save chart
        chart_file = self.charts_dir / f"drawdown_{timestamp}.png"
        plt.tight_layout()
        plt.savefig(chart_file, dpi=300, bbox_inches="tight")
        plt.close()

        return str(chart_file)

    def _create_html_report(
        self, results: dict[str, Any], charts: dict[str, str], title: str
    ) -> str:
        """Create comprehensive HTML report"""

        # Calculate additional metrics
        roi = results.get("roi_percent", 0)
        profit = results.get("total_profit", 0)
        win_rate = results.get("win_rate", 0) * 100
        total_bets = results.get("total_bets", 0)
        sharpe = results.get("sharpe_ratio", 0)
        max_dd = results.get("max_drawdown", 0) * 100

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
                .header {{ text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                          color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
                .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
                .chart-container {{ margin: 30px 0; text-align: center; }}
                .chart-container img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                .positive {{ color: #28a745; }}
                .negative {{ color: #dc3545; }}
                .footer {{ text-align: center; margin-top: 40px; color: #666; border-top: 1px solid #eee; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                    <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>

                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value {"positive" if roi > 0 else "negative"}">{roi:+.2f}%</div>
                        <div class="metric-label">ROI</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value {"positive" if profit > 0 else "negative"}">${profit:+.2f}</div>
                        <div class="metric-label">Total Profit</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{win_rate:.1f}%</div>
                        <div class="metric-label">Win Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_bets}</div>
                        <div class="metric-label">Total Bets</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{sharpe:.2f}</div>
                        <div class="metric-label">Sharpe Ratio</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value negative">{max_dd:.1f}%</div>
                        <div class="metric-label">Max Drawdown</div>
                    </div>
                </div>
        """

        # Add charts if available
        for chart_name, chart_path in charts.items():
            if Path(chart_path).exists():
                # Convert path to relative for HTML
                rel_path = Path(chart_path).relative_to(self.reports_dir)
                html += f"""
                <div class="chart-container">
                    <h3>{chart_name.replace("_", " ").title()}</h3>
                    <img src="{rel_path}" alt="{chart_name}">
                </div>
                """

        html += """
                <div class="footer">
                    <p>EQ12 Backtester Report | Powered by EQ12 GODSTACK</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _send_telegram_report(self, results: dict[str, Any], title: str):
        """Send summary report via Telegram"""
        if not self.telegram_config["enabled"]:
            return

        try:
            # Format message
            roi = results.get("roi_percent", 0)
            profit = results.get("total_profit", 0)
            win_rate = results.get("win_rate", 0) * 100
            total_bets = results.get("total_bets", 0)

            roi_emoji = "📈" if roi > 0 else "📉"
            profit_emoji = "💰" if profit > 0 else "💸"

            message = f"""
🎯 *{title}*

{roi_emoji} *ROI:* {roi:+.2f}%
{profit_emoji} *Profit:* ${profit:+.2f}
🎲 *Win Rate:* {win_rate:.1f}%
📊 *Total Bets:* {total_bets}
📅 *Report Time:* {datetime.now().strftime("%Y-%m-%d %H:%M")}

_Generated by EQ12 GODSTACK_
            """.strip()

            # Send via Telegram API
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            payload = {
                "chat_id": self.telegram_config["chat_id"],
                "text": message,
                "parse_mode": "Markdown",
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
            else:
                logger.warning(f"Telegram notification failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")

    def export_csv_report(self, results: dict[str, Any], filename: str | None = None) -> str:
        """Export results to detailed CSV report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eq12_backtest_export_{timestamp}.csv"

        # Create comprehensive data export
        export_data = []

        # Summary row
        export_data.append(
            {
                "metric": "Summary",
                "value": f"ROI: {results.get('roi_percent', 0):.2f}%",
                "details": f"Profit: ${results.get('total_profit', 0):.2f}",
            }
        )

        # Performance metrics
        metrics = [
            ("Total Bets", results.get("total_bets", 0)),
            ("Wins", results.get("wins", 0)),
            ("Losses", results.get("losses", 0)),
            ("Win Rate %", results.get("win_rate", 0) * 100),
            ("ROI %", results.get("roi_percent", 0)),
            ("Total Profit $", results.get("total_profit", 0)),
            ("Initial Bankroll $", results.get("initial_bankroll", 0)),
            ("Final Bankroll $", results.get("final_bankroll", 0)),
            ("Max Drawdown %", results.get("max_drawdown", 0) * 100),
            ("Sharpe Ratio", results.get("sharpe_ratio", 0)),
        ]

        for metric_name, metric_value in metrics:
            export_data.append({"metric": metric_name, "value": metric_value, "details": ""})

        # Market breakdown
        market_data = results.get("market_breakdown", {})
        for market, data in market_data.items():
            export_data.append(
                {
                    "metric": f"Market: {market}",
                    "value": f"Profit: ${data.get('profit', 0):.2f}",
                    "details": f"Bets: {data.get('bets', 0)}, Wins: {data.get('wins', 0)}",
                }
            )

        # Convert to DataFrame and save
        df = pd.DataFrame(export_data)
        csv_file = self.reports_dir / filename
        df.to_csv(csv_file, index=False)

        logger.info(f"CSV report exported: {csv_file}")
        return str(csv_file)


class EQ12TaskIntegration:
    """Integration with EQ12 task system and automation"""

    def __init__(self, eq12_root: str = "C:/EQ12"):
        self.eq12_root = Path(eq12_root)

    def create_daily_backtest_task(self) -> str:
        """Create Windows task for daily backtesting"""

        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().isoformat()}</Date>
    <Author>EQ12 GODSTACK</Author>
    <Description>Daily EQ12 backtesting and edge scanning</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>{datetime.now().strftime("%Y-%m-%d")}T09:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>python</Command>
      <Arguments>"{self.eq12_root / "eq12_backtester" / "run.py"}" scan</Arguments>
      <WorkingDirectory>{self.eq12_root}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

        # Save task XML
        task_file = self.eq12_root / "EQ12_Daily_Backtest_Task.xml"
        with open(task_file, "w", encoding="utf-16") as f:
            f.write(task_xml)

        logger.info(f"Created task XML: {task_file}")
        return str(task_file)

    def create_eq12_tasks_json(self) -> str:
        """Create tasks.json entries for VS Code integration"""

        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "EQ12: Run Historical Backtest",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/eq12_backtester/run.py",
                        "backtest",
                        "--sport",
                        "${input:sport}",
                        "--market",
                        "${input:market}",
                        "--start",
                        "${input:startDate}",
                        "--end",
                        "${input:endDate}",
                    ],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared",
                    },
                },
                {
                    "label": "EQ12: Optimize Parlays",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/eq12_backtester/run.py",
                        "parlay",
                        "--sport",
                        "${input:sport}",
                        "--type",
                        "${input:parlayType}",
                    ],
                    "group": "build",
                },
                {
                    "label": "EQ12: Daily Edge Scan",
                    "type": "shell",
                    "command": "python",
                    "args": ["${workspaceFolder}/eq12_backtester/run.py", "scan"],
                    "group": "test",
                },
                {
                    "label": "EQ12: Paper Trading Simulation",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "${workspaceFolder}/eq12_backtester/run.py",
                        "paper",
                        "--days",
                        "30",
                    ],
                    "group": "build",
                },
            ],
            "inputs": [
                {
                    "id": "sport",
                    "description": "Select sport",
                    "type": "pickString",
                    "options": ["MLB", "NFL", "NBA", "UFC"],
                },
                {
                    "id": "market",
                    "description": "Enter market type",
                    "type": "promptString",
                    "default": "HR",
                },
                {
                    "id": "startDate",
                    "description": "Start date (YYYY-MM-DD)",
                    "type": "promptString",
                    "default": "2024-01-01",
                },
                {
                    "id": "endDate",
                    "description": "End date (YYYY-MM-DD)",
                    "type": "promptString",
                    "default": "2024-12-31",
                },
                {
                    "id": "parlayType",
                    "description": "Select parlay type",
                    "type": "pickString",
                    "options": ["same_game", "multi_game", "multi_sport", "moonshot"],
                },
            ],
        }

        # Save tasks.json
        vscode_dir = self.eq12_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        tasks_file = vscode_dir / "tasks.json"
        with open(tasks_file, "w") as f:
            json.dump(tasks, f, indent=2)

        logger.info(f"Created VS Code tasks: {tasks_file}")
        return str(tasks_file)


if __name__ == "__main__":
    # Test the reporting system
    print("🎯 EQ12 Reporting & Integration Test")

    # Sample results for testing
    test_results = {
        "total_bets": 150,
        "wins": 85,
        "losses": 65,
        "win_rate": 0.567,
        "roi_percent": 12.5,
        "total_profit": 125.0,
        "initial_bankroll": 1000.0,
        "final_bankroll": 1125.0,
        "max_drawdown": 0.08,
        "sharpe_ratio": 1.35,
        "daily_pnl": {
            datetime(2024, 1, 1).date(): 15.0,
            datetime(2024, 1, 2).date(): -25.0,
            datetime(2024, 1, 3).date(): 35.0,
            datetime(2024, 1, 4).date(): 10.0,
            datetime(2024, 1, 5).date(): -5.0,
        },
        "market_breakdown": {
            "MLB_HR": {"profit": 75.0, "bets": 50, "wins": 30},
            "MLB_TB": {"profit": 50.0, "bets": 40, "wins": 22},
            "NFL_PROPS": {"profit": 0.0, "bets": 60, "wins": 33},
        },
    }

    # Test report generation
    reporter = EQ12ReportGenerator()
    report_file = reporter.generate_backtest_report(test_results, "Test Backtest Report")
    csv_file = reporter.export_csv_report(test_results)

    print(f"Generated HTML report: {report_file}")
    print(f"Generated CSV export: {csv_file}")

    # Test task integration
    task_integration = EQ12TaskIntegration()
    task_xml = task_integration.create_daily_backtest_task()
    tasks_json = task_integration.create_eq12_tasks_json()

    print(f"Created task XML: {task_xml}")
    print(f"Created tasks.json: {tasks_json}")

    logger.info("EQ12 Reporting & Integration test completed!")
