#!/usr/bin/env python3
"""
EQ12 GitLeaks Protection and Secret Remediation System
Advanced secret detection, history cleanup, and automated environment variable migration
Author: EQ12 Platform
Version: 2.0.0
"""

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


class EQ12GitLeaksGuardian:
    def __init__(self, workspace_path: str | None = None):
        self.workspace = Path(workspace_path or os.getcwd())
        self.log_dir = Path("C:/EQ12/logs")
        self.backup_dir = Path("C:/EQ12/backups")
        self.config_dir = Path("C:/EQ12/configs")

        # Ensure directories exist
        for directory in [self.log_dir, self.backup_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.setup_logging()

        # Secret patterns for detection and remediation
        self.secret_patterns = {
            "aws_access_key": r"AKIA[0-9A-Z]{16}",
            "aws_secret_key": r"[A-Za-z0-9/+=]{40}",
            "openai_key": r"sk-[A-Za-z0-9]{48}",
            "github_token": r"gh[pousr]_[A-Za-z0-9]{36}",
            "slack_token": r"xox[baprs]-[A-Za-z0-9-]+",
            "discord_token": r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}",
            "telegram_token": r"\d{8,10}:[A-Za-z0-9_-]{35}",
            "generic_api_key": r'[Aa]pi[_-]?[Kk]ey["\']?\s*[:=]\s*["\'][A-Za-z0-9_-]{20,}["\']',
        }

        # Environment variable mappings
        self.env_mappings = {
            "aws_access_key": "AWS_ACCESS_KEY_ID",
            "aws_secret_key": "AWS_SECRET_ACCESS_KEY",
            "openai_key": "OPENAI_API_KEY",
            "github_token": "GITHUB_TOKEN",
            "slack_token": "SLACK_BOT_TOKEN",
            "discord_token": "DISCORD_BOT_TOKEN",
            "telegram_token": "TELEGRAM_BOT_TOKEN",
            "generic_api_key": "API_KEY",
        }

    def setup_logging(self):
        """Initialize comprehensive logging system"""
        log_file = (
            self.log_dir /
            f"gitleaks_guardian_{
                datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.log")

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"🛡️ EQ12 GitLeaks Guardian initialized - Workspace: {self.workspace}")

    def check_prerequisites(self) -> bool:
        """Verify required tools are installed"""
        self.logger.info("🔍 Checking prerequisites...")

        required_tools = ["git", "gitleaks"]
        missing_tools = []

        for tool in required_tools:
            if not shutil.which(tool):
                missing_tools.append(tool)

        if missing_tools:
            self.logger.error(f"❌ Missing required tools: {', '.join(missing_tools)}")
            self.logger.error(
                "Install GitLeaks: https://github.com/zricethezav/gitleaks")
            return False

        self.logger.info("✅ All prerequisites satisfied")
        return True

    def run_gitleaks_scan(self) -> tuple[bool, dict | None]:
        """Execute GitLeaks scan and return results"""
        self.logger.info("🔍 Running GitLeaks security scan...")

        report_file = (
            self.log_dir /
            f"gitleaks_report_{
                datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json")

        try:
            cmd = [
                "gitleaks",
                "detect",
                "--source",
                str(self.workspace),
                "--report-format",
                "json",
                "--report-path",
                str(report_file),
                "--exit-code",
                "1",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.workspace)

            if result.returncode == 0:
                self.logger.info("✅ No secrets detected by GitLeaks")
                return True, None

            # Parse GitLeaks report
            if report_file.exists():
                with open(report_file) as f:
                    report_data = json.load(f)

                self.logger.warning(
                    f"🚨 GitLeaks found {
                        len(report_data)} potential secrets")
                return False, report_data

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ GitLeaks scan failed: {e}")
        except Exception as e:
            self.logger.error(f"❌ Error during GitLeaks scan: {e}")

        return False, None

    def create_backup(self) -> Path:
        """Create timestamped backup of workspace before remediation"""
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"workspace_backup_{timestamp}"

        self.logger.info(f"💾 Creating backup: {backup_path}")

        try:
            # Copy workspace excluding large/unnecessary directories
            def ignore_patterns(directory, files):
                return {
                    f
                    for f in files
                    if f
                    in {
                        "node_modules",
                        ".git",
                        "__pycache__",
                        ".pytest_cache",
                        "bin",
                        "obj",
                        ".vs",
                        ".vscode",
                        "dist",
                        "build",
                    }
                }

            shutil.copytree(self.workspace, backup_path, ignore=ignore_patterns)
            self.logger.info("✅ Backup created successfully")
            return backup_path

        except Exception as e:
            self.logger.error(f"❌ Backup creation failed: {e}")
            raise

    def remediate_secrets(self, report_data: dict) -> dict[str, int]:
        """Automatically remediate detected secrets"""
        self.logger.info("🛠️ Starting automated secret remediation...")

        remediation_stats = {
            "files_processed": 0,
            "secrets_removed": 0,
            "env_vars_created": 0,
            "errors": 0,
        }

        # Group findings by file
        files_to_process = {}
        for finding in report_data:
            file_path = finding.get("File", "")
            if file_path not in files_to_process:
                files_to_process[file_path] = []
            files_to_process[file_path].append(finding)

        env_vars = {}

        for file_path, findings in files_to_process.items():
            try:
                self.logger.info(f"📝 Processing file: {file_path}")
                full_path = self.workspace / file_path

                if not full_path.exists():
                    self.logger.warning(f"⚠️ File not found: {file_path}")
                    continue

                # Read file content
                with open(full_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                original_content = content

                # Process each finding in the file
                for finding in findings:
                    secret_value = finding.get("Secret", "")
                    rule_id = finding.get("RuleID", "generic")

                    if secret_value in content:
                        # Determine appropriate environment variable name
                        env_var_name = self._get_env_var_name(rule_id, finding)

                        # Replace secret with environment variable reference
                        replacement = self._get_replacement_pattern(
                            file_path, env_var_name)
                        content = content.replace(f'"{secret_value}"', replacement)
                        content = content.replace(f"'{secret_value}'", replacement)
                        content = content.replace(secret_value, replacement)

                        # Store env var for .env file
                        env_vars[env_var_name] = secret_value
                        remediation_stats["secrets_removed"] += 1

                        self.logger.info(f"🔧 Replaced secret with {env_var_name}")

                # Write updated content if changes were made
                if content != original_content:
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    remediation_stats["files_processed"] += 1

            except Exception as e:
                self.logger.error(f"❌ Error processing {file_path}: {e}")
                remediation_stats["errors"] += 1

        # Create .env file with extracted secrets
        if env_vars:
            self._create_env_file(env_vars)
            remediation_stats["env_vars_created"] = len(env_vars)

        return remediation_stats

    def _get_env_var_name(self, rule_id: str, finding: dict) -> str:
        """Generate appropriate environment variable name"""
        file_path = finding.get("File", "")

        # Map common rule IDs to env var names
        rule_mappings = {
            "aws-access-token": "AWS_ACCESS_KEY_ID",
            "aws-secret-access-key": "AWS_SECRET_ACCESS_KEY",
            "openai-api-key": "OPENAI_API_KEY",
            "github-pat": "GITHUB_TOKEN",
            "slack-bot-token": "SLACK_BOT_TOKEN",
            "discord-bot-token": "DISCORD_BOT_TOKEN",
            "telegram-bot-api-token": "TELEGRAM_BOT_TOKEN",
        }

        if rule_id in rule_mappings:
            return rule_mappings[rule_id]

        # Generate based on file context
        if "openai" in file_path.lower() or "gpt" in file_path.lower():
            return "OPENAI_API_KEY"
        elif "aws" in file_path.lower():
            return "AWS_ACCESS_KEY_ID"
        elif "github" in file_path.lower():
            return "GITHUB_TOKEN"
        elif "telegram" in file_path.lower():
            return "TELEGRAM_BOT_TOKEN"
        else:
            return "API_KEY"

    def _get_replacement_pattern(self, file_path: str, env_var_name: str) -> str:
        """Generate appropriate replacement code for environment variable"""
        extension = Path(file_path).suffix.lower()

        if extension in [".py"]:
            return f'os.getenv("{env_var_name}")'
        elif extension in [".js", ".ts"]:
            return f"process.env.{env_var_name}"
        elif extension in [".ps1"]:
            return f"$env:{env_var_name}"
        elif extension in [".cs"]:
            return f'Environment.GetEnvironmentVariable("{env_var_name}")'
        else:
            return f"${env_var_name}"

    def _create_env_file(self, env_vars: dict[str, str]):
        """Create .env file with extracted secrets"""
        env_file = self.workspace / ".env"
        gitignore_file = self.workspace / ".gitignore"

        self.logger.info(f"📋 Creating .env file with {len(env_vars)} variables")

        # Create .env file
        with open(env_file, "w") as f:
            f.write("# EQ12 Environment Variables - Generated by GitLeaks Guardian\n")
            f.write(f"# Generated: {datetime.now(UTC).isoformat()}\n")
            f.write("# NEVER COMMIT THIS FILE TO VERSION CONTROL\n\n")

            for var_name, var_value in env_vars.items():
                f.write(f"{var_name}={var_value}\n")

        # Update .gitignore
        gitignore_content = ""
        if gitignore_file.exists():
            with open(gitignore_file) as f:
                gitignore_content = f.read()

        env_patterns = [".env", "*.env", ".env.*"]
        patterns_to_add = []

        for pattern in env_patterns:
            if pattern not in gitignore_content:
                patterns_to_add.append(pattern)

        if patterns_to_add:
            with open(gitignore_file, "a") as f:
                f.write("\n# Environment variables (added by EQ12 GitLeaks Guardian)\n")
                for pattern in patterns_to_add:
                    f.write(f"{pattern}\n")

            self.logger.info("✅ Updated .gitignore to exclude environment files")

    def clean_git_history(self) -> bool:
        """Remove secrets from Git history using git filter-repo"""
        self.logger.info("🧹 Cleaning secrets from Git history...")

        try:
            # Check if git filter-repo is available
            if shutil.which("git-filter-repo"):
                cmd = [
                    "git",
                    "filter-repo",
                    "--invert-paths",
                    "--path",
                    ".env",
                    "--force",
                ]
                subprocess.run(cmd, cwd=self.workspace, check=True)
                self.logger.info("✅ Git history cleaned using git filter-repo")
            else:
                # Fallback to filter-branch (deprecated but widely available)
                self.logger.warning(
                    "⚠️ git-filter-repo not found, using filter-branch (deprecated)")

                # Remove .env from history
                cmd = [
                    "git",
                    "filter-branch",
                    "--force",
                    "--index-filter",
                    "git rm --cached --ignore-unmatch .env",
                    "--prune-empty",
                    "--tag-name-filter",
                    "cat",
                    "--",
                    "--all",
                ]
                subprocess.run(cmd, cwd=self.workspace, check=True)

                # Clean up
                cleanup_cmds = [
                    ["rm", "-r", ".git/refs/original/"],
                    ["git", "reflog", "expire", "--expire=now", "--all"],
                    ["git", "gc", "--prune=now", "--aggressive"],
                ]

                for cmd in cleanup_cmds:
                    subprocess.run(cmd, cwd=self.workspace, check=False)

                self.logger.info("✅ Git history cleaned using filter-branch")

            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Git history cleanup failed: {e}")
            return False

    def generate_copilot_prompts(self) -> dict[str, str]:
        """Generate expert Copilot prompts for comprehensive code repair"""
        prompts = {
            "secret_scan": """You are an expert security auditor AI. Scan all code files in this workspace for hardcoded credentials, API keys, passwords, tokens, or secrets. For each finding:

1. Replace hardcoded secrets with secure environment variable references (
    os.getenv(),
    process.env.,
    $env:,
    etc.
)
2. Ensure proper .env file structure and .gitignore exclusions
3. Add input validation and error handling for missing environment variables
4. Document security improvements in comments
5. Generate a security audit report listing all changes made

Goal: Zero hardcoded secrets with robust environment variable management.""",
            "script_integrity": """You are an expert code quality AI. Scan all script files (
                .py,
                .js,
                .ps1,
                .sh
            ) for syntax errors, missing imports, deprecated functions, and logic issues:

1. Fix all syntax errors and missing imports automatically
2. Update deprecated functions to modern alternatives
3. Add proper error handling and input validation
4. Ensure consistent coding standards and formatting
5. Add type hints where applicable (Python, TypeScript)
6. Generate comprehensive documentation for complex functions

Goal: Production-ready, maintainable scripts with zero linting errors.""",
            "context_validation": """You are an expert async/threading AI. Scan for invalid context access, thread safety issues, and async problems:

1. Fix UI thread violations with proper Invoke/Dispatcher calls
2. Ensure proper async/await patterns throughout
3. Add proper object lifetime management and disposal
4. Fix race conditions and thread safety issues
5. Add cancellation token support for long-running operations
6. Validate context access patterns in Entity Framework or similar

Goal: Thread-safe, properly scoped code with no context access violations.""",
            "mapping_resolution": """You are an expert React/JSX AI. Fix nested mapping issues, implicit keys, and unresolved actions:

1. Extract nested maps into separate memoized components
2. Add explicit, stable keys for all JSX lists (key={item.id}, not index)
3. Fix unresolved action references in YAML/JSON configs
4. Optimize context providers to prevent unnecessary re-renders
5. Ensure proper dependency arrays in useEffect/useMemo
6. Validate prop types and component interfaces

Goal: Clean, performant React code with proper key management and context usage.""",
        }

        # Save prompts to file
        prompts_file = self.config_dir / "copilot_expert_prompts.json"
        with open(prompts_file, "w") as f:
            json.dump(prompts, f, indent=2)

        self.logger.info(f"💡 Generated Copilot expert prompts: {prompts_file}")
        return prompts

    def run_comprehensive_scan(self) -> dict:
        """Execute complete security and quality scan"""
        self.logger.info("🚀 Starting comprehensive EQ12 security and quality scan...")

        scan_results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "workspace": str(self.workspace),
            "gitleaks_clean": False,
            "backup_created": False,
            "secrets_remediated": 0,
            "history_cleaned": False,
            "prompts_generated": False,
            "errors": [],
        }

        try:
            # Step 1: Prerequisites check
            if not self.check_prerequisites():
                scan_results["errors"].append("Prerequisites check failed")
                return scan_results

            # Step 2: GitLeaks scan
            gitleaks_clean, report_data = self.run_gitleaks_scan()
            scan_results["gitleaks_clean"] = gitleaks_clean

            if not gitleaks_clean and report_data:
                # Step 3: Create backup
                backup_path = self.create_backup()
                scan_results["backup_created"] = True
                scan_results["backup_path"] = str(backup_path)

                # Step 4: Remediate secrets
                remediation_stats = self.remediate_secrets(report_data)
                scan_results.update(remediation_stats)

                # Step 5: Clean Git history
                if remediation_stats["secrets_removed"] > 0:
                    history_cleaned = self.clean_git_history()
                    scan_results["history_cleaned"] = history_cleaned

            # Step 6: Generate Copilot prompts
            prompts = self.generate_copilot_prompts()
            scan_results["prompts_generated"] = True
            scan_results["copilot_prompts"] = list(prompts.keys())

        except Exception as e:
            self.logger.error(f"❌ Comprehensive scan failed: {e}")
            scan_results["errors"].append(str(e))

        # Save scan results
        results_file = (
            self.log_dir /
            f"comprehensive_scan_{
                datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, "w") as f:
            json.dump(scan_results, f, indent=2)

        self.logger.info(f"📊 Scan results saved: {results_file}")
        return scan_results


def main():
    parser = argparse.ArgumentParser(
        description="EQ12 GitLeaks Protection and Secret Remediation System"
    )
    parser.add_argument(
        "--workspace",
        "-w",
        default=None,
        help="Workspace directory path")
    parser.add_argument(
        "--action",
        "-a",
        choices=["scan", "remediate", "comprehensive"],
        default="comprehensive",
        help="Action to perform",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize guardian
    guardian = EQ12GitLeaksGuardian(args.workspace)

    try:
        if args.action == "scan":
            clean, report = guardian.run_gitleaks_scan()
            if clean:
                print("✅ No secrets detected")
                sys.exit(0)
            else:
                print("🚨 Secrets detected - run with --action remediate to fix")
                sys.exit(1)

        elif args.action == "remediate":
            clean, report = guardian.run_gitleaks_scan()
            if not clean and report:
                guardian.create_backup()
                stats = guardian.remediate_secrets(report)
                print(f"🛠️ Remediation complete: {stats}")

        elif args.action == "comprehensive":
            results = guardian.run_comprehensive_scan()

            if results["errors"]:
                print(f"❌ Scan completed with errors: {results['errors']}")
                sys.exit(1)
            else:
                print("✅ Comprehensive scan completed successfully")
                print(f"🔍 GitLeaks clean: {results['gitleaks_clean']}")
                if results["secrets_remediated"] > 0:
                    print(f"🛠️ Secrets remediated: {results['secrets_remediated']}")
                    print(f"🧹 History cleaned: {results['history_cleaned']}")
                print(f"💡 Copilot prompts generated: {results['prompts_generated']}")

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
