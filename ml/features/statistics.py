"""Feature store statistics."""

class FeatureStatistics:
    def __init__(self): self.datasets = 0; self.rows = 0; self.failures = 0
    def record_build(self, rows: int): self.datasets += 1; self.rows += rows
    def record_failure(self): self.failures += 1
    def snapshot(self) -> dict:
        return {"datasets_built": self.datasets, "rows_exported": self.rows, "validation_failures": self.failures}
