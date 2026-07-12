# GCC Car Value — Browser Binary Manager

**Date:** 2026-07-12  
**Package:** `browser/binaries/`

## Architecture

```
DriverManager.launch()
    │
    ▼
BinaryManager.resolve("chromium", version="120.0")
    │
    ├── 1. Check registry for validated binary
    ├── 2. Discover in configured paths, PATH, standard locations
    ├── 3. Validate (exists, platform, arch, version)
    ├── 4. Cache validation result (TTL 300s)
    └── 5. Return BrowserBinary with executable_path
```

## Usage

```python
from browser.binaries import BinaryManager
from browser.binaries.config import BinaryManagerConfig

mgr = BinaryManager(BinaryManagerConfig(
    configured_paths=["/opt/chromium"],
    search_path=True,
))
await mgr.initialize()  # Discover + validate all binaries

binary = await mgr.resolve("chromium", version="120.0")
# binary.executable_path = "/usr/bin/chromium"
# binary.version = "120.0.6099.109"
# binary.status = "valid"
```

## Components

| Component | Purpose |
|-----------|---------|
| `BinaryRegistry` | Register, lookup, enumerate binaries (keyed by type+path) |
| `BinaryDiscovery` | Find binaries in configured paths, PATH, standard OS locations |
| `BinaryValidator` | Check executable exists, platform match, arch match, version parseable |
| `BinaryCache` | TTL-based validation result cache with hit rate tracking |
| `VersionResolver` | Semver parse, compare, meets_minimum |
| `BinaryInstaller` (ABC) | Interface for future Playwright/Selenium installers |

## Verified

- Registry: register, find by type, find by version (prefers highest), duplicate rejection
- Validator: validates real files (Python executable), rejects missing paths
- Cache: hit/miss, TTL expiry, hit rate tracking
- Version: parse, compare, meets_minimum
- Concurrency: 50 simultaneous registrations — no duplicates

---

*Binary manager documented 2026-07-12.*
