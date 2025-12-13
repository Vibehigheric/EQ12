#!/usr/bin/env python3
"""
EQ12 Devcontainer Expert - Comprehensive Development Environment Fixer
Author: Devcontainer Expert System
Date: September 27, 2025
Purpose: Analyze and fix all devcontainer configuration issues across EQ12 project

This expert system provides comprehensive devcontainer analysis, security auditing,
performance optimization, and automated setup for development environments.
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("devcontainer_fixes.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class DevcontainerIssue:
    """Represents a devcontainer configuration issue"""

    file_path: str
    issue_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    fix_applied: bool = False
    fix_description: str = ""


@dataclass
class DevcontainerStats:
    """Statistics about devcontainer analysis"""

    total_configs: int = 0
    issues_found: int = 0
    fixes_applied: int = 0
    security_improvements: int = 0
    performance_optimizations: int = 0


class DevcontainerExpertFixer:
    """Expert-level devcontainer configuration analysis and fixing system"""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.issues: list[DevcontainerIssue] = []
        self.stats = DevcontainerStats()
        self.fixes_summary = []

        # Standard devcontainer configurations
        self.standard_python_version = "3.12"
        self.recommended_features = {
            "ghcr.io/devcontainers/features/powershell:1": {},
            "ghcr.io/devcontainers/features/github-cli:1": {},
            "ghcr.io/devcontainers/features/git:1": {},
            "ghcr.io/devcontainers/features/gpg:1": {},
            "ghcr.io/devcontainers/features/playwright:1": {},
        }

    def analyze_devcontainer_configs(self) -> list[Path]:
        """Find and analyze all devcontainer configurations"""
        logger.info("🔍 Analyzing devcontainer configurations...")

        devcontainer_files = []
        for pattern in ["**/.devcontainer/devcontainer.json", "**/devcontainer.json"]:
            devcontainer_files.extend(self.repo_root.glob(pattern))

        self.stats.total_configs = len(devcontainer_files)
        logger.info(f"Found {self.stats.total_configs} devcontainer configurations")

        for config_file in devcontainer_files:
            self._analyze_single_config(config_file)

        return devcontainer_files

    def _analyze_single_config(self, config_file: Path) -> None:
        """Analyze a single devcontainer.json file"""
        try:
            with open(config_file, encoding="utf-8") as f:
                content = f.read()

            # Remove JSON comments for parsing
            clean_content = self._remove_json_comments(content)
            config = json.loads(clean_content)

            # Security analysis
            self._check_security_issues(config_file, config)

            # Performance analysis
            self._check_performance_issues(config_file, config)

            # Configuration completeness
            self._check_configuration_completeness(config_file, config)

            # Post-create script analysis
            self._analyze_post_create_scripts(config_file, config)

        except json.JSONDecodeError as e:
            self._add_issue(config_file, "json_syntax", "critical", f"Invalid JSON syntax: {e}")
        except Exception as e:
            self._add_issue(config_file, "analysis_error", "high", f"Analysis failed: {e}")

    def _remove_json_comments(self, content: str) -> str:
        """Remove JSON comments for proper parsing"""
        # Remove // comments
        content = re.sub(r"//.*", "", content)
        # Remove /* */ comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        # Remove _comment properties
        content = re.sub(r'"_comment"\s*:\s*"[^"]*",?\s*', "", content)
        return content

    def _check_security_issues(self, config_file: Path, config: dict) -> None:
        """Check for security vulnerabilities in devcontainer config"""

        # Check for privileged containers
        if config.get("runArgs", []):
            run_args = config["runArgs"]
            if "--privileged" in run_args:
                self._add_issue(
                    config_file,
                    "security_privileged",
                    "critical",
                    "Privileged container detected - security risk",
                )

        # Check for unsafe mounts
        mounts = config.get("mounts", [])
        for mount in mounts:
            if "type=bind" in mount and "/var/run/docker.sock" in mount:
                self._add_issue(
                    config_file,
                    "security_docker_socket",
                    "high",
                    "Docker socket mount detected - potential security risk",
                )

        # Check for missing user restrictions
        if not config.get("remoteUser"):
            self._add_issue(
                config_file,
                "security_no_user",
                "medium",
                "No remoteUser specified - should use 'vscode' for security",
            )

        # Check for unsafe environment variables
        container_env = config.get("containerEnv", {})
        remote_env = config.get("remoteEnv", {})

        for env_dict, env_type in [
            (container_env, "containerEnv"),
            (remote_env, "remoteEnv"),
        ]:
            for key, value in env_dict.items():
                if (
                    isinstance(value, str)
                    and ("password" in key.lower() or "secret" in key.lower())
                    and not value.startswith("${")
                ):
                    self._add_issue(
                        config_file,
                        "security_hardcoded_secret",
                        "critical",
                        f"Hardcoded secret in {env_type}: {key}",
                    )

    def _check_performance_issues(self, config_file: Path, config: dict) -> None:
        """Check for performance optimization opportunities"""

        # Check Python version consistency
        image = config.get("image", "")
        if "python:" in image:
            version_match = re.search(r"python:(\d+\.\d+)", image)
            if version_match:
                version = version_match.group(1)
                if version != self.standard_python_version:
                    self._add_issue(
                        config_file,
                        "performance_python_version",
                        "medium",
                        f"Python {version} detected, recommend {self.standard_python_version}",
                    )

        # Check for missing performance features
        features = config.get("features", {})
        missing_features = []
        for feature_name in self.recommended_features:
            if feature_name not in features:
                missing_features.append(feature_name)

        if missing_features:
            self._add_issue(
                config_file,
                "performance_missing_features",
                "low",
                f"Missing recommended features: {', '.join(missing_features)}",
            )

        # Check for inefficient post-create commands
        post_create = config.get("postCreateCommand", "")
        if post_create and "pip install" in post_create and "--upgrade pip" not in post_create:
            self._add_issue(
                config_file,
                "performance_pip_upgrade",
                "low",
                "Post-create should upgrade pip for better performance",
            )

    def _check_configuration_completeness(self, config_file: Path, config: dict) -> None:
        """Check for missing or incomplete configuration elements"""

        # Required fields for EQ12 project
        required_fields = ["name", "image", "workspaceFolder"]
        for field in required_fields:
            if field not in config:
                self._add_issue(
                    config_file,
                    "config_missing_field",
                    "medium",
                    f"Missing required field: {field}",
                )

        # EQ12-specific requirements
        if not config.get("containerEnv", {}).get("EQ12_LOGS"):
            self._add_issue(
                config_file,
                "config_missing_eq12_logs",
                "medium",
                "Missing EQ12_LOGS environment variable",
            )

        # VS Code customizations
        vscode_config = config.get("customizations", {}).get("vscode", {})
        if not vscode_config.get("extensions"):
            self._add_issue(
                config_file,
                "config_missing_extensions",
                "low",
                "No VS Code extensions specified",
            )

        # Git configuration
        vscode_settings = vscode_config.get("settings", {})
        if not vscode_settings.get("git.enableCommitSigning"):
            self._add_issue(
                config_file,
                "config_git_signing",
                "medium",
                "Git commit signing not enabled",
            )

    def _analyze_post_create_scripts(self, config_file: Path, config: dict) -> None:
        """Analyze post-create scripts for issues"""
        post_create = config.get("postCreateCommand", "")
        if not post_create:
            self._add_issue(
                config_file,
                "config_no_postcreate",
                "medium",
                "No postCreateCommand specified",
            )
            return

        # Check if post-create script exists
        config_dir = config_file.parent

        # Extract script path from command
        script_patterns = [
            r"\.devcontainer/(\w+\.ps1)",
            r"\.devcontainer/(\w+\.sh)",
            r"scripts/(\w+\.sh)",
            r"(\w+\.ps1)",
            r"(\w+\.sh)",
        ]

        script_found = False
        for pattern in script_patterns:
            match = re.search(pattern, post_create)
            if match:
                script_name = match.group(1)
                script_path = config_dir / script_name
                if script_path.exists():
                    script_found = True
                    self._analyze_post_create_script_content(script_path)
                    break

        if not script_found and (".ps1" in post_create or ".sh" in post_create):
            self._add_issue(
                config_file,
                "postcreate_script_missing",
                "high",
                "Post-create script referenced but not found",
            )

    def _analyze_post_create_script_content(self, script_path: Path) -> None:
        """Analyze post-create script content"""
        try:
            content = script_path.read_text(encoding="utf-8")

            # Check for error handling
            if script_path.suffix == ".ps1" and "$ErrorActionPreference" not in content:
                self._add_issue(
                    script_path,
                    "postcreate_no_error_handling",
                    "medium",
                    "PowerShell script missing error handling",
                )

            # Check for requirements installation
            if "requirements.txt" in content and "--upgrade pip" not in content:
                self._add_issue(
                    script_path,
                    "postcreate_pip_upgrade",
                    "low",
                    "Should upgrade pip before installing requirements",
                )

        except Exception as e:
            self._add_issue(
                script_path,
                "postcreate_analysis_error",
                "medium",
                f"Failed to analyze script: {e}",
            )

    def fix_devcontainer_issues(self, mode: str = "selective") -> int:
        """Fix identified devcontainer issues"""
        logger.info(f"🔧 Fixing devcontainer issues in {mode} mode...")

        fixes_applied = 0

        for issue in self.issues:
            if issue.severity in ["critical", "high"] or mode == "aggressive":
                if self._apply_fix(issue):
                    fixes_applied += 1

        # Create improved devcontainer templates
        self._create_standard_devcontainer_template()

        # Create comprehensive documentation
        self._create_devcontainer_documentation()

        # Create CI/CD integration
        self._create_devcontainer_ci_integration()

        self.stats.fixes_applied = fixes_applied
        return fixes_applied

    def _apply_fix(self, issue: DevcontainerIssue) -> bool:
        """Apply a specific fix for an issue"""
        try:
            file_path = Path(issue.file_path)

            if issue.issue_type == "json_syntax":
                return self._fix_json_syntax(file_path, issue)
            if issue.issue_type == "security_no_user":
                return self._fix_missing_remote_user(file_path, issue)
            if issue.issue_type == "performance_python_version":
                return self._fix_python_version(file_path, issue)
            if issue.issue_type == "config_missing_eq12_logs":
                return self._fix_missing_eq12_logs(file_path, issue)
            if issue.issue_type == "config_git_signing":
                return self._fix_git_signing(file_path, issue)
            if issue.issue_type == "performance_missing_features":
                return self._fix_missing_features(file_path, issue)
            if issue.issue_type == "config_no_postcreate":
                return self._fix_missing_postcreate(file_path, issue)
            logger.warning(f"No fix implemented for issue type: {issue.issue_type}")
            return False

        except Exception as e:
            logger.error(f"Failed to apply fix for {issue.file_path}: {e}")
            return False

    def _fix_json_syntax(self, file_path: Path, issue: DevcontainerIssue) -> bool:
        """Fix JSON syntax issues by removing comments"""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Remove _comment properties
            fixed_content = re.sub(r'"_comment"\s*:\s*"[^"]*",?\s*\n?', "", content)

            # Validate JSON
            json.loads(self._remove_json_comments(fixed_content))

            file_path.write_text(fixed_content, encoding="utf-8")
            issue.fix_applied = True
            issue.fix_description = "Removed invalid _comment properties"
            logger.info(f"Fixed JSON syntax in {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to fix JSON syntax in {file_path}: {e}")
            return False

    def _fix_missing_remote_user(self, file_path: Path, issue: DevcontainerIssue) -> bool:
        """Add missing remoteUser configuration"""
        try:
            content = file_path.read_text(encoding="utf-8")
            config = json.loads(self._remove_json_comments(content))

            config["remoteUser"] = "vscode"

            # Write back with proper formatting
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            issue.fix_applied = True
            issue.fix_description = "Added remoteUser: vscode"
            logger.info(f"Added remote user to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to add remote user to {file_path}: {e}")
            return False

    def _fix_python_version(self, file_path: Path, issue: DevcontainerIssue) -> bool:
        """Update Python version to recommended version"""
        try:
            content = file_path.read_text(encoding="utf-8")
            config = json.loads(self._remove_json_comments(content))

            current_image = config.get("image", "")
            if "python:" in current_image:
                new_image = re.sub(
                    r"python:\d+\.\d+",
                    f"python:{self.standard_python_version}",
                    current_image,
                )
                config["image"] = new_image

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            issue.fix_applied = True
            issue.fix_description = f"Updated Python version to {self.standard_python_version}"
            logger.info(f"Updated Python version in {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to update Python version in {file_path}: {e}")
            return False

    def _fix_missing_eq12_logs(self, file_path: Path, issue: DevcontainerIssue) -> bool:
        """Add EQ12_LOGS environment variable"""
        try:
            content = file_path.read_text(encoding="utf-8")
            config = json.loads(self._remove_json_comments(content))

            if "containerEnv" not in config:
                config["containerEnv"] = {}

            config["containerEnv"]["EQ12_LOGS"] = "/workspaces/EQ12/logs"

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            issue.fix_applied = True
            issue.fix_description = "Added EQ12_LOGS environment variable"
            logger.info(f"Added EQ12_LOGS to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to add EQ12_LOGS to {file_path}: {e}")
            return False

    def _fix_git_signing(self, file_path: Path, issue: DevcontainerIssue) -> bool:
        """Enable git commit signing in VS Code settings"""
        try:
            content = file_path.read_text(encoding="utf-8")
            config = json.loads(self._remove_json_comments(content))

            if "customizations" not in config:
                config["customizations"] = {}
            if "vscode" not in config["customizations"]:
                config["customizations"]["vscode"] = {}
            if "settings" not in config["customizations"]["vscode"]:
                config["customizations"]["vscode"]["settings"] = {}

            config["customizations"]["vscode"]["settings"]["git.enableCommitSigning"] = True
            config["customizations"]["vscode"]["settings"]["git.ignoreLegacyWarning"] = True

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)

            issue.fix_applied = True
            issue.fix_description = "Enabled git commit signing"
            logger.info(f"Enabled git signing in {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to enable git signing in {file_path}: {e}")
            return False

    def _create_standard_devcontainer_template(self) -> None:
        """Create standardized devcontainer template"""
        template_dir = self.repo_root / ".devcontainer"
        template_dir.mkdir(exist_ok=True)

        # Standard devcontainer.json
        standard_config = {
            "name": "EQ12 Devcontainer",
            "image": f"mcr.microsoft.com/devcontainers/python:{self.standard_python_version}",
            "features": self.recommended_features,
            "containerEnv": {
                "EQ12_LOGS": "/workspaces/EQ12/logs",
                "GNUPGHOME": "/home/vscode/.gnupg",
            },
            "postCreateCommand": "pwsh -NoProfile -ExecutionPolicy Bypass -File .devcontainer/postCreate.ps1",
            "forwardPorts": [5000, 9222, 8000],
            "mounts": [
                "source=/workspaces/EQ12/.vscode-extensions,target=/home/vscode/.vscode-server/extensions,type=bind"
            ],
            "remoteUser": "vscode",
            "customizations": {
                "vscode": {
                    "settings": {
                        "git.enableCommitSigning": True,
                        "git.ignoreLegacyWarning": True,
                        "security.allowedUNCHosts": ["*"],
                        "telemetry.enableTelemetry": False,
                        "python.defaultInterpreterPath": "/usr/local/bin/python",
                        "python.linting.enabled": True,
                        "python.linting.pylintEnabled": True,
                    },
                    "extensions": [
                        "ms-vscode.powershell",
                        "github.copilot",
                        "ms-python.python",
                        "ms-azuretools.vscode-docker",
                        "ms-python.pylint",
                        "ms-python.flake8",
                    ],
                }
            },
            "shutdownAction": "stopContainer",
            "workspaceFolder": "/workspaces/EQ12",
        }

        config_path = template_dir / "devcontainer.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(standard_config, f, indent=2)

        self.fixes_summary.append("Created standardized devcontainer.json template")
        logger.info(f"Created standard devcontainer template at {config_path}")

    def _create_devcontainer_documentation(self) -> None:
        """Create comprehensive devcontainer documentation"""
        docs_content = """# EQ12 Devcontainer Documentation

