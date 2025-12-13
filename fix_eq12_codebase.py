#!/usr/bin/env python3
"""
EQ12 Codebase Improvement Script
Automatically fixes common Python issues across the EQ12 codebase
"""

import ast
import logging
import pathlib
import re
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EQ12CodeFixer:
    """Automated code improvement for EQ12 Python files"""

    def __init__(self, root_dir: pathlib.Path) -> bool:
        self.root_dir = root_dir
        self.fixed_files: list[str] = []
        self.issues_found: dict[str, list[str]] = {}

    def find_python_files(self) -> list[pathlib.Path]:
        """Find all Python files in the project"""
        python_files = []
        for pattern in ["**/*.py"]:
            python_files.extend(self.root_dir.glob(pattern))

        # Exclude virtual environments and .git directories
        excluded_patterns = [".venv", "venv", ".git", "__pycache__", ".pytest_cache"]
        filtered_files = []

        for file_path in python_files:
            exclude = False
            for pattern in excluded_patterns:
                if pattern in str(file_path):
                    exclude = True
                    break
            if not exclude:
                filtered_files.append(file_path)

        return filtered_files

    def fix_print_statements(self, content: str, file_path: pathlib.Path) -> tuple[str, list[str]]:
        """Convert print() statements to proper logging where appropriate"""
        changes = []
        lines = content.split("\n")
        modified_lines = []
        needs_logging_import = False
        has_logging_import = "import logging" in content or "from logging import" in content

        for i, line in enumerate(lines):

            # Skip lines that are clearly for user interaction or output formatting
            if any(
                keyword in line.lower()
                for keyword in [
                    "input(",
                    "json.dumps(",
                    "# print",
                    "print(json",
                    "return print",
                ]
            ):
                modified_lines.append(line)
                continue

            # Look for print statements that should be logging
            if re.search(r"^\s*print\s*\(.*\)", line) and not any(
                x in line for x in ['"', "'", "f'", 'f"']
            ):
                # Simple print statement without formatting - convert to logging
                indent = len(line) - len(line.lstrip())
                message_match = re.search(r"print\s*\(\s*(.+?)\s*\)", line)
                if message_match:
                    message = message_match.group(1)
                    # Determine appropriate logging level
                    if any(keyword in line.lower() for keyword in ["error", "failed", "exception"]):
                        new_line = " " * indent + f"logger.error({message})"
                    elif any(keyword in line.lower() for keyword in ["warn", "warning"]):
                        new_line = " " * indent + f"logger.warning({message})"
                    elif any(keyword in line.lower() for keyword in ["debug"]):
                        new_line = " " * indent + f"logger.debug({message})"
                    else:
                        new_line = " " * indent + f"logger.info({message})"

                    modified_lines.append(new_line)
                    changes.append(f"Line {i + 1}: Converted print to logging")
                    needs_logging_import = True
                    continue

            modified_lines.append(line)

        # Add logging import if needed
        if needs_logging_import and not has_logging_import:
            # Find the right place to insert logging import
            import_lines = []
            other_lines = []
            in_imports = True

            for line in modified_lines:
                if line.strip().startswith(("import ", "from ")) and in_imports:
                    import_lines.append(line)
                else:
                    if line.strip() and not line.startswith("#"):
                        in_imports = False
                    other_lines.append(line)

            # Insert logging import
            import_lines.append("import logging")
            import_lines.append("")
            import_lines.append("# Set up logging")
            import_lines.append("logger = logging.getLogger(__name__)")

            modified_lines = import_lines + other_lines
            changes.append("Added logging import and logger setup")

        return "\n".join(modified_lines), changes

    def add_type_hints(self, content: str, file_path: pathlib.Path) -> tuple[str, list[str]]:
        """Add basic type hints to function definitions"""
        changes = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return content, ["Could not parse file for type hint analysis"]

        lines = content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip if function already has type hints
                if node.returns is not None:
                    continue

                func_line_idx = node.lineno - 1
                if func_line_idx < len(lines):
                    func_line = lines[func_line_idx]

                    # Simple heuristics for return type
                    if "return True" in content or "return False" in content:
                        if ") -> bool:" not in func_line:
                            lines[func_line_idx] = func_line.replace("):", ") -> bool:")
                            changes.append(f"Added bool return type to {node.name}")
                    elif (
                        "return None" in content
                        or not any(
                            "return " in line for line in content.split("\n")[func_line_idx:]
                        )
                    ) and ") -> None:" not in func_line:
                        lines[func_line_idx] = func_line.replace("):", ") -> None:")
                        changes.append(f"Added None return type to {node.name}")

        return "\n".join(lines), changes

    def fix_import_order(self, content: str, file_path: pathlib.Path) -> tuple[str, list[str]]:
        """Fix import statement ordering (stdlib, third-party, local)"""
        changes = []
        lines = content.split("\n")

        # Find import section
        import_lines = []
        other_lines = []
        stdlib_imports = []
        third_party_imports = []
        local_imports = []

        in_imports = True

        for i, line in enumerate(lines):
            if line.strip().startswith(("import ", "from ")) and in_imports:
                import_lines.append((i, line))
            else:
                if line.strip() and not line.startswith("#"):
                    in_imports = False
                other_lines.append((i, line))

        # Categorize imports (simplified)
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "time",
            "datetime",
            "pathlib",
            "subprocess",
            "logging",
            "argparse",
            "typing",
            "collections",
            "re",
            "urllib",
        }

        for i, line in import_lines:
            if any(f"import {mod}" in line or f"from {mod}" in line for mod in stdlib_modules):
                stdlib_imports.append(line)
            elif line.strip().startswith("from .") or line.strip().startswith("from eq12"):
                local_imports.append(line)
            else:
                third_party_imports.append(line)

        if len(import_lines) > 1:  # Only reorganize if there are multiple imports
            # Reorganize imports
            new_import_section = []
            if stdlib_imports:
                new_import_section.extend(stdlib_imports)
                new_import_section.append("")
            if third_party_imports:
                new_import_section.extend(third_party_imports)
                new_import_section.append("")
            if local_imports:
                new_import_section.extend(local_imports)
                new_import_section.append("")

            # Rebuild content
            non_import_lines = [line for i, line in other_lines]
            new_content = "\n".join(new_import_section + non_import_lines)

            if new_content != content:
                changes.append("Reorganized import statements")
                return new_content, changes

        return content, changes

    def fix_file(self, file_path: pathlib.Path) -> bool:
        """Fix issues in a single Python file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            content = original_content
            all_changes = []

            # Apply fixes
            content, changes = self.fix_import_order(content, file_path)
            all_changes.extend(changes)

            content, changes = self.add_type_hints(content, file_path)
            all_changes.extend(changes)

            # Only apply print->logging fix to specific files to avoid breaking output
            if not any(name in str(file_path) for name in ["template", "test_", "conftest"]):
                content, changes = self.fix_print_statements(content, file_path)
                all_changes.extend(changes)

            # Write back if changes were made
            if all_changes and content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.fixed_files.append(str(file_path))
                self.issues_found[str(file_path)] = all_changes
                logger.info(f"Fixed {len(all_changes)} issues in {file_path}")
                return True

        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False

        return False

    def run_fixes(self) -> dict[str, any]:
        """Run all fixes across the codebase"""
        python_files = self.find_python_files()
        logger.info(f"Found {len(python_files)} Python files to analyze")

        fixed_count = 0
        for file_path in python_files:
            if self.fix_file(file_path):
                fixed_count += 1

        return {
            "total_files": len(python_files),
            "files_fixed": fixed_count,
            "fixed_files": self.fixed_files,
            "issues_found": self.issues_found,
        }


def main() -> bool:
    """Main execution function"""
    eq12_root = pathlib.Path(__file__).parent

    logger.info("Starting EQ12 codebase improvement...")
    logger.info(f"Working directory: {eq12_root}")

    fixer = EQ12CodeFixer(eq12_root)
    results = fixer.run_fixes()

    logger.info("\n" + "=" * 60)
    logger.info("EQ12 CODEBASE IMPROVEMENT SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total Python files analyzed: {results['total_files']}")
    logger.info(f"Files with fixes applied: {results['files_fixed']}")

    if results["fixed_files"]:
        logger.info("\nFiles modified:")
        for file_path in results["fixed_files"]:
            logger.info(f"  ✅ {file_path}")
            for issue in results["issues_found"][file_path]:
                logger.info(f"     - {issue}")
    else:
        logger.info("\n✨ No issues found or all files already optimized!")

    logger.info("\nEQ12 codebase improvement completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
