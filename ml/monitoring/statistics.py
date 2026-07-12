class MonitoringStatistics:
    def __init__(self): self.runs = 0; self.drifts = 0; self.alerts = 0
    def record_run(self): self.runs += 1
    def record_drift(self): self.drifts += 1
    def record_alert(self): self.alerts += 1
    def snapshot(self) -> dict: return {"runs": self.runs, "drifts": self.drifts, "alerts": self.alerts}
