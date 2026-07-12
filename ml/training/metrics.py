"""Training metrics collector."""

class MetricsCollector:
    def __init__(self): self.runs = 0; self.successes = 0; self.failures = 0
    def record_success(self): self.runs += 1; self.successes += 1
    def record_failure(self): self.runs += 1; self.failures += 1
    def snapshot(self) -> dict:
        return {"total_runs": self.runs, "successful": self.successes, "failed": self.failures}
