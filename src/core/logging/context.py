"""Logging context — request-scoped fields bound to structlog contextvars.

Future prompts (P0021 correlation IDs, P0022 OpenTelemetry) will populate
these fields automatically via middleware. For now, the API provides
bind/clear for manual use.

Usage:
    from src.core.logging.context import bind_context, clear_context

    bind_context(request_id="abc123", user_id="user-1")
    log.info("request_started")  # includes request_id, user_id
    clear_context()
"""

import structlog


def bind_context(**kwargs) -> None:
    """Bind key-value pairs to the current request's logging context.

    These fields appear in every log message until cleared.
    Safe for async — uses contextvars under the hood.
    """
    # Filter out None values and mask sensitive keys
    from src.config.secrets import mask_sensitive_value
    cleaned = {}
    for k, v in kwargs.items():
        if v is not None:
            cleaned[k] = mask_sensitive_value(k, v)
    structlog.contextvars.bind_contextvars(**cleaned)


def clear_context() -> None:
    """Clear all bound context for the current request."""
    structlog.contextvars.clear_contextvars()


def get_context() -> dict:
    """Return current bound context (for debugging)."""
    return dict(structlog.contextvars.get_contextvars())


# Placeholder slots — populated by future middleware prompts
# These are documented here so application code knows what's available.

"""
Context fields (populated by middleware, not application code):

request_id       str   — UUID per HTTP request (P0021)
correlation_id   str   — cross-service trace ID (P0022)
user_id          str   — authenticated user UUID
role             str   — RBAC role
client_ip        str   — hashed remote IP
endpoint         str   — API path (e.g. /v1/valuate)
method           str   — HTTP method
status_code      int   — HTTP response status
"""