## Overview
EQ12 uses standardized development containers to ensure consistent development environments across all team members and CI/CD systems.

## Features
- **Python 3.12**: Latest stable Python version
- **PowerShell**: Cross-platform PowerShell for scripting
- **GitHub CLI**: Integrated GitHub operations
- **Git with GPG**: Secure commit signing
- **Playwright**: Browser automation testing
- **VS Code Extensions**: Pre-configured development tools

## Quick Start
1. Open the repository in VS Code
2. When prompted, click "Reopen in Container"
3. Wait for the container to build and post-create scripts to run
4. Start developing with a fully configured environment

## Environment Variables
Set these secrets in your GitHub Codespaces or local environment:
- `ODDS_API_KEY`: API key for sports betting data
- `TELEGRAM_BOT_TOKEN`: Telegram bot token for notifications
- `TELEGRAM_CHAT_ID`: Telegram chat ID for notifications
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `NGROK_AUTHTOKEN`: Ngrok authentication token for tunneling

## Post-Create Setup
The post-create script automatically:
1. Installs Python requirements from `requirements.txt`
2. Downloads Playwright browsers for testing
3. Configures development environment
4. Sets up logging directories
5. Configures ngrok if token provided

## Security Features
- **Non-privileged container**: Runs as `vscode` user for security
- **GPG commit signing**: Enabled by default
- **Secure environment variables**: Uses GitHub secrets
- **Limited permissions**: Minimal required access

