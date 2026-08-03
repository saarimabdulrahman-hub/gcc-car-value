"""Playwright E2E tests for the GCC Car Value UI.

Tests the actual HTML pages served by the app.
Run with: pytest tests/e2e/test_ui_playwright.py --headed
"""

import pytest
from pathlib import Path

# playwright may not be importable in CI — skip gracefully
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    sync_playwright = None

UI_DIR = Path(__file__).resolve().parent.parent.parent / "ui"

pytestmark = pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="playwright not installed")


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture
def page(browser):
    p = browser.new_page()
    yield p
    p.close()


class TestIndexPage:
    """The main landing page at ui/index.html."""

    def test_index_page_loads(self, page):
        page.goto(f"file:///{UI_DIR / 'index.html'}")
        assert page.title()
        # Page should have content
        body = page.locator("body")
        assert body.is_visible()

    def test_hero_section_present(self, page):
        page.goto(f"file:///{UI_DIR / 'index.html'}")
        # Index should have a hero or main content area
        hero_candidates = page.locator("[class*='hero'], header, main, .container")
        assert hero_candidates.count() > 0

    def test_no_console_errors_on_load(self, page):
        errors = []
        page.on("pageerror", lambda err: errors.append(err))
        page.goto(f"file:///{UI_DIR / 'index.html'}")
        page.wait_for_load_state("networkidle")
        # Allow cross-origin errors for file:// but fail on real JS errors
        real_errors = [e for e in errors if "cross-origin" not in str(e).lower()
                      and "file://" not in str(e).lower()]
        assert len(real_errors) == 0, f"Console errors: {[str(e) for e in real_errors]}"


class TestBrowsePage:
    """Browse/search page."""

    def test_browse_page_loads(self, page):
        page.goto(f"file:///{UI_DIR / 'browse.html'}")
        assert page.title()
        body = page.locator("body")
        assert body.is_visible()

    def test_search_input_exists(self, page):
        page.goto(f"file:///{UI_DIR / 'browse.html'}")
        # Should have some form of search/filter input
        inputs = page.locator("input, select, [role='search'], [role='combobox']")
        assert inputs.count() > 0


class TestMarketPage:
    def test_market_page_loads(self, page):
        page.goto(f"file:///{UI_DIR / 'market.html'}")
        assert page.title()


class TestSettingsPage:
    def test_settings_page_loads(self, page):
        page.goto(f"file:///{UI_DIR / 'settings.html'}")
        assert page.title()


class TestWatchlistPage:
    def test_watchlist_page_loads(self, page):
        page.goto(f"file:///{UI_DIR / 'watchlist.html'}")
        assert page.title()


class TestPreviewStates:
    @pytest.mark.parametrize("filename", [
        "reports.html",
        "results.html",
        "vehicle.html",
        "comparables.html",
        "report-detail.html",
        "notifications.html",
    ])
    def test_demo_pages_disclose_preview_data(self, page, filename):
        page.goto(f"file:///{UI_DIR / filename}")
        disclosure = page.locator(".preview-state")
        assert disclosure.is_visible()
        assert "Preview data" in disclosure.inner_text()

    def test_auth_page_is_interactive(self, page):
        """Auth page inputs are enabled and the form accepts input."""
        page.goto(f"file:///{UI_DIR / 'auth.html'}")
        # Inputs should be enabled (real auth, not a mockup)
        assert page.locator("#email").is_enabled()
        assert page.locator("#password").is_enabled()
        # Sign In tab should be active by default
        assert page.get_by_text("Sign In").first.is_visible()
        # Register tab should also be present
        assert page.get_by_text("Register").first.is_visible()
