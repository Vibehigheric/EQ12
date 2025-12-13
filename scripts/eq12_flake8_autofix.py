#!/usr/bin/env python3
"""
EQ12 Flake8 Comprehensive Auto-Fix System
Complete Python code quality automation with all E02*, W*, F*, and C* error handling
Author: EQ12 Platform
Version: 2.0.0
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


class EQ12Flake8AutoFixer:
    def __init__(self, workspace_path: str | None = None):
        self.workspace = Path(workspace_path or os.getcwd())
        self.log_dir = Path("C:/EQ12/logs")
        self.config_dir = Path("C:/EQ12/configs")

        # Ensure directories exist
        for directory in [self.log_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        self.setup_logging()

        # Flake8 error categories and their descriptions
        self.error_categories = {
            "E02": "Spacing and indentation issues (E201-E272)",
            "E30": "Blank line issues (E301-E306)",
            "E50": "Line length issues (E501-E502)",
            "E70": "Statement construction issues (E701-E743)",
            "W29": "Whitespace issues (W291-W293)",
            "W60": "Escape sequence issues (W601-W606)",
            "F40": "Import issues (F401-F405)",
            "F82": "Undefined name issues (F821-F823)",
            "F84": "Unused local variable issues (F841)",
            "C90": "Complexity issues (C901)",
        }

    def setup_logging(self):
        """Initialize comprehensive logging system"""
        log_file = (
            self.log_dir /
            f"flake8_autofix_{
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
            f"🐍 EQ12 Flake8 Auto-Fixer initialized - Workspace: {self.workspace}")

    def check_prerequisites(self) -> bool:
        """Verify required tools are installed"""
        self.logger.info("🔍 Checking Python linting prerequisites...")

        required_tools = ["python", "pip"]
        missing_tools = []

        for tool in required_tools:
            try:
                subprocess.run([tool, "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing_tools.append(tool)

        if missing_tools:
            self.logger.error(f"❌ Missing required tools: {', '.join(missing_tools)}")
            return False

        self.logger.info("✅ Python environment available")
        return True

    def install_linting_tools(self) -> dict[str, bool]:
        """Install or upgrade Python linting tools"""
        self.logger.info("📦 Installing/upgrading Python linting tools...")

        tools = {
            "flake8": False,
            "autopep8": False,
            "black": False,
            "isort": False,
            "pylint": False,
            "mypy": False,
            "bandit": False,
        }

        for tool in tools:
            try:
                self.logger.info(f"Installing {tool}...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", tool],
                    capture_output=True,
                    check=True,
                )
                tools[tool] = True
                self.logger.info(f"✅ {tool} installed successfully")
            except subprocess.CalledProcessError as e:
                self.logger.warning(f"⚠️ Failed to install {tool}: {e}")

        return tools

    def get_python_files(self) -> list[Path]:
        """Discover Python files in workspace"""
        self.logger.info("🔍 Discovering Python files...")

        python_files = list(self.workspace.rglob("*.py"))

        # Filter out common directories to skip
        skip_patterns = [
            "__pycache__",
            ".git",
            ".vs",
            ".vscode",
            "node_modules",
            "venv",
            "env",
            ".pytest_cache",
            "dist",
            "build",
        ]

        filtered_files = []
        for file in python_files:
            if not any(pattern in str(file) for pattern in skip_patterns):
                filtered_files.append(file)

        self.logger.info(f"📋 Found {len(filtered_files)} Python files to analyze")
        return filtered_files

    def run_flake8_analysis(self) -> tuple[dict, list[str]]:
        """Run comprehensive Flake8 analysis"""
        self.logger.info("🔍 Running comprehensive Flake8 analysis...")

        try:
            # Run flake8 with detailed output
            result = subprocess.run(
                [
                    "flake8",
                    str(self.workspace),
                    "--statistics",
                    "--show-source",
                    "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
                ],
                capture_output=True,
                text=True,
                cwd=self.workspace,
            )

            if result.returncode == 0:
                self.logger.info("✅ No Flake8 issues found")
                return {}, []

            # Parse Flake8 output
            errors = result.stdout.strip().split("\n") if result.stdout.strip() else []

            # Categorize errors
            categorized_errors = {}
            for error_line in errors:
                if ":" in error_line and any(
                    code in error_line for code in [
                        "E", "W", "", "C"]):
                    # Extract error code
                    parts = error_line.split(":")
                    if len(parts) >= 4:
                        error_part = parts[3].strip()
                        error_code = error_part.split()[0] if error_part else "UNKNOWN"

                        # Categorize by prefix
                        category = error_code[:3] if len(
                            error_code) >= 3 else error_code
                        if category not in categorized_errors:
                            categorized_errors[category] = []
                        categorized_errors[category].append(error_line)

            total_errors = len(errors)
            self.logger.warning(
                f"🚨 Found {total_errors} Flake8 issues across {
                    len(categorized_errors)} categories")

            return categorized_errors, errors

        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Flake8 analysis failed: {e}")
            return {}, []

    def apply_autopep8_fixes(
            self, target_errors: list[str] | None = None) -> dict[str, int]:
        """Apply autopep8 automatic fixes"""
        self.logger.info("🛠️ Applying autopep8 automatic fixes...")

        fixes_applied = {"files_processed": 0, "errors_fixed": 0, "errors": 0}

        try:
            python_files = self.get_python_files()

            for file_path in python_files:
                try:
                    # Apply autopep8 fixes
                    cmd = [
                        sys.executable,
                        "-m",
                        "autopep8",
                        "--in-place",
                        "--aggressive",
                        "--aggressive",
                        str(file_path),
                    ]

                    # If specific errors targeted, use select option
                    if target_errors:
                        error_codes = ",".join(target_errors)
                        cmd.extend(["--select", error_codes])

                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode == 0:
                        fixes_applied["files_processed"] += 1
                    else:
                        self.logger.warning(f"⚠️ autopep8 warning for {file_path.name}")

                except Exception as e:
                    self.logger.error(f"❌ Error processing {file_path.name}: {e}")
                    fixes_applied["errors"] += 1

            self.logger.info(
                f"✅ autopep8 processed {
                    fixes_applied['files_processed']} files")

        except Exception as e:
            self.logger.error(f"❌ autopep8 execution failed: {e}")
            fixes_applied["errors"] += 1

        return fixes_applied

    def apply_black_formatting(self) -> dict[str, int]:
        """Apply Black code formatting"""
        self.logger.info("⚫ Applying Black code formatting...")

        result_stats = {"files_formatted": 0, "errors": 0}

        try:
            cmd = [
                sys.executable,
                "-m",
                "black",
                "--line-length",
                "88",
                "--target-version",
                "py38",
                str(self.workspace),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.workspace)

            # Parse Black output to count reformatted files
            if result.stdout:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "reformatted" in line.lower():
                        result_stats["files_formatted"] += 1

            if result.returncode == 0:
                self.logger.info(
                    f"✅ Black formatting completed - {result_stats['files_formatted']} files reformatted"
                )
            else:
                self.logger.warning("⚠️ Black formatting completed with warnings")

        except Exception as e:
            self.logger.error(f"❌ Black formatting failed: {e}")
            result_stats["errors"] += 1

        return result_stats

    def apply_isort_imports(self) -> dict[str, int]:
        """Apply isort import sorting"""
        self.logger.info("📝 Sorting imports with isort...")

        result_stats = {"files_processed": 0, "imports_sorted": 0, "errors": 0}

        try:
            cmd = [
                sys.executable,
                "-m",
                "isort",
                "--profile",
                "black",
                "--line-length",
                "88",
                str(self.workspace),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.workspace)

            if result.stdout:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "Fixing" in line:
                        result_stats["imports_sorted"] += 1

            self.logger.info(
                f"✅ isort completed - {result_stats['imports_sorted']} files with sorted imports"
            )

        except Exception as e:
            self.logger.error(f"❌ isort failed: {e}")
            result_stats["errors"] += 1

        return result_stats

    def fix_specific_error_categories(self, categories: list[str]) -> dict[str, int]:
        """Fix specific Flake8 error categories"""
        self.logger.info(
            f"🎯 Targeting specific error categories: {
                ', '.join(categories)}")

        category_fixes = {}

        for category in categories:
            if category.upper() == "E02":
                # E02* - Spacing and indentation issues
                self.logger.info("🔧 Fixing E02* spacing and indentation issues...")
                fixes = self.apply_autopep8_fixes(
                    [
                        "E201",
                        "E202",
                        "E203",
                        "E211",
                        "E221",
                        "E222",
                        "E225",
                        "E226",
                        "E231",
                        "E241",
                        "E251",
                        "E261",
                        "E262",
                        "E265",
                        "E266",
                        "E271",
                        "E272",
                    ]
                )
                category_fixes["E02"] = fixes

            elif category.upper() == "E30":
                # E30* - Blank line issues
                self.logger.info("🔧 Fixing E30* blank line issues...")
                fixes = self.apply_autopep8_fixes(
                    ["E301", "E302", "E303", "E304", "E305", "E306"])
                category_fixes["E30"] = fixes

            elif category.upper() == "W29":
                # W29* - Whitespace issues
                self.logger.info("🔧 Fixing W29* whitespace issues...")
                fixes = self.apply_autopep8_fixes(["W291", "W292", "W293"])
                category_fixes["W29"] = fixes

            elif category.upper() == "F84":
                # F841 - Unused local variable issues
                self.logger.info("🔧 Fixing F841 unused local variable issues...")
                fixes = self.fix_f841_unused_variables()
                category_fixes["F84"] = fixes

        return category_fixes

    def parse_flake8_output(self, flake8_output: str) -> list[dict]:
        """Parse flake8 output into structured error information"""
        errors = []

        for line in flake8_output.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Parse flake8 output format: filename:line:column: code message
            parts = line.split(":", 3)
            if len(parts) >= 4:
                errors.append(
                    {
                        "file": parts[0],
                        "line": int(parts[1]),
                        "column": int(parts[2]),
                        "code_and_message": parts[3].strip(),
                        "message": parts[3].strip(),
                    }
                )

        return errors

    def run_flake8(self, args: list[str] | None = None) -> str:
        """Run flake8 with specified arguments and return output"""
        cmd = ["flake8"]
        if args:
            cmd.extend(args)

        # Add workspace directory
        cmd.append(str(self.workspace))

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,  # Don't raise exception on non-zero exit
            )
            return result.stdout
        except Exception as e:
            self.logger.error(f"❌ Failed to run flake8: {e}")
            return ""

    def fix_f841_unused_variables(self) -> int:
        """Fix F841 unused local variable errors with intelligent handling"""
        self.logger.info("🧹 Analyzing and fixing unused local variables (F841)...")

        # Get F841 errors from flake8
        if not flake8_output:
            self.logger.info("✅ No F841 unused variable errors found")
            return 0

        f841_errors = self.parse_flake8_output(flake8_output)
        fixes_applied = 0

        # Group errors by file for batch processing
        errors_by_file = {}
        for error in f841_errors:
            file_path = error["file"]
            if file_path not in errors_by_file:
                errors_by_file[file_path] = []
            errors_by_file[file_path].append(error)

        for file_path, file_errors in errors_by_file.items():
            try:
                if self.fix_f841_in_file(file_path, file_errors):
                    fixes_applied += len(file_errors)
                    self.logger.info(
                        f"✅ Fixed {
                            len(file_errors)} F841 errors in {file_path}")

            except Exception as e:
                self.logger.error(f"❌ Failed to fix F841 errors in {file_path}: {e}")

        return fixes_applied

    def fix_f841_in_file(self, file_path: str, errors: list[dict]) -> bool:
        """Fix F841 errors in a specific file with intelligent variable handling"""
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            original_lines = lines[:]

            # Sort errors by line number (descending) to avoid offset issues
            errors.sort(key=lambda x: x["line"], reverse=True)

            for error in errors:
                line_no = error["line"] - 1  # Convert to 0-based indexing
                if line_no < len(lines):
                    line = lines[line_no]

                    # Extract variable name from F841 message
                    # Format: "local variable 'varname' is assigned to but never used"
                    import re

                    match = re.search(
                        r"local variable '([^']+)' is assigned to but never used",
                        error["message"],
                    )
                    if not match:
                        continue

                    var_name = match.group(1)

                    # Intelligent F841 handling
                    fixed_line = self.handle_f841_variable(
                        line, var_name, file_path, line_no + 1)
                    if fixed_line != line:
                        lines[line_no] = fixed_line
                        self.logger.info(
                            f"🔧 Fixed F841 for variable '{var_name}' at line {
                                line_no + 1}")

            # Only write if changes were made
            if lines != original_lines:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)
                return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Error processing file {file_path}: {e}")
            return False

    def handle_f841_variable(
            self,
            line: str,
            var_name: str,
            file_path: str,
            line_no: int) -> str:
        """Intelligently handle F841 unused variable with context awareness"""
        import re

        # Strategy 1: Check if it's a simple assignment that can be removed
        simple_assignment = re.match(rf"(\s*){re.escape(var_name)}\s*=\s*(.+)", line)
        if simple_assignment:
            indent = simple_assignment.group(1)
            value_expr = simple_assignment.group(2).strip()

            # Check if the expression has side effects (function calls, method calls)
            has_side_effects = self.expression_has_side_effects(value_expr)

            if has_side_effects:
                # Keep the expression but remove assignment
                return f"{indent}{value_expr}\n"
            else:
                # Safe to remove entirely if it's a literal or simple expression
                if self.is_safe_to_remove(value_expr):
                    # Comment out the line instead of removing to preserve line numbers
                    return f"{indent}# REMOVED: {var_name} = {value_expr}  # F841 unused variable\n"
                else:
                    # Rename to underscore to indicate intentional unused
                    return f"{indent}_ = {value_expr}  # F841 fix: renamed unused variable\n"

        # Strategy 2: For other patterns, rename variable to underscore
        line_fixed = re.sub(rf"\b{re.escape(var_name)}\b", f"_{var_name}", line)
        if line_fixed != line:
            return line_fixed

        # Strategy 3: Add underscore prefix as fallback
        return line.replace(var_name, f"_{var_name}", 1)

    def expression_has_side_effects(self, expr: str) -> bool:
        """Check if an expression likely has side effects"""
        side_effect_patterns = [
            r"\w+\(",  # Function calls
            r"\.\w+\(",  # Method calls
            r"\.append\(",  # List modifications
            r"\.update\(",  # Dict updates
            r"\.write\(",  # File writes
            r"\.send\(",  # Network calls
            r"\.execute\(",  # Database calls
            r"input\(",  # User input
            r"print\(",  # Output functions
            r"open\(",  # File operations
        ]

        return any(re.search(pattern, expr, re.IGNORECASE)
                   for pattern in side_effect_patterns)

    def is_safe_to_remove(self, expr: str) -> bool:
        """Check if an expression is safe to completely remove"""
        import ast

        try:
            # Try to parse as a simple literal or name
            node = ast.parse(expr.strip(), mode="eval")

            # Safe literals: numbers, strings, booleans, None, simple names
            if isinstance(node.body, (ast.Constant, ast.Name)):
                return True

            # Simple list/dict/tuple literals
            if isinstance(node.body, (ast.List, ast.Dict, ast.Tuple)):
                return True

        except (SyntaxError, ValueError):
            pass

        return False

    def generate_copilot_prompts(self) -> dict[str, str]:
        """Generate expert Copilot prompts for comprehensive Python fixes"""

        prompts = {
            "flake8_comprehensive": """You are an expert Python linter and code quality engineer. Perform comprehensive Flake8 compliance analysis and automatic fixing:

