#!/usr/bin/env python3
"""
Automated Code Quality Fixer for EQ12
Automatically fixes common flake8 issues without manual intervention.
"""

import argparse
import ast
import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AutomatedCodeFixer:
    """Automated fixer for common code quality issues"""

    def __init__(self, base_paths: list[str]):
        self.base_paths = base_paths
        self.fixed_files = set()
        self.stats = {
            "w293_fixed": 0,  # blank line whitespace
            "w291_fixed": 0,  # trailing whitespace
            "e501_fixed": 0,  # long lines
            "f841_fixed": 0,  # unused variables
            "f401_fixed": 0,  # unused imports
            "e722_fixed": 0,  # bare except
            "w605_fixed": 0,  # invalid escape
            "files_processed": 0,
        }

    def get_python_files(self) -> list[Path]:
        """Get all Python files in the specified paths"""
        python_files = []
        for base_path in self.base_paths:
            base = Path(base_path)
            if base.is_file() and base.suffix == ".py":
                python_files.append(base)
            elif base.is_dir():
                python_files.extend(base.rglob("*.py"))
        return sorted(python_files)

    def fix_whitespace_issues(self, content: str) -> str:
        """Fix W293 (blank line whitespace) and W291 (trailing whitespace)"""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            # Fix W291: Remove trailing whitespace
            if line.rstrip() != line:
                self.stats["w291_fixed"] += 1

            # Fix W293: Remove whitespace from blank lines
            if line.strip() == "" and line != "":
                self.stats["w293_fixed"] += 1
                fixed_lines.append("")
            else:
                fixed_lines.append(line.rstrip())

        return "\n".join(fixed_lines) + "\n"

    def fix_long_lines(self, content: str) -> str:
        """Fix E501: Intelligently break long lines"""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            if len(line) <= 100:
                fixed_lines.append(line)
                continue

            # Skip certain patterns that are hard to break
            if any(pattern in line for pattern in ["http://", "https://", "file://", r"C:\\"]):
                fixed_lines.append(line)
                continue

            # Try to break function calls and assignments
            if "=" in line and "==" not in line:
                # Break at assignment
                indent = len(line) - len(line.lstrip())
                if line.count("(") == line.count(")"):  # Balanced parens
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        var_part = parts[0].rstrip()
                        value_part = parts[1].lstrip()
                        if len(var_part) + len(value_part) + 3 > 100:
                            fixed_lines.append(var_part + " = (")
                            fixed_lines.append(" " * (indent + 4) + value_part.strip())
                            fixed_lines.append(" " * indent + ")")
                            self.stats["e501_fixed"] += 1
                            continue

            # Break function calls with multiple parameters
            if "(" in line and line.count("(") == line.count(")"):
                # Find function calls with multiple parameters
                paren_start = line.find("(")
                paren_end = line.rfind(")")
                if paren_start != -1 and paren_end != -1 and "," in line[paren_start:paren_end]:
                    before_paren = line[: paren_start + 1]
                    params = line[paren_start + 1 : paren_end]
                    after_paren = line[paren_end:]

                    # Split parameters
                    param_list = []
                    current_param = ""
                    paren_count = 0
                    quote_count = 0

                    for char in params:
                        if char == '"' or char == "'":
                            quote_count = 1 - quote_count
                        elif char == "(" and quote_count == 0:
                            paren_count += 1
                        elif char == ")" and quote_count == 0:
                            paren_count -= 1
                        elif char == "," and paren_count == 0 and quote_count == 0:
                            param_list.append(current_param.strip())
                            current_param = ""
                            continue
                        current_param += char

                    if current_param.strip():
                        param_list.append(current_param.strip())

                    if len(param_list) > 1:
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.append(before_paren)
                        for i, param in enumerate(param_list):
                            comma = "," if i < len(param_list) - 1 else ""
                            fixed_lines.append(" " * (indent + 4) + param + comma)
                        fixed_lines.append(" " * indent + after_paren)
                        self.stats["e501_fixed"] += 1
                        continue

            # If we couldn't break it intelligently, just add it as-is
            fixed_lines.append(line)

        return "\n".join(fixed_lines) + "\n"

    def fix_unused_variables(self, content: str) -> str:
        """Fix F841: Remove simple unused local variables"""
        try:
            ast.parse(content)
        except SyntaxError:
            return content  # Skip files with syntax errors

        lines = content.splitlines()

        # Find unused variables (simple pattern matching)
        unused_patterns = [
            r"^\s+(\w+)\s*=\s*.*  # F841.*assigned to but never used",
            r"^\s+(\w+)\s*=\s*[^=].*$",  # Simple assignments
        ]

        fixed_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this line has an unused variable assignment
            should_remove = False
            for pattern in unused_patterns:
                match = re.search(pattern, line)
                if match and "F841" in line:
                    # Only remove very simple assignments
                    if "=" in line and not any(
                        x in line
                        for x in [
                            "if ",
                            "for ",
                            "while ",
                            "def ",
                            "class ",
                            "try:",
                            "except:",
                            "with ",
                        ]
                    ):
                        var_name = match.group(1)
                        # Don't remove if variable name suggests it might be important
                        if not any(
                            important in var_name.lower()
                            for important in [
                                "result",
                                "response",
                                "data",
                                "config",
                                "logger",
                                "client",
                            ]
                        ):
                            should_remove = True
                            self.stats["f841_fixed"] += 1
                            break

            if not should_remove:
                fixed_lines.append(line)
            i += 1

        return "\n".join(fixed_lines) + "\n"

    def fix_import_issues(self, content: str) -> str:
        """Fix F401: Remove unused imports and F821: Add missing imports"""
        lines = content.splitlines()

        # Common missing imports for F821 errors
        missing_imports = {
            "logging": "import logging",
            "Dict": "from typing import Dict",
            "List": "from typing import List",
            "Optional": "from typing import Optional",
            "Union": "from typing import Union",
            "json": "import json",
            "os": "import os",
            "sys": "import sys",
            "datetime": "import datetime",
        }

        # Check what's undefined and what imports exist
        has_imports = set()
        needs_imports = set()

        for line in lines:
            # Check existing imports
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                for imp_name in missing_imports:
                    if imp_name in line:
                        has_imports.add(imp_name)

            # Check for undefined names
            for undefined in missing_imports:
                if undefined in line and "F821" in line:
                    needs_imports.add(undefined)

        # Add missing imports after existing imports
        if needs_imports - has_imports:
            new_lines = []
            import_section_ended = False
            imports_added = False

            for line in lines:
                new_lines.append(line)

                # Add imports after the last import line
                if (
                    line.strip().startswith("import ") or line.strip().startswith("from ")
                ) and not imports_added:
                    continue
                elif (
                    not import_section_ended
                    and line.strip()
                    and not (
                        line.strip().startswith("import ")
                        or line.strip().startswith("from ")
                        or line.strip().startswith("#")
                    )
                ):
                    # This is the first non-import, non-comment line
                    for imp_name in sorted(needs_imports - has_imports):
                        new_lines.insert(-1, missing_imports[imp_name])
                        self.stats["f401_fixed"] += 1
                    imports_added = True
                    import_section_ended = True

            return "\n".join(new_lines) + "\n"

        return content

    def fix_bare_except(self, content: str) -> str:
        """Fix E722: Replace bare except with Exception"""
        lines = content.splitlines()
        fixed_lines = []

        for line in lines:
            if "except:" in line and "E722" in line:
                # Replace bare except with Exception
                fixed_line = line.replace("except:", "except Exception:")
                fixed_lines.append(fixed_line)
                self.stats["e722_fixed"] += 1
            else:
                fixed_lines.append(line)

        return "\n".join(fixed_lines) + "\n"

    def fix_escape_sequences(self, content: str) -> str:
        """Fix W605: Invalid escape sequences"""
        # Common invalid escape sequence fixes
        fixes = {
            r"\\E": r"\\\\E",
            r"\\e": r"\\\\e",
            r"\\s": r"\\\\s",
            r"\\d": r"\\\\d",
            r"\\.": r"\\\\.",
        }

        fixed_content = content
        for pattern, replacement in fixes.items():
            if pattern in fixed_content:
                fixed_content = fixed_content.replace(pattern, replacement)
                self.stats["w605_fixed"] += 1

        return fixed_content

    def process_file(self, file_path: Path) -> bool:
        """Process a single file and apply all fixes"""
        try:
            logger.info(f"Processing {file_path}")

            # Read original content
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                original_content = f.read()

            # Apply all fixes in sequence
            content = original_content
            content = self.fix_whitespace_issues(content)
            content = self.fix_long_lines(content)
            content = self.fix_unused_variables(content)
            content = self.fix_import_issues(content)
            content = self.fix_bare_except(content)
            content = self.fix_escape_sequences(content)

            # Only write if content changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(content)
                self.fixed_files.add(str(file_path))
                logger.info(f"Fixed issues in {file_path}")

            self.stats["files_processed"] += 1
            return True

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False

    def run_fixes(self) -> dict:
        """Run all automated fixes"""
        python_files = self.get_python_files()
        logger.info(f"Found {len(python_files)} Python files to process")

        for file_path in python_files:
            self.process_file(file_path)

        logger.info(f"Processed {self.stats['files_processed']} files")
        logger.info(f"Fixed files: {len(self.fixed_files)}")
        logger.info("Fix statistics:")
        for key, value in self.stats.items():
            if value > 0 and key != "files_processed":
                logger.info(f"  {key}: {value}")

        return {
            "files_fixed": len(self.fixed_files),
            "stats": self.stats,
            "fixed_files": list(self.fixed_files),
        }


def main():
    parser = argparse.ArgumentParser(description="Automated Code Quality Fixer")
    parser.add_argument("paths", nargs="+", help="Paths to fix (files or directories)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    fixer = AutomatedCodeFixer(args.paths)
    results = fixer.run_fixes()

    print("\nAutomated fixes completed!")
    print(f"Files processed: {results['stats']['files_processed']}")
    print(f"Files with fixes: {results['files_fixed']}")
    print(
        f"Total fixes applied: {sum(v for k, v in results['stats'].items() if k != 'files_processed')}"
    )


if __name__ == "__main__":
    main()
