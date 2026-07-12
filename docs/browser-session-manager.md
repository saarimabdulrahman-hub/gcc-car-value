# GCC Car Value — Cookie & Session Manager

**Date:** 2026-07-12  
**Package:** `browser/session/`

## Architecture

```
Scraper → BrowserPool → SessionManager
                            │
                  ┌─────────┼─────────┐
                  ▼         ▼         ▼
            CookieStore  StorageState  SessionPolicies
```

## Usage

```python
from browser.session import SessionManager
from browser.session.models import SessionPolicy

mgr = SessionManager()

# Create (persistent sessions are reused for same marketplace)
session = await mgr.create("dubizzle_uae", policy=SessionPolicy.PERSISTENT)

# Restore cookies into a browser context
await mgr.restore_cookies(session.session_id, context)

# ... scrape ...

# Save cookies from context
cookies = await context.cookies()
await mgr.save_cookies(session.session_id, cookies)

await mgr.release(session.session_id)
```

## Session Policies

| Policy | Reuse? | Use Case |
|--------|--------|----------|
| `EPHEMERAL` | Never | Default, one-off scrapes |
| `PERSISTENT` | Same marketplace | Long-running scrapers |
| `AUTHENTICATED` | Same marketplace | Login-required sites |
| `GUEST` | Never | Browse-only, no forms |
| `READONLY` | Never | No interaction |
| `DISPOSABLE` | Never | Destroy after one use |

## Cookie Store

- Domain-based lookup with subdomain matching
- Playwright-compatible import/export format
- Automatic duplicate replacement (name+domain keyed)
- Session isolation — no cross-session contamination
- Thread-safe — async lock on all mutations

## Storage State

Playwright-compatible `storage_state` dicts for context creation:

```json
{
  "cookies": [...],
  "origins": [{"origin": "https://...", "localStorage": [...]}]
}
```

## Verified

- Cookie CRUD, domain lookup, session isolation
- 100 concurrent cookie operations — no race conditions
- 50 concurrent session creations — no duplicates
- Session reuse for persistent/authenticated policies
- Playwright dict round-trip (export → import → export)

---

*Session manager documented 2026-07-12.*
