# GCC Car Value — Enterprise Browser Automation Engine

**Date:** 2026-07-12  
**Package:** `browser/`

---

## 1. Architecture

```
Marketplace Scraper → Browser Interface (ABC)
                         │
                         ├── DummyBrowser      (tests, no real browser)
                         ├── PlaywrightBrowser  (P0025 — future)
                         ├── SeleniumBrowser    (future)
                         └── RemoteBrowser      (future)
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              BrowserContext  BrowserPage  BrowserSession
                    │              │
              NavigationEngine  ScreenshotEngine
              DownloadManager   NetworkManager
```

## 2. Core Interfaces

### Browser
```python
class Browser(ABC):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def new_context(self, config) -> BrowserContext: ...
    async def health(self) -> bool: ...
```

### BrowserContext
```python
class BrowserContext(ABC):
    async def new_page(self) -> BrowserPage: ...
    async def set_cookies(self, cookies) -> None: ...
    async def close(self) -> None: ...
```

### BrowserPage
```python
class BrowserPage(ABC):
    async def goto(self, url, options) -> None: ...
    async def content(self) -> str: ...
    async def wait_for_selector(self, selector, timeout) -> None: ...
    async def click(self, selector) -> None: ...
    async def fill(self, selector, value) -> None: ...
    async def screenshot(self, options) -> bytes: ...
    async def evaluate(self, expression) -> Any: ...
```

## 3. Factory & Registry

```python
from browser.registry import browser_registry
from browser.factory import BrowserFactory

browser_registry.register("playwright", PlaywrightBrowser)

factory = BrowserFactory()
browser = factory.create("playwright", BrowserConfig(headless=True))

async with BrowserSession(browser) as session:
    ctx = await session.new_context()
    page = await ctx.new_page()
    await page.goto("https://example.com")
```

## 4. Building a Driver

Implement the three interfaces:
```python
class PlaywrightBrowser(Browser): ...
class PlaywrightContext(BrowserContext): ...
class PlaywrightPage(BrowserPage): ...
```
Then register: `browser_registry.register("playwright", PlaywrightBrowser)`

No scraper code changes needed. The scraper framework only depends on the `Browser` ABC.

---

*Browser engine documented 2026-07-12.*
