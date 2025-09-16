"""Helper utilities for Focus API tests."""
from __future__ import annotations

import time
from typing import Tuple


def now_epoch() -> int:
    """Return current UNIX epoch time in seconds as integer."""
    return int(time.time())

def last_minutes_window(minutes: int = 10) -> Tuple[int, int]:
    """Return a (start, end) epoch window for the last N minutes.

    Args:
        minutes: The duration in minutes to look back from now.
    Returns:
        A tuple of (start_epoch, end_epoch) in seconds.
    """
    end = now_epoch()
    start = end - (minutes * 60)
    return start, end
