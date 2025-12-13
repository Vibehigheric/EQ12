#!/usr/bin/env python3
"""
EQ12 Expert System Verification Script
Professional Engineering Grade Python Environment Validator

Author: EQ12 Engineering Team
Version: 2.1.0
Date: 2025-11-22
Python: 3.12+
Dependencies: hashlib, pathlib, json, sys

This script performs comprehensive integrity checks on:
- Python interpreter installations
- Virtual environments
- Package dependencies
- Path configurations
- VS Code Python extensions
- File system consistency

Teaching Notes (30-Day Python Curriculum Integration):
- Variables and data types (Day 2): Used for storing paths and configuration
- Lists and dictionaries (Day 6): Storing multiple scan results
- Functions (Day 11): Modular verification functions
- Error handling (Day 19): Comprehensive try/except blocks
- Classes (Day 20): Structured verification objects
- File operations (Day 25): Reading configs and logs
"""

import os
import sys
import json
import hashlib
import subprocess
import pathlib
import platform
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

# ASCII-safe logging configuration
class ASCIIFormatter(logging.Formatter):
    """Custom formatter ensuring ASCII-safe log output"""

    def format(self, record):
        # Get the formatted message
        msg = super().format(record)
        # Convert to ASCII-safe string
        return msg.encode('ascii', 'replace').decode('ascii')