**COMPREHENSIVE FLAKE8 REPAIR:**
1. **E02* Spacing Issues**: Fix all spacing around operators, parentheses, brackets, commas, and colons
2. **E30* Blank Lines**: Ensure proper blank line spacing between functions, classes, and methods
3. **E50* Line Length**: Break long lines intelligently while maintaining readability
4. **W29* Whitespace**: Remove trailing whitespace and ensure proper file endings
5. **F40* Imports**: Remove unused imports and fix import organization
6. **F82* Names**: Fix undefined variables and remove unused local variables
7. **F84* Unused Variables**: Intelligently handle F841 unused local variable errors
8. **C90* Complexity**: Refactor overly complex functions into smaller, maintainable units

**ADVANCED PYTHON QUALITY:**
9. Add proper type hints where missing or incorrect
10. Implement comprehensive docstrings following Google or NumPy style
11. Add proper error handling and input validation
12. Apply Black formatting for consistent code style
13. Sort imports using isort with Black profile compatibility
14. Ensure PEP8 compliance across all Python files

**OUTPUT REQUIREMENTS:**
- Generate /logs/flake8_comprehensive_fixes.json with detailed change log
- Document performance improvements and refactoring decisions
- Provide before/after complexity metrics for refactored functions
- Include recommendations for further code improvements

