"""DOMDocument — wraps a parsed HTML document with query and navigation capabilities."""

from bs4 import BeautifulSoup
from browser.dom.node import DOMNode
from browser.dom.models import DocumentStats


class DOMDocument:
    """A parsed HTML document. Provides CSS query, text extraction,
    and document-level metadata.

    Backend: BeautifulSoup4 (default parser: lxml).

    Usage:
        doc = DOMDocument.from_html("<html>...</html>")
        title = doc.select_one("h1").text_stripped
        links = doc.select("a[href]")
    """

    def __init__(self, soup: BeautifulSoup, url: str = ""):
        self._soup = soup
        self.url = url
        self._root = DOMNode(soup)

    @classmethod
    def from_html(cls, html: str, url: str = "",
                  parser: str = "lxml") -> "DOMDocument":
        """Parse an HTML string into a DOMDocument."""
        soup = BeautifulSoup(html, parser)
        return cls(soup, url=url)

    # --- Metadata ---

    @property
    def title(self) -> str:
        tag = self._soup.title
        return tag.get_text(strip=True) if tag else ""

    @property
    def text(self) -> str:
        return self._soup.get_text()

    # --- Root ---

    @property
    def root(self) -> DOMNode:
        return self._root

    # --- Query API ---

    def select(self, css: str) -> list[DOMNode]:
        """Return all elements matching the CSS selector."""
        results = self._soup.select(css)
        return [DOMNode(r) for r in results]

    def select_one(self, css: str) -> DOMNode | None:
        """Return the first element matching the CSS selector, or None."""
        el = self._soup.select_one(css)
        return DOMNode(el) if el else None

    def exists(self, css: str) -> bool:
        """Check if any element matches the CSS selector."""
        return self._soup.select_one(css) is not None

    def count(self, css: str) -> int:
        """Return the number of elements matching the CSS selector."""
        return len(self._soup.select(css))

    # --- Statistics ---

    @property
    def stats(self) -> DocumentStats:
        return DocumentStats(
            node_count=len(self._soup.find_all()),
            text_length=len(self._soup.get_text()),
            links_count=self.count("a[href]"),
            images_count=self.count("img"),
            forms_count=self.count("form"),
            tables_count=self.count("table"),
        )
