#!/usr/bin/env python3
"""
EQ12 Clean Python Workspace Builder
Rebuilds optimal Python development environment with proper isolation and configuration

This script provides comprehensive Python workspace management:
- Creates isolated virtual environment with latest packages
- Configures optimal Pylance and VS Code settings
- Excludes heavy folders that cause memory issues
- Sets up proper import paths and analysis configuration
- Validates Python environment stability
- Generates workspace health reports

Author: EQ12 Engineering Team
Version: 1.0.0
Requires: Python 3.9+, pip, venv module
"""

import sys
import os
import json
import logging
import argparse
import subprocess
import shutil
import venv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import platform

# Initialize logging
logger = logging.getLogger(__name__)

class EQ12WorkspaceBuilder:
    """Professional Python workspace builder with comprehensive environment management."""

    def __init__(self, workspace_root: str, python_version: str = None):
        """Initialize workspace builder with validation and setup.

        Args:
            workspace_root: Root directory for EQ12 workspace
            python_version: Target Python version (default: current version)
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.python_version = python_version or f"{sys.version_info.major}.{sys.version_info.minor}"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Core paths
        self.venv_path = self.workspace_root / ".venv"
        self.vscode_path = self.workspace_root / ".vscode"
        self.logs_path = self.workspace_root / "logs"
        self.scripts_path = self.workspace_root / "scripts"

        # Results tracking
        self.build_results = {
            "timestamp": datetime.now().isoformat(),
            "workspace_root": str(self.workspace_root),
            "python_version": self.python_version,
            "success": False,
            "environment_created": False,
            "packages_installed": False,
            "settings_configured": False,
            "validation_passed": False,
            "errors": [],
            "warnings": [],
            "package_list": [],
            "excluded_paths": [],
            "interpreter_path": None
        }

        # Essential EQ12 packages
        self.core_packages = [
            "requests>=2.31.0",
            "beautifulsoup4>=4.12.0",
            "lxml>=4.9.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "python-dotenv>=1.0.0",
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0"
        ]

        # Heavy folders to exclude (prevent Pylance overload)
        self.exclusion_patterns = [
            "**/envs/**",
            "**/.venv_new/**",
            "**/node_modules/**",
            "**/__pycache__/**",
            "**/.pytest_cache/**",
            "**/data/**",
            "**/datasets/**",
            "**/.git/**",
            "**/logs/**",
            "**/cache/**",
            "**/.mypy_cache/**"
        ]

        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure comprehensive logging for workspace operations."""
        self.logs_path.mkdir(exist_ok=True)

        log_file = self.logs_path / f"workspace_build_{self.timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        logger.info(f"EQ12 Workspace Builder initialized - Log: {log_file}")

    def _log_error(self, message: str, exception: Exception = None) -> None:
        """Log error and add to results tracking."""
        error_msg = f"{message}"
        if exception:
            error_msg += f" - {str(exception)}"

        logger.error(error_msg)
        self.build_results["errors"].append(error_msg)

    def _log_warning(self, message: str) -> None:
        """Log warning and add to results tracking."""
        logger.warning(message)
        self.build_results["warnings"].append(message)

    def validate_prerequisites(self) -> bool:
        """Validate system prerequisites for workspace building."""
        logger.info("Validating prerequisites...")

        try:
            # Check Python version
            if sys.version_info < (3, 9):
                self._log_error("Python 3.9+ required for optimal Pylance performance")
                return False

            # Check workspace directory
            if not self.workspace_root.exists():
                self._log_error(f"Workspace root not found: {self.workspace_root}")
                return False

            # Check venv module availability
            try:
                import venv
                logger.info("venv module available")
            except ImportError:
                self._log_error("Python venv module not available")
                return False

            # Check pip availability
            pip_result = subprocess.run([sys.executable, "-m", "pip", "--version"],
                                      capture_output=True, text=True)
            if pip_result.returncode != 0:
                self._log_error("pip module not available")
                return False

            logger.info("Prerequisites validation passed")
            return True

        except Exception as e:
            self._log_error("Prerequisites validation failed", e)
            return False

    def remove_corrupt_environments(self) -> bool:
        """Remove corrupt or conflicting virtual environments."""
        logger.info("Removing corrupt virtual environments...")

        try:
            corrupt_paths = [
                self.workspace_root / ".venv_new",
                self.workspace_root / "envs",
                self.workspace_root / "venv"
            ]

            for corrupt_path in corrupt_paths:
                if corrupt_path.exists():
                    logger.warning(f"Removing corrupt environment: {corrupt_path}")
                    shutil.rmtree(corrupt_path, ignore_errors=True)

            # Also remove existing .venv if it exists to ensure clean rebuild
            if self.venv_path.exists():
                logger.info("Removing existing .venv for clean rebuild")
                shutil.rmtree(self.venv_path, ignore_errors=True)

            logger.info("Corrupt environments removed successfully")
            return True

        except Exception as e:
            self._log_error("Failed to remove corrupt environments", e)
            return False

    def create_virtual_environment(self) -> bool:
        """Create clean virtual environment with optimal configuration."""
        logger.info("Creating clean virtual environment...")

        try:
            # Create venv using Python's built-in venv module
            venv.create(self.venv_path, with_pip=True, clear=True)

            # Verify creation
            if platform.system() == "Windows":
                python_exe = self.venv_path / "Scripts" / "python.exe"
                pip_exe = self.venv_path / "Scripts" / "pip.exe"
            else:
                python_exe = self.venv_path / "bin" / "python"
                pip_exe = self.venv_path / "bin" / "pip"

            if not python_exe.exists():
                self._log_error(f"Python executable not found: {python_exe}")
                return False

            # Test virtual environment
            test_result = subprocess.run([str(python_exe), "--version"],
                                       capture_output=True, text=True)
            if test_result.returncode == 0:
                logger.info(f"Virtual environment created: {test_result.stdout.strip()}")
                self.build_results["interpreter_path"] = str(python_exe)
                self.build_results["environment_created"] = True
                return True
            else:
                self._log_error("Virtual environment validation failed")
                return False

        except Exception as e:
            self._log_error("Failed to create virtual environment", e)
            return False

    def install_packages(self) -> bool:
        """Install essential EQ12 packages with version pinning."""
        logger.info("Installing essential packages...")

        try:
            # Get pip executable
            if platform.system() == "Windows":
                pip_exe = self.venv_path / "Scripts" / "pip.exe"
            else:
                pip_exe = self.venv_path / "bin" / "pip"

            if not pip_exe.exists():
                self._log_error(f"Pip executable not found: {pip_exe}")
                return False

            # Upgrade pip first
            upgrade_result = subprocess.run([str(pip_exe), "install", "--upgrade", "pip"],
                                          capture_output=True, text=True)
            if upgrade_result.returncode != 0:
                self._log_warning("Failed to upgrade pip")

            # Install core packages
            successful_packages = []
            failed_packages = []

            for package in self.core_packages:
                logger.info(f"Installing {package}...")
                install_result = subprocess.run([str(pip_exe), "install", package],
                                              capture_output=True, text=True)
                if install_result.returncode == 0:
                    successful_packages.append(package)
                    logger.info(f"Successfully installed {package}")
                else:
                    failed_packages.append(package)
                    self._log_error(f"Failed to install {package}: {install_result.stderr}")

            # Generate installed package list
            list_result = subprocess.run([str(pip_exe), "list", "--format=json"],
                                       capture_output=True, text=True)
            if list_result.returncode == 0:
                try:
                    package_list = json.loads(list_result.stdout)
                    self.build_results["package_list"] = package_list
                except json.JSONDecodeError:
                    self._log_warning("Could not parse package list")

            self.build_results["packages_installed"] = len(failed_packages) == 0

            if failed_packages:
                self._log_error(f"Some packages failed to install: {failed_packages}")
                return False
            else:
                logger.info(f"All packages installed successfully: {len(successful_packages)}")
                return True

        except Exception as e:
            self._log_error("Package installation failed", e)
            return False

    def configure_vscode_settings(self) -> bool:
        """Configure optimal VS Code settings for EQ12 development."""
        logger.info("Configuring VS Code settings...")

        try:
            self.vscode_path.mkdir(exist_ok=True)

            # Determine correct Python executable path
            if platform.system() == "Windows":
                python_path = str(self.venv_path / "Scripts" / "python.exe").replace("\\", "\\\\")
            else:
                python_path = str(self.venv_path / "bin" / "python")

            # Optimal settings for EQ12 with Pylance performance tuning
            settings = {
                # Python configuration
                "python.defaultInterpreterPath": python_path,
                "python.venvPath": str(self.workspace_root),
                "python.venvFolders": [".venv"],
                "python.terminal.activateEnvironment": True,

                # Pylance performance optimization
                "python.analysis.typeCheckingMode": "basic",
                "python.analysis.autoSearchPaths": True,
                "python.analysis.autoImportCompletions": True,
                "python.analysis.diagnosticMode": "workspace",
                "python.analysis.indexing": True,
                "python.analysis.packageIndexDepths": [
                    {"name": "sklearn", "depth": 2},
                    {"name": "pandas", "depth": 2},
                    {"name": "numpy", "depth": 1}
                ],

                # File exclusions (prevent Pylance overload)
                "files.exclude": {
                    "**/envs": True,
                    "**/.venv_new": True,
                    "**/node_modules": True,
                    "**/__pycache__": True,
                    "**/.pytest_cache": True,
                    "**/data": True,
                    "**/.git": True,
                    "**/logs": True,
                    "**/.mypy_cache": True
                },

                # Python analysis exclusions
                "python.analysis.exclude": [
                    "**/envs/**",
                    "**/.venv_new/**",
                    "**/data/**",
                    "**/logs/**",
                    "**/node_modules/**",
                    "**/__pycache__/**"
                ],

                # Search exclusions
                "search.exclude": {
                    "**/envs": True,
                    "**/.venv_new": True,
                    "**/data": True,
                    "**/logs": True,
                    "**/__pycache__": True,
                    "**/.pytest_cache": True
                },

                # File watching exclusions (performance)
                "files.watcherExclude": {
                    "**/envs/**": True,
                    "**/.venv_new/**": True,
                    "**/data/**": True,
                    "**/logs/**": True,
                    "**/__pycache__/**": True,
                    "**/.git/**": True
                },

                # Testing configuration
                "python.testing.pytestEnabled": True,
                "python.testing.unittestEnabled": False,
                "python.testing.pytestArgs": [
                    "tests"
                ],

                # Formatting and linting
                "python.formatting.provider": "black",
                "python.linting.enabled": True,
                "python.linting.flake8Enabled": True,
                "python.linting.mypyEnabled": True,
                "python.linting.lintOnSave": True,

                # Editor settings
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": True
                },

                # Terminal settings
                "terminal.integrated.defaultProfile.windows": "PowerShell",
                "terminal.integrated.profiles.windows": {
                    "PowerShell": {
                        "source": "PowerShell",
                        "icon": "terminal-powershell"
                    }
                }
            }

            # Save settings
            settings_file = self.vscode_path / "settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info(f"VS Code settings configured: {settings_file}")
            self.build_results["excluded_paths"] = list(settings["files.exclude"].keys())
            self.build_results["settings_configured"] = True

            # Create launch configuration for debugging
            self._create_launch_config()

            return True

        except Exception as e:
            self._log_error("VS Code settings configuration failed", e)
            return False

    def _create_launch_config(self) -> None:
        """Create debugging launch configuration."""
        try:
            launch_config = {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Python: Current File",
                        "type": "python",
                        "request": "launch",
                        "program": "${file}",
                        "console": "integratedTerminal",
                        "python": "${workspaceFolder}/.venv/Scripts/python.exe" if platform.system() == "Windows" else "${workspaceFolder}/.venv/bin/python",
                        "cwd": "${workspaceFolder}",
                        "env": {
                            "PYTHONPATH": "${workspaceFolder}/scripts"
                        }
                    },
                    {
                        "name": "Python: EQ12 Script",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/scripts/${input:scriptName}",
                        "console": "integratedTerminal",
                        "python": "${workspaceFolder}/.venv/Scripts/python.exe" if platform.system() == "Windows" else "${workspaceFolder}/.venv/bin/python",
                        "cwd": "${workspaceFolder}",
                        "env": {
                            "PYTHONPATH": "${workspaceFolder}/scripts"
                        }
                    }
                ],
                "inputs": [
                    {
                        "id": "scriptName",
                        "description": "EQ12 script to run",
                        "default": "eq12_master.py",
                        "type": "promptString"
                    }
                ]
            }

            launch_file = self.vscode_path / "launch.json"
            with open(launch_file, 'w', encoding='utf-8') as f:
                json.dump(launch_config, f, indent=2)

            logger.info("Launch configuration created")

        except Exception as e:
            self._log_warning(f"Failed to create launch configuration: {e}")

    def validate_workspace(self) -> bool:
        """Comprehensive workspace validation."""
        logger.info("Validating workspace configuration...")

        try:
            validation_results = {
                "venv_exists": False,
                "python_executable": False,
                "packages_available": False,
                "settings_valid": False,
                "imports_working": False
            }

            # Check virtual environment
            if self.venv_path.exists():
                validation_results["venv_exists"] = True
                logger.info("✓ Virtual environment exists")
            else:
                self._log_error("✗ Virtual environment missing")

            # Check Python executable
            if platform.system() == "Windows":
                python_exe = self.venv_path / "Scripts" / "python.exe"
            else:
                python_exe = self.venv_path / "bin" / "python"

            if python_exe.exists():
                validation_results["python_executable"] = True
                logger.info("✓ Python executable available")
            else:
                self._log_error("✗ Python executable missing")

            # Test package imports
            test_imports = ["requests", "beautifulsoup4", "pandas", "pytest"]
            import_test_script = f"""
import sys
sys.path.insert(0, '{self.scripts_path}')

failed_imports = []
for pkg in {test_imports}:
    try:
        __import__(pkg)
        print(f'✓ {{pkg}}')
    except ImportError:
        failed_imports.append(pkg)
        print(f'✗ {{pkg}}')

if failed_imports:
    print(f'Failed imports: {{failed_imports}}')
    sys.exit(1)
else:
    print('All packages available')
    sys.exit(0)
"""

            import_result = subprocess.run([str(python_exe), "-c", import_test_script],
                                         capture_output=True, text=True)
            if import_result.returncode == 0:
                validation_results["packages_available"] = True
                logger.info("✓ All packages available")
            else:
                self._log_error(f"✗ Package import failed: {import_result.stderr}")

            # Check VS Code settings
            settings_file = self.vscode_path / "settings.json"
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    if "python.defaultInterpreterPath" in settings:
                        validation_results["settings_valid"] = True
                        logger.info("✓ VS Code settings valid")
                except Exception as e:
                    self._log_error(f"✗ Invalid VS Code settings: {e}")
            else:
                self._log_error("✗ VS Code settings missing")

            # Test basic script execution
            test_script = """
print('EQ12 workspace test successful')
import sys
import os
print(f'Python: {sys.version}')
print(f'Working directory: {os.getcwd()}')
"""

            exec_result = subprocess.run([str(python_exe), "-c", test_script],
                                       capture_output=True, text=True,
                                       cwd=str(self.workspace_root))
            if exec_result.returncode == 0:
                validation_results["imports_working"] = True
                logger.info("✓ Script execution working")
            else:
                self._log_error(f"✗ Script execution failed: {exec_result.stderr}")

            # Calculate overall success
            success_count = sum(validation_results.values())
            total_checks = len(validation_results)
            success_rate = success_count / total_checks

            self.build_results["validation_passed"] = success_rate >= 0.8

            if success_rate >= 0.8:
                logger.info(f"✓ Workspace validation PASSED ({success_count}/{total_checks})")
                return True
            else:
                self._log_error(f"✗ Workspace validation FAILED ({success_count}/{total_checks})")
                return False

        except Exception as e:
            self._log_error("Workspace validation failed", e)
            return False

    def generate_health_report(self) -> str:
        """Generate comprehensive workspace health report."""
        logger.info("Generating workspace health report...")

        try:
            report_file = self.logs_path / f"workspace_health_{self.timestamp}.json"

            # Add system information
            self.build_results["system_info"] = {
                "platform": platform.system(),
                "python_version": sys.version,
                "workspace_size": self._get_workspace_size(),
                "venv_size": self._get_venv_size()
            }

            # Save detailed report
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.build_results, f, indent=2, ensure_ascii=False)

            logger.info(f"Health report saved: {report_file}")
            return str(report_file)

        except Exception as e:
            self._log_error("Failed to generate health report", e)
            return ""

    def _get_workspace_size(self) -> str:
        """Calculate workspace directory size."""
        try:
            total_size = sum(f.stat().st_size for f in self.workspace_root.rglob('*') if f.is_file())
            return f"{total_size / (1024*1024):.1f} MB"
        except:
            return "Unknown"

    def _get_venv_size(self) -> str:
        """Calculate virtual environment size."""
        try:
            if self.venv_path.exists():
                total_size = sum(f.stat().st_size for f in self.venv_path.rglob('*') if f.is_file())
                return f"{total_size / (1024*1024):.1f} MB"
            return "0 MB"
        except:
            return "Unknown"

    def build_workspace(self) -> bool:
        """Execute complete workspace building process."""
        logger.info("=== Starting EQ12 Workspace Build ===")

        try:
            # Step 1: Prerequisites validation
            if not self.validate_prerequisites():
                self._log_error("Prerequisites validation failed")
                return False

            # Step 2: Remove corrupt environments
            if not self.remove_corrupt_environments():
                self._log_error("Failed to remove corrupt environments")
                return False

            # Step 3: Create virtual environment
            if not self.create_virtual_environment():
                self._log_error("Failed to create virtual environment")
                return False

            # Step 4: Install packages
            if not self.install_packages():
                self._log_error("Failed to install packages")
                return False

            # Step 5: Configure VS Code
            if not self.configure_vscode_settings():
                self._log_error("Failed to configure VS Code settings")
                return False

            # Step 6: Validate workspace
            if not self.validate_workspace():
                self._log_error("Workspace validation failed")
                return False

            # Step 7: Generate health report
            report_file = self.generate_health_report()

            self.build_results["success"] = True
            logger.info("=== EQ12 Workspace Build COMPLETED SUCCESSFULLY ===")

            if report_file:
                logger.info(f"Health report: {report_file}")

            return True

        except Exception as e:
            self._log_error("Workspace build failed", e)
            return False


