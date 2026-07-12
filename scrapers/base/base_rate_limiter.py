"""Token-bucket rate limiter — async, burst-aware."""

import asyncio
import time
import threading


class RateLimiter:
    """Async token-bucket rate limiter.

    Usage:
        limiter = RateLimiter(requests_per_second=2.0)
        async with limiter:
            await fetch_page(url)
    """

    def __init__(self, requests_per_second: float = 2.0,
                 burst_size: int | None = None):
        self.rate = requests_per_second
        self.max_tokens = burst_size or max(1, int(requests_per_second))
        self._tokens = float(self.max_tokens)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    async def acquire(self) -> None:
        """Wait until a token is available."""
        while True:
            wait = self._try_acquire()
            if wait <= 0:
                return
            await asyncio.sleep(wait)

    def _try_acquire(self) -> float:
        """Try to consume a token. Returns seconds to wait (0 = acquired)."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._tokens = min(self.max_tokens,
                              self._tokens + elapsed * self.rate)
            self._last_refill = now
            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return 0.0
            return (1.0 - self._tokens) / self.rate

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        pass

    @property
    def available_tokens(self) -> float:
        with self._lock:
            return self._tokens
