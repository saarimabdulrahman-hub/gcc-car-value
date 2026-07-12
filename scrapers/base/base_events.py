"""Event bus — decoupled event emission for scraper lifecycle events."""

from typing import Callable, Awaitable
from scrapers.models import ScraperEvent
import structlog

logger = structlog.get_logger()

EventHandler = Callable[[ScraperEvent], Awaitable[None]]


class EventBus:
    """Simple pub/sub event bus for scraper lifecycle events.

    Usage:
        bus = EventBus()
        bus.on("job.started", my_handler)
        await bus.emit(ScraperEvent("job.started", job_id="abc"))
    """

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}

    def on(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def off(self, event_type: str, handler: EventHandler) -> None:
        """Remove a handler."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)

    async def emit(self, event: ScraperEvent) -> None:
        """Emit an event to all registered handlers.

        Handlers run concurrently. Exceptions in handlers are logged
        but never propagate — one bad handler doesn't break others.
        """
        handlers = self._handlers.get(event.event_type, [])
        if not handlers:
            return

        import asyncio
        tasks = []
        for handler in handlers:
            tasks.append(self._safe_invoke(handler, event))
        await asyncio.gather(*tasks)

    async def _safe_invoke(self, handler: EventHandler,
                           event: ScraperEvent) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error("event_handler_failed",
                        event_type=event.event_type, error=str(e)[:200])


# Standard event types
EVENTS = {
    "job.started":     "A scraper job has started execution",
    "job.completed":   "A scraper job completed successfully",
    "job.failed":      "A scraper job failed permanently",
    "job.cancelled":   "A scraper job was cancelled",
    "job.retrying":    "A scraper job is retrying after failure",
    "page.downloaded": "A page was successfully downloaded",
    "page.parsed":     "A page was successfully parsed",
    "listing.found":   "A listing was extracted from a page",
    "rate.limited":    "The scraper hit a rate limit",
}
