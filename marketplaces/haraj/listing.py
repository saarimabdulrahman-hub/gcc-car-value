"""Haraj listing extraction — extract listing cards from search results."""

from browser.dom.document import DOMDocument


class HarajListingExtractor:
    def extract_cards(self, doc: DOMDocument) -> list[dict]:
        """Extract listing cards from Haraj search results. Supports Arabic class names."""
        cards = doc.select("[class*='post'], [class*='listing'], article, [class*='advert']")
        if not cards:
            cards = doc.select("[class*='card'], li, [class*='item']")
        results = []
        for card in cards:
            data = self._extract_card(card)
            if data.get("url"):
                results.append(data)
        return results

    def _extract_card(self, card) -> dict:
        return {
            "url": self._first(card, "a[href*='/haraj/']", attr="href"),
            "title": self._first(card, "h3, [class*='title'], [class*='عنوان']"),
            "price": self._first(card, "[class*='price'], [class*='سعر']"),
            "year": self._first(card, "[class*='year'], [class*='سنة']"),
            "mileage": self._first(card, "[class*='mileage'], [class*='كم']"),
            "location": self._first(card, "[class*='location'], [class*='مدينة']"),
            "image": self._first(card, "img", attr="src"),
        }

    def _first(self, node, css: str, attr: str | None = None) -> str:
        if node is None: return ""
        child = node.select_one(css)
        if child is None: return ""
        if attr: return child.attr(attr, "") or ""
        return child.text_stripped
