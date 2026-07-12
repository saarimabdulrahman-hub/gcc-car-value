"""Test HTML normalization engine — parse, clean, normalize, metadata, validation."""
import pytest
from markup.engine import HTMLEngine
from markup.config import HTMLConfig
from markup.cleaner import HTMLCleaner
from markup.whitespace import WhitespaceNormalizer
from markup.metadata import MetadataExtractor
from markup.models import CleaningReport, HTMLMetadata

SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Toyota Land Cruiser 2018 for sale - Dubizzle</title>
    <meta name="description" content="Toyota Land Cruiser VXR 2018, GCC spec, 120,000 km">
    <meta charset="UTF-8">
    <meta property="og:title" content="Toyota Land Cruiser 2018">
    <script>console.log('tracking');</script>
    <script>ga('send', 'pageview');</script>
    <style>.ad { display:none; }</style>
</head>
<body>
    <!-- Header comment -->
    <h1>Toyota Land Cruiser 2018</h1>
    <div class="price">AED 125,000</div>
    <div class="mileage">120,000 km</div>
    <div style="display:none" class="ad">Buy now!</div>
    <div class="hidden-banner" hidden>Special offer</div>
    <!-- Footer comment -->
    <script>console.log('footer');</script>
</body>
</html>"""


class TestHTMLEngine:
    def test_process_returns_soup_and_report(self):
        engine = HTMLEngine()
        soup, report = engine.process(SAMPLE_HTML)
        assert soup is not None
        assert isinstance(report, CleaningReport)

    def test_scripts_removed(self):
        engine = HTMLEngine()
        soup, report = engine.process(SAMPLE_HTML)
        assert report.scripts_removed >= 3  # 3 <script> tags

    def test_styles_removed(self):
        engine = HTMLEngine()
        soup, report = engine.process(SAMPLE_HTML)
        assert report.styles_removed >= 1  # <style> tag

    def test_comments_removed(self):
        engine = HTMLEngine()
        soup, report = engine.process(SAMPLE_HTML)
        assert report.comments_removed >= 2  # 2 HTML comments

    def test_hidden_nodes_detected(self):
        engine = HTMLEngine()
        soup, report = engine.process(SAMPLE_HTML)
        assert report.hidden_nodes_found >= 2  # display:none + hidden attr

    def test_metadata_extracted(self):
        engine = HTMLEngine()
        soup, report = engine.process(SAMPLE_HTML)
        assert "Toyota Land Cruiser" in report.metadata["title"]
        assert report.metadata["og_title"] == "Toyota Land Cruiser 2018"

    def test_cleaning_report_has_sizes(self):
        engine = HTMLEngine()
        soup, report = engine.process(SAMPLE_HTML)
        assert report.original_size > 0
        assert report.cleaned_size > 0
        # Scripts + styles + comments removed → typically smaller
        assert (report.scripts_removed + report.styles_removed + report.comments_removed) > 0

    def test_processing_time_measured(self):
        engine = HTMLEngine()
        soup, report = engine.process(SAMPLE_HTML)
        assert report.processing_time_ms > 0

    def test_clean_html_returns_string(self):
        engine = HTMLEngine()
        result = engine.clean_html(SAMPLE_HTML)
        assert isinstance(result, str)
        assert "Toyota" in result
        assert "console.log" not in result  # Scripts removed


class TestCleaner:
    def test_scripts_removed(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<html><body><script>x()</script><p>Hello</p></body></html>", "lxml")
        cleaner = HTMLCleaner()
        counts = cleaner.clean(soup)
        assert counts["scripts_removed"] == 1
        assert soup.find("script") is None
        assert soup.find("p") is not None  # Content preserved

    def test_comments_removed(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<html><!-- comment --><p>Hello</p></html>", "lxml")
        cleaner = HTMLCleaner()
        counts = cleaner.clean(soup)
        assert counts["comments_removed"] == 1

    def test_hidden_marked_not_deleted(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<html><body><div style='display:none'>Hidden</div></body></html>", "lxml")
        cleaner = HTMLCleaner()
        counts = cleaner.clean(soup)
        assert counts["hidden_nodes_found"] == 1
        # Node is still there, just marked
        div = soup.find("div")
        assert div is not None
        assert div.get("data-was-hidden") == "true"


class TestWhitespace:
    def test_collapses_multiple_spaces(self):
        normalizer = WhitespaceNormalizer()
        result = normalizer.normalize("hello    world  \t  test")
        assert result == "hello world test"

    def test_preserves_newlines(self):
        normalizer = WhitespaceNormalizer()
        result = normalizer.normalize("line1\n\n\nline2")
        assert result == "line1\n\nline2"


class TestMetadata:
    def test_title(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup("<html><head><title>Test Page</title></head></html>", "lxml")
        extractor = MetadataExtractor()
        meta = extractor.extract(soup)
        assert meta.title == "Test Page"

    def test_og_tags(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(
            '<html><head><meta property="og:title" content="OG Title"></head></html>',
            "lxml"
        )
        extractor = MetadataExtractor()
        meta = extractor.extract(soup)
        assert meta.og_title == "OG Title"


class TestValidation:
    def test_empty_document_detected(self):
        engine = HTMLEngine()
        _, report = engine.process("")
        assert len(report.validation_errors) > 0  # Empty input triggers validation errors

    def test_complete_document_passes(self):
        engine = HTMLEngine()
        _, report = engine.process(SAMPLE_HTML)
        assert len(report.validation_errors) == 0
