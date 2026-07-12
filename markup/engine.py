"""HTML Engine — orchestrates parsing, cleaning, validation, and metadata extraction."""

import time
from bs4 import BeautifulSoup
from markup.config import HTMLConfig
from markup.cleaner import HTMLCleaner
from markup.whitespace import WhitespaceNormalizer
from markup.metadata import MetadataExtractor
from markup.models import CleaningReport, HTMLMetadata
from markup.errors import ParseError, ValidationError


class HTMLEngine:
    """Central HTML normalization engine.

    Usage:
        engine = HTMLEngine()
        soup, report = engine.process(html_string)
        # soup is a clean, normalized BeautifulSoup document
        # report contains cleaning statistics and metadata
    """

    def __init__(self, config: HTMLConfig | None = None):
        self.config = config or HTMLConfig()
        self._cleaner = HTMLCleaner(
            remove_scripts=self.config.remove_scripts,
            remove_styles=self.config.remove_styles,
            remove_comments=self.config.remove_comments,
            detect_hidden=self.config.detect_hidden,
        )
        self._whitespace = WhitespaceNormalizer()
        self._metadata = MetadataExtractor()

    # ------------------------------------------------------------------
    # Main pipeline
    # ------------------------------------------------------------------

    def process(self, html: str, url: str = "") -> tuple[BeautifulSoup, CleaningReport]:
        """Parse → clean → normalize → report.

        Returns (cleaned_soup, CleaningReport).
        """
        start = time.perf_counter()
        report = CleaningReport(original_size=len(html.encode("utf-8")))

        # 1. Parse
        soup = self.parse(html)

        # 2. Validate
        errors = self.validate(soup)
        report.validation_errors = errors

        # 3. Clean
        counts = self._cleaner.clean(soup)
        report.scripts_removed = counts["scripts_removed"]
        report.styles_removed = counts["styles_removed"]
        report.comments_removed = counts["comments_removed"]
        report.hidden_nodes_found = counts["hidden_nodes_found"]

        # 4. Whitespace normalization
        if self.config.normalize_whitespace:
            self._whitespace.normalize_document_text(soup)

        # 5. Metadata extraction
        if self.config.extract_metadata:
            meta = self._metadata.extract(soup)
            report.metadata = {
                "title": meta.title,
                "description": meta.description,
                "canonical_url": meta.canonical_url,
                "keywords": meta.keywords,
                "language": meta.language,
                "charset": meta.charset,
                "og_title": meta.og_title,
                "og_description": meta.og_description,
            }

        # 6. Final size
        report.cleaned_size = len(str(soup).encode("utf-8"))
        report.processing_time_ms = (time.perf_counter() - start) * 1000

        return soup, report

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def parse(self, html: str) -> BeautifulSoup:
        """Parse HTML string into BeautifulSoup. Handles malformed markup."""
        if not html:
            return BeautifulSoup("", self.config.parser)
        if len(html.encode("utf-8")) > self.config.max_size_bytes:
            raise ParseError(
                f"HTML size {len(html.encode('utf-8'))} exceeds max {self.config.max_size_bytes}"
            )
        try:
            return BeautifulSoup(html, self.config.parser)
        except Exception as e:
            raise ParseError(f"Failed to parse HTML: {e}")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, soup: BeautifulSoup) -> list[str]:
        """Validate parsed HTML structure. Returns list of issues."""
        errors = []

        # Check for html tag
        if not soup.find("html"):
            errors.append("Missing <html> tag — document may be a fragment")

        # Check for head
        if not soup.find("head"):
            errors.append("Missing <head> tag")

        # Check for body
        if not soup.find("body"):
            errors.append("Missing <body> tag")

        # Check for empty document
        text = soup.get_text(strip=True)
        if not text:
            errors.append("Document contains no visible text")

        return errors

    # ------------------------------------------------------------------
    # Quick helpers
    # ------------------------------------------------------------------

    def clean_html(self, html: str) -> str:
        """Quick clean — returns normalized HTML string."""
        soup, _ = self.process(html)
        return str(soup)

    def extract_metadata(self, html: str) -> HTMLMetadata:
        """Extract metadata without full cleaning pipeline."""
        soup = self.parse(html)
        return self._metadata.extract(soup)
