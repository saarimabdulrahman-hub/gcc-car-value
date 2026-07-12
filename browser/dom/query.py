"""Query helpers — CSS selector utilities."""

from browser.dom.document import DOMDocument
from browser.dom.node import DOMNode


def query_text(doc: DOMDocument, css: str, default: str = "") -> str:
    """Query the first matching element and return its stripped text."""
    node = doc.select_one(css)
    return node.text_stripped if node else default


def query_all_text(doc: DOMDocument, css: str) -> list[str]:
    """Query all matching elements and return their stripped text."""
    return [n.text_stripped for n in doc.select(css)]


def query_attr(doc: DOMDocument, css: str, attr_name: str,
               default: str | None = None) -> str | None:
    """Query the first matching element and return an attribute value."""
    node = doc.select_one(css)
    return node.attr(attr_name, default) if node else default


def query_exists(doc: DOMDocument, css: str) -> bool:
    return doc.exists(css)


def query_count(doc: DOMDocument, css: str) -> int:
    return doc.count(css)
