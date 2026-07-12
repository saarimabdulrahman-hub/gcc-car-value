"""Test DOM extraction engine — document, node, query, extractors, validation."""
import pytest
from browser.dom.document import DOMDocument
from browser.dom.node import DOMNode
from browser.dom.engine import DOMEngine
from browser.dom.extractors import Extractor
from browser.dom.validation import ExtractionValidator
from browser.dom.errors import ValidationError
from browser.dom.query import query_text, query_all_text, query_attr, query_exists

# Sample car listing HTML
LISTING_HTML = """
<html>
<head><title>Toyota Land Cruiser 2018 for sale</title></head>
<body>
    <h1 class="title">Toyota Land Cruiser 2018 VXR</h1>
    <div class="price">AED 125,000</div>
    <div class="mileage">120,000 km</div>
    <div class="year">2018</div>
    <span class="spec">GCC Spec</span>
    <div class="location">Dubai, UAE</div>
    <a class="seller" href="/dealer/123">Al-Futtaim Motors</a>
    <ul class="features">
        <li>Leather seats</li>
        <li>Sunroof</li>
        <li>Navigation</li>
    </ul>
    <img src="/images/car123.jpg" alt="Toyota Land Cruiser" class="main-image">
</body>
</html>
"""


@pytest.fixture
def doc():
    return DOMDocument.from_html(LISTING_HTML)


class TestDOMDocument:
    def test_parse_html(self, doc):
        assert doc is not None
        assert doc.title == "Toyota Land Cruiser 2018 for sale"

    def test_select_one(self, doc):
        node = doc.select_one("h1")
        assert node is not None
        assert "Land Cruiser" in node.text_stripped

    def test_select_multiple(self, doc):
        nodes = doc.select("ul.features li")
        assert len(nodes) == 3
        assert "Leather seats" in nodes[0].text_stripped

    def test_select_returns_empty_list(self, doc):
        nodes = doc.select(".nonexistent-class")
        assert len(nodes) == 0

    def test_select_one_returns_none(self, doc):
        assert doc.select_one(".nonexistent") is None

    def test_exists(self, doc):
        assert doc.exists("h1")
        assert not doc.exists(".nonexistent")

    def test_count(self, doc):
        assert doc.count("ul.features li") == 3


class TestDOMNode:
    def test_tag_name(self, doc):
        node = doc.select_one("h1")
        assert node.tag_name == "h1"

    def test_text(self, doc):
        node = doc.select_one("h1")
        assert "Toyota" in node.text

    def test_attr(self, doc):
        node = doc.select_one("img")
        assert "car123" in node.attr("src", "")

    def test_children(self, doc):
        node = doc.select_one("ul.features")
        # children filters to element nodes only (not whitespace text)
        assert len(node.children) > 0
        assert any("Leather" in c.text for c in node.children)

    def test_visibility(self, doc):
        node = doc.select_one("h1")
        assert node.is_visible


class TestExtractor:
    def test_text(self, doc):
        ext = Extractor()
        result = ext.text(doc.select_one("h1"))
        assert result.success
        assert "Land Cruiser" in result.value

    def test_text_on_none(self):
        ext = Extractor()
        result = ext.text(None)
        assert not result.success

    def test_integer(self, doc):
        ext = Extractor()
        result = ext.integer(doc.select_one(".year"))
        assert result.success
        assert result.value == 2018

    def test_currency(self, doc):
        ext = Extractor()
        result = ext.currency(doc.select_one(".price"))
        assert result.success
        assert result.value == 125000.0

    def test_year(self, doc):
        ext = Extractor()
        result = ext.year(doc.select_one(".year"))
        assert result.success
        assert result.value == 2018

    def test_url(self, doc):
        ext = Extractor()
        result = ext.url(doc.select_one("a.seller"))
        assert result.success
        assert "/dealer/123" in result.value

    def test_float(self, doc):
        ext = Extractor()
        result = ext.float_val(doc.select_one(".price"))
        assert result.success


class TestValidator:
    def test_require_node_passes(self, doc):
        node = doc.select_one("h1")
        ExtractionValidator.require_node(node, "title")  # No error

    def test_require_node_raises(self):
        with pytest.raises(ValidationError, match="price"):
            ExtractionValidator.require_node(None, "price")

    def test_require_text(self, doc):
        text = ExtractionValidator.require_text(doc.select_one("h1"), "title")
        assert "Toyota" in text


class TestQueryHelpers:
    def test_query_text(self, doc):
        assert query_text(doc, "h1") == "Toyota Land Cruiser 2018 VXR"
        assert query_text(doc, ".nonexistent", "default") == "default"

    def test_query_all_text(self, doc):
        texts = query_all_text(doc, "ul.features li")
        assert "Leather seats" in texts

    def test_query_attr(self, doc):
        src = query_attr(doc, "img", "src")
        assert "car123" in src

    def test_query_exists(self, doc):
        assert query_exists(doc, "h1")
        assert not query_exists(doc, ".nonexistent")


class TestDOMEngine:
    def test_parse_and_extract(self):
        engine = DOMEngine()
        doc = engine.parse(LISTING_HTML)
        assert doc.title != ""
        extractor = engine.extract(doc)
        result = extractor.text(doc.select_one("h1"))
        assert result.success

    def test_validate_selectors(self):
        engine = DOMEngine()
        doc = engine.parse(LISTING_HTML)
        missing = engine.validate_selectors(doc, {
            "title": "h1",
            "price": ".price",
            "missing_field": ".definitely-not-here",
        })
        assert "missing_field" in missing
        assert "title" not in missing
