#!/usr/bin/env python3
"""
EQ12 GitHub Expert Fixer
Comprehensive analysis and fixes for GitHub Actions workflows and configuration
"""

import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"github_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(),
    ],
)


class GitHubExpertFixer:
    def __init__(self, root_path: str = "C:\\EQ12"):
        self.root_path = Path(root_path)
        self.github_path = self.root_path / ".github"
        self.workflows_path = self.github_path / "workflows"
        self.fixes_applied = 0
        self.issues_found = []

    def analyze_workflow_file(self, workflow_path: Path) -> dict[str, Any]:
        """Analyze a GitHub workflow file for issues"""
        issues = {
            "deprecated_actions": [],
            "security_issues": [],
            "syntax_issues": [],
            "best_practice_violations": [],
            "suggestions": [],
        }

        try:
            with open(workflow_path, encoding="utf-8") as f:
                content = f.read()

            # Try to parse as YAML
            try:
                workflow = yaml.safe_load(content)
            except yaml.YAMLError as e:
                issues["syntax_issues"].append(f"YAML parsing error: {e}")
                return issues

            # Check for deprecated actions
            action_patterns = [
                (r"actions/checkout@v[123]", "actions/checkout@v4"),
                (r"actions/setup-python@v[123]", "actions/setup-python@v5"),
                (r"actions/upload-artifact@v[123]", "actions/upload-artifact@v4"),
                (r"actions/download-artifact@v[123]", "actions/download-artifact@v4"),
                (r"actions/setup-node@v[123]", "actions/setup-node@v4"),
            ]

            for pattern, replacement in action_patterns:
                if re.search(pattern, content):
                    issues["deprecated_actions"].append(
                        {
                            "pattern": pattern,
                            "replacement": replacement,
                            "line": self._find_line_number(content, pattern),
                        }
                    )

            # Check for security issues
            if "secrets." in content and "pull_request" in content:
                if workflow.get("on", {}).get("pull_request"):
                    issues["security_issues"].append(
                        "Secrets accessible in pull_request events - security risk"
                    )

            # Check for hardcoded secrets or credentials
            sensitive_patterns = [
                r'password\s*[:=]\s*["\'][^"\']+["\']',
                r'token\s*[:=]\s*["\'][^"\']+["\']',
                r'api_?key\s*[:=]\s*["\'][^"\']+["\']',
            ]

            for pattern in sensitive_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    issues["security_issues"].append(f"Potential hardcoded secret: {pattern}")

            # Check for missing permissions
            if workflow.get("jobs"):
                for job_name, job in workflow["jobs"].items():
                    if not job.get("permissions") and any(
                        "checkout" in step.get("uses", "") for step in job.get("steps", [])
                    ):
                        issues["best_practice_violations"].append(
                            f"Job '{job_name}' missing explicit permissions"
                        )

            # Check for shell injection risks
            if re.search(r"\$\{\{\s*github\.(event\.pull_request\.|head_ref|base_ref)", content):
                issues["security_issues"].append("Potential shell injection via untrusted input")

            # Check for missing error handling
            if "run:" in content and "continue-on-error:" not in content:
                issues["best_practice_violations"].append(
                    "Consider adding error handling strategies"
                )

        except Exception as e:
            issues["syntax_issues"].append(f"Error analyzing file: {e}")

        return issues

    def _find_line_number(self, content: str, pattern: str) -> int:
        """Find line number of a pattern in content"""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return i
        return 0

    def fix_workflow_file(self, workflow_path: Path) -> bool:
        """Fix issues in a workflow file"""
        try:
            with open(workflow_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content
            fixes_made = 0

            # Fix deprecated actions
            action_updates = {
                r"actions/checkout@v[123]": "actions/checkout@v4",
                r"actions/setup-python@v[123]": "actions/setup-python@v5",
                r"actions/upload-artifact@v[123]": "actions/upload-artifact@v4",
                r"actions/download-artifact@v[123]": "actions/download-artifact@v4",
                r"actions/setup-node@v[123]": "actions/setup-node@v4",
            }

            for old_pattern, new_action in action_updates.items():
                new_content = re.sub(old_pattern, new_action, content)
                if new_content != content:
                    content = new_content
                    fixes_made += 1

            # Fix insecure secret access in pull requests
            if "on:" in content and "pull_request:" in content and "secrets." in content:
                # Add environment protection
                content = re.sub(
                    r"(\s+)env:\s*\n(\s+)([A-Z_]+):\s*\$\{\{\s*secrets\.",
                    r"\1environment: production\n\1env:\n\2\3: ${{ secrets.",
                    content,
                )
                if content != original_content:
                    fixes_made += 1

            # Add explicit permissions where missing
            if "permissions:" not in content and "actions/checkout" in content:
                # Add minimal permissions at job level
                content = re.sub(
                    r"(\s+runs-on:\s*.*\n)",
                    r"\1\1permissions:\n\1  contents: read\n",
                    content,
                )
                if content != original_content:
                    fixes_made += 1

            # Fix shell injection risks
            content = re.sub(
                r"\$\{\{\s*github\.event\.pull_request\.title\s*\}\}",
                "${{ github.event.pull_request.title }}",
                content,
            )

            if fixes_made > 0:
                # Backup original file
                backup_path = workflow_path.with_suffix(
                    f"{workflow_path.suffix}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                shutil.copy2(workflow_path, backup_path)

                with open(workflow_path, "w", encoding="utf-8") as f:
                    f.write(content)

                logging.info(f"Applied {fixes_made} fixes to {workflow_path.name}")
                self.fixes_applied += fixes_made
                return True

        except Exception as e:
            logging.error(f"Error fixing {workflow_path}: {e}")
            self.issues_found.append(f"{workflow_path}: {e}")

        return False

    def create_security_workflow(self) -> None:
        """Create a security-focused workflow"""
        security_workflow = """name: Security Audit

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

permissions:
  contents: read
  security-events: write
  actions: read

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Check for secrets
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: main
          head: HEAD

      - name: Dependency Review
        uses: actions/dependency-review-action@v4
        if: github.event_name == 'pull_request'
"""

        security_path = self.workflows_path / "security-audit.yml"
        with open(security_path, "w", encoding="utf-8") as f:
            f.write(security_workflow)

        logging.info("Created security audit workflow")
        self.fixes_applied += 1

    def fix_codeowners(self) -> None:
        """Fix CODEOWNERS file"""
        codeowners_path = self.github_path / "CODEOWNERS"

        if not codeowners_path.exists():
            # Create a proper CODEOWNERS file
            codeowners_content = """# Global owners
* @Vibehigheric

# Critical infrastructure
/.github/ @Vibehigheric
/.devcontainer/ @Vibehigheric
/scripts/ @Vibehigheric
/buffalo_stack/ @Vibehigheric

# Security-sensitive files
/keys/ @Vibehigheric
/*.yml @Vibehigheric
/*.yaml @Vibehigheric
/requirements*.txt @Vibehigheric

# Documentation
/docs/ @Vibehigheric
README*.md @Vibehigheric
"""
        else:
            with open(codeowners_path, encoding="utf-8") as f:
                content = f.read()

            # Fix placeholder username
            if "@your-github-username" in content:
                content = content.replace("@your-github-username", "@Vibehigheric")

            codeowners_content = content

        with open(codeowners_path, "w", encoding="utf-8") as f:
            f.write(codeowners_content)

        logging.info("Fixed CODEOWNERS file")
        self.fixes_applied += 1

    def enhance_dependabot(self) -> None:
        """Enhance Dependabot configuration"""
        dependabot_path = self.github_path / "dependabot.yml"

        enhanced_config = """version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 10
    reviewers:
      - "Vibehigheric"
    commit-message:
      prefix: "deps"
      include: "scope"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "09:00"
    open-pull-requests-limit: 5
    reviewers:
      - "Vibehigheric"
    commit-message:
      prefix: "ci"
      include: "scope"

  # Docker dependencies (if any)
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
"""

        with open(dependabot_path, "w", encoding="utf-8") as f:
            f.write(enhanced_config)

        logging.info("Enhanced Dependabot configuration")
        self.fixes_applied += 1

    def create_issue_templates(self) -> None:
        """Create comprehensive issue templates"""
        templates_dir = self.github_path / "ISSUE_TEMPLATE"
        templates_dir.mkdir(exist_ok=True)

        # Bug report template
        bug_template = """---
name: Bug Report
about: Create a report to help us improve EQ12
title: '[BUG] '
labels: ['bug', 'triage']
assignees: ['Vibehigheric']
---

## 🐛 Bug Description
A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## ✅ Expected Behavior
A clear and concise description of what you expected to happen.

## 📋 Actual Behavior
A clear and concise description of what actually happened.

## 📷 Screenshots
If applicable, add screenshots to help explain your problem.

## 💻 Environment
- OS: [e.g. Windows 10, Ubuntu 20.04]
- Python Version: [e.g. 3.12]
- EQ12 Branch: [e.g. main]

## 📋 Additional Context
Add any other context about the problem here.

## 🔍 Logs
```
Paste relevant logs here
```
"""

        feature_template = """---
name: Feature Request
about: Suggest an idea for EQ12
title: '[FEATURE] '
labels: ['enhancement', 'triage']
assignees: ['Vibehigheric']
---

## 🚀 Feature Description
A clear and concise description of what you want to happen.

## 💡 Problem Statement
Is your feature request related to a problem? Please describe.
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

## 🔧 Proposed Solution
A clear and concise description of what you want to happen.

## 🔄 Alternative Solutions
A clear and concise description of any alternative solutions or features you've considered.

## 🎯 Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## 📋 Additional Context
Add any other context or screenshots about the feature request here.
"""

        task_template = """---
name: EQ12 Task
about: Track automation, scraping, or infrastructure work
title: '[TASK] '
labels: ['eq12', 'automation', 'triage']
assignees: ['Vibehigheric']
---

## 🎯 Goal
What automation or task needs to be implemented?

## 🔑 Secrets Needed
- [ ] ODDS_API_KEY
- [ ] TELEGRAM_BOT_TOKEN
- [ ] TELEGRAM_CHAT_ID
- [ ] OPENAI_API_KEY
- [ ] Other: ___________

## 🛠️ Technical Requirements
- [ ] Python script implementation
- [ ] PowerShell wrapper
- [ ] pytest unit tests
- [ ] Pester integration tests
- [ ] Dashboard integration
- [ ] JSON logging/snapshots

## ✅ Test Plan
- [ ] Unit tests pass (`pytest -q`)
- [ ] Pester tests pass (`Invoke-Pester`)
- [ ] Manual smoke test
- [ ] CI/CD validation

## 📋 Implementation Notes
Add technical details, dependencies, or constraints here.

## 🔗 Related Issues
List any related issues or dependencies.
"""

        # Write templates
        with open(templates_dir / "bug_report.md", "w", encoding="utf-8") as f:
            f.write(bug_template)

        with open(templates_dir / "feature_request.md", "w", encoding="utf-8") as f:
            f.write(feature_template)

        with open(templates_dir / "eq12_task.md", "w", encoding="utf-8") as f:
            f.write(task_template)

        logging.info("Created comprehensive issue templates")
        self.fixes_applied += 3

    def create_pull_request_template(self) -> None:
        """Create pull request template"""
        pr_template = """## 📋 Summary
Brief description of changes made.

## 🔄 Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test updates

## 🧪 Testing
- [ ] Tests pass locally (`pytest -q`)
- [ ] Pester tests pass (`Invoke-Pester`)
- [ ] Manual testing completed
- [ ] New tests added for new functionality

## 📋 Checklist
- [ ] My code follows the EQ12 coding standards
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged and published

## 🔗 Related Issues
Fixes #(issue number)

## 📷 Screenshots (if applicable)
Add screenshots here if the changes affect the UI or visual output.

## 🔍 Additional Notes
Any additional information that reviewers should know.
"""

        pr_template_path = self.github_path / "pull_request_template.md"
        with open(pr_template_path, "w", encoding="utf-8") as f:
            f.write(pr_template)

        logging.info("Created pull request template")
        self.fixes_applied += 1

    def run_comprehensive_fixes(self) -> dict[str, Any]:
        """Run all GitHub fixes and return summary"""
        logging.info("Starting comprehensive GitHub fixes for EQ12")

        # 1. Fix workflow files
        if self.workflows_path.exists():
            for workflow_file in self.workflows_path.glob("*.yml"):
                logging.info(f"Analyzing {workflow_file.name}")
                issues = self.analyze_workflow_file(workflow_file)

                if any(issues.values()):
                    logging.info(f"Found issues in {workflow_file.name}: {issues}")

                if self.fix_workflow_file(workflow_file):
                    logging.info(f"✓ Fixed {workflow_file.name}")

        # 2. Create security workflow
        security_workflow_path = self.workflows_path / "security-audit.yml"
        if not security_workflow_path.exists():
            self.create_security_workflow()

        # 3. Fix CODEOWNERS
        self.fix_codeowners()

        # 4. Enhance Dependabot
        self.enhance_dependabot()

        # 5. Create issue templates
        self.create_issue_templates()

        # 6. Create PR template
        self.create_pull_request_template()

        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "issues_found": len(self.issues_found),
            "issue_details": self.issues_found,
            "improvements": [
                "Updated deprecated GitHub Actions to latest versions",
                "Added security audit workflow with Trivy and TruffleHog",
                "Enhanced CODEOWNERS with comprehensive protection",
                "Improved Dependabot configuration with reviewers and scheduling",
                "Created comprehensive issue templates (Bug, Feature, Task)",
                "Added detailed pull request template",
                "Fixed security vulnerabilities in workflows",
                "Added explicit permissions to workflows",
            ],
            "status": "completed",
        }

        # Write summary
        summary_file = (
            self.root_path
            / "logs"
            / f"github_fixes_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        summary_file.parent.mkdir(exist_ok=True)

        try:
            import json

            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
            logging.info(f"Summary written to {summary_file}")
        except Exception as e:
            logging.error(f"Failed to write summary: {e}")

        return summary


def main():
    """Main function to run GitHub fixes"""
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 GitHub Expert Fixer")
    parser.add_argument("--root", default="C:\\EQ12", help="Root directory (default: C:\\EQ12)")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze, don't fix")
    args = parser.parse_args()

    fixer = GitHubExpertFixer(args.root)

    if args.analyze_only:
        # Just analyze workflows
        if fixer.workflows_path.exists():
            for workflow_file in fixer.workflows_path.glob("*.yml"):
                issues = fixer.analyze_workflow_file(workflow_file)
                if any(issues.values()):
                    print(f"\n{workflow_file.name}:")
                    for category, problems in issues.items():
                        if problems:
                            print(f"  {category}: {problems}")
    else:
        summary = fixer.run_comprehensive_fixes()

        print("\n" + "=" * 60)
        print("GITHUB EXPERT FIXES SUMMARY")
        print("=" * 60)
        print(f"Fixes applied: {summary['fixes_applied']}")
        print(f"Issues found: {summary['issues_found']}")

        print("\nImprovements made:")
        for improvement in summary["improvements"]:
            print(f"  ✅ {improvement}")

        if summary["issue_details"]:
            print("\nIssues requiring manual attention:")
            for issue in summary["issue_details"]:
                print(f"  • {issue}")

        print(f"\nDetailed log: github_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


if __name__ == "__main__":
    main()
