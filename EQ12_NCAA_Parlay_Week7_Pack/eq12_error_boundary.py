"""
EQ12 GPT-5 Error Boundary
Self-healing wrapper for LLM/API calls with retries, backoff, and fallback.
"""

import asyncio
from datetime import datetime


class GPT5ErrorBoundary:
    def __init__(self, primary_call, fallback_call=None, name="LLM"):
        self.primary_call = primary_call
        self.fallback_call = fallback_call
        self.name = name

    async def safe_call(self, *args, **kwargs):
        for attempt in range(1, 4):
            try:
                return (
                    await self.primary_call(*args, **kwargs)
                    if asyncio.iscoroutinefunction(self.primary_call)
                    else self.primary_call(*args, **kwargs)
                )
            except Exception as e:
                self._log(f"Attempt {attempt} failed: {e}")
                await asyncio.sleep(min(5 * attempt, 15))
        if self.fallback_call:
            try:
                self._log("Falling back ...")
                return (
                    await self.fallback_call(*args, **kwargs)
                    if asyncio.iscoroutinefunction(self.fallback_call)
                    else self.fallback_call(*args, **kwargs)
                )
            except Exception as e2:
                self._log(f"Fallback failed: {e2}")
                raise
        raise RuntimeError(f"{self.name} safe_call exhausted retries.")

    def _log(self, msg):
        line = f"[{datetime.utcnow().isoformat()}] [GPT5ErrorBoundary:{self.name}] {msg}"
        print(line)
        with open("logs/gpt5_errorboundary.log", "a", encoding="utf-8", errors="replace") as f:
            f.write(line + "\n")
