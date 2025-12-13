#!/usr/bin/env python3
"""
EQ12 Expert System Bootstrap - Complete Environment Setup
Professional Engineering Grade Python 3.12 Environment Bootstrap

Author: EQ12 Engineering Team
Version: 2.1.0
Date: 2025-11-22
Python: 3.12+

This script performs complete EQ12 system bootstrap including:
- Python 3.12 validation and installation
- Virtual environment creation and configuration
- VS Code Python extension setup
- Essential package installation
- Development environment optimization
- GitHub CLI and Copilot integration

Teaching Notes (30-Day Python Curriculum Integration):
- Environment management (Day 30): Setting up professional development environments
- Package management (Day 28): Installing and managing Python packages
- Virtual environments (Day 29): Isolated Python environments for projects
- Error handling (Day 19): Robust setup with comprehensive error checking
- System integration (Day 30): Integrating multiple development tools
"""

import sys
import os
import subprocess
import pathlib
import json
from datetime import datetime
import logging
import urllib.request
import zipfile
import shutil
import platform

class EQ12SystemBootstrap:
    """
    Expert-level system bootstrap for complete EQ12 Python development environment

    Teaching note (Day 20 - Classes): This class encapsulates the entire
    bootstrap process with clear phases and comprehensive error handling.
    """

    def __init__(self, force_reinstall=False, verbose=True):
        """Initialize the bootstrap system"""
        self.force_reinstall = force_reinstall
        self.verbose = verbose
        self.setup_logging()

        # System information
        self.system_info = {
            'os': platform.system(),
            'architecture': platform.architecture()[0],
            'python_version': sys.version,
            'platform': platform.platform()
        }

        # Bootstrap configuration
        self.config = {
            'python_version': '3.12',
            'venv_path': 'C:/EQ12/.venv',
            'scripts_path': 'C:/EQ12/scripts',
            'logs_path': 'C:/EQ12/logs',
            'required_packages': [
                'pip>=23.0',
                'setuptools>=68.0',
                'wheel>=0.41.0',
                'pylint>=3.0.0',
                'black>=23.0.0',
                'pytest>=7.4.0',
                'requests>=2.31.0',
                'pathlib2>=2.3.7',
                'colorama>=0.4.6',
                'python-dateutil>=2.8.2',
                'numpy>=1.24.0',
                'pandas>=2.0.0'
            ],
            'vscode_extensions': [
                'ms-python.python',
                'ms-python.vscode-pylance',
                'ms-toolsai.jupyter',
                'github.copilot',
                'github.copilot-chat'
            ]
        }

        # Bootstrap phases
        self.phases = [
            'system_check',
            'python_validation',
            'venv_creation',
            'package_installation',
            'vscode_setup',
            'github_integration',
            'verification',
            'optimization'
        ]

        self.phase_status = {phase: 'pending' for phase in self.phases}
        self.errors = []
        self.warnings = []

    def setup_logging(self):
        """Set up comprehensive logging system"""
        log_dir = pathlib.Path("C:/EQ12/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"eq12_bootstrap_{timestamp}.log"

        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='ascii', errors='replace'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('eq12_bootstrap')
        self.logger.info("=== EQ12 Expert System Bootstrap Started ===")

    def run_command(self, command, check=True, timeout=300):
        """
        Run shell command with comprehensive error handling

        Teaching note (Day 19 - Error handling): Professional command execution
        with timeout, error capture, and logging.
        """
        self.logger.info(f"Executing: {' '.join(command) if isinstance(command, list) else command}")

        try:
            if isinstance(command, str):
                # Split string command for subprocess
                command = command.split()

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=check,
                timeout=timeout
            )

            if result.stdout:
                self.logger.debug(f"STDOUT: {result.stdout.strip()}")
            if result.stderr:
                self.logger.warning(f"STDERR: {result.stderr.strip()}")

            return result

        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout}s: {' '.join(command)}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            raise

        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with exit code {e.returncode}: {' '.join(command)}"
            self.logger.error(error_msg)
            self.logger.error(f"Error output: {e.stderr}")
            self.errors.append(error_msg)
            if check:
                raise
            return e

        except Exception as e:
            error_msg = f"Unexpected error executing command: {str(e)}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            raise

    def phase_system_check(self):
        """
        Phase 1: Comprehensive system compatibility check

        Teaching note (Day 30 - System integration): Validating that the system
        meets all requirements for Python development.
        """
        self.logger.info("PHASE 1: System Compatibility Check")

        try:
            # Check Windows version
            if self.system_info['os'] != 'Windows':
                raise Exception(f"Unsupported OS: {self.system_info['os']} (Windows required)")

            # Check architecture
            if '64' not in self.system_info['architecture']:
                self.warnings.append("32-bit system detected - some features may be limited")

            # Check PowerShell availability
            try:
                self.run_command(['powershell', '-Command', 'Get-Host'], timeout=10)
                self.logger.info("PowerShell available")
            except:
                self.warnings.append("PowerShell not available - some features limited")

            # Check internet connectivity
            try:
                urllib.request.urlopen('https://python.org', timeout=10)
                self.logger.info("Internet connectivity confirmed")
            except:
                self.warnings.append("Limited internet connectivity - downloads may fail")

            # Check disk space
            free_space = shutil.disk_usage('C:').free // (1024**3)  # GB
            if free_space < 5:
                raise Exception(f"Insufficient disk space: {free_space}GB available (5GB minimum)")

            self.logger.info(f"System check passed - {free_space}GB disk space available")
            self.phase_status['system_check'] = 'completed'

        except Exception as e:
            self.logger.error(f"System check failed: {str(e)}")
            self.phase_status['system_check'] = 'failed'
            raise

    def phase_python_validation(self):
        """
        Phase 2: Python 3.12+ validation and installation if needed

        Teaching note (Day 30 - Environment management): Ensuring the correct
        Python version is available for development.
        """
        self.logger.info("PHASE 2: Python 3.12+ Validation")

        try:
            # Check current Python version
            version_info = sys.version_info
            current_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

            self.logger.info(f"Current Python: {current_version}")
            self.logger.info(f"Python executable: {sys.executable}")

            # Validate version requirement
            if version_info.major != 3 or version_info.minor < 12:
                self.logger.warning(f"Python {current_version} detected - Python 3.12+ recommended")

                # Look for Python 3.12 installation
                python312_paths = [
                    f"C:/Users/{os.environ.get('USERNAME', 'Unknown')}/AppData/Local/Programs/Python/Python312/python.exe",
                    "C:/Python312/python.exe",
                    "C:/Program Files/Python312/python.exe"
                ]

                python312_found = None
                for path in python312_paths:
                    if os.path.exists(path):
                        try:
                            result = self.run_command([path, '--version'])
                            if 'Python 3.12' in result.stdout:
                                python312_found = path
                                self.logger.info(f"Found Python 3.12: {path}")
                                break
                        except:
                            continue

                if not python312_found and not self.force_reinstall:
                    self.warnings.append("Python 3.12+ not found - consider upgrading for optimal compatibility")

            else:
                self.logger.info(f"Python {current_version} meets requirements")

            # Validate pip
            try:
                result = self.run_command([sys.executable, '-m', 'pip', '--version'])
                self.logger.info(f"Pip available: {result.stdout.strip()}")
            except:
                self.logger.error("Pip not available - attempting repair")
                try:
                    self.run_command([sys.executable, '-m', 'ensurepip', '--upgrade'])
                except:
                    raise Exception("Failed to install/repair pip")

            self.phase_status['python_validation'] = 'completed'

        except Exception as e:
            self.logger.error(f"Python validation failed: {str(e)}")
            self.phase_status['python_validation'] = 'failed'
            raise

    def phase_venv_creation(self):
        """
        Phase 3: Virtual environment creation and configuration

        Teaching note (Day 29 - Virtual environments): Creating isolated
        Python environments for project dependencies.
        """
        self.logger.info("PHASE 3: Virtual Environment Creation")

        try:
            venv_path = pathlib.Path(self.config['venv_path'])

            # Remove existing venv if force reinstall
            if self.force_reinstall and venv_path.exists():
                self.logger.info("Force reinstall - removing existing virtual environment")
                shutil.rmtree(venv_path)

            # Create virtual environment if it doesn't exist
            if not venv_path.exists():
                self.logger.info(f"Creating virtual environment: {venv_path}")
                self.run_command([sys.executable, '-m', 'venv', str(venv_path)])
            else:
                self.logger.info(f"Virtual environment already exists: {venv_path}")

            # Verify virtual environment
            venv_python = venv_path / 'Scripts' / 'python.exe'
            if not venv_python.exists():
                raise Exception("Virtual environment creation failed - python.exe not found")

            # Test virtual environment
            result = self.run_command([str(venv_python), '--version'])
            self.logger.info(f"Virtual environment Python: {result.stdout.strip()}")

            # Upgrade pip in virtual environment
            self.logger.info("Upgrading pip in virtual environment")
            self.run_command([str(venv_python), '-m', 'pip', 'install', '--upgrade', 'pip'])

            self.phase_status['venv_creation'] = 'completed'

        except Exception as e:
            self.logger.error(f"Virtual environment creation failed: {str(e)}")
            self.phase_status['venv_creation'] = 'failed'
            raise

    def phase_package_installation(self):
        """
        Phase 4: Essential package installation

        Teaching note (Day 28 - Package management): Installing required
        packages for Python development and EQ12 functionality.
        """
        self.logger.info("PHASE 4: Essential Package Installation")

        try:
            venv_python = pathlib.Path(self.config['venv_path']) / 'Scripts' / 'python.exe'

            # Install essential packages
            for package in self.config['required_packages']:
                self.logger.info(f"Installing package: {package}")
                try:
                    self.run_command([
                        str(venv_python), '-m', 'pip', 'install',
                        '--upgrade', package
                    ])
                except Exception as e:
                    self.warnings.append(f"Failed to install {package}: {str(e)}")

            # Verify critical packages
            critical_packages = ['pip', 'setuptools', 'wheel']
            for package in critical_packages:
                try:
                    result = self.run_command([
                        str(venv_python), '-m', 'pip', 'show', package
                    ])
                    self.logger.info(f"Verified package: {package}")
                except:
                    self.warnings.append(f"Critical package not found: {package}")

            # Generate requirements.txt
            try:
                requirements_path = pathlib.Path(self.config['scripts_path']) / 'requirements.txt'
                result = self.run_command([
                    str(venv_python), '-m', 'pip', 'freeze'
                ])

                with open(requirements_path, 'w') as f:
                    f.write(result.stdout)

                self.logger.info(f"Generated requirements.txt: {requirements_path}")
            except:
                self.warnings.append("Failed to generate requirements.txt")

            self.phase_status['package_installation'] = 'completed'

        except Exception as e:
            self.logger.error(f"Package installation failed: {str(e)}")
            self.phase_status['package_installation'] = 'failed'
            raise

    def phase_vscode_setup(self):
        """
        Phase 5: VS Code Python extension setup and configuration

        Teaching note (Day 30 - Development environment): Configuring VS Code
        for optimal Python development experience.
        """
        self.logger.info("PHASE 5: VS Code Setup and Configuration")

        try:
            # Check if VS Code is available
            try:
                self.run_command(['code', '--version'])
                vscode_available = True
            except:
                self.warnings.append("VS Code not found in PATH - manual setup required")
                vscode_available = False

            if vscode_available:
                # Install essential extensions
                for extension in self.config['vscode_extensions']:
                    self.logger.info(f"Installing VS Code extension: {extension}")
                    try:
                        self.run_command(['code', '--install-extension', extension])
                    except:
                        self.warnings.append(f"Failed to install extension: {extension}")

                # Configure Python interpreter
                vscode_settings_dir = pathlib.Path(os.path.expanduser('~/AppData/Roaming/Code/User'))
                vscode_settings_dir.mkdir(parents=True, exist_ok=True)

                settings_file = vscode_settings_dir / 'settings.json'

                # Create or update VS Code settings
                venv_python_path = str(pathlib.Path(self.config['venv_path']) / 'Scripts' / 'python.exe').replace('\\', '/')

                vscode_settings = {
                    "python.defaultInterpreterPath": venv_python_path,
                    "python.terminal.activateEnvironment": True,
                    "python.linting.enabled": True,
                    "python.linting.pylintEnabled": True,
                    "python.formatting.provider": "black",
                    "python.analysis.autoImportCompletions": True,
                    "python.analysis.typeCheckingMode": "basic"
                }

                # Merge with existing settings if they exist
                if settings_file.exists():
                    try:
                        with open(settings_file, 'r') as f:
                            existing_settings = json.load(f)
                        existing_settings.update(vscode_settings)
                        vscode_settings = existing_settings
                    except:
                        self.warnings.append("Could not read existing VS Code settings")

                # Write settings
                with open(settings_file, 'w') as f:
                    json.dump(vscode_settings, f, indent=4)

                self.logger.info(f"Updated VS Code settings: {settings_file}")

            self.phase_status['vscode_setup'] = 'completed'

        except Exception as e:
            self.logger.error(f"VS Code setup failed: {str(e)}")
            self.phase_status['vscode_setup'] = 'failed'
            # Don't raise - this is not critical for core functionality

    def phase_github_integration(self):
        """
        Phase 6: GitHub CLI and Copilot integration

        Teaching note (Day 30 - Development tools): Setting up version control
        and AI-assisted development tools.
        """
        self.logger.info("PHASE 6: GitHub Integration Setup")

        try:
            # Check GitHub CLI
            try:
                result = self.run_command(['gh', '--version'])
                self.logger.info(f"GitHub CLI available: {result.stdout.strip()}")

                # Check authentication status
                try:
                    self.run_command(['gh', 'auth', 'status'])
                    self.logger.info("GitHub CLI authenticated")
                except:
                    self.warnings.append("GitHub CLI not authenticated - run 'gh auth login'")

            except:
                self.warnings.append("GitHub CLI not found - install from https://cli.github.com/")

            # Verify Copilot if VS Code is available
            try:
                self.run_command(['code', '--version'])
                # Check if Copilot extension is installed
                result = self.run_command(['code', '--list-extensions'], check=False)
                if 'github.copilot' in result.stdout:
                    self.logger.info("GitHub Copilot extension detected")
                else:
                    self.warnings.append("GitHub Copilot extension not found")
            except:
                pass

            self.phase_status['github_integration'] = 'completed'

        except Exception as e:
            self.logger.error(f"GitHub integration failed: {str(e)}")
            self.phase_status['github_integration'] = 'failed'
            # Don't raise - this is not critical for core functionality

    def phase_verification(self):
        """
        Phase 7: Comprehensive environment verification

        Teaching note (Day 30 - Testing): Verifying that all components
        are working together correctly.
        """
        self.logger.info("PHASE 7: Environment Verification")

        try:
            venv_python = pathlib.Path(self.config['venv_path']) / 'Scripts' / 'python.exe'

            # Test Python import capabilities
            test_imports = [
                'sys', 'os', 'pathlib', 'json', 'subprocess',
                'requests', 'numpy', 'pandas'
            ]

            for module in test_imports:
                try:
                    self.run_command([
                        str(venv_python), '-c', f'import {module}; print(f"{module} OK")'
                    ])
                except:
                    self.warnings.append(f"Failed to import {module}")

            # Test script execution
            test_script = f'''
import sys
import pathlib
print(f"Python version: {{sys.version}}")
print(f"Python executable: {{sys.executable}}")
print(f"Current directory: {{pathlib.Path.cwd()}}")
print("Environment verification successful")
'''

            try:
                result = self.run_command([str(venv_python), '-c', test_script])
                self.logger.info("Script execution test passed")
                self.logger.debug(f"Test output: {result.stdout}")
            except:
                self.warnings.append("Script execution test failed")

            self.phase_status['verification'] = 'completed'

        except Exception as e:
            self.logger.error(f"Verification failed: {str(e)}")
            self.phase_status['verification'] = 'failed'
            raise

    def phase_optimization(self):
        """
        Phase 8: Performance optimization and final configuration

        Teaching note (Day 30 - Optimization): Final tweaks for optimal
        development environment performance.
        """
        self.logger.info("PHASE 8: Environment Optimization")

        try:
            # Create useful batch files
            scripts_dir = pathlib.Path(self.config['scripts_path'])

            # Activation batch file
            activate_bat = scripts_dir / 'activate_env.bat'
            with open(activate_bat, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'call "{self.config["venv_path"]}\\Scripts\\activate.bat"\n')
                f.write(f'echo EQ12 Python environment activated\n')
                f.write(f'python --version\n')

            # Quick test script
            test_py = scripts_dir / 'test_environment.py'
            with open(test_py, 'w') as f:
                f.write('#!/usr/bin/env python3\n')
                f.write('"""\nEQ12 Environment Test Script\n"""\n\n')
                f.write('import sys\nimport pathlib\n\n')
                f.write('def main():\n')
                f.write('    print("EQ12 Python Environment Test")\n')
                f.write('    print(f"Python: {sys.version}")\n')
                f.write('    print(f"Executable: {sys.executable}")\n')
                f.write('    print("Environment is ready!")\n\n')
                f.write('if __name__ == "__main__":\n')
                f.write('    main()\n')

            # Set environment variables for current session
            os.environ['EQ12_PYTHON'] = str(pathlib.Path(self.config['venv_path']) / 'Scripts' / 'python.exe')
            os.environ['EQ12_VENV'] = self.config['venv_path']

            self.logger.info("Environment optimization completed")
            self.phase_status['optimization'] = 'completed'

        except Exception as e:
            self.logger.error(f"Optimization failed: {str(e)}")
            self.phase_status['optimization'] = 'failed'
            # Don't raise - this is not critical

    def generate_bootstrap_report(self):
        """Generate comprehensive bootstrap report"""
        timestamp = datetime.now().isoformat()

        report = {
            'timestamp': timestamp,
            'system_info': self.system_info,
            'configuration': self.config,
            'phase_status': self.phase_status,
            'errors': self.errors,
            'warnings': self.warnings,
            'summary': {
                'total_phases': len(self.phases),
                'completed_phases': len([p for p in self.phase_status.values() if p == 'completed']),
                'failed_phases': len([p for p in self.phase_status.values() if p == 'failed']),
                'total_errors': len(self.errors),
                'total_warnings': len(self.warnings)
            }
        }

        # Save report
        log_dir = pathlib.Path(self.config['logs_path'])
        report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = log_dir / f"eq12_bootstrap_report_{report_timestamp}.json"

        try:
            with open(report_path, 'w', encoding='ascii', errors='replace') as f:
                json.dump(report, f, indent=2, ensure_ascii=True)

            self.logger.info(f"Bootstrap report saved: {report_path}")

        except Exception as e:
            self.logger.error(f"Failed to save report: {str(e)}")

        return report

    def run_bootstrap(self):
        """
        Execute complete bootstrap process

        Teaching note (Day 11 - Functions): Main orchestration function that
        runs all bootstrap phases in sequence with error handling.
        """
        self.logger.info("Starting EQ12 Expert System Bootstrap")

        try:
            # Run all bootstrap phases
            for phase_name in self.phases:
                phase_method = getattr(self, f'phase_{phase_name}')

                try:
                    self.logger.info(f"Starting phase: {phase_name}")
                    phase_method()
                    self.logger.info(f"Phase completed: {phase_name}")

                except Exception as e:
                    self.logger.error(f"Phase failed: {phase_name} - {str(e)}")

                    # Stop on critical phase failure
                    if phase_name in ['system_check', 'python_validation', 'venv_creation']:
                        self.logger.error("Critical phase failed - stopping bootstrap")
                        break

            # Generate final report
            report = self.generate_bootstrap_report()

            # Print summary
            self.logger.info("=== Bootstrap Summary ===")
            self.logger.info(f"Completed phases: {report['summary']['completed_phases']}/{report['summary']['total_phases']}")
            self.logger.info(f"Errors: {report['summary']['total_errors']}")
            self.logger.info(f"Warnings: {report['summary']['total_warnings']}")

            if self.errors:
                self.logger.error("Bootstrap completed with errors:")
                for error in self.errors:
                    self.logger.error(f"  - {error}")

            if self.warnings:
                self.logger.warning("Bootstrap warnings:")
                for warning in self.warnings:
                    self.logger.warning(f"  - {warning}")

            # Success criteria
            critical_phases = ['system_check', 'python_validation', 'venv_creation']
            critical_success = all(self.phase_status[phase] == 'completed' for phase in critical_phases)

            if critical_success:
                self.logger.info("=== EQ12 Bootstrap Successful ===")
                self.logger.info("Your development environment is ready!")
                return True
            else:
                self.logger.error("=== EQ12 Bootstrap Failed ===")
                self.logger.error("Critical components failed to initialize")
                return False

        except Exception as e:
            self.logger.error(f"Bootstrap failed with unexpected error: {str(e)}")
            return False

def main():
    """
    Main entry point for bootstrap script

    Teaching note (Day 11 - Functions): Clean entry point with argument
    handling and error management.
    """
    import argparse

    parser = argparse.ArgumentParser(description='EQ12 Expert System Bootstrap')
    parser.add_argument('--force', action='store_true', help='Force reinstall of existing components')
    parser.add_argument('--quiet', action='store_true', help='Reduce output verbosity')

    args = parser.parse_args()

    try:
        bootstrap = EQ12SystemBootstrap(
            force_reinstall=args.force,
            verbose=not args.quiet
        )

        success = bootstrap.run_bootstrap()

        if success:
            print("\n✅ EQ12 bootstrap completed successfully!")
            print("🚀 Your development environment is ready for use.")
            sys.exit(0)
        else:
            print("\n❌ EQ12 bootstrap failed.")
            print("📋 Check the logs for detailed error information.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nBootstrap cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
