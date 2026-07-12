"""Span abstraction — wraps OpenTelemetry Span or provides no-op fallback.

When OpenTelemetry is disabled or not installed, all span operations are
no-ops. This means application code can always call span methods without
checking if tracing is enabled.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any


class Span:
    """Wrapper around an OpenTelemetry span.

    Provides a clean API: set_attribute, add_event, record_exception, set_status.
    When OTel is disabled, this becomes a NoOpSpan — no errors, no overhead.
    """

    def __init__(self, otel_span: Any | None = None, name: str = ""):
        self._otel_span = otel_span
        self.name = name
        self._start_time = time.perf_counter()

    # ------------------------------------------------------------------
    # Public API — safe to call regardless of OTel state
    # ------------------------------------------------------------------

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute. No-op if tracing disabled."""
        if self._otel_span is not None and value is not None:
            # Mask sensitive attributes
            from src.core.logging.filters import mask_field
            safe_value = mask_field(key, value)
            self._otel_span.set_attribute(key, safe_value)

    def set_attributes(self, **kwargs: Any) -> None:
        """Set multiple attributes at once."""
        for key, value in kwargs.items():
            self.set_attribute(key, value)

    def add_event(self, name: str, **attributes: Any) -> None:
        """Add a timed event to the span."""
        if self._otel_span is not None:
            safe_attrs = {}
            for k, v in attributes.items():
                from src.core.logging.filters import mask_field
                safe_attrs[k] = mask_field(k, v)
            self._otel_span.add_event(name, attributes=safe_attrs)

    def record_exception(self, exception: Exception) -> None:
        """Record an exception on the span."""
        if self._otel_span is not None:
            self._otel_span.record_exception(exception)
            self._otel_span.set_status(
                type(self._otel_span).__class__.__name__.replace("Span", ""),
                "ERROR",
            )
            # Use a simple status approach
            if hasattr(self._otel_span, 'set_status'):
                try:
                    from opentelemetry.trace import Status, StatusCode
                    self._otel_span.set_status(Status(StatusCode.ERROR))
                except ImportError:
                    pass

    def set_status_ok(self) -> None:
        """Mark span as successful."""
        if self._otel_span is not None:
            try:
                from opentelemetry.trace import Status, StatusCode
                self._otel_span.set_status(Status(StatusCode.OK))
            except ImportError:
                pass

    def set_status_error(self, description: str = "") -> None:
        """Mark span as failed."""
        if self._otel_span is not None:
            try:
                from opentelemetry.trace import Status, StatusCode
                self._otel_span.set_status(Status(StatusCode.ERROR, description))
            except ImportError:
                pass

    def end(self) -> None:
        """End the span."""
        if self._otel_span is not None:
            self._otel_span.end()

    @property
    def duration_ms(self) -> float:
        return (time.perf_counter() - self._start_time) * 1000


class NoOpSpan(Span):
    """Span that does nothing — used when tracing is disabled."""

    def __init__(self, name: str = "noop"):
        super().__init__(otel_span=None, name=name)
