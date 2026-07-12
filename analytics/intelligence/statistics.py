class IntelligenceStatistics:
    def __init__(self): self.indexes = 0; self.benchmarks = 0; self.depreciation = 0; self.liquidity = 0
    def record_index(self): self.indexes += 1
    def record_benchmark(self): self.benchmarks += 1
    def snapshot(self) -> dict:
        return {"indexes_generated": self.indexes, "benchmarks_generated": self.benchmarks}
