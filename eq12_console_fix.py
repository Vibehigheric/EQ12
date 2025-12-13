"""
EQ12 Console UTF-8 Fix for Windows
==================================

Fixes UnicodeEncodeError crashes when using emojis in Windows PowerShell/CMD.
Import this module at the top of any script that uses emojis or Unicode in console output.

Usage:
    import eq12_console_fix  # Just import, it auto-applies the fix

Author: EQ12 Development Team
License: MIT
"""

import contextlib
import locale
import os
import sys


def apply_utf8_fix():
    """
    Apply UTF-8 encoding fix for Windows console to prevent emoji crashes.

    This fixes the common error:
    UnicodeEncodeError: 'cp1252' codec can't encode character '🤖' in position X
    """
    try:
        # Method 1: Reconfigure stdout/stderr to UTF-8
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass  # Silently continue if reconfigure not available

    try:
        # Method 2: Set environment encoding
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")

        # Method 3: Set console code page to UTF-8 (Windows)
        if os.name == "nt":
            with contextlib.suppress(Exception):
                os.system("chcp 65001 >nul 2>&1")

    except Exception:
        pass  # Continue if any method fails


def safe_print(*args, **kwargs):
    """
    Safe print function that handles Unicode characters gracefully.

    Args:
        *args: Arguments to print
        **kwargs: Keyword arguments for print()

    Returns:
        None
    """
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: encode to ASCII with replacement
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode("ascii", "replace").decode("ascii"))
            else:
                safe_args.append(str(arg).encode("ascii", "replace").decode("ascii"))
        print(*safe_args, **kwargs)


def get_safe_encoding():
    """
    Get the safest encoding for the current console.

    Returns:
        str: Encoding name ('utf-8' preferred, fallback to system default)
    """
    try:
        # Try UTF-8 first
        test_string = "🤖 Test"
        test_string.encode("utf-8")
        sys.stdout.write("")  # Test if console supports it
        return "utf-8"
    except (UnicodeError, UnicodeEncodeError):
        # Fallback to system default
        return locale.getpreferredencoding() or "cp1252"


# Auto-apply fix when module is imported
apply_utf8_fix()

# Make safe_print available for import
__all__ = ["apply_utf8_fix", "get_safe_encoding", "safe_print"]
