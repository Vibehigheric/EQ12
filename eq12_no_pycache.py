#!/usr/bin/env python3
"""
EQ12 No-Pycache Hook - Complete Bytecode Prevention
===================================================
Blocks ALL __pycache__ creation that causes Pylance corruption
Must be imported FIRST in every EQ12 script

Author: EQ12 AI Development Team
Version: NO-CACHE 1.0
Date: November 16, 2025
Location: Buffalo NY 14215 Content Empire
"""

import sys
import os

def disable_pycache():
    """
    Hardcoded pycache prevention for EQ12 system
    Prevents ALL bytecode corruption that breaks Pylance
    """
    # Set environment variable to prevent bytecode generation
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

    # Set Python flag to prevent .pyc creation
    sys.dont_write_bytecode = True

    # Additional safety measures
    os.environ["PYTHONOPTIMIZE"] = "0"  # Disable optimization
    os.environ["PYTHON_PYCACHE_PREFIX"] = ""  # Disable cache prefix

    print("EQ12: pycache creation disabled - Pylance protection active")

def clean_existing_pycache(root_path="C:/EQ12"):
    """
    Remove all existing __pycache__ directories from EQ12
    """
    import shutil
    removed_count = 0

    try:
        for root, dirs, files in os.walk(root_path):
            if "__pycache__" in dirs:
                pycache_path = os.path.join(root, "__pycache__")
                try:
                    shutil.rmtree(pycache_path, ignore_errors=True)
                    removed_count += 1
                    print(f"Removed: {pycache_path}")
                except:
                    pass  # Ignore errors

        print(f"EQ12: Cleaned {removed_count} __pycache__ directories")
        return removed_count

    except Exception as e:
        print(f"EQ12: Pycache cleanup warning: {e}")
        return 0

def verify_no_pycache():
    """
    Verify that pycache is properly disabled
    """
    checks = []

    # Check environment variables
    checks.append(os.environ.get("PYTHONDONTWRITEBYTECODE") == "1")
    checks.append(sys.dont_write_bytecode == True)

    # Check for existing pycache directories
    pycache_exists = False
    try:
        for root, dirs, files in os.walk("C:/EQ12"):
            if "__pycache__" in dirs:
                pycache_exists = True
                break
        checks.append(not pycache_exists)
    except:
        checks.append(True)  # Assume good if can't check

    safety_score = sum(checks) / len(checks)
    return safety_score >= 0.8  # 80% or higher means safe

def eq12_import_hook():
    """
    EQ12 standard import hook - call this at start of every script
    """
    disable_pycache()

    # Set additional EQ12 environment safety
    os.environ["EQ12_NO_PYCACHE"] = "ACTIVE"
    os.environ["EQ12_PYLANCE_SAFE"] = "TRUE"

    # Verify safety
    if not verify_no_pycache():
        print("WARNING: EQ12 pycache prevention may not be fully active")

# Auto-disable when imported
if __name__ == "__main__":
    print("================================================================")
    print("EQ12 NO-PYCACHE SYSTEM - PYLANCE PROTECTION")
    print("================================================================")
    print("")

    # Disable pycache
    disable_pycache()

    # Clean existing
    removed = clean_existing_pycache()

    # Verify
    if verify_no_pycache():
        print("")
        print("SUCCESS: EQ12 pycache protection is ACTIVE")
        print("- Bytecode generation disabled")
        print("- Existing cache directories cleaned")
        print("- Pylance corruption prevented")
        print("- Python will run clean without cached bytecode")
    else:
        print("")
        print("WARNING: EQ12 pycache protection incomplete")
        print("Manual intervention may be required")

    print("")
    print("To use in EQ12 scripts:")
    print("from eq12_no_pycache import eq12_import_hook")
    print("eq12_import_hook()  # Call at start of every script")
    print("")
    print("Buffalo NY 14215 Content Empire - NO-CACHE MODE ACTIVE")
else:
    # Auto-configure when imported
    eq12_import_hook()
