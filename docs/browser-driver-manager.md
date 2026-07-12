# GCC Car Value — Browser Driver Manager

**Date:** 2026-07-12  
**Package:** `browser/drivers/`

## Architecture

```
BrowserPool.acquire()
    │
    ▼
DriverManager.launch(prefer="playwright-chromium")
    │
    ├── 1. Try preferred driver
    ├── 2. Match required capabilities
    ├── 3. Use default registered driver
    └── 4. Fallback driver from config
    │
    ▼
BrowserDriver.launch() → Browser instance
```

## Driver Interface

```python
class BrowserDriver(ABC):
    async def launch(self) -> Browser: ...
    async def shutdown(self) -> None: ...
    async def health(self) -> bool: ...

    @property
    def name(self) -> str: ...          # "playwright-chromium"
    @property
    def version(self) -> str: ...       # "1.48.0"
    @property
    def capabilities(self) -> DriverCapabilities: ...
```

## Registration

```python
from browser.drivers import DriverRegistry

registry = DriverRegistry()
await registry.register(PlaywrightChromiumDriver)
await registry.register(PlaywrightFirefoxDriver)
```

## Selection Flow

```
launch(prefer="playwright-firefox", required_capabilities={"screenshots": True})
    │
    ├── 1. Try "playwright-firefox" → healthy? capabilities match? → USE
    ├── 2. Scan all drivers for screenshots=True → first healthy match → USE
    ├── 3. Fall back to default registered driver
    └── 4. Fall back to config.fallback_driver
```

## Capabilities

```python
DriverCapabilities(
    browser_type="chromium",
    headless=True,
    screenshots=True,
    downloads=True,
    proxy_support=True,
    pdf=False,
    mobile_emulation=False,
)
```

## Verified

- 14 tests: registry CRUD, manager launch/health, capability matching
- 20 concurrent driver registrations — no duplicates, no race conditions
- Selection by name, browser_type, capabilities, default, fallback

---

*Driver manager documented 2026-07-12.*
