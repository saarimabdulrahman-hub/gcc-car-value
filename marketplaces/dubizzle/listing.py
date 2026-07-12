"""Listing extraction — extract listing cards from Dubizzle search result pages.

Uses the Selector Framework + DOM Engine — never raw CSS or BS4 directly.
"""

from browser.dom.document import DOMDocument
from browser.dom.extractors import Extractor
from browser.selectors.compiler import SelectorCompiler
from browser.selectors.models import Selector


class DubizzleListingExtractor:
    """Extracts listing summaries from Dubizzle search result pages.

    Each listing card contains: url, title, price, year, mileage, location.
    Detail extraction happens separately on the listing detail page.
    """

    def __init__(self):
        self._compiler = SelectorCompiler()
        self._extractor = Extractor()

    def extract_cards(self, doc: DOMDocument) -> list[dict]:
        """Extract all listing cards from a search results page."""
        cards = doc.select("[class*='listing-card'], article.listing, li[class*='listing']")
        if not cards:
            # Fallback: try broader card selectors
            cards = doc.select("[class*='card'], article, [class*='item']")

        results = []
        for card in cards:
            data = self._extract_card(card)
            if data.get("url"):  # At minimum, we need a URL
                results.append(data)
        return results

    def _extract_card(self, card) -> dict:
        """Extract fields from a single listing card."""
        return {
            "url": self._first_text(card, "a[href*='/motors/']", attr="href"),
            "title": self._first_text(card, "h2, h3, [class*='title']"),
            "price": self._first_text(card, "[class*='price']"),
            "year": self._first_text(card, "[class*='year']"),
            "mileage": self._first_text(card, "[class*='mileage'], [class*='km']"),
            "location": self._first_text(card, "[class*='location'], [class*='city']"),
            "image": self._first_text(card, "img", attr="src"),
        }

    def _first_text(self, node, css: str, attr: str | None = None) -> str:
        """Extract text (or attribute) from the first matching child node."""
        if node is None:
            return ""
        child = node.select_one(css)
        if child is None:
            return ""
        if attr:
            return child.attr(attr, "") or ""
        return child.text_stripped
