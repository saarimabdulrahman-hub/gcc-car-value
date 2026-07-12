"""MetricCollector — abstract base for metric data collectors.

Collectors gather values from application internals and feed them
into the MetricsRegistry. They run on a schedule (push) or are
triggered by application events.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.metrics.registry import MetricsRegistry


class MetricCollector(ABC):
    """Abstract base for metric collectors.

    Subclasses implement collect() to gather data and update registry metrics.
    Collectors are registered with the registry and called on schedule or
    on-demand by metric exporters.
    """

    def __init__(self, registry: "MetricsRegistry", namespace: str = ""):
        self.registry = registry
        self.namespace = namespace

    @abstractmethod
    async def collect(self) -> None:
        """Gather metrics and update the registry.

        Called periodically by the metrics framework or on-demand
        by exporters before export().
        """
        ...

    @abstractmethod
    def name(self) -> str:
        """Human-readable collector name for logging."""
        ...
