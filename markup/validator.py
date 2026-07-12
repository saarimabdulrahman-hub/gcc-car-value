"""HTML Validator — re-exports engine.validate."""

from markup.engine import HTMLEngine
from markup.config import HTMLConfig


def validate_html(html: str) -> list[str]:
    engine = HTMLEngine(HTMLConfig())
    soup = engine.parse(html)
    return engine.validate(soup)
