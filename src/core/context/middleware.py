"""CorrelationMiddleware — FastAPI middleware for request context propagation.

Generates or preserves correlation IDs, creates a RequestContext for each
request, binds it to the logging context, and includes the correlation ID
in the response header.

Middleware overhead target: < 0.2 ms per request (no I/O, pure in-memory).
"""

from __future__ import annotations

import time
import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.context.models import RequestContext
from src.core.context.storage import set_context, clear_context, get_context
from src.core.logging.context import bind_context as log_bind


def _generate_correlation_id() -> str:
    """Generate a time-sortable correlation ID.

    UUID7 is preferred (time-ordered, sortable) but not available in
    Python's uuid module. We use UUID4 as a universal fallback.
    """
    return str(uuid.uuid4())


class CorrelationMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that manages request context.

    For each request:
    1. Extract or generate a correlation ID
    2. Create a RequestContext with request metadata
    3. Store in ContextVar for the duration of the request
    4. Bind relevant fields to the logging context
    5. Return X-Correlation-ID in the response header

    Respects incoming X-Correlation-ID — if the client sends one, we reuse it.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # --- Generate or reuse correlation ID ---
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            request.headers.get("x-correlation-id", ""),
        )
        if not correlation_id:
            correlation_id = _generate_correlation_id()

        # --- Build request context ---
        client_ip = (
            request.client.host if request.client
            else request.headers.get("X-Forwarded-For", "")
        )
        # Hash the IP for privacy (not PII)
        if client_ip and not client_ip.startswith("sha256:"):
            import hashlib
            client_ip = f"sha256:{hashlib.sha256(client_ip.encode()).hexdigest()[:12]}"

        ctx = RequestContext(
            correlation_id=correlation_id,
            request_id=str(uuid.uuid4()),
            request_start=time.time(),
            request_method=request.method,
            request_path=request.url.path,
            client_ip=client_ip,
            user_agent=request.headers.get("User-Agent", ""),
        )

        set_context(ctx)

        # --- Bind to logging context ---
        log_bind(**ctx.to_log_fields())

        # --- Process request ---
        try:
            response = await call_next(request)
        except Exception:
            # Include correlation_id in error response
            response = Response(
                content='{"detail":"Internal server error"}',
                status_code=500,
                media_type="application/json",
            )

        # --- Add correlation ID to response ---
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Request-ID"] = ctx.request_id

        # --- Include response time ---
        duration_ms = (time.time() - ctx.request_start) * 1000
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.1f}"

        # --- Cleanup ---
        clear_context()

        return response


# ------------------------------------------------------------------
# Exception handler — injects correlation_id into error responses
# ------------------------------------------------------------------

async def correlation_exception_handler(request: Request, exc: Exception):
    """FastAPI exception handler that includes correlation_id in errors.

    Register in main.py:
        app.add_exception_handler(Exception, correlation_exception_handler)
    """
    from fastapi.responses import JSONResponse
    ctx = get_context()
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "correlation_id": ctx.correlation_id or "",
        },
    )
