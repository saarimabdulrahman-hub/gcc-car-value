"""Enterprise structured logging framework.

Centralized Logger that wraps structlog with:
    - JSON formatting (production) / console (development)
    - Log categories: audit, security, performance
    - Sensitive data masking
    - Context support (request_id, user_id, etc.)
    - Thread-safe async-compatible operation

Usage:
    from src.core.logging import get_logger

    log = get_logger(__name__)
    log.info("valuation_computed", make="Toyota", estimate=125000)
    log.audit("admin_access", user_id="abc", resource="/admin/stats")
    log.security("auth_failed", ip="1.2.3.4")
"""

from src.core.logging.config import configure_logging
from src.core.logging.logger import get_logger, Logger

__all__ = ["configure_logging", "get_logger", "Logger"]
