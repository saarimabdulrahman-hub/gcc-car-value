"""Attribute extraction helpers."""

from browser.dom.node import DOMNode


def extract_attr(node: DOMNode | None, name: str,
                 default: str | None = None) -> str | None:
    """Extract an attribute value from a node."""
    if node is None:
        return default
    return node.attr(name, default)


def extract_href(node: DOMNode | None) -> str | None:
    return extract_attr(node, "href")

def extract_src(node: DOMNode | None) -> str | None:
    return extract_attr(node, "src")

def extract_alt(node: DOMNode | None) -> str | None:
    return extract_attr(node, "alt")

def extract_title_attr(node: DOMNode | None) -> str | None:
    return extract_attr(node, "title")

def extract_class(node: DOMNode | None) -> str | None:
    return extract_attr(node, "class")

def extract_data(node: DOMNode | None, key: str) -> str | None:
    """Extract a data-* attribute. key='price' → data-price."""
    return extract_attr(node, f"data-{key}")