Goal: Production-ready, fully compliant Python codebase with zero Flake8 errors and modern best practices.""",
            "flake8_e02_specialist": """You are an expert Python spacing and indentation specialist. Fix all Flake8 E02* category errors:

**SPACING FIXES (E02* Category):**
1. **E201/E202**: Remove extra whitespace after '(' and before ')'
2. **E203**: Remove whitespace before ':' in slicing operations
3. **E211**: Remove whitespace before '(' in function calls
4. **E221/E222**: Fix multiple spaces around operators
5. **E225/E226**: Add missing whitespace around operators and arithmetic
6. **E231**: Add missing whitespace after commas in function calls
7. **E241**: Remove multiple spaces after commas
8. **E251**: Remove unexpected spaces around '=' in keyword arguments
9. **E261/E262**: Fix inline comment spacing (at least 2 spaces, start with '# ')
10. **E265/E266**: Fix block comment formatting
11. **E271/E272**: Remove extra spaces inside brackets and parentheses

**QUALITY ASSURANCE:**
- Preserve all existing functionality and logic
- Maintain consistent indentation style (spaces vs tabs)
- Ensure proper operator precedence is maintained
- Validate fixes with autopep8 and Black compatibility

**LOGGING:**
- Create /logs/flake8_e02_spacing_fixes.txt with line-by-line changes
- Document each fix type and count of corrections made

