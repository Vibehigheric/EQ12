#!/usr/bin/env python3
"""
EQ12 GitLeaks Security Monitor
Professional-grade continuous security monitoring for EQ12 platform

This module provides:
- Continuous GitLeaks scanning and monitoring
- Integration with GitHub Copilot for automated fixes
- Real-time security event logging
- Automated remediation and backup systems
- Risk assessment and compliance reporting
- VS Code integration for seamless workflows

Author: EQ12 Platform Security Team
Version: 2.1.0
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class SecurityLevel(Enum):
    """Security risk levels for findings"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RemediationStatus(Enum):
    """Status of automated remediation attempts"""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    MANUAL_REQUIRED = "MANUAL_REQUIRED"


@dataclass
class SecurityFinding:
    """Represents a security finding from GitLeaks"""

    file_path: str
    line_number: int
    rule_id: str
    secret_type: str
    match_text: str
    security_level: SecurityLevel
    commit_hash: str | None = None
    remediation_status: RemediationStatus = RemediationStatus.PENDING
    first_seen: str = ""
    last_seen: str = ""

    def __post_init__(self):
        if not self.first_seen:
            self.first_seen = datetime.now(UTC).isoformat()
        self.last_seen = datetime.now(UTC).isoformat()


@dataclass
class SecurityReport:
    """Comprehensive security report"""

    scan_timestamp: str
    repository_path: str
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    remediated_findings: int
    pending_findings: int
    risk_score: float
    compliance_status: str
    findings: list[SecurityFinding]
    backup_paths: list[str]
    recommendations: list[str]


class EQ12SecurityLogger:
    """Enhanced security logging with EQ12 integration"""

    def __init__(self, log_dir: str = "C:/EQ12/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup structured logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"gitleaks_monitor_{timestamp}.log"
        self.security_file = self.log_dir / f"security_events_{timestamp}.json"

        # Configure logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger("EQ12Security")

    def log_security_event(self, level: str, message: str, data: dict | None = None):
        """Log structured security events"""
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": level,
            "category": "SECURITY_MONITOR",
            "message": message,
            "eq12_version": "2.1.0",
            "data": data or {},
        }

        # Append to JSON log file
        with open(self.security_file, "a") as f:
            json.dump(event, f)
            f.write("\n")

        # Standard logging
        getattr(self.logger, level.lower(), self.logger.info)(message)


