#!/usr/bin/env python3
"""
EQ12 Import Auditor and Auto-Installer
Scans for missing imports and auto-installs packages with uv.
"""

import importlib
import pathlib
import re
import subprocess
import sys


def main():
    """Audit imports and install missing packages."""
    print("🔍 EQ12 Import Auditor Starting...")

    # Find all Python files
    root = pathlib.Path(__file__).resolve().parents[1]
    py_files = list(root.rglob("*.py"))

    # Exclude problematic directories
    excluded_dirs = {
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "archive_duplicates",
        "generated_projects",
        "EdgeGodParlays",
        "EQ12_Automation",
    }

    py_files = [f for f in py_files if not any(exc in str(f) for exc in excluded_dirs)]

    print(f"📁 Scanning {len(py_files)} Python files...")

    # Extract imports
    imports = set()
    import_pattern = re.compile(
        r"^\s*(?:from\s+([\w\.]+)\s+import|import\s+([\w\.]+))", re.MULTILINE
    )

    for file_path in py_files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            for match in import_pattern.finditer(content):
                module = match.group(1) or match.group(2)
                if module and not module.startswith((".", "tests", "eq12")):
                    # Get top-level module name
                    top_module = module.split(".")[0]
                    imports.add(top_module)
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")

    print(f"📦 Found {len(imports)} unique imports to check")

    # Check which modules are missing
    missing = []
    available = []

    for module in sorted(imports):
        try:
            importlib.import_module(module)
            available.append(module)
        except ImportError:
            # Skip built-in modules that might not import directly
            if module not in {
                "os",
                "sys",
                "json",
                "time",
                "datetime",
                "collections",
                "typing",
                "pathlib",
                "asyncio",
                "logging",
                "traceback",
                "functools",
                "itertools",
                "dataclasses",
                "enum",
            }:
                missing.append(module)

    print(f"✅ Available: {len(available)} modules")
    print(f"❌ Missing: {len(missing)} modules")

    if missing:
        print("\n📋 Missing modules:")
        for module in missing:
            print(f"   - {module}")

        # Auto-install with uv if available
        try:
            subprocess.check_call(
                [sys.executable, "-m", "uv", "--version"], stdout=subprocess.DEVNULL
            )

            print(f"\n⚡ Auto-installing {len(missing)} missing packages with uv...")
            subprocess.check_call(
                [sys.executable, "-m", "uv", "pip", "install", *missing])
            print("✅ Installation completed!")

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("\n💡 uv not found, falling back to pip...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", *missing])
                print("✅ Installation completed with pip!")
            except subprocess.CalledProcessError as e:
                print(f"❌ Installation failed: {e}")
                print("💡 You may need to install some packages manually")
    else:
        print("\n🎉 All imports are satisfied!")

    # Generate requirements update suggestion
    if missing:
        print("\n💡 Consider adding to requirements.txt:")
        for module in missing:
            print(f"   {module}>=latest")


if __name__ == "__main__":
    main()
