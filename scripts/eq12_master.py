#!/usr/bin/env python3
"""
EQ12 Expert Master Control - Unified System Management
Professional Engineering Grade Master Controller

Author: EQ12 Engineering Team
Version: 2.1.0
Date: 2025-11-22
Python: 3.12+

This is the MASTER CONTROL SCRIPT for the entire EQ12 Expert Repair Suite.
It provides unified access to all system management, repair, and validation tools:

1. System Bootstrap (complete environment setup)
2. Repair Operations (PowerShell-based comprehensive repairs)
3. Verification & Validation (Python-based system checks)
4. ASCII Cleaning (code compatibility fixes)
5. Test Suite Execution (comprehensive validation)
6. Performance Monitoring & Health Checks
7. Emergency Recovery Operations

Usage Examples:
  python eq12_master.py --bootstrap          # Complete system setup
  python eq12_master.py --repair             # Run comprehensive repairs
  python eq12_master.py --verify             # Validate system health
  python eq12_master.py --test               # Run full test suite
  python eq12_master.py --clean              # Clean ASCII issues
  python eq12_master.py --emergency          # Emergency recovery
  python eq12_master.py --all                # Run everything

Teaching Notes (30-Day Python Curriculum Integration):
- System architecture (Day 30): Master control pattern for complex systems
- Error handling (Day 19): Comprehensive exception management with recovery
- Logging systems (Day 21): Professional logging with multiple outputs
- File operations (Day 12): Safe file handling with backup creation
- Process management (Day 25): Subprocess coordination and monitoring
"""

import sys
import os
import argparse
import pathlib
import json
import subprocess
import time
from datetime import datetime
import logging
import traceback
import platform

