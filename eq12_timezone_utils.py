"""
EQ12 Timezone Utilities
======================

Fixes timezone-aware datetime comparisons and provides utilities for
consistent datetime handling across the EQ12 sports betting platform.

This solves the common error:
"TypeError: can't compare offset-naive and offset-aware datetimes"

Author: EQ12 Development Team
License: MIT
"""

from datetime import UTC, datetime, timezone

import pytz
from dateutil import parser


def parse_utc(timestamp: str) -> datetime:
    """
    Parse ISO8601 timestamp string to timezone-aware datetime in UTC.

    The Odds API returns timestamps like "2025-10-06T01:15:00Z" which need
    to be properly parsed as UTC timezone-aware datetimes.

    Args:
        timestamp: ISO8601 timestamp string (with or without timezone info)

    Returns:
        Timezone-aware datetime in UTC
    """
    try:
        # Use dateutil parser which handles various ISO formats
        dt = parser.isoparse(timestamp)

        # If no timezone info, assume UTC (Odds API default)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # Convert to UTC if not already
        return dt.astimezone(timezone.utc)

    except (ValueError, TypeError) as e:
        raise ValueError(f"Failed to parse timestamp '{timestamp}': {e}")


def now_utc() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def ensure_aware(dt: datetime | str, default_tz: timezone | None = None) -> datetime:
    """
    Ensure datetime is timezone-aware.

    Args:
        dt: datetime object or ISO string
        default_tz: timezone to assume if dt is naive (defaults to UTC)

    Returns:
        Timezone-aware datetime
    """
    if isinstance(dt, str):
        return parse_utc(dt)

    if dt.tzinfo is None:
        # Naive datetime - add default timezone
        default_tz = default_tz or timezone.utc
        return dt.replace(tzinfo=default_tz)

    return dt


def to_local(dt: datetime | str, tz: pytz.BaseTzInfo | None = None) -> datetime:
    """
    Convert datetime to local timezone for display.

    Args:
        dt: UTC datetime or ISO string
        tz: target timezone (defaults to system local)

    Returns:
        Datetime in local timezone
    """
    if isinstance(dt, str):
        dt = parse_utc(dt)

    # Ensure it's timezone-aware
    dt = ensure_aware(dt)

    if tz is None:
        # Use system local timezone
        return dt.astimezone()
    else:
        return dt.astimezone(tz)


def format_display_time(dt: datetime | str, format_str: str = "%A, %B %d at %I:%M %p %Z") -> str:
    """
    Format datetime for user display with proper timezone handling.

    Args:
        dt: datetime or ISO string
        format_str: strftime format string

    Returns:
        Formatted datetime string
    """
    if isinstance(dt, str):
        dt = parse_utc(dt)

    # Convert to local time for display
    local_dt = to_local(dt)
    return local_dt.strftime(format_str)


def is_game_started(commence_time: datetime | str) -> bool:
    """
    Check if a game has already started.

    Args:
        commence_time: Game start time (datetime or ISO string)

    Returns:
        True if game has started
    """
    game_time = (
        ensure_aware(commence_time)
        if isinstance(commence_time, datetime)
        else parse_utc(commence_time)
    )
    current_time = now_utc()

    return current_time >= game_time


def time_until_game(commence_time: datetime | str) -> str:
    """
    Get human-readable time until game starts.

    Args:
        commence_time: Game start time (datetime or ISO string)

    Returns:
        Human-readable time string (e.g., "2 hours 15 minutes")
    """
    game_time = (
        ensure_aware(commence_time)
        if isinstance(commence_time, datetime)
        else parse_utc(commence_time)
    )
    current_time = now_utc()

    if current_time >= game_time:
        return "Game has started"

    delta = game_time - current_time

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    if days > 0:
        return f"{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"


# Common timezone objects for convenience
EST = pytz.timezone("US/Eastern")
CST = pytz.timezone("US/Central")
MST = pytz.timezone("US/Mountain")
PST = pytz.timezone("US/Pacific")
UTC = UTC

# Export commonly used functions
__all__ = [
    "CST",
    "EST",
    "MST",
    "PST",
    "UTC",
    "ensure_aware",
    "format_display_time",
    "is_game_started",
    "now_utc",
    "parse_utc",
    "time_until_game",
    "to_local",
]
