"""Pagination — first/next page, last page detection, checkpoint resume."""

from marketplaces.dubizzle.config import DubizzleConfig
from marketplaces.dubizzle.errors import PaginationExhaustedError


class DubizzlePagination:
    """Handles page-by-page traversal of Dubizzle search results.

    Tracks current page, detects last page, respects max_pages.
    Supports checkpoint resume from a previously saved state.
    """

    def __init__(self, config: DubizzleConfig | None = None):
        self.config = config or DubizzleConfig()
        self._current_page = 0
        self._pages_processed = 0
        self._last_page = False
        self._total_listings_found = 0

    @property
    def current_page(self) -> int:
        return self._current_page

    @property
    def is_exhausted(self) -> bool:
        return self._last_page or self._pages_processed >= self.config.max_pages

    def start(self, resume_from: int = 1) -> None:
        """Start or resume pagination from a given page."""
        self._current_page = resume_from - 1
        self._pages_processed = 0
        self._last_page = False

    def next_page(self) -> int:
        """Advance to the next page. Returns the new page number.

        Raises PaginationExhaustedError if no more pages are available.
        """
        if self.is_exhausted:
            raise PaginationExhaustedError("No more pages")

        self._current_page += 1
        self._pages_processed += 1
        return self._current_page

    def mark_last_page(self) -> None:
        """Mark that the last page has been reached (no next link found)."""
        self._last_page = True

    def record_listings(self, count: int) -> None:
        self._total_listings_found += count

    def checkpoint_state(self) -> dict:
        """Return current state for checkpointing."""
        return {
            "current_page": self._current_page,
            "pages_processed": self._pages_processed,
            "last_page": self._last_page,
            "total_listings": self._total_listings_found,
        }

    def restore_state(self, state: dict) -> None:
        """Restore from a checkpoint."""
        self._current_page = state.get("current_page", 0)
        self._pages_processed = state.get("pages_processed", 0)
        self._last_page = state.get("last_page", False)
        self._total_listings_found = state.get("total_listings", 0)
