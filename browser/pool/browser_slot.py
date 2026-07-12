"""BrowserSlot — wraps a Browser with lease state, health, idle tracking."""

from __future__ import annotations

import time
import asyncio
from enum import StrEnum
from browser.base.interfaces import Browser, BrowserContext


class SlotState(StrEnum):
    IDLE = "idle"
    LEASED = "leased"
    RECYCLING = "recycling"
    STOPPED = "stopped"


class BrowserSlot:
    """A managed browser instance with lease and health tracking.

    Each slot wraps one Browser and tracks:
        - Lease state (idle/leased/recycling/stopped)
        - Active contexts
        - Health (crashes, idle time)
        - Lifetime (for recycling policies)
    """

    def __init__(self, browser: Browser, slot_id: str = ""):
        self.browser = browser
        self.slot_id = slot_id
        self.state = SlotState.IDLE
        self._contexts: list[BrowserContext] = []
        self._created_at = time.monotonic()
        self._leased_at: float | None = None
        self._last_used = time.monotonic()
        self.crash_count = 0

    async def acquire(self) -> BrowserContext:
        """Lease a new context from this slot."""
        ctx = await self.browser.new_context()
        self._contexts.append(ctx)
        self.state = SlotState.LEASED
        self._leased_at = time.monotonic()
        self._last_used = time.monotonic()
        return ctx

    async def release(self) -> None:
        """Release the lease. Closes all contexts."""
        for ctx in self._contexts:
            try:
                await ctx.close()
            except Exception:
                pass
        self._contexts.clear()
        self.state = SlotState.IDLE
        self._leased_at = None

    async def health_check(self) -> bool:
        """Check if the browser is still responsive."""
        try:
            return await asyncio.wait_for(self.browser.health(), timeout=5.0)
        except Exception:
            self.crash_count += 1
            return False

    async def stop(self) -> None:
        """Stop the browser and mark as stopped."""
        await self.release()
        self.state = SlotState.STOPPED
        try:
            await self.browser.stop()
        except Exception:
            pass

    @property
    def context_count(self) -> int:
        return len(self._contexts)

    @property
    def idle_seconds(self) -> float:
        return time.monotonic() - self._last_used

    @property
    def lifetime_seconds(self) -> float:
        return time.monotonic() - self._created_at

    @property
    def lease_seconds(self) -> float:
        if self._leased_at is None:
            return 0.0
        return time.monotonic() - self._leased_at