## Performance Optimizations
- **Extension caching**: VS Code extensions cached between sessions
- **Python package caching**: Pip cache persisted
- **Optimized base image**: Microsoft's official Python devcontainer
- **Selective port forwarding**: Only necessary ports exposed

## Troubleshooting

### Container Build Issues
```bash
# Rebuild container completely
Ctrl+Shift+P -> "Dev Containers: Rebuild Container"
```

### Post-Create Script Fails
```bash
# Run manually
pwsh -NoProfile -ExecutionPolicy Bypass -File .devcontainer/postCreate.ps1
```

### GPG Signing Issues
```bash
# Import GPG keys manually
gpg --import keys/*.asc
git config --global user.signingkey YOUR_KEY_ID
```

### Permission Issues
```bash
# Fix file permissions
sudo chown -R vscode:vscode /workspaces/EQ12
```

## Customization
Create environment-specific configurations in subdirectories:
- `.devcontainer/` - Main project configuration
- `scraper_starter/.devcontainer/` - Scraper development
- `scaffold/.devcontainer/` - Project scaffolding

## Best Practices
1. **Always use the devcontainer** for consistent environments
2. **Keep secrets in GitHub Codespaces secrets** not in code
3. **Update the template** when adding new tools or requirements
4. **Test changes** in a separate branch before merging
5. **Document modifications** in this file

