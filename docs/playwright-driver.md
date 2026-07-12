# GCC Car Value — Playwright Chromium Driver

**Date:** 2026-07-12  
**Package:** `browser/drivers/playwright/`

## Architecture

```
DriverManager.launch(prefer="playwright-chromium")
    │
    ▼
PlaywrightChromiumDriver.launch()
    │
    ├── BinaryManager.resolve("chromium")   ← locate executable
    ├── async_playwright().start()           ← start Playwright
    ├── pw.chromium.launch(executable_path)  ← launch Chromium
    │
    ▼
PlaywrightBrowser (implements Browser ABC)
    │
    ▼
PlaywrightContext (implements BrowserContext ABC)
    │
    ▼
PlaywrightPage (implements BrowserPage ABC)
```

## Installation

```bash
pip install playwright
playwright install chromium
```

## Registration

```python
from browser.drivers import DriverRegistry
from browser.drivers.playwright import PlaywrightChromiumDriver

registry = DriverRegistry()
await registry.register(PlaywrightChromiumDriver)

# Now DriverManager can use it
mgr = DriverManager(registry)
browser = await mgr.launch(prefer="playwright-chromium")
```

## Error Translation

All Playwright exceptions are caught and translated to platform exceptions:

| Playwright Error | Platform Exception |
|-----------------|-------------------|
| `TimeoutError` | `TimeoutError` |
| `TargetClosedError` | `PageClosedError` |
| Browser crash | `BrowserCrashError` |
| Launch failure | `BrowserLaunchError` |

No raw Playwright exceptions escape outside `browser/drivers/playwright/`.

## Configuration

```python
PlaywrightChromiumConfig(
    headless=True,
    viewport_width=1920, viewport_height=1080,
    locale="en-AE",
    timezone="Asia/Dubai",
    proxy=None,
    args=["--no-sandbox", "--disable-gpu"],
)
```

## Encapsulation

- `PlaywrightBrowser` — wraps `pw.Browser` as `Browser` ABC
- `PlaywrightContext` — wraps `pw.BrowserContext` as `BrowserContext` ABC
- `PlaywrightPage` — wraps `pw.Page` as `BrowserPage` ABC

No Playwright type is exposed outside this package. The rest of the platform sees only the abstract interfaces.

---

*Playwright driver documented 2026-07-12.*
