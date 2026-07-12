"""Trace exporters — pluggable backends for span data."""

from src.core.tracing.exporters.base import TraceExporter

__all__ = ["TraceExporter"]
