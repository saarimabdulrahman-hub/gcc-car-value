"""RequestContext — immutable snapshot of the current request's metadata."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RequestContext:
    """Immutable snapshot of request-scoped metadata.

    Frozen (hashable) to prevent accidental mutation across coroutines.
    Use update_context() to create a modified copy.
    """

    # Identity
    correlation_id: str = ""
    request_id: str = ""

    # Timing
    request_start: float = field(default_factory=time.time)

    # HTTP
    request_method: str = ""
    request_path: str = ""
    client_ip: str = ""
    user_agent: str = ""

    # User
    user_id: str = ""
    role: str = ""
    organization_id: str = ""

    # Geo / Locale
    country: str = ""
    locale: str = ""

    # Session
    session_id: str = ""

    # Version
    api_version: str = ""
    environment: str = ""

    @classmethod
    def empty(cls) -> "RequestContext":
        """Create an empty context (used for background tasks without a request)."""
        return cls()

    def to_log_fields(self) -> dict[str, str | float]:
        """Return non-empty fields as a dict suitable for logging context."""
        fields = {}
        for field_name in [
            "correlation_id", "request_id", "user_id", "role",
            "request_method", "request_path", "client_ip", "country",
        ]:
            value = getattr(self, field_name, "")
            if value:
                fields[field_name] = value
        return fields

    def to_response_headers(self) -> dict[str, str]:
        """Return headers to include in the HTTP response."""
        headers = {}
        if self.correlation_id:
            headers["X-Correlation-ID"] = self.correlation_id
        if self.request_id:
            headers["X-Request-ID"] = self.request_id
        return headers
