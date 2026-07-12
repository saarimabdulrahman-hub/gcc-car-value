"""Test selector framework — registry, compiler, fallback, validation, groups, versioning."""
import pytest
from browser.selectors.models import Selector
from browser.selectors.registry import SelectorRegistry
from browser.selectors.compiler import SelectorCompiler
from browser.selectors.validation import SelectorValidator
from browser.selectors.diagnostics import SelectorDiagnosticsEngine
from browser.selectors.versioning import SelectorVersion
from browser.selectors.fallback import build_fallback_chain
from browser.selectors.group import create_selector, GROUPS
from browser.selectors.errors import SelectorNotFoundError, DuplicateSelectorError

from browser.dom.document import DOMDocument


@pytest.fixture
def sample_html():
    return """<html><body>
        <h1 class="title">Toyota Land Cruiser 2018</h1>
        <div class="price">AED 125,000</div>
        <div class="mileage">120,000 km</div>
        <span class="year-label">2018</span>
    </body></html>"""


@pytest.fixture
def doc(sample_html):
    return DOMDocument.from_html(sample_html)


class TestSelectorModel:
    def test_selector_all_selectors_includes_primary_and_fallbacks(self):
        s = Selector(name="test", css=".primary",
                     fallbacks=[".fb1", ".fb2"])
        assert s.all_selectors == [".primary", ".fb1", ".fb2"]

    def test_create_selector_factory(self):
        s = create_selector("test.name", ".test", [".fb1"],
                          marketplace="mp", group="price")
        assert s.name == "test.name"
        assert s.marketplace == "mp"
        assert s.group == "price"


class TestSelectorRegistry:
    @pytest.mark.asyncio
    async def test_register_and_get(self):
        reg = SelectorRegistry()
        s = Selector(name="listing.title", css="h1", marketplace="test", group="title")
        await reg.register(s)
        retrieved = await reg.get("test", "listing.title")
        assert retrieved.css == "h1"

    @pytest.mark.asyncio
    async def test_duplicate_raises(self):
        reg = SelectorRegistry()
        await reg.register(Selector(name="x", css=".a", marketplace="m", group="g"))
        with pytest.raises(DuplicateSelectorError):
            await reg.register(Selector(name="x", css=".b", marketplace="m", group="g"))

    @pytest.mark.asyncio
    async def test_update_increments_version(self):
        reg = SelectorRegistry()
        s = Selector(name="v", css=".a", marketplace="m", group="g")
        await reg.register(s)
        await reg.update(s)
        updated = await reg.get("m", "v")
        assert updated.version == 2

    @pytest.mark.asyncio
    async def test_list_by_marketplace(self):
        reg = SelectorRegistry()
        await reg.register(Selector(name="a", css=".a", marketplace="m1", group="g"))
        await reg.register(Selector(name="b", css=".b", marketplace="m1", group="g"))
        await reg.register(Selector(name="c", css=".c", marketplace="m2", group="g"))
        m1 = await reg.list_by_marketplace("m1")
        assert len(m1) == 2

    @pytest.mark.asyncio
    async def test_list_by_group(self):
        reg = SelectorRegistry()
        await reg.register(Selector(name="a", css=".a", marketplace="m", group="price"))
        await reg.register(Selector(name="b", css=".b", marketplace="m", group="title"))
        price = await reg.list_by_group("m", "price")
        assert len(price) == 1

    @pytest.mark.asyncio
    async def test_get_nonexistent_raises(self):
        reg = SelectorRegistry()
        with pytest.raises(SelectorNotFoundError):
            await reg.get("m", "nope")

    @pytest.mark.asyncio
    async def test_get_marketplaces(self):
        reg = SelectorRegistry()
        await reg.register(Selector(name="a", css=".a", marketplace="dubizzle", group="g"))
        await reg.register(Selector(name="b", css=".b", marketplace="opensooq", group="g"))
        mps = await reg.get_marketplaces()
        assert "dubizzle" in mps
        assert "opensooq" in mps


