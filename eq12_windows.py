from datetime import timedelta

LOCK_BUFFER = timedelta(seconds=120)
LIVE_TTL = timedelta(seconds=20)
PREGAME_TTL = timedelta(minutes=5)
def is_placeable(commence: str, now) -> bool:

def is_placeable(commence: str, now) -> bool:
    from eq12_time import parse_ts
    return parse_ts(commence) > now + LOCK_BUFFER
def is_fresh(last_update: str, now, live: bool) -> bool:

def is_fresh(last_update: str, now, live: bool) -> bool:
    from eq12_time import parse_ts
    ttl = LIVE_TTL if live else PREGAME_TTL
    return now - parse_ts(last_update) <= ttl
