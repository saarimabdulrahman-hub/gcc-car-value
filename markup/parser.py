"""HTML Parser — re-exports engine.parse for dedicated parser usage."""

from markup.engine import HTMLEngine
from markup.config import HTMLConfig


def parse_html(html: str, parser: str = "lxml"):
    """Quick parse — returns BeautifulSoup without cleaning."""
    engine = HTMLEngine(HTMLConfig(parser=parser))
    return engine.parse(html)
