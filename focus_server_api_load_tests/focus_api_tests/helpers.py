from datetime import datetime, timedelta, timezone

def last_minutes_window(minutes: int, tz_aware: bool = False):
    """
    Return a (start, end) time window for the last minutes minutes.
    If tz_aware is True, returns timezone-aware datetimes in UTC.
    """
    now = datetime.now(timezone.utc) if tz_aware else datetime.utcnow()
    start = now - timedelta(minutes=minutes)
    return start, now
