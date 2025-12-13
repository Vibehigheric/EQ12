#!/usr/bin/env python3
"""
EQ12 Universal Code Repair Assistant - Expert Copilot Prompts and Automation
Comprehensive code analysis, repair prompts, and automated fixes for all common VS Code issues
Author: EQ12 Platform
Version: 3.0.0
"""

import json
import logging
import os
import sys
from datetime import UTC, datetime
from pathlib import Path


class EQ12UniversalRepairAssistant:
    def __init__(self, workspace_path: str | None = None):
        self.workspace = Path(workspace_path or os.getcwd())
        self.log_dir = Path("C:/EQ12/logs")
        self.config_dir = Path("C:/EQ12/configs")

        # Ensure directories exist
        for directory in [self.log_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self.setup_logging()

    def setup_logging(self):
        """Initialize logging system"""
        log_file = (
            self.log_dir /
            f"universal_repair_{
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
        self.logger.info("🤖 EQ12 Universal Repair Assistant initialized")

    def generate_expert_prompts(self) -> dict[str, dict]:
        """Generate comprehensive expert prompts for all repair scenarios"""

        prompts = {
            "gitleaks_security": {
                "title": "GitLeaks Security Remediation Expert",
                "category": "Security",
                "description": "Comprehensive secret detection and environment variable migration",
                "prompt": """You are an expert security auditor and remediation AI. Perform a comprehensive security analysis and automatic remediation:

**SECURITY SCAN AND REMEDIATION:**
1. Scan ALL files in the workspace for hardcoded credentials, API keys, passwords, tokens, or secrets
2. Identify patterns: AWS keys (AKIA*), OpenAI keys (sk-*), GitHub tokens (gh*_*), Slack tokens (xox*), etc.
3. For each secret found:
   - Replace with secure environment variable references (
       os.getenv(),
       process.env.,
       $env:,
       Environment.GetEnvironmentVariable()
   )
   - Generate appropriate variable names (AWS_ACCESS_KEY_ID, OPENAI_API_KEY, etc.)
   - Create .env file with extracted secrets
   - Add .env patterns to .gitignore

**ADDITIONAL SECURITY MEASURES:**
4. Add input validation and null checks for environment variables
5. Implement secure credential loading with fallbacks
6. Add security headers and middleware where applicable
7. Review file permissions and access patterns
8. Generate security audit report with recommendations

**OUTPUT:**
- Create /logs/security_remediation_report.json with all changes
- List files modified, secrets found, and environment variables created
- Provide instructions for secure deployment and key rotation

Goal: Zero hardcoded secrets with production-ready security practices.""",
                "files_to_scan": [
                    "*.py",
                    "*.js",
                    "*.ts",
                    "*.ps1",
                    "*.sh",
                    "*.cs",
                    "*.json",
                    "*.yaml",
                    "*.yml",
                ],
                "auto_fix": True,
            },
            "script_integrity": {
                "title": "Multi-Language Script Integrity Expert",
                "category": "Code Quality",
                "description": "Comprehensive linting, formatting, and error correction",
                "prompt": """You are an expert multi-language code quality AI. Perform comprehensive script analysis and repair across all languages:

**PYTHON FIXES:**
1. Fix all syntax errors, missing imports, and undefined variables
2. Update deprecated functions to modern alternatives (
    e.g.,
    datetime.utcnow() → datetime.now(timezone.utc)
)
3. Add proper type hints and docstrings
4. Apply Black formatting and fix Flake8/Pylint issues
5. Add error handling and input validation
6. Fix security issues flagged by Bandit

**JAVASCRIPT/TYPESCRIPT FIXES:**
1. Fix ESLint errors and apply Prettier formatting
2. Add proper TypeScript types and interfaces
3. Fix async/await patterns and Promise handling
4. Update deprecated Node.js APIs
5. Add proper error boundaries and validation
6. Fix React key props and component lifecycle issues

**POWERSHELL FIXES:**
1. Fix PSScriptAnalyzer warnings and errors
2. Add proper CmdletBinding() and parameter validation
3. Use approved verbs and consistent naming
4. Add proper error handling with try/catch blocks
5. Fix scope and variable declaration issues

**BASH FIXES:**
1. Fix ShellCheck warnings and errors
2. Add proper error handling with set -e
3. Quote variables and handle spaces in paths
4. Use modern bash constructs and avoid deprecated syntax

**OUTPUT:**
- Generate /logs/script_integrity_report.json with all fixes applied
- Document performance improvements and security enhancements
- Provide migration notes for deprecated features

Goal: Production-ready, maintainable code with zero linting errors.""",
                "files_to_scan": [
                    "*.py",
                    "*.js",
                    "*.jsx",
                    "*.ts",
                    "*.tsx",
                    "*.ps1",
                    "*.psm1",
                    "*.sh",
                    "*.bash",
                ],
                "auto_fix": True,
            },
            "context_validation": {
                "title": "Context Access and Threading Expert",
                "category": "Runtime Safety",
                "description": "Fix invalid context access, threading issues, and async problems",
                "prompt": """You are an expert threading and async programming AI. Fix all context access violations and threading issues:

**THREADING AND CONTEXT FIXES:**
1. Fix UI thread violations - use proper Invoke/Dispatcher calls for cross-thread UI access
2. Ensure proper async/await patterns throughout - never mix blocking and async code
3. Add proper object lifetime management and disposal patterns
4. Fix race conditions and add appropriate locking mechanisms
5. Validate Entity Framework context usage - ensure proper scoping and disposal

**ASYNC PROGRAMMING FIXES:**
6. Fix missing await keywords on async operations
7. Add proper cancellation token support for long-running operations
8. Fix deadlock-prone patterns (e.g., .Result on async methods in sync context)
9. Ensure proper ConfigureAwait(false) usage in library code
10. Add timeout handling for network operations

**RESOURCE MANAGEMENT:**
11. Implement proper using statements and IDisposable patterns
12. Fix memory leaks from event handler subscriptions
13. Add proper cleanup in finally blocks or using statements
14. Validate database connection lifecycle and pooling

**OUTPUT:**
- Create /logs/context_validation_report.json with all threading fixes
- Document performance improvements from async optimizations
- Provide best practices guide for future development

Goal: Thread-safe, properly scoped code with no context access violations.""",
                "files_to_scan": ["*.cs", "*.py", "*.js", "*.ts"],
                "auto_fix": True,
            },
            "react_mapping": {
                "title": "React JSX and Mapping Expert",
                "category": "Frontend",
                "description": "Fix nested mapping, implicit keys, and React performance issues",
                "prompt": """You are an expert React and JSX optimization AI. Fix all mapping, rendering, and performance issues:

**JSX AND MAPPING FIXES:**
1. Fix nested .map() calls - extract inner maps to separate memoized components
2. Add explicit, stable keys for ALL JSX lists (key = (
    {item.id}, never use array index unless no alternative)
)
3. Fix "implicit keys need to be in line" - ensure key props are properly formatted and positioned
4. Refactor nested mapping inside context providers - move context outside mapping functions
5. Extract complex JSX expressions to separate functions or components

**PERFORMANCE OPTIMIZATIONS:**
6. Add React.memo() for components that re-render unnecessarily
7. Optimize context providers to prevent unnecessary re-renders (useMemo for context values)
8. Fix dependency arrays in useEffect, useMemo, and useCallback
9. Add proper prop types and TypeScript interfaces
10. Implement proper error boundaries and fallback UI

**ADVANCED REACT PATTERNS:**
11. Fix conditional rendering patterns for better performance
12. Optimize large list rendering with virtualization where appropriate
13. Add proper form validation and controlled component patterns
14. Fix state management anti-patterns and prop drilling

**OUTPUT:**
- Generate /logs/react_optimization_report.json with performance improvements
- Document component extraction and memoization changes
- Provide React best practices guide

Goal: Performant, maintainable React code with proper key management and optimized rendering.""",
                "files_to_scan": ["*.jsx", "*.tsx", "*.js", "*.ts"],
                "auto_fix": True,
            },
            "action_resolution": {
                "title": "Action and Reference Resolution Expert",
                "category": "Build System",
                "description": "Fix unresolved actions, missing imports, and build configuration issues",
                "prompt": """You are an expert build system and dependency resolution AI. Fix all unresolved references and build issues:

**IMPORT AND REFERENCE FIXES:**
1. Fix all missing imports and namespace references
2. Resolve "unable to resolve action" errors in GitHub Actions, Azure Pipelines, and CI/CD configs
3. Update deprecated action versions (e.g., actions/checkout@v4 instead of @v1)
4. Fix project references and dependency paths in solution files

**BUILD CONFIGURATION:**
5. Align target frameworks across projects (.NET, Node.js versions)
6. Fix NuGet/npm/pip package version conflicts and security vulnerabilities
7. Update outdated dependencies to latest stable versions
8. Fix circular dependencies and project reference issues

**CI/CD AND AUTOMATION:**
9. Fix YAML syntax and indentation errors
10. Update runner versions and environment configurations
11. Add proper secret management in CI/CD pipelines
12. Fix path issues and cross-platform compatibility

**ENVIRONMENT SETUP:**
13. Generate proper package.json, requirements.txt, or .csproj configurations
14. Add missing development dependencies and tooling
15. Create proper .gitignore patterns for each technology stack
16. Add VSCode/Visual Studio configuration files for consistent development

**OUTPUT:**
- Create /logs/action_resolution_report.json with all fixes
- Document dependency updates and version changes
- Provide setup instructions for new developers

Goal: Fully buildable, resolvable project with no missing references or build errors.""",
                "files_to_scan": [
                    "*.json",
                    "*.yaml",
                    "*.yml",
                    "*.csproj",
                    "*.sln",
                    "*.py",
                    "*.js",
                    "*.ts",
                    "*.cs",
                ],
                "auto_fix": True,
            },
            "comprehensive_health": {
                "title": "Comprehensive Workspace Health Expert",
                "category": "System Health",
                "description": "Complete workspace analysis and repair across all categories",
                "prompt": """You are the ultimate code health and repair AI. Perform a comprehensive analysis and fix ALL issues across the entire workspace:

**EXECUTE ALL REPAIR CATEGORIES:**
1. **Security Audit**: Scan for and remediate all hardcoded secrets, implement proper environment variable usage
2. **Code Quality**: Fix linting errors, formatting issues, and code smells across all languages
3. **Threading Safety**: Resolve context access violations, async issues, and resource management problems
4. **Performance**: Optimize React rendering, database queries, and resource usage
5. **Build System**: Fix all unresolved references, dependency conflicts, and configuration issues

**ADVANCED ANALYSIS:**
6. **Architecture Review**: Identify and fix architectural anti-patterns
7. **Security Hardening**: Add input validation, sanitization, and secure coding practices
8. **Error Handling**: Implement comprehensive error handling and logging throughout
9. **Testing**: Add missing test cases and fix broken tests
10. **Documentation**: Generate proper README, API documentation, and code comments

**PROACTIVE IMPROVEMENTS:**
11. **Modernization**: Update to latest language features and best practices
12. **Accessibility**: Fix accessibility issues in UI components
13. **SEO/Performance**: Optimize web applications for performance and SEO
14. **Monitoring**: Add health checks, metrics, and observability

**COMPREHENSIVE OUTPUT:**
- Generate /logs/comprehensive_health_report.json with executive summary
- Create workspace_improvements.md with detailed improvement guide
- Provide priority-ordered task list for ongoing maintenance
- Generate developer onboarding guide

Goal: Production-ready, secure, performant, and maintainable codebase with comprehensive documentation.""",
                "files_to_scan": ["*.*"],
                "auto_fix": True,
            },
        }

        # Save prompts to configuration
        prompts_file = self.config_dir / "universal_repair_prompts.json"
        with open(prompts_file, "w", encoding="utf-8") as f:
            json.dump(prompts, f, indent=2, ensure_ascii=False)

        self.logger.info(
            f"💡 Generated {
                len(prompts)} expert repair prompts: {prompts_file}")
        return prompts

    def generate_vscode_tasks(self) -> dict:
        """Generate VS Code tasks.json configuration for all repair operations"""

        tasks_config = {"version": "2.0.0",
                        "tasks": [{"label": "EQ12: Complete Security Scan",
                                   "type": "shell",
                                   "command": "python",
                                   "args": ["${workspaceFolder}/scripts/eq12_gitleaks_guardian.py",
                                            "--action",
                                            "comprehensive",
                                            "--workspace",
                                            "${workspaceFolder}",
                                            "--verbose",
                                            ],
                                   "group": {"kind": "test",
                                             "isDefault": True},
                                   "presentation": {"echo": True,
                                                    "reveal": "always",
                                                    "focus": False,
                                                    "panel": "new",
                                                    },
                                   "problemMatcher": [],
                                   },
                                  {"label": "EQ12: Script Integrity Check",
                                   "type": "shell",
                                   "command": "powershell",
                                   "args": ["-ExecutionPolicy",
                                            "Bypass",
                                            "-File",
                                            "${workspaceFolder}/scripts/eq12_script_integrity_suite.ps1",
                                            "-Action",
                                            "All",
                                            "-AutoFix",
                                            "-GenerateReport",
                                            ],
                                   "group": "test",
                                   "presentation": {"echo": True,
                                                    "reveal": "always",
                                                    "focus": False,
                                                    "panel": "new",
                                                    },
                                   "problemMatcher": [],
                                   },
                                  {"label": "EQ12: VS Code Troubleshooter",
                                   "type": "shell",
                                   "command": "powershell",
                                   "args": ["-ExecutionPolicy",
                                            "Bypass",
                                            "-File",
                                            "${workspaceFolder}/scripts/eq12_vscode_troubleshooter_simple.ps1",
                                            "-Action",
                                            "Full",
                                            "-Workspace",
                                            "${workspaceFolder}",
                                            ],
                                   "group": "build",
                                   "presentation": {"echo": True,
                                                    "reveal": "always",
                                                    "focus": False,
                                                    "panel": "new",
                                                    },
                                   "problemMatcher": [],
                                   },
                                  {"label": "EQ12: Quick Health Check",
                                   "type": "shell",
                                   "command": "python",
                                   "args": ["${workspaceFolder}/scripts/eq12_universal_repair_assistant.py",
                                            "--action",
                                            "health-check",
                                            "--workspace",
                                            "${workspaceFolder}",
                                            ],
                                   "group": "build",
                                   "presentation": {"echo": True,
                                                    "reveal": "always",
                                                    "focus": False,
                                                    "panel": "shared",
                                                    },
                                   "problemMatcher": [],
                                   },
                                  {"label": "EQ12: Emergency Repair Suite",
                                   "dependsOrder": "sequence",
                                   "dependsOn": ["EQ12: Complete Security Scan",
                                                 "EQ12: Script Integrity Check",
                                                 "EQ12: VS Code Troubleshooter",
                                                 ],
                                   "group": "build",
                                   "presentation": {"echo": True,
                                                    "reveal": "always",
                                                    "focus": True,
                                                    "panel": "new",
                                                    },
                                   },
                                  ],
                        }

        # Save tasks configuration
        vscode_dir = self.workspace / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        tasks_file = vscode_dir / "tasks.json"
        with open(tasks_file, "w", encoding="utf-8") as f:
            json.dump(tasks_config, f, indent=2, ensure_ascii=False)

        self.logger.info(f"⚙️ Generated VS Code tasks configuration: {tasks_file}")
        return tasks_config

    def generate_copilot_workspace_config(self) -> dict:
        """Generate GitHub Copilot workspace configuration for optimal AI assistance"""

        copilot_config = {
            "copilot": {
                "enable": True,
                "suggestions": {"enabled": True, "keyBindings": "tab"},
                "chat": {
                    "enabled": True,
                    "contextFiles": [
                        "AGENTS.md",
                        "README.md",
                        "package.json",
                        "requirements.txt",
                        ".gitignore",
                    ],
                },
            },
            "eq12": {
                "prompts": {
                    "security": "Use the EQ12 GitLeaks Guardian prompts for security analysis",
                    "quality": "Apply EQ12 Script Integrity Suite standards for code quality",
                    "performance": "Follow EQ12 optimization patterns for performance improvements",
                    "context": "Implement EQ12 context validation patterns for thread safety",
                },
                "standards": {
                    "logging": "Always use structured JSON logging to C:/EQ12/logs",
                    "secrets": "Never hardcode secrets - use environment variables only",
                    "errors": "Implement comprehensive error handling with proper logging",
                    "testing": "Include pytest and Pester tests for all new functionality",
                },
            },
        }

        # Save Copilot configuration
        copilot_file = self.config_dir / "copilot_workspace_config.json"
        with open(copilot_file, "w", encoding="utf-8") as f:
            json.dump(copilot_config, f, indent=2, ensure_ascii=False)

        self.logger.info(f"🤖 Generated Copilot workspace configuration: {copilot_file}")
        return copilot_config

    def run_health_check(self) -> dict:
        """Perform quick health check of workspace"""

        self.logger.info("🏥 Running EQ12 workspace health check...")

        health_status = {
            "timestamp": datetime.now(UTC).isoformat(),
            "workspace": str(self.workspace),
            "checks": {
                "git_repo": False,
                "secrets_safe": False,
                "scripts_valid": False,
                "dependencies_ok": False,
                "config_present": False,
            },
            "issues": [],
            "recommendations": [],
        }

        # Check if Git repository
        if (self.workspace / ".git").exists():
            health_status["checks"]["git_repo"] = True
        else:
            health_status["issues"].append("Not a Git repository")
            health_status["recommendations"].append(
                "Initialize Git repository: git init")

        # Check for common secret patterns (basic check)
        common_secrets = [".env", "*.key", "*.pem", "config.json"]
        secret_files = []
        for pattern in common_secrets:
            secret_files.extend(list(self.workspace.glob(pattern)))

        if secret_files:
            health_status["issues"].append(
                f"Potential secret files found: {[f.name for f in secret_files]}"
            )
            health_status["recommendations"].append(
                "Run EQ12 GitLeaks Guardian for comprehensive secret scan"
            )
        else:
            health_status["checks"]["secrets_safe"] = True

        # Check for script files
        script_patterns = ["*.py", "*.js", "*.ps1", "*.sh"]
        script_files = []
        for pattern in script_patterns:
            script_files.extend(list(self.workspace.glob(pattern)))

        if script_files:
            health_status["checks"]["scripts_valid"] = True
        else:
            health_status["issues"].append("No script files found")

        # Check for dependency files
        dep_files = ["package.json", "requirements.txt", "*.csproj", "pyproject.toml"]
        dep_found = any(
            (self.workspace / pattern).exists() or list(self.workspace.glob(pattern))
            for pattern in dep_files
        )

        if dep_found:
            health_status["checks"]["dependencies_ok"] = True
        else:
            health_status["issues"].append("No dependency configuration files found")
            health_status["recommendations"].append(
                "Create appropriate dependency files (package.json, requirements.txt, etc.)"
            )

        # Check for EQ12 configuration
        if self.config_dir.exists() and any(self.config_dir.glob("*.json")):
            health_status["checks"]["config_present"] = True
        else:
            health_status["issues"].append("EQ12 configuration not found")
            health_status["recommendations"].append(
                "Run EQ12 Universal Repair Assistant to generate configuration"
            )

        # Calculate overall health score
        total_checks = len(health_status["checks"])
        passed_checks = sum(health_status["checks"].values())
        health_score = (passed_checks / total_checks) * 100

        health_status["health_score"] = health_score
        health_status["status"] = (
            "HEALTHY"
            if health_score >= 80
            else "NEEDS_ATTENTION" if health_score >= 60 else "CRITICAL"
        )

        # Save health check results
        health_file = (
            self.log_dir /
            f"health_check_{
                datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json")
        with open(health_file, "w", encoding="utf-8") as f:
            json.dump(health_status, f, indent=2, ensure_ascii=False)

        self.logger.info(
            f"🏥 Health check complete - Score: {health_score:.1f}% ({health_status['status']})"
        )
        self.logger.info(f"📊 Health report saved: {health_file}")

        return health_status

    def generate_comprehensive_suite(self) -> dict:
        """Generate complete EQ12 repair and maintenance suite"""

        self.logger.info("🚀 Generating comprehensive EQ12 repair suite...")

        suite_components = {
            "expert_prompts": self.generate_expert_prompts(),
            "vscode_tasks": self.generate_vscode_tasks(),
            "copilot_config": self.generate_copilot_workspace_config(),
            "health_status": self.run_health_check(),
        }

        # Create comprehensive documentation
        readme_content = """# EQ12 Universal Repair Assistant

## Overview
Complete automation suite for VS Code troubleshooting, security scanning, and code quality management.

## Quick Start Commands

### Security & Secrets
```bash
# Complete security scan and remediation
python scripts/eq12_gitleaks_guardian.py --action comprehensive

# Quick secret scan only
python scripts/eq12_gitleaks_guardian.py --action scan
```

### Script Quality
```powershell
# Complete script integrity check (all languages)
.\\\\scripts\\\\eq12_script_integrity_suite.ps1 -Action All -AutoFix

# Python only linting
.\\\\scripts\\\\eq12_script_integrity_suite.ps1 -Action Lint -Language Python
```

### VS Code Issues
```powershell
# Complete VS Code troubleshooting
.\\\\scripts\\\\eq12_vscode_troubleshooter_simple.ps1 -Action Full

# Quick health check
.\\\\scripts\\\\eq12_vscode_troubleshooter_simple.ps1 -Action Quick
```

### One-Click Solutions
Use VS Code Command Palette (Ctrl+Shift+P):
- `Tasks: Run Task` → `EQ12: Emergency Repair Suite` (runs all repairs)
- `Tasks: Run Task` → `EQ12: Quick Health Check` (diagnosis only)

## Expert Copilot Prompts

Copy and paste these into GitHub Copilot Chat for automated repairs:

### 🔐 Security Remediation
```
{prompts[security]}
```

### 🧹 Script Quality
```
{prompts[quality]}
```

### ⚡ Performance & Threading
```
{prompts[performance]}
```

### 🎯 Complete Health Check
```
{prompts[comprehensive]}
```

## File Structure
```
C:\\\\EQ12\\
├── scripts/              # Automation scripts
├── logs/                 # Execution logs and reports
├── configs/              # Configuration files
└── .vscode/tasks.json    # VS Code task definitions
```

## Support
- Logs: Check `C:\\\\EQ12\\logs\\` for detailed execution reports
- Issues: Review JSON reports for specific problems and solutions
- Configuration: All settings stored in `C:\\\\EQ12\\configs\\`
"""

        # Format README with actual prompts
        prompts = suite_components["expert_prompts"]
        formatted_readme = readme_content.format(
            prompts={
                "security": prompts["gitleaks_security"]["prompt"][:500] + "...",
                "quality": prompts["script_integrity"]["prompt"][:500] + "...",
                "performance": prompts["context_validation"]["prompt"][:500] + "...",
                "comprehensive": prompts["comprehensive_health"]["prompt"][:500] + "...",
            }
        )

        readme_file = self.workspace / "EQ12_REPAIR_GUIDE.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(formatted_readme)

        # Save complete suite configuration
        suite_file = (
            self.config_dir /
            f"repair_suite_{
                datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json")
        with open(suite_file, "w", encoding="utf-8") as f:
            # Remove circular references for JSON serialization
            suite_copy = suite_components.copy()
            suite_copy["summary"] = {
                "prompts_generated": len(suite_components["expert_prompts"]),
                "tasks_created": len(suite_components["vscode_tasks"]["tasks"]),
                "health_score": suite_components["health_status"]["health_score"],
                "timestamp": datetime.now(UTC).isoformat(),
            }
            json.dump(suite_copy, f, indent=2, ensure_ascii=False)

        self.logger.info("✅ Comprehensive repair suite generated successfully")
        self.logger.info(f"📚 User guide: {readme_file}")
        self.logger.info(f"⚙️ Configuration: {suite_file}")

        return suite_components


def main():
    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Universal Code Repair Assistant")
    parser.add_argument(
        "--workspace",
        "-w",
        default=None,
        help="Workspace directory path")
    parser.add_argument(
        "--action",
        "-a",
        choices=["health-check", "generate-prompts", "generate-tasks", "comprehensive"],
        default="comprehensive",
        help="Action to perform",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    assistant = EQ12UniversalRepairAssistant(args.workspace)

    try:
        if args.action == "health-check":
            health = assistant.run_health_check()
            print(
                f"🏥 Workspace Health: {
                    health['status']} ({
                    health['health_score']:.1f}%)")

        elif args.action == "generate-prompts":
            prompts = assistant.generate_expert_prompts()
            print(f"💡 Generated {len(prompts)} expert prompts")

        elif args.action == "generate-tasks":
            tasks = assistant.generate_vscode_tasks()
            print(f"⚙️ Generated {len(tasks['tasks'])} VS Code tasks")

        elif args.action == "comprehensive":
            assistant.generate_comprehensive_suite()
            print("🚀 Comprehensive repair suite generated successfully!")
            print("📚 See EQ12_REPAIR_GUIDE.md for usage instructions")

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
