class TrainingStatistics:
    def __init__(self): self.runs = 0; self.failures = 0
    def record(self): self.runs += 1
    def record_failure(self): self.failures += 1
    def snapshot(self) -> dict: return {"runs": self.runs, "failures": self.failures}
