#!/usr/bin/env python3
"""
EQ12 System Validation - Quick Status Check
Validates that the professional development environment is working correctly
"""

import subprocess
import sys
from pathlib import Path


def check_python():
    """Check Python version"""
    print("🐍 Checking Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.12+)")
        return False


def check_uv():
    """Check uv package manager"""
    print("📦 Checking uv...")
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ uv {result.stdout.strip()}")
            return True
        else:
            print("❌ uv not working")
            return False
    except FileNotFoundError:
        print("❌ uv not installed")
        return False


def check_venv():
    """Check virtual environment"""
    print("🏠 Checking virtual environment...")
    venv_path = Path(".venv")
    if venv_path.exists():
        python_exe = venv_path / "Scripts" / "python.exe"
        if python_exe.exists():
            print("✅ Virtual environment active")
            return True
    print("❌ Virtual environment not found")
    return False


def check_ruff():
    """Check ruff formatting"""
    print("🔍 Checking ruff...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruf", "--version"], capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print("❌ ruff not working")
            return False
    except Exception:
        print("❌ ruff not available")
        return False


def check_pytest():
    """Check pytest"""
    print("🧪 Checking pytest...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print("❌ pytest not working")
            return False
    except Exception:
        print("❌ pytest not available")
        return False


def check_eq12_files():
    """Check EQ12 core files"""
    print("📁 Checking EQ12 files...")

    required_files = [
        "pyproject.toml",
        "scripts/eq12_sportsbooks.py",
        "scripts/run_tests.py",
        "scripts/ci_pipeline.py",
        "scripts/audit_imports.py",
        ".pre-commit-config.yaml",
    ]

    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)

    if not missing:
        print(f"✅ All {len(required_files)} core files present")
        return True
    else:
        print(f"❌ Missing files: {missing}")
        return False


def main():
    """Main validation routine"""
    print("🚀 EQ12 Professional Development Environment Validation")
    print("=" * 60)

    checks = [
        check_python,
        check_uv,
        check_venv,
        check_ruff,
        check_pytest,
        check_eq12_files,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed: {e}")
            results.append(False)
        print()

    passed = sum(results)
    total = len(results)

    print("=" * 60)
    print(f"📊 SUMMARY: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 EQ12 ENVIRONMENT: FULLY OPERATIONAL")
        print("Ready for expert sports betting automation!")
    elif passed >= total * 0.8:
        print("⚠️ EQ12 ENVIRONMENT: MOSTLY WORKING")
        print("Minor issues detected but system is functional")
    else:
        print("❌ EQ12 ENVIRONMENT: NEEDS ATTENTION")
        print("Major issues detected, please run bootstrap script")

    return passed == total


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