Goal: Perfect spacing compliance with PEP8 standards for professional Python code.""",
            "python_import_optimizer": """You are an expert Python import optimization specialist. Fix all import-related issues:

**IMPORT OPTIMIZATION (F40* Category):**
1. **F401**: Remove all unused imports automatically
2. **F403**: Fix 'from module import *' to explicit imports
3. **F405**: Fix names that may be undefined due to star imports
4. **Import Organization**: Group imports in PEP8 order (standard library, third-party, local)
5. **Import Sorting**: Apply isort with Black profile compatibility

**ADVANCED IMPORT MANAGEMENT:**
6. Convert relative imports to absolute where appropriate
7. Add missing imports for undefined names (F821)
8. Optimize imports for better performance (lazy loading where beneficial)
9. Add proper __all__ definitions in modules
10. Fix circular import issues with refactoring suggestions

**VALIDATION:**
- Ensure all imports resolve correctly
- Test that functionality is preserved after import changes
- Verify no new undefined name errors are introduced

**OUTPUT:**
- Generate /logs/python_import_optimization.json with all changes
- List removed unused imports and their original locations
- Document any import reorganization or refactoring applied

Goal: Clean, optimized import structure with zero unused imports and proper organization.""",
            "f841_unused_variables": """You are an expert Python code quality specialist focused on F841 unused local variable elimination:

