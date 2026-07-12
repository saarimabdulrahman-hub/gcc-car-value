# GCC Car Value — Browser Fingerprint Manager

**Date:** 2026-07-12  
**Package:** `browser/fingerprint/`

## Architecture

```
Browser Session
    │
    ▼
FingerprintManager.acquire(country="AE")
    │
    ▼
FingerprintCatalog → BrowserProfile
    │
    ├── User-Agent          (matching OS + browser + version)
    ├── Sec-CH-UA           (Chromium Client Hints)
    ├── Sec-CH-UA-Platform  (OS platform)
    ├── Sec-CH-UA-Mobile    (desktop/mobile)
    ├── Locale              (en-AE, ar-SA, etc.)
    ├── Timezone            (Asia/Dubai, Asia/Riyadh, etc.)
    ├── Screen              (1920x1080, 2560x1440, etc.)
    └── Platform            (Win32, MacIntel, Linux x86_64)
```

## Curated Catalog (10 profiles)

| Country | OS | Browser | Resolution |
|---------|-----|---------|------------|
| 🇦🇪 AE | Windows 10 | Chrome 131 | 1920×1080 |
| 🇦🇪 AE | macOS 14.7 | Chrome 130 | 1680×1050 |
| 🇦🇪 AE | Windows 10 | Chrome 131 | 2560×1440 |
| 🇸🇦 SA | Windows 10 | Chrome 131 | 1920×1080 |
| 🇸🇦 SA | macOS 15.0 | Chrome 131 | 1728×1117 |
| 🇰🇼 KW | Windows 11 | Chrome 131 | 1920×1080 |
| 🇶🇦 QA | Windows 10 | Chrome 131 | 1920×1080 |
| 🇧🇭 BH | Windows 10 | Chrome 131 | 1920×1080 |
| 🇴🇲 OM | Windows 10 | Chrome 131 | 1920×1080 |

## Validation Rules

| Rule | Example Rejection |
|------|------------------|
| OS + browser family must be valid | Windows + Safari ❌ |
| Timezone must match country | AE + Asia/Tokyo ❌ |
| Locale must match country | SA + en-US ❌ |
| Viewport cannot exceed screen | 4000×3000 on 1920×1080 ❌ |
| Mobile must have touch | mobile=true, touch=false ❌ |
| Device memory must be realistic | 128GB ❌ |

## Usage

```python
from browser.fingerprint import FingerprintManager

mgr = FingerprintManager()
profile = mgr.acquire(country="AE")

# Apply to Playwright context
headers = generate_headers(profile)
context = await browser.new_context(
    viewport={"width": profile.viewport_width, "height": profile.viewport_height},
    locale=profile.locale,
    timezone_id=profile.timezone,
    extra_http_headers=headers,
)
```

## Verified

- All 10 catalog profiles pass validation
- Timezone/locale consistency enforced for 6 GCC countries
- User-Agent matches OS + browser + version
- Client Hints consistent with profile
- Session assignment and release

---

*Fingerprint manager documented 2026-07-12.*
