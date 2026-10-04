import asyncio
import time
from collections import defaultdict


class RateLimiter:
    """Fixed-window limiter for a single application process."""

    def __init__(self, limit: int, window_seconds: float) -> None:
        self._limit = limit
        self._window_seconds = window_seconds
        self._lock = asyncio.Lock()
        self._buckets: dict[str, tuple[float, int]] = defaultdict(
            lambda: (0.0, 0)
        )

    async def allow(self, key: str) -> bool:
        now = time.monotonic()
        async with self._lock:
            started, count = self._buckets[key]
            if now - started >= self._window_seconds:
                self._buckets[key] = (now, 1)
                return True
            if count >= self._limit:
                return False
            self._buckets[key] = (started, count + 1)
            return True

    async def reset(self) -> None:
        async with self._lock:
            self._buckets.clear()
