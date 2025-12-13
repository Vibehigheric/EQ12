from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

ISO_UTC = "%Y-%m-%dT%H:%M:%S.%fZ"


def now_utc() -> datetime:
    return datetime.now(UTC)


def parse_ts(ts: str) -> datetime:
    """Parse RFC3339/ISO-8601 string to tz-aware datetime in UTC/offset-aware."""
    if ts.endswith("Z"):
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return datetime.fromisoformat(ts)


def to_iso_utc(dt: datetime) -> str:
    """Format datetime as ISO UTC string with trailing Z."""
    return dt.astimezone(UTC).strftime(ISO_UTC)


def to_local(dt: datetime, tz: str) -> datetime:
    """Convert aware datetime to given IANA timezone."""
    return dt.astimezone(ZoneInfo(tz))
