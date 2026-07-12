# GCC Car Value — Challenge Detection & Recovery Framework

**Date:** 2026-07-12  
**Package:** `browser/challenge/`

## Architecture

```
Browser Page Content (HTML, title, URL, HTTP status)
    │
    ▼
ChallengeDetector (4 signal checks)
    │
    ├── HTML patterns   → reCAPTCHA, hCaptcha, Cloudflare, Sucuri, DDoS-Guard
    ├── Page title      → "Access Denied", "Blocked", "CAPTCHA", "Rate Limit"
    ├── URL patterns    → /blocked, /captcha, /challenge, rate-limit
    └── HTTP status     → 429 (rate limit), 403 (denied), 503 (unavailable)
    │
    ▼
ChallengeClassifier → refine type, apply severity
    │
    ▼
PolicyEngine → get_policy(challenge_type, marketplace)
    │
    ▼
RecoveryManager → execute actions in order until success or exhaustion
    │
    └── WAIT → RETRY → REFRESH → RESTART_BROWSER → RESTART_SESSION → ESCALATE → ABORT
```

## Challenge Types

| Type | Detected By | Default Severity |
|------|------------|-----------------|
| `captcha` | reCAPTCHA, hCaptcha, Turnstile patterns in HTML | HIGH |
| `javascript_challenge` | Cloudflare, DDoS-Guard, Sucuri patterns | HIGH |
| `access_denied` | 403 status, "Access Denied" title | MEDIUM |
| `rate_limited` | 429 status, rate-limit URL patterns | MEDIUM |
| `security_interstitial` | "Verify you are human", "Unusual traffic" | MEDIUM |
| `unknown` | 503 status, unrecognized patterns | LOW |

## Recovery Actions

| Action | Effect |
|--------|--------|
| `WAIT` | Sleep for retry_delay (default 5s) |
| `RETRY` | Retry the request (up to max_retries, default 3) |
| `REFRESH` | Refresh the current page |
| `RESTART_BROWSER` | Restart the browser instance |
| `RESTART_SESSION` | Create a fresh browser session |
| `ESCALATE` | Log warning, mark for manual review |
| `ABORT` | Give up — report failure |

## Per-Marketplace Policies

```python
from browser.challenge.policies import PolicyEngine
from browser.challenge.models import ChallengeType, RecoveryAction

engine = PolicyEngine()
engine.set_policy(
    ChallengeType.CAPTCHA,
    [RecoveryAction.ABORT],  # Don't retry CAPTCHAs on Dubizzle
    marketplace="dubizzle",
)
```

## Usage

```python
from browser.challenge import ChallengeManager

mgr = ChallengeManager()

# After page load
challenge = mgr.detect(html=page_html, title=page_title, url=page_url)
if challenge:
    result = await mgr.recover(challenge, session_id="s1")
    if not result.success:
        logger.warning("unrecoverable_challenge", type=challenge.challenge_type)
```

## Verified

- HTML detection: reCAPTCHA, Cloudflare JS, security interstitial
- Title detection: Access Denied, CAPTCHA
- HTTP status: 429 → rate_limited, 403 → access_denied
- Normal pages return None (no false positives on listing pages)
- Policy engine: default + per-marketplace overrides
- Recovery: WAIT, RETRY (with max attempt tracking), ABORT

---

*Challenge framework documented 2026-07-12.*
