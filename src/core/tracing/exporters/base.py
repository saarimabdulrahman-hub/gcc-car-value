"""TraceExporter — abstract base for span exporters."""

from abc import ABC, abstractmethod


class TraceExporter(ABC):
    """Abstract trace exporter. Subclasses implement export() for specific backends.

    Built-in implementations:
        OtlpExporter  — OTLP/gRPC to Jaeger, Tempo, etc.
        ConsoleExporter — stdout for development
    """

    @abstractmethod
    def export(self, spans: list) -> None:
        """Export a batch of spans to the backend."""
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Flush and shutdown the exporter."""
        ...