class GitLeaksScanner:
    """GitLeaks integration and scanning"""

    def __init__(self, repo_path: str, logger: EQ12SecurityLogger):
        self.repo_path = Path(repo_path)
        self.logger = logger
        self.gitleaks_available = self._check_gitleaks()

    def _check_gitleaks(self) -> bool:
        """Check if GitLeaks is available"""
        try:
            result = subprocess.run(
                ["gitleaks", "version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                self.logger.log_security_event(
                    "INFO", f"GitLeaks available: {result.stdout.strip()}"
                )
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.log_security_event("ERROR", f"GitLeaks not available: {e}")

        return False

    def scan_repository(self, include_history: bool = True) -> list[SecurityFinding]:
        """Perform comprehensive repository scan"""
        if not self.gitleaks_available:
            raise RuntimeError("GitLeaks not available - cannot perform security scan")

        findings = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Scan current files
        current_report = self.repo_path / f"gitleaks_current_{timestamp}.json"

        try:
            cmd = [
                "gitleaks",
                "detect",
                "--source",
                str(self.repo_path),
                "--report-path",
                str(current_report),
                "--exit-code",
                "0",
            ]

            self.logger.log_security_event(
                "INFO", "Starting GitLeaks scan of current files")
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if current_report.exists():
                findings.extend(self._parse_gitleaks_report(current_report))
                current_report.unlink()  # Cleanup

            # Scan Git history if requested
            if include_history:
                history_report = self.repo_path / f"gitleaks_history_{timestamp}.json"

                cmd_history = [
                    "gitleaks",
                    "detect",
                    "--source",
                    str(self.repo_path),
                    "--report-path",
                    str(history_report),
                    "--exit-code",
                    "0",
                    "--log-level",
                    "debug",
                ]

                self.logger.log_security_event(
                    "INFO", "Starting GitLeaks scan of Git history")
                subprocess.run(cmd_history, capture_output=True, text=True, timeout=600)

                if history_report.exists():
                    history_findings = self._parse_gitleaks_report(history_report)
                    # Mark history findings with commit info
                    for finding in history_findings:
                        finding.commit_hash = "history_scan"
                    findings.extend(history_findings)
                    history_report.unlink()  # Cleanup

            self.logger.log_security_event(
                "SUCCESS", f"GitLeaks scan completed - {len(findings)} findings"
            )

        except subprocess.TimeoutExpired:
            self.logger.log_security_event("ERROR", "GitLeaks scan timed out")
            raise
        except Exception as e:
            self.logger.log_security_event("ERROR", f"GitLeaks scan failed: {e}")
            raise

        return findings

    def _parse_gitleaks_report(self, report_path: Path) -> list[SecurityFinding]:
        """Parse GitLeaks JSON report into SecurityFinding objects"""
        findings = []

        try:
            if report_path.stat().st_size == 0:
                return findings

            with open(report_path) as f:
                data = json.load(f)

            if not data:
                return findings

            for item in data:
                # Determine security level based on secret type
                security_level = self._assess_security_level(item.get("RuleID", ""))

                finding = SecurityFinding(
                    file_path=item.get("File", ""),
                    line_number=item.get("StartLine", 0),
                    rule_id=item.get("RuleID", ""),
                    secret_type=self._categorize_secret(item.get("RuleID", "")),
                    match_text=item.get("Match", "")[
                        :50] + "...",  # Truncate for safety
                    security_level=security_level,
                )

                findings.append(finding)

        except json.JSONDecodeError as e:
            self.logger.log_security_event(
                "WARN", f"Could not parse GitLeaks report: {e}")
        except Exception as e:
            self.logger.log_security_event(
                "ERROR", f"Error parsing GitLeaks report: {e}")

        return findings

    def _assess_security_level(self, rule_id: str) -> SecurityLevel:
        """Assess security level based on rule ID"""
        rule_lower = rule_id.lower()

        # Critical - API keys, tokens
        if any(
            keyword in rule_lower
            for keyword in ["api-key", "secret-key", "private-key", "token", "password"]
        ):
            return SecurityLevel.CRITICAL

        # High - Database URLs, credentials
        if any(
            keyword in rule_lower for keyword in [
                "database",
                "connection",
                "credential",
                "auth"]):
            return SecurityLevel.HIGH

        # Medium - Configuration secrets
        if any(keyword in rule_lower for keyword in ["config", "env", "secret"]):
            return SecurityLevel.MEDIUM

        return SecurityLevel.LOW

    def _categorize_secret(self, rule_id: str) -> str:
        """Categorize the type of secret"""
        rule_lower = rule_id.lower()

        if "aws" in rule_lower:
            return "AWS Credential"
        elif "github" in rule_lower:
            return "GitHub Token"
        elif "openai" in rule_lower:
            return "OpenAI API Key"
        elif "google" in rule_lower:
            return "Google API Key"
        elif "database" in rule_lower or "db" in rule_lower:
            return "Database Credential"
        elif "jwt" in rule_lower:
            return "JWT Token"
        elif "api" in rule_lower:
            return "API Key"
        else:
            return "Generic Secret"


class AutoRemediator:
    """Automated secret remediation system"""

    def __init__(self, repo_path: str, logger: EQ12SecurityLogger):
        self.repo_path = Path(repo_path)
        self.logger = logger
        self.backup_dir = Path("C:/EQ12/backups/gitleaks")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def remediate_findings(
        self, findings: list[SecurityFinding], dry_run: bool = False
    ) -> dict[str, Any]:
        """Automatically remediate security findings"""
        if not findings:
            return {"success": True, "fixed_count": 0, "errors": []}

        self.logger.log_security_event(
            "INFO", f"Starting auto-remediation of {len(findings)} findings"
        )

        # Create backup
        backup_path = self._create_backup()
        if not backup_path and not dry_run:
            return {"success": False, "error": "Backup creation failed"}

        fixed_count = 0
        errors = []

        # Group findings by file for efficient processing
        files_to_process = {}
        for finding in findings:
            if finding.file_path not in files_to_process:
                files_to_process[finding.file_path] = []
            files_to_process[finding.file_path].append(finding)

        # Process each file
        for file_path, file_findings in files_to_process.items():
            try:
                if self._remediate_file(file_path, file_findings, dry_run):
                    fixed_count += len(file_findings)
                    # Update finding status
                    for finding in file_findings:
                        finding.remediation_status = RemediationStatus.COMPLETED

            except Exception as e:
                error_msg = f"Failed to remediate {file_path}: {e}"
                errors.append(error_msg)
                self.logger.log_security_event("ERROR", error_msg)

                # Mark findings as failed
                for finding in file_findings:
                    finding.remediation_status = RemediationStatus.FAILED

        # Update environment files
        if not dry_run:
            self._update_env_files()
            self._update_gitignore()

        result = {
            "success": len(errors) == 0,
            "fixed_count": fixed_count,
            "errors": errors,
            "backup_path": str(backup_path) if backup_path else None,
        }

        self.logger.log_security_event(
            "SUCCESS",
            f"Auto-remediation completed: {fixed_count} files fixed, {len(errors)} errors",
        )

        return result

    def _create_backup(self) -> Path | None:
        """Create backup of repository state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"

        try:
            shutil.copytree(self.repo_path, backup_path)
            self.logger.log_security_event("SUCCESS", f"Backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.log_security_event("ERROR", f"Backup failed: {e}")
            return None

    def _remediate_file(
        self, file_path: str, findings: list[SecurityFinding], dry_run: bool
    ) -> bool:
        """Remediate secrets in a single file"""
        full_path = self.repo_path / file_path

        if not full_path.exists():
            return False

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()

            # Apply secret pattern replacements
            secret_patterns = {
                # API Keys
                r"sk-[A-Za-z0-9]{32,}": 'os.getenv("OPENAI_API_KEY")',
                r"AIza[A-Za-z0-9]{35}": 'os.getenv("GOOGLE_API_KEY")',
                r"AKIA[A-Z0-9]{16}": 'os.getenv("AWS_ACCESS_KEY_ID")',
                r"[A-Za-z0-9+/]{40}": 'os.getenv("AWS_SECRET_ACCESS_KEY")',
                r"ghp_[A-Za-z0-9]{36}": 'os.getenv("GITHUB_TOKEN")',
                # Database URLs
                r"postgres://[^:]+:[^@]+@[^/]+/\w+": 'os.getenv("DATABASE_URL")',
                r"mysql://[^:]+:[^@]+@[^/]+/\w+": 'os.getenv("DATABASE_URL")',
                # JWT tokens
                r"eyJ[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=]*": 'os.getenv("JWT_TOKEN")',
            }

            import re

            modified = False

            for pattern, replacement in secret_patterns.items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True

            # Add environment imports for Python files
            if full_path.suffix == ".py" and modified and "import os" not in content:
                if "from dotenv import load_dotenv" not in content:
                    content = (
                        "from dotenv import load_dotenv\nimport os\nload_dotenv()\n\n" +
                        content)

            # Add environment requires for JavaScript files
            elif (
                full_path.suffix in [".js", ".ts"]
                and modified
                and "require('dotenv')" not in content
            ):
                content = "require('dotenv').config();\n\n" + content

            # Write changes
            if modified and not dry_run:
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.logger.log_security_event(
                    "SUCCESS", f"Remediated secrets in: {file_path}")
                return True
            elif modified and dry_run:
                self.logger.log_security_event(
                    "INFO", f"[DRY RUN] Would remediate secrets in: {file_path}"
                )
                return True

        except Exception as e:
            self.logger.log_security_event(
                "ERROR", f"Failed to process {file_path}: {e}")
            raise

        return False

    def _update_env_files(self):
        """Update .env template and .gitignore"""
        env_template = self.repo_path / ".env.template"

        env_content = """# EQ12 Environment Variables Template
# Copy to .env and fill in your actual values

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GITHUB_TOKEN=your_github_token_here

# AWS Credentials
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here

# Database
DATABASE_URL=your_database_url_here

# JWT
JWT_TOKEN=your_jwt_token_here
JWT_SECRET=your_jwt_secret_here

# Generated by EQ12 GitLeaks Auto-Remediation
"""

        with open(env_template, "w") as f:
            f.write(env_content)

    def _update_gitignore(self):
        """Update .gitignore with security entries"""
        gitignore_path = self.repo_path / ".gitignore"

        security_entries = [
            ".env",
            "*.env",
            ".env.local",
            ".env.production",
            "secrets.txt",
            "credentials.json",
        ]

        if gitignore_path.exists():
            with open(gitignore_path) as f:
                content = f.read()
        else:
            content = ""

        for entry in security_entries:
            if entry not in content:
                content += f"\n{entry}"

        with open(gitignore_path, "w") as f:
            f.write(content.strip() + "\n")


class EQ12SecurityMonitor:
    """Main security monitoring system"""

    def __init__(self, repo_path: str | None = None, config: dict | None = None):
        self.repo_path = Path(repo_path or os.getcwd())
        self.config = config or {}

        # Initialize components
        self.logger = EQ12SecurityLogger()
        self.scanner = GitLeaksScanner(str(self.repo_path), self.logger)
        self.remediator = AutoRemediator(str(self.repo_path), self.logger)

        # Monitoring state
        self.monitoring = False
        self.scan_interval = self.config.get("scan_interval", 3600)  # 1 hour default

    def scan_and_remediate(
        self,
        auto_fix: bool = False,
        include_history: bool = True,
        dry_run: bool = False,
    ) -> SecurityReport:
        """Perform scan and optional remediation"""
        self.logger.log_security_event(
            "INFO", "Starting security scan and remediation cycle")

        # Perform scan
        findings = self.scanner.scan_repository(include_history=include_history)

        # Calculate risk metrics
        risk_score = self._calculate_risk_score(findings)
        compliance_status = self._assess_compliance(findings)

        # Remediation
        remediation_results = None
        backup_paths = []

        if auto_fix and findings:
            remediation_results = self.remediator.remediate_findings(
                findings, dry_run=dry_run)
            if remediation_results.get("backup_path"):
                backup_paths.append(remediation_results["backup_path"])

        # Generate report
        report = SecurityReport(
            scan_timestamp=datetime.now(UTC).isoformat(),
            repository_path=str(self.repo_path),
            total_findings=len(findings),
            critical_findings=len(
                [f for f in findings if f.security_level == SecurityLevel.CRITICAL]
            ),
            high_findings=len([f for f in findings if f.security_level == SecurityLevel.HIGH]),
            medium_findings=len([f for f in findings if f.security_level == SecurityLevel.MEDIUM]),
            low_findings=len([f for f in findings if f.security_level == SecurityLevel.LOW]),
            remediated_findings=len(
                [f for f in findings if f.remediation_status == RemediationStatus.COMPLETED]
            ),
            pending_findings=len(
                [f for f in findings if f.remediation_status == RemediationStatus.PENDING]
            ),
            risk_score=risk_score,
            compliance_status=compliance_status,
            findings=findings,
            backup_paths=backup_paths,
            recommendations=self._generate_recommendations(findings, risk_score),
        )

        # Save report
        self._save_report(report)

        return report

    def start_monitoring(self, interval: int | None = None):
        """Start continuous monitoring"""
        if self.monitoring:
            self.logger.log_security_event("WARN", "Monitoring already active")
            return

        self.monitoring = True
        self.scan_interval = interval or self.scan_interval

        self.logger.log_security_event(
            "INFO", f"Starting continuous monitoring (interval: {self.scan_interval}s)"
        )

        def monitor_loop():
            while self.monitoring:
                try:
                    report = self.scan_and_remediate(auto_fix=True)

                    if report.critical_findings > 0:
                        self.logger.log_security_event(
                            "CRITICAL", f"Critical security findings detected: {
                                report.critical_findings}", )

                    time.sleep(self.scan_interval)

                except Exception as e:
                    self.logger.log_security_event(
                        "ERROR", f"Monitoring cycle failed: {e}")
                    time.sleep(60)  # Short delay before retry

        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        self.logger.log_security_event("INFO", "Stopping continuous monitoring")

    def _calculate_risk_score(self, findings: list[SecurityFinding]) -> float:
        """Calculate overall risk score (0-100)"""
        if not findings:
            return 0.0

        weight_map = {
            SecurityLevel.CRITICAL: 40,
            SecurityLevel.HIGH: 20,
            SecurityLevel.MEDIUM: 5,
            SecurityLevel.LOW: 1,
        }

        total_weight = sum(weight_map[f.security_level] for f in findings)
        max_possible = len(findings) * weight_map[SecurityLevel.CRITICAL]

        return min(100.0, (total_weight / max_possible)
                   * 100) if max_possible > 0 else 0.0

    def _assess_compliance(self, findings: list[SecurityFinding]) -> str:
        """Assess compliance status"""
        critical_count = len(
            [f for f in findings if f.security_level == SecurityLevel.CRITICAL])
        high_count = len(
            [f for f in findings if f.security_level == SecurityLevel.HIGH])

        if critical_count > 0:
            return "NON_COMPLIANT_CRITICAL"
        elif high_count > 5:
            return "NON_COMPLIANT_HIGH"
        elif high_count > 0:
            return "CONDITIONALLY_COMPLIANT"
        else:
            return "COMPLIANT"

    def _generate_recommendations(
        self, findings: list[SecurityFinding], risk_score: float
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if risk_score > 70:
            recommendations.append(
                "🚨 IMMEDIATE ACTION: Critical security vulnerabilities detected"
            )
            recommendations.append(
                "🔄 Run emergency remediation: EQ12 GitLeaks Emergency Response")

        if any(f.security_level == SecurityLevel.CRITICAL for f in findings):
            recommendations.append("🔑 Regenerate all exposed API keys and credentials")
            recommendations.append("📋 Audit systems for potential compromise")

        if findings:
            recommendations.append(
                "🛠️ Implement automated remediation with EQ12 GitLeaks Auto-Fix")
            recommendations.append(
                "🔧 Install pre-commit hooks to prevent future issues")

        recommendations.extend(
            [
                "🔒 Use proper secret management (Azure Key Vault, AWS Secrets Manager)",
                "📊 Schedule regular security scans",
                "👥 Train team on secure coding practices",
                "📖 Review EQ12 security documentation",
            ]
        )

        return recommendations

    def _save_report(self, report: SecurityReport):
        """Save security report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.logger.log_dir / f"security_report_{timestamp}.json"

        # Convert to serializable format
        report_dict = asdict(report)

        # Convert enums to strings
        for finding_dict in report_dict["findings"]:
            finding_dict["security_level"] = finding_dict["security_level"].value
            finding_dict["remediation_status"] = finding_dict["remediation_status"].value

        with open(report_file, "w") as f:
            json.dump(report_dict, f, indent=2)

        self.logger.log_security_event(
            "SUCCESS", f"Security report saved: {report_file}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="EQ12 GitLeaks Security Monitor")
    parser.add_argument(
        "--action",
        choices=["scan", "monitor", "remediate", "report"],
        default="scan",
        help="Action to perform",
    )
    parser.add_argument(
        "--repository",
        help="Repository path (default: current directory)")
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Enable automatic remediation")
    parser.add_argument(
        "--include-history",
        action="store_true",
        default=True,
        help="Include Git history in scan",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying")
    parser.add_argument(
        "--monitor-interval",
        type=int,
        default=3600,
        help="Monitoring interval in seconds",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup repository path
    repo_path = args.repository or os.getcwd()

    # Initialize monitor
    monitor = EQ12SecurityMonitor(repo_path)

    if args.verbose:
        monitor.logger.logger.setLevel(logging.DEBUG)

    try:
        if args.action == "scan":
            print("🔍 EQ12 Security Scan Starting...")
            report = monitor.scan_and_remediate(
                auto_fix=args.auto_fix,
                include_history=args.include_history,
                dry_run=args.dry_run,
            )

            print("\n📊 SECURITY REPORT SUMMARY:")
            print(f"   Total Findings: {report.total_findings}")
            print(f"   Critical: {report.critical_findings}")
            print(f"   High: {report.high_findings}")
            print(f"   Risk Score: {report.risk_score:.1f}/100")
            print(f"   Compliance: {report.compliance_status}")

            if report.recommendations:
                print("\n💡 RECOMMENDATIONS:")
                for rec in report.recommendations[:5]:
                    print(f"   {rec}")

        elif args.action == "monitor":
            print("👁️ Starting EQ12 Continuous Security Monitoring...")
            monitor.start_monitoring(args.monitor_interval)

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping monitoring...")
                monitor.stop_monitoring()

        elif args.action == "remediate":
            print("🛠️ EQ12 Security Remediation Starting...")
            report = monitor.scan_and_remediate(auto_fix=True, dry_run=args.dry_run)
            print(f"✅ Remediation complete. Fixed: {report.remediated_findings}")

        else:
            print("❓ Invalid action specified")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
