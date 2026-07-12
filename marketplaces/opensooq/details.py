"""OpenSooq detail extraction."""

from browser.dom.document import DOMDocument
from browser.dom.extractors import Extractor


class OpenSooqDetailExtractor:
    def __init__(self): self._extractor = Extractor()

    def extract(self, doc: DOMDocument) -> dict:
        return {
            "title": self._t(doc, "h1, [class*='title']"),
            "make": self._infer_make(doc), "model": self._infer_model(doc),
            "year": self._i(doc, "[class*='year']"), "price": self._c(doc, "[class*='price'], [class*='amount']"),
            "mileage_km": self._i(doc, "[class*='mileage'], [class*='km']"),
            "spec": self._t(doc, "[class*='spec']"), "transmission": self._t(doc, "[class*='transmission']"),
            "fuel_type": self._t(doc, "[class*='fuel']"), "body_type": self._t(doc, "[class*='body']"),
            "color": self._t(doc, "[class*='color']"), "description": self._t(doc, "[class*='description']"),
            "seller_name": self._t(doc, "[class*='seller'], [class*='dealer']"),
            "location": self._t(doc, "[class*='location'], [class*='city']"),
            "images": self._img(doc),
        }

    def _t(self, doc, css, d=""): n = doc.select_one(css); return n.text_stripped if n else d
    def _i(self, doc, css, d=0): return self._extractor.integer(doc.select_one(css), default=d).value
    def _c(self, doc, css, d=0.0): return self._extractor.currency(doc.select_one(css), default=d).value
    def _img(self, doc): return [n.attr("src", "") for n in doc.select("[class*='gallery'] img, img[src*='opensooq']") if n.attr("src")]
    def _infer_make(self, doc): t = self._t(doc, "h1"); return t.split()[0] if t else ""
    def _infer_model(self, doc): t = self._t(doc, "h1"); toks = t.split(); return " ".join(toks[1:3]) if len(toks) >= 3 else (toks[1] if len(toks) >= 2 else "")
