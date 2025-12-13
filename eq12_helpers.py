# eq12_helpers.py
import json
import logging
import os
import threading
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any


# ---------- UTF-8 safe logging (fixes cp1252 emoji issues on Windows) ----------
def setup_utf8_logging(level=logging.INFO) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    h = logging.StreamHandler()
    try:
        # Py3.9+: StreamHandler has .setStream; ensure writer is UTF-8
        import sys

        sys.stdout.reconfigure(encoding="utf-8")  # ok on Win Py3.7+
    except Exception:
        pass
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    h.setFormatter(fmt)
    root.addHandler(h)
    root.setLevel(level)


# ---------- ENV helpers ----------
def env_get(name: str, default: str | None = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and (v is None or v == ""):
        raise ValueError(f"Missing required env: {name}")
    return v


def env_csv(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [s.strip() for s in raw.split(",") if s.strip()]


# ---------- Model chooser ----------
def choose_model(task: str) -> str:
    task = (task or "").lower()
    if any(k in task for k in ("boolean", "validator", "parlay", "risk", "refactor", "root-cause")):
        return env_get("OPENAI_MODEL_PRIMARY", "gpt-4o")
    if any(k in task for k in ("ui", "summary", "props", "news", "delta", "explain", "dashboard")):
        return env_get("OPENAI_MODEL_FAST", "gpt-4o-mini")
    return env_get("OPENAI_MODEL_BULK", "gpt-3.5-turbo")


# ---------- Simple token/rate budget guard (per-minute) ----------
class RateBudget:
    def __init__(self, rpm: int = 400, tpm: int = 800_000):
        self.rpm, self.tpm = rpm, tpm
        self._r_calls, self._r_tokens = 0, 0
        self._window_start = time.time()

    def _reset_if_needed(self):
        if time.time() - self._window_start >= 60:
            self._window_start = time.time()
            self._r_calls = 0
            self._r_tokens = 0

    def admit(self, est_tokens: int = 0):
        self._reset_if_needed()
        if self._r_calls + 1 > self.rpm or self._r_tokens + est_tokens > self.tpm:
            sleep_for = 60 - (time.time() - self._window_start)
            time.sleep(max(0.05, sleep_for))
            self._reset_if_needed()
        self._r_calls += 1
        self._r_tokens += max(0, est_tokens)


# ---------- Backoff & header parsing ----------
def parse_retry_after(headers: dict[str, str]) -> float | None:
    for k in ("retry-after", "Retry-After", "x-ratelimit-reset-requests"):
        if k in headers:
            try:
                return float(headers[k])
            except Exception:
                pass
    return None


def backoff_sequence() -> Iterable[float]:
    # Env override: "500,1000,2000,4000,8000,12000" (ms)
    raw = os.getenv("EQ12_RETRY_BACKOFF_MS", "500,1000,2000,4000,8000,12000")
    for part in raw.split(","):
        try:
            yield int(part) / 1000.0
        except Exception:
            continue


# ---------- Circuit breaker ----------
@dataclass
class BreakerState:
    offline: bool = False
    until: float | None = None
    reason: str | None = None


class CircuitBreaker:
    def __init__(self):
        self.state = BreakerState()

    def is_open(self) -> bool:
        if not self.state.offline:
            return False
        if self.state.until and time.time() >= self.state.until:
            # auto reset
            self.state = BreakerState()
            return False
        return True

    def trip(self, seconds: int, reason: str):
        self.state = BreakerState(True, time.time() + seconds, reason)


# ---------- Fallback rotation + call wrapper (Chat Completions) ----------
# This helper expects an OpenAI client factory you already use.
def call_with_fallbacks(
    create_client: Callable[[], Any],
    payload_builder: Callable[[str], dict[str, Any]],
    task_label: str,
    on_result: Callable[[Any], Any] | None = None,
) -> Any:
    """
    - create_client(): returns OpenAI client
    - payload_builder(model): returns kwargs for client.chat.completions.create(...)
    - on_result(resp): optional transform
    Rotates OPENAI_FALLBACK_MODELS on 429/5xx and trips breaker on insufficient_quota.
    """
    log = logging.getLogger("eq12.helpers")
    # Breaker
    global_breaker = _GLOBAL_BREAKER
    if global_breaker.is_open():
        raise RuntimeError(f"LLM breaker open: {global_breaker.state.reason}")

    models = [env_get("OPENAI_MODEL_SNAPSHOT", "")] if env_get("OPENAI_MODEL_SNAPSHOT", "") else []
    models.append(choose_model(task_label))
    models.extend(env_csv("OPENAI_FALLBACK_MODELS", ""))

    # De-duplicate while preserving order
    seen, model_queue = set(), []
    for m in models:
        if m and m not in seen:
            seen.add(m)
            model_queue.append(m)

    client = create_client()
    budget = RateBudget(
        rpm=int(os.getenv("EQ12_RPM_BUDGET", "400")),
        tpm=int(os.getenv("EQ12_TPM_BUDGET", "800000")),
    )

    last_err = None
    for model in model_queue:
        kwargs = payload_builder(model)
        # rough token estimate: input chars/4 + max_tokens
        est_tokens = (len(json.dumps(kwargs.get("messages", []))) // 4) + int(
            kwargs.get("max_tokens", 0) or 0
        )
        budget.admit(est_tokens)
        for delay in [0.0, *backoff_sequence()]:
            if delay:
                time.sleep(delay)
            try:
                resp = client.chat.completions.create(**kwargs)
                return on_result(resp) if on_result else resp
            except Exception as e:
                msg = str(e)
                # 429 vs quota
                if "insufficient_quota" in msg or "quota" in msg:
                    # Trip breaker for 15 minutes (not 24h hard lock)
                    global_breaker.trip(15 * 60, "insufficient_quota")
                    log.warning("Quota exhausted; breaker tripped for 15m")
                    raise
                if "429" in msg or "rate limit" in msg.lower():
                    # honor Retry-After if present
                    try:
                        ra = parse_retry_after(getattr(e, "response", {}).headers)  # type: ignore
                        if ra:
                            time.sleep(float(ra))
                    except Exception:
                        pass
                    last_err = e
                    continue
                # 5xx transient
                if any(s in msg for s in ("502", "503", "504", "temporar")):
                    last_err = e
                    continue
                # non-retryable
                raise
        logging.warning(f"Model failed after retries: {model}")
    # If all models failed:
    if last_err:
        raise last_err
    raise RuntimeError("All models unavailable")


_GLOBAL_BREAKER = CircuitBreaker()


# ---------- Structured JSON helper ----------
def build_json_payload(
    model: str, messages: list[dict[str, Any]], max_tokens: int = 1500, **kw
) -> dict[str, Any]:
    d = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": float(os.getenv("EQ12_TEMPERATURE", "0.2")),
        "max_tokens": max_tokens,
    }
    d.update(kw)
    return d


# ---------- Offline stub (when breaker is open) ----------
def offline_stub(task: str, messages: list[dict[str, Any]]) -> dict[str, Any]:
    # deterministic, safe JSON so your pipeline doesn't crash
    return {
        "mode": "offline",
        "task": task,
        "summary": "Operating in offline mode — using local heuristics.",
        "messages_seen": len(messages),
        "timestamp": time.time(),
    }


# ---------- Health probe to clear breaker ----------
def start_llm_health_probe(create_client: Callable[[], Any], interval_sec: int = 900):
    log = logging.getLogger("eq12.helpers.probe")

    def _tick():
        threading.Timer(interval_sec, _tick).start()
        if not _GLOBAL_BREAKER.is_open():
            return
        try:
            c = create_client()
            _ = c.models.list()  # cheap probe
            _GLOBAL_BREAKER.state = BreakerState()  # clear
            log.info("LLM breaker cleared by health probe")
        except Exception as e:
            log.info(f"Probe still failing: {e}")

    _tick()


# ---------- EQ12 OpenAI Client Factory ----------
def create_openai_client():
    """Factory for OpenAI client with EQ12 configuration"""
    try:
        from openai import OpenAI

        api_key = env_get("OPENAI_API_KEY", required=True)

        return OpenAI(
            api_key=api_key,
            timeout=float(os.getenv("OPENAI_TIMEOUT", "60")),
            max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
        )
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")
