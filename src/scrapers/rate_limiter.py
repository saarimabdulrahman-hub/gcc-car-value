import asyncio
import time


class RateLimiter:
    """Token bucket rate limiter for polite scraping."""

    def __init__(self, requests_per_second: float = 2.0):
        self.rate = requests_per_second
        self.tokens = requests_per_second
        self.max_tokens = requests_per_second
        self.last_refill = time.monotonic()

    async def acquire(self) -> None:
        while True:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.max_tokens, self.tokens + elapsed * self.rate)
            self.last_refill = now
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return
            wait_time = (1.0 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
