"""High-level context helpers — correlation_id accessor, background task runner."""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable

from src.core.context.storage import (
    get_context, set_context, clear_context, clone_context,
)
from src.core.context.models import RequestContext


def correlation_id() -> str:
    """Return the current request's correlation ID, or empty string."""
    return get_context().correlation_id


async def run_with_context(
    coro: Awaitable,
    context: RequestContext | None = None,
) -> None:
    """Run a coroutine with the specified request context.

    Saves and restores the parent context, so after the coroutine
    completes, the caller's context is unchanged.

    Usage:
        ctx = clone_context()  # snapshot current context
        asyncio.create_task(run_with_context(background_job(), ctx))
    """
    ctx = context or get_context()
    previous = get_context()
    set_context(ctx)
    try:
        await coro
    finally:
        set_context(previous)  # restore, don't clear


def run_sync_with_context(
    func: Callable,
    context: RequestContext | None = None,
) -> None:
    """Run a synchronous function with the specified context.

    Saves and restores the parent context.
    """
    ctx = context or get_context()
    previous = get_context()
    set_context(ctx)
    try:
        func()
    finally:
        set_context(previous)  # restore, don't clear
