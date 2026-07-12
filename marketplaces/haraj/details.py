"""Haraj detail extraction — extract full vehicle details from listing pages."""

from browser.dom.document import DOMDocument
from browser.dom.extractors import Extractor


class HarajDetailExtractor:
    def __init__(self):
        self._extractor = Extractor()

    def extract(self, doc: DOMDocument) -> dict:
        return {
            "title": self._text(doc, "h1, [class*='title'], [class*='عنوان']"),
            "make": self._infer_make(doc),
            "model": self._infer_model(doc),
            "year": self._int(doc, "[class*='year'], [class*='سنة']"),
            "price": self._currency(doc, "[class*='price'], [class*='سعر']"),
            "mileage_km": self._int(doc, "[class*='mileage'], [class*='كم'], [class*='ممشى']"),
            "spec": self._text(doc, "[class*='spec'], [class*='مواصفات']"),
            "transmission": self._text(doc, "[class*='transmission'], [class*='ناقل'], [class*='جير']"),
            "fuel_type": self._text(doc, "[class*='fuel'], [class*='وقود'], [class*='بنزين']"),
            "body_type": self._text(doc, "[class*='body'], [class*='نوع']"),
            "color": self._text(doc, "[class*='color'], [class*='لون']"),
            "description": self._text(doc, "[class*='description'], [class*='وصف']"),
            "seller_name": self._text(doc, "[class*='seller'], [class*='بائع'], [class*='معلن']"),
            "location": self._text(doc, "[class*='location'], [class*='مدينة'], [class*='city']"),
            "images": self._images(doc),
        }

    def _text(self, doc, css: str, default: str = "") -> str:
        n = doc.select_one(css); return n.text_stripped if n else default
    def _int(self, doc, css: str, default: int = 0) -> int:
        r = self._extractor.integer(doc.select_one(css), default=default); return r.value
    def _currency(self, doc, css: str, default: float = 0.0) -> float:
        r = self._extractor.currency(doc.select_one(css), default=default); return r.value
    def _images(self, doc) -> list[str]:
        ns = doc.select("[class*='gallery'] img, [class*='photo'] img, img[src*='haraj']")
        return [n.attr("src", "") for n in ns if n.attr("src")]
    def _infer_make(self, doc) -> str:
        t = self._text(doc, "h1, [class*='title']"); return t.split()[0] if t else ""
    def _infer_model(self, doc) -> str:
        t = self._text(doc, "h1, [class*='title']"); toks = t.split()
        return " ".join(toks[1:3]) if len(toks) >= 3 else (toks[1] if len(toks) >= 2 else "")
