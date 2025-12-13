#!/usr/bin/env python3
"""
EQ12 GODSTACK Badge Health Monitor
Automated monitoring of GitHub repository status badges with Telegram alerts
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

# Configure logging
log_dir = Path("C:/EQ12/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "badge-health-monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class BadgeHealthMonitor:
    def __init__(self):
        """Initialize the badge health monitor."""
        self.repo_owner = "Vibehigheric"
        self.repo_name = "EQ12-GODSTACK"
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

        # Badge configurations
        self.badges = {
            "ci": {
                "name": "🔄 CI/Security Workflow",
                "url": f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/actions/workflows/github-advanced-security.yml/runs",
                "status_check": "conclusion",
                "critical": True,
            },
            "codeql": {
                "name": "🔐 CodeQL Security Analysis",
                "url": f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/code-scanning/analyses",
                "status_check": "state",
                "critical": True,
            },
            "dependabot": {
                "name": "🤖 Dependabot Security",
                "url": f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/vulnerability-alerts",
                "status_check": "enabled",
                "critical": False,
            },
            "secrets": {
                "name": "🔑 Secret Scanning",
                "url": f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/secret-scanning/alerts",
                "status_check": "state",
                "critical": True,
            },
            "repository": {
                "name": "🔐 Repository Security",
                "url": f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}",
                "status_check": "private",
                "critical": True,
            },
        }

        self.headers = (
            {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            if self.github_token
            else {}
        )

    def check_workflow_status(self) -> tuple[str, str, dict]:
        """Check GitHub Actions workflow status."""
        try:
            url = self.badges["ci"]["url"]
            response = requests.get(url, headers=self.headers, params={"per_page": 1})

            if response.status_code == 200:
                runs = response.json().get("workflow_runs", [])
                if runs:
                    latest_run = runs[0]
                    conclusion = latest_run.get("conclusion", "unknown")
                    status = latest_run.get("status", "unknown")

                    if conclusion == "success":
                        return (
                            "✅",
                            "Passing",
                            {
                                "status": status,
                                "conclusion": conclusion,
                                "run_id": latest_run.get("id"),
                                "created_at": latest_run.get("created_at"),
                            },
                        )
                    if conclusion == "failure":
                        return (
                            "❌",
                            "Failing",
                            {
                                "status": status,
                                "conclusion": conclusion,
                                "run_id": latest_run.get("id"),
                                "html_url": latest_run.get("html_url"),
                            },
                        )
                    return (
                        "🟡",
                        f"Status: {status}",
                        {"status": status, "conclusion": conclusion},
                    )
                return "⚪", "No runs found", {}
            return "❓", f"API Error: {response.status_code}", {}

        except Exception as e:
            logger.error(f"Error checking workflow status: {e}")
            return "❓", f"Error: {e!s}", {}

    def check_codeql_status(self) -> tuple[str, str, dict]:
        """Check CodeQL security analysis status."""
        try:
            url = self.badges["codeql"]["url"]
            response = requests.get(url, headers=self.headers, params={"per_page": 10})

            if response.status_code == 200:
                analyses = response.json()
                if analyses:
                    # Count alerts by severity
                    recent_analyses = analyses[:5]  # Check last 5 analyses
                    total_alerts = 0
                    critical_alerts = 0

                    for analysis in recent_analyses:
                        if analysis.get("results_count", 0) > 0:
                            total_alerts += analysis.get("results_count", 0)
                            # Assume high severity if error count > 0
                            if analysis.get("error", {}).get("count", 0) > 0:
                                critical_alerts += 1

                    if critical_alerts > 0:
                        return (
                            "❌",
                            f"Critical Issues: {critical_alerts}",
                            {
                                "total_alerts": total_alerts,
                                "critical_alerts": critical_alerts,
                                "latest_analysis": (
                                    recent_analyses[0] if recent_analyses else None
                                ),
                            },
                        )
                    if total_alerts > 0:
                        return (
                            "🟡",
                            f"Warnings: {total_alerts}",
                            {"total_alerts": total_alerts, "critical_alerts": 0},
                        )
                    return "✅", "No Issues", {"total_alerts": 0, "critical_alerts": 0}
                return "⚪", "No analyses found", {}
            return "❓", f"API Error: {response.status_code}", {}

        except Exception as e:
            logger.error(f"Error checking CodeQL status: {e}")
            return "❓", f"Error: {e!s}", {}

    def check_secret_scanning(self) -> tuple[str, str, dict]:
        """Check secret scanning alerts."""
        try:
            url = self.badges["secrets"]["url"]
            response = requests.get(url, headers=self.headers, params={"state": "open"})

            if response.status_code == 200:
                alerts = response.json()
                open_alerts = len(alerts)

                if open_alerts > 0:
                    critical_secrets = [
                        alert
                        for alert in alerts
                        if alert.get("secret_type_display_name", "").lower()
                        in ["github token", "api key", "private key", "oauth token"]
                    ]

                    if critical_secrets:
                        return (
                            "❌",
                            f"Critical Secrets: {len(critical_secrets)}",
                            {
                                "total_alerts": open_alerts,
                                "critical_alerts": len(critical_secrets),
                                "alerts": alerts[:3],  # First 3 for details
                            },
                        )
                    return (
                        "🟡",
                        f"Secrets Found: {open_alerts}",
                        {"total_alerts": open_alerts, "critical_alerts": 0},
                    )
                return "✅", "No Secrets Detected", {"total_alerts": 0}
            return "❓", f"API Error: {response.status_code}", {}

        except Exception as e:
            logger.error(f"Error checking secret scanning: {e}")
            return "❓", f"Error: {e!s}", {}

    def check_repository_security(self) -> tuple[str, str, dict]:
        """Check overall repository security settings."""
        try:
            url = self.badges["repository"]["url"]
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                repo_data = response.json()
                security_issues = []

                # Check if repository is private
                if not repo_data.get("private", False):
                    security_issues.append("Repository is public (should be private)")

                # Check security features
                security_analysis = repo_data.get("security_and_analysis", {})

                if security_analysis.get(
                    "secret_scanning",
                        {}).get("status") != "enabled":
                    security_issues.append("Secret scanning not enabled")

                if (security_analysis.get("secret_scanning_push_protection", {}).get(
                        "status") != "enabled"):
                    security_issues.append("Push protection not enabled")

                # Check vulnerability alerts
                if not repo_data.get("has_vulnerability_alerts", False):
                    security_issues.append("Vulnerability alerts not enabled")

                if security_issues:
                    return (
                        "❌",
                        f"Issues: {len(security_issues)}",
                        {
                            "issues": security_issues,
                            "private": repo_data.get("private", False),
                            "security_features": security_analysis,
                        },
                    )
                return (
                    "✅",
                    "All Security Features Active",
                    {
                        "private": repo_data.get("private", False),
                        "security_features": security_analysis,
                    },
                )
            return "❓", f"API Error: {response.status_code}", {}

        except Exception as e:
            logger.error(f"Error checking repository security: {e}")
            return "❓", f"Error: {e!s}", {}

    def check_dependabot_status(self) -> tuple[str, str, dict]:
        """Check Dependabot security status."""
        try:
            # Check for open vulnerability alerts
            url = (
                f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/dependabot/alerts"
            )
            response = requests.get(url, headers=self.headers, params={"state": "open"})

            if response.status_code == 200:
                alerts = response.json()
                open_alerts = len(alerts)

                if open_alerts > 0:
                    critical_alerts = [
                        alert
                        for alert in alerts
                        if alert.get("security_advisory", {}).get("severity", "").lower()
                        in ["critical", "high"]
                    ]

                    if critical_alerts:
                        return (
                            "❌",
                            f"Critical Vulnerabilities: {len(critical_alerts)}",
                            {
                                "total_alerts": open_alerts,
                                "critical_alerts": len(critical_alerts),
                                "alerts": alerts[:3],
                            },
                        )
                    return (
                        "🟡",
                        f"Vulnerabilities: {open_alerts}",
                        {"total_alerts": open_alerts, "critical_alerts": 0},
                    )
                return "✅", "No Vulnerabilities", {"total_alerts": 0}
            if response.status_code == 404:
                return "⚪", "Dependabot not configured", {}
            return "❓", f"API Error: {response.status_code}", {}

        except Exception as e:
            logger.error(f"Error checking Dependabot status: {e}")
            return "❓", f"Error: {e!s}", {}

    def run_health_check(self) -> dict:
        """Run comprehensive health check on all badges."""
        logger.info("🔍 Starting EQ12 GODSTACK badge health check...")

        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "repository": f"{self.repo_owner}/{self.repo_name}",
            "overall_status": "✅",
            "critical_issues": 0,
            "warning_issues": 0,
            "checks": {},
        }

        # Run individual checks
        checks = {
            "ci_workflow": self.check_workflow_status,
            "codeql_security": self.check_codeql_status,
            "secret_scanning": self.check_secret_scanning,
            "repository_security": self.check_repository_security,
            "dependabot": self.check_dependabot_status,
        }

        for check_name, check_func in checks.items():
            try:
                badge, status, details = check_func()
                health_report["checks"][check_name] = {
                    "badge": badge,
                    "status": status,
                    "details": details,
                }

                # Count issues
                if badge == "❌":
                    health_report["critical_issues"] += 1
                    health_report["overall_status"] = "❌"
                elif badge == "🟡":
                    health_report["warning_issues"] += 1
                    if health_report["overall_status"] != "❌":
                        health_report["overall_status"] = "🟡"

                logger.info(f"{badge} {check_name}: {status}")

            except Exception as e:
                logger.error(f"Error in {check_name} check: {e}")
                health_report["checks"][check_name] = {
                    "badge": "❓",
                    "status": f"Error: {e!s}",
                    "details": {},
                }

        # Save report
        report_path = (
            log_dir / f"badge-health-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        )
        with open(report_path, "w") as f:
            json.dump(health_report, f, indent=2)

        logger.info(f"📊 Health report saved: {report_path}")
        return health_report

    def send_telegram_alert(self, health_report: dict) -> bool:
        """Send Telegram alert with health report."""
        if not self.telegram_token or not self.telegram_chat_id:
            logger.warning("Telegram credentials not configured")
            return False

        try:
            # Build alert message
            overall_status = health_report["overall_status"]
            critical_count = health_report["critical_issues"]
            warning_count = health_report["warning_issues"]

            if overall_status == "✅":
                message = "🟢 *EQ12 GODSTACK Health Check - ALL CLEAR*\n\n"
                message += "✅ All security badges are green!\n"
                message += "🛡️ Repository security: Optimal\n"
                message += "🔒 No vulnerabilities detected\n"
                message += "📊 All systems operational\n\n"
                message += f"📅 Check completed: {
                    datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"

            else:
                message = f"{overall_status} *EQ12 GODSTACK Security Alert*\n\n"

                if critical_count > 0:
                    message += f"🚨 *CRITICAL ISSUES: {critical_count}*\n"
                if warning_count > 0:
                    message += f"⚠️ *Warnings: {warning_count}*\n"

                message += "\n📊 *Badge Status Summary:*\n"

                # Add individual check results
                for check_name, check_data in health_report["checks"].items():
                    badge = check_data["badge"]
                    status = check_data["status"]
                    message += f"{badge} {
                        check_name.replace(
                            '_', ' ').title()}: {status}\n"

                message += (
                    f"\n🔗 Repository: https://github.com/{self.repo_owner}/{self.repo_name}\n"
                )
                message += f"📅 Alert time: {
                    datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n"

                if critical_count > 0:
                    message += "🚨 *Immediate action required for critical issues!*"
                else:
                    message += "⚠️ Review and address warnings when convenient"

            # Send via Telegram
            telegram_url = f"https://api.telegram.org/bot{
                self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown",
            }

            response = requests.post(telegram_url, json=payload)

            if response.status_code == 200:
                logger.info("✅ Telegram alert sent successfully")
                return True
            logger.error(f"❌ Telegram alert failed: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
            return False


def main():
    """Main execution function."""
    logger.info("🚀 EQ12 GODSTACK Badge Health Monitor Starting")

    try:
        # Initialize monitor
        monitor = BadgeHealthMonitor()

        # Run health check
        health_report = monitor.run_health_check()

        # Send alert if issues found or if it's a scheduled report
        should_send_alert = (
            health_report["overall_status"] != "✅"  # Issues found
            or "--force-alert" in sys.argv  # Forced alert
            or datetime.now().day == 1  # Monthly report (1st of month)
        )

        if should_send_alert:
            logger.info("📱 Sending Telegram health report...")
            monitor.send_telegram_alert(health_report)
        else:
            logger.info("📊 All badges healthy - no alert needed")

        # Print summary
        print("\n" + "=" * 50)
        print("📊 EQ12 GODSTACK BADGE HEALTH SUMMARY")
        print("=" * 50)
        print(f"🎯 Overall Status: {health_report['overall_status']}")
        print(f"🚨 Critical Issues: {health_report['critical_issues']}")
        print(f"⚠️ Warning Issues: {health_report['warning_issues']}")
        print(f"📅 Check Time: {health_report['timestamp']}")
        print("=" * 50)

        for check_name, check_data in health_report["checks"].items():
            badge = check_data["badge"]
            status = check_data["status"]
            print(f"{badge} {check_name.replace('_', ' ').title()}: {status}")

        print("=" * 50)

        # Return appropriate exit code
        if health_report["critical_issues"] > 0:
            return 1  # Critical issues found
        if health_report["warning_issues"] > 0:
            return 2  # Warnings found
        return 0  # All clear

    except Exception as e:
        logger.error(f"❌ Badge health check failed: {e}")
        return 3  # Script error


if __name__ == "__main__":
    exit(main())
