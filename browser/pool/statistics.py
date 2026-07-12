"""Pool statistics collector."""

from browser.pool.browser_pool import BrowserPool
from browser.pool.browser_slot import SlotState


class PoolStatistics:
    """Collects pool utilization statistics."""

    def __init__(self, pool: BrowserPool):
        self._pool = pool

    def snapshot(self) -> dict:
        """Return current pool statistics."""
        slots = self._pool._slots
        active = sum(1 for s in slots if s.state == SlotState.LEASED)
        idle = sum(1 for s in slots if s.state == SlotState.IDLE)
        total_contexts = sum(s.context_count for s in slots)

        return {
            "total_slots": len(slots),
            "active_leases": active,
            "idle_slots": idle,
            "total_contexts": total_contexts,
            "utilization_pct": round(active / max(len(slots), 1) * 100, 1),
        }
