#!/usr/bin/env python3
"""
EQ12 F541 F-string Auto-Fix Script

This script automatically fixes F541 violations (f-strings missing placeholders)
by converting f"string" to "string" when no variables are used.
"""

import argparse
import logging
import re
import sys


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=level)


def get_f541_violations() -> list[tuple[str, int]]:
    """Get all F541 violations using flake8."""
    import subprocess

    try:
        result = subprocess.run(
            [
                "python",
                "-m",
                "flake8",
                "C:\\EQ12\\scripts\\",
                "C:\\EQ12\\tests\\",
                "--select=F541",
                "--max-line-length=100",
            ],
            capture_output=True,
            text=True,
            cwd="C:\\EQ12",
        )

        violations = []
        for line in result.stdout.strip().split("\n"):
            if line and "F541" in line and line.strip():
                # Parse: filepath:line:col: F541 message
                # Split on ':' but be careful with Windows paths containing ':'
                if ":\\" in line:  # Windows path
                    # Find the path part (everything up to the second colon)
                    colon_indices = [i for i, c in enumerate(line) if c == ":"]
                    if len(colon_indices) >= 3:  # C:\path:line:col format
                        filepath = line[: colon_indices[2]]
                        remaining = line[colon_indices[2] + 1 :]
                        parts = remaining.split(":")
                        if len(parts) >= 1:
                            try:
                                line_num = int(parts[0])
                                violations.append((filepath, line_num))
                            except ValueError:
                                logging.debug(f"Could not parse line number from: {line}")

        return violations
    except Exception as e:
        logging.error(f"Error getting F541 violations: {e}")
        return []


def fix_f541_in_line(line: str) -> tuple[str, bool]:
    """
    Fix F541 violations in a single line by removing f prefix from strings
    that don't contain placeholder expressions.

    Returns (fixed_line, was_modified)
    """
    modified = False

    # Pattern to match f-strings: f"..." or f'...'
    # This regex looks for f followed by quotes, captures the string content,
    # and checks if there are no {} placeholder expressions

    def fix_fstring(match):
        nonlocal modified
        quote_char = match.group(1)  # " or '
        string_content = match.group(2)

        # Check if string contains any {} expressions
        # Simple check: if no { or } characters, it's safe to remove f
        if "{" not in string_content and "}" not in string_content:
            modified = True
            return f"{quote_char}{string_content}{quote_char}"
        return match.group(0)  # Return unchanged if it has placeholders

    # Match f"..." or f'...' patterns
    # This handles both single and double quotes
    patterns = [
        r'f(["\'])((?:[^"\'\\]|\\.)*)(["\'])',  # f"string" or f'string'
    ]

    for pattern in patterns:
        line = re.sub(pattern, fix_fstring, line)

    return line, modified


def fix_file_f541_issues(filepath: str, line_numbers: list[int]) -> int:
    """
    Fix F541 issues in a specific file for given line numbers.
    Returns the number of lines modified.
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()

        modifications = 0
        line_numbers_set = set(line_numbers)

        for i, line in enumerate(lines):
            line_num = i + 1
            if line_num in line_numbers_set:
                fixed_line, was_modified = fix_f541_in_line(line)
                if was_modified:
                    lines[i] = fixed_line
                    modifications += 1
                    logging.debug(f"Fixed line {line_num} in {filepath}")

        if modifications > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(lines)
            logging.info(f"Fixed {modifications} F541 issues in {filepath}")

        return modifications

    except Exception as e:
        logging.error(f"Error fixing {filepath}: {e}")
        return 0


def main():
    """Main function to fix all F541 violations."""
    parser = argparse.ArgumentParser(description="Fix F541 f-string violations")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be fixed without making changes",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    logging.info("Starting F541 f-string fix process...")

    # Get all F541 violations
    violations = get_f541_violations()
    if not violations:
        logging.info("No F541 violations found!")
        return 0

    logging.info(f"Found {len(violations)} F541 violations to fix")

    # Group violations by file
    files_to_fix = {}
    for filepath, line_num in violations:
        if filepath not in files_to_fix:
            files_to_fix[filepath] = []
        files_to_fix[filepath].append(line_num)

    total_modifications = 0

    if args.dry_run:
        logging.info("DRY RUN - showing what would be fixed:")
        for filepath, line_numbers in files_to_fix.items():
            logging.info(f"Would fix {len(line_numbers)} lines in {filepath}")
    else:
        # Fix each file
        for filepath, line_numbers in files_to_fix.items():
            modifications = fix_file_f541_issues(filepath, line_numbers)
            total_modifications += modifications

    if not args.dry_run:
        logging.info(
            f"Successfully fixed {total_modifications} F541 violations across {len(files_to_fix)} files"
        )

        # Verify by running flake8 again
        remaining_violations = get_f541_violations()
        logging.info(f"Remaining F541 violations: {len(remaining_violations)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
