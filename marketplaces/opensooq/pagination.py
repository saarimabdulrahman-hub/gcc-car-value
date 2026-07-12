"""OpenSooq pagination."""
from marketplaces.opensooq.config import OpenSooqConfig
from marketplaces.opensooq.errors import PaginationExhaustedError

class OpenSooqPagination:
    def __init__(self, config=None): self.config = config or OpenSooqConfig(); self._page = 0; self._processed = 0; self._last = False
    @property
    def current_page(self) -> int: return self._page
    @property
    def is_exhausted(self) -> bool: return self._last or self._processed >= self.config.max_pages
    def start(self, rf=1): self._page = rf - 1; self._processed = 0; self._last = False
    def next_page(self) -> int:
        if self.is_exhausted: raise PaginationExhaustedError(); self._page += 1; self._processed += 1; return self._page
    def mark_last_page(self): self._last = True
    def checkpoint_state(self) -> dict: return {"page": self._page, "processed": self._processed, "last": self._last}
    def restore_state(self, s): self._page = s.get("page", 0); self._processed = s.get("processed", 0); self._last = s.get("last", False)
