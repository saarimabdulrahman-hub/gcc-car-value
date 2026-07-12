"""DOM Engine — the main entry point for DOM extraction.

Marketplace scrapers use this engine instead of calling BeautifulSoup,
Playwright, or Selenium APIs directly. The engine creates DOMDocuments
from HTML strings, which can be obtained from any browser driver.

Usage:
    from browser.dom import DOMEngine
    engine = DOMEngine()
    doc = engine.parse(html_string, url="https://...")
    title = engine.extract(doc).text(doc.select_one("h1")).value
    price = engine.extract(doc).currency(doc.select_one(".price")).value
"""

from browser.dom.document import DOMDocument
from browser.dom.extractors import Extractor
from browser.dom.validation import ExtractionValidator
from browser.dom.config import DOMConfig


class DOMEngine:
    """Central DOM extraction engine.

    Wraps document creation, extraction, and validation behind a single API.
    Scrapers interact only with this engine — never with BeautifulSoup directly.
    """

    def __init__(self, config: DOMConfig | None = None):
        self.config = config or DOMConfig()

    # ------------------------------------------------------------------
    # Document creation
    # ------------------------------------------------------------------

    def parse(self, html: str, url: str = "") -> DOMDocument:
        """Parse raw HTML into a DOMDocument."""
        return DOMDocument.from_html(
            html, url=url, parser=self.config.parser
        )

    # ------------------------------------------------------------------
    # Extraction
    # ------------------------------------------------------------------

    def extract(self, doc: DOMDocument) -> Extractor:
        """Return an Extractor bound to this document context.
        Usage: engine.extract(doc).text(node).value"""
        return Extractor()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> ExtractionValidator:
        """Return a validator for extraction results."""
        return ExtractionValidator()

    def validate_selectors(self, doc: DOMDocument,
                           selectors: dict[str, str]) -> list[str]:
        """Check that all required selectors exist. Returns missing field names."""
        return ExtractionValidator.validate_selectors(doc, selectors)