class EQ12MasterController:
    """
    Expert Master Controller for the complete EQ12 system

    This class orchestrates all repair, validation, and maintenance operations
    with professional error handling, logging, and recovery capabilities.
    """

    def __init__(self, verbose=True):
        """Initialize the master controller"""
        self.verbose = verbose
        self.start_time = datetime.now()

        # System configuration
        self.config = {
            'eq12_root': 'C:/EQ12',
            'scripts_path': 'C:/EQ12/scripts',
            'logs_path': 'C:/EQ12/logs',
            'venv_path': 'C:/EQ12/.venv',
            'expert_scripts': {
                'bootstrap': 'eq12_bootstrap.py',
                'repair': 'eq12_repair.ps1',
                'verify': 'eq12_verify.py',
                'clean': 'eq12_clean_ascii.py',
                'test': 'eq12_test_suite.py'
            }
        }

        # Initialize logging
        self.setup_logging()

        # Operation tracking
        self.operations = {
            'bootstrap': {'status': 'pending', 'start_time': None, 'end_time': None, 'success': None},
            'repair': {'status': 'pending', 'start_time': None, 'end_time': None, 'success': None},
            'verify': {'status': 'pending', 'start_time': None, 'end_time': None, 'success': None},
            'clean': {'status': 'pending', 'start_time': None, 'end_time': None, 'success': None},
            'test': {'status': 'pending', 'start_time': None, 'end_time': None, 'success': None}
        }

        self.errors = []
        self.warnings = []

        self.logger.info("=== EQ12 Expert Master Controller Initialized ===")
        self.logger.info(f"System: {platform.system()} {platform.release()}")
        self.logger.info(f"Python: {sys.version}")
        self.logger.info(f"Working Directory: {os.getcwd()}")

    def setup_logging(self):
        """Set up comprehensive logging system"""
        # Ensure logs directory exists
        logs_dir = pathlib.Path(self.config['logs_path'])
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped log file
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"eq12_master_controller_{timestamp}.log"

        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s [%(levelname)8s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='ascii', errors='replace'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('eq12_master')
        self.logger.info(f"Logging initialized: {log_file}")

    def run_script_operation(self, operation_name, script_name, args=None, timeout=600):
        """
        Run a script operation with comprehensive tracking and error handling

        Args:
            operation_name: Name of the operation for tracking
            script_name: Name of the script file to execute
            args: Additional arguments to pass to the script
            timeout: Maximum execution time in seconds

        Returns:
            bool: True if operation succeeded, False otherwise
        """
        if args is None:
            args = []

        # Update operation tracking
        self.operations[operation_name]['status'] = 'running'
        self.operations[operation_name]['start_time'] = datetime.now()

        script_path = pathlib.Path(self.config['scripts_path']) / script_name

        self.logger.info(f"Starting {operation_name} operation: {script_name}")

        try:
            # Check if script exists
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")

            # Determine how to execute the script
            if script_name.endswith('.py'):
                command = [sys.executable, str(script_path)] + args
            elif script_name.endswith('.ps1'):
                command = ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                          '-File', str(script_path)] + args
            else:
                raise ValueError(f"Unsupported script type: {script_name}")

            # Execute the script
            self.logger.info(f"Executing: {' '.join(command)}")

            start_time = time.time()
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.config['scripts_path']
            )
            execution_time = time.time() - start_time

            # Log execution results
            self.logger.info(f"Execution completed in {execution_time:.2f} seconds")
            self.logger.info(f"Return code: {result.returncode}")

            if result.stdout:
                self.logger.debug(f"STDOUT:\n{result.stdout}")

            if result.stderr:
                if result.returncode == 0:
                    self.logger.warning(f"STDERR (warnings):\n{result.stderr}")
                else:
                    self.logger.error(f"STDERR (errors):\n{result.stderr}")

            # Determine success
            success = result.returncode == 0

            # Update tracking
            self.operations[operation_name]['end_time'] = datetime.now()
            self.operations[operation_name]['status'] = 'completed'
            self.operations[operation_name]['success'] = success
            self.operations[operation_name]['execution_time'] = execution_time
            self.operations[operation_name]['return_code'] = result.returncode

            if success:
                self.logger.info(f"✅ {operation_name} operation completed successfully")
            else:
                error_msg = f"❌ {operation_name} operation failed with return code {result.returncode}"
                self.logger.error(error_msg)
                self.errors.append(error_msg)

            return success

        except subprocess.TimeoutExpired:
            error_msg = f"❌ {operation_name} operation timed out after {timeout} seconds"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            self.operations[operation_name]['status'] = 'timeout'
            self.operations[operation_name]['success'] = False
            return False

        except FileNotFoundError as e:
            error_msg = f"❌ {operation_name} operation failed: {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            self.operations[operation_name]['status'] = 'file_not_found'
            self.operations[operation_name]['success'] = False
            return False

        except Exception as e:
            error_msg = f"❌ {operation_name} operation failed with unexpected error: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.errors.append(error_msg)
            self.operations[operation_name]['status'] = 'error'
            self.operations[operation_name]['success'] = False
            return False

    def run_bootstrap(self, force=False):
        """Run the complete system bootstrap"""
        self.logger.info("🚀 Starting EQ12 System Bootstrap")
        args = ['--force'] if force else []
        return self.run_script_operation('bootstrap', self.config['expert_scripts']['bootstrap'], args)

    def run_repair(self):
        """Run comprehensive system repairs"""
        self.logger.info("🔧 Starting EQ12 System Repair")
        return self.run_script_operation('repair', self.config['expert_scripts']['repair'])

    def run_verification(self):
        """Run system verification and health checks"""
        self.logger.info("🔍 Starting EQ12 System Verification")
        return self.run_script_operation('verify', self.config['expert_scripts']['verify'])

    def run_ascii_cleaning(self):
        """Run ASCII cleaning operations"""
        self.logger.info("🧹 Starting EQ12 ASCII Cleaning")
        return self.run_script_operation('clean', self.config['expert_scripts']['clean'])

    def run_test_suite(self):
        """Run comprehensive test suite"""
        self.logger.info("🧪 Starting EQ12 Test Suite")
        return self.run_script_operation('test', self.config['expert_scripts']['test'])

    def run_emergency_recovery(self):
        """Run emergency recovery operations"""
        self.logger.warning("🚨 Starting EMERGENCY RECOVERY sequence")
        self.logger.warning("This will attempt to repair critical system issues")

        recovery_success = True

        # Step 1: Try to repair the system
        self.logger.info("Step 1: Attempting system repair...")
        if not self.run_repair():
            self.warnings.append("System repair had issues but continuing...")

        # Step 2: Clean ASCII issues that might be causing problems
        self.logger.info("Step 2: Cleaning ASCII compatibility issues...")
        if not self.run_ascii_cleaning():
            self.warnings.append("ASCII cleaning had issues but continuing...")

        # Step 3: Re-bootstrap if necessary
        self.logger.info("Step 3: Re-bootstrapping system if needed...")
        if not self.run_bootstrap(force=True):
            self.logger.error("Bootstrap failed during emergency recovery")
            recovery_success = False

        # Step 4: Verify the recovery worked
        self.logger.info("Step 4: Verifying emergency recovery...")
        if not self.run_verification():
            self.logger.error("Verification failed after emergency recovery")
            recovery_success = False

        if recovery_success:
            self.logger.info("✅ Emergency recovery completed successfully")
        else:
            self.logger.error("❌ Emergency recovery failed - manual intervention required")

        return recovery_success

    def run_complete_operation(self, include_test=True):
        """Run all operations in sequence"""
        self.logger.info("🌟 Starting COMPLETE EQ12 system operation")

        operations_success = []

        # 1. Bootstrap
        operations_success.append(self.run_bootstrap())

        # 2. Repair
        operations_success.append(self.run_repair())

        # 3. Clean
        operations_success.append(self.run_ascii_cleaning())

        # 4. Verify
        operations_success.append(self.run_verification())

        # 5. Test (optional)
        if include_test:
            operations_success.append(self.run_test_suite())

        # Calculate success rate
        total_operations = len(operations_success)
        successful_operations = sum(operations_success)
        success_rate = successful_operations / total_operations if total_operations > 0 else 0

        self.logger.info(f"Complete operation finished: {successful_operations}/{total_operations} successful ({success_rate:.1%})")

        return success_rate >= 0.8  # 80% success rate required

    def generate_master_report(self):
        """Generate comprehensive master report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        # Calculate summary statistics
        completed_operations = len([op for op in self.operations.values() if op['status'] == 'completed'])
        successful_operations = len([op for op in self.operations.values() if op['success'] is True])
        total_operations = len([op for op in self.operations.values() if op['status'] != 'pending'])

        # Create comprehensive report
        report = {
            'timestamp': end_time.isoformat(),
            'session_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_duration_seconds': total_duration,
                'system': {
                    'os': platform.system(),
                    'release': platform.release(),
                    'architecture': platform.architecture()[0],
                    'python_version': sys.version,
                    'working_directory': os.getcwd()
                }
            },
            'configuration': self.config,
            'operations': self.operations,
            'summary': {
                'total_operations': total_operations,
                'completed_operations': completed_operations,
                'successful_operations': successful_operations,
                'success_rate': successful_operations / total_operations if total_operations > 0 else 0,
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings)
            },
            'errors': self.errors,
            'warnings': self.warnings
        }

        # Save report
        timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        report_path = pathlib.Path(self.config['logs_path']) / f"eq12_master_report_{timestamp}.json"

        try:
            with open(report_path, 'w', encoding='ascii', errors='replace') as f:
                json.dump(report, f, indent=2, ensure_ascii=True, default=str)

            self.logger.info(f"Master report saved: {report_path}")

        except Exception as e:
            self.logger.error(f"Failed to save master report: {str(e)}")

        return report, report_path

    def print_final_summary(self):
        """Print final summary and status"""
        # Generate report
        report, report_path = self.generate_master_report()

        print("\n" + "="*80)
        print("🎯 EQ12 EXPERT MASTER CONTROLLER - FINAL SUMMARY")
        print("="*80)

        # Session info
        duration_mins = report['session_info']['total_duration_seconds'] / 60
        print(f"⏱️  Session Duration: {duration_mins:.1f} minutes")
        print(f"🖥️  System: {report['session_info']['system']['os']} {report['session_info']['system']['release']}")

        # Operations summary
        print(f"\n📊 Operations Summary:")
        print(f"   Total Operations: {report['summary']['total_operations']}")
        print(f"   Successful: {report['summary']['successful_operations']}")
        print(f"   Success Rate: {report['summary']['success_rate']:.1%}")

        # Individual operation status
        print(f"\n🔍 Operation Details:")
        for op_name, op_data in self.operations.items():
            if op_data['status'] != 'pending':
                status_icon = "✅" if op_data['success'] else "❌"
                duration = ""
                if 'execution_time' in op_data:
                    duration = f" ({op_data['execution_time']:.1f}s)"
                print(f"   {status_icon} {op_name.capitalize()}: {op_data['status']}{duration}")

        # Issues summary
        if self.errors:
            print(f"\n⚠️  Errors ({len(self.errors)}):")
            for error in self.errors[-3:]:  # Show last 3 errors
                print(f"   • {error}")

        if self.warnings:
            print(f"\n🟡 Warnings ({len(self.warnings)}):")
            for warning in self.warnings[-3:]:  # Show last 3 warnings
                print(f"   • {warning}")

        # Final assessment
        overall_success = report['summary']['success_rate'] >= 0.8

        print(f"\n🎯 Final Assessment:")
        if overall_success:
            print("   ✅ SYSTEM OPERATIONAL - EQ12 is ready for production use!")
            print("   🚀 All critical components are functioning correctly.")
        else:
            print("   ❌ SYSTEM REQUIRES ATTENTION")
            print("   🔧 Review errors and run specific repair operations.")

        print(f"\n📋 Detailed Report: {report_path}")
        print("="*80)

        return overall_success

def main():
    """Main entry point for the master controller"""
    parser = argparse.ArgumentParser(
        description='EQ12 Expert Master Controller - Unified System Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --bootstrap          Complete system setup
  %(prog)s --repair             Run comprehensive repairs
  %(prog)s --verify             Validate system health
  %(prog)s --test               Run full test suite
  %(prog)s --clean              Clean ASCII issues
  %(prog)s --emergency          Emergency recovery
  %(prog)s --all                Run everything
  %(prog)s --all --no-test      Run everything except tests
        """
    )

    # Operation selection
    parser.add_argument('--bootstrap', action='store_true', help='Run system bootstrap')
    parser.add_argument('--repair', action='store_true', help='Run system repairs')
    parser.add_argument('--verify', action='store_true', help='Run system verification')
    parser.add_argument('--clean', action='store_true', help='Run ASCII cleaning')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--emergency', action='store_true', help='Run emergency recovery')
    parser.add_argument('--all', action='store_true', help='Run all operations')

    # Modifiers
    parser.add_argument('--force', action='store_true', help='Force reinstall/repair')
    parser.add_argument('--no-test', action='store_true', help='Skip test suite (with --all)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')

    args = parser.parse_args()

    # Check if at least one operation is selected
    operations_selected = any([
        args.bootstrap, args.repair, args.verify, args.clean,
        args.test, args.emergency, args.all
    ])

    if not operations_selected:
        print("❌ Error: Please select at least one operation to perform.")
        print("Use --help to see available options.")
        return 1

    try:
        # Initialize master controller
        controller = EQ12MasterController(verbose=args.verbose and not args.quiet)

        print("🌟 EQ12 Expert Master Controller")
        print("Professional Engineering Grade System Management")
        print("="*60)

        # Execute requested operations
        overall_success = True

        if args.all:
            # Run complete operation
            overall_success = controller.run_complete_operation(include_test=not args.no_test)

        elif args.emergency:
            # Run emergency recovery
            overall_success = controller.run_emergency_recovery()

        else:
            # Run individual operations
            if args.bootstrap:
                if not controller.run_bootstrap(force=args.force):
                    overall_success = False

            if args.repair:
                if not controller.run_repair():
                    overall_success = False

            if args.clean:
                if not controller.run_ascii_cleaning():
                    overall_success = False

            if args.verify:
                if not controller.run_verification():
                    overall_success = False

            if args.test:
                if not controller.run_test_suite():
                    overall_success = False

        # Print final summary
        final_success = controller.print_final_summary()

        # Return appropriate exit code
        if final_success and overall_success:
            return 0
        else:
            return 1

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        return 130

    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