def main():
    """Main entry point for EQ12 workspace builder."""
    parser = argparse.ArgumentParser(
        description="EQ12 Clean Python Workspace Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python eq12_clean_workspace_builder.py --workspace C:\\EQ12 --rebuild
  python eq12_clean_workspace_builder.py --validate --python-version 3.12
  python eq12_clean_workspace_builder.py --emergency-repair
        """
    )

    parser.add_argument(
        "--workspace", "-w",
        default=os.getcwd(),
        help="EQ12 workspace root directory (default: current directory)"
    )

    parser.add_argument(
        "--python-version", "-p",
        help="Target Python version (default: current version)"
    )

    parser.add_argument(
        "--rebuild", "-r",
        action="store_true",
        help="Force complete rebuild of workspace"
    )

    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Only validate existing workspace"
    )

    parser.add_argument(
        "--emergency-repair", "-e",
        action="store_true",
        help="Emergency repair for corrupted workspace"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize workspace builder
        builder = EQ12WorkspaceBuilder(
            workspace_root=args.workspace,
            python_version=args.python_version
        )

        if args.validate:
            # Validation only mode
            logger.info("Running workspace validation...")
            success = builder.validate_workspace()
            builder.generate_health_report()

        elif args.emergency_repair:
            # Emergency repair mode
            logger.info("Running emergency workspace repair...")
            builder.remove_corrupt_environments()
            success = builder.build_workspace()

        else:
            # Full workspace build
            logger.info("Running full workspace build...")
            success = builder.build_workspace()

        if success:
            logger.info("EQ12 workspace operation completed successfully")
            sys.exit(0)
        else:
            logger.error("EQ12 workspace operation failed")
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Workspace build interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
