"""Console UX helpers for Commander++"""

from __future__ import annotations

import time
from contextlib import contextmanager

try:
    import winsound  # type: ignore
except ImportError:  # pragma: no cover
    winsound = None  # type: ignore


class ConsoleUX:
    def __init__(self, enable_sound: bool = True):
        self.enable_sound = enable_sound and winsound is not None

    @contextmanager
    def timed(self, label: str):
        start = time.time()
        print(f"[timer] {label} started...")
        try:
            yield
        finally:
            duration = time.time() - start
            print(f"[timer] {label} completed in {duration:.2f}s")
            if self.enable_sound:
                winsound.Beep(880, 120)

    def alert(self, message: str, level: str = "info") -> None:
        prefix = {
            "info": "[info]",
            "warning": "[warn]",
            "error": "[error]",
            "success": "[ok]",
        }.get(level, "[info]")
        print(f"{prefix} {message}")
        if self.enable_sound and level in {"warning", "error"}:
            winsound.Beep(440 if level == "warning" else 220, 200)


def build_console(config: dict) -> ConsoleUX:
    return ConsoleUX(enable_sound=config.get("enable_sound", False))