class TestSelectorCompiler:
    def test_validate_valid_selector(self):
        compiler = SelectorCompiler()
        s = Selector(name="test", css=".valid", marketplace="m", group="g")
        errors = compiler.validate(s)
        assert len(errors) == 0

    def test_validate_missing_name(self):
        compiler = SelectorCompiler()
        s = Selector(css=".x", marketplace="m", group="g")
        errors = compiler.validate(s)
        assert any("name" in e for e in errors)

    def test_validate_mismatched_parens(self):
        compiler = SelectorCompiler()
        s = Selector(name="t", css=":has(a", marketplace="m", group="g")
        errors = compiler.validate(s)
        assert any("parentheses" in e for e in errors)

    def test_execute_primary_selector(self, doc):
        compiler = SelectorCompiler()
        s = Selector(name="title", css="h1", marketplace="test", group="title")
        result = compiler.execute(s, doc)
        assert result.matched
        assert not result.fallback_used
        assert "Toyota" in result.value

    def test_execute_fallback_on_primary_miss(self, doc):
        compiler = SelectorCompiler()
        s = Selector(name="year", css=".nonexistent",
                     fallbacks=[".year-label"],
                     marketplace="test", group="year")
        result = compiler.execute(s, doc)
        assert result.matched
        assert result.fallback_used
        assert result.fallback_index == 1

    def test_execute_no_match(self, doc):
        compiler = SelectorCompiler()
        s = Selector(name="nope", css=".nope", fallbacks=[".also-nope"],
                     marketplace="test", group="g")
        result = compiler.execute(s, doc)
        assert not result.matched
        assert result.error is not None

    def test_execute_with_extractor(self, doc):
        compiler = SelectorCompiler()
        from browser.dom.extractors import Extractor
        extractor = Extractor()
        s = Selector(name="price", css=".price", selector_type="currency",
                     marketplace="test", group="price")
        result = compiler.execute(s, doc, extractor=extractor)
        assert result.matched
        assert "125000" in result.value


class TestValidation:
    def test_self_referential_fallback_rejected(self):
        s = Selector(name="t", css=".x", fallbacks=[".x"], marketplace="m", group="g")
        errors = SelectorValidator.validate(s)
        assert any("fallback" in e.lower() for e in errors)

    def test_duplicate_fallbacks_rejected(self):
        s = Selector(name="t", css=".x", fallbacks=[".a", ".a"], marketplace="m", group="g")
        errors = SelectorValidator.validate(s)
        assert any("duplicate" in e.lower() for e in errors)


class TestDiagnostics:
    def test_summary_for_matched(self):
        engine = SelectorDiagnosticsEngine()
        from browser.selectors.models import SelectorExecutionResult
        s = Selector(name="test", css=".x", marketplace="m", group="g")
        r = SelectorExecutionResult(
            selector_name="test", matched=True,
            matched_selector=".x", value="hello",
        )
        diag = engine.diagnose(s, r)
        summary = engine.summary(diag)
        assert "✓" in summary
        assert "hello" in summary

    def test_summary_for_unmatched(self):
        engine = SelectorDiagnosticsEngine()
        from browser.selectors.models import SelectorExecutionResult
        s = Selector(name="test", css=".x", fallbacks=[".y"],
                     marketplace="m", group="g")
        r = SelectorExecutionResult(selector_name="test", matched=False)
        diag = engine.diagnose(s, r)
        summary = engine.summary(diag)
        assert "✗" in summary


class TestVersioning:
    def test_version_tracking(self):
        ver = SelectorVersion()
        s1 = Selector(name="test", css=".v1", marketplace="m", group="g", version=1)
        s2 = Selector(name="test", css=".v2", marketplace="m", group="g", version=2)
        ver.add_version(s1)
        ver.add_version(s2)
        assert ver.get_latest_version("m", "test") == 2
        assert len(ver.get_history("m", "test")) == 2
