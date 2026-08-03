"""Request context propagation — correlation IDs, async-safe storage.

Every request gets a unique correlation_id that flows through logs,
metrics, health checks, and background tasks via Python contextvars.
No manual parameter passing required.

Usage:
    from src.core.context import get_context, set_context, correlation_id

    ctx = get_context()
    print(ctx.correlation_id)

    # Background task helper:
    from src.core.context import run_with_context
    asyncio.create_task(run_with_context(my_coro, parent_ctx))
"""

from src.core.context.context import correlation_id
from src.core.context.middleware import CorrelationMiddleware
from src.core.context.models import RequestContext
from src.core.context.storage import (
    clear_context,
    clone_context,
    get_context,
    set_context,
    update_context,
)

__all__ = [
    "RequestContext",
    "set_context", "get_context", "clear_context",
    "update_context", "clone_context",
    "correlation_id",
    "CorrelationMiddleware",
]
