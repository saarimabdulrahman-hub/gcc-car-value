"""Trace context — inject trace_id/span_id into request context and logs.

When a span is active, its trace_id and span_id are available through
the request context system. This enables log correlation: every log line
within a traced request automatically includes trace_id.
"""

from __future__ import annotations


def inject_trace_into_context(span) -> None:
    """Inject the current span's trace_id into the request context.

    Called automatically when a root HTTP span is created by the
    tracing middleware. Makes trace_id available to all downstream
    code via get_context().
    """
    if span is None or span._otel_span is None:
        return

    try:
        otel_span = span._otel_span
        ctx = otel_span.get_span_context()
        if ctx.is_valid:
            from src.core.context.storage import update_context, set_context
            updated = update_context(
                **{"trace_id": format(ctx.trace_id, '032x'),
                   "span_id": format(ctx.span_id, '016x')}
            )
            set_context(updated)

            # Also bind to logging context
            from src.core.logging.context import bind_context
            bind_context(
                trace_id=format(ctx.trace_id, '032x'),
                span_id=format(ctx.span_id, '016x'),
            )
    except Exception:
        pass  # Never let context injection break the request


def current_trace_id() -> str:
    """Return the current trace_id from request context, or empty string."""
    try:
        from src.core.context.storage import get_context
        return getattr(get_context(), 'trace_id', '') or ''
    except Exception:
        return ''
