"""OpenSooq listing extraction."""

from browser.dom.document import DOMDocument


class OpenSooqListingExtractor:
    def extract_cards(self, doc: DOMDocument) -> list[dict]:
        cards = doc.select("[class*='listing'], [class*='card'], [class*='item'], article")
        if not cards: cards = doc.select("li, [class*='post']")
        return [d for d in (self._extract(c) for c in cards) if d.get("url")]

    def _extract(self, card) -> dict:
        return {
            "url": self._first(card, "a[href*='/vehicles/'], a[href*='/cars/']", attr="href"),
            "title": self._first(card, "[class*='title'], h2, h3"),
            "price": self._first(card, "[class*='price'], [class*='amount']"),
            "year": self._first(card, "[class*='year']"), "mileage": self._first(card, "[class*='mileage'], [class*='km']"),
            "location": self._first(card, "[class*='location'], [class*='city']"), "image": self._first(card, "img", attr="src"),
        }

    def _first(self, node, css: str, attr: str | None = None) -> str:
        if node is None: return ""
        child = node.select_one(css)
        if child is None: return ""
        return child.attr(attr, "") if attr else child.text_stripped
