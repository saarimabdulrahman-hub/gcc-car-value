"""Whitespace normalizer — collapse multiple spaces, blank lines, Unicode whitespace."""

import re


class WhitespaceNormalizer:
    """Normalizes whitespace in text content while preserving semantic structure.

    Does NOT modify HTML structure — only normalizes text within elements.
    """

    def normalize(self, text: str) -> str:
        """Normalize whitespace in a text string.

        - Replaces Unicode non-breaking spaces with regular spaces
        - Collapses multiple whitespace chars to a single space
        - Strips leading/trailing whitespace
        - Preserves meaningful line breaks
        """
        if not text:
            return text

        # Replace non-breaking spaces and other Unicode whitespace
        text = text.replace(' ', ' ')  # &nbsp;
        text = text.replace('​', '')    # zero-width space
        text = text.replace('\t', ' ')       # tabs → space

        # Collapse multiple spaces (but not newlines)
        text = re.sub(r'[ \f\r\v]+', ' ', text)

        # Collapse multiple blank lines (keep at most 1 consecutive newline)
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Strip leading/trailing whitespace
        return text.strip()

    def normalize_document_text(self, soup) -> None:
        """Normalize text in all text-containing elements of a BeautifulSoup tree."""
        for el in soup.find_all(string=True):
            if el.parent and el.parent.name not in ("script", "style", "code", "pre"):
                text = self.normalize(str(el))
                el.replace_with(text)
