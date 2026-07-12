class ServingStatistics:
    def __init__(self): self.requests = 0
    def record(self): self.requests += 1
    def snapshot(self) -> dict: return {"requests": self.requests}
