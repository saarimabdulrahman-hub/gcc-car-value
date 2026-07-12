"""MetricExporter — abstract base for all metric exporters.

Exporters pull metrics from the registry and publish them to an external
system. The registry is exporter-agnostic — it never calls exporters directly.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.metrics.registry import MetricsRegistry


class MetricExporter(ABC):
    """Abstract base for metric exporters.

    Subclasses implement export() to publish metrics to a specific system.
    Exporters are responsible for their own scheduling (push vs pull).
    """

    def __init__(self, registry: "MetricsRegistry"):
        self.registry = registry

    @abstractmethod
    async def export(self) -> None:
        """Collect metrics from registry and publish them.

        Called on a schedule (push) or on-demand (pull via /metrics).
        Must be implemented by each exporter.
        """
        ...

    @abstractmethod
    def format_name(self) -> str:
        """Human-readable exporter name for logging."""
        ...

    async def shutdown(self) -> None:
        """Cleanup resources before application shutdown."""
        pass
