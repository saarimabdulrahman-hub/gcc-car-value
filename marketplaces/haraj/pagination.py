"""Haraj pagination handler."""

from marketplaces.haraj.config import HarajConfig
from marketplaces.haraj.errors import PaginationExhaustedError


class HarajPagination:
    def __init__(self, config: HarajConfig | None = None):
        self.config = config or HarajConfig()
        self._page = 0; self._processed = 0; self._last = False; self._total = 0

    @property
    def current_page(self) -> int: return self._page
    @property
    def is_exhausted(self) -> bool: return self._last or self._processed >= self.config.max_pages

    def start(self, resume_from: int = 1): self._page = resume_from - 1; self._processed = 0; self._last = False
    def next_page(self) -> int:
        if self.is_exhausted: raise PaginationExhaustedError("No more pages")
        self._page += 1; self._processed += 1; return self._page
    def mark_last_page(self): self._last = True
    def record_listings(self, count: int): self._total += count

    def checkpoint_state(self) -> dict:
        return {"current_page": self._page, "pages_processed": self._processed,
                "last_page": self._last, "total_listings": self._total}
    def restore_state(self, state: dict):
        self._page = state.get("current_page", 0); self._processed = state.get("pages_processed", 0)
        self._last = state.get("last_page", False); self._total = state.get("total_listings", 0)
