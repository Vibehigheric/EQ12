#!/usr/bin/env python3
"""
EQ12 System Issue Scanner and Fixer
Comprehensive scanning and automated fixing of Python/PowerShell issues

Features:
- Code quality analysis
- Import optimization
- Error handling improvements
- Performance optimizations
- Style fixes (PEP 8)
- Type hint corrections
"""

import ast
import logging
import re
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EQ12CodeScanner:
    """Advanced code scanner for EQ12 system issues"""

    def __init__(self, eq12_root: Path = Path("C:/EQ12")):
        self.eq12_root = eq12_root
        self.issues_found: dict[str, list[str]] = {}
        self.fixes_applied: dict[str, list[str]] = {}

    def scan_all_files(self) -> dict[str, Any]:
        """Scan all Python and PowerShell files for issues"""
        logger.info("🔍 Scanning EQ12 system for issues...")

        results = {
            "python_files": self.scan_python_files(),
            "powershell_files": self.scan_powershell_files(),
            "summary": {},
        }

        # Generate summary
        total_issues = sum(len(issues) for issues in self.issues_found.values())
        results["summary"] = {
            "total_files_scanned": len(self.issues_found),
            "total_issues_found": total_issues,
            "files_with_issues": len([f for f, issues in self.issues_found.items() if issues]),
        }

        logger.info(
            f"Scan completed: {total_issues} issues found in {len(self.issues_found)} files"
        )
        return results

    def scan_python_files(self) -> list[str]:
        """Scan Python files for common issues"""
        python_files = []

        for py_file in self.eq12_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            python_files.append(str(py_file))
            issues = self._analyze_python_file(py_file)

            if issues:
                self.issues_found[str(py_file)] = issues

        return python_files

    def scan_powershell_files(self) -> list[str]:
        """Scan PowerShell files for common issues"""
        powershell_files = []

        for ps_file in self.eq12_root.rglob("*.ps1"):
            if self._should_skip_file(ps_file):
                continue

            powershell_files.append(str(ps_file))
            issues = self._analyze_powershell_file(ps_file)

            if issues:
                self.issues_found[str(ps_file)] = issues

        return powershell_files

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during scanning"""
        skip_patterns = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "env",
            "build",
            "dist",
        }

        return any(pattern in str(file_path) for pattern in skip_patterns)

    def _analyze_python_file(self, file_path: Path) -> list[str]:
        """Analyze Python file for issues"""
        issues = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse AST for structural analysis
            try:
                tree = ast.parse(content)
                issues.extend(self._check_ast_issues(tree, content))
            except SyntaxError as e:
                issues.append(f"Syntax Error at line {e.lineno}: {e.msg}")

            # Check for common issues
            issues.extend(self._check_python_style_issues(content, file_path))
            issues.extend(self._check_import_issues(content))
            issues.extend(self._check_security_issues(content))

        except Exception as e:
            issues.append(f"Failed to analyze file: {e}")

        return issues

    def _analyze_powershell_file(self, file_path: Path) -> list[str]:
        """Analyze PowerShell file for issues"""
        issues = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Check PowerShell specific issues
            issues.extend(self._check_powershell_style_issues(content))
            issues.extend(self._check_powershell_security_issues(content))

        except Exception as e:
            issues.append(f"Failed to analyze PowerShell file: {e}")

        return issues

    def _check_ast_issues(self, tree: ast.AST, content: str) -> list[str]:
        """Check AST-based issues"""
        issues = []

        # Check for unused imports
        imports = []
        used_names = set()

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    import_name = alias.asname or alias.name
                    imports.append((import_name, node.lineno))

            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        # Find unused imports
        for import_name, line_no in imports:
            if import_name not in used_names and not import_name.startswith("_"):
                issues.append(f"Line {line_no}: Unused import '{import_name}'")

        # Check for missing type hints
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.returns and node.name not in (
                    "__init__",
                    "__str__",
                    "__repr__",
                ):
                    issues.append(
                        f"Line {node.lineno}: Function '{node.name}' missing return type hint"
                    )

        return issues

    def _check_python_style_issues(self, content: str, file_path: Path) -> list[str]:
        """Check Python style issues"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Line too long
            if len(line) > 79:
                issues.append(f"Line {i}: Line too long ({len(line)} > 79 characters)")

            # Trailing whitespace
            if line.rstrip() != line:
                issues.append(f"Line {i}: Trailing whitespace")

            # Missing docstring for classes/functions
            if line.strip().startswith(("def ", "class ")) and i < len(lines):
                next_line = lines[i] if i < len(lines) else ""
                if not next_line.strip().startswith('"""') and not next_line.strip().startswith(
                    "'''"
                ):
                    func_name = line.split("(")[0].split()[-1]
                    if not func_name.startswith("_"):
                        issues.append(f"Line {i}: Missing docstring for '{func_name}'")

        return issues

    def _check_import_issues(self, content: str) -> list[str]:
        """Check import-related issues"""
        issues = []
        lines = content.split("\n")

        import_lines = []
        for i, line in enumerate(lines, 1):
            if line.strip().startswith(("import ", "from ")):
                import_lines.append((i, line.strip()))

        # Check import organization
        if len(import_lines) > 1:
            stdlib_imports = []
            third_party_imports = []
            local_imports = []

            for line_no, import_line in import_lines:
                if "from ." in import_line or import_line.startswith("from eq12"):
                    local_imports.append(line_no)
                elif any(
                    lib in import_line for lib in ["os", "sys", "json", "logging", "datetime"]
                ):
                    stdlib_imports.append(line_no)
                else:
                    third_party_imports.append(line_no)

            # Check if imports are not properly grouped
            all_imports = stdlib_imports + third_party_imports + local_imports
            if import_lines and all_imports != sorted([line[0] for line in import_lines]):
                issues.append(
                    "Imports not properly organized (should be: stdlib, third-party, local)"
                )

        return issues

    def _check_security_issues(self, content: str) -> list[str]:
        """Check for security issues"""
        issues = []

        security_patterns = [
            (r"eval\s*\(", "Use of eval() is dangerous"),
            (r"exec\s*\(", "Use of exec() is dangerous"),
            (r"shell=True", "shell=True in subprocess calls is risky"),
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
        ]

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern, message in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(f"Line {i}: Security issue - {message}")

        return issues

    def _check_powershell_style_issues(self, content: str) -> list[str]:
        """Check PowerShell style issues"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for proper parameter declaration
            if line.strip().startswith("param(") and "CmdletBinding" not in content:
                issues.append(f"Line {i}: Missing [CmdletBinding()] attribute")

            # Check for error handling
            if "Invoke-" in line and "try" not in content.lower():
                issues.append(f"Line {i}: Missing error handling for Invoke command")

            # Check for hardcoded paths
            if re.search(r'[A-Z]:\\[^"\']+', line) and not line.strip().startswith("#"):
                issues.append(f"Line {i}: Hardcoded path detected - consider using variables")

        return issues

    def _check_powershell_security_issues(self, content: str) -> list[str]:
        """Check PowerShell security issues"""
        issues = []

        security_patterns = [
            (r"-ExecutionPolicy\s+Bypass", "ExecutionPolicy Bypass detected"),
            (r"Invoke-Expression", "Invoke-Expression usage detected"),
            (r"DownloadString", "DownloadString usage detected"),
            (r'password.*=.*["\'][^"\']+["\']', "Hardcoded password detected"),
        ]

        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern, message in security_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(f"Line {i}: Security issue - {message}")

        return issues

    def fix_common_issues(self) -> dict[str, list[str]]:
        """Apply automated fixes for common issues"""
        logger.info("🔧 Applying automated fixes...")

        for file_path, issues in self.issues_found.items():
            if file_path.endswith(".py"):
                fixes = self._fix_python_file(Path(file_path), issues)
                if fixes:
                    self.fixes_applied[file_path] = fixes

        return self.fixes_applied

    def _fix_python_file(self, file_path: Path, issues: list[str]) -> list[str]:
        """Apply fixes to Python file"""
        fixes_applied = []

        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            modified_content = original_content

            # Fix trailing whitespace
            if any("Trailing whitespace" in issue for issue in issues):
                lines = modified_content.split("\n")
                lines = [line.rstrip() for line in lines]
                modified_content = "\n".join(lines)
                fixes_applied.append("Removed trailing whitespace")

            # Fix f-string issues
            modified_content = re.sub(r'print\(f"([^{]*)"\)', r'print("\1")', modified_content)
            if modified_content != original_content:
                fixes_applied.append("Fixed f-string without placeholders")

            # Write back if changes were made
            if fixes_applied:
                # Create backup
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(original_content)

                # Write fixed version
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)

                logger.info(f"Fixed {len(fixes_applied)} issues in {file_path.name}")

        except Exception as e:
            logger.error(f"Failed to fix {file_path}: {e}")

        return fixes_applied

    def generate_report(self) -> str:
        """Generate comprehensive issue report"""
        report = []
        report.append("# EQ12 System Issue Report")
        report.append("=" * 50)
        report.append("")

        # Summary
        total_issues = sum(len(issues) for issues in self.issues_found.values())
        report.append(f"**Total Issues Found:** {total_issues}")
        report.append(f"**Files Scanned:** {len(self.issues_found)}")
        report.append(
            f"**Files with Issues:** {len([f for f, issues in self.issues_found.items() if issues])}"
        )
        report.append("")

        # Issues by file
        if self.issues_found:
            report.append("## Issues by File")
            report.append("")

            for file_path, issues in self.issues_found.items():
                if issues:
                    report.append(f"### {Path(file_path).name}")
                    report.append(f"Path: `{file_path}`")
                    report.append("")
                    for issue in issues:
                        report.append(f"- {issue}")
                    report.append("")

        # Fixes applied
        if self.fixes_applied:
            report.append("## Automated Fixes Applied")
            report.append("")

            for file_path, fixes in self.fixes_applied.items():
                report.append(f"### {Path(file_path).name}")
                for fix in fixes:
                    report.append(f"- ✅ {fix}")
                report.append("")

        # Recommendations
        report.append("## Recommendations")
        report.append("")
        report.append("1. **Code Quality:** Install and configure `black` for Python formatting")
        report.append("2. **Type Safety:** Add comprehensive type hints to all functions")
        report.append("3. **Security:** Review hardcoded credentials and paths")
        report.append("4. **Performance:** Consider using async/await for I/O operations")
        report.append("5. **Documentation:** Add docstrings to all public functions and classes")

        return "\n".join(report)


def main():
    """Main scanner execution"""
    logger.info("🚀 Starting EQ12 System Issue Scanner")

    scanner = EQ12CodeScanner()

    # Scan for issues
    scan_results = scanner.scan_all_files()

    # Apply fixes
    if scanner.issues_found:
        fixes = scanner.fix_common_issues()
        logger.info(f"Applied fixes to {len(fixes)} files")

    # Generate report
    report_content = scanner.generate_report()

    # Save report
    report_path = Path("C:/EQ12/logs/system_issues_report.md")
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.info(f"📊 Issue report saved to: {report_path}")

    # Print summary
    summary = scan_results["summary"]
    print(
        f"""
🔍 EQ12 System Scan Complete
============================
Files Scanned: {summary["total_files_scanned"]}
Issues Found: {summary["total_issues_found"]}
Files with Issues: {summary["files_with_issues"]}
Fixes Applied: {len(scanner.fixes_applied)}

📊 Full report: {report_path}
    """
    )


if __name__ == "__main__":
    main()
