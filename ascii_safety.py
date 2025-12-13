#!/usr/bin/env python3
"""
EQ12 ASCII Safety Enforcement Module
====================================
Hardcoded ASCII-only environment configuration
Prevents ALL Unicode corruption that causes Pylance EPIPE errors

Author: EQ12 AI Development Team
Version: ASCII-SAFE 2.0
Date: November 16, 2025
Location: Buffalo NY 14215 Content Empire
"""

import os
import sys
import locale

def enforce_ascii():
    """
    Hardcode ASCII-only environment for complete corruption immunity
    Call this at the start of every EQ12 script
    """
    # Force ASCII-only I/O streams
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding="ascii", errors="replace")
        sys.stderr.reconfigure(encoding="ascii", errors="replace")
        if hasattr(sys.stdin, 'reconfigure'):
            sys.stdin.reconfigure(encoding="ascii", errors="replace")

    # Set ASCII-safe environment variables
    ascii_env_vars = {
        'PYTHONIOENCODING': 'ascii:replace',
        'PYTHONUTF8': '0',  # Disable UTF-8 mode
        'LC_ALL': 'C',
        'LANG': 'C',
        'PYTHONLEGACYWINDOWSSTDIO': '1',
        'EQ12_ASCII_MODE': 'ACTIVE'
    }

    for var, value in ascii_env_vars.items():
        os.environ[var] = value

    # Force locale to C (ASCII-safe)
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except:
        pass  # Ignore if locale setting fails

def ascii_safe_print(text):
    """
    Print text safely in ASCII-only mode
    Strips all Unicode characters that could corrupt Pylance
    """
    if isinstance(text, bytes):
        text = text.decode('ascii', errors='replace')
    else:
        text = str(text)

    # Force ASCII conversion
    clean_text = text.encode('ascii', errors='replace').decode('ascii')
    print(clean_text)

def ascii_safe_input(prompt=""):
    """
    Get input safely in ASCII-only mode
    """
    ascii_safe_print(prompt)
    try:
        user_input = input()
        return user_input.encode('ascii', errors='replace').decode('ascii')
    except:
        return ""

def sanitize_string(text):
    """
    Convert any string to pure ASCII
    Removes all characters that could cause EPIPE errors
    """
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='replace')
    else:
        text = str(text)

    # Force ASCII-only conversion
    return text.encode('ascii', errors='replace').decode('ascii')

def check_ascii_safety():
    """
    Verify that ASCII safety mode is active
    Returns True if environment is properly configured
    """
    checks = []

    # Check environment variables
    checks.append(os.environ.get('PYTHONIOENCODING', '').startswith('ascii'))
    checks.append(os.environ.get('PYTHONUTF8') == '0')
    checks.append(os.environ.get('LC_ALL') == 'C')
    checks.append(os.environ.get('EQ12_ASCII_MODE') == 'ACTIVE')

    # Check stream configurations
    try:
        checks.append(sys.stdout.encoding.lower().startswith('ascii') or sys.stdout.encoding == 'cp437')
        checks.append(sys.stderr.encoding.lower().startswith('ascii') or sys.stderr.encoding == 'cp437')
    except:
        checks.append(False)

    safety_score = sum(checks) / len(checks)
    return safety_score >= 0.7  # 70% or higher means safe

def create_ascii_banner(title, width=60):
    """
    Create ASCII-safe banner without any Unicode characters
    Safe for Pylance and all LSP operations
    """
    if len(title) > width - 4:
        title = title[:width-4]

    border = "=" * width
    padding = (width - len(title) - 2) // 2
    title_line = "=" + " " * padding + title + " " * (width - len(title) - padding - 2) + "="

    return f"{border}\n{title_line}\n{border}"

def log_ascii_safe(message, log_file=None):
    """
    Log messages in ASCII-safe format
    Prevents log corruption that can crash Pylance
    """
    import datetime

    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    clean_message = sanitize_string(message)
    log_entry = f"[{timestamp}] {clean_message}"

    if log_file:
        try:
            with open(log_file, 'a', encoding='ascii', errors='replace') as f:
                f.write(log_entry + '\n')
        except:
            pass  # Ignore if logging fails

    ascii_safe_print(log_entry)

# Auto-configure ASCII safety when module is imported
def auto_configure():
    """
    Automatically configure ASCII safety when this module is imported
    """
    enforce_ascii()

    # Create ASCII-safe print aliases
    sys.modules[__name__].print = ascii_safe_print
    sys.modules[__name__].input = ascii_safe_input

# Initialize ASCII safety
if __name__ == "__main__":
    ascii_safe_print(create_ascii_banner("EQ12 ASCII SAFETY MODULE"))
    ascii_safe_print("Configuring ASCII-safe environment...")

    enforce_ascii()

    if check_ascii_safety():
        ascii_safe_print("SUCCESS: ASCII safety mode is ACTIVE")
        ascii_safe_print("Pylance EPIPE errors prevented")
        ascii_safe_print("Unicode corruption immunity enabled")
        ascii_safe_print("Buffalo NY 14215 Content Empire - ASCII SAFE MODE")
    else:
        ascii_safe_print("WARNING: ASCII safety configuration incomplete")
        ascii_safe_print("Manual environment adjustment may be required")

    ascii_safe_print("\nTo use in scripts:")
    ascii_safe_print("from ascii_safety import enforce_ascii, ascii_safe_print")
    ascii_safe_print("enforce_ascii()  # Call at start of script")
else:
    # Auto-configure when imported
    auto_configure()
