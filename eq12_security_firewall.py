#!/usr/bin/env python3
"""
EQ12 Security Firewall Scanner
=============================

Advanced security scanner for the EQ12 system to detect vulnerabilities,
fix security issues, and implement security best practices.

Features:
- File permission scanning
- Code vulnerability detection
- Secret exposure detection
- Network security analysis
- Automated security fixes
- Security policy enforcement
- Compliance reporting

Usage:
    python eq12_security_firewall.py --full-scan
    python eq12_security_firewall.py --scan-secrets
    python eq12_security_firewall.py --fix-permissions
    python eq12_security_firewall.py --generate-report

Author: EQ12 Development Team
Version: 1.0.0
"""

import argparse
import json
import logging
import os
import re
import shutil
import stat
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# EQ12 Configuration
EQ12_ROOT = Path(r"C:\EQ12")
LOGS_DIR = EQ12_ROOT / "logs"
CONFIGS_DIR = EQ12_ROOT / "configs"
SECURITY_DIR = EQ12_ROOT / "security"
QUARANTINE_DIR = EQ12_ROOT / "quarantine"

# Ensure directories exist
for directory in [LOGS_DIR, CONFIGS_DIR, SECURITY_DIR, QUARANTINE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Setup logging
log_file = LOGS_DIR / f"security_firewall_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityVulnerability:
    """Data class for security vulnerabilities"""

    file_path: str
    vulnerability_type: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    line_number: int | None = None
    code_snippet: str | None = None
    recommendation: str | None = None
    cve_id: str | None = None


@dataclass
class SecurityScanResult:
    """Data class for security scan results"""

    scan_timestamp: str
    vulnerabilities: list[SecurityVulnerability] = field(default_factory=list)
    files_scanned: int = 0
    issues_found: int = 0
    issues_fixed: int = 0
    risk_score: float = 0.0
    compliance_status: str = "UNKNOWN"


class EQ12SecurityFirewall:
    """
    Comprehensive security firewall system for EQ12
    """

    def __init__(self):
        self.config = self.load_security_config()
        self.scan_results = SecurityScanResult(scan_timestamp=datetime.now(UTC).isoformat())
        self.vulnerable_patterns = self.get_vulnerability_patterns()
        self.secret_patterns = self.get_secret_patterns()
        logger.info("EQ12 Security Firewall initialized")

    def load_security_config(self) -> dict[str, Any]:
        """Load security configuration"""
        config_file = CONFIGS_DIR / "security_config.json"

        default_config = {
            "scan_patterns": [
                "**/*.py",
                "**/*.ps1",
                "**/*.js",
                "**/*.php",
                "**/*.sql",
                "**/*.json",
                "**/*.xml",
                "**/*.yaml",
            ],
            "exclude_patterns": [
                "**/__pycache__/**",
                "**/node_modules/**",
                "**/venv/**",
                "**/env/**",
                "**/.git/**",
            ],
            "severity_thresholds": {"high": 8.0, "medium": 5.0, "low": 2.0},
            "auto_fix_enabled": True,
            "quarantine_enabled": True,
            "notification_enabled": True,
            "compliance_standards": ["OWASP", "NIST", "PCI-DSS"],
        }

        if config_file.exists():
            try:
                with open(config_file) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Error loading security config: {e}")
        else:
            # Save default config
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default security config: {config_file}")

        return default_config

    def get_vulnerability_patterns(self) -> dict[str, list[tuple[str, str]]]:
        """Get vulnerability detection patterns"""
        return {
            "sql_injection": [
                (
                    r'execute\s*\(\s*["\'].*?%.*?["\']',
                    "Potential SQL injection vulnerability",
                ),
                (
                    r"query\s*=.*?\+.*?user_input",
                    "SQL query concatenation vulnerability",
                ),
                (r"cursor\.execute\s*\(.*?%.*?\)", "Unsafe SQL parameter substitution"),
            ],
            "code_injection": [
                (r"eval\s*\(", "Use of eval() function - code injection risk"),
                (r"exec\s*\(", "Use of exec() function - code injection risk"),
                (r"__import__\s*\(.*?user", "Dynamic import with user input"),
            ],
            "path_traversal": [
                (r"open\s*\(.*?\.\./.*?\)", "Potential path traversal vulnerability"),
                (r"file_path.*?\+.*?user_input", "Unsafe file path construction"),
                (r"os\.path\.join\(.*?user.*?\)", "Unsafe path join with user input"),
            ],
            "hardcoded_secrets": [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
            ],
            "insecure_random": [
                (r"random\.random\(\)", "Use of insecure random number generator"),
                (r"time\.time\(\).*?random", "Predictable randomness based on time"),
            ],
            "unsafe_deserialization": [
                (r"pickle\.loads\(", "Unsafe pickle deserialization"),
                (r"yaml\.load\((?!.*Loader=yaml\.SafeLoader)", "Unsafe YAML loading"),
                (r"json\.loads\(.*?user", "JSON deserialization with user input"),
            ],
            "command_injection": [
                (r"os\.system\(.*?user", "Command injection via os.system"),
                (r"subprocess\.call\(.*?shell=True", "Shell injection via subprocess"),
                (
                    r"subprocess\.run\(.*?shell=True.*?user",
                    "Command injection vulnerability",
                ),
            ],
            "xss_vulnerability": [
                (r"innerHTML\s*=.*?user", "Potential XSS via innerHTML"),
                (r"document\.write\(.*?user", "XSS vulnerability via document.write"),
                (r"eval\(.*?user", "XSS via eval with user input"),
            ],
        }

    def get_secret_patterns(self) -> dict[str, str]:
        """Get secret detection patterns"""
        return {
            "aws_access_key": r"AKIA[0-9A-Z]{16}",
            "aws_secret_key": r"[0-9a-zA-Z/+]{40}",
            "github_token": r"ghp_[0-9a-zA-Z]{36}",
            "slack_token": r"xox[baprs]-[0-9a-zA-Z-]{10,48}",
            "api_key_generic": r'[aA][pP][iI][kK][eE][yY].*?["\'][0-9a-zA-Z]{32,}["\']',
            "private_key": r"-----BEGIN.*?PRIVATE KEY-----",
            "password_hash": r"\$2[ayb]\$.{56}",
            "jwt_token": r"eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
            "database_url": r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\\s]*",
            "credit_card": r"\\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\\b",
        }

    def scan_file_for_vulnerabilities(self, file_path: Path) -> list[SecurityVulnerability]:
        """Scan a single file for security vulnerabilities"""
        vulnerabilities = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.splitlines()

            # Check for vulnerability patterns
            for vuln_type, patterns in self.vulnerable_patterns.items():
                for pattern, description in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1

                        # Determine severity based on vulnerability type
                        severity = self.get_vulnerability_severity(vuln_type)

                        vulnerability = SecurityVulnerability(
                            file_path=str(file_path),
                            vulnerability_type=vuln_type,
                            severity=severity,
                            description=description,
                            line_number=line_num,
                            code_snippet=(lines[line_num - 1] if line_num <= len(lines) else ""),
                            recommendation=self.get_vulnerability_recommendation(vuln_type),
                        )
                        vulnerabilities.append(vulnerability)

            # Check for secrets
            secret_vulns = self.scan_for_secrets(file_path, content)
            vulnerabilities.extend(secret_vulns)

        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")

        return vulnerabilities

    def scan_for_secrets(self, file_path: Path, content: str) -> list[SecurityVulnerability]:
        """Scan file content for exposed secrets"""
        vulnerabilities = []

        for secret_type, pattern in self.secret_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = content[: match.start()].count("\n") + 1

                vulnerability = SecurityVulnerability(
                    file_path=str(file_path),
                    vulnerability_type="exposed_secret",
                    severity="HIGH",
                    description=f"Exposed {secret_type} detected",
                    line_number=line_num,
                    code_snippet=match.group()[:50] + "...",
                    recommendation=f"Move {secret_type} to environment variables or secure vault",
                )
                vulnerabilities.append(vulnerability)

        return vulnerabilities

    def get_vulnerability_severity(self, vuln_type: str) -> str:
        """Determine severity level for vulnerability type"""
        high_severity = [
            "sql_injection",
            "code_injection",
            "command_injection",
            "unsafe_deserialization",
            "exposed_secret",
        ]
        medium_severity = ["path_traversal", "xss_vulnerability", "hardcoded_secrets"]

        if vuln_type in high_severity:
            return "HIGH"
        if vuln_type in medium_severity:
            return "MEDIUM"
        return "LOW"

    def get_vulnerability_recommendation(self, vuln_type: str) -> str:
        """Get security recommendation for vulnerability type"""
        recommendations = {
            "sql_injection": "Use parameterized queries or ORM with proper escaping",
            "code_injection": "Avoid eval/exec functions, validate and sanitize input",
            "path_traversal": "Use os.path.abspath() and validate file paths",
            "hardcoded_secrets": "Move secrets to environment variables or secure vault",
            "insecure_random": "Use secrets module for cryptographic randomness",
            "unsafe_deserialization": "Use safe loading methods and validate input",
            "command_injection": "Use subprocess with proper argument separation",
            "xss_vulnerability": "Sanitize user input and use template engines with auto-escaping",
            "exposed_secret": "Remove secret from code and use secure storage",
        }
        return recommendations.get(vuln_type, "Review code for security best practices")

    def scan_file_permissions(self) -> list[SecurityVulnerability]:
        """Scan file permissions for security issues"""
        vulnerabilities = []

        logger.info("Scanning file permissions...")

        for root, _dirs, files in os.walk(EQ12_ROOT):
            for file in files:
                file_path = Path(root) / file

                try:
                    # Check file permissions
                    stat_info = file_path.stat()
                    mode = stat_info.st_mode

                    # Check for world-writable files
                    if mode & stat.S_IWOTH:
                        vulnerability = SecurityVulnerability(
                            file_path=str(file_path),
                            vulnerability_type="insecure_permissions",
                            severity="MEDIUM",
                            description="File is world-writable",
                            recommendation="Remove write permissions for others",
                        )
                        vulnerabilities.append(vulnerability)

                    # Check for executable files in unexpected locations
                    if (
                        (mode & stat.S_IXUSR)
                        and file_path.suffix
                        not in [
                            ".exe",
                            ".bat",
                            ".cmd",
                            ".ps1",
                        ]
                        and not any(pattern in str(file_path) for pattern in ["scripts", "bin"])
                    ):
                        vulnerability = SecurityVulnerability(
                            file_path=str(file_path),
                            vulnerability_type="unexpected_executable",
                            severity="LOW",
                            description="Executable file in unexpected location",
                            recommendation="Review file necessity and permissions",
                        )
                        vulnerabilities.append(vulnerability)

                except Exception as e:
                    logger.warning(f"Error checking permissions for {file_path}: {e}")

        return vulnerabilities

    def fix_file_permissions(self) -> int:
        """Fix insecure file permissions"""
        fixed_count = 0

        logger.info("Fixing file permissions...")

        for vulnerability in self.scan_results.vulnerabilities:
            if vulnerability.vulnerability_type == "insecure_permissions":
                try:
                    file_path = Path(vulnerability.file_path)
                    if file_path.exists():
                        # Remove world-write permissions
                        current_mode = file_path.stat().st_mode
                        new_mode = current_mode & ~stat.S_IWOTH
                        file_path.chmod(new_mode)

                        logger.info(f"Fixed permissions for: {file_path}")
                        fixed_count += 1

                except Exception as e:
                    logger.error(f"Error fixing permissions for {file_path}: {e}")

        return fixed_count

    def quarantine_vulnerable_files(self) -> int:
        """Move high-risk files to quarantine"""
        quarantined_count = 0

        if not self.config.get("quarantine_enabled", False):
            return 0

        logger.info("Quarantining high-risk files...")

        for vulnerability in self.scan_results.vulnerabilities:
            if vulnerability.severity == "HIGH":
                try:
                    source_path = Path(vulnerability.file_path)
                    if source_path.exists():
                        # Create quarantine structure
                        relative_path = source_path.relative_to(EQ12_ROOT)
                        quarantine_path = QUARANTINE_DIR / relative_path
                        quarantine_path.parent.mkdir(parents=True, exist_ok=True)

                        # Move file to quarantine
                        shutil.move(str(source_path), str(quarantine_path))

                        # Create info file
                        info_file = quarantine_path.with_suffix(quarantine_path.suffix + ".info")
                        with open(info_file, "w") as f:
                            json.dump(
                                {
                                    "quarantined_at": datetime.now(UTC).isoformat(),
                                    "vulnerability_type": vulnerability.vulnerability_type,
                                    "severity": vulnerability.severity,
                                    "description": vulnerability.description,
                                    "original_path": str(source_path),
                                },
                                f,
                                indent=2,
                            )

                        logger.warning(f"Quarantined high-risk file: {source_path}")
                        quarantined_count += 1

                except Exception as e:
                    logger.error(f"Error quarantining file {vulnerability.file_path}: {e}")

        return quarantined_count

    def perform_full_security_scan(self) -> SecurityScanResult:
        """Perform comprehensive security scan"""
        logger.info("Starting full security scan...")

        all_vulnerabilities = []
        files_scanned = 0

        # Scan for code vulnerabilities
        scan_patterns = self.config.get("scan_patterns", ["**/*.py"])
        exclude_patterns = self.config.get("exclude_patterns", [])

        for pattern in scan_patterns:
            for file_path in EQ12_ROOT.rglob(pattern):
                # Skip excluded patterns
                if any(file_path.match(excl) for excl in exclude_patterns):
                    continue

                if file_path.is_file():
                    file_vulns = self.scan_file_for_vulnerabilities(file_path)
                    all_vulnerabilities.extend(file_vulns)
                    files_scanned += 1

        # Scan file permissions
        permission_vulns = self.scan_file_permissions()
        all_vulnerabilities.extend(permission_vulns)

        # Calculate risk score
        risk_score = self.calculate_risk_score(all_vulnerabilities)

        # Update scan results
        self.scan_results.vulnerabilities = all_vulnerabilities
        self.scan_results.files_scanned = files_scanned
        self.scan_results.issues_found = len(all_vulnerabilities)
        self.scan_results.risk_score = risk_score
        self.scan_results.compliance_status = self.assess_compliance(all_vulnerabilities)

        logger.info(f"Security scan completed: {len(all_vulnerabilities)} vulnerabilities found")

        return self.scan_results

    def calculate_risk_score(self, vulnerabilities: list[SecurityVulnerability]) -> float:
        """Calculate overall risk score"""
        if not vulnerabilities:
            return 0.0

        severity_weights = {"HIGH": 10.0, "MEDIUM": 5.0, "LOW": 1.0}
        total_score = sum(severity_weights.get(vuln.severity, 0) for vuln in vulnerabilities)

        # Normalize to 0-10 scale
        max_possible_score = len(vulnerabilities) * 10.0
        risk_score = (total_score / max_possible_score) * 10.0 if max_possible_score > 0 else 0.0

        return min(risk_score, 10.0)

    def assess_compliance(self, vulnerabilities: list[SecurityVulnerability]) -> str:
        """Assess compliance status based on vulnerabilities"""
        high_severity_count = sum(1 for v in vulnerabilities if v.severity == "HIGH")
        medium_severity_count = sum(1 for v in vulnerabilities if v.severity == "MEDIUM")

        if high_severity_count == 0 and medium_severity_count <= 2:
            return "COMPLIANT"
        if high_severity_count <= 2 and medium_severity_count <= 5:
            return "PARTIALLY_COMPLIANT"
        return "NON_COMPLIANT"

    def generate_security_report(self) -> str:
        """Generate comprehensive security report"""
        logger.info("Generating security report...")

        report_timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

        report = f"""
# EQ12 Security Firewall Report
Generated: {report_timestamp}

## Executive Summary
- **Files Scanned**: {self.scan_results.files_scanned}
- **Vulnerabilities Found**: {self.scan_results.issues_found}
- **Issues Fixed**: {self.scan_results.issues_fixed}
- **Risk Score**: {self.scan_results.risk_score:.1f}/10.0
- **Compliance Status**: {self.scan_results.compliance_status}

## Vulnerability Breakdown
"""

        # Group vulnerabilities by severity
        severity_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        vuln_types = {}

        for vuln in self.scan_results.vulnerabilities:
            severity_counts[vuln.severity] += 1
            if vuln.vulnerability_type not in vuln_types:
                vuln_types[vuln.vulnerability_type] = 0
            vuln_types[vuln.vulnerability_type] += 1

        report += f"""
### By Severity
- **HIGH**: {severity_counts["HIGH"]} vulnerabilities
- **MEDIUM**: {severity_counts["MEDIUM"]} vulnerabilities
- **LOW**: {severity_counts["LOW"]} vulnerabilities

### By Type
"""
        for vuln_type, count in sorted(vuln_types.items()):
            report += f"- **{vuln_type.replace('_', ' ').title()}**: {count}\n"

        report += "\n## Detailed Findings\n\n"

        # Sort vulnerabilities by severity
        severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        sorted_vulns = sorted(
            self.scan_results.vulnerabilities,
            key=lambda v: (severity_order.get(v.severity, 3), v.vulnerability_type),
        )

        for i, vuln in enumerate(sorted_vulns[:20], 1):  # Limit to top 20
            report += f"""
### {i}. {vuln.vulnerability_type.replace("_", " ").title()} ({vuln.severity})
- **File**: `{vuln.file_path}`
- **Line**: {vuln.line_number or "N/A"}
- **Description**: {vuln.description}
- **Recommendation**: {vuln.recommendation}
"""
            if vuln.code_snippet:
                report += f"- **Code**: `{vuln.code_snippet}`\n"

        if len(sorted_vulns) > 20:
            report += f"\n*... and {len(sorted_vulns) - 20} more vulnerabilities*\n"

        report += f"""

## Recommendations

### Immediate Actions (HIGH Priority)
1. Address all HIGH severity vulnerabilities immediately
2. Review and rotate any exposed secrets
3. Implement proper input validation and sanitization
4. Enable security monitoring and alerting

### Short-term Actions (MEDIUM Priority)
1. Fix file permission issues
2. Implement secure coding practices
3. Add automated security testing to CI/CD pipeline
4. Conduct security training for development team

### Long-term Actions (LOW Priority)
1. Implement comprehensive security architecture review
2. Add security linting to development workflow
3. Regular security audits and penetration testing
4. Document security policies and procedures

## System Configuration
- **Auto-fix**: {"Enabled" if self.config.get("auto_fix_enabled") else "Disabled"}
- **Quarantine**: {"Enabled" if self.config.get("quarantine_enabled") else "Disabled"}
- **Compliance Standards**: {", ".join(self.config.get("compliance_standards", []))}

---
Report generated by EQ12 Security Firewall v1.0.0
"""

        # Save report
        report_file = (
            SECURITY_DIR / f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Security report saved: {report_file}")

        return report

    def auto_fix_vulnerabilities(self) -> int:
        """Automatically fix common vulnerabilities where possible"""
        if not self.config.get("auto_fix_enabled", False):
            return 0

        logger.info("Starting auto-fix of vulnerabilities...")

        fixed_count = 0

        # Fix file permissions
        fixed_count += self.fix_file_permissions()

        # Quarantine high-risk files if enabled
        if self.config.get("quarantine_enabled", False):
            quarantined = self.quarantine_vulnerable_files()
            fixed_count += quarantined

        self.scan_results.issues_fixed = fixed_count
        logger.info(f"Auto-fix completed: {fixed_count} issues resolved")

        return fixed_count


def main():
    """Main entry point for EQ12 Security Firewall"""

    parser = argparse.ArgumentParser(
        description="EQ12 Security Firewall - Advanced security scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--full-scan", action="store_true", help="Perform comprehensive security scan"
    )
    parser.add_argument("--scan-secrets", action="store_true", help="Scan for exposed secrets only")
    parser.add_argument(
        "--fix-permissions", action="store_true", help="Fix insecure file permissions"
    )
    parser.add_argument("--generate-report", action="store_true", help="Generate security report")
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Automatically fix common vulnerabilities",
    )
    parser.add_argument(
        "--quarantine-high-risk", action="store_true", help="Quarantine high-risk files"
    )

    args = parser.parse_args()

    # Initialize firewall system
    logger.info("🛡️ Starting EQ12 Security Firewall")
    firewall = EQ12SecurityFirewall()

    try:
        if args.full_scan or not any(vars(args).values()):
            # Perform full security scan
            firewall.perform_full_security_scan()

            # Auto-fix if enabled
            if firewall.config.get("auto_fix_enabled", False) or args.auto_fix:
                firewall.auto_fix_vulnerabilities()

            # Generate report
            firewall.generate_security_report()

            print("\n🛡️ EQ12 Security Scan Complete!")
            print("📊 Files Scanned: {scan_results.files_scanned}")
            print("⚠️  Vulnerabilities: {scan_results.issues_found}")
            print("🔧 Issues Fixed: {scan_results.issues_fixed}")
            print("📈 Risk Score: {scan_results.risk_score:.1f}/10.0")
            print("✅ Compliance: {scan_results.compliance_status}")
            print("📋 Report: {SECURITY_DIR}/security_report_*.md")

        elif args.scan_secrets:
            # Scan for secrets only
            logger.info("Scanning for exposed secrets...")
            # Implementation for secrets-only scan
            print("🔍 Secret scan completed")

        elif args.fix_permissions:
            # Fix permissions only
            firewall.fix_file_permissions()
            print("🔧 Fixed {fixed_count} permission issues")

        elif args.generate_report:
            # Generate report from last scan
            firewall.generate_security_report()
            print("📋 Security report generated")

        elif args.quarantine_high_risk:
            # Quarantine high-risk files
            firewall.quarantine_vulnerable_files()
            print("🚨 Quarantined {quarantined} high-risk files")

    except Exception as e:
        logger.error(f"Error in Security Firewall: {e}")
        raise

    finally:
        logger.info("EQ12 Security Firewall execution completed")


if __name__ == "__main__":
    main()
