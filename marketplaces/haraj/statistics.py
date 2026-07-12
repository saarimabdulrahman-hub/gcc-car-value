"""Haraj pipeline statistics."""

import time

class HarajStatistics:
    def __init__(self): self._start = 0.0; self._end = 0.0; self.pages = 0; self.found = 0; self.processed = 0; self.failures = 0
    def start(self): self._start = time.time()
    def finish(self): self._end = time.time()
    def record_page(self): self.pages += 1
    def record_found(self, n): self.found += n
    def record_processed(self): self.processed += 1
    def record_failure(self): self.failures += 1
    @property
    def duration_ms(self) -> float: return (self._end - self._start) * 1000 if self._end else 0.0
    def snapshot(self) -> dict:
        return {"pages_crawled": self.pages, "listings_found": self.found,
                "listings_processed": self.processed, "failures": self.failures,
                "duration_ms": self.duration_ms,
                "success_rate": (self.processed / max(self.found, 1)) * 100}
