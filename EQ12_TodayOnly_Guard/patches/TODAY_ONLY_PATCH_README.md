
# EQ12 "Today-Only" Guard — Quick Patch Guide

**Goal:** Only pull/build parlays from games on the **current date** (America/New_York) unless a different date is explicitly requested.

## 1) Add the shared guard module
Copy `eq12_date_filters.py` into `C:\EQ12\` (project root).

## 2) Patch each script to enforce today-only by default

### A) `eq12_enhanced_daily_parlay_system.py`
1. At the top, after other imports, add:
```python
from eq12_date_filters import filter_events_today, filter_after_time
from datetime import datetime
TARGET_DATE = None  # None = today (America/New_York); override with --date
AFTER = None        # e.g., "15:00" for after 3 PM
```

2. Wherever you collect events (list of dicts) from odds APIs or your engine, **immediately filter**:
```python
events = filter_events_today(events, get_commence=lambda e: e.get("commence_time"), target_date=TARGET_DATE)
if AFTER:
    events = filter_after_time(events, get_commence=lambda e: e.get("commence_time"), hhmm=AFTER, target_date=TARGET_DATE)
```

3. Wire CLI (if not already):
```python
import argparse
ap = argparse.ArgumentParser(...)
ap.add_argument("--date", help="YYYY-MM-DD (default: today America/New_York)")
ap.add_argument("--after", help="HH:MM 24h cutoff (optional)")
args = ap.parse_args()
TARGET_DATE = args.date or None
AFTER = args.after or None
```

### B) `eq12_historical_odds_engine.py`
Apply the **same import and filtering** right after you fetch historical or live events:
```python
from eq12_date_filters import filter_events_today, filter_after_time
events = filter_events_today(events, get_commence=lambda e: e.get("commence_time"), target_date=args.date)
if args.after:
    events = filter_after_time(events, get_commence=lambda e: e.get("commence_time"), hhmm=args.after, target_date=args.date)
```

Also add CLI flags if missing:
```python
ap.add_argument("--date", help="YYYY-MM-DD (default: today America/New_York)")
ap.add_argument("--after", help="HH:MM 24h cutoff (optional)")
```

### C) `eq12_complete_daily_analysis.py` & any other builders
Just before building tickets, enforce the filter on your **event pool** using the same two lines.

## 3) Fix the Mega Parlay Builder sort crash

Error:
```
TypeError: '<' not supported between instances of 'ParlayLeg' and 'ParlayLeg'
```
Cause: sorting list of tuples `(score, leg)` without a key may try to compare `leg` objects on ties.

**Patch** in `eq12_mega_parlay_builder.py` where you pick best legs:

**Before (problematic):**
```python
scored_legs = [(self._score_leg(leg), leg) for leg in legs]
best = [leg for _, leg in sorted(scored_legs, reverse=True)[:count]]
```

**After (safe):**
```python
# 1) Easiest: sort with a key directly on legs
best = sorted(legs, key=self._score_leg, reverse=True)[:count]

# (or) If you must keep tuples, add a numeric tiebreaker and a key:
scored_legs = [(self._score_leg(leg), idx, leg) for idx, leg in enumerate(legs)]
best = [t[2] for t in sorted(scored_legs, key=lambda t: (t[0], t[1]), reverse=True)[:count]]
```

## 4) Verify

**Today only, verbose:**
```
python eq12_enhanced_daily_parlay_system.py --bankroll 1000 --verbose
```

**Today only, after 3 PM:**
```
python eq12_mega_parlay_builder.py --after 15:00
```

**Override to another date (explicitly):**
```
python eq12_enhanced_daily_parlay_system.py --date 2025-10-05 --bankroll 1000
```

---

### Notes
- Filtering is timezone-aware for **America/New_York**.
- If an API returns UTC times (e.g. `2025-10-04T23:30:00Z`), the guard converts and keeps only events that fall on the NY calendar date.
- Use `--after HH:MM` for your "Games after 3PM only" scenario.
