"""Prometheus text format serializer.

Converts Metric objects from the registry into the Prometheus exposition
format (text/plain; version=0.0.4). Handles all metric types supported
by the framework: Counter, Gauge, Histogram, Timer, Info.

Naming convention:
    namespace.name → namespace_name{,_total,_bucket,_sum,_count,_info,_created}
    Tags become Prometheus labels: {key="value", ...}
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.metrics.types import Metric

# Prometheus content type
CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"


def format_metrics(metrics: list["Metric"]) -> str:
    """Serialize a list of Metric objects into Prometheus text format.

    Args:
        metrics: List of Metric objects from registry.collect_all().

    Returns:
        Prometheus exposition format string, ready for the /metrics endpoint.
    """
    lines: list[str] = []
    for metric in metrics:
        lines.extend(_format_metric(metric))
    return "\n".join(lines) + "\n"


def _format_metric(metric: "Metric") -> list[str]:
    """Route to the correct formatter based on metric type."""
    from src.core.metrics.types import Counter, Gauge, Histogram, Info

    if isinstance(metric, Counter):
        return _format_counter(metric)
    elif isinstance(metric, Gauge):
        return _format_gauge(metric)
    elif isinstance(metric, Histogram):
        return _format_histogram(metric)
    elif isinstance(metric, Info):
        return _format_info(metric)
    else:
        # Unknown type — emit as untyped
        return _format_untyped(metric)


# ------------------------------------------------------------------
# Name conversion
# ------------------------------------------------------------------

def _prometheus_name(metric: "Metric", suffix: str = "") -> str:
    """Convert namespace.name to Prometheus-compatible metric name.

    Dots become underscores. Suffix is appended (e.g., '_total' for counters).
    Colons and hyphens are replaced with underscores.
    """
    name = metric.full_name.replace(".", "_").replace(":", "_").replace("-", "_")
    if suffix:
        name = f"{name}{suffix}"
    return name


def _format_labels(tags: dict[str, str]) -> str:
    """Format tags as Prometheus label string: {key="value", ...}."""
    if not tags:
        return ""
    parts = [f'{k}="{v}"' for k, v in sorted(tags.items())]
    return "{" + ",".join(parts) + "}"


def _format_line(name: str, tags: dict[str, str], value: float,
                 timestamp: float | None = None) -> str:
    """Format a single Prometheus metric line: name{labels} value [timestamp]."""
    labels = _format_labels(tags)
    line = f"{name}{labels} {_format_value(value)}"
    if timestamp is not None:
        line += f" {int(timestamp * 1000)}"
    return line


def _format_value(value: float) -> str:
    """Format a float value for Prometheus exposition."""
    if value == float("inf"):
        return "+Inf"
    if value == float("-inf"):
        return "-Inf"
    if value != value:  # NaN
        return "Nan"
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


# ------------------------------------------------------------------
# Type-specific formatters
# ------------------------------------------------------------------

def _format_counter(metric: "Counter") -> list[str]:
    """Counter → metric_total line(s) + optional HELP/TYPE."""
    from src.core.metrics.types import MetricValue
    name = _prometheus_name(metric, "_total")
    lines = [
        f"# HELP {name} {metric.description or metric.full_name}",
        f"# TYPE {name} counter",
    ]
    for val in metric.collect():
        lines.append(_format_line(name, val.tags, val.value))
    return lines


def _format_gauge(metric: "Gauge") -> list[str]:
    """Gauge → metric line(s)."""
    name = _prometheus_name(metric)
    lines = [
        f"# HELP {name} {metric.description or metric.full_name}",
        f"# TYPE {name} gauge",
    ]
    for val in metric.collect():
        lines.append(_format_line(name, val.tags, val.value))
    return lines


def _format_histogram(metric: "Histogram") -> list[str]:
    """Histogram → _bucket, _sum, _count metric families.

    Prometheus histogram format requires:
        metric_bucket{le="..."} value
        metric_sum value
        metric_count value
        [optional] metric_created timestamp
    """
    name = _prometheus_name(metric)
    lines = [
        f"# HELP {name} {metric.description or metric.full_name}",
        f"# TYPE {name} histogram",
    ]

    values = metric.collect()
    base_tags: dict[str, str] = {}

    for val in values:
        stat = val.tags.get("stat", "")
        le = val.tags.get("le", "")

        if le:
            # Bucket: metric_bucket{le="..."} value
            bucket_tags = {k: v for k, v in val.tags.items()
                          if k not in ("stat", "le")}
            bucket_tags["le"] = le
            lines.append(_format_line(f"{name}_bucket", bucket_tags, val.value))
        elif stat == "sum":
            # Total sum: metric_sum value
            sum_tags = {k: v for k, v in val.tags.items() if k != "stat"}
            lines.append(_format_line(f"{name}_sum", sum_tags, val.value))
        elif stat == "count":
            # Observation count: metric_count value
            count_tags = {k: v for k, v in val.tags.items() if k != "stat"}
            lines.append(_format_line(f"{name}_count", count_tags, val.value))
        else:
            # Base tags for the HELP/TYPE
            if not base_tags:
                base_tags = {k: v for k, v in val.tags.items()
                           if k not in ("stat", "le")}

    return lines


def _format_info(metric: "Info") -> list[str]:
    """Info → metric_info gauge with info labels."""
    name = _prometheus_name(metric, "_info")
    lines = [
        f"# HELP {name} {metric.description or metric.full_name}",
        f"# TYPE {name} gauge",
    ]
    for val in metric.collect():
        lines.append(_format_line(name, val.tags, 1.0))
    return lines


def _format_untyped(metric: "Metric") -> list[str]:
    """Fallback for unknown metric types — emit as untyped."""
    name = _prometheus_name(metric)
    lines = [
        f"# HELP {name} {metric.description or metric.full_name}",
        f"# TYPE {name} untyped",
    ]
    for val in metric.collect():
        lines.append(_format_line(name, val.tags, val.value))
    return lines
