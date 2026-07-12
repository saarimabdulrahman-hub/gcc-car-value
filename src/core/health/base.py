"""Health check abstractions — status enum, result dataclass, check interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
import time


class HealthStatus(StrEnum):
    HEALTHY   = "healthy"
    DEGRADED  = "degraded"
    UNHEALTHY = "unhealthy"


class CheckSeverity(StrEnum):
    CRITICAL = "critical"  # Failure → overall status UNHEALTHY
    OPTIONAL = "optional"  # Failure → overall status DEGRADED


@dataclass
class CheckResult:
    """Result of a single health check execution."""
    name: str
    status: HealthStatus
    severity: CheckSeverity = CheckSeverity.CRITICAL
    duration_ms: float = 0.0
    details: dict = field(default_factory=dict)
    error: str | None = None
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def healthy(cls, name: str, severity: CheckSeverity = CheckSeverity.CRITICAL,
                duration_ms: float = 0.0, **details) -> "CheckResult":
        return cls(name=name, status=HealthStatus.HEALTHY, severity=severity,
                   duration_ms=duration_ms, details=details)

    @classmethod
    def degraded(cls, name: str, severity: CheckSeverity = CheckSeverity.OPTIONAL,
                 error: str | None = None, duration_ms: float = 0.0,
                 **details) -> "CheckResult":
        return cls(name=name, status=HealthStatus.DEGRADED, severity=severity,
                   error=error, duration_ms=duration_ms, details=details)

    @classmethod
    def unhealthy(cls, name: str, error: str,
                  severity: CheckSeverity = CheckSeverity.CRITICAL,
                  duration_ms: float = 0.0, **details) -> "CheckResult":
        return cls(name=name, status=HealthStatus.UNHEALTHY, severity=severity,
                   error=error, duration_ms=duration_ms, details=details)


class HealthCheck(ABC):
    """Abstract health check. Each dependency registers one.

    Subclasses implement check() which returns a CheckResult.
    The registry handles timeout, error catching, and aggregation.
    """

    def __init__(self, name: str, severity: CheckSeverity = CheckSeverity.CRITICAL,
                 timeout_seconds: float = 5.0):
        self.name = name
        self.severity = severity
        self.timeout_seconds = timeout_seconds

    @abstractmethod
    async def check(self) -> CheckResult:
        """Execute the health check. Must not raise — catch and return unhealthy."""
        ...
