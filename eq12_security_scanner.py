#!/usr/bin/env python3
"""
EQ12 Security Scanner

Scans the EQ12 codebase for security vulnerabilities:
- Hardcoded API keys and secrets
- Insecure coding patterns
- Personal data exposure
- File permission issues
- Dependency vulnerabilities

Usage:
    python eq12_security_scanner.py --scan-all
    python eq12_security_scanner.py --scan-secrets
    python eq12_security_scanner.py --scan-files
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any


class SecurityIssue:
    def __init__(
        self,
        severity: str,
        category: str,
        file_path: str,
        line_number: int,
        description: str,
        content: str = "",
    ):
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.category = category  # SECRET, PERSONAL, INSECURE, PERMISSION
        self.file_path = file_path
        self.line_number = line_number
        self.description = description
        self.content = content
        self.timestamp = datetime.now().isoformat()


class EQ12SecurityScanner:
    """Security scanner for EQ12 automation platform"""

    def __init__(self, eq12_home: str | None = None):
        self.eq12_home = Path(eq12_home) if eq12_home else Path(os.getenv("EQ12_HOME", r"C:\EQ12"))
        self.issues: list[SecurityIssue] = []

        # Secret patterns to detect
        self.secret_patterns = {
            "openai_api_key": r"sk-[a-zA-Z0-9]{48,}",
            "telegram_token": r"\d{8,10}:[a-zA-Z0-9_-]{35}",
            "aws_access_key": r"AKIA[0-9A-Z]{16}",
            "aws_secret_key": r"[a-zA-Z0-9/+=]{40}",
            "generic_api_key": r'["\']?[a-zA-Z0-9_-]{32,}["\']?',
            "password_hardcoded": r'password\s*=\s*["\'][^"\']{6,}["\']',
            "secret_hardcoded": r'secret\s*=\s*["\'][^"\']+["\']',
        }

        # Personal data patterns
        self.personal_patterns = {
            "email_address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone_number": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        }

        # Insecure coding patterns
        self.insecure_patterns = {
            "sql_injection": r'(?i)(SELECT|INSERT|UPDATE|DELETE).*\+.*[\'"]\s*\+',
            "command_injection": r"(?i)(os\.system|subprocess\.call|exec|eval)\s*\(",
            "hardcoded_ip": r"\b(?:192\.168|10\.|172\.(?:1[6-9]|2[0-9]|3[01])|127\.0\.0\.1)\.",
            "insecure_random": r"random\.random\(\)|Math\.random\(\)",
            "debug_enabled": r"(?i)debug\s*=\s*true",
            "ssl_disabled": r"(?i)verify\s*=\s*false|ssl_verify.*false",
        }

        # Files to scan
        self.scannable_extensions = {
            ".py",
            ".ps1",
            ".js",
            ".json",
            ".yaml",
            ".yml",
            ".txt",
            ".md",
            ".env",
        }

        # Files/directories to skip
        self.skip_paths = {
            "__pycache__",
            ".git",
            "node_modules",
            ".vs",
            "logs",
            "data",
            "keys",
            "archive",
            ".pytest_cache",
            "build",
            "dist",
        }

    def scan_file_for_secrets(self, file_path: Path) -> list[SecurityIssue]:
        """Scan individual file for hardcoded secrets"""
        issues = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_content = line.strip()

                # Skip comments and empty lines for some patterns
                if line_content.startswith("#") or not line_content:
                    continue

                # Check secret patterns
                for pattern_name, pattern in self.secret_patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        # Skip obvious placeholders
                        matched_text = match.group()
                        if any(
                            placeholder in matched_text.lower()
                            for placeholder in [
                                "placeholder",
                                "replace",
                                "your_",
                                "example",
                                "test_",
                            ]
                        ):
                            continue

                        issues.append(
                            SecurityIssue(
                                severity="CRITICAL",
                                category="SECRET",
                                file_path=str(file_path),
                                line_number=line_num,
                                description=f"Hardcoded {pattern_name} detected",
                                content=(
                                    matched_text[:50] + "..."
                                    if len(matched_text) > 50
                                    else matched_text
                                ),
                            )
                        )

                # Check personal data patterns
                for pattern_name, pattern in self.personal_patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        issues.append(
                            SecurityIssue(
                                severity="HIGH",
                                category="PERSONAL",
                                file_path=str(file_path),
                                line_number=line_num,
                                description=f"Personal data ({pattern_name}) detected",
                                content=match.group(),
                            )
                        )

                # Check insecure patterns
                for pattern_name, pattern in self.insecure_patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        issues.append(
                            SecurityIssue(
                                severity="MEDIUM",
                                category="INSECURE",
                                file_path=str(file_path),
                                line_number=line_num,
                                description=f"Insecure pattern ({pattern_name}) detected",
                                content=match.group(),
                            )
                        )

        except Exception as e:
            issues.append(
                SecurityIssue(
                    severity="LOW",
                    category="SCAN_ERROR",
                    file_path=str(file_path),
                    line_number=0,
                    description=f"Could not scan file: {e}",
                    content="",
                )
            )

        return issues

    def scan_directory(self, directory: Path) -> list[SecurityIssue]:
        """Recursively scan directory for security issues"""
        issues = []

        for file_path in directory.rglob("*"):
            # Skip directories and non-scannable files
            if not file_path.is_file():
                continue

            # Skip excluded paths
            if any(skip in str(file_path) for skip in self.skip_paths):
                continue

            # Skip non-scannable extensions
            if file_path.suffix not in self.scannable_extensions:
                continue

            # Scan the file
            file_issues = self.scan_file_for_secrets(file_path)
            issues.extend(file_issues)

        return issues

    def check_file_permissions(self) -> list[SecurityIssue]:
        """Check file permissions for sensitive directories (Windows)"""
        issues = []

        if os.name != "nt":
            return issues  # Only check on Windows

        sensitive_dirs = [
            self.eq12_home / "keys",
            self.eq12_home / "logs",
            self.eq12_home / "data",
        ]

        for dir_path in sensitive_dirs:
            if not dir_path.exists():
                continue

            try:
                # Check if directory has proper permissions (simplified check)
                test_file = dir_path / "perm_test.tmp"
                test_file.touch()
                test_file.unlink()

                # In a full implementation, would use Windows APIs to check ACLs
                # For now, just verify basic access works

            except PermissionError:
                issues.append(
                    SecurityIssue(
                        severity="MEDIUM",
                        category="PERMISSION",
                        file_path=str(dir_path),
                        line_number=0,
                        description="Directory permission issue detected",
                        content="Cannot write to sensitive directory",
                    )
                )

        return issues

    def check_gitignore_coverage(self) -> list[SecurityIssue]:
        """Check if .gitignore properly covers sensitive files"""
        issues = []
        gitignore_path = self.eq12_home / ".gitignore"

        if not gitignore_path.exists():
            issues.append(
                SecurityIssue(
                    severity="HIGH",
                    category="SECURITY_CONFIG",
                    file_path=str(gitignore_path),
                    line_number=0,
                    description=".gitignore file missing",
                    content="",
                )
            )
            return issues

        try:
            with open(gitignore_path) as f:
                gitignore_content = f.read()

            # Check for required security patterns
            required_patterns = [
                "keys/",
                "*.key",
                ".env",
                "credentials.*",
                "secrets.*",
                "logs/",
                "data/",
                "*.db",
                "*.sqlite",
            ]

            for pattern in required_patterns:
                if pattern not in gitignore_content:
                    issues.append(
                        SecurityIssue(
                            severity="MEDIUM",
                            category="SECURITY_CONFIG",
                            file_path=str(gitignore_path),
                            line_number=0,
                            description=f"Missing .gitignore pattern: {pattern}",
                            content=pattern,
                        )
                    )

        except Exception as e:
            issues.append(
                SecurityIssue(
                    severity="LOW",
                    category="SCAN_ERROR",
                    file_path=str(gitignore_path),
                    line_number=0,
                    description=f"Could not read .gitignore: {e}",
                    content="",
                )
            )

        return issues

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive security report"""
        # Group issues by severity
        by_severity = {}
        by_category = {}
        by_file = {}

        for issue in self.issues:
            # By severity
            if issue.severity not in by_severity:
                by_severity[issue.severity] = []
            by_severity[issue.severity].append(issue)

            # By category
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)

            # By file
            if issue.file_path not in by_file:
                by_file[issue.file_path] = []
            by_file[issue.file_path].append(issue)

        # Calculate risk score
        severity_weights = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 1}
        risk_score = sum(severity_weights.get(issue.severity, 0) for issue in self.issues)

        return {
            "scan_timestamp": datetime.now().isoformat(),
            "total_issues": len(self.issues),
            "risk_score": risk_score,
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "by_category": {k: len(v) for k, v in by_category.items()},
            "by_file": {k: len(v) for k, v in by_file.items()},
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "description": issue.description,
                    "content": issue.content,
                    "timestamp": issue.timestamp,
                }
                for issue in self.issues
            ],
        }

    def run_full_scan(self):
        """Run comprehensive security scan"""
        print("🔍 Starting EQ12 Security Scan...")
        print(f"📁 Scanning directory: {self.eq12_home}")
        print()

        # Scan for secrets in files
        print("🔐 Scanning for hardcoded secrets...")
        secret_issues = self.scan_directory(self.eq12_home)
        self.issues.extend(secret_issues)

        # Check file permissions
        print("🔒 Checking file permissions...")
        perm_issues = self.check_file_permissions()
        self.issues.extend(perm_issues)

        # Check .gitignore coverage
        print("📝 Validating .gitignore coverage...")
        gitignore_issues = self.check_gitignore_coverage()
        self.issues.extend(gitignore_issues)

        # Generate report
        report = self.generate_report()

        print()
        print("=" * 50)
        print("🛡️ EQ12 SECURITY SCAN RESULTS")
        print("=" * 50)

        if self.issues:
            print(f"⚠️  {len(self.issues)} security issues found")
            print(f"🎯 Risk Score: {report['risk_score']}")
            print()

            # Show by severity
            for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
                count = report["by_severity"].get(severity, 0)
                if count > 0:
                    emoji = {"CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "ℹ️"}
                    print(f"{emoji[severity]} {severity}: {count}")

            print()
            print("Top Issues:")
            for i, issue in enumerate(self.issues[:5], 1):
                print(f"{i}. {issue.severity} - {issue.description}")
                print(f"   📁 {issue.file_path}:{issue.line_number}")
                if issue.content:
                    print(f"   💬 {issue.content}")
                print()

        else:
            print("✅ No security issues found!")

        # Save detailed report
        report_file = self.eq12_home / "logs" / "security_report.json"
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📊 Detailed report saved: {report_file}")

        return len(self.issues) == 0


def main():
    parser = argparse.ArgumentParser(description="EQ12 Security Scanner")
    parser.add_argument("--scan-all", action="store_true", help="Run full security scan")
    parser.add_argument("--scan-secrets", action="store_true", help="Scan for secrets only")
    parser.add_argument("--scan-files", action="store_true", help="Scan file permissions only")
    parser.add_argument("--eq12-home", help="EQ12 home directory")

    args = parser.parse_args()

    scanner = EQ12SecurityScanner(args.eq12_home)

    if args.scan_all or not any([args.scan_secrets, args.scan_files]):
        success = scanner.run_full_scan()
        exit(0 if success else 1)

    elif args.scan_secrets:
        print("🔐 Scanning for secrets...")
        issues = scanner.scan_directory(scanner.eq12_home)
        scanner.issues.extend(issues)

    elif args.scan_files:
        print("🔒 Checking file permissions...")
        issues = scanner.check_file_permissions()
        scanner.issues.extend(issues)

    if scanner.issues:
        for issue in scanner.issues:
            print(f"{issue.severity}: {issue.description} in {issue.file_path}:{issue.line_number}")
        exit(1)
    else:
        print("✅ No issues found")
        exit(0)


if __name__ == "__main__":
    main()
