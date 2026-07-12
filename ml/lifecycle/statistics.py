class LifecycleStatistics:
    def __init__(self): self.workflows = 0; self.completions = 0; self.failures = 0; self.rollbacks = 0
    def record_workflow(self): self.workflows += 1
    def record_completion(self): self.completions += 1
    def record_failure(self): self.failures += 1
    def record_rollback(self): self.rollbacks += 1
    def snapshot(self) -> dict:
        return {"workflows": self.workflows, "completed": self.completions,
                "failed": self.failures, "rolled_back": self.rollbacks}
