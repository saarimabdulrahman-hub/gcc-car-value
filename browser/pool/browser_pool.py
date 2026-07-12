"""BrowserPool — manages browser lifecycle, leasing, scaling, recycling.

The single component responsible for creating, reusing, and shutting down
browser instances. Scrapers request contexts from the pool and never
create browsers directly.

Thread-safe for async use. Supports concurrent leases without
double-leasing or context leakage.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Callable

import structlog

from browser.base.interfaces import Browser, BrowserContext
from browser.pool.config import PoolConfig
from browser.pool.browser_slot import BrowserSlot, SlotState
from browser.pool.errors import (
    PoolExhaustedError, PoolShuttingDownError, LeaseTimeoutError,
)

logger = structlog.get_logger()

BrowserFactory = Callable[[], Browser]


class BrowserPool:
    """Thread-safe async browser pool with leasing, scaling, and recycling.

    Usage:
        def make_browser():
            return factory.create("dummy")

        pool = BrowserPool(make_browser, PoolConfig(min_browsers=1, max_browsers=5))
        await pool.start()

        ctx = await pool.acquire()
        try:
            page = await ctx.new_page()
            await page.goto("https://example.com")
        finally:
            await pool.release(ctx)

        await pool.shutdown()
    """

    def __init__(self, browser_factory: BrowserFactory,
                 config: PoolConfig | None = None):
        self._factory = browser_factory
        self.config = config or PoolConfig()
        self._slots: list[BrowserSlot] = []
        self._lock = asyncio.Lock()
        self._shutting_down = False
        self._context_to_slot: dict[int, BrowserSlot] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the pool — pre-warms to min_browsers."""
        async with self._lock:
            for _ in range(self.config.warm_pool_size):
                await self._create_slot()

    async def shutdown(self) -> None:
        """Gracefully shutdown all browsers in the pool."""
        self._shutting_down = True
        async with self._lock:
            for slot in self._slots:
                await slot.stop()
            self._slots.clear()
            self._context_to_slot.clear()

    # ------------------------------------------------------------------
    # Leasing
    # ------------------------------------------------------------------

    async def acquire(self) -> BrowserContext:
        """Acquire a browser context from the pool.

        Blocks until a context is available or lease_timeout is reached.
        Automatically scales up the pool if all slots are busy.
        Raises PoolExhaustedError if no slots available and at max.
        Raises PoolShuttingDownError if pool is shutting down.
        """
        if self._shutting_down:
            raise PoolShuttingDownError("Pool is shutting down")

        deadline = time.monotonic() + self.config.lease_timeout

        while True:
            async with self._lock:
                # Try to find an idle slot
                for slot in self._slots:
                    if slot.state == SlotState.IDLE:
                        if not await slot.health_check():
                            await self._recycle_slot(slot)
                            continue
                        if slot.context_count < self.config.max_contexts_per_browser:
                            ctx = await slot.acquire()
                            self._context_to_slot[id(ctx)] = slot
                            return ctx

                # No idle slot — try to scale up
                if len(self._slots) < self.config.max_browsers:
                    await self._create_slot()
                    continue

                # Pool is full — check if we should wait or raise
                if time.monotonic() > deadline:
                    raise PoolExhaustedError(
                        f"No browser available after "
                        f"{self.config.lease_timeout}s. "
                        f"Active slots: {len(self._slots)}"
                    )

            # Wait and retry
            await asyncio.sleep(0.1)

    async def release(self, ctx: BrowserContext) -> None:
        """Release a leased context back to the pool."""
        async with self._lock:
            slot = self._context_to_slot.pop(id(ctx), None)
            if slot is None:
                return  # Already released or never leased

            # Check lease duration
            if (self.config.max_lease_duration > 0
                    and slot.lease_seconds > self.config.max_lease_duration):
                logger.warning("lease_timeout", slot_id=slot.slot_id,
                             duration=slot.lease_seconds)

            await slot.release()

            # Recycle if needed
            if self._should_recycle(slot):
                await self._recycle_slot(slot)
                # Create replacement if below min
                if (len(self._slots) < self.config.min_browsers
                        and not self._shutting_down):
                    await self._create_slot()

    # ------------------------------------------------------------------
    # Scaling
    # ------------------------------------------------------------------

    async def _create_slot(self) -> BrowserSlot:
        """Create a new browser slot. Must hold _lock."""
        browser = self._factory()
        await browser.start()
        slot = BrowserSlot(browser, slot_id=str(uuid.uuid4())[:8])
        self._slots.append(slot)
        logger.debug("browser_created", slot_id=slot.slot_id,
                    total_slots=len(self._slots))
        return slot

    async def _recycle_slot(self, slot: BrowserSlot) -> None:
        """Recycle a browser slot — stop and remove it."""
        slot.state = SlotState.RECYCLING
        await slot.stop()
        self._slots.remove(slot)
        logger.info("browser_recycled", slot_id=slot.slot_id,
                   reason=self._recycle_reason(slot))

    # ------------------------------------------------------------------
    # Health & Recycling
    # ------------------------------------------------------------------

    def _should_recycle(self, slot: BrowserSlot) -> bool:
        """Determine if a slot should be recycled."""
        if slot.crash_count >= self.config.crash_limit:
            return True
        if slot.lifetime_seconds > self.config.max_lifetime_seconds:
            return True
        return False

    async def run_health_checks(self) -> dict:
        """Run health checks on all slots. Returns summary."""
        async with self._lock:
            active = 0
            idle = 0
            unhealthy = 0
            for slot in self._slots:
                if not await slot.health_check():
                    unhealthy += 1
                    await self._recycle_slot(slot)
                elif slot.state == SlotState.LEASED:
                    active += 1
                else:
                    idle += 1
            return {
                "total_slots": len(self._slots),
                "active_leases": active,
                "idle_slots": idle,
                "unhealthy_recycled": unhealthy,
                "total_contexts": sum(s.context_count for s in self._slots),
            }

    def _recycle_reason(self, slot: BrowserSlot) -> str:
        if slot.crash_count >= self.config.crash_limit:
            return f"crash_limit ({slot.crash_count})"
        if slot.lifetime_seconds > self.config.max_lifetime_seconds:
            return "max_lifetime"
        if slot.idle_seconds > self.config.max_idle_seconds:
            return "max_idle"
        return "unknown"

    async def scale_idle(self) -> None:
        """Shrink pool by recycling idle slots above warm_pool_size."""
        async with self._lock:
            idle_slots = [s for s in self._slots
                        if s.state == SlotState.IDLE]
            idle_slots.sort(key=lambda s: s.idle_seconds, reverse=True)
            to_remove = idle_slots[self.config.warm_pool_size:]
            for slot in to_remove:
                if slot.idle_seconds > self.config.max_idle_seconds:
                    await self._recycle_slot(slot)
