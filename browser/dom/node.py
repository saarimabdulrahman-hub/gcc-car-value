"""DOMNode — wraps a single HTML element with unified accessors.

Backend-agnostic: wraps BeautifulSoup Tag objects but the API is the same
regardless of the underlying parser (lxml, html.parser, Playwright element).
"""

from __future__ import annotations


class DOMNode:
    """A single DOM element. Wraps BeautifulSoup Tag or similar.

    Provides a unified interface for tag name, text, attributes, children,
    and CSS selection. Marketplace scrapers interact only with this class,
    never with raw BeautifulSoup or Playwright objects.
    """

    def __init__(self, element):
        """element: BeautifulSoup Tag or compatible object."""
        self._el = element

    # --- Identity ---

    @property
    def tag_name(self) -> str:
        return getattr(self._el, 'name', '')

    @property
    def text(self) -> str:
        return self._el.get_text(strip=False) if hasattr(self._el, 'get_text') else str(self._el)

    @property
    def text_stripped(self) -> str:
        return self._el.get_text(strip=True) if hasattr(self._el, 'get_text') else str(self._el).strip()

    # --- Attributes ---

    def attr(self, name: str, default: str | None = None) -> str | None:
        """Get an attribute value by name."""
        if hasattr(self._el, 'get'):
            return self._el.get(name, default)
        return default

    @property
    def attrs(self) -> dict[str, str]:
        return dict(getattr(self._el, 'attrs', {}))

    # --- Navigation ---

    @property
    def children(self) -> list[DOMNode]:
        els = getattr(self._el, 'children', [])
        return [DOMNode(c) for c in els if hasattr(c, 'name')]

    @property
    def parent(self) -> DOMNode | None:
        p = getattr(self._el, 'parent', None)
        return DOMNode(p) if p and hasattr(p, 'name') else None

    # --- Query ---

    def select(self, css: str) -> list[DOMNode]:
        """Run a CSS selector query on this node's subtree."""
        results = getattr(self._el, 'select', lambda _: [])(css)
        return [DOMNode(r) for r in results]

    def select_one(self, css: str) -> DOMNode | None:
        """Return the first element matching the CSS selector, or None."""
        results = self.select(css)
        return results[0] if results else None

    # --- Visibility ---

    @property
    def is_visible(self) -> bool:
        """Heuristic visibility check — not hidden by common patterns."""
        style = (self.attr('style') or '').lower()
        if 'display:none' in style or 'visibility:hidden' in style:
            return False
        if self.attr('type') == 'hidden':
            return False
        return True
