"""
EQ12 UNICODE INTEGRATION PATCHER
================================
Automatically adds Unicode protection to all EQ12 Python scripts.
This patches existing scripts to use Unicode-safe operations.

Usage:
    python eq12_unicode_patcher.py --patch-all
    python eq12_unicode_patcher.py --verify
    python eq12_unicode_patcher.py --list-files
"""

import argparse
import re
from pathlib import Path

from eq12_unicode_simple import safe_print

# List of EQ12 Python files to patch
EQ12_PYTHON_FILES = [
    "eq12_godstack_orchestrator.py",
    "eq12_x_factor_master.py",
    "eq12_sports_betting_advanced.py",
    "chrome_governance_automation.py",
    "firefox_governance_automation.py",
    "eq12_governance_assistant.py",
    "eq12_streaming_assistant.py",
    "eq12_openai_governance.py",
    "eq12_auto_trade_executor.py",
]

# Import statement to add at the top
UNICODE_IMPORT = "from eq12_unicode_simple import sanitize_text, safe_print, safe_open"


def find_eq12_scripts():
    """Find all EQ12 Python scripts in the current directory."""
    found_files = []

    for pattern in ["eq12_*.py", "chrome_*.py", "firefox_*.py", "*_governance*.py"]:
        for file_path in Path(".").glob(pattern):
            if file_path.name not in [
                "eq12_unicode_simple.py",
                "eq12_unicode_guard.py",
                "eq12_unicode_patcher.py",
            ]:
                found_files.append(str(file_path))

    return found_files


def has_unicode_protection(file_path):
    """Check if a file already has Unicode protection."""
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        return "eq12_unicode_simple" in content
    except Exception as e:
        safe_print(f"❌ Error reading {file_path}: {e}")
        return False


