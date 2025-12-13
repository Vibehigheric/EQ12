#!/usr/bin/env python3
"""
EQ12 Enterprise Security Hardening Suite
Buffalo NY 14215 Content Empire

Multi-Hat Security Analysis:
- Red Hat: Offensive security testing and vulnerability discovery
- Black Hat: Advanced persistent threat (APT) simulation
- White Hat: Defensive security measures and compliance
- Blue Hat: System hardening and monitoring

This is the ULTIMATE security audit for your EQ12 automation system.
"""

import os
import re
import json
import hashlib
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/EQ12/logs/eq12_security_audit.log'),
        logging.StreamHandler()
    ]
)

class EQ12SecurityHardening:
    """Enterprise-grade security hardening suite for EQ12 system"""

    def __init__(self):
        self.workspace_root = Path("C:/EQ12")
        self.logs_dir = self.workspace_root / "logs"
        self.security_report = {}
        self.vulnerabilities = []
        self.recommendations = []

        # Critical security patterns to detect
        self.secret_patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'password': r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s]{8,})["\']?',
            'token': r'(?i)(token|auth[_-]?token)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'secret': r'(?i)(secret|secret[_-]?key)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{16,})["\']?',
            'telegram_token': r'(?i)(telegram.*token|bot.*token)\s*[=:]\s*["\']?([0-9]{8,10}:[a-zA-Z0-9_-]{35})["\']?',
            'odds_api_key': r'(?i)(odds.*api.*key)\s*[=:]\s*["\']?([a-zA-Z0-9]{32})["\']?',
            'openai_key': r'(?i)(openai[_-]?(api[_-]?)?key)\s*[=:]\s*["\']?(sk-[a-zA-Z0-9]{48})["\']?',
            'github_token': r'(?i)(github[_-]?token|gh[_-]?token)\s*[=:]\s*["\']?(ghp_[a-zA-Z0-9]{36})["\']?',
            'crypto_key': r'(?i)(crypto[_-]?key|binance[_-]?key)\s*[=:]\s*["\']?([a-zA-Z0-9]{64})["\']?',
        }

        # Dangerous PowerShell patterns
        self.powershell_risks = {
            'unrestricted_execution': r'Set-ExecutionPolicy.*Unrestricted',
            'execution_bypass': r'ExecutionPolicy.*Bypass',
            'invoke_expression': r'Invoke-Expression.*\$',
            'iex_variable': r'IEX\s+\$',
            'download_string': r'DownloadString\(',
            'webclient_download': r'WebClient\(',
            'encoded_command': r'-EncodedCommand',
            'hidden_window': r'-WindowStyle\s+Hidden',
            'no_profile': r'-NoProfile.*-Command',
        }

        # File integrity patterns
        self.integrity_risks = {
            'unicode_corruption': r'[^\x00-\x7F]',
            'bom_marker': r'\ufeff',
            'zero_width': r'[\u200b-\u200f\u2060\ufeff]',
            'replacement_char': r'\ufffd',
        }

    def run_comprehensive_audit(self) -> Dict:
        """Run complete multi-hat security audit"""
        logging.info("=== STARTING EQ12 COMPREHENSIVE SECURITY AUDIT ===")

        # Red Hat: Offensive Security Testing
        self.red_hat_offensive_tests()

        # Black Hat: APT Simulation
        self.black_hat_apt_simulation()

        # White Hat: Defensive Measures
        self.white_hat_defensive_analysis()

        # Blue Hat: System Hardening
        self.blue_hat_system_hardening()

        # Generate comprehensive report
        return self.generate_security_report()

    def red_hat_offensive_tests(self):
        """Red Hat: Offensive security testing and penetration testing"""
        logging.info("🔴 RED HAT: Offensive Security Testing")

        # 1. Secret Discovery Attack Simulation
        secrets_found = self.discover_hardcoded_secrets()
        if secrets_found:
            self.vulnerabilities.append({
                'type': 'CRITICAL',
                'category': 'Hardcoded Secrets',
                'description': f'Found {len(secrets_found)} potential hardcoded secrets',
                'impact': 'CRITICAL - Complete system compromise possible',
                'locations': secrets_found,
                'cwe': 'CWE-798'
            })

        # 2. PowerShell Execution Policy Bypass Testing
        ps_vulns = self.test_powershell_security()
        if ps_vulns:
            self.vulnerabilities.extend(ps_vulns)

        # 3. File System Permission Testing
        fs_vulns = self.test_filesystem_permissions()
        if fs_vulns:
            self.vulnerabilities.extend(fs_vulns)

        # 4. Environment Variable Leakage
        env_vulns = self.test_environment_exposure()
        if env_vulns:
            self.vulnerabilities.extend(env_vulns)

    def black_hat_apt_simulation(self):
        """Black Hat: Advanced Persistent Threat simulation"""
        logging.info("⚫ BLACK HAT: APT Simulation")

        # 1. Persistent Backdoor Detection
        self.detect_potential_backdoors()

        # 2. Privilege Escalation Vectors
        self.analyze_privilege_escalation()

        # 3. Data Exfiltration Paths
        self.map_data_exfiltration_paths()

        # 4. Lateral Movement Simulation
        self.simulate_lateral_movement()

    def white_hat_defensive_analysis(self):
        """White Hat: Defensive security measures and compliance"""
        logging.info("⚪ WHITE HAT: Defensive Analysis")

        # 1. Security Controls Assessment
        self.assess_security_controls()

        # 2. Compliance Validation
        self.validate_compliance_standards()

        # 3. Incident Response Readiness
        self.test_incident_response()

        # 4. Security Monitoring Effectiveness
        self.evaluate_monitoring_systems()

    def blue_hat_system_hardening(self):
        """Blue Hat: System hardening and proactive defense"""
        logging.info("🔵 BLUE HAT: System Hardening")

        # 1. System Configuration Hardening
        self.harden_system_configuration()

        # 2. Network Security Assessment
        self.assess_network_security()

        # 3. Application Security Hardening
        self.harden_application_security()

        # 4. Continuous Monitoring Setup
        self.setup_continuous_monitoring()

    def discover_hardcoded_secrets(self) -> List[Dict]:
        """Discover hardcoded secrets in codebase"""
        secrets_found = []

        # Scan all relevant files
        for file_path in self.get_scannable_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for secret_type, pattern in self.secret_patterns.items():
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        secrets_found.append({
                            'file': str(file_path),
                            'type': secret_type,
                            'line': content[:match.start()].count('\n') + 1,
                            'pattern': match.group(0)[:50] + '...',
                            'severity': 'CRITICAL'
                        })
            except Exception as e:
                logging.warning(f"Could not scan {file_path}: {e}")

        return secrets_found

    def test_powershell_security(self) -> List[Dict]:
        """Test PowerShell security configurations"""
        vulnerabilities = []

        # Check PowerShell execution policy
        try:
            result = subprocess.run(
                ['powershell', '-Command', 'Get-ExecutionPolicy'],
                capture_output=True, text=True, timeout=10
            )

            execution_policy = result.stdout.strip()
            if execution_policy in ['Unrestricted', 'Bypass']:
                vulnerabilities.append({
                    'type': 'HIGH',
                    'category': 'PowerShell Security',
                    'description': f'Dangerous execution policy: {execution_policy}',
                    'impact': 'HIGH - Code execution without restrictions',
                    'recommendation': 'Set execution policy to RemoteSigned or AllSigned',
                    'cwe': 'CWE-94'
                })

        except Exception as e:
            logging.warning(f"Could not check PowerShell execution policy: {e}")

        # Scan PowerShell files for dangerous patterns
        ps_files = list(self.workspace_root.rglob("*.ps1"))
        for ps_file in ps_files:
            try:
                with open(ps_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for risk_type, pattern in self.powershell_risks.items():
                    if re.search(pattern, content, re.IGNORECASE):
                        vulnerabilities.append({
                            'type': 'MEDIUM',
                            'category': 'PowerShell Risk',
                            'description': f'Dangerous pattern in {ps_file}: {risk_type}',
                            'impact': 'MEDIUM - Potential code execution risk',
                            'file': str(ps_file),
                            'cwe': 'CWE-78'
                        })
            except Exception as e:
                logging.warning(f"Could not scan PowerShell file {ps_file}: {e}")

        return vulnerabilities

    def test_filesystem_permissions(self) -> List[Dict]:
        """Test file system permissions for security issues"""
        vulnerabilities = []

        # Check for world-writable directories in EQ12 workspace
        critical_dirs = [
            self.workspace_root / "scripts",
            self.workspace_root / "configs",
            self.workspace_root / ".github",
            self.workspace_root / "logs"
        ]

        for dir_path in critical_dirs:
            if dir_path.exists():
                try:
                    # On Windows, check if directory is writable by everyone
                    import win32security
                    import ntsecuritycon

                    sd = win32security.GetFileSecurity(str(dir_path), win32security.DACL_SECURITY_INFORMATION)
                    dacl = sd.GetSecurityDescriptorDacl()

                    if dacl:
                        for i in range(dacl.GetAceCount()):
                            ace = dacl.GetAce(i)
                            if ace[0][1] & ntsecuritycon.FILE_ALL_ACCESS:
                                vulnerabilities.append({
                                    'type': 'MEDIUM',
                                    'category': 'File Permissions',
                                    'description': f'Overly permissive access to {dir_path}',
                                    'impact': 'MEDIUM - Potential unauthorized file access',
                                    'recommendation': 'Restrict directory permissions'
                                })
                                break
                except ImportError:
                    # Skip Windows-specific checks on non-Windows
                    pass
                except Exception as e:
                    logging.warning(f"Could not check permissions for {dir_path}: {e}")

        return vulnerabilities

    def test_environment_exposure(self) -> List[Dict]:
        """Test for environment variable exposure"""
        vulnerabilities = []

        # Check for sensitive environment variables
        sensitive_vars = [
            'ODDS_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID',
            'OPENAI_API_KEY', 'GITHUB_TOKEN', 'CRYPTO_API_KEY'
        ]

        for var in sensitive_vars:
            if os.environ.get(var):
                # Good - using environment variables
                continue
            else:
                # Check if these are hardcoded instead
                files_with_var = []
                for file_path in self.get_scannable_files():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if var in content and '=' in content:
                                files_with_var.append(str(file_path))
                    except:
                        continue

                if files_with_var:
                    vulnerabilities.append({
                        'type': 'HIGH',
                        'category': 'Environment Security',
                        'description': f'Sensitive variable {var} not in environment',
                        'impact': 'HIGH - Secrets may be hardcoded',
                        'files': files_with_var,
                        'recommendation': f'Set {var} as environment variable'
                    })

        return vulnerabilities

    def detect_potential_backdoors(self):
        """Detect potential backdoors and malicious code"""
        backdoor_patterns = [
            r'eval\(',
            r'exec\(',
            r'subprocess\.call.*shell=True',
            r'os\.system\(',
            r'__import__\(',
            r'getattr\(.*,.*\)',
            r'setattr\(.*,.*,.*\)',
        ]

        backdoor_files = []
        for file_path in self.get_python_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern in backdoor_patterns:
                    if re.search(pattern, content):
                        backdoor_files.append({
                            'file': str(file_path),
                            'pattern': pattern,
                            'risk': 'Potential code execution'
                        })
            except:
                continue

        if backdoor_files:
            self.vulnerabilities.append({
                'type': 'HIGH',
                'category': 'Backdoor Detection',
                'description': f'Found {len(backdoor_files)} potential backdoor patterns',
                'impact': 'HIGH - Possible remote code execution',
                'files': backdoor_files,
                'cwe': 'CWE-94'
            })

    def analyze_privilege_escalation(self):
        """Analyze privilege escalation vectors"""
        escalation_risks = []

        # Check for UAC bypass attempts
        uac_patterns = [
            r'runas.*\/user:',
            r'Start-Process.*-Verb RunAs',
            r'elevate\.exe',
            r'fodhelper\.exe',
        ]

        for file_path in self.get_scannable_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern in uac_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        escalation_risks.append({
                            'file': str(file_path),
                            'pattern': pattern,
                            'risk': 'Privilege escalation attempt'
                        })
            except:
                continue

        if escalation_risks:
            self.vulnerabilities.append({
                'type': 'CRITICAL',
                'category': 'Privilege Escalation',
                'description': f'Found {len(escalation_risks)} privilege escalation patterns',
                'impact': 'CRITICAL - Potential system compromise',
                'files': escalation_risks
            })

    def map_data_exfiltration_paths(self):
        """Map potential data exfiltration paths"""
        exfil_patterns = [
            r'curl.*-d.*@',
            r'wget.*--post-file',
            r'Invoke-WebRequest.*-Body',
            r'Invoke-RestMethod.*-Body',
            r'ftp.*put',
            r'scp.*@',
        ]

        exfil_risks = []
        for file_path in self.get_scannable_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern in exfil_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        exfil_risks.append({
                            'file': str(file_path),
                            'pattern': pattern,
                            'risk': 'Data exfiltration capability'
                        })
            except:
                continue

        if exfil_risks:
            self.vulnerabilities.append({
                'type': 'HIGH',
                'category': 'Data Exfiltration',
                'description': f'Found {len(exfil_risks)} potential exfiltration methods',
                'impact': 'HIGH - Sensitive data could be stolen',
                'files': exfil_risks
            })

    def simulate_lateral_movement(self):
        """Simulate lateral movement capabilities"""
        # Check for network enumeration capabilities
        network_patterns = [
            r'nmap',
            r'Test-NetConnection',
            r'ping.*-n',
            r'arp.*-a',
            r'netstat.*-an',
            r'Get-NetTCPConnection',
        ]

        lateral_risks = []
        for file_path in self.get_scannable_files():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern in network_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        lateral_risks.append({
                            'file': str(file_path),
                            'pattern': pattern,
                            'risk': 'Network reconnaissance capability'
                        })
            except:
                continue

        if lateral_risks:
            self.vulnerabilities.append({
                'type': 'MEDIUM',
                'category': 'Lateral Movement',
                'description': f'Found {len(lateral_risks)} network reconnaissance capabilities',
                'impact': 'MEDIUM - Potential network mapping',
                'files': lateral_risks
            })

    def assess_security_controls(self):
        """Assess existing security controls"""
        controls = {
            'ascii_safety': self.workspace_root / "eq12_no_pycache.py",
            'security_policy': self.workspace_root / ".github" / "SECURITY.md",
            'codeowners': self.workspace_root / ".github" / "CODEOWNERS",
            'security_workflow': self.workspace_root / ".github" / "workflows" / "eq12_security.yml"
        }

        missing_controls = []
        for control_name, control_path in controls.items():
            if not control_path.exists():
                missing_controls.append(control_name)

        if missing_controls:
            self.vulnerabilities.append({
                'type': 'MEDIUM',
                'category': 'Security Controls',
                'description': f'Missing security controls: {", ".join(missing_controls)}',
                'impact': 'MEDIUM - Reduced security posture',
                'recommendation': 'Implement missing security controls'
            })

    def validate_compliance_standards(self):
        """Validate compliance with security standards"""
        # Check for required security practices
        compliance_checks = {
            'environment_variables': self.check_environment_usage(),
            'signed_commits': self.check_commit_signing(),
            'access_controls': self.check_access_controls(),
            'audit_logging': self.check_audit_logging()
        }

        failed_checks = [check for check, result in compliance_checks.items() if not result]

        if failed_checks:
            self.vulnerabilities.append({
                'type': 'MEDIUM',
                'category': 'Compliance',
                'description': f'Failed compliance checks: {", ".join(failed_checks)}',
                'impact': 'MEDIUM - Compliance violations',
                'recommendation': 'Address compliance failures'
            })

    def test_incident_response(self):
        """Test incident response readiness"""
        ir_components = {
            'backup_system': self.workspace_root / ".github" / "workflows" / "eq12_backup_sync.yml",
            'monitoring': self.workspace_root / ".github" / "workflows" / "eq12_telemetry_report.yml",
            'security_scanning': self.workspace_root / ".github" / "workflows" / "eq12_security.yml"
        }

        missing_ir = [comp for comp, path in ir_components.items() if not path.exists()]

        if missing_ir:
            self.recommendations.append({
                'type': 'Incident Response',
                'description': f'Missing IR components: {", ".join(missing_ir)}',
                'priority': 'HIGH',
                'action': 'Implement missing incident response capabilities'
            })

    def evaluate_monitoring_systems(self):
        """Evaluate security monitoring effectiveness"""
        monitoring_files = list(self.workspace_root.glob("**/eq12_telemetry*.py"))
        monitoring_files.extend(list(self.workspace_root.glob("**/eq12_monitoring*.py")))

        if not monitoring_files:
            self.vulnerabilities.append({
                'type': 'MEDIUM',
                'category': 'Monitoring',
                'description': 'No security monitoring systems detected',
                'impact': 'MEDIUM - Blind to security events',
                'recommendation': 'Implement comprehensive security monitoring'
            })

    def harden_system_configuration(self):
        """Provide system hardening recommendations"""
        hardening_recommendations = [
            {
                'category': 'PowerShell Security',
                'action': 'Set execution policy to RemoteSigned',
                'command': 'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser',
                'priority': 'HIGH'
            },
            {
                'category': 'Environment Variables',
                'action': 'Ensure all sensitive data uses environment variables',
                'command': 'Review and set: ODDS_API_KEY, TELEGRAM_BOT_TOKEN, OPENAI_API_KEY',
                'priority': 'CRITICAL'
            },
            {
                'category': 'File Permissions',
                'action': 'Restrict access to sensitive directories',
                'command': 'Review permissions on scripts/, configs/, logs/ directories',
                'priority': 'MEDIUM'
            },
            {
                'category': 'Network Security',
                'action': 'Enable Windows Firewall with strict rules',
                'command': 'netsh advfirewall set allprofiles state on',
                'priority': 'HIGH'
            }
        ]

        self.recommendations.extend(hardening_recommendations)

    def assess_network_security(self):
        """Assess network security configuration"""
        # Check for insecure network configurations
        network_files = list(self.workspace_root.rglob("*config*"))

        insecure_patterns = [
            r'http://',  # Unencrypted HTTP
            r'ftp://',   # Unencrypted FTP
            r'telnet://', # Unencrypted telnet
        ]

        network_risks = []
        for file_path in network_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern in insecure_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        network_risks.append({
                            'file': str(file_path),
                            'pattern': pattern,
                            'risk': 'Unencrypted network communication'
                        })
            except:
                continue

        if network_risks:
            self.vulnerabilities.append({
                'type': 'MEDIUM',
                'category': 'Network Security',
                'description': f'Found {len(network_risks)} insecure network configurations',
                'impact': 'MEDIUM - Data could be intercepted',
                'files': network_risks
            })

    def harden_application_security(self):
        """Provide application security hardening"""
        # Check Python security practices
        python_files = self.get_python_files()

        security_issues = []
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Check for dangerous practices
                if 'eval(' in content:
                    security_issues.append(f"eval() usage in {py_file}")
                if 'exec(' in content:
                    security_issues.append(f"exec() usage in {py_file}")
                if 'shell=True' in content:
                    security_issues.append(f"shell=True usage in {py_file}")

            except:
                continue

        if security_issues:
            self.vulnerabilities.append({
                'type': 'HIGH',
                'category': 'Application Security',
                'description': f'Found {len(security_issues)} dangerous coding practices',
                'impact': 'HIGH - Code injection vulnerabilities',
                'issues': security_issues
            })

    def setup_continuous_monitoring(self):
        """Setup continuous security monitoring"""
        monitoring_script = '''
# EQ12 Continuous Security Monitor
# Add to scheduled tasks for continuous monitoring

$LogFile = "C:\\EQ12\\logs\\security_monitor.log"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# Monitor for suspicious PowerShell activity
$SuspiciousPS = Get-WinEvent -FilterHashtable @{LogName='Windows PowerShell'; ID=4104} -MaxEvents 50 |
    Where-Object {$_.Message -match 'Invoke-Expression|DownloadString|EncodedCommand'}

if ($SuspiciousPS) {
    "$Timestamp - ALERT: Suspicious PowerShell activity detected" | Add-Content $LogFile
}

# Monitor for file integrity changes
$CriticalFiles = @(
    "C:\\EQ12\\eq12_no_pycache.py",
    "C:\\EQ12\\.copilot\\copilot.yml",
    "C:\\EQ12\\scripts\\eq12_pycache_cleanup.ps1"
)

foreach ($File in $CriticalFiles) {
    if (Test-Path $File) {
        $Hash = (Get-FileHash $File -Algorithm SHA256).Hash
        $HashFile = "$File.sha256"

        if (Test-Path $HashFile) {
            $StoredHash = Get-Content $HashFile
            if ($Hash -ne $StoredHash) {
                "$Timestamp - ALERT: File integrity violation: $File" | Add-Content $LogFile
            }
        } else {
            $Hash | Out-File $HashFile
        }
    }
}

# Monitor for network connections to suspicious destinations
$SuspiciousConnections = Get-NetTCPConnection | Where-Object {
    $_.RemoteAddress -match '^(?!10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.|127\.|169\.254\.|224\.|239\.|255\.).*'
}

if ($SuspiciousConnections) {
    "$Timestamp - INFO: External network connections detected" | Add-Content $LogFile
}
'''

        monitor_path = self.workspace_root / "scripts" / "eq12_security_monitor.ps1"
        with open(monitor_path, 'w', encoding='ascii') as f:
            f.write(monitoring_script)

        self.recommendations.append({
            'type': 'Continuous Monitoring',
            'description': 'Security monitoring script created',
            'file': str(monitor_path),
            'action': 'Schedule this script to run every 15 minutes',
            'priority': 'HIGH'
        })

    def get_scannable_files(self) -> List[Path]:
        """Get all files that should be scanned for security issues"""
        extensions = ['.py', '.ps1', '.json', '.yml', '.yaml', '.md', '.txt', '.sh', '.bat', '.cmd']
        files = []

        for ext in extensions:
            files.extend(list(self.workspace_root.rglob(f"*{ext}")))

        # Filter out non-scannable directories
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}

        return [f for f in files if not any(exclude_dir in f.parts for exclude_dir in exclude_dirs)]

    def get_python_files(self) -> List[Path]:
        """Get all Python files for scanning"""
        return list(self.workspace_root.rglob("*.py"))

    def check_environment_usage(self) -> bool:
        """Check if environment variables are properly used"""
        required_env_vars = ['PYTHONDONTWRITEBYTECODE', 'EQ12_ASCII_MODE']
        return all(os.environ.get(var) for var in required_env_vars)

    def check_commit_signing(self) -> bool:
        """Check if commit signing is enabled"""
        try:
            result = subprocess.run(
                ['git', 'config', '--global', 'commit.gpgsign'],
                capture_output=True, text=True, timeout=5
            )
            return result.stdout.strip().lower() == 'true'
        except:
            return False

    def check_access_controls(self) -> bool:
        """Check if proper access controls are in place"""
        codeowners_file = self.workspace_root / ".github" / "CODEOWNERS"
        return codeowners_file.exists()

    def check_audit_logging(self) -> bool:
        """Check if audit logging is configured"""
        logs_dir = self.workspace_root / "logs"
        return logs_dir.exists() and len(list(logs_dir.glob("*.log"))) > 0

    def generate_security_report(self) -> Dict:
        """Generate comprehensive security report"""
        timestamp = datetime.now().isoformat()

        # Calculate risk scores
        total_vulns = len(self.vulnerabilities)
        critical_vulns = len([v for v in self.vulnerabilities if v['type'] == 'CRITICAL'])
        high_vulns = len([v for v in self.vulnerabilities if v['type'] == 'HIGH'])
        medium_vulns = len([v for v in self.vulnerabilities if v['type'] == 'MEDIUM'])

        risk_score = (critical_vulns * 10) + (high_vulns * 5) + (medium_vulns * 2)

        if risk_score == 0:
            risk_level = "LOW"
        elif risk_score <= 10:
            risk_level = "MEDIUM"
        elif risk_score <= 30:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        report = {
            'timestamp': timestamp,
            'system': 'EQ12 Buffalo NY 14215 Content Empire',
            'audit_type': 'Multi-Hat Security Assessment',
            'summary': {
                'total_vulnerabilities': total_vulns,
                'critical_vulnerabilities': critical_vulns,
                'high_vulnerabilities': high_vulns,
                'medium_vulnerabilities': medium_vulns,
                'risk_score': risk_score,
                'risk_level': risk_level
            },
            'vulnerabilities': self.vulnerabilities,
            'recommendations': self.recommendations,
            'compliance_status': {
                'environment_variables': self.check_environment_usage(),
                'commit_signing': self.check_commit_signing(),
                'access_controls': self.check_access_controls(),
                'audit_logging': self.check_audit_logging()
            },
            'next_actions': self.generate_next_actions()
        }

        # Save report
        report_path = self.logs_dir / f"eq12_security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        logging.info(f"Security audit report saved to: {report_path}")

        return report

    def generate_next_actions(self) -> List[str]:
        """Generate prioritized next actions"""
        actions = []

        # Critical actions first
        if any(v['type'] == 'CRITICAL' for v in self.vulnerabilities):
            actions.append("IMMEDIATE: Address all CRITICAL vulnerabilities")

        # Environment variable setup
        if not self.check_environment_usage():
            actions.append("HIGH: Set up proper environment variables")

        # PowerShell security
        actions.append("HIGH: Configure PowerShell execution policy")

        # Commit signing
        if not self.check_commit_signing():
            actions.append("MEDIUM: Enable commit signing")

        # Continuous monitoring
        actions.append("MEDIUM: Implement continuous security monitoring")

        return actions

    def generate_executive_summary(self) -> str:
        """Generate executive summary for management"""
        summary = f"""
EQ12 ENTERPRISE SECURITY AUDIT - EXECUTIVE SUMMARY
Buffalo NY 14215 Content Empire
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SECURITY POSTURE: {self.security_report.get('summary', {}).get('risk_level', 'UNKNOWN')}

KEY FINDINGS:
- Total Vulnerabilities: {len(self.vulnerabilities)}
- Critical Issues: {len([v for v in self.vulnerabilities if v['type'] == 'CRITICAL'])}
- High Priority Issues: {len([v for v in self.vulnerabilities if v['type'] == 'HIGH'])}

IMMEDIATE ACTIONS REQUIRED:
{chr(10).join(f"• {action}" for action in self.generate_next_actions()[:5])}

COMPLIANCE STATUS:
- Environment Variables: {'✓' if self.check_environment_usage() else '✗'}
- Commit Signing: {'✓' if self.check_commit_signing() else '✗'}
- Access Controls: {'✓' if self.check_access_controls() else '✗'}
- Audit Logging: {'✓' if self.check_audit_logging() else '✗'}

RECOMMENDATION:
Address all CRITICAL and HIGH vulnerabilities within 24-48 hours.
Implement continuous monitoring for ongoing security assurance.
        """

        return summary


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='EQ12 Multi-Hat Security Audit')
    parser.add_argument('--mode', choices=['full', 'quick', 'critical-only'],
                       default='full', help='Audit mode')
    parser.add_argument('--output', choices=['json', 'text', 'both'],
                       default='both', help='Output format')
    parser.add_argument('--fix-issues', action='store_true',
                       help='Automatically fix non-critical issues')

    args = parser.parse_args()

    # Ensure logs directory exists
    os.makedirs("C:/EQ12/logs", exist_ok=True)

    # Initialize security hardening
    hardening = EQ12SecurityHardening()

    # Run audit based on mode
    if args.mode == 'critical-only':
        logging.info("Running critical-only security scan...")
        report = {'vulnerabilities': hardening.discover_hardcoded_secrets()}
    elif args.mode == 'quick':
        logging.info("Running quick security scan...")
        hardening.red_hat_offensive_tests()
        report = hardening.generate_security_report()
    else:
        logging.info("Running comprehensive security audit...")
        report = hardening.run_comprehensive_audit()

    hardening.security_report = report

    # Output results
    if args.output in ['text', 'both']:
        print("\n" + "="*80)
        print("EQ12 SECURITY AUDIT RESULTS")
        print("="*80)
        print(hardening.generate_executive_summary())

        if report.get('vulnerabilities'):
            print("\nTOP VULNERABILITIES:")
            for vuln in sorted(report['vulnerabilities'],
                             key=lambda x: {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(x['type'], 0),
                             reverse=True)[:5]:
                print(f"• [{vuln['type']}] {vuln['description']}")

    if args.output in ['json', 'both']:
        report_file = f"C:/EQ12/logs/security_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed JSON report: {report_file}")

    # Auto-fix if requested
    if args.fix_issues and report.get('recommendations'):
        logging.info("Applying automatic fixes...")
        # Implementation for auto-fixes would go here

    # Exit with appropriate code
    critical_vulns = len([v for v in report.get('vulnerabilities', []) if v['type'] == 'CRITICAL'])
    if critical_vulns > 0:
        sys.exit(1)  # Critical issues found
    else:
        sys.exit(0)  # No critical issues


if __name__ == "__main__":
    main()
