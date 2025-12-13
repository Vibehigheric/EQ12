"""
EQ12 UNICODE PROTECTION (SIMPLIFIED)
====================================
Basic Unicode protection for EQ12 without complex initialization.
This version focuses on fixing the core encoding issues.
"""

import os
import re
import warnings

# Force UTF-8 environment
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONLEGACYWINDOWSFSENCODING"] = "0"

# Suppress Unicode warnings
warnings.filterwarnings("ignore", category=UnicodeWarning)

# Text cleaning patterns
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
INVALID_UNICODE = re.compile(r"[\uFFFE\uFFFF]")


def sanitize_text(text):
    """Clean text for safe Unicode handling."""
    if text is None:
        return ""

    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return "[CONVERSION_ERROR]"

    # Remove control characters and invalid Unicode
    text = CONTROL_CHARS.sub("", text)
    text = INVALID_UNICODE.sub("", text)

    # Ensure proper encoding
    try:
        return text.encode("utf-8", "replace").decode("utf-8", "replace")
    except:
        return "[ENCODING_ERROR]"


def safe_print(*args, **kwargs):
    """Print with Unicode protection."""
    safe_args = []
    for arg in args:
        safe_args.append(sanitize_text(str(arg)))

    try:
        print(*safe_args, **kwargs)
    except UnicodeError:
        # Fallback to ASCII
        ascii_args = []
        for arg in safe_args:
            try:
                ascii_args.append(arg.encode("ascii", "replace").decode("ascii"))
            except:
                ascii_args.append("[PRINT_ERROR]")
        print(*ascii_args, **kwargs)


def safe_open(filename, mode="r", **kwargs):
    """Open file with Unicode protection."""
    kwargs.setdefault("encoding", "utf-8")
    kwargs.setdefault("errors", "replace")
    return open(filename, mode, **kwargs)


# Test if this module works
if __name__ == "__main__":
    safe_print("🛡️ EQ12 Unicode Protection: ACTIVE")

    test_text = "Hello 🌍 World! \x00\x01 Test"
    clean_text = sanitize_text(test_text)
    safe_print(f"✅ Sanitized: '{clean_text}'")

    safe_print("🎉 Basic Unicode Protection: WORKING!")
