"""Fallback chain utilities."""

from browser.selectors.models import Selector


def build_fallback_chain(css: str, *fallbacks: str,
                         name: str = "", marketplace: str = "",
                         group: str = "", **kwargs) -> Selector:
    """Build a selector with a primary CSS and fallback chain."""
    return Selector(
        name=name, css=css, fallbacks=list(fallbacks),
        marketplace=marketplace, group=group,
        **kwargs,
    )
