"""Pipeline statistics tracker."""

import time


class PipelineStatistics:
    def __init__(self):
        self._start_time = 0.0
        self._end_time = 0.0
        self.pages_crawled = 0
        self.listings_found = 0
        self.listings_processed = 0
        self.failures = 0

    def start(self): self._start_time = time.time()
    def finish(self): self._end_time = time.time()

    def record_page(self): self.pages_crawled += 1
    def record_listings_found(self, n): self.listings_found += n
    def record_listing_processed(self): self.listings_processed += 1
    def record_failure(self): self.failures += 1

    @property
    def duration_ms(self) -> float:
        return (self._end_time - self._start_time) * 1000 if self._end_time else 0.0

    def snapshot(self) -> dict:
        return {
            "pages_crawled": self.pages_crawled,
            "listings_found": self.listings_found,
            "listings_processed": self.listings_processed,
            "failures": self.failures,
            "duration_ms": self.duration_ms,
            "success_rate": (self.listings_processed / max(self.listings_found, 1)) * 100,
        }
