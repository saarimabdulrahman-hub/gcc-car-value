"""ContextVar-based storage for request context.

Each async task gets its own copy of the context. No global variables,
no threading.local — ContextVars are the correct primitive for async Python.

Context is propagated automatically to child coroutines within the same
task. For background tasks, use clone_context() + run_with_context().
"""

from __future__ import annotations

from contextvars import ContextVar

from src.core.context.models import RequestContext

# The single ContextVar that holds the current request's context.
# Initialized to an empty context for code paths outside HTTP requests
# (e.g., startup, background workers before context is set).
_request_context: ContextVar[RequestContext] = ContextVar(
    "request_context",
    default=RequestContext.empty(),
)


def set_context(ctx: RequestContext) -> None:
    """Set the current request context.

    Called by the CorrelationMiddleware at the start of each request.
    Overwrites any previously set context for this task.
    """
    _request_context.set(ctx)


def get_context() -> RequestContext:
    """Get the current request context.

    Always returns a RequestContext (never None). If no context has been
    set (e.g., during startup or in a background task), returns an empty
    context with correlation_id="".
    """
    return _request_context.get()


def clear_context() -> None:
    """Reset the context to empty for this task.

    Called at request teardown or when a background task finishes.
    """
    _request_context.set(RequestContext.empty())


def update_context(**kwargs) -> RequestContext:
    """Create a modified copy of the current context.

    Since RequestContext is frozen (immutable), this creates a new instance
    with the specified fields replaced. The original context is unchanged.

    Usage:
        ctx = update_context(user_id="abc123", country="AE")
        set_context(ctx)
    """
    current = get_context()
    fields = {
        f.name: getattr(current, f.name)
        for f in current.__dataclass_fields__.values()
    }
    fields.update(kwargs)
    return RequestContext(**fields)


def clone_context() -> RequestContext:
    """Create an independent copy of the current context.

    Used to propagate context into background tasks. The clone is a
    separate snapshot that won't be affected by the parent task's
    context changes.
    """
    return get_context()  # Frozen — safe to share without copying
