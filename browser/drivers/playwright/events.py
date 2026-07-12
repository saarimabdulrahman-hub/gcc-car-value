"""Playwright-specific event types."""

PLAYWRIGHT_EVENTS = {
    "playwright.chromium.launched":   "Chromium launched via Playwright",
    "playwright.chromium.crashed":    "Chromium crashed or was killed",
    "playwright.chromium.shutdown":   "Chromium shutdown gracefully",
    "playwright.context.created":     "BrowserContext created",
    "playwright.page.navigation":     "Page navigation completed",
}