## CI/CD Integration
The devcontainer configuration is used by:
- GitHub Actions workflows for testing
- Automated dependency management
- Security scanning and compliance checks
- Performance monitoring and optimization

---
*Generated by EQ12 Devcontainer Expert System*
"""

        docs_path = self.repo_root / "docs" / "devcontainer.md"
        docs_path.parent.mkdir(exist_ok=True)
        docs_path.write_text(docs_content, encoding="utf-8")

        self.fixes_summary.append("Created comprehensive devcontainer documentation")
        logger.info(f"Created devcontainer documentation at {docs_path}")

    def _create_devcontainer_ci_integration(self) -> None:
        """Create CI/CD integration for devcontainer management"""
        workflow_content = """name: Devcontainer Validation

on:
  push:
    paths:
      - '.devcontainer/**'
      - '*/.devcontainer/**'
  pull_request:
    paths:
      - '.devcontainer/**'
      - '*/.devcontainer/**'

jobs:
  validate-devcontainer:
    runs-on: ubuntu-latest
    permissions:
      contents: read

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install devcontainer CLI
        run: npm install -g @devcontainers/cli

      - name: Validate devcontainer configurations
        run: |
          for config in $(find . -name "devcontainer.json" -not -path "./node_modules/*"); do
            echo "Validating $config"
            devcontainer build --workspace-folder "$(dirname $config)" --log-level debug
          done

      - name: Test devcontainer build
        run: |
          devcontainer build --workspace-folder .

      - name: Security scan devcontainer
        run: |
          # Check for security issues in devcontainer configs
          python -c "
          import json
          import sys
          from pathlib import Path

          issues = []
          for config_file in Path('.').rglob('devcontainer.json'):
              try:
                  config = json.loads(config_file.read_text())
                  # Check for privileged containers
                  if '--privileged' in str(config.get('runArgs', [])):
                      issues.append(f'{config_file}: Privileged container detected')
                  # Check for docker socket mounts
                  mounts = config.get('mounts', [])
                  for mount in mounts:
                      if 'docker.sock' in mount:
                          issues.append(f'{config_file}: Docker socket mount detected')
              except Exception as e:
                  issues.append(f'{config_file}: Parse error - {e}')

          if issues:
              for issue in issues:
                  print(f'SECURITY ISSUE: {issue}')
              sys.exit(1)
          else:
              print('No security issues found in devcontainer configurations')
          "
