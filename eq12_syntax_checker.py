#!/usr/bin/env python3
"""
EQ12 Syntax Error Scanner and Fixer
Scans Python files for syntax errors and provides fixes
"""

import ast
import logging
import sys
from pathlib import Path


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("C:/EQ12/logs/syntax_checker.log"),
        ],
    )
    return logging.getLogger(__name__)


def check_python_syntax(file_path: Path) -> tuple[bool, str]:
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()

        # Try to parse the AST
        ast.parse(source, filename=str(file_path))
        return True, "Syntax OK"

    except SyntaxError as e:
        error_msg = f"Line {e.lineno}: {e.msg}"
        return False, error_msg

    except UnicodeDecodeError:
        return False, "Unicode decode error - file encoding issue"

    except Exception as e:
        return False, f"Parse error: {e!s}"


def scan_directory(base_path: Path) -> dict[str, list[tuple[Path, str]]]:
    """Scan directory for Python files with syntax errors"""
    logger = logging.getLogger(__name__)
    results = {"valid": [], "errors": [], "skipped": []}

    python_files = list(base_path.rglob("*.py"))
    logger.info(f"Found {len(python_files)} Python files to check")

    for py_file in python_files:
        # Skip virtual environment files
        if ".venv" in str(py_file) or "__pycache__" in str(py_file):
            results["skipped"].append((py_file, "Virtual environment file"))
            continue

        is_valid, message = check_python_syntax(py_file)

        if is_valid:
            results["valid"].append((py_file, message))
        else:
            results["errors"].append((py_file, message))
            logger.warning(f"SYNTAX ERROR in {py_file}: {message}")

    return results


def main():
    """Main execution function"""
    logger = setup_logging()
    logger.info("🔍 EQ12 Python Syntax Error Scanner Starting")

    # Scan the EQ12 directory
    base_path = Path("C:/EQ12")
    if not base_path.exists():
        logger.error("EQ12 directory not found!")
        return 1

    results = scan_directory(base_path)

    # Print summary
    print("\n" + "=" * 60)
    print("📊 EQ12 PYTHON SYNTAX SCAN RESULTS")
    print("=" * 60)

    print(f"✅ Valid files: {len(results['valid'])}")
    print(f"❌ Files with errors: {len(results['errors'])}")
    print(f"⏭️  Skipped files: {len(results['skipped'])}")

    if results["errors"]:
        print("\n🚨 FILES WITH SYNTAX ERRORS:")
        print("-" * 40)
        for file_path, error_msg in results["errors"]:
            rel_path = file_path.relative_to(base_path)
            print(f"📁 {rel_path}")
            print(f"   ❌ {error_msg}")
            print()

        # Try to fix common issues
        print("🔧 ATTEMPTING AUTOMATIC FIXES:")
        print("-" * 40)
        for file_path, error_msg in results["errors"]:
            if "invalid character" in error_msg.lower():
                print(f"🔧 Fixing encoding issues in {file_path.name}")
                fix_encoding_issues(file_path)
            elif "unexpected indent" in error_msg.lower():
                print(f"🔧 Fixing indentation in {file_path.name}")
                fix_indentation_issues(file_path)

    else:
        print("\n🎉 All Python files have valid syntax!")

    logger.info("Syntax scan complete")
    return 0 if not results["errors"] else 1


def fix_encoding_issues(file_path: Path):
    """Attempt to fix common encoding issues"""
    try:
        # Try reading with different encodings
        for encoding in ["utf-8", "latin-1", "cp1252"]:
            try:
                with open(file_path, encoding=encoding) as f:
                    content = f.read()

                # Write back as UTF-8
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"   ✅ Fixed encoding: {encoding} -> utf-8")
                return

            except UnicodeDecodeError:
                continue

        print(f"   ❌ Could not fix encoding for {file_path.name}")

    except Exception as e:
        print(f"   ❌ Error fixing encoding: {e}")


def fix_indentation_issues(file_path: Path):
    """Attempt to fix common indentation issues"""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        # Convert tabs to spaces
        fixed_lines = []
        for line in lines:
            # Replace tabs with 4 spaces
            fixed_line = line.expandtabs(4)
            fixed_lines.append(fixed_line)

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(fixed_lines)

        print("   ✅ Fixed indentation (tabs -> spaces)")

    except Exception as e:
        print(f"   ❌ Error fixing indentation: {e}")


if __name__ == "__main__":
    sys.exit(main())
