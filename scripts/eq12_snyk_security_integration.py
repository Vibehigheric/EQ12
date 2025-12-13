#!/usr/bin/env python3
"""
EQ12 Snyk Security Integration System
Comprehensive security scanning and vulnerability detection for the EQ12 betting platform

Based on Snyk documentation analysis:
- Snyk Code: Static Application Security Testing (SAST) with AI-based engine
- Snyk Open Source: Software Composition Analysis (SCA) for dependencies
- Snyk CLI: Command-line security scanning and monitoring
- Snyk API: Programmatic security automation and reporting

Author: EQ12 Security Team
Created: 2024
Version: 1.0.0
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/snyk_security.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityVulnerability:
    """Structured vulnerability representation"""

    id: str
    severity: str
    title: str
    description: str
    file_path: str | None
    line_number: int | None
    cwe: str | None
    cvss_score: float | None
    fix_guidance: str | None
    package_name: str | None
    package_version: str | None
    scan_type: str
    detected_at: str


@dataclass
class SecurityScanResult:
    """Comprehensive security scan results"""

    scan_id: str
    project_path: str
    scan_timestamp: str
    scan_types: list[str]
    total_vulnerabilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    vulnerabilities: list[SecurityVulnerability]
    scan_metadata: dict[str, Any]
    recommendations: list[str]


class SnykSecurityScanner:
    """Advanced security scanner using Snyk capabilities"""

    def __init__(self):
        self.snyk_token = os.getenv("SNYK_TOKEN")
        self.api_base = "https://api.snyk.io/v1"
        self.project_root = Path("C:/EQ12")
        self.logs_dir = Path("C:/EQ12/logs")
        self.logs_dir.mkdir(exist_ok=True)

        # EQ12 specific scanning targets
        self.scan_targets = {
            "scripts": self.project_root / "scripts",
            "tests": self.project_root / "tests",
            "configs": self.project_root / "configs",
            "dashboard": self.project_root / "dashboard",
        }

        logger.info("EQ12 Snyk Security Scanner initialized")

    async def check_snyk_installation(self) -> bool:
        """Verify Snyk CLI is installed and configured"""
        try:
            result = subprocess.run(
                ["snyk", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info(f"Snyk CLI detected: {result.stdout.strip()}")
                return True
            else:
                logger.warning("Snyk CLI not found or not working")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"Snyk CLI check failed: {e}")
            return False

    async def install_snyk_cli(self) -> bool:
        """Install Snyk CLI using multiple methods"""
        logger.info("Installing Snyk CLI...")

        # Method 1: Try npm installation
        try:
            result = subprocess.run(
                ["npm", "install", "-g", "snyk"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                logger.info("Snyk CLI installed via npm")
                return await self.check_snyk_installation()
        except Exception as e:
            logger.warning(f"npm installation failed: {e}")

        # Method 2: Try standalone executable download
        try:
            import urllib.request

            # Download Windows executable
            url = "https://downloads.snyk.io/cli/stable/snyk-win.exe"
            snyk_path = self.project_root / "snyk.exe"

            logger.info(f"Downloading Snyk CLI from {url}")
            urllib.request.urlretrieve(url, snyk_path)

            # Make executable and test
            if snyk_path.exists():
                logger.info("Snyk CLI standalone executable downloaded")
                return True

        except Exception as e:
            logger.error(f"Standalone installation failed: {e}")

        return False

    async def authenticate_snyk(self) -> bool:
        """Authenticate Snyk CLI with API token"""
        if not self.snyk_token:
            logger.error("SNYK_TOKEN environment variable not set")
            logger.info("Please set SNYK_TOKEN or run 'snyk auth' manually")
            return False

        try:
            # Set token via environment for CLI
            env = os.environ.copy()
            env["SNYK_TOKEN"] = self.snyk_token

            result = subprocess.run(
                ["snyk", "auth", self.snyk_token],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )

            if result.returncode == 0:
                logger.info("Snyk authentication successful")
                return True
            else:
                logger.error(f"Snyk auth failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    async def scan_code_security(
            self, target_path: Path) -> list[SecurityVulnerability]:
        """Perform static code analysis using Snyk Code"""
        vulnerabilities = []

        try:
            logger.info(f"Running Snyk Code scan on {target_path}")

            cmd = ["snyk", "code", "test", str(target_path), "--json"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300, cwd=str(target_path)
            )

            if result.stdout:
                try:
                    scan_data = json.loads(result.stdout)

                    # Parse Snyk Code results
                    if scan_data.get("runs"):
                        for run in scan_data["runs"]:
                            if "results" in run:
                                for vuln in run["results"]:
                                    vulnerability = SecurityVulnerability(
                                        id=vuln.get("ruleId", "SNYK-CODE-UNKNOWN"),
                                        severity=vuln.get("level", "unknown").upper(),
                                        title=vuln.get("message", {}).get(
                                            "text", "Code vulnerability"
                                        ),
                                        description=self._extract_description(vuln),
                                        file_path=self._extract_file_path(
                                            vuln, target_path),
                                        line_number=self._extract_line_number(vuln),
                                        cwe=self._extract_cwe(vuln),
                                        cvss_score=None,  # Snyk Code uses different scoring
                                        fix_guidance=self._extract_fix_guidance(vuln),
                                        package_name=None,
                                        package_version=None,
                                        scan_type="SAST",
                                        detected_at=datetime.now(UTC).isoformat(),
                                    )
                                    vulnerabilities.append(vulnerability)

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Snyk Code JSON: {e}")

        except subprocess.TimeoutExpired:
            logger.error(f"Snyk Code scan timeout for {target_path}")
        except Exception as e:
            logger.error(f"Snyk Code scan failed: {e}")

        logger.info(f"Found {len(vulnerabilities)} code vulnerabilities")
        return vulnerabilities

    async def scan_open_source_dependencies(
            self, target_path: Path) -> list[SecurityVulnerability]:
        """Scan for open source vulnerabilities using Snyk Open Source"""
        vulnerabilities = []

        try:
            logger.info(f"Running Snyk Open Source scan on {target_path}")

            cmd = ["snyk", "test", str(target_path), "--json"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300, cwd=str(target_path)
            )

            if result.stdout:
                try:
                    scan_data = json.loads(result.stdout)

                    # Parse open source vulnerabilities
                    if "vulnerabilities" in scan_data:
                        for vuln in scan_data["vulnerabilities"]:
                            vulnerability = SecurityVulnerability(
                                id=vuln.get(
                                    "id",
                                    "SNYK-OS-UNKNOWN"),
                                severity=vuln.get(
                                    "severity",
                                    "unknown").upper(),
                                title=vuln.get(
                                    "title",
                                    "Dependency vulnerability"),
                                description=vuln.get(
                                    "description",
                                    ""),
                                file_path=(
                                    vuln.get(
                                        "from",
                                        [None])[0] if vuln.get("from") else None),
                                line_number=None,
                                cwe=(
                                    vuln.get(
                                        "identifiers",
                                        {}).get(
                                        "CWE",
                                        [None])[0] if vuln.get(
                                            "identifiers",
                                            {}).get("CWE") else None),
                                cvss_score=vuln.get("cvssScore"),
                                fix_guidance=self._extract_os_fix_guidance(vuln),
                                package_name=vuln.get("packageName"),
                                package_version=vuln.get("version"),
                                scan_type="SCA",
                                detected_at=datetime.now(UTC).isoformat(),
                            )
                            vulnerabilities.append(vulnerability)

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Snyk OS JSON: {e}")

        except subprocess.TimeoutExpired:
            logger.error(f"Snyk OS scan timeout for {target_path}")
        except Exception as e:
            logger.error(f"Snyk OS scan failed: {e}")

        logger.info(f"Found {len(vulnerabilities)} dependency vulnerabilities")
        return vulnerabilities

    async def scan_infrastructure_as_code(
            self, target_path: Path) -> list[SecurityVulnerability]:
        """Scan Infrastructure as Code files for security issues"""
        vulnerabilities = []

        try:
            logger.info(f"Running Snyk IaC scan on {target_path}")

            cmd = ["snyk", "iac", "test", str(target_path), "--json"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300, cwd=str(target_path)
            )

            if result.stdout:
                try:
                    scan_data = json.loads(result.stdout)

                    # Parse IaC vulnerabilities
                    if "infrastructureAsCodeIssues" in scan_data:
                        for issue in scan_data["infrastructureAsCodeIssues"]:
                            vulnerability = SecurityVulnerability(
                                id=issue.get(
                                    "id",
                                    "SNYK-IAC-UNKNOWN"),
                                severity=issue.get(
                                    "severity",
                                    "unknown").upper(),
                                title=issue.get(
                                    "title",
                                    "Infrastructure security issue"),
                                description=issue.get(
                                    "description",
                                    ""),
                                file_path=issue.get("targetFile"),
                                line_number=issue.get("lineNumber"),
                                cwe=None,
                                cvss_score=None,
                                fix_guidance=issue.get(
                                    "remediation",
                                    {}).get(
                                    "advice",
                                    "No fix guidance available"),
                                package_name=None,
                                package_version=None,
                                scan_type="IAC",
                                detected_at=datetime.now(UTC).isoformat(),
                            )
                            vulnerabilities.append(vulnerability)

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Snyk IaC JSON: {e}")

        except subprocess.TimeoutExpired:
            logger.error(f"Snyk IaC scan timeout for {target_path}")
        except Exception as e:
            logger.error(f"Snyk IaC scan failed: {e}")

        logger.info(f"Found {len(vulnerabilities)} infrastructure vulnerabilities")
        return vulnerabilities

    async def generate_security_report(self, scan_result: SecurityScanResult) -> str:
        """Generate comprehensive security report"""
        report_path = (
            self.logs_dir /
            f"security_report_{
                datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        # Create detailed report
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "eq12_version": "1.0.0",
                "snyk_integration": "enabled",
                "scan_coverage": list(self.scan_targets.keys()),
            },
            "executive_summary": {
                "total_vulnerabilities": scan_result.total_vulnerabilities,
                "critical_vulnerabilities": scan_result.critical_count,
                "high_vulnerabilities": scan_result.high_count,
                "medium_vulnerabilities": scan_result.medium_count,
                "low_vulnerabilities": scan_result.low_count,
                "risk_score": self._calculate_risk_score(scan_result),
                "compliance_status": self._assess_compliance_status(scan_result),
            },
            "scan_results": asdict(scan_result),
            "vulnerability_breakdown": self._create_vulnerability_breakdown(scan_result),
            "remediation_priorities": self._create_remediation_priorities(scan_result),
            "security_recommendations": self._generate_security_recommendations(scan_result),
        }

        # Save detailed report
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Security report generated: {report_path}")
        return str(report_path)

    async def run_comprehensive_security_scan(self) -> SecurityScanResult:
        """Execute comprehensive security scanning across all EQ12 components"""
        logger.info("Starting comprehensive EQ12 security scan")

        # Check Snyk installation and authentication
        if not await self.check_snyk_installation() and not await self.install_snyk_cli():
            raise RuntimeError("Failed to install Snyk CLI")

        if not await self.authenticate_snyk():
            logger.warning("Snyk authentication failed, continuing with basic scans")

        all_vulnerabilities = []
        scan_types = []

        # Scan each target directory
        for target_name, target_path in self.scan_targets.items():
            if not target_path.exists():
                logger.warning(f"Target path does not exist: {target_path}")
                continue

            logger.info(f"Scanning {target_name}: {target_path}")

            # Code security scan
            code_vulns = await self.scan_code_security(target_path)
            all_vulnerabilities.extend(code_vulns)
            if code_vulns:
                scan_types.append("SAST")

            # Open source dependency scan
            os_vulns = await self.scan_open_source_dependencies(target_path)
            all_vulnerabilities.extend(os_vulns)
            if os_vulns:
                scan_types.append("SCA")

            # Infrastructure as Code scan
            iac_vulns = await self.scan_infrastructure_as_code(target_path)
            all_vulnerabilities.extend(iac_vulns)
            if iac_vulns:
                scan_types.append("IAC")

        # Count vulnerabilities by severity
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for vuln in all_vulnerabilities:
            if vuln.severity in severity_counts:
                severity_counts[vuln.severity] += 1

        # Create comprehensive scan result
        scan_result = SecurityScanResult(
            scan_id=hashlib.sha256(
                f"eq12_security_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16],
            project_path=str(self.project_root),
            scan_timestamp=datetime.now(UTC).isoformat(),
            scan_types=list(set(scan_types)),
            total_vulnerabilities=len(all_vulnerabilities),
            critical_count=severity_counts["CRITICAL"],
            high_count=severity_counts["HIGH"],
            medium_count=severity_counts["MEDIUM"],
            low_count=severity_counts["LOW"],
            vulnerabilities=all_vulnerabilities,
            scan_metadata={
                "snyk_version": await self._get_snyk_version(),
                "scan_duration": "TBD",  # Will be calculated
                "targets_scanned": list(self.scan_targets.keys()),
                "eq12_components": [
                    "betting_engine",
                    "chrome_automation",
                    "ai_integration",
                    "dashboard",
                ],
            },
            recommendations=self._generate_initial_recommendations(all_vulnerabilities),
        )

        logger.info(
            f"Security scan completed: {
                len(all_vulnerabilities)} vulnerabilities found")
        return scan_result

    def _extract_description(self, vuln: dict) -> str:
        """Extract vulnerability description from Snyk Code result"""
        if "message" in vuln and "text" in vuln["message"]:
            return vuln["message"]["text"]
        return "No description available"

    def _extract_file_path(self, vuln: dict, base_path: Path) -> str | None:
        """Extract file path from vulnerability data"""
        if vuln.get("locations"):
            location = vuln["locations"][0]
            if "physicalLocation" in location:
                artifact_uri = location["physicalLocation"]["artifactLocation"]["uri"]
                return str(base_path / artifact_uri)
        return None

    def _extract_line_number(self, vuln: dict) -> int | None:
        """Extract line number from vulnerability data"""
        if vuln.get("locations"):
            location = vuln["locations"][0]
            if "physicalLocation" in location:
                region = location["physicalLocation"].get("region", {})
                return region.get("startLine")
        return None

    def _extract_cwe(self, vuln: dict) -> str | None:
        """Extract CWE identifier from vulnerability"""
        # This would need to be implemented based on actual Snyk response format
        return None

    def _extract_fix_guidance(self, vuln: dict) -> str | None:
        """Extract fix guidance from Snyk Code result"""
        if "message" in vuln and "markdown" in vuln["message"]:
            return vuln["message"]["markdown"]
        return "No fix guidance available"

    def _extract_os_fix_guidance(self, vuln: dict) -> str | None:
        """Extract fix guidance for open source vulnerabilities"""
        if vuln.get("fixes"):
            fixes = vuln["fixes"]
            if fixes:
                return f"Upgrade to version {fixes[0].get('version', 'unknown')}"
        return "No automated fix available"

    async def _get_snyk_version(self) -> str:
        """Get Snyk CLI version"""
        try:
            result = subprocess.run(
                ["snyk", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except BaseException:
            return "unknown"

    def _calculate_risk_score(self, scan_result: SecurityScanResult) -> float:
        """Calculate overall security risk score"""
        weights = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 1}
        total_score = (
            scan_result.critical_count * weights["CRITICAL"]
            + scan_result.high_count * weights["HIGH"]
            + scan_result.medium_count * weights["MEDIUM"]
            + scan_result.low_count * weights["LOW"]
        )

        # Normalize to 0-100 scale
        max_possible = scan_result.total_vulnerabilities * weights["CRITICAL"]
        if max_possible > 0:
            return min(100, (total_score / max_possible) * 100)
        return 0

    def _assess_compliance_status(self, scan_result: SecurityScanResult) -> str:
        """Assess compliance status based on vulnerabilities"""
        if scan_result.critical_count > 0:
            return "NON_COMPLIANT"
        elif scan_result.high_count > 5:
            return "AT_RISK"
        elif scan_result.medium_count > 10:
            return "NEEDS_ATTENTION"
        else:
            return "COMPLIANT"

    def _create_vulnerability_breakdown(
            self, scan_result: SecurityScanResult) -> dict[str, Any]:
        """Create detailed vulnerability breakdown"""
        breakdown = {
            "by_severity": {
                "critical": scan_result.critical_count,
                "high": scan_result.high_count,
                "medium": scan_result.medium_count,
                "low": scan_result.low_count,
            },
            "by_scan_type": {},
            "by_component": {},
            "top_vulnerabilities": [],
        }

        # Count by scan type
        for vuln in scan_result.vulnerabilities:
            scan_type = vuln.scan_type
            if scan_type not in breakdown["by_scan_type"]:
                breakdown["by_scan_type"][scan_type] = 0
            breakdown["by_scan_type"][scan_type] += 1

        # Extract top critical/high vulnerabilities
        critical_high_vulns = [
            v for v in scan_result.vulnerabilities if v.severity in ["CRITICAL", "HIGH"]
        ]
        breakdown["top_vulnerabilities"] = [
            {
                "id": v.id,
                "severity": v.severity,
                "title": v.title,
                "file_path": v.file_path,
                "scan_type": v.scan_type,
            }
            for v in critical_high_vulns[:10]  # Top 10
        ]

        return breakdown

    def _create_remediation_priorities(
        self, scan_result: SecurityScanResult
    ) -> list[dict[str, Any]]:
        """Create prioritized remediation plan"""
        priorities = []

        # Critical vulnerabilities - immediate action
        critical_vulns = [
            v for v in scan_result.vulnerabilities if v.severity == "CRITICAL"]
        if critical_vulns:
            priorities.append(
                {
                    "priority": "IMMEDIATE",
                    "action": "Fix Critical Vulnerabilities",
                    "count": len(critical_vulns),
                    "timeframe": "24 hours",
                    "vulnerabilities": [v.id for v in critical_vulns[:5]],
                }
            )

        # High severity - within week
        high_vulns = [v for v in scan_result.vulnerabilities if v.severity == "HIGH"]
        if high_vulns:
            priorities.append(
                {
                    "priority": "HIGH",
                    "action": "Address High Severity Issues",
                    "count": len(high_vulns),
                    "timeframe": "1 week",
                    "vulnerabilities": [v.id for v in high_vulns[:5]],
                }
            )

        # Dependency updates
        dep_vulns = [v for v in scan_result.vulnerabilities if v.scan_type == "SCA"]
        if dep_vulns:
            priorities.append(
                {
                    "priority": "MEDIUM",
                    "action": "Update Vulnerable Dependencies",
                    "count": len(dep_vulns),
                    "timeframe": "2 weeks",
                    "focus": "Package updates and security patches",
                }
            )

        return priorities

    def _generate_security_recommendations(
            self, scan_result: SecurityScanResult) -> list[str]:
        """Generate actionable security recommendations"""
        recommendations = []

        if scan_result.critical_count > 0:
            recommendations.append(
                "Immediately address all critical vulnerabilities before production deployment"
            )

        if scan_result.high_count > 3:
            recommendations.append(
                "Implement automated security scanning in CI/CD pipeline")

        # Scan type specific recommendations
        scan_types = {v.scan_type for v in scan_result.vulnerabilities}

        if "SAST" in scan_types:
            recommendations.append(
                "Enable Snyk Code in IDE for real-time security feedback")
            recommendations.append(
                "Implement secure coding practices and code review processes")

        if "SCA" in scan_types:
            recommendations.append("Enable automated dependency monitoring and updates")
            recommendations.append(
                "Establish dependency approval process for new packages")

        if "IAC" in scan_types:
            recommendations.append("Implement Infrastructure as Code security policies")
            recommendations.append("Use Snyk IaC in deployment pipelines")

        recommendations.extend(
            [
                "Set up Snyk monitoring for continuous vulnerability detection",
                "Implement security training for development team",
                "Establish vulnerability disclosure and response process",
                "Consider implementing Snyk Broker for enhanced security",
                "Regular security audits and penetration testing",
            ]
        )

        return recommendations

    def _generate_initial_recommendations(
        self, vulnerabilities: list[SecurityVulnerability]
    ) -> list[str]:
        """Generate initial recommendations based on vulnerabilities found"""
        if not vulnerabilities:
            return ["No security vulnerabilities detected - maintain current security practices"]

        recommendations = [
            "Review and prioritize security vulnerabilities by severity",
            "Implement automated security scanning in development workflow",
            "Establish security review process for code changes",
        ]

        return recommendations


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 Snyk Security Integration")
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Run comprehensive security scan")
    parser.add_argument("--install-snyk", action="store_true", help="Install Snyk CLI")
    parser.add_argument("--auth", action="store_true", help="Authenticate Snyk CLI")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report from existing scan data",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    scanner = SnykSecurityScanner()

    try:
        if args.install_snyk:
            success = await scanner.install_snyk_cli()
            if success:
                logger.info("Snyk CLI installation completed")
            else:
                logger.error("Snyk CLI installation failed")
                return 1

        if args.auth:
            success = await scanner.authenticate_snyk()
            if success:
                logger.info("Snyk authentication completed")
            else:
                logger.error("Snyk authentication failed")
                return 1

        if args.scan:
            logger.info("🔒 Starting EQ12 Security Scan with Snyk Integration")
            scan_result = await scanner.run_comprehensive_security_scan()

            # Generate comprehensive report
            report_path = await scanner.generate_security_report(scan_result)

            # Display summary
            print("\n" + "=" * 60)
            print("🔒 EQ12 SECURITY SCAN RESULTS")
            print("=" * 60)
            print(f"📊 Total Vulnerabilities: {scan_result.total_vulnerabilities}")
            print(f"🚨 Critical: {scan_result.critical_count}")
            print(f"⚠️  High: {scan_result.high_count}")
            print(f"📋 Medium: {scan_result.medium_count}")
            print(f"ℹ️  Low: {scan_result.low_count}")
            print(f"📄 Detailed Report: {report_path}")
            print("=" * 60)

            if scan_result.critical_count > 0:
                print("🚨 CRITICAL: Immediate action required for critical vulnerabilities!")
                return 2
            elif scan_result.high_count > 5:
                print("⚠️ WARNING: High number of high-severity vulnerabilities detected")
                return 1
            else:
                print("✅ Security scan completed successfully")
                return 0

        if args.report_only:
            # This would load existing scan data and regenerate report
            logger.info("Report-only mode not yet implemented")
            return 0

        # Default: Show help
        parser.print_help()
        return 0

    except Exception as e:
        logger.error(f"Security scan failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
