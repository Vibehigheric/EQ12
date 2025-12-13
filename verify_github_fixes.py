#!/usr/bin/env python3
"""
GitHub Expert Verification Script - EQ12
Verifies all GitHub-related fixes and improvements are working properly
"""

from pathlib import Path
from typing import Any

import yaml


def verify_github_fixes(root_path: str = "C:\\EQ12") -> dict[str, Any]:
    """Verify all GitHub fixes are working properly"""

    print("🔍 GitHub Expert - Final Verification")
    print("=" * 60)

    root = Path(root_path)
    github_dir = root / ".github"
    workflows_dir = github_dir / "workflows"

    results = {
        "workflows_fixed": 0,
        "security_improvements": 0,
        "templates_created": 0,
        "config_files_enhanced": 0,
        "issues_found": [],
    }

    print("\n📁 Verifying Workflow Files:")

    # Check workflow files for proper permissions and structure
    workflow_files = list(workflows_dir.glob("*.yml")) if workflows_dir.exists() else []

    for workflow_file in workflow_files:
        try:
            with open(workflow_file, encoding="utf-8") as f:
                workflow = yaml.safe_load(f)

            # Check for explicit permissions
            has_permissions = False
            if workflow.get("permissions"):
                has_permissions = True
            elif workflow.get("jobs"):
                for job in workflow["jobs"].values():
                    if job.get("permissions"):
                        has_permissions = True
                        break

            print("  {workflow_file.name}: {status}")

            if has_permissions:
                results["workflows_fixed"] += 1
            else:
                results["issues_found"].append(
                    f"{workflow_file.name}: Missing explicit permissions"
                )

        except Exception as e:
            print("  {workflow_file.name}: ❌ ERROR - {e}")
            results["issues_found"].append(f"{workflow_file.name}: {e}")

    print("\n🔒 Security Features:")

    # Check for security workflow
    security_workflow = workflows_dir / "security-audit.yml"
    if security_workflow.exists():
        print("  ✅ Security audit workflow: CREATED")
        results["security_improvements"] += 1
    else:
        print("  ❌ Security audit workflow: MISSING")
        results["issues_found"].append("Security audit workflow not found")

    # Check CODEOWNERS
    codeowners_file = github_dir / "CODEOWNERS"
    if codeowners_file.exists():
        with open(codeowners_file, encoding="utf-8") as f:
            content = f.read()

        if "@your-github-username" not in content and "@Vibehigheric" in content:
            print("  ✅ CODEOWNERS file: PROPERLY CONFIGURED")
            results["config_files_enhanced"] += 1
        else:
            print("  ⚠️ CODEOWNERS file: NEEDS CONFIGURATION")
            results["issues_found"].append("CODEOWNERS contains placeholder username")
    else:
        print("  ❌ CODEOWNERS file: MISSING")
        results["issues_found"].append("CODEOWNERS file not found")

    # Check Dependabot
    dependabot_file = github_dir / "dependabot.yml"
    if dependabot_file.exists():
        try:
            with open(dependabot_file, encoding="utf-8") as f:
                dependabot_config = yaml.safe_load(f)

            updates = dependabot_config.get("updates", [])
            has_pip = any(update.get("package-ecosystem") == "pip" for update in updates)
            has_github_actions = any(
                update.get("package-ecosystem") == "github-actions" for update in updates
            )

            if has_pip and has_github_actions:
                print("  ✅ Dependabot config: COMPREHENSIVE")
                results["config_files_enhanced"] += 1
            else:
                print("  ⚠️ Dependabot config: INCOMPLETE")
                results["issues_found"].append("Dependabot missing package ecosystems")

        except Exception as e:
            print("  ❌ Dependabot config: ERROR - {e}")
            results["issues_found"].append(f"Dependabot config error: {e}")
    else:
        print("  ❌ Dependabot config: MISSING")
        results["issues_found"].append("Dependabot configuration not found")

    print("\n📋 Issue and PR Templates:")

    # Check issue templates
    templates_dir = github_dir / "ISSUE_TEMPLATE"
    if templates_dir.exists():
        list(templates_dir.glob("*.md"))
        expected_templates = ["bug_report.md", "feature_request.md", "eq12_task.md"]

        for template in expected_templates:
            template_path = templates_dir / template
            if template_path.exists():
                print("  ✅ {template}: EXISTS")
                results["templates_created"] += 1
            else:
                print("  ❌ {template}: MISSING")
                results["issues_found"].append(f"Issue template {template} not found")
    else:
        print("  ❌ Issue templates directory: MISSING")
        results["issues_found"].append("ISSUE_TEMPLATE directory not found")

    # Check PR template
    pr_template = github_dir / "pull_request_template.md"
    if pr_template.exists():
        print("  ✅ Pull request template: EXISTS")
        results["templates_created"] += 1
    else:
        print("  ❌ Pull request template: MISSING")
        results["issues_found"].append("Pull request template not found")

    # Summary
    (
        results["workflows_fixed"]
        + results["security_improvements"]
        + results["config_files_enhanced"]
        + results["templates_created"]
    )

    print("\n" + "=" * 60)
    if len(results["issues_found"]) == 0:
        print("🎉 ALL GITHUB ISSUES RESOLVED SUCCESSFULLY!")
        print("\n✅ Summary:")
        print("   • {results['workflows_fixed']} workflow files secured with explicit permissions")
        print("   • {results['security_improvements']} security features implemented")
        print("   • {results['config_files_enhanced']} configuration files enhanced")
        print("   • {results['templates_created']} templates created")
        print("   • Total improvements: {total_checks}")
        print("\n🚀 GitHub repository is now enterprise-ready with:")
        print("   📋 Comprehensive issue templates")
        print("   🔒 Security audit workflows")
        print("   👥 Proper code ownership")
        print("   🔄 Automated dependency updates")
        print("   ⚡ Optimized CI/CD workflows")
    else:
        print("⚠️ {len(results['issues_found'])} issues still need attention:")
        for _issue in results["issues_found"]:
            print("  • {issue}")

    return results


if __name__ == "__main__":
    verify_github_fixes()
