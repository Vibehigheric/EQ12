#!/usr/bin/env python3
"""
EQ12 GitHub CLI Installer - Professional Development Environment Setup
Automated installation and configuration of GitHub CLI for EQ12 stack
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EQ12GitHubCLIInstaller:
    """
    Professional GitHub CLI installer for EQ12 automation stack

    Features:
    - Silent MSI installation with error handling
    - Automatic token authentication setup
    - Integration with EQ12 credential management
    - Cross-platform compatibility preparation
    - Verification and testing of installation
    """

    def __init__(self, eq12_root: str = "C:/EQ12"):
        """
        Initialize GitHub CLI installer

        Args:
            eq12_root: EQ12 root directory path
        """
        self.eq12_root = Path(eq12_root)
        self.downloads_dir = Path.home() / "Downloads"
        self.tokens_dir = self.eq12_root / "tokens"
        self.logs_dir = self.eq12_root / "logs"

        # Ensure directories exist
        self.tokens_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        # GitHub CLI installer details
        self.gh_installer = "gh_2.81.0_windows_amd64.msi"
        self.installer_path = self.downloads_dir / self.gh_installer

        logger.info("EQ12 GitHub CLI Installer initialized")

    def check_prerequisites(self) -> dict[str, bool]:
        """
        Check installation prerequisites

        Returns:
            Dictionary of prerequisite check results
        """
        checks = {}

        # Check if installer exists
        checks["installer_exists"] = self.installer_path.exists()
        logger.info(f"Installer exists: {checks['installer_exists']} ({self.installer_path})")

        # Check if already installed
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True, timeout=10)
            checks["already_installed"] = result.returncode == 0
            if checks["already_installed"]:
                logger.info(f"GitHub CLI already installed: {result.stdout.strip()}")
        except (subprocess.SubprocessError, FileNotFoundError):
            checks["already_installed"] = False

        # Check admin privileges (needed for MSI install)
        try:
            import ctypes

            checks["is_admin"] = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            checks["is_admin"] = False

        logger.info(f"Admin privileges: {checks['is_admin']}")

        # Check EQ12 directory structure
        checks["eq12_structure"] = all(
            [self.eq12_root.exists(), self.tokens_dir.exists(), self.logs_dir.exists()]
        )

        return checks

    def install_github_cli(self, silent: bool = True) -> tuple[bool, str]:
        """
        Install GitHub CLI using MSI installer

        Args:
            silent: Install silently without GUI

        Returns:
            Tuple of (success, message)
        """
        try:
            # Prepare installation command
            if silent:
                cmd = [
                    "msiexec.exe",
                    "/i",
                    str(self.installer_path),
                    "/qn",  # Quiet mode - no UI
                    "/norestart",  # Don't restart automatically
                ]
            else:
                cmd = ["msiexec.exe", "/i", str(self.installer_path)]

            logger.info(f"Installing GitHub CLI: {' '.join(cmd)}")

            # Run installation
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Check result
            if result.returncode == 0:
                logger.info("GitHub CLI installation completed successfully")

                # Verify installation
                verification_result = subprocess.run(
                    ["gh", "--version"], capture_output=True, text=True, timeout=10
                )

                if verification_result.returncode == 0:
                    version_info = verification_result.stdout.strip()
                    logger.info(f"Installation verified: {version_info}")
                    return True, f"GitHub CLI installed successfully: {version_info}"
                return False, "Installation completed but verification failed"
            error_msg = f"Installation failed with exit code {result.returncode}"
            if result.stderr:
                error_msg += f": {result.stderr}"
            logger.error(error_msg)
            return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Installation timed out after 5 minutes"
        except Exception as e:
            error_msg = f"Installation error: {e!s}"
            logger.error(error_msg)
            return False, error_msg

    def setup_authentication(self, token_file: str = "github_token.txt") -> tuple[bool, str]:
        """
        Setup GitHub CLI authentication using token

        Args:
            token_file: Token file name in tokens directory

        Returns:
            Tuple of (success, message)
        """
        try:
            token_path = self.tokens_dir / token_file

            if not token_path.exists():
                return False, f"GitHub token file not found: {token_path}"

            # Read token
            with open(token_path) as f:
                token = f.read().strip()

            if not token:
                return False, "GitHub token file is empty"

            logger.info("Configuring GitHub CLI authentication...")

            # Login with token (stdin method)
            login_process = subprocess.Popen(
                ["gh", "auth", "login", "--with-token"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            _stdout, stderr = login_process.communicate(input=token)

            if login_process.returncode == 0:
                logger.info("GitHub CLI authentication successful")

                # Verify authentication
                auth_check = subprocess.run(
                    ["gh", "auth", "status"], capture_output=True, text=True
                )

                if auth_check.returncode == 0:
                    return True, "GitHub CLI authenticated successfully"
                return False, "Authentication completed but verification failed"
            error_msg = f"Authentication failed: {stderr}"
            logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"Authentication error: {e!s}"
            logger.error(error_msg)
            return False, error_msg

    def configure_git_settings(self) -> tuple[bool, str]:
        """
        Configure global Git settings for EQ12 stack

        Returns:
            Tuple of (success, message)
        """
        try:
            # Standard EQ12 Git configuration
            git_configs = [
                ("user.name", "EQ12-Automation"),
                ("user.email", "eq12@automation.local"),
                ("init.defaultBranch", "main"),
                ("core.autocrlf", "true"),  # Windows line endings
                ("push.default", "simple"),
                ("pull.rebase", "false"),
            ]

            for key, value in git_configs:
                result = subprocess.run(
                    ["git", "config", "--global", key, value],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    return False, f"Failed to set {key}: {result.stderr}"

                logger.info(f"Git config set: {key} = {value}")

            return True, "Git settings configured successfully"

        except Exception as e:
            error_msg = f"Git configuration error: {e!s}"
            logger.error(error_msg)
            return False, error_msg

    def test_github_integration(self) -> dict[str, bool]:
        """
        Test GitHub CLI integration and functionality

        Returns:
            Dictionary of test results
        """
        tests = {}

        try:
            # Test 1: Basic CLI functionality
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True, timeout=10)
            tests["cli_version"] = result.returncode == 0

            # Test 2: Authentication status
            result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True, timeout=10
            )
            tests["auth_status"] = result.returncode == 0

            # Test 3: API connectivity
            result = subprocess.run(
                ["gh", "api", "user"], capture_output=True, text=True, timeout=15
            )
            tests["api_connectivity"] = result.returncode == 0

            # Test 4: Repository access
            result = subprocess.run(
                ["gh", "repo", "list", "--limit", "1"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            tests["repo_access"] = result.returncode == 0

        except Exception as e:
            logger.error(f"Testing error: {e}")
            # Set all tests to False on error
            for test in [
                "cli_version",
                "auth_status",
                "api_connectivity",
                "repo_access",
            ]:
                tests.setdefault(test, False)

        return tests

    def generate_installation_report(
        self,
        installation_success: bool,
        auth_success: bool,
        git_config_success: bool,
        test_results: dict[str, bool],
    ) -> dict:
        """
        Generate comprehensive installation report

        Returns:
            Installation report dictionary
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "installer_version": self.gh_installer,
            "eq12_root": str(self.eq12_root),
            "installation": {
                "success": installation_success,
                "method": "MSI Silent Install",
            },
            "authentication": {"success": auth_success, "method": "Token-based"},
            "git_configuration": {"success": git_config_success},
            "functionality_tests": test_results,
            "overall_success": all(
                [
                    installation_success,
                    auth_success,
                    git_config_success,
                    all(test_results.values()),
                ]
            ),
        }

        return report

    def save_installation_log(self, report: dict) -> None:
        """
        Save installation report to logs

        Args:
            report: Installation report dictionary
        """
        log_file = (
            self.logs_dir / f"github_cli_install_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            with open(log_file, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"Installation log saved: {log_file}")

        except Exception as e:
            logger.error(f"Failed to save installation log: {e}")

    def run_complete_installation(self) -> dict:
        """
        Run complete GitHub CLI installation and setup process

        Returns:
            Complete installation report
        """
        logger.info("🚀 Starting EQ12 GitHub CLI Installation Process")
        logger.info("=" * 60)

        # Check prerequisites
        prereqs = self.check_prerequisites()
        logger.info(f"Prerequisites check: {prereqs}")

        if not prereqs["installer_exists"]:
            return {
                "error": f"Installer not found: {self.installer_path}",
                "prerequisites": prereqs,
            }

        if prereqs["already_installed"]:
            logger.info("GitHub CLI already installed, skipping installation...")
            install_success = True
        else:
            if not prereqs["is_admin"]:
                logger.warning("Not running as administrator - installation may fail")

            # Install GitHub CLI
            install_success, install_msg = self.install_github_cli(silent=True)
            logger.info(f"Installation result: {install_msg}")

        # Setup authentication
        auth_success, auth_msg = self.setup_authentication()
        logger.info(f"Authentication result: {auth_msg}")

        # Configure Git settings
        git_success, git_msg = self.configure_git_settings()
        logger.info(f"Git configuration result: {git_msg}")

        # Test functionality
        test_results = self.test_github_integration()
        logger.info(f"Functionality tests: {test_results}")

        # Generate report
        report = self.generate_installation_report(
            install_success, auth_success, git_success, test_results
        )

        # Save log
        self.save_installation_log(report)

        # Summary
        if report["overall_success"]:
            logger.info("✅ GitHub CLI installation and setup completed successfully!")
        else:
            logger.warning("⚠️  GitHub CLI installation completed with issues")

        return report


def main():
    """Main installation function with CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 GitHub CLI Installer")
    parser.add_argument("--eq12-root", default="C:/EQ12", help="EQ12 root directory")
    parser.add_argument("--token-file", default="github_token.txt", help="GitHub token file name")
    parser.add_argument("--gui", action="store_true", help="Show GUI during installation")
    parser.add_argument("--test-only", action="store_true", help="Only run functionality tests")

    args = parser.parse_args()

    # Initialize installer
    installer = EQ12GitHubCLIInstaller(eq12_root=args.eq12_root)

    if args.test_only:
        # Run tests only
        tests = installer.test_github_integration()
        print("\n🧪 GitHub CLI Functionality Tests:")
        for test_name, result in tests.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")

        overall = all(tests.values())
        print(f"\nOverall: {'✅ ALL TESTS PASSED' if overall else '❌ SOME TESTS FAILED'}")

        sys.exit(0 if overall else 1)

    # Run complete installation
    report = installer.run_complete_installation()

    # Print summary
    print("\n🎯 EQ12 GitHub CLI Installation Summary")
    print("=" * 50)
    print(f"Overall Success: {'✅ YES' if report.get('overall_success') else '❌ NO'}")

    if "error" in report:
        print(f"Error: {report['error']}")
        sys.exit(1)

    print(f"Installation: {'✅' if report['installation']['success'] else '❌'}")
    print(f"Authentication: {'✅' if report['authentication']['success'] else '❌'}")
    print(f"Git Config: {'✅' if report['git_configuration']['success'] else '❌'}")

    print("\nFunctionality Tests:")
    for test_name, result in report["functionality_tests"].items():
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")

    print(f"\nInstallation completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    sys.exit(0 if report["overall_success"] else 1)


if __name__ == "__main__":
    main()