def patch_file(file_path):
    """Add Unicode protection to a Python file."""
    try:
        safe_print(f"🔧 Patching {file_path}...")

        # Read the file
        with open(file_path, encoding="utf-8", errors="replace") as f:
            content = f.read()

        # Check if already patched
        if "eq12_unicode_simple" in content:
            safe_print(f"✅ {file_path} already has Unicode protection")
            return True

        # Find the best place to insert the import
        lines = content.split("\n")
        insert_position = 0

        # Look for existing imports
        for i, line in enumerate(lines):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                insert_position = i + 1
            elif line.strip().startswith("#") or line.strip() == "":
                continue
            else:
                break

        # Insert the Unicode import
        lines.insert(insert_position, UNICODE_IMPORT)
        lines.insert(insert_position + 1, "")

        # Patch common problematic patterns
        modified_content = "\n".join(lines)

        # Replace print() calls with safe_print() (basic replacement)
        modified_content = re.sub(r"\bprint\(", "safe_print(", modified_content)

        # Replace open() calls with safe_open() (basic replacement)
        modified_content = re.sub(r"\bopen\(", "safe_open(", modified_content)

        # Add text sanitization to logging calls (basic)
        modified_content = re.sub(
            r'logger\.(info|warning|error|debug)\(f?"([^"]*)"',
            r'logger.\1(sanitize_text(f"\2")',
            modified_content,
        )

        # Create backup
        backup_path = f"{file_path}.unicode_backup"
        with open(backup_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(content)

        # Write patched file
        with open(file_path, "w", encoding="utf-8", errors="replace") as f:
            f.write(modified_content)

        safe_print(f"✅ {file_path} patched successfully (backup: {backup_path})")
        return True

    except Exception as e:
        safe_print(f"❌ Failed to patch {file_path}: {e}")
        return False


def verify_files():
    """Verify Unicode protection in EQ12 files."""
    safe_print("🔍 Verifying Unicode protection...")

    files = find_eq12_scripts()
    protected_count = 0

    for file_path in files:
        if has_unicode_protection(file_path):
            safe_print(f"✅ {file_path}: Protected")
            protected_count += 1
        else:
            safe_print(f"⚠️ {file_path}: Not protected")

    safe_print(f"\n📊 Protection Status: {protected_count}/{len(files)} files protected")
    return protected_count == len(files)


def patch_all_files():
    """Patch all EQ12 Python files with Unicode protection."""
    safe_print("🛡️ EQ12 UNICODE INTEGRATION PATCHER")
    safe_print("===================================")

    files = find_eq12_scripts()
    safe_print(f"Found {len(files)} EQ12 Python files")

    success_count = 0

    for file_path in files:
        if patch_file(file_path):
            success_count += 1

    safe_print(f"\n📊 Patching Results: {success_count}/{len(files)} files patched successfully")

    if success_count == len(files):
        safe_print("🎉 All files patched successfully!")
        safe_print("\n📋 NEXT STEPS:")
        safe_print("  1. Test your EQ12 scripts to ensure they work correctly")
        safe_print("  2. Run: python eq12_unicode_patcher.py --verify")
        safe_print("  3. If issues occur, restore from .unicode_backup files")
    else:
        safe_print("⚠️ Some files failed to patch. Check error messages above.")


def list_files():
    """List all EQ12 files and their Unicode protection status."""
    safe_print("📁 EQ12 PYTHON FILES")
    safe_print("===================")

    files = find_eq12_scripts()

    for file_path in files:
        status = "Protected" if has_unicode_protection(file_path) else "Not Protected"
        status_icon = "✅" if has_unicode_protection(file_path) else "⚠️"

        file_size = Path(file_path).stat().st_size if Path(file_path).exists() else 0
        safe_print(f"{status_icon} {file_path:<40} {status:<15} ({file_size:,} bytes)")


def restore_backups():
    """Restore files from Unicode backup files."""
    safe_print("🔄 Restoring from backups...")

    backup_files = list(Path(".").glob("*.unicode_backup"))

    if not backup_files:
        safe_print("ℹ️ No backup files found")
        return

    for backup_path in backup_files:
        original_path = str(backup_path).replace(".unicode_backup", "")

        try:
            # Restore the original file
            with open(backup_path, encoding="utf-8", errors="replace") as f:
                content = f.read()

            with open(original_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(content)

            safe_print(f"✅ Restored {original_path}")

            # Remove backup file
            backup_path.unlink()

        except Exception as e:
            safe_print(f"❌ Failed to restore {original_path}: {e}")


def test_unicode_integration():
    """Test Unicode integration by importing patched files."""
    safe_print("🧪 Testing Unicode integration...")

    test_files = find_eq12_scripts()[:3]  # Test first 3 files only

    for file_path in test_files:
        try:
            # Try to import the module
            module_name = Path(file_path).stem
            safe_print(f"🔍 Testing {module_name}...")

            # This is a basic test - just check if it imports without Unicode errors
            exec(f"import {module_name}")
            safe_print(f"✅ {module_name} imports successfully")

        except UnicodeError as e:
            safe_print(f"❌ {module_name} has Unicode error: {e}")
        except ImportError as e:
            safe_print(f"⚠️ {module_name} import error (may be expected): {e}")
        except Exception as e:
            safe_print(f"⚠️ {module_name} other error: {e}")


def main():
    parser = argparse.ArgumentParser(description="EQ12 Unicode Integration Patcher")
    parser.add_argument("--patch-all", action="store_true", help="Patch all EQ12 files")
    parser.add_argument("--verify", action="store_true", help="Verify Unicode protection")
    parser.add_argument("--list-files", action="store_true", help="List all EQ12 files")
    parser.add_argument("--restore", action="store_true", help="Restore from backups")
    parser.add_argument("--test", action="store_true", help="Test Unicode integration")

    args = parser.parse_args()

    if args.patch_all:
        patch_all_files()
    elif args.verify:
        verify_files()
    elif args.list_files:
        list_files()
    elif args.restore:
        restore_backups()
    elif args.test:
        test_unicode_integration()
    else:
        safe_print("🛡️ EQ12 Unicode Integration Patcher")
        safe_print("Use --help for available options")
        safe_print("\nQuick start: python eq12_unicode_patcher.py --list-files")


if __name__ == "__main__":
    main()
