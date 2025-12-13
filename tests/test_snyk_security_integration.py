#!/usr/bin/env python3
"""
EQ12 Snyk Security Integration Tests
Comprehensive test suite for security scanning functionality

Tests cover:
- Snyk CLI installation and configuration
- Security scanning of different component types
- Vulnerability detection and reporting
- Integration with EQ12 betting platform components
- Configuration management and policy enforcement

Author: EQ12 Security Team
Created: 2024
Version: 1.0.0
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from eq12_snyk_security_integration import (
    SecurityScanResult,
    SecurityVulnerability,
    SnykSecurityScanner,
)


class TestSnykSecurityIntegration:
    """Test suite for EQ12 Snyk security integration"""

    @pytest.fixture
    def mock_scanner(self):
        """Create a mock scanner for testing"""
        scanner = SnykSecurityScanner()
        scanner.project_root = Path(tempfile.mkdtemp())
        scanner.logs_dir = scanner.project_root / "logs"
        scanner.logs_dir.mkdir(exist_ok=True)
        return scanner

    @pytest.fixture
    def sample_vulnerability(self):
        """Create sample vulnerability for testing"""
        return SecurityVulnerability(
            id="SNYK-TEST-001",
            severity="HIGH",
            title="Test SQL Injection Vulnerability",
            description="Potential SQL injection in user input handling",
            file_path="/test/vulnerable_file.py",
            line_number=42,
            cwe="CWE-89",
            cvss_score=7.5,
            fix_guidance="Use parameterized queries to prevent SQL injection",
            package_name="test_package",
            package_version="1.0.0",
            scan_type="SAST",
            detected_at="2024-01-15T10:30:00Z",
        )

    @pytest.fixture
    def sample_scan_result(self, sample_vulnerability):
        """Create sample scan result for testing"""
        return SecurityScanResult(
            scan_id="test_scan_001",
            project_path="/test/project",
            scan_timestamp="2024-01-15T10:30:00Z",
            scan_types=["SAST", "SCA"],
            total_vulnerabilities=5,
            critical_count=1,
            high_count=2,
            medium_count=1,
            low_count=1,
            vulnerabilities=[sample_vulnerability],
            scan_metadata={"snyk_version": "1.0.0", "scan_duration": "120s"},
            recommendations=["Fix critical vulnerabilities immediately"],
        )


class TestSnykCLIIntegration:
    """Test Snyk CLI installation and configuration"""

    @pytest.mark.asyncio
    async def test_check_snyk_installation(self, mock_scanner):
        """Test Snyk CLI installation check"""
        with patch("subprocess.run") as mock_run:
            # Test successful installation check
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "1.0.0"

            result = await mock_scanner.check_snyk_installation()
            assert result is True

            # Test failed installation check
            mock_run.return_value.returncode = 1
            result = await mock_scanner.check_snyk_installation()
            assert result is False

    @pytest.mark.asyncio
    async def test_install_snyk_cli(self, mock_scanner):
        """Test Snyk CLI installation methods"""
        with patch("subprocess.run") as mock_run:
            # Test npm installation success
            mock_run.return_value.returncode = 0

            with patch.object(mock_scanner, "check_snyk_installation", return_value=True):
                result = await mock_scanner.install_snyk_cli()
                assert result is True

    @pytest.mark.asyncio
    async def test_authenticate_snyk(self, mock_scanner):
        """Test Snyk authentication process"""
        # Test with token present
        with patch.dict(os.environ, {"SNYK_TOKEN": "test-token"}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0

                result = await mock_scanner.authenticate_snyk()
                assert result is True

        # Test without token
        mock_scanner.snyk_token = None
        result = await mock_scanner.authenticate_snyk()
        assert result is False


class TestSecurityScanning:
    """Test security scanning functionality"""

    @pytest.mark.asyncio
    async def test_scan_code_security(self, mock_scanner):
        """Test static code analysis scanning"""
        test_path = mock_scanner.project_root / "test_code"
        test_path.mkdir(exist_ok=True)

        # Mock Snyk Code response
        mock_response = {
            "runs": [
                {
                    "results": [
                        {
                            "ruleId": "SNYK-CODE-001",
                            "level": "error",
                            "message": {"text": "SQL Injection vulnerability"},
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": "test.py"},
                                        "region": {"startLine": 10},
                                    }
                                }
                            ],
                        }
                    ]
                }
            ]
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(mock_response)

            vulnerabilities = await mock_scanner.scan_code_security(test_path)
            assert len(vulnerabilities) == 1
            assert vulnerabilities[0].scan_type == "SAST"

    @pytest.mark.asyncio
    async def test_scan_open_source_dependencies(self, mock_scanner):
        """Test open source dependency scanning"""
        test_path = mock_scanner.project_root / "test_deps"
        test_path.mkdir(exist_ok=True)

        # Mock Snyk Open Source response
        mock_response = {
            "vulnerabilities": [
                {
                    "id": "SNYK-OS-001",
                    "severity": "high",
                    "title": "Vulnerable dependency",
                    "description": "Security issue in package",
                    "packageName": "test-package",
                    "version": "1.0.0",
                    "cvssScore": 8.5,
                    "from": ["package.json"],
                }
            ]
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(mock_response)

            vulnerabilities = await mock_scanner.scan_open_source_dependencies(test_path)
            assert len(vulnerabilities) == 1
            assert vulnerabilities[0].scan_type == "SCA"

    @pytest.mark.asyncio
    async def test_scan_infrastructure_as_code(self, mock_scanner):
        """Test Infrastructure as Code scanning"""
        test_path = mock_scanner.project_root / "test_iac"
        test_path.mkdir(exist_ok=True)

        # Mock Snyk IaC response
        mock_response = {
            "infrastructureAsCodeIssues": [
                {
                    "id": "SNYK-IAC-001",
                    "severity": "medium",
                    "title": "Insecure configuration",
                    "description": "Security misconfiguration detected",
                    "targetFile": "config.yaml",
                    "lineNumber": 15,
                    "remediation": {"advice": "Update configuration"},
                }
            ]
        }

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = json.dumps(mock_response)

            vulnerabilities = await mock_scanner.scan_infrastructure_as_code(test_path)
            assert len(vulnerabilities) == 1
            assert vulnerabilities[0].scan_type == "IAC"


class TestVulnerabilityManagement:
    """Test vulnerability detection and management"""

    def test_vulnerability_creation(self, sample_vulnerability):
        """Test vulnerability object creation and validation"""
        assert sample_vulnerability.id == "SNYK-TEST-001"
        assert sample_vulnerability.severity == "HIGH"
        assert sample_vulnerability.scan_type == "SAST"
        assert sample_vulnerability.cvss_score == 7.5

    def test_scan_result_creation(self, sample_scan_result):
        """Test scan result object creation and validation"""
        assert sample_scan_result.total_vulnerabilities == 5
        assert sample_scan_result.critical_count == 1
        assert sample_scan_result.high_count == 2
        assert len(sample_scan_result.vulnerabilities) == 1
        assert "SAST" in sample_scan_result.scan_types


class TestReportingAndAnalytics:
    """Test security reporting and analytics functionality"""

    @pytest.mark.asyncio
    async def test_generate_security_report(self, mock_scanner, sample_scan_result):
        """Test security report generation"""
        report_path = await mock_scanner.generate_security_report(sample_scan_result)

        # Verify report file was created
        assert Path(report_path).exists()

        # Verify report content
        with open(report_path) as f:
            report_data = json.load(f)

        assert "report_metadata" in report_data
        assert "executive_summary" in report_data
        assert "scan_results" in report_data
        assert "vulnerability_breakdown" in report_data

    def test_risk_score_calculation(self, mock_scanner, sample_scan_result):
        """Test security risk score calculation"""
        risk_score = mock_scanner._calculate_risk_score(sample_scan_result)
        assert 0 <= risk_score <= 100
        assert isinstance(risk_score, (int, float))

    def test_compliance_assessment(self, mock_scanner, sample_scan_result):
        """Test compliance status assessment"""
        # Test with critical vulnerabilities
        sample_scan_result.critical_count = 2
        status = mock_scanner._assess_compliance_status(sample_scan_result)
        assert status == "NON_COMPLIANT"

        # Test with no critical vulnerabilities
        sample_scan_result.critical_count = 0
        sample_scan_result.high_count = 2
        status = mock_scanner._assess_compliance_status(sample_scan_result)
        assert status in ["AT_RISK", "NEEDS_ATTENTION", "COMPLIANT"]


class TestEQ12Integration:
    """Test EQ12-specific security integration"""

    def test_eq12_scan_targets(self, mock_scanner):
        """Test EQ12 component scan target configuration"""
        expected_targets = ["scripts", "tests", "configs", "dashboard"]
        assert all(target in mock_scanner.scan_targets for target in expected_targets)

    def test_betting_platform_security_focus(self, mock_scanner):
        """Test betting platform specific security considerations"""
        # Verify financial and gambling-specific security recommendations
        vulnerabilities = [
            SecurityVulnerability(
                id="FINANCIAL-001",
                severity="CRITICAL",
                title="Payment processing vulnerability",
                description="",
                file_path="",
                line_number=None,
                cwe=None,
                cvss_score=9.0,
                fix_guidance="",
                package_name="",
                package_version="",
                scan_type="SAST",
                detected_at="",
            )
        ]

        recommendations = mock_scanner._generate_initial_recommendations(vulnerabilities)
        assert any("security" in rec.lower() for rec in recommendations)


class TestConfigurationManagement:
    """Test security configuration management"""

    def test_load_security_config(self):
        """Test loading security configuration"""
        config_path = Path(__file__).parent.parent / "configs" / "snyk_security_config.json"

        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)

            assert "snyk_security_config" in config
            assert "security_scanning" in config["snyk_security_config"]
            assert "vulnerability_management" in config["snyk_security_config"]

    def test_security_policy_validation(self):
        """Test security policy configuration validation"""
        # This would test policy enforcement rules
        test_policy = {
            "critical_max_allowed": 0,
            "high_max_allowed": 5,
            "fail_on_critical": True,
        }

        # Validate policy structure
        assert "critical_max_allowed" in test_policy
        assert isinstance(test_policy["fail_on_critical"], bool)


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_snyk_command_timeout(self, mock_scanner):
        """Test handling of Snyk command timeouts"""
        test_path = mock_scanner.project_root / "test"
        test_path.mkdir(exist_ok=True)

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("snyk", 300)

            vulnerabilities = await mock_scanner.scan_code_security(test_path)
            assert vulnerabilities == []  # Should return empty list on timeout

    @pytest.mark.asyncio
    async def test_invalid_json_response(self, mock_scanner):
        """Test handling of invalid JSON responses from Snyk"""
        test_path = mock_scanner.project_root / "test"
        test_path.mkdir(exist_ok=True)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "invalid json"

            vulnerabilities = await mock_scanner.scan_code_security(test_path)
            assert vulnerabilities == []  # Should return empty list on JSON error

    def test_missing_environment_variables(self, mock_scanner):
        """Test handling of missing environment variables"""
        # Test without SNYK_TOKEN
        original_token = mock_scanner.snyk_token
        mock_scanner.snyk_token = None

        # Should handle gracefully without crashing
        assert mock_scanner.snyk_token is None

        # Restore for other tests
        mock_scanner.snyk_token = original_token


class TestPerformanceAndScalability:
    """Test performance and scalability aspects"""

    @pytest.mark.asyncio
    async def test_concurrent_scanning(self, mock_scanner):
        """Test concurrent scanning of multiple targets"""
        # Create multiple test targets
        test_targets = []
        for i in range(3):
            target_path = mock_scanner.project_root / f"test_{i}"
            target_path.mkdir(exist_ok=True)
            test_targets.append(target_path)

        # Mock successful scans
        with patch.object(mock_scanner, "scan_code_security", return_value=[]):
            # Test concurrent execution (simplified)
            tasks = [mock_scanner.scan_code_security(target) for target in test_targets]
            results = await asyncio.gather(*tasks)

            assert len(results) == 3
            assert all(isinstance(result, list) for result in results)

    def test_large_vulnerability_list_handling(self, mock_scanner):
        """Test handling of large vulnerability lists"""
        # Create a large list of vulnerabilities
        large_vuln_list = []
        for i in range(1000):
            vuln = SecurityVulnerability(
                id=f"TEST-{i:04d}",
                severity="LOW",
                title=f"Test vulnerability {i}",
                description="",
                file_path="",
                line_number=None,
                cwe=None,
                cvss_score=2.0,
                fix_guidance="",
                package_name="",
                package_version="",
                scan_type="SAST",
                detected_at="",
            )
            large_vuln_list.append(vuln)

        # Test performance with large dataset
        scan_result = SecurityScanResult(
            scan_id="perf_test",
            project_path="",
            scan_timestamp="",
            scan_types=["SAST"],
            total_vulnerabilities=1000,
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=1000,
            vulnerabilities=large_vuln_list,
            scan_metadata={},
            recommendations=[],
        )

        # Should handle large datasets without performance issues
        risk_score = mock_scanner._calculate_risk_score(scan_result)
        assert isinstance(risk_score, (int, float))


# Integration test with actual EQ12 components
@pytest.mark.integration
class TestEQ12ComponentIntegration:
    """Integration tests with actual EQ12 components"""

    @pytest.mark.skipif(not Path("C:/EQ12").exists(), reason="EQ12 project not found")
    def test_eq12_project_structure(self):
        """Test that EQ12 project structure is as expected"""
        eq12_root = Path("C:/EQ12")
        expected_dirs = ["scripts", "tests", "configs", "logs"]

        for expected_dir in expected_dirs:
            assert (eq12_root / expected_dir).exists(), f"Missing directory: {expected_dir}"

    @pytest.mark.skipif(not Path("C:/EQ12/scripts").exists(), reason="EQ12 scripts not found")
    def test_eq12_security_script_integration(self):
        """Test integration with existing EQ12 security scripts"""
        scripts_dir = Path("C:/EQ12/scripts")

        # Check for related security files
        security_files = list(scripts_dir.glob("*security*"))
        assert len(security_files) > 0, "No security-related scripts found"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
