"""Text extraction helper — visible text from cleaned HTML."""

from bs4 import BeautifulSoup


def extract_visible_text(soup: BeautifulSoup) -> str:
    """Extract visible text, excluding script/style content."""
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    # Collapse whitespace
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    return text