**F841 UNUSED VARIABLE FIXES:**
1. **Detection**: Identify all local variables assigned but never used (F841 errors)
2. **Side Effect Preservation**: For assignments like `x = (
    func()`, determine if `func()` has side effects
)
3. **Intelligent Removal Strategy**:
   - Safe literals (numbers, strings, None) → Remove assignment entirely
   - Function/method calls with side effects → Keep call, remove assignment: `func()` instead of `x = (
       func()`
   )
   - Pure expressions without side effects → Comment out with explanation
   - Intentional placeholders → Rename to underscore: `_` or `_varname`

**SMART HANDLING PATTERNS:**
4. **Loop variables**: `for i, item in enumerate(lst): pass` → `for _, item in enumerate(lst): pass`
5. **Exception handling**: `except Exception as e: pass` → `except Exception: pass` (if e unused)
6. **Tuple unpacking**: `a, b, c = get_values()` → `a, _, c = get_values()` (if b unused)
7. **Debug variables**: `debug_info = (
    calculate_debug()` → `# debug_info = calculate_debug()  # F841: unused in production`
)

**VALIDATION & SAFETY:**
8. Preserve all function calls that modify state or have I/O operations
9. Ensure no functional changes to program behavior
10. Maintain code readability and developer intent
11. Test that removed variables don't break future code additions

