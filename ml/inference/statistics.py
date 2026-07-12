class InferenceStatistics:
    def __init__(self): self.predictions = 0; self.failures = 0
    def record(self): self.predictions += 1
    def record_failure(self): self.failures += 1
    def snapshot(self) -> dict:
        return {"predictions": self.predictions, "validation_failures": self.failures}
