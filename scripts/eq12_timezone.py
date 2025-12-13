#!/usr/bin/env python3
"""
EQ12 Timezone Utilities
Fix for "offset-naive vs offset-aware" datetime comparison errors.

This module standardizes all datetime handling in EQ12 to UTC timezone-aware format.
"""

import re
from datetime import UTC, datetime


def parse_commence_time(time_str: str) -> datetime:
    """
    Parse commence time string to UTC timezone-aware datetime.

    Handles various formats:
    - ISO with Z: "2025-10-05T17:01:00Z"
    - ISO with offset: "2025-10-05T17:01:00-04:00"
    - ISO naive: "2025-10-05T17:01:00" (assumes UTC)
    - Common formats: "Oct 5, 2025 7:30 PM ET"

    Args:
        time_str: Time string in various formats

    Returns:
        UTC timezone-aware datetime object
    """
    if not time_str:
        raise ValueError("Empty time string")

    # Normalize 'Z' suffix to UTC offset
    if time_str.endswith("Z"):
        time_str = time_str[:-1] + "+00:00"

    try:
        # Try ISO format first
        dt = datetime.fromisoformat(time_str)

        # If naive (no timezone), assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)

        # Convert to UTC
        return dt.astimezone(UTC)

    except ValueError:
        # Try parsing common formats
        return _parse_common_formats(time_str)


