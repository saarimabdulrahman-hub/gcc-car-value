# GCC Car Value — Human Behaviour Engine

**Date:** 2026-07-12  
**Package:** `browser/behavior/`

## Architecture

```
Browser Session
    │
    ▼
BehaviourManager.assign(session_id, profile_name="normal")
    │
    ▼
BehaviourProfile (4 curated styles)
    │
    ├── TypingBehaviour     → char_delay(), word_delay(), field_delay()
    ├── ScrollBehaviour     → steps_for_distance(), step_delay()
    ├── MouseBehaviour      → move_delay(), hover_delay(), click_delay()
    ├── NavigationBehaviour → page_settle_delay(), post_click_delay()
    ├── ReadingBehaviour    → estimate_time(scroll_height)
    └── IdleBehaviour       → maybe_brief_idle(), maybe_medium_idle()
```

## Curated Profiles

| Profile | Typing (ms) | Scroll | Reading | Idle | Style |
|---------|------------|--------|---------|------|-------|
| `normal` | 80-200 | 200-800ms pause | 3s/1Kpx | 10%/2% | Balanced |
| `fast` | 40-100 | 100-300ms pause | 1s/1Kpx | 3%/0% | Speed-focused |
| `thorough` | 100-300 | 500-1500ms pause | 5s/1Kpx | 15%/5% | Detail-oriented |
| `relaxed` | 150-400 | 800-2000ms pause | 6s/1Kpx | 20%/8% | Leisurely |

## Usage

```python
from browser.behavior import BehaviourManager

mgr = BehaviourManager()
await mgr.assign("session-1", profile_name="normal")

typing = await mgr.typing("session-1")
delay = typing.char_delay()
# await page.keyboard.type(char, delay=int(delay))

scroll = await mgr.scroll("session-1")
steps = scroll.steps_for_distance(1200)
# for step in steps: await page.evaluate(f"window.scrollBy(0, {step})")
```

## Timing Engine

- `seed=42` → deterministic replay (testing)
- `seed=None` → system randomness (production)
- `jitter(base, pct)` → ±pct% around base value
- `should_trigger(probability)` → probabilistic action gate

## Verified

- All 4 curated profiles pass validation
- Seeded timing is deterministic (same seed = same sequence)
- Typing, scroll, mouse, navigation, reading, idle all produce positive delays
- Scroll steps sum exactly to target distance

---

*Behaviour engine documented 2026-07-12.*