"""

        workflow_path = self.repo_root / ".github" / "workflows" / "devcontainer-validation.yml"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        workflow_path.write_text(workflow_content, encoding="utf-8")

        self.fixes_summary.append("Created devcontainer CI/CD validation workflow")
        logger.info(f"Created devcontainer workflow at {workflow_path}")

    def _add_issue(self, file_path: Path, issue_type: str, severity: str, description: str) -> None:
        """Add an issue to the tracking list"""
        issue = DevcontainerIssue(
            file_path=str(file_path),
            issue_type=issue_type,
            severity=severity,
            description=description,
        )
        self.issues.append(issue)
        self.stats.issues_found += 1
        logger.debug(f"Issue found in {file_path}: {description}")

    def generate_summary_report(self) -> str:
        """Generate comprehensive summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create detailed JSON log
        log_data = {
            "timestamp": timestamp,
            "stats": {
                "total_configs": self.stats.total_configs,
                "issues_found": self.stats.issues_found,
                "fixes_applied": self.stats.fixes_applied,
                "security_improvements": self.stats.security_improvements,
                "performance_optimizations": self.stats.performance_optimizations,
            },
            "issues": [
                {
                    "file": issue.file_path,
                    "type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "fixed": issue.fix_applied,
                    "fix_description": issue.fix_description,
                }
                for issue in self.issues
            ],
            "fixes_summary": self.fixes_summary,
        }

        log_path = self.repo_root / "logs" / f"devcontainer_fixes_summary_{timestamp}.json"
        log_path.parent.mkdir(exist_ok=True)

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, indent=2)

        # Generate text summary
        summary = f"""
======================================================================
DEVCONTAINER EXPERT FIXES SUMMARY
======================================================================
Configurations analyzed: {self.stats.total_configs}
Issues found: {self.stats.issues_found}
Fixes applied: {self.stats.fixes_applied}
Security improvements: {self.stats.security_improvements}
Performance optimizations: {self.stats.performance_optimizations}

Issues by severity:
"""

        # Count issues by severity
        severity_counts = {}
        for issue in self.issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            summary += f"  {severity.upper()}: {count} issues\n"

        summary += """
Improvements made:
"""
        for fix in self.fixes_summary:
            summary += f"  ✅ {fix}\n"

        summary += f"""
Detailed log: devcontainer_fixes_summary_{timestamp}.json

🚀 Next steps:
  • Review and test updated devcontainer configurations
  • Validate CI/CD integration works correctly
  • Update team documentation with new procedures
  • Monitor devcontainer performance and security
"""

        return summary


def main():
    parser = argparse.ArgumentParser(description="EQ12 Devcontainer Expert Fixer")
    parser.add_argument(
        "--mode",
        choices=["selective", "aggressive"],
        default="selective",
        help="Fix mode: selective (safe fixes) or aggressive (all fixes)",
    )
    parser.add_argument("--repo-root", default=".", help="Repository root directory")

    args = parser.parse_args()

    try:
        fixer = DevcontainerExpertFixer(args.repo_root)

        # Analysis phase
        logger.info("🔍 Starting devcontainer expert analysis...")
        fixer.analyze_devcontainer_configs()

        # Fixing phase
        logger.info("🔧 Applying devcontainer fixes...")
        fixes_applied = fixer.fix_devcontainer_issues(args.mode)

        # Summary phase
        logger.info("📊 Generating summary report...")
        summary = fixer.generate_summary_report()
        print(summary)

        logger.info(f"✅ Devcontainer expert analysis complete! Applied {fixes_applied} fixes.")

    except Exception as e:
        logger.error(f"❌ Devcontainer expert analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
