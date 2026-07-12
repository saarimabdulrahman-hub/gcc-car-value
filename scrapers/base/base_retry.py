"""Retry engine — exponential backoff with jitter, max attempts, circuit breaker hooks."""

import asyncio
import random
import time
from typing import Callable, Awaitable

from scrapers.constants import DEFAULT_RETRIES, DEFAULT_BACKOFF_BASE, DEFAULT_BACKOFF_MAX
from scrapers.errors import ScraperError


class RetryEngine:
    """Exponential backoff retry with full jitter.

    Usage:
        engine = RetryEngine(max_attempts=3)
        result = await engine.execute(lambda: fetch_page(url))
    """

    def __init__(self, max_attempts: int = DEFAULT_RETRIES,
                 base_seconds: float = DEFAULT_BACKOFF_BASE,
                 max_seconds: float = DEFAULT_BACKOFF_MAX):
        self.max_attempts = max_attempts
        self.base_seconds = base_seconds
        self.max_seconds = max_seconds
        self.total_retries = 0

    async def execute(self, operation: Callable[[], Awaitable],
                      is_retryable: Callable[[Exception], bool] | None = None,
                      on_retry: Callable[[int, Exception], Awaitable] | None = None,
                      ) -> tuple[bool, object | None, list[Exception]]:
        """Execute an operation with retries.

        Returns (success, result, errors).
        """
        errors: list[Exception] = []
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = await operation()
                return True, result, errors
            except Exception as e:
                errors.append(e)
                if attempt == self.max_attempts:
                    return False, None, errors

                if is_retryable and not is_retryable(e):
                    return False, None, errors

                if isinstance(e, ScraperError) and not e.retryable:
                    return False, None, errors

                self.total_retries += 1
                if on_retry:
                    await on_retry(attempt, e)

                delay = self._backoff(attempt)
                await asyncio.sleep(delay)

        return False, None, errors

    def _backoff(self, attempt: int) -> float:
        """Exponential backoff with full jitter: min(cap, base * 2^(attempt-1))."""
        raw = self.base_seconds * (2 ** (attempt - 1))
        capped = min(raw, self.max_seconds)
        return random.uniform(0, capped)


def is_retryable_http(exc: Exception) -> bool:
    """Default retryability check for HTTP errors."""
    if isinstance(exc, ScraperError):
        return exc.retryable
    return True  # Unknown errors are retried by default
