"""
EQ12 UNICODE GUARD
Prevents, catches, and corrects Unicode errors across EQ12 scripts.
"""

import asyncio
import builtins
import io
import re
import sys
import warnings


def _patch_stdio():
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


_patch_stdio()

_original_print = builtins.print


def safe_print(*args, **kwargs):
    safe_args = []
    for a in args:
        if isinstance(a, bytes):
            try:
                a = a.decode("utf-8", "replace")
            except Exception:
                a = str(a)
        elif isinstance(a, str):
            a = a.encode("utf-8", "replace").decode("utf-8", "replace")
        safe_args.append(a)
    kwargs.setdefault("flush", True)
    return _original_print(*safe_args, **kwargs)


builtins.print = safe_print


def sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return ""
    text = re.sub(r"[^\x09\x0A\x0D\x20-\uFFFF]", "", text)
    return text.encode("utf-8", "replace").decode("utf-8", "replace")


warnings.filterwarnings("ignore", category=UnicodeWarning)


def unicode_safe(func):
    async def async_wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return sanitize_text(result) if isinstance(result, str) else result
        except UnicodeError as ue:
            safe_print(f"[UnicodeGuard] {ue}")
            return ""

    def sync_wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return sanitize_text(result) if isinstance(result, str) else result
        except UnicodeError as ue:
            safe_print(f"[UnicodeGuard] {ue}")
            return ""

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
