"""OpenTelemetry distributed tracing — optional, disabled by default.

All tracing operations are no-ops when OpenTelemetry is not installed or
disabled. Application code uses the Tracer abstraction — never raw OTel SDK.

Usage:
    from src.core.tracing import get_tracer

    tracer = get_tracer("src.api.routes.valuation")
    with tracer.start_span("valuate") as span:
        span.set_attribute("make", "Toyota")
        result = await compute()
        span.set_attribute("estimate", result.estimate)
"""

from src.core.tracing.tracer import get_tracer, Tracer
from src.core.tracing.span import Span, NoOpSpan
from src.core.tracing.provider import init_tracing, is_tracing_enabled

__all__ = [
    "get_tracer", "Tracer", "Span", "NoOpSpan",
    "init_tracing", "is_tracing_enabled",
]
