#!/usr/bin/env python3
"""
EQ12 Focused Syntax Error Fixer
Fix syntax errors in core EQ12 Python files
"""

import ast
import logging
import re
import sys
from pathlib import Path


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    return logging.getLogger(__name__)


def fix_bom_encoding(file_path: Path) -> bool:
    """Fix BOM (Byte Order Mark) encoding issues"""
    try:
        with open(file_path, "rb") as f:
            content_bytes = f.read()

        # Check for BOM
        if content_bytes.startswith(b"\xef\xbb\xbf"):
            # Remove BOM and save as clean UTF-8
            content_clean = content_bytes[3:]  # Remove BOM
            with open(file_path, "wb") as f:
                f.write(content_clean)
            print("   ✅ Fixed BOM encoding in {file_path.name}")
            return True

        return False
    except Exception:
        print("   ❌ Error fixing BOM: {e}")
        return False


def fix_unterminated_string(file_path: Path, line_num: int) -> bool:
    """Fix unterminated string literals"""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        if line_num <= len(lines):
            target_line = lines[line_num - 1]

            # Look for common unterminated string patterns
            if target_line.count('"') % 2 == 1:  # Odd number of quotes
                # Add missing quote at end of line
                lines[line_num - 1] = target_line.rstrip() + '"\n'

                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                print("   ✅ Fixed unterminated string at line {line_num}")
                return True

        return False
    except Exception:
        print("   ❌ Error fixing string: {e}")
        return False


def fix_unclosed_parenthesis(file_path: Path, line_num: int) -> bool:
    """Fix unclosed parenthesis"""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        if line_num <= len(lines):
            # Look at the line and surrounding context
            start_idx = max(0, line_num - 3)
            end_idx = min(len(lines), line_num + 3)

            open_parens = 0
            for i in range(start_idx, end_idx):
                line = lines[i]
                open_parens += line.count("(") - line.count(")")

            if open_parens > 0:
                # Add missing closing parenthesis at end of problematic line
                lines[line_num - 1] = lines[line_num - 1].rstrip() + ")" * open_parens + "\n"

                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                print("   ✅ Fixed unclosed parenthesis at line {line_num}")
                return True

        return False
    except Exception:
        print("   ❌ Error fixing parenthesis: {e}")
        return False


def fix_invalid_syntax(file_path: Path, line_num: int) -> bool:
    """Try to fix common invalid syntax issues"""
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        if line_num <= len(lines):
            target_line = lines[line_num - 1]
            original_line = target_line

            # Common fixes
            # Fix common typing issues
            target_line = re.sub(r"from __future__ import annotations\s*\n", "", target_line)
            # Fix match statements (Python 3.10+ feature)
            if "match " in target_line and ":" in target_line:
                target_line = target_line.replace("match ", "if ")

            # Fix f-string issues
            if 'f"' in target_line or "f'" in target_line:
                # Check for malformed f-strings
                target_line = re.sub(r'f"([^{]*?)"', r'"\1"', target_line)
                target_line = re.sub(r"f'([^{]*?)'", r"'\1'", target_line)

            if target_line != original_line:
                lines[line_num - 1] = target_line

                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

                print("   ✅ Fixed syntax issue at line {line_num}")
                return True

        return False
    except Exception:
        print("   ❌ Error fixing syntax: {e}")
        return False


def main():
    """Main execution function"""
    setup_logging()

    # Core EQ12 files with syntax errors (excluding virtual env files)
    error_files = [
        ("cfb_dk_boost_optimizer.py", 704, "unterminated string"),
        ("eq12_copilot_triggers_fixed.py", 395, "unterminated string"),
        ("eq12_restore.py", 24, "unclosed parenthesis"),
        ("eq12_telegram_master_bot.py", 704, "invalid syntax"),
        ("eq12_vbnet_copilot_assistant.py", 289, "unterminated string"),
        ("launch_production.py", 332, "unexpected indent"),
        ("buffalo_stack/eq12_godmode_runner_plus.py", 269, "invalid syntax"),
        ("EdgeGodParlays/ai_betting_bot_stealth_final_flask_pro.py", 1, "BOM encoding"),
        ("EdgeGodParlays/sports_live.py", 1, "BOM encoding"),
        ("scripts/sports.py", 1, "BOM encoding"),
        (
            "generated_projects/EQ12SystemMonitor/eq12systemmonitor.py",
            40,
            "except/finally block",
        ),
        ("generated_projects/EQ12SystemMonitor/setup.py", 6, "unterminated string"),
        ("scraper_starter/tests/test_bookmarks_schema.py", 11, "unclosed parenthesis"),
        ("scraper_starter/tests/test_parsing.py", 42, "unclosed parenthesis"),
        ("scraper_starter/tests/test_vpn_check.py", 39, "unclosed parenthesis"),
    ]

    print("🔧 EQ12 FOCUSED SYNTAX ERROR FIXER")
    print("=" * 50)

    base_path = Path("C:/EQ12")
    fixes_applied = 0

    for file_rel_path, line_num, error_type in error_files:
        file_path = base_path / file_rel_path

        if not file_path.exists():
            print("⚠️  File not found: {file_rel_path}")
            continue

        print("\n🔧 Fixing: {file_rel_path} (Line {line_num}: {error_type})")

        fixed = False

        if error_type == "BOM encoding":
            fixed = fix_bom_encoding(file_path)
        elif error_type == "unterminated string":
            fixed = fix_unterminated_string(file_path, line_num)
        elif error_type == "unclosed parenthesis":
            fixed = fix_unclosed_parenthesis(file_path, line_num)
        elif error_type in [
            "invalid syntax",
            "unexpected indent",
            "except/finally block",
        ]:
            fixed = fix_invalid_syntax(file_path, line_num)

        if fixed:
            fixes_applied += 1

            # Verify the fix worked
            try:
                with open(file_path, encoding="utf-8") as f:
                    source = f.read()
                ast.parse(source, filename=str(file_path))
                print("   ✅ Syntax validation PASSED")
            except SyntaxError:
                print("   ⚠️  Syntax still has issues: Line {e.lineno}: {e.msg}")
            except Exception:
                print("   ⚠️  Validation error: {e}")

    print("\n🎉 SUMMARY: {fixes_applied}/{len(error_files)} files fixed")

    # Run a quick re-scan on the fixed files
    print("\n📊 RE-SCANNING FIXED FILES:")
    print("-" * 30)

    remaining_errors = 0
    for file_rel_path, line_num, error_type in error_files:
        file_path = base_path / file_rel_path

        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    source = f.read()
                ast.parse(source, filename=str(file_path))
                print("✅ {file_path.name}")
            except SyntaxError:
                print("❌ {file_path.name}: Line {e.lineno}: {e.msg}")
                remaining_errors += 1
            except Exception:
                print("❌ {file_path.name}: Parse error")
                remaining_errors += 1

    print(f"\n🎯 FINAL RESULT: {remaining_errors} syntax errors remaining in core files")

    return remaining_errors


if __name__ == "__main__":
    sys.exit(main())
