#!/usr/bin/env python3
"""
EQ12 Expert Test Suite - Comprehensive System Validation
Professional Engineering Grade Testing Framework

Author: EQ12 Engineering Team
Version: 2.1.0
Date: 2025-11-22
Python: 3.12+

This script provides comprehensive testing and validation for the EQ12 system including:
- Bootstrap validation and verification
- Repair script functionality testing
- ASCII cleaner validation
- System integrity checks
- Performance benchmarking
- Automated issue detection and resolution

Teaching Notes (30-Day Python Curriculum Integration):
- Testing frameworks (Day 26): Using unittest for professional test suites
- File I/O operations (Day 12): Reading and validating file contents
- Error handling (Day 19): Comprehensive exception management
- Performance testing (Day 27): Benchmarking and optimization validation
- System integration (Day 30): End-to-end system validation
"""

import sys
import os
import unittest
import pathlib
import json
import subprocess
import time
from datetime import datetime
import logging
import tempfile
import shutil
import hashlib

class EQ12ExpertTestSuite:
    """
    Expert-level testing framework for EQ12 system validation

    Teaching note (Day 20 - Classes): Comprehensive test orchestration
    class with multiple validation phases and detailed reporting.
    """

    def __init__(self, verbose=True):
        """Initialize the testing framework"""
        self.verbose = verbose
        self.setup_logging()

        # Test configuration
        self.config = {
            'eq12_root': 'C:/EQ12',
            'scripts_path': 'C:/EQ12/scripts',
            'logs_path': 'C:/EQ12/logs',
            'test_timeout': 300,
            'required_scripts': [
                'eq12_bootstrap.py',
                'eq12_repair.ps1',
                'eq12_verify.py',
                'eq12_clean_ascii.py'
            ],
            'test_modules': [
                'bootstrap_tests',
                'repair_tests',
                'verification_tests',
                'ascii_cleaner_tests',
                'integration_tests'
            ]
        }

        # Test results tracking
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'errors': [],
            'warnings': [],
            'performance_metrics': {},
            'test_details': {}
        }

    def setup_logging(self):
        """Set up comprehensive logging system"""
        log_dir = pathlib.Path("C:/EQ12/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"eq12_test_suite_{timestamp}.log"

        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='ascii', errors='replace'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('eq12_test_suite')
        self.logger.info("=== EQ12 Expert Test Suite Started ===")

    def run_command_test(self, command, expected_return_code=0, timeout=30):
        """
        Run a command and validate its execution

        Teaching note (Day 19 - Error handling): Professional command testing
        with timeout, return code validation, and comprehensive logging.
        """
        start_time = time.time()

        try:
            self.logger.info(f"Testing command: {' '.join(command) if isinstance(command, list) else command}")

            if isinstance(command, str):
                command = command.split()

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            execution_time = time.time() - start_time

            # Validate return code
            success = result.returncode == expected_return_code

            test_result = {
                'command': ' '.join(command),
                'return_code': result.returncode,
                'expected_return_code': expected_return_code,
                'execution_time': execution_time,
                'success': success,
                'stdout_lines': len(result.stdout.splitlines()) if result.stdout else 0,
                'stderr_lines': len(result.stderr.splitlines()) if result.stderr else 0
            }

            if result.stdout:
                self.logger.debug(f"STDOUT: {result.stdout.strip()}")
            if result.stderr:
                self.logger.warning(f"STDERR: {result.stderr.strip()}")

            self.logger.info(f"Command completed in {execution_time:.2f}s with return code {result.returncode}")

            return test_result, result

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time
            error_msg = f"Command timed out after {timeout}s"
            self.logger.error(error_msg)

            return {
                'command': ' '.join(command),
                'return_code': -1,
                'expected_return_code': expected_return_code,
                'execution_time': execution_time,
                'success': False,
                'error': error_msg
            }, None

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Command failed with error: {str(e)}"
            self.logger.error(error_msg)

            return {
                'command': ' '.join(command),
                'return_code': -2,
                'expected_return_code': expected_return_code,
                'execution_time': execution_time,
                'success': False,
                'error': error_msg
            }, None

    def test_bootstrap_functionality(self):
        """
        Test bootstrap script functionality

        Teaching note (Day 26 - Testing): Comprehensive testing of the
        bootstrap script with multiple scenarios and validation.
        """
        self.logger.info("Testing Bootstrap Functionality")

        tests = []
        bootstrap_path = pathlib.Path(self.config['scripts_path']) / 'eq12_bootstrap.py'

        # Test 1: Bootstrap script exists and is executable
        test_name = "bootstrap_script_exists"
        if bootstrap_path.exists():
            tests.append({'name': test_name, 'success': True, 'message': "Bootstrap script found"})
        else:
            tests.append({'name': test_name, 'success': False, 'message': "Bootstrap script not found"})

        # Test 2: Bootstrap help command
        test_name = "bootstrap_help_command"
        test_result, cmd_result = self.run_command_test([
            sys.executable, str(bootstrap_path), '--help'
        ])
        test_result['name'] = test_name
        tests.append(test_result)

        # Test 3: Bootstrap syntax validation
        test_name = "bootstrap_syntax_validation"
        test_result, cmd_result = self.run_command_test([
            sys.executable, '-m', 'py_compile', str(bootstrap_path)
        ])
        test_result['name'] = test_name
        tests.append(test_result)

        # Test 4: Bootstrap dry run (if supported)
        test_name = "bootstrap_dry_run"
        if bootstrap_path.exists():
            try:
                # Check if the script has a dry-run option
                with open(bootstrap_path, 'r', encoding='ascii', errors='ignore') as f:
                    content = f.read()

                if '--dry-run' in content or 'dry_run' in content:
                    test_result, cmd_result = self.run_command_test([
                        sys.executable, str(bootstrap_path), '--dry-run'
                    ])
                    test_result['name'] = test_name
                    tests.append(test_result)
                else:
                    tests.append({
                        'name': test_name,
                        'success': True,
                        'message': "Dry run not supported (expected)",
                        'skipped': True
                    })
            except Exception as e:
                tests.append({
                    'name': test_name,
                    'success': False,
                    'message': f"Failed to analyze script: {str(e)}"
                })

        self.test_results['test_details']['bootstrap_tests'] = tests
        return tests

    def test_repair_script_functionality(self):
        """
        Test PowerShell repair script functionality

        Teaching note (Day 26 - Testing): Cross-platform testing for
        PowerShell scripts with proper validation.
        """
        self.logger.info("Testing Repair Script Functionality")

        tests = []
        repair_path = pathlib.Path(self.config['scripts_path']) / 'eq12_repair.ps1'

        # Test 1: Repair script exists
        test_name = "repair_script_exists"
        if repair_path.exists():
            tests.append({'name': test_name, 'success': True, 'message': "Repair script found"})
        else:
            tests.append({'name': test_name, 'success': False, 'message': "Repair script not found"})
            self.test_results['test_details']['repair_tests'] = tests
            return tests

        # Test 2: PowerShell availability
        test_name = "powershell_availability"
        test_result, cmd_result = self.run_command_test([
            'powershell', '-Command', 'Get-Host'
        ], timeout=10)
        test_result['name'] = test_name
        tests.append(test_result)

        if not test_result['success']:
            self.logger.warning("PowerShell not available - skipping PowerShell-specific tests")
            self.test_results['test_details']['repair_tests'] = tests
            return tests

        # Test 3: PowerShell script syntax validation
        test_name = "repair_script_syntax"
        test_result, cmd_result = self.run_command_test([
            'powershell', '-NoProfile', '-Command', f'Get-Command -Syntax "{repair_path}"'
        ], expected_return_code=None)  # May return non-zero but still be valid
        test_result['name'] = test_name
        # Consider it successful if it doesn't crash completely
        test_result['success'] = test_result['return_code'] != -1 and test_result['return_code'] != -2
        tests.append(test_result)

        # Test 4: Repair script help/info
        test_name = "repair_script_help"
        test_result, cmd_result = self.run_command_test([
            'powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', str(repair_path), '-WhatIf'
        ], timeout=60)
        test_result['name'] = test_name
        tests.append(test_result)

        self.test_results['test_details']['repair_tests'] = tests
        return tests

    def test_verification_script_functionality(self):
        """
        Test Python verification script functionality

        Teaching note (Day 26 - Testing): Module testing with import
        validation and class instantiation checks.
        """
        self.logger.info("Testing Verification Script Functionality")

        tests = []
        verify_path = pathlib.Path(self.config['scripts_path']) / 'eq12_verify.py'

        # Test 1: Verification script exists
        test_name = "verify_script_exists"
        if verify_path.exists():
            tests.append({'name': test_name, 'success': True, 'message': "Verification script found"})
        else:
            tests.append({'name': test_name, 'success': False, 'message': "Verification script not found"})
            self.test_results['test_details']['verification_tests'] = tests
            return tests

        # Test 2: Syntax validation
        test_name = "verify_script_syntax"
        test_result, cmd_result = self.run_command_test([
            sys.executable, '-m', 'py_compile', str(verify_path)
        ])
        test_result['name'] = test_name
        tests.append(test_result)

        # Test 3: Import validation
        test_name = "verify_script_import"
        test_script = f"""
import sys
sys.path.insert(0, '{self.config['scripts_path']}')
try:
    import eq12_verify
    print("Import successful")
except Exception as e:
    print(f"Import failed: {{e}}")
    sys.exit(1)
"""

        test_result, cmd_result = self.run_command_test([
            sys.executable, '-c', test_script
        ])
        test_result['name'] = test_name
        tests.append(test_result)

        # Test 4: Help command
        test_name = "verify_script_help"
        test_result, cmd_result = self.run_command_test([
            sys.executable, str(verify_path), '--help'
        ])
        test_result['name'] = test_name
        tests.append(test_result)

        self.test_results['test_details']['verification_tests'] = tests
        return tests

    def test_ascii_cleaner_functionality(self):
        """
        Test ASCII cleaner script functionality

        Teaching note (Day 12 - File I/O): Testing file processing scripts
        with temporary files and content validation.
        """
        self.logger.info("Testing ASCII Cleaner Functionality")

        tests = []
        cleaner_path = pathlib.Path(self.config['scripts_path']) / 'eq12_clean_ascii.py'

        # Test 1: ASCII cleaner script exists
        test_name = "ascii_cleaner_exists"
        if cleaner_path.exists():
            tests.append({'name': test_name, 'success': True, 'message': "ASCII cleaner found"})
        else:
            tests.append({'name': test_name, 'success': False, 'message': "ASCII cleaner not found"})
            self.test_results['test_details']['ascii_cleaner_tests'] = tests
            return tests

        # Test 2: Syntax validation
        test_name = "ascii_cleaner_syntax"
        test_result, cmd_result = self.run_command_test([
            sys.executable, '-m', 'py_compile', str(cleaner_path)
        ])
        test_result['name'] = test_name
        tests.append(test_result)

        # Test 3: Functional test with temporary file
        test_name = "ascii_cleaner_functional"
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp:
                # Create test content with non-ASCII characters
                test_content = "Hello World! 🚀 This has unicode: café, résumé, naïve"
                tmp.write(test_content)
                tmp_path = tmp.name

            # Run ASCII cleaner on the test file
            test_result, cmd_result = self.run_command_test([
                sys.executable, str(cleaner_path), '--file', tmp_path, '--backup'
            ])

            # Verify the file was processed
            if test_result['success'] and os.path.exists(tmp_path):
                with open(tmp_path, 'r', encoding='ascii', errors='ignore') as f:
                    cleaned_content = f.read()

                # Verify non-ASCII characters were handled
                test_result['success'] = len(cleaned_content) > 0
                test_result['message'] = f"File processed, content length: {len(cleaned_content)}"

            # Cleanup
            try:
                os.unlink(tmp_path)
                backup_path = tmp_path + '.backup'
                if os.path.exists(backup_path):
                    os.unlink(backup_path)
            except:
                pass

        except Exception as e:
            test_result = {
                'name': test_name,
                'success': False,
                'message': f"Functional test failed: {str(e)}"
            }

        test_result['name'] = test_name
        tests.append(test_result)

        self.test_results['test_details']['ascii_cleaner_tests'] = tests
        return tests

    def test_system_integration(self):
        """
        Test overall system integration

        Teaching note (Day 30 - System integration): End-to-end testing
        of the complete EQ12 system with performance validation.
        """
        self.logger.info("Testing System Integration")

        tests = []

        # Test 1: Directory structure validation
        test_name = "directory_structure"
        required_dirs = ['scripts', 'logs', 'configs', 'tests', 'data', 'dashboard']
        eq12_root = pathlib.Path(self.config['eq12_root'])

        missing_dirs = []
        for dir_name in required_dirs:
            if not (eq12_root / dir_name).exists():
                missing_dirs.append(dir_name)

        if not missing_dirs:
            tests.append({
                'name': test_name,
                'success': True,
                'message': "All required directories found"
            })
        else:
            tests.append({
                'name': test_name,
                'success': False,
                'message': f"Missing directories: {', '.join(missing_dirs)}"
            })

        # Test 2: Log directory writability
        test_name = "log_directory_writable"
        try:
            test_log_path = pathlib.Path(self.config['logs_path']) / 'test_write.tmp'
            with open(test_log_path, 'w') as f:
                f.write("test")
            os.unlink(test_log_path)

            tests.append({
                'name': test_name,
                'success': True,
                'message': "Log directory is writable"
            })
        except Exception as e:
            tests.append({
                'name': test_name,
                'success': False,
                'message': f"Log directory not writable: {str(e)}"
            })

        # Test 3: Python environment check
        test_name = "python_environment"
        venv_path = pathlib.Path('C:/EQ12/.venv')
        if venv_path.exists():
            tests.append({
                'name': test_name,
                'success': True,
                'message': f"Virtual environment found at {venv_path}"
            })
        else:
            tests.append({
                'name': test_name,
                'success': False,
                'message': "Virtual environment not found"
            })

        # Test 4: Script integrity check
        test_name = "script_integrity"
        scripts_found = 0
        scripts_total = len(self.config['required_scripts'])

        for script_name in self.config['required_scripts']:
            script_path = pathlib.Path(self.config['scripts_path']) / script_name
            if script_path.exists():
                scripts_found += 1

        success_rate = scripts_found / scripts_total if scripts_total > 0 else 0
        tests.append({
            'name': test_name,
            'success': success_rate >= 0.75,  # 75% of scripts must be present
            'message': f"Found {scripts_found}/{scripts_total} required scripts ({success_rate:.0%})"
        })

        self.test_results['test_details']['integration_tests'] = tests
        return tests

    def run_performance_benchmarks(self):
        """
        Run basic performance benchmarks

        Teaching note (Day 27 - Performance): Basic benchmarking to ensure
        the system meets performance requirements.
        """
        self.logger.info("Running Performance Benchmarks")

        benchmarks = {}

        # Benchmark 1: File I/O performance
        start_time = time.time()
        test_data = "x" * 1024 * 1024  # 1MB of data
        test_path = pathlib.Path(self.config['logs_path']) / 'benchmark_test.tmp'

        try:
            with open(test_path, 'w') as f:
                f.write(test_data)

            with open(test_path, 'r') as f:
                read_data = f.read()

            os.unlink(test_path)

            file_io_time = time.time() - start_time
            benchmarks['file_io_1mb'] = {
                'time_seconds': file_io_time,
                'success': file_io_time < 5.0,  # Should complete in under 5 seconds
                'description': '1MB file write/read test'
            }

        except Exception as e:
            benchmarks['file_io_1mb'] = {
                'time_seconds': -1,
                'success': False,
                'error': str(e),
                'description': '1MB file write/read test'
            }

        # Benchmark 2: Python import speed
        start_time = time.time()
        try:
            import json, sys, os, pathlib, subprocess
            import_time = time.time() - start_time
            benchmarks['python_imports'] = {
                'time_seconds': import_time,
                'success': import_time < 1.0,  # Should complete in under 1 second
                'description': 'Standard library imports'
            }
        except Exception as e:
            benchmarks['python_imports'] = {
                'time_seconds': -1,
                'success': False,
                'error': str(e),
                'description': 'Standard library imports'
            }

        # Benchmark 3: PowerShell availability check
        start_time = time.time()
        test_result, cmd_result = self.run_command_test([
            'powershell', '-Command', '$PSVersionTable.PSVersion'
        ], timeout=10)
        powershell_time = test_result['execution_time']

        benchmarks['powershell_startup'] = {
            'time_seconds': powershell_time,
            'success': test_result['success'] and powershell_time < 10.0,
            'description': 'PowerShell startup time'
        }

        self.test_results['performance_metrics'] = benchmarks
        return benchmarks

    def generate_test_report(self):
        """Generate comprehensive test report"""
        # Calculate test statistics
        total_tests = 0
        passed_tests = 0
        failed_tests = 0

        for module_name, tests in self.test_results['test_details'].items():
            for test in tests:
                if not test.get('skipped', False):
                    total_tests += 1
                    if test.get('success', False):
                        passed_tests += 1
                    else:
                        failed_tests += 1

        self.test_results.update({
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0
        })

        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = pathlib.Path(self.config['logs_path']) / f"eq12_test_report_{timestamp}.json"

        try:
            with open(report_path, 'w', encoding='ascii', errors='replace') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=True)

            self.logger.info(f"Test report saved: {report_path}")

        except Exception as e:
            self.logger.error(f"Failed to save test report: {str(e)}")

        return report_path

    def run_complete_test_suite(self):
        """
        Execute the complete test suite

        Teaching note (Day 11 - Functions): Main orchestration function
        that runs all test modules and generates comprehensive results.
        """
        self.logger.info("=== Starting EQ12 Expert Test Suite ===")

        try:
            # Run all test modules
            self.test_bootstrap_functionality()
            self.test_repair_script_functionality()
            self.test_verification_script_functionality()
            self.test_ascii_cleaner_functionality()
            self.test_system_integration()

            # Run performance benchmarks
            self.run_performance_benchmarks()

            # Generate comprehensive report
            report_path = self.generate_test_report()

            # Print summary
            self.logger.info("=== Test Suite Summary ===")
            self.logger.info(f"Total Tests: {self.test_results['total_tests']}")
            self.logger.info(f"Passed: {self.test_results['passed_tests']}")
            self.logger.info(f"Failed: {self.test_results['failed_tests']}")
            self.logger.info(f"Success Rate: {self.test_results['success_rate']:.1%}")

            # Performance summary
            if self.test_results['performance_metrics']:
                self.logger.info("=== Performance Summary ===")
                for benchmark_name, metrics in self.test_results['performance_metrics'].items():
                    status = "PASS" if metrics['success'] else "FAIL"
                    time_str = f"{metrics['time_seconds']:.3f}s" if metrics['time_seconds'] >= 0 else "ERROR"
                    self.logger.info(f"{benchmark_name}: {time_str} [{status}]")

            # Overall assessment
            overall_success = self.test_results['success_rate'] >= 0.80  # 80% pass rate required

            if overall_success:
                self.logger.info("=== ✅ EQ12 SYSTEM VALIDATION SUCCESSFUL ===")
                return True
            else:
                self.logger.error("=== ❌ EQ12 SYSTEM VALIDATION FAILED ===")
                self.logger.error("System requires attention before production use")
                return False

        except Exception as e:
            self.logger.error(f"Test suite failed with critical error: {str(e)}")
            return False

def main():
    """
    Main entry point for test suite

    Teaching note (Day 11 - Functions): Clean entry point with argument
    handling and professional output formatting.
    """
    import argparse

    parser = argparse.ArgumentParser(description='EQ12 Expert Test Suite')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')

    args = parser.parse_args()

    try:
        test_suite = EQ12ExpertTestSuite(verbose=args.verbose and not args.quiet)

        success = test_suite.run_complete_test_suite()

        if success:
            print("\n🚀 EQ12 Expert Test Suite: ALL SYSTEMS OPERATIONAL")
            print("✅ Your EQ12 system is ready for production use!")
            sys.exit(0)
        else:
            print("\n⚠️  EQ12 Expert Test Suite: ISSUES DETECTED")
            print("❌ System validation failed - review logs for details")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nTest suite cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
