"""Centralized Logger — single entry point for all application logging.

Wraps structlog with category methods (audit, security, performance) and
automatic sensitive data masking. Application code never calls Python's
logging module directly.

Usage:
    from src.core.logging import get_logger

    log = get_logger(__name__)
    log.info("valuation_computed", make="Toyota", estimate=125000)
    log.audit("admin_access", user_id="abc", resource="/admin/stats")
    log.security("auth_failed", ip="1.2.3.4")
    log.performance("db_query", query="SELECT...", execution_time_ms=45.2)
"""

from __future__ import annotations

import time
from typing import Any

import structlog

from src.core.logging.filters import mask_field


class Logger:
    """Structured logger wrapping structlog with category methods.

    Provides standard log levels plus specialized categories:
    - audit()    — for security-relevant events (access, changes)
    - security() — for auth failures, permission denials, rate limits
    - performance() — for timing data (query times, API latency)

    All key-value pairs are automatically passed through sensitive data
    masking before emission.
    """

    def __init__(self, name: str):
        self._logger = structlog.get_logger(name)
        self._name = name

    # ------------------------------------------------------------------
    # Standard log levels
    # ------------------------------------------------------------------

    def trace(self, event: str, **kwargs: Any) -> None:
        self._logger.debug(self._masked_event(event, **kwargs))

    def debug(self, event: str, **kwargs: Any) -> None:
        self._logger.debug(self._masked_event(event, **kwargs))

    def info(self, event: str, **kwargs: Any) -> None:
        self._logger.info(self._masked_event(event, **kwargs))

    def warning(self, event: str, **kwargs: Any) -> None:
        self._logger.warning(self._masked_event(event, **kwargs))

    def error(self, event: str, **kwargs: Any) -> None:
        self._logger.error(self._masked_event(event, **kwargs))

    def critical(self, event: str, **kwargs: Any) -> None:
        self._logger.critical(self._masked_event(event, **kwargs))

    def exception(self, event: str, exc_info: bool = True, **kwargs: Any) -> None:
        self._logger.exception(self._masked_event(event, **kwargs),
                               exc_info=exc_info)

    # ------------------------------------------------------------------
    # Specialized categories
    # ------------------------------------------------------------------

    def audit(self, event: str, **kwargs: Any) -> None:
        """Log a security-relevant event for audit trail.

        Use for: admin actions, data modifications, permission changes,
        model deployments, configuration changes.
        """
        self._logger.info(
            self._masked_event(event, **kwargs),
            category="audit",
        )

    def security(self, event: str, **kwargs: Any) -> None:
        """Log a security event (auth failure, permission denial, rate limit).

        Use for: failed login attempts, authorization denials,
        rate limit hits, suspicious activity.
        """
        self._logger.warning(
            self._masked_event(event, **kwargs),
            category="security",
        )

    def performance(self, event: str, **kwargs: Any) -> None:
        """Log a performance measurement.

        Use for: API latency, DB query times, ML prediction duration,
        scraper run duration, cache timing.
        """
        self._logger.info(
            self._masked_event(event, **kwargs),
            category="performance",
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _masked_event(self, event: str, **kwargs: Any) -> str:
        """Apply sensitive data masking to all kwargs and return the event string.

        The masking is applied here so callers don't need to think about it.
        Structlog processors handle the rest (timestamp, level, etc.).
        """
        # Apply masking — kwargs with sensitive names or values are sanitized
        for key in list(kwargs.keys()):
            kwargs[key] = mask_field(key, kwargs[key])

        # Inject module name for filtering
        kwargs.setdefault("module", self._name)

        return event


# ------------------------------------------------------------------
# Logger factory — the preferred way to get a logger instance
# ------------------------------------------------------------------

_loggers: dict[str, Logger] = {}


def get_logger(name: str) -> Logger:
    """Get or create a Logger instance for the given module name.

    Cached — repeated calls with the same name return the same instance.

    Usage:
        from src.core.logging import get_logger
        log = get_logger(__name__)
    """
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name]