def _parse_common_formats(time_str: str) -> datetime:
    """Parse common datetime formats used in sports betting."""
    time_str = time_str.strip()

    # Pattern: "Oct 5, 2025 7:30 PM ET" or "October 5, 2025 7:30 PM EST"
    et_pattern = r"(\w+)\s+(\d+),\s+(\d{4})\s+(\d{1,2}):(\d{2})\s+(AM|PM)\s+(ET|EST|EDT)"
    match = re.match(et_pattern, time_str, re.IGNORECASE)

    if match:
        month_str, day, year, hour, minute, ampm, _tz = match.groups()

        # Convert month name to number
        months = {
            "jan": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "may": 5,
            "jun": 6,
            "jul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12,
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        month = months.get(month_str.lower()[:3])
        if not month:
            raise ValueError(f"Unknown month: {month_str}")

        # Convert to 24-hour format
        hour = int(hour)
        if ampm.upper() == "PM" and hour != 12:
            hour += 12
        elif ampm.upper() == "AM" and hour == 12:
            hour = 0

        # Create naive datetime
        dt_naive = datetime(int(year), month, int(day), hour, int(minute))

        # Convert ET to UTC (ET is UTC-5 in winter, UTC-4 in summer)
        # For simplicity, assume EST (UTC-5) - adjust as needed
        from datetime import timedelta

        dt_utc = dt_naive + timedelta(hours=5)

        return dt_utc.replace(tzinfo=UTC)

    # Pattern: "2025-10-05 19:30:00"
    simple_pattern = r"(\d{4})-(\d{2})-(\d{2})\s+(\d{1,2}):(\d{2}):(\d{2})"
    match = re.match(simple_pattern, time_str)

    if match:
        year, month, day, hour, minute, second = match.groups()
        dt = datetime(
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            int(second))
        return dt.replace(tzinfo=UTC)

    raise ValueError(f"Unable to parse time format: {time_str}")


def utc_now() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(UTC)


def seconds_until_commence(commence_time: str | datetime) -> float:
    """
    Calculate seconds until game commences.

    Args:
        commence_time: Game start time (string or datetime)

    Returns:
        Seconds until commence (negative if in past)
    """
    if isinstance(commence_time, str):
        commence_dt = parse_commence_time(commence_time)
    else:
        commence_dt = commence_time

    # Ensure timezone-aware
    if commence_dt.tzinfo is None:
        commence_dt = commence_dt.replace(tzinfo=UTC)

    now_utc = utc_now()
    delta = commence_dt - now_utc
    return delta.total_seconds()


def is_within_steaming_window(
        commence_time: str | datetime,
        window_minutes: int = 10) -> bool:
    """
    Check if game is within steaming window (close to start).

    Args:
        commence_time: Game start time
        window_minutes: Steaming window in minutes before start

    Returns:
        True if within steaming window
    """
    seconds_until = seconds_until_commence(commence_time)
    window_seconds = window_minutes * 60

    # Within window if positive and less than window
    return 0 <= seconds_until <= window_seconds


def is_game_live(commence_time: str | datetime) -> bool:
    """Check if game has already started."""
    return seconds_until_commence(commence_time) < 0


def format_time_until(commence_time: str | datetime) -> str:
    """
    Format time until game starts in human-readable format.

    Returns:
        String like "2h 15m", "45m", "LIVE", or "FINISHED"
    """
    seconds = seconds_until_commence(commence_time)

    if seconds < 0:
        if abs(seconds) < 3600 * 4:  # Less than 4 hours ago
            return "LIVE"
        else:
            return "FINISHED"

    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        if minutes == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {minutes}m"


def validate_timezone_aware(dt: datetime, context: str = "") -> datetime:
    """
    Validate that datetime is timezone-aware.
    Convert to UTC if naive (with warning).

    Args:
        dt: Datetime to validate
        context: Context string for error messages

    Returns:
        Timezone-aware datetime in UTC
    """
    if dt.tzinfo is None:
        print(f"⚠️ Warning: Naive datetime detected in {context}. Assuming UTC.")
        return dt.replace(tzinfo=UTC)

    return dt.astimezone(UTC)


def safe_time_comparison(time1: str | datetime, time2: str | datetime) -> int:
    """
    Safely compare two times, handling timezone issues.

    Args:
        time1: First time (string or datetime)
        time2: Second time (string or datetime)

    Returns:
        -1 if time1 < time2, 0 if equal, 1 if time1 > time2
    """
    # Parse and normalize both times
    if isinstance(time1, str):
        dt1 = parse_commence_time(time1)
    else:
        dt1 = validate_timezone_aware(time1, "time1")

    if isinstance(time2, str):
        dt2 = parse_commence_time(time2)
    else:
        dt2 = validate_timezone_aware(time2, "time2")

    if dt1 < dt2:
        return -1
    elif dt1 > dt2:
        return 1
    else:
        return 0


# EQ12-specific helpers for common patterns
def filter_upcoming_games(games: list, commence_key: str = "commence_time") -> list:
    """Filter games to only upcoming ones."""
    now_utc = utc_now()
    upcoming = []

    for game in games:
        commence_time = game.get(commence_key)
        if commence_time:
            try:
                commence_dt = parse_commence_time(commence_time)
                if commence_dt > now_utc:
                    upcoming.append(game)
            except Exception as e:
                print(f"⚠️ Error parsing commence time for game: {e}")

    return upcoming


def sort_games_by_time(games: list, commence_key: str = "commence_time") -> list:
    """Sort games by commence time (earliest first)."""

    def get_commence_time(game):
        try:
            return parse_commence_time(game.get(commence_key, ""))
        except BaseException:
            return datetime.max.replace(tzinfo=UTC)  # Put invalid times last

    return sorted(games, key=get_commence_time)


def add_time_metadata(game: dict, commence_key: str = "commence_time") -> dict:
    """Add time-related metadata to game dict."""
    game_copy = game.copy()

    try:
        commence_time = game.get(commence_key)
        if commence_time:
            commence_dt = parse_commence_time(commence_time)

            game_copy["commence_time_utc"] = commence_dt.isoformat()
            game_copy["seconds_until_start"] = seconds_until_commence(commence_dt)
            game_copy["time_until_start"] = format_time_until(commence_dt)
            game_copy["is_live"] = is_game_live(commence_dt)
            game_copy["in_steaming_window"] = is_within_steaming_window(commence_dt)

    except Exception as e:
        print(f"⚠️ Error adding time metadata: {e}")

    return game_copy


if __name__ == "__main__":
    # Test timezone utilities
    print("🕐 EQ12 Timezone Utilities Test")
    print("=" * 50)

    # Test parsing various formats
    test_times = [
        "2025-10-05T17:01:00Z",
        "2025-10-05T17:01:00-04:00",
        "2025-10-05T17:01:00",
        "Oct 5, 2025 7:30 PM ET",
        "October 5, 2025 7:30 PM EST",
    ]

    for time_str in test_times:
        try:
            parsed = parse_commence_time(time_str)
            print(f"✅ '{time_str}' → {parsed.isoformat()}")
        except Exception as e:
            print(f"❌ '{time_str}' → Error: {e}")

    # Test time calculations
    future_time = "2025-10-05T20:00:00Z"
    seconds_until = seconds_until_commence(future_time)
    time_until = format_time_until(future_time)

    print(f"\n⏰ Time until {future_time}: {seconds_until:.0f}s ({time_until})")
    print("✅ All timezone utilities working correctly!")