def setup_logging() -> logging.Logger:
    """
    Set up ASCII-safe logging for the verification system

    Teaching note (Day 11 - Functions): This function encapsulates logging setup
    to avoid repeating configuration code throughout the script.
    """
    # Create logs directory if it doesn't exist (Day 25 - File operations)
    log_dir = pathlib.Path("C:/EQ12/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Set up logger with ASCII formatter
    logger = logging.getLogger('eq12_verify')
    logger.setLevel(logging.INFO)

    # File handler with ASCII-safe formatting
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"eq12_verify_{timestamp}.log"

    file_handler = logging.FileHandler(log_file, encoding='ascii', errors='replace')
    file_handler.setFormatter(ASCIIFormatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ASCIIFormatter(
        '%(levelname)s: %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

class EQ12SystemVerifier:
    """
    Expert-level system verification class for EQ12 Python environments

    Teaching note (Day 20 - Classes): This class encapsulates all verification
    logic into a single, reusable object with clear methods and properties.
    """

    def __init__(self):
        """Initialize the system verifier with configuration"""
        self.logger = setup_logging()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'python_installations': {},
            'virtual_environments': {},
            'vscode_integration': {},
            'file_integrity': {},
            'recommendations': []
        }
        self.error_count = 0
        self.warning_count = 0

    def log_finding(self, level: str, message: str, category: str = "general"):
        """
        Log a finding with appropriate level and categorization

        Teaching note (Day 11 - Functions): Using default parameters to make
        the category optional while maintaining backwards compatibility.
        """
        # Convert message to ASCII-safe format
        safe_message = message.encode('ascii', 'replace').decode('ascii')

        if level.upper() == 'ERROR':
            self.error_count += 1
            self.logger.error(f"[{category}] {safe_message}")
        elif level.upper() == 'WARNING':
            self.warning_count += 1
            self.logger.warning(f"[{category}] {safe_message}")
        else:
            self.logger.info(f"[{category}] {safe_message}")

    def verify_system_info(self) -> None:
        """
        Collect and verify basic system information

        Teaching note (Day 6 - Dictionaries): Storing system information in a
        structured dictionary for easy access and JSON serialization.
        """
        self.log_finding('INFO', 'Collecting system information', 'system')

        try:
            self.results['system_info'] = {
                'platform': platform.platform(),
                'python_version': sys.version,
                'python_executable': sys.executable,
                'python_path': sys.path[:5],  # Limit to first 5 entries
                'working_directory': os.getcwd(),
                'environment_variables': {
                    'PATH': os.environ.get('PATH', '').split(os.pathsep)[:10],  # Limit output
                    'PYTHONPATH': os.environ.get('PYTHONPATH', 'Not set'),
                    'VIRTUAL_ENV': os.environ.get('VIRTUAL_ENV', 'Not set')
                }
            }

            # Verify Python version is 3.12+
            version_info = sys.version_info
            if version_info.major == 3 and version_info.minor >= 12:
                self.log_finding('INFO', f'Python version {version_info.major}.{version_info.minor}.{version_info.micro} is supported', 'system')
            else:
                self.log_finding('WARNING', f'Python version {version_info.major}.{version_info.minor}.{version_info.micro} may not be optimal (recommend 3.12+)', 'system')

        except Exception as e:
            self.log_finding('ERROR', f'Failed to collect system info: {str(e)}', 'system')

    def discover_python_installations(self) -> Dict[str, Any]:
        """
        Discover and verify all Python installations on the system

        Teaching note (Day 9 - Loops): Using for loops to iterate through
        potential installation directories and check each one.
        """
        self.log_finding('INFO', 'Discovering Python installations', 'python')

        # Common Python installation paths (Day 6 - Lists)
        search_paths = [
            f"C:/Users/{os.environ.get('USERNAME', 'Unknown')}/AppData/Local/Programs/Python",
            "C:/Python312",
            "C:/Program Files/Python312",
            "C:/Program Files (x86)/Python312",
        ]

        installations = {}

        for base_path in search_paths:
            if os.path.exists(base_path):
                try:
                    # Look for python.exe in the directory or subdirectories
                    for root, dirs, files in os.walk(base_path):
                        if 'python.exe' in files:
                            python_exe = os.path.join(root, 'python.exe')

                            # Verify the installation (Day 19 - Error handling)
                            try:
                                result = subprocess.run(
                                    [python_exe, '--version'],
                                    capture_output=True,
                                    text=True,
                                    timeout=10
                                )

                                if result.returncode == 0:
                                    version = result.stdout.strip()
                                    installations[root] = {
                                        'executable': python_exe,
                                        'version': version,
                                        'status': 'working'
                                    }
                                    self.log_finding('INFO', f'Found working Python: {version} at {python_exe}', 'python')
                                else:
                                    installations[root] = {
                                        'executable': python_exe,
                                        'version': 'unknown',
                                        'status': 'broken',
                                        'error': result.stderr
                                    }
                                    self.log_finding('ERROR', f'Broken Python installation at {python_exe}', 'python')

                            except subprocess.TimeoutExpired:
                                installations[root] = {
                                    'executable': python_exe,
                                    'version': 'timeout',
                                    'status': 'unresponsive'
                                }
                                self.log_finding('ERROR', f'Unresponsive Python installation at {python_exe}', 'python')

                            except Exception as e:
                                installations[root] = {
                                    'executable': python_exe,
                                    'version': 'error',
                                    'status': 'error',
                                    'error': str(e)
                                }
                                self.log_finding('ERROR', f'Error checking Python at {python_exe}: {str(e)}', 'python')

                except Exception as e:
                    self.log_finding('ERROR', f'Error scanning {base_path}: {str(e)}', 'python')

        self.results['python_installations'] = installations
        return installations

    def verify_virtual_environments(self) -> Dict[str, Any]:
        """
        Verify the integrity of virtual environments

        Teaching note (Day 25 - File operations): Checking for specific files
        and directories that should exist in a healthy virtual environment.
        """
        self.log_finding('INFO', 'Verifying virtual environments', 'venv')

        # Common venv locations (Day 6 - Lists)
        venv_paths = [
            "C:/EQ12/.venv",
            "C:/EQ12/.venv_new",
            "S:/EQ12/.venv"
        ]

        venv_results = {}

        for venv_path in venv_paths:
            if os.path.exists(venv_path):
                self.log_finding('INFO', f'Checking virtual environment: {venv_path}', 'venv')

                venv_info = {
                    'path': venv_path,
                    'status': 'unknown',
                    'issues': [],
                    'files_check': {}
                }

                # Critical files that should exist in a venv (Day 6 - Dictionary)
                critical_files = {
                    'activate_script': 'Scripts/Activate.ps1' if os.name == 'nt' else 'bin/activate',
                    'python_executable': 'Scripts/python.exe' if os.name == 'nt' else 'bin/python',
                    'pip_executable': 'Scripts/pip.exe' if os.name == 'nt' else 'bin/pip',
                    'pyvenv_cfg': 'pyvenv.cfg'
                }

                # Check each critical file (Day 9 - Loops + Day 19 - Error handling)
                for file_type, relative_path in critical_files.items():
                    full_path = os.path.join(venv_path, relative_path)
                    exists = os.path.exists(full_path)
                    venv_info['files_check'][file_type] = {
                        'path': full_path,
                        'exists': exists
                    }

                    if not exists:
                        venv_info['issues'].append(f'Missing {file_type}: {relative_path}')
                        self.log_finding('ERROR', f'Missing {file_type} in {venv_path}', 'venv')

                # Test if the venv Python is working
                python_exe = os.path.join(venv_path, critical_files['python_executable'])
                if os.path.exists(python_exe):
                    try:
                        result = subprocess.run(
                            [python_exe, '-c', 'import sys; print(sys.version)'],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )

                        if result.returncode == 0:
                            venv_info['python_version'] = result.stdout.strip()
                            self.log_finding('INFO', f'Virtual environment Python working: {venv_path}', 'venv')
                        else:
                            venv_info['issues'].append('Python executable not working')
                            self.log_finding('ERROR', f'Virtual environment Python broken: {venv_path}', 'venv')

                    except Exception as e:
                        venv_info['issues'].append(f'Python test failed: {str(e)}')
                        self.log_finding('ERROR', f'Virtual environment Python test failed: {venv_path}', 'venv')

                # Determine overall status
                if len(venv_info['issues']) == 0:
                    venv_info['status'] = 'healthy'
                elif len(venv_info['issues']) <= 2:
                    venv_info['status'] = 'degraded'
                else:
                    venv_info['status'] = 'broken'

                venv_results[venv_path] = venv_info

            else:
                self.log_finding('INFO', f'Virtual environment not found: {venv_path}', 'venv')

        self.results['virtual_environments'] = venv_results
        return venv_results

    def check_vscode_integration(self) -> Dict[str, Any]:
        """
        Check VS Code Python and Pylance integration health

        Teaching note (Day 25 - File operations): Reading and parsing configuration
        files to verify VS Code is properly configured for Python development.
        """
        self.log_finding('INFO', 'Checking VS Code integration', 'vscode')

        vscode_info = {
            'user_settings': {},
            'extensions': {},
            'workspace_storage': {},
            'issues': []
        }

        # Check VS Code user settings
        user_settings_path = os.path.expanduser('~/AppData/Roaming/Code/User/settings.json')
        if os.path.exists(user_settings_path):
            try:
                with open(user_settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                python_settings = {k: v for k, v in settings.items() if 'python' in k.lower()}
                vscode_info['user_settings'] = python_settings

                # Check for common Python configuration
                if 'python.defaultInterpreterPath' in settings:
                    interpreter_path = settings['python.defaultInterpreterPath']
                    if os.path.exists(interpreter_path):
                        self.log_finding('INFO', f'Default Python interpreter configured: {interpreter_path}', 'vscode')
                    else:
                        self.log_finding('ERROR', f'Configured Python interpreter not found: {interpreter_path}', 'vscode')
                        vscode_info['issues'].append(f'Missing interpreter: {interpreter_path}')

            except json.JSONDecodeError as e:
                self.log_finding('ERROR', f'Invalid JSON in VS Code settings: {str(e)}', 'vscode')
                vscode_info['issues'].append('Corrupt settings.json')
            except Exception as e:
                self.log_finding('ERROR', f'Error reading VS Code settings: {str(e)}', 'vscode')
        else:
            self.log_finding('WARNING', 'VS Code user settings not found', 'vscode')

        # Check VS Code extensions
        extensions_dir = os.path.expanduser('~/.vscode/extensions')
        if os.path.exists(extensions_dir):
            try:
                extensions = os.listdir(extensions_dir)
                python_extensions = [ext for ext in extensions if 'python' in ext.lower() or 'pylance' in ext.lower()]
                vscode_info['extensions'] = python_extensions

                if any('ms-python.python' in ext for ext in python_extensions):
                    self.log_finding('INFO', 'Python extension found', 'vscode')
                else:
                    self.log_finding('WARNING', 'Python extension not found', 'vscode')
                    vscode_info['issues'].append('Missing Python extension')

                if any('ms-python.vscode-pylance' in ext for ext in python_extensions):
                    self.log_finding('INFO', 'Pylance extension found', 'vscode')
                else:
                    self.log_finding('WARNING', 'Pylance extension not found', 'vscode')
                    vscode_info['issues'].append('Missing Pylance extension')

            except Exception as e:
                self.log_finding('ERROR', f'Error checking VS Code extensions: {str(e)}', 'vscode')

        self.results['vscode_integration'] = vscode_info
        return vscode_info

    def verify_file_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of critical Python and EQ12 files

        Teaching note (Day 22 - Advanced concepts): Using generators and hash
        functions to efficiently process large numbers of files without loading
        everything into memory at once.
        """
        self.log_finding('INFO', 'Verifying file integrity', 'files')

        integrity_info = {
            'scanned_files': 0,
            'corrupt_files': [],
            'suspicious_files': [],
            'empty_files': []
        }

        # Scan critical directories
        scan_paths = [
            "C:/EQ12/scripts",
            "C:/EQ12/configs"
        ]

        for scan_path in scan_paths:
            if os.path.exists(scan_path):
                try:
                    # Walk through directory structure (Day 25 - File operations)
                    for root, dirs, files in os.walk(scan_path):
                        # Skip __pycache__ directories
                        dirs[:] = [d for d in dirs if d != '__pycache__']

                        for file in files:
                            if file.endswith(('.py', '.json', '.ps1')):
                                file_path = os.path.join(root, file)
                                integrity_info['scanned_files'] += 1

                                try:
                                    # Check file size
                                    file_size = os.path.getsize(file_path)
                                    if file_size == 0:
                                        integrity_info['empty_files'].append(file_path)
                                        self.log_finding('WARNING', f'Empty file found: {file_path}', 'files')

                                    # Read and verify file content
                                    with open(file_path, 'rb') as f:
                                        content = f.read()

                                        # Check for null bytes (corruption indicator)
                                        if b'\x00' in content:
                                            integrity_info['corrupt_files'].append(file_path)
                                            self.log_finding('ERROR', f'Corrupt file (null bytes): {file_path}', 'files')

                                        # Calculate file hash for future integrity checks
                                        file_hash = hashlib.sha256(content).hexdigest()

                                        # Basic syntax check for Python files
                                        if file.endswith('.py'):
                                            try:
                                                compile(content, file_path, 'exec')
                                            except SyntaxError as e:
                                                integrity_info['corrupt_files'].append(file_path)
                                                self.log_finding('ERROR', f'Python syntax error in {file_path}: {str(e)}', 'files')

                                        # Basic JSON validation
                                        elif file.endswith('.json'):
                                            try:
                                                json.loads(content.decode('utf-8'))
                                            except json.JSONDecodeError as e:
                                                integrity_info['corrupt_files'].append(file_path)
                                                self.log_finding('ERROR', f'Invalid JSON in {file_path}: {str(e)}', 'files')

                                except Exception as e:
                                    integrity_info['suspicious_files'].append(file_path)
                                    self.log_finding('ERROR', f'Error reading file {file_path}: {str(e)}', 'files')

                except Exception as e:
                    self.log_finding('ERROR', f'Error scanning directory {scan_path}: {str(e)}', 'files')

        self.results['file_integrity'] = integrity_info
        return integrity_info

    def generate_recommendations(self) -> List[str]:
        """
        Generate actionable recommendations based on verification results

        Teaching note (Day 11 - Functions): This function analyzes all collected
        data and returns a list of specific actions to fix identified issues.
        """
        recommendations = []

        # Python installation recommendations
        python_installations = self.results.get('python_installations', {})
        working_installations = [info for info in python_installations.values() if info.get('status') == 'working']

        if not working_installations:
            recommendations.append("CRITICAL: Install Python 3.12+ from python.org")
        elif len(working_installations) > 1:
            recommendations.append("WARNING: Multiple Python installations detected - consider cleanup")

        # Virtual environment recommendations
        venv_results = self.results.get('virtual_environments', {})
        broken_venvs = [path for path, info in venv_results.items() if info.get('status') == 'broken']

        if broken_venvs:
            recommendations.append(f"REPAIR: Rebuild broken virtual environments: {', '.join(broken_venvs)}")

        # VS Code recommendations
        vscode_info = self.results.get('vscode_integration', {})
        vscode_issues = vscode_info.get('issues', [])

        if 'Missing Python extension' in vscode_issues:
            recommendations.append("INSTALL: Install Python extension in VS Code")

        if 'Missing Pylance extension' in vscode_issues:
            recommendations.append("INSTALL: Install Pylance extension in VS Code")

        # File integrity recommendations
        file_info = self.results.get('file_integrity', {})
        corrupt_files = file_info.get('corrupt_files', [])

        if corrupt_files:
            recommendations.append(f"REPAIR: Fix or restore corrupted files: {len(corrupt_files)} files affected")

        # General recommendations based on error counts
        if self.error_count > 0:
            recommendations.append(f"ATTENTION: {self.error_count} errors found - review log for details")

        if self.warning_count > 5:
            recommendations.append(f"MAINTENANCE: {self.warning_count} warnings suggest system maintenance needed")

        self.results['recommendations'] = recommendations
        return recommendations

    def save_results(self) -> str:
        """
        Save verification results to a JSON report file

        Teaching note (Day 25 - File operations): Writing structured data to a
        file in JSON format for later analysis or processing by other tools.
        """
        # Ensure logs directory exists
        log_dir = pathlib.Path("C:/EQ12/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = log_dir / f"eq12_verification_report_{timestamp}.json"

        try:
            # Convert results to ASCII-safe JSON
            json_str = json.dumps(self.results, indent=2, ensure_ascii=True)

            with open(report_path, 'w', encoding='ascii', errors='replace') as f:
                f.write(json_str)

            self.log_finding('INFO', f'Verification report saved: {report_path}', 'system')
            return str(report_path)

        except Exception as e:
            self.log_finding('ERROR', f'Failed to save report: {str(e)}', 'system')
            return ""

    def run_full_verification(self) -> Dict[str, Any]:
        """
        Run complete system verification and return results

        Teaching note (Day 11 - Functions): This is the main orchestration function
        that calls all other verification methods in the correct order.
        """
        self.log_finding('INFO', '=== EQ12 Expert System Verification Started ===', 'system')

        try:
            # Run all verification phases
            self.verify_system_info()
            self.discover_python_installations()
            self.verify_virtual_environments()
            self.check_vscode_integration()
            self.verify_file_integrity()
            self.generate_recommendations()

            # Save results
            report_path = self.save_results()

            # Print summary
            self.log_finding('INFO', '=== Verification Summary ===', 'system')
            self.log_finding('INFO', f'Errors: {self.error_count}', 'system')
            self.log_finding('INFO', f'Warnings: {self.warning_count}', 'system')
            self.log_finding('INFO', f'Report saved: {report_path}', 'system')

            # Print recommendations
            recommendations = self.results.get('recommendations', [])
            if recommendations:
                self.log_finding('INFO', '=== Recommendations ===', 'system')
                for i, rec in enumerate(recommendations, 1):
                    self.log_finding('INFO', f'{i}. {rec}', 'system')

            self.log_finding('INFO', '=== EQ12 Expert System Verification Completed ===', 'system')

        except Exception as e:
            self.log_finding('ERROR', f'Verification failed: {str(e)}', 'system')
            raise

        return self.results

def main():
    """
    Main entry point for the verification script

    Teaching note (Day 11 - Functions): The main function provides a clean
    entry point and handles command-line execution properly.
    """
    try:
        # Create and run verifier (Day 20 - Classes)
        verifier = EQ12SystemVerifier()
        results = verifier.run_full_verification()

        # Exit with appropriate code
        if verifier.error_count > 0:
            sys.exit(1)  # Exit with error if issues found
        else:
            sys.exit(0)  # Exit successfully

    except KeyboardInterrupt:
        print("\nVerification cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
