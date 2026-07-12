"""Detail extraction — extract full vehicle details from Dubizzle listing pages."""

from browser.dom.document import DOMDocument
from browser.dom.extractors import Extractor


class DubizzleDetailExtractor:
    """Extracts full vehicle details from a Dubizzle listing detail page.

    Uses the DOM Engine — never raw BeautifulSoup or Playwright APIs.
    All extraction goes through typed extractors for validation.
    """

    def __init__(self):
        self._extractor = Extractor()

    def extract(self, doc: DOMDocument) -> dict:
        """Extract all vehicle details from a listing detail page."""
        return {
            "title": self._text(doc, "h1"),
            "make": self._infer_make(doc),
            "model": self._infer_model(doc),
            "year": self._int(doc, "[class*='year']"),
            "price": self._currency(doc, "[class*='price-value'], [class*='amount'], [class*='price']"),
            "mileage_km": self._int(doc, "[class*='mileage'], [class*='km'], [class*='odometer']"),
            "spec": self._text(doc, "[class*='spec'], [class*='regional-spec']"),
            "transmission": self._text(doc, "[class*='transmission']"),
            "fuel_type": self._text(doc, "[class*='fuel']"),
            "body_type": self._text(doc, "[class*='body-type'], [class*='body']"),
            "color": self._text(doc, "[class*='color']"),
            "description": self._text(doc, "[class*='description'], [class*='details']"),
            "seller_name": self._text(doc, "[class*='seller'], [class*='dealer']"),
            "location": self._text(doc, "[class*='location'], [class*='city'], [class*='area']"),
            "images": self._images(doc),
        }

    def _text(self, doc: DOMDocument, css: str, default: str = "") -> str:
        node = doc.select_one(css)
        return node.text_stripped if node else default

    def _int(self, doc: DOMDocument, css: str, default: int = 0) -> int:
        result = self._extractor.integer(doc.select_one(css), default=default)
        return result.value

    def _currency(self, doc: DOMDocument, css: str, default: float = 0.0) -> float:
        result = self._extractor.currency(doc.select_one(css), default=default)
        return result.value

    def _images(self, doc: DOMDocument) -> list[str]:
        nodes = doc.select("[class*='gallery'] img, [class*='carousel'] img, img[src*='dubizzle']")
        return [n.attr("src", "") for n in nodes if n.attr("src")]

    def _infer_make(self, doc: DOMDocument) -> str:
        """Infer make from title or metadata."""
        title = self._text(doc, "h1, [class*='title']")
        if title:
            return title.split()[0] if title.split() else ""
        return ""

    def _infer_model(self, doc: DOMDocument) -> str:
        """Infer model from title."""
        title = self._text(doc, "h1, [class*='title']")
        tokens = title.split()
        return " ".join(tokens[1:3]) if len(tokens) >= 3 else (
            tokens[1] if len(tokens) >= 2 else ""
        )
