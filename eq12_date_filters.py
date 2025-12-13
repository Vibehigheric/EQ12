# eq12_date_filters.py
"""
EQ12 Today-Only Date Guard (America/New_York by default)
- Centralized helpers to ensure we only pull/use games scheduled for *today*,
  unless the caller explicitly overrides.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timedelta
from typing import Any

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    ZoneInfo = None

NY_TZ = ZoneInfo("America/New_York") if ZoneInfo else None


def _to_dt(dt_like: Any) -> datetime | None:
    if dt_like is None:
        return None
    if isinstance(dt_like, datetime):
        return (
            dt_like
            if dt_like.tzinfo
            else dt_like.replace(tzinfo=ZoneInfo("UTC")) if ZoneInfo else dt_like
        )
    if isinstance(dt_like, (int, float)):
        try:
            return datetime.utcfromtimestamp(float(dt_like)).replace(
                tzinfo=ZoneInfo("UTC") if ZoneInfo else None
            )
        except Exception:
            return None
    if isinstance(dt_like, str):
        s = dt_like.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(s)
        except Exception:
            return None
    return None


def _ny_day_bounds(target_date: str | datetime | None = None):
    if target_date is None:
        now_ny = datetime.now(NY_TZ) if NY_TZ else datetime.now()
        day = now_ny.date()
    elif isinstance(target_date, str):
        day = datetime.fromisoformat(target_date).date()
    elif isinstance(target_date, datetime):
        day = (target_date.astimezone(NY_TZ) if NY_TZ else target_date).date()
    else:
        day = datetime.now(NY_TZ).date() if NY_TZ else datetime.now().date()

    start = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=NY_TZ)
    end = start + timedelta(days=1)
    return start, end


def filter_events_today(
    events: Iterable[dict[str, Any]],
    *,
    get_commence: Callable[[dict[str, Any]], Any],
    target_date: str | datetime | None = None,
) -> list[dict[str, Any]]:
    start, end = _ny_day_bounds(target_date)
    kept: list[dict[str, Any]] = []
    for ev in events:
        dt = _to_dt(get_commence(ev))
        if not dt:
            continue
        dt_ny = (
            dt.astimezone(NY_TZ)
            if NY_TZ and dt.tzinfo
            else (dt if NY_TZ is None else dt.replace(tzinfo=NY_TZ))
        )
        if start <= dt_ny < end:
            kept.append(ev)
    return kept


def filter_after_time(
    events: Iterable[dict[str, Any]],
    *,
    get_commence: Callable[[dict[str, Any]], Any],
    hhmm: str = "00:00",
    target_date: str | datetime | None = None,
) -> list[dict[str, Any]]:
    start_day, _ = _ny_day_bounds(target_date)
    try:
        hh, mm = map(int, hhmm.split(":"))
    except Exception:
        hh, mm = 0, 0
    cutoff = start_day.replace(hour=hh, minute=mm)
    kept: list[dict[str, Any]] = []
    for ev in events:
        dt = _to_dt(get_commence(ev))
        if not dt:
            continue
        dt_ny = (
            dt.astimezone(NY_TZ)
            if NY_TZ and dt.tzinfo
            else (dt if NY_TZ is None else dt.replace(tzinfo=NY_TZ))
        )
        if dt_ny >= cutoff and dt_ny.date() == cutoff.date():
            kept.append(ev)
    return kept
