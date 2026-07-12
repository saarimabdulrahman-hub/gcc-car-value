"""Tracer abstraction — application-facing API for creating spans.

When OpenTelemetry is disabled, returns NoOpSpan instances — no overhead.
Application code never imports raw OTel SDK objects.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from src.core.tracing.span import Span, NoOpSpan


class Tracer:
    """Application-facing tracer. Creates spans with automatic context injection.

    Each span gets the current correlation_id, request_id, and user_id from
    the request context (if available). This happens automatically —
    no application code changes needed.
    """

    def __init__(self, name: str, otel_tracer: Any | None = None):
        self._name = name
        self._otel_tracer = otel_tracer

    @contextmanager
    def start_span(self, name: str, kind: str = "internal",
                   attributes: dict[str, Any] | None = None):
        """Start a new span. Use as context manager.

        Usage:
            with tracer.start_span("valuate") as span:
                span.set_attribute("make", "Toyota")
                result = await compute()
        """
        otel_span = None

        if self._otel_tracer is not None:
            try:
                otel_span = self._otel_tracer.start_span(name)
            except Exception:
                otel_span = None

        span = Span(otel_span, name)

        # Auto-inject request context attributes
        self._inject_context(span)

        # User-provided attributes
        if attributes:
            span.set_attributes(**attributes)

        try:
            yield span
            span.set_status_ok()
        except Exception as exc:
            span.record_exception(exc)
            span.set_status_error(str(exc)[:200])
            raise
        finally:
            span.end()

    async def start_span_async(self, name: str, kind: str = "internal",
                                attributes: dict[str, Any] | None = None):
        """Async context manager for spans. Same as start_span but async-safe."""
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def _async_span():
            with self.start_span(name, kind, attributes) as span:
                yield span

        return _async_span()

    def _inject_context(self, span: Span) -> None:
        """Auto-inject correlation_id, request_id, user_id from request context."""
        try:
            from src.core.context import get_context
            ctx = get_context()
            if ctx.correlation_id:
                span.set_attribute("correlation_id", ctx.correlation_id)
            if ctx.request_id:
                span.set_attribute("request_id", ctx.request_id)
            if ctx.user_id:
                span.set_attribute("user_id", ctx.user_id)
            if ctx.request_method:
                span.set_attribute("http.method", ctx.request_method)
            if ctx.request_path:
                span.set_attribute("http.path", ctx.request_path)
        except Exception:
            pass  # Never let context injection break tracing


# ------------------------------------------------------------------
# Tracer factory
# ------------------------------------------------------------------

_tracers: dict[str, Tracer] = {}


def get_tracer(name: str) -> Tracer:
    """Get or create a Tracer for the given module name.

    Returns a real OTel tracer if tracing is enabled, otherwise a no-op tracer
    that produces NoOpSpan instances.

    Usage:
        from src.core.tracing import get_tracer
        tracer = get_tracer(__name__)
        with tracer.start_span("my_operation") as span:
            ...
    """
    if name in _tracers:
        return _tracers[name]

    otel_tracer = None
    try:
        from src.core.tracing.provider import is_tracing_enabled
        if is_tracing_enabled():
            from opentelemetry import trace
            otel_tracer = trace.get_tracer(name)
    except ImportError:
        pass

    tracer = Tracer(name, otel_tracer)
    _tracers[name] = tracer
    return tracer
