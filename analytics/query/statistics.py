"""Analytics statistics tracker."""

class QueryStatistics:
    def __init__(self): self._count = 0; self._total_ms = 0.0
    def record(self, ms): self._count += 1; self._total_ms += ms
    @property
    def avg_latency(self) -> float: return self._total_ms / max(self._count, 1)
