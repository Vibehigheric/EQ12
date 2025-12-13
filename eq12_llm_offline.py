# eq12_llm_offline.py
"""
Cross-process LLM offline circuit breaker for EQ12.
Prevents all OpenAI calls when quota is exhausted.
"""

from __future__ import annotations

import json
import os
import time

SENTINEL = os.path.join(os.path.dirname(__file__), "logs", ".llm_offline.json")
_DEFAULT_COOLDOWN_S = 24 * 3600


class LLMOffline:
    """Cross-process circuit breaker for LLM calls."""

    _until_ts: float = 0.0  # in-memory fast path

    @classmethod
    def _file_until(cls) -> float:
        """Read offline-until timestamp from sentinel file."""
        try:
            with open(SENTINEL, encoding="utf-8") as f:
                data = json.load(f)
            s = data.get("until")
            if not s:
                return 0.0
            # Parse 'YYYY-MM-DDTHH:MM:SSZ' format
            t = time.strptime(s.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
            return time.mktime(t)
        except Exception:
            return 0.0

    @classmethod
    def is_offline(cls) -> bool:
        """Check if LLM calls should be blocked."""
        now = time.time()
        if now < cls._until_ts:
            return True
        u = cls._file_until()
        cls._until_ts = max(cls._until_ts, u)
        return now < cls._until_ts

    @classmethod
    def trip(cls, cooldown_s: int | None = None, reason: str = "quota"):
        """Trip the circuit breaker for specified cooldown period."""
        cooldown_s = int(cooldown_s or _DEFAULT_COOLDOWN_S)
        until = time.time() + cooldown_s
        cls._until_ts = until
        os.makedirs(os.path.dirname(SENTINEL), exist_ok=True)
        payload = {
            "until": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(until)),
            "reason": reason,
            "tripped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            with open(SENTINEL, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @classmethod
    def reset(cls):
        """Manually reset the circuit breaker."""
        cls._until_ts = 0.0
        try:
            if os.path.exists(SENTINEL):
                os.remove(SENTINEL)
        except Exception:
            pass

    @classmethod
    def status(cls) -> dict:
        """Get current circuit breaker status."""
        try:
            with open(SENTINEL, encoding="utf-8") as f:
                data = json.load(f)
            return {
                "offline": cls.is_offline(),
                "until": data.get("until"),
                "reason": data.get("reason"),
                "tripped_at": data.get("tripped_at"),
            }
        except Exception:
            return {"offline": False, "until": None, "reason": None, "tripped_at": None}