**LOGGING:**
- Create /logs/f841_unused_variable_fixes.txt with detailed change log
- Document removal vs renaming decisions for each variable
- List preserved side-effect expressions

Goal: Clean codebase with zero F841 errors while preserving all intended functionality.""",
        }

        # Save prompts to configuration
        prompts_file = self.config_dir / "flake8_copilot_prompts.json"
        with open(prompts_file, "w", encoding="utf-8") as f:
            json.dump(prompts, f, indent=2, ensure_ascii=False)

        self.logger.info(f"💡 Generated Flake8 Copilot prompts: {prompts_file}")
        return prompts

    def generate_fix_report(
        self, initial_errors: dict, final_errors: dict, fixes_applied: dict
    ) -> dict:
        """Generate comprehensive fix report"""

        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "workspace": str(self.workspace),
            "initial_analysis": {
                "total_errors": sum(len(errors) for errors in initial_errors.values()),
                "error_categories": len(initial_errors),
                "category_breakdown": {cat: len(errors) for cat, errors in initial_errors.items()},
            },
            "fixes_applied": fixes_applied,
            "final_analysis": {
                "total_errors": sum(len(errors) for errors in final_errors.values()),
                "error_categories": len(final_errors),
                "category_breakdown": {cat: len(errors) for cat, errors in final_errors.items()},
            },
            "improvement_metrics": {
                "errors_reduced": (
                    sum(len(errors) for errors in initial_errors.values())
                    - sum(len(errors) for errors in final_errors.values())
                ),
                "categories_resolved": len(initial_errors) - len(final_errors),
                "fix_success_rate": 0,
            },
        }

        # Calculate success rate
        initial_total = report["initial_analysis"]["total_errors"]
        if initial_total > 0:
            errors_fixed = report["improvement_metrics"]["errors_reduced"]
            report["improvement_metrics"]["fix_success_rate"] = (
                errors_fixed / initial_total) * 100

        # Save report
        report_file = (
            self.log_dir /
            f"flake8_comprehensive_report_{
                datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"📊 Comprehensive fix report saved: {report_file}")
        return report

    def run_comprehensive_fix(self) -> dict:
        """Execute comprehensive Flake8 auto-fix process"""
        self.logger.info("🚀 Starting comprehensive Flake8 auto-fix process...")

        fix_results = {
            "timestamp": datetime.now(UTC).isoformat(),
            "workspace": str(self.workspace),
            "prerequisites_ok": False,
            "tools_installed": {},
            "initial_errors": {},
            "fixes_applied": {},
            "final_errors": {},
            "success": False,
            "errors": [],
        }

        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                fix_results["errors"].append("Prerequisites check failed")
                return fix_results
            fix_results["prerequisites_ok"] = True

            # Step 2: Install linting tools
            tools_status = self.install_linting_tools()
            fix_results["tools_installed"] = tools_status

            # Step 3: Initial analysis
            initial_errors, _ = self.run_flake8_analysis()
            fix_results["initial_errors"] = {
                cat: len(errors) for cat, errors in initial_errors.items()
            }

            if not initial_errors:
                self.logger.info("✅ No Flake8 issues found - code already compliant")
                fix_results["success"] = True
                return fix_results

            # Step 4: Apply comprehensive fixes
            self.logger.info("🛠️ Applying comprehensive auto-fixes...")

            # Apply autopep8 fixes
            autopep8_fixes = self.apply_autopep8_fixes()
            fix_results["fixes_applied"]["autopep8"] = autopep8_fixes

            # Apply Black formatting
            black_fixes = self.apply_black_formatting()
            fix_results["fixes_applied"]["black"] = black_fixes

            # Apply import sorting
            isort_fixes = self.apply_isort_imports()
            fix_results["fixes_applied"]["isort"] = isort_fixes

            # Step 5: Final analysis
            final_errors, _ = self.run_flake8_analysis()
            fix_results["final_errors"] = {
                cat: len(errors) for cat,
                errors in final_errors.items()}

            # Step 6: Generate comprehensive report
            report = self.generate_fix_report(
                initial_errors, final_errors, fix_results["fixes_applied"]
            )
            fix_results["report_file"] = str(report.get("report_file", ""))

            # Step 7: Generate Copilot prompts
            copilot_prompts = self.generate_copilot_prompts()
            fix_results["copilot_prompts"] = list(copilot_prompts.keys())

            # Determine success
            initial_count = sum(len(errors) for errors in initial_errors.values())
            final_count = sum(len(errors) for errors in final_errors.values())
            improvement = (((initial_count - final_count) /
                            initial_count * 100) if initial_count > 0 else 0)

            fix_results["success"] = improvement >= 80  # 80% improvement threshold

            self.logger.info("📊 Fix process completed:")
            self.logger.info(f"   Initial errors: {initial_count}")
            self.logger.info(f"   Final errors: {final_count}")
            self.logger.info(f"   Improvement: {improvement:.1f}%")

        except Exception as e:
            self.logger.error(f"❌ Comprehensive fix process failed: {e}")
            fix_results["errors"].append(str(e))

        return fix_results


def main():
    parser = argparse.ArgumentParser(
        description="EQ12 Flake8 Comprehensive Auto-Fix System")
    parser.add_argument(
        "--workspace",
        "-w",
        default=None,
        help="Workspace directory path")
    parser.add_argument(
        "--action",
        "-a",
        choices=[
            "analyze",
            "fix-e02",
            "fix-f84",
            "fix-comprehensive",
            "generate-prompts",
        ],
        default="fix-comprehensive",
        help="Action to perform",
    )
    parser.add_argument(
        "--categories",
        "-c",
        nargs="+",
        default=None,
        help="Specific error categories to fix (e.g., E02 E30 W29)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    fixer = EQ12Flake8AutoFixer(args.workspace)

    try:
        if args.action == "analyze":
            errors, _ = fixer.run_flake8_analysis()
            if errors:
                print(f"🔍 Found errors in {len(errors)} categories")
                for category, error_list in errors.items():
                    print(f"  {category}: {len(error_list)} errors")
            else:
                print("✅ No Flake8 errors found")

        elif args.action == "fix-e02":
            fixer.fix_specific_error_categories(["E02"])
            print("🔧 E02* spacing fixes applied")

        elif args.action == "fix-f84":
            fixer.fix_specific_error_categories(["F84"])
            print("🧹 F841 unused variable fixes applied")

        elif args.action == "generate-prompts":
            prompts = fixer.generate_copilot_prompts()
            print(f"💡 Generated {len(prompts)} Copilot prompts")

        elif args.action == "fix-comprehensive":
            results = fixer.run_comprehensive_fix()

            if results["success"]:
                print("✅ Comprehensive Flake8 fixes completed successfully")
            else:
                print("⚠️ Fix process completed with remaining issues")

            if results["errors"]:
                print(f"❌ Errors encountered: {results['errors']}")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
