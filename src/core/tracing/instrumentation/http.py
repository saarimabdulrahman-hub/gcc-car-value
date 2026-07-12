"""HTTP instrumentation — creates root spans for incoming requests."""

from __future__ import annotations

from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.tracing.tracer import get_tracer


class HTTPInstrumentation(BaseHTTPMiddleware):
    """FastAPI middleware that creates a root span for every HTTP request.

    Must be placed early in the middleware stack (after CorrelationMiddleware).
    When tracing is disabled, passes through with zero overhead.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        tracer = get_tracer("http")
        from src.core.tracing.provider import is_tracing_enabled

        if not is_tracing_enabled():
            return await call_next(request)

        with tracer.start_span(
            f"{request.method} {request.url.path}",
            kind="server",
            attributes={
                "http.method": request.method,
                "http.url": str(request.url.path),
                "http.scheme": request.url.scheme or "http",
                "http.client_ip": (
                    request.client.host if request.client
                    else request.headers.get("X-Forwarded-For", "")
                ),
                "http.user_agent": request.headers.get("User-Agent", ""),
                "http.request_content_length": request.headers.get(
                    "Content-Length", "0"
                ),
            },
        ) as span:
            from src.core.tracing.context import inject_trace_into_context
            inject_trace_into_context(span)

            response = await call_next(request)

            span.set_attributes(
                http_status_code=response.status_code,
                http_response_content_length=response.headers.get(
                    "Content-Length", "0"
                ),
            )
            return response
