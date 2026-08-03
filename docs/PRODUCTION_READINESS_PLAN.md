# Production Readiness Plan — gcc-car-value

## HOW TO USE THIS DOCUMENT (read first)

You are executing a fix list. Follow these rules exactly.

1. Do tasks in order. `P0` before `P1` before `P2` before `P3`. Never skip ahead.
2. One task = one commit. Commit message = the task ID and title, e.g. `P0-2: wire pipeline persistence`.
3. Every task has a **DONE WHEN** block. Run that check. If it fails, fix it before moving on. Do not mark a task done because the code "looks right".
4. Do not refactor anything the task does not name. Do not add abstractions, config options, or extra features. Shortest diff that satisfies DONE WHEN.
5. If a task's file or line does not match what is written here, STOP and report the mismatch instead of guessing.
6. Never run `git commit -a`, `git add .`, or a bare `git commit` in this repo until **P0-0** is complete. 600 changes are already staged (567 deletions + 33 unrelated modifications); any of those commands would commit the whole mixed pile under one message.
7. `python -m pytest -q` must pass at the end of every task. If your change breaks a test, fix it in the same task.

**Verify commands** (from repo root `C:\Users\saari\projects\gcc-car-value`):

```bash
python -m pytest -q                      # all tests
python -m pytest --collect-only -q       # import health
ruff check src/ tests/                   # lint
```

---

## CONTEXT: what is actually broken

The codebase is well structured. Four things make it non-functional in production:

1. **Scraped data is thrown away.** `src/scrapers/base.py` parses a listing into a local variable `parsed`, then never saves it. `validator.py`, `normalizer.py`, `quality.py`, `promoter.py` are all written and correct but **never called by anything**. The database is therefore empty.
2. **Empty database means the API cannot answer.** `POST /v1/valuate` needs 5+ comps from the `listings` table. With none, every request returns HTTP 422.
3. **The deploy target does not exist.** `render.yaml` says `branch: main`. The remote has `master`, `preview`, `feature-url-valuation`. No `main`.
4. **Data-corrupting bugs** in the scrapers would poison valuations the moment data flows (wrong currency, wrong make/model, empty dedup key).

Everything else (auth, observability, backups) is secondary to the above.

---

# PHASE P0 — Stop the bleeding, make the product work

## P0-0: Separate the legacy-layout deletion from unrelated session work

**Why:** 567 files are deleted and staged (`analytics/`, `browser/`, `marketplaces/`, `ml/`, `scrapers/`, `pipeline/`, `schema/`, `normalization/`, `markup/`, `storage/`, plus `.ml_artifacts/` and the retired `deploy-frontend.yml`). These are the OLD pre-`src/` layout — gone from disk, still tracked in git. Removing them is correct. The hazard is that 33 unrelated modifications are staged alongside them, and a `git checkout .` would restore 567 dead files.

**Do this — do not improvise:**

```bash
git rev-parse HEAD                       # write this hash down in the commit body
git checkout -b backup/pre-cleanup-snapshot
git checkout release/prod-hardening      # come back; the branch is just a safety label
```

**Current state — verified, read this before running anything.** `git add -u` has ALREADY been run on this repo. Everything is staged and nothing is committed (HEAD is still `f1bbe54`). Status codes appear in **column 1** (`D `, `M `), not column 2. The index currently holds:

- **567 staged deletions** — the 10 legacy dirs, `.ml_artifacts/`, and the retired `.github/workflows/deploy-frontend.yml`
- **33 staged modifications** — unrelated session work

**Do NOT run `git add -u` or `git commit` as-is.** Committing the index as it stands would sweep `src/config/settings.py` (that is P0-6's job), plus `src/scrapers/base.py`, `src/pipeline/orchestrator.py`, `src/auth/jwt.py` and `src/db/session.py` (P0-2 and P0-3's files) into a commit labelled "legacy layout removal". That destroys the one-task-one-commit audit trail every later task depends on, and makes P0-6 look already-done with no way to verify it.

**Unstage the modifications, keep the deletions, then commit:**

```bash
git restore --staged $(git diff --cached --name-only --diff-filter=M)
git status --porcelain | awk '{print substr($0,1,2)}' | sort | uniq -c
# expect exactly: 567 "D " (staged deletions) and 33 " M" (unstaged modifications)
git commit -m "P0-0: remove pre-src/ legacy layout, .ml_artifacts, retired deploy-frontend workflow (567 files)"
```

`git restore --staged` edits only the index — it never touches the working tree, so all 33 modified files stay exactly as they are on disk, unstaged, waiting for P0-6 and their own commits. Do not use a bare `git reset`: it works but discards the entire index when only 33 paths need unstaging.

**DONE WHEN:** `git diff --cached --name-only | wc -l` prints `0` (index empty after commit), `git diff --name-only --diff-filter=M | wc -l` prints `33` (modifications preserved and still unstaged), `git log --oneline -1` shows your commit, and `python -m pytest -q` passes.

---

## P0-1: Point the deploy at a branch that exists

**File:** `render.yaml` line 7

**Change:** `branch: main` → `branch: master`

Also note the repo has no `main`. If you would rather deploy from `master`, this one-line change is correct and is the lazy fix. Do not create a `main` branch.

**DONE WHEN:** `grep -n "branch:" render.yaml` shows `branch: master`.

---

## P0-2: Wire the pipeline so scraped data is actually saved  ← THE MOST IMPORTANT TASK

**Problem:** `src/scrapers/base.py:69-73` builds `parsed` then drops it.

**The four stages already exist and are already correct. You are only connecting them.** Do not rewrite them.

**Session factory name — confirmed, do not guess.** `src/db/session.py:19` defines `async_session_factory`. Use that exact name in this task and in P0-5. `AsyncSessionLocal` does not exist anywhere in this repo.

The contract, confirmed by reading each file:

| Step | Function | Import from | Takes | Returns |
|---|---|---|---|---|
| 1 | `validate_listing(data)` | `src.pipeline.validator` | dict | `ValidationResult(is_valid, data, errors)` |
| 2 | `normalize_listing(data)` | `src.pipeline.normalizer` | dict | dict (adds `normalized_price_aed`, `original_price`, `exchange_rate`) |
| 3 | `score_quality(data)` | `src.pipeline.quality` | dict | `(score:int, flags:list[str])` |
| 4 | `promote_listing(data, score, flags, session)` | `src.pipeline.promoter` | dict + session | `Listing` or `None` |

`validate_listing` requires these keys present and non-None, or it rejects:
`make`, `model`, `year`, `asking_price`, `city`, `country`, `source`, `external_id`.

### Edit 1 — `src/scrapers/base.py`

`BaseScraper.__init__` currently takes no session. Add an optional one:

```python
    def __init__(self, session_factory=None):
        self.rate_limiter = RateLimiter(settings.scraper_rate_limit_rps)
        self.raw_storage = RawStorage()
        self._session = None
        self._session_factory = session_factory
```

Then replace the body of the inner `try` in `run()` (currently `base.py:65-75`, the block from `await self.rate_limiter.acquire()` through `_consecutive_failures = 0`) with:

```python
                        await self.rate_limiter.acquire()
                        html = await self.fetch_listing(url)
                        s3_key = f"raw/{self.source}/{result.run_id}/{uuid.uuid4()}.html"
                        self.raw_storage.upload_text(s3_key, html)
                        parsed = self.parse(html, url)
                        parsed["raw_data_s3_key"] = s3_key
                        parsed["source"] = self.source
                        parsed["pipeline_run_id"] = result.run_id

                        saved = await self._persist(parsed)
                        if saved == "new":
                            result.records_new += 1
                            result.records_ingested += 1
                        elif saved == "updated":
                            result.records_updated += 1
                            result.records_ingested += 1
                        else:
                            result.records_rejected += 1

                        result.pages_crawled += 1
                        _consecutive_failures = 0
```

Add the `_persist` method to `BaseScraper`:

```python
    async def _persist(self, parsed: dict) -> str:
        """Run parsed data through validate -> normalize -> score -> promote.

        Returns "new", "updated", or "rejected".
        """
        if self._session_factory is None:
            return "rejected"

        from src.pipeline.validator import validate_listing
        from src.pipeline.normalizer import normalize_listing
        from src.pipeline.quality import score_quality
        from src.pipeline.promoter import promote_listing
        # Session factory is injected by the orchestrator (see Edit 2).
        # The concrete object is src.db.session.async_session_factory.

        validation = validate_listing(parsed)
        if not validation.is_valid:
            structlog.get_logger().info(
                "listing_rejected_validation", source=self.source,
                errors=validation.errors[:3])
            return "rejected"

        data = normalize_listing(validation.data)
        score, flags = score_quality(data)

        async with self._session_factory() as session:
            listing = await promote_listing(data, score, flags, session)
            is_new = listing is not None and listing.first_seen_at == listing.last_seen_at
            await session.commit()

        if listing is None:
            return "rejected"
        return "new" if is_new else "updated"
```

Add `import structlog` at the top of `base.py` and delete the two inline `import structlog` statements inside `run()` (currently at `base.py:78` and `base.py:85`).

Add the two missing counters to `ScraperResult` (it already has `records_new` and `records_updated`; add the third):

```python
    records_rejected: int = 0
```

### Edit 2 — `src/pipeline/orchestrator.py`

`PipelineOrchestrator` already receives `session_factory`. Pass it to each scraper before running. In `run_pipeline`, immediately after `logger.info("scraper_starting", ...)`:

```python
            if getattr(scraper, "_session_factory", None) is None:
                scraper._session_factory = self.session_factory
```

Also record the new counters. In `_record_run`, add to the `PipelineRun(...)` constructor:

```python
                records_new=result.records_new,
                records_updated=result.records_updated,
```

Only add these if `src/models/pipeline_run.py` already defines those columns. **Check first** with `grep -n "records_" src/models/pipeline_run.py`. If the columns do not exist, skip this sub-step — do not write a migration for it.

**DONE WHEN:** all of these pass:

```bash
python -m pytest -q
grep -n "_persist" src/scrapers/base.py          # method exists and is called
grep -c "import structlog" src/scrapers/base.py  # prints 1, not 3
```

---

## P0-3: Fail loudly when a scraper yields nothing

**Problem:** `orchestrator.py:43` sets `success=len(result.errors) == 0`. A scraper that is blocked, or whose selectors broke, returns `[]` from `fetch_index`, hits the clean `break` at `base.py:61`, logs zero errors, and records **`success=True, records_ingested=0`**. Your pipeline reports green while doing nothing. This is how the current state went unnoticed.

**File:** `src/pipeline/orchestrator.py`, in `_record_run`, replace the `success=` line:

```python
                success=len(result.errors) == 0 and result.records_ingested > 0,
```

And after `scraper_result = await scraper.run()` in `run_pipeline`, add:

```python
                if scraper_result.records_ingested == 0:
                    logger.critical(
                        "scraper_zero_yield", source=scraper.source,
                        pages_crawled=scraper_result.pages_crawled,
                        errors=len(scraper_result.errors),
                        hint="selectors broken, blocked, or JS-rendered page")
```

**DONE WHEN:** `grep -n "zero_yield" src/pipeline/orchestrator.py` matches, and `python -m pytest -q` passes.

---

## P0-4: Fix the quality gate so real listings survive

**Problem — verify this yourself before changing anything.** `src/pipeline/quality.py` starts at 100 and subtracts 5 for each of 8 missing optional fields (`mileage_km`, `spec`, `trim`, `body_type`, `transmission`, `fuel_type`, `color`, `seller_type`), then another 5 for `sparse_listing`. The scrapers reliably extract only make/model/year/price/city/country. So a typical real listing scores **100 − 35 − 5 = 60 or below**. Both `promote_listing` (`promoter.py:17`) and `find_comps` (`comp_finder.py:86`) gate at **>= 60**. Result: most real listings get dead-lettered, and those that squeak through are excluded from comps anyway.

**Fix:** lower the promotion threshold in `.env` / settings rather than editing the scoring maths.

**File:** `src/config/settings.py` line 31

```python
    quality_promotion_threshold: int = 45
```

**File:** `src/engine/comp_finder.py` line 86 — change the comp filter to match:

```python
            Listing.quality_score >= 45,
```

Add a `# ponytail:` comment on the comp_finder line: `# ponytail: 45 matches quality_promotion_threshold; raise both once scrapers extract optional fields`.

**DONE WHEN:** `grep -n "45" src/config/settings.py src/engine/comp_finder.py` shows both, and `python -m pytest -q` passes.

---

## P0-5: Seed the database so the API can answer today

**Why:** P0-2 makes ingestion work, but the scrapers may still yield nothing until P1 (JS rendering / selector fixes). The API must be demonstrably working before that. Seed realistic comps.

`find_comps` needs, per query: >= 5 rows (for any answer), >= 10 (for `medium` confidence), >= 30 (for `high`). Matching on `make`, `model`, `year ± 2`, `status in (active, probably_sold, sold_confirmed)`, `quality_score >= 45`.

**Create:** `scripts/seed_demo_listings.py`

```python
"""Seed realistic demo listings so /v1/valuate returns real answers.

Usage:
    python scripts/seed_demo_listings.py            # seed
    python scripts/seed_demo_listings.py --clear    # remove seeded rows only

Seeded rows are marked source='seed_demo' so they can be removed cleanly.
"""
import asyncio
import random
import sys
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from src.db.session import async_session_factory
from src.models.listing import Listing

SOURCE = "seed_demo"

# (make, model, base_price_aed, price_per_year_older)
MODELS = [
    ("Toyota", "Land Cruiser", 280000, 22000),
    ("Toyota", "Camry", 95000, 8000),
    ("Nissan", "Patrol", 250000, 20000),
    ("Nissan", "Altima", 78000, 7000),
    ("Mitsubishi", "Pajero", 110000, 9000),
    ("Lexus", "LX 570", 400000, 30000),
    ("Honda", "Accord", 88000, 7500),
    ("Hyundai", "Sonata", 72000, 6500),
]
CITIES = [("Dubai", "AE"), ("Abu Dhabi", "AE"), ("Sharjah", "AE"), ("Riyadh", "SA")]
SPECS = ["GCC", "GCC", "GCC", "US", "Japan"]  # GCC weighted, matches real market


def build_rows() -> list[Listing]:
    rng = random.Random(42)  # deterministic
    now = datetime.now(timezone.utc)
    rows = []
    for make, model, base, per_year in MODELS:
        for year in range(2016, 2024):
            age = 2024 - year
            for _ in range(6):  # 6 per (model, year) -> ~48 per model
                city, country = rng.choice(CITIES)
                spec = rng.choice(SPECS)
                price = base - (per_year * age)
                price *= rng.uniform(0.90, 1.10)          # market spread
                price *= 1.0 if spec == "GCC" else 0.90   # non-GCC discount
                mileage = int(age * rng.uniform(12000, 22000)) or 5000
                first_seen = now - timedelta(days=rng.randint(1, 45))
                rows.append(Listing(
                    id=uuid.uuid4(),
                    source=SOURCE,
                    external_id=f"{make}-{model}-{year}-{uuid.uuid4().hex[:8]}",
                    url=None,
                    first_seen_at=first_seen,
                    last_seen_at=now,
                    status="active",
                    make=make, model=model, year=year,
                    spec=spec, city=city, country=country,
                    mileage_km=mileage,
                    body_type="SUV" if per_year > 15000 else "sedan",
                    transmission="automatic",
                    fuel_type="petrol",
                    seller_type=rng.choice(["dealer", "private"]),
                    original_price=round(price, 2),
                    original_currency="AED",
                    exchange_rate=1.0,
                    exchange_timestamp=now,
                    normalized_price_aed=round(price, 2),
                    quality_score=85,
                    quality_flags=[],
                    schema_version=1,
                    parser_version="seed_v1",
                    normalizer_version="seed_v1",
                    pipeline_run_id=str(uuid.uuid4()),
                ))
    return rows


async def main() -> None:
    clear = "--clear" in sys.argv
    async with async_session_factory() as session:
        deleted = await session.execute(delete(Listing).where(Listing.source == SOURCE))
        if clear:
            await session.commit()
            print(f"cleared {deleted.rowcount} seeded rows")
            return
        rows = build_rows()
        session.add_all(rows)
        await session.commit()
        print(f"seeded {len(rows)} listings across {len(MODELS)} models")


if __name__ == "__main__":
    asyncio.run(main())
```

**Session factory name — already confirmed.** `src/db/session.py:19` defines `async_session_factory`. The script above uses it. Sanity-check with `grep -n "async_session_factory" src/db/session.py` — expect one hit. If it is missing, STOP and report; do not substitute another name.

**DONE WHEN:**

```bash
python scripts/seed_demo_listings.py     # prints "seeded 384 listings..."
```

then start the API and confirm a real answer, not a 422:

```bash
uvicorn src.api.main:app --port 8000
# in another shell:
curl -s -X POST http://localhost:8000/v1/valuate \
  -H "Content-Type: application/json" \
  -d '{"make":"Toyota","model":"Land Cruiser","year":2019,"mileage_km":90000,"spec":"GCC","country":"AE"}'
```

Response must contain a non-zero `estimate`, `comp_count >= 10`, and `confidence` of `medium` or `high`. If you get HTTP 422, the seed did not land or the quality gate from P0-4 was not applied — fix that, do not proceed.

---

## P0-6: Lock CORS to the real origin

**Problem:** deployed `HEAD` has `api_cors_origins = ["*"]` from commit `f1bbe54` ("allow all CORS origins for preview deployments"). The working tree already contains the corrected allowlist version with a wildcard guard — it is **uncommitted**. So the fix exists locally but production still runs `["*"]`.

**Action:** commit the existing working-tree `src/config/settings.py` **by itself**. Do not rewrite the file — it is already correct (explicit allowlist, comma/JSON parsing, `no_wildcard_with_credentials` validator).

P0-0 deliberately unstaged this file, so you must stage it explicitly here. Never `git add -u` — that would sweep in the other 32 modifications:

```bash
git diff HEAD -- src/config/settings.py | grep -n "cors"   # review the change first
grep -n "api_cors_origins" src/config/settings.py
git add src/config/settings.py                             # this file ONLY
git commit -m "P0-6: lock CORS to explicit allowlist"
```

`render.yaml` already sets `API_CORS_ORIGINS=https://gcc-car-value.vercel.app`, so production picks up the right origin once this ships.

**DONE WHEN:** the default assignment is an explicit allowlist, not a bare wildcard:

```bash
grep -n "api_cors_origins" -A4 src/config/settings.py   # default = localhost list
python -m pytest -q
```

**Do NOT check this with `grep '"*"'`.** The string `"*"` legitimately appears at `settings.py:126` inside the `no_wildcard_with_credentials` validator — that code *rejects* wildcards, it does not set one. A bare `grep` false-flags it and the task can never pass. Read the `api_cors_origins` default assignment itself.

---

# PHASE P1 — Fix the data-corrupting scraper bugs

These bugs are harmless today (no data flows) and catastrophic the moment P0-2 works. Do them before you turn scrapers on.

## P1-1: YallaMotor tags every country's price as AED

**File:** `src/scrapers/yallamotor/scraper.py` line 49

One scraper serves 6 countries but hardcodes `"original_currency": "AED"`. A Kuwait listing at 5,000 KWD becomes 5,000 AED — off by ~12x (`normalizer.py` has `KWD: 11.94`). This corrupts every valuation in the segment.

**Fix:** extend the `COUNTRIES` map at line 7 to carry currency, then use it.

```python
# Country config: url key -> (country code, default city, currency)
COUNTRIES = {
    "uae":     ("AE", "Dubai",        "AED"),
    "ksa":     ("SA", "Riyadh",       "SAR"),
    "qatar":   ("QA", "Doha",         "QAR"),
    "kuwait":  ("KW", "Kuwait City",  "KWD"),
    "bahrain": ("BH", "Manama",       "BHD"),
    "oman":    ("OM", "Muscat",       "OMR"),
}
```

In `__init__`:

```python
        self.country_code, self.default_city, self.currency = COUNTRIES[country_key]
```

In `parse`, line 49: `"original_currency": self.currency`.

**DONE WHEN:** `grep -n "self.currency" src/scrapers/yallamotor/scraper.py` shows both the assignment and the use; no `"AED"` literal remains in that file.

---

## P1-2: Make/model extraction is wrong in all three scrapers

Three different broken implementations:

- `yallamotor/scraper.py:94` — `tokens[1]` → "Land Rover Range Rover" becomes make=`Land`, model=`Rover`
- `haraj_ksa/scraper.py:89` — same bug
- `dubizzle_uae/parser.py:55` — `tokens[1:3]` → "Toyota Camry 2020" becomes model=`Camry 2020` (year glued in)

Wrong make/model means `find_comps` (which matches on exact `make` AND `model`) never finds comps. **This is a root-cause fix: one shared helper, three call sites.** Do not fix them individually.

**Create:** `src/scrapers/title_parser.py`

```python
"""Shared make/model extraction from listing titles.

All scrapers use this. Multi-word makes must be matched longest-first,
otherwise "Land Rover Range Rover" yields make="Land".
"""
import re

# Longest-first so "Land Rover" wins over "Land". Lowercase keys.
MULTI_WORD_MAKES = [
    "mercedes benz", "mercedes-benz", "land rover", "range rover",
    "alfa romeo", "aston martin", "rolls royce", "rolls-royce",
    "great wall",
]

SINGLE_WORD_MAKES = [
    "toyota", "nissan", "honda", "hyundai", "kia", "ford", "chevrolet",
    "bmw", "mercedes", "audi", "lexus", "mazda", "mitsubishi", "porsche",
    "volkswagen", "vw", "gmc", "cadillac", "jeep", "dodge", "chrysler",
    "infiniti", "jaguar", "volvo", "subaru", "suzuki", "renault",
    "peugeot", "bentley", "ferrari", "lamborghini", "maserati", "mini",
    "tesla", "genesis", "changan", "chery", "haval", "mg", "byd",
]

_NOISE = re.compile(
    r'\b(19\d{2}|20[0-3]\d)\b'                 # years
    r'|\b\d[\d,]*\s*km\b'                       # mileage
    r'|\bgcc\b|\bus\s*spec\b|\bjapan(ese)?\b|\beuro(pean)?\b|\bamerican\b'
    r'|\bfor sale\b|\bused\b|\bnew\b|\baed\b|\bsar\b',
    re.IGNORECASE,
)


def extract_make_model(title: str) -> tuple[str, str]:
    """Return (make, model). Either may be "" if not confidently found.

    Strips years, mileage, spec words, and filler before taking the model,
    so "Toyota Camry 2020 GCC 50,000 km" -> ("Toyota", "Camry").
    """
    if not title:
        return "", ""

    cleaned = _NOISE.sub(" ", title)
    cleaned = re.sub(r'[|/,\-–—]+', " ", cleaned)
    cleaned = re.sub(r'\s+', " ", cleaned).strip()
    low = cleaned.lower()

    for make in MULTI_WORD_MAKES:
        if low.startswith(make) or f" {make}" in low:
            idx = low.find(make)
            rest = cleaned[idx + len(make):].strip()
            return _title(make), _first_words(rest, 2)

    for make in SINGLE_WORD_MAKES:
        if re.search(rf'\b{re.escape(make)}\b', low):
            idx = low.find(make)
            rest = cleaned[idx + len(make):].strip()
            return _title(make), _first_words(rest, 2)

    tokens = cleaned.split()
    if len(tokens) >= 2:
        return tokens[0], tokens[1]
    return "", ""


def _first_words(text: str, n: int) -> str:
    return " ".join(text.split()[:n]).strip()


def _title(make: str) -> str:
    return " ".join(w.capitalize() for w in make.split())


def demo() -> None:
    """Self-check. Run: python -m src.scrapers.title_parser"""
    cases = [
        ("Toyota Camry 2020 GCC 50,000 km", ("Toyota", "Camry")),
        ("Land Rover Range Rover Vogue 2019", ("Land Rover", "Range Rover")),
        ("2018 Nissan Patrol Platinum GCC", ("Nissan", "Patrol")),
        ("Mercedes Benz C200 2021", ("Mercedes Benz", "C200")),
        ("BMW 320i 2017 | 80,000 km", ("BMW", "320i")),
        ("Lexus LX 570 2020 GCC Spec", ("Lexus", "LX 570")),
    ]
    for title, expected in cases:
        got = extract_make_model(title)
        assert got == expected, f"{title!r}: expected {expected}, got {got}"
    assert extract_make_model("") == ("", "")
    print(f"title_parser: {len(cases)} cases passed")


if __name__ == "__main__":
    demo()
```

Then replace all three call sites to use it:

- `dubizzle_uae/parser.py`: delete `_extract_make_model` (lines 52-56), import the shared one, call `extract_make_model(title)` at line 13.
- `yallamotor/scraper.py`: delete `_extract_make_model` (lines 92-94), call the shared one at line 55.
- `haraj_ksa/scraper.py`: delete `_extract_make_model` (lines 86-89), call the shared one at line 42.

**DONE WHEN:**

```bash
python -m src.scrapers.title_parser      # prints "title_parser: 6 cases passed"
grep -rn "_extract_make_model" src/      # returns nothing
python -m pytest -q
```

---

## P1-3: Dubizzle's dedup key is always empty

**File:** `src/scrapers/dubizzle_uae/parser.py` line 25

```python
match = re.search(r'/cars/(\d+)|id[-_](\d+)', url)
```

The index collects `/motors/used-cars/...` URLs. Those contain `-cars/`, never `/cars/`. So `external_id` is `""` for every listing. `validate_listing` accepts `""` (it is non-None), and `listings` has `UniqueConstraint(source, external_id)` — so **all Dubizzle listings collide on `("dubizzle_uae", "")` and only one row ever exists.**

**Fix — two parts.**

Part 1, `parser.py` line 25-26, widen the pattern and fall back to a URL hash:

```python
    import hashlib
    match = re.search(r'/(\d{6,})(?:/|$|\?)|id[-_](\d+)', url)
    if match:
        result["external_id"] = match.group(1) or match.group(2)
    else:
        # Fall back to a stable hash of the URL path so dedup still works.
        result["external_id"] = "url_" + hashlib.sha256(
            url.split("?")[0].encode()).hexdigest()[:16]
```

Part 2, `src/pipeline/validator.py` — reject empty strings, not just None. At line 49-51, change the required-field loop:

```python
    for field in required:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"missing_required_field: {field}")
```

Part 2 is the root-cause guard — it protects all three scrapers, not just Dubizzle.

**DONE WHEN:** `python -m pytest -q` passes and this returns True:

```bash
python -c "from src.pipeline.validator import validate_listing; print(validate_listing({'make':'Toyota','model':'Camry','year':2020,'asking_price':90000.0,'city':'Dubai','country':'AE','source':'x','external_id':'  '}).is_valid == False)"
```

---

## P1-4: Haraj reads the whole page instead of the listing

**File:** `src/scrapers/haraj_ksa/scraper.py` lines 44-45, 60-67

```python
result["spec"] = self._extract_spec(title_text + " " + html)
result["mileage_km"] = self._extract_mileage(title_text + " " + html)
```

Passing the entire raw HTML means any footer link saying "GCC", or a filter reading "within 50 km", sets that value on the listing. Same for `body_type`/`transmission` at lines 60-67, which substring-search the whole lowercased page — one stray "sedan" anywhere marks the car a sedan.

**Fix:** scope extraction to the listing container. Replace lines 44-45:

```python
        # Scope to the listing body; fall back to the title only, never whole HTML.
        body = soup.select_one("[class*='postBody'], [class*='post-body'], article, main")
        scope_text = body.get_text(" ", strip=True) if body else title_text

        result["spec"] = self._extract_spec(scope_text)
        result["mileage_km"] = self._extract_mileage(scope_text)
```

Replace lines 60-67 to use `scope_text.lower()` instead of `html.lower()`, and `in scope_text` instead of `in html`. Same for the city regex at line 72 — search `scope_text`, not `html`.

Also delete the invalid selector at line 48: `td:contains('السعر') + td` is jQuery syntax, not CSS. BeautifulSoup with lxml raises or silently fails on it. Reduce to:

```python
        price_elem = soup.select_one("[class*='price'], .price-value")
```

**DONE WHEN:** `grep -n "html.lower()\|+ html\|:contains" src/scrapers/haraj_ksa/scraper.py` returns nothing, and `python -m pytest -q` passes.

---

## P1-5: Cap pagination and dedup across pages

**File:** `src/scrapers/base.py`, `run()`

`while True` with no page cap. Sites that clamp `?page=99999` back to page 1 make this loop forever, re-fetching the same listings and hammering the target.

**Fix:** add a page cap and a seen-set. At the top of `run()`:

```python
        _MAX_PAGES = 50
        _seen_urls: set[str] = set()
```

Change `while True:` to `while page <= _MAX_PAGES:` and, right after `urls = await self.fetch_index(page)`:

```python
                fresh = [u for u in urls if u not in _seen_urls]
                if not fresh:
                    structlog.get_logger().info(
                        "pagination_exhausted", source=self.source, page=page)
                    break
                _seen_urls.update(fresh)
```

Then iterate `for url in fresh:` instead of `for url in urls:`.

**DONE WHEN:** `grep -n "_MAX_PAGES\|_seen_urls" src/scrapers/base.py` shows all uses, and `python -m pytest -q` passes.

---

## P1-6: Rate limiter is per-scraper, not per-host

**File:** `src/scrapers/base.py:31`

Each scraper instance builds its own `RateLimiter`. Six YallaMotor country scrapers = 6× the configured rate against `yallamotor.com` the moment you run them concurrently.

**Fix — lazy version:** share one limiter per host via a module-level dict in `rate_limiter.py`:

```python
_HOST_LIMITERS: dict[str, "RateLimiter"] = {}


def get_limiter(host: str, rps: float) -> "RateLimiter":
    """One shared limiter per hostname, so concurrent scrapers of the same
    site do not multiply the request rate."""
    if host not in _HOST_LIMITERS:
        _HOST_LIMITERS[host] = RateLimiter(rps)
    return _HOST_LIMITERS[host]
```

In `base.py.__init__`:

```python
        from urllib.parse import urlparse
        from src.scrapers.rate_limiter import get_limiter
        host = urlparse(self.base_url).hostname or self.source
        self.rate_limiter = get_limiter(host, settings.scraper_rate_limit_rps)
```

Note `base_url` is set as a class attribute on subclasses, and YallaMotor sets it in `__init__` **before** calling `super().__init__()` — so this works. Verify that ordering is still true before you rely on it.

**DONE WHEN:** `python -m pytest -q` passes and `grep -n "get_limiter" src/scrapers/base.py src/scrapers/rate_limiter.py` shows both sides.

---

## P1-7: Decide on JS rendering — measure first, do not guess

**Do not install anything until this check is done.**

Dubizzle UAE is a Next.js app. If listings are client-rendered, `httpx` gets an empty shell and every selector fails — which would make P0-2's work look broken when it is not.

```bash
curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  "https://uae.dubizzle.com/motors/used-cars/" -o /tmp/dz.html
wc -c /tmp/dz.html
grep -c "__NEXT_DATA__" /tmp/dz.html
grep -o "AED" /tmp/dz.html | head -3
grep -c "motors/used-cars/" /tmp/dz.html
```

**Branch on the result:**

- **`__NEXT_DATA__` found** → best case. Parse that JSON directly instead of CSS selectors. It is structured, stable, and needs no new dependency. Write the parser against the JSON; skip crawl4ai entirely for this source.
- **No `__NEXT_DATA__`, no prices, few links** → the page is client-rendered. Add `crawl4ai` (Python, free, self-hosted, Playwright-backed) as the fetch layer for this source only. Keep `httpx` for sources that work without JS.
- **Prices and links present in raw HTML** → no JS needed. The selectors are just wrong; fix them against the real markup.

Repeat for `yallamotor.com` and `haraj.com.sa`.

**DONE WHEN:** you have written the outcome for all three sources into `docs/scraper-status.md` — one line each: source, needs-JS yes/no, evidence. Do not add a dependency without that line.

---

## P1-8: Add robots.txt awareness

There is no `robots.txt` check anywhere in `src/` (verified: `grep -rn "robots" src/` returns nothing). You are scraping 9 commercial marketplaces for a commercial product. This is a business risk, not just a technical one.

**Lazy fix** — stdlib, no dependency. In `src/scrapers/base.py`:

```python
    async def _robots_allows(self, url: str) -> bool:
        """Check robots.txt once per host. Fails open on fetch error."""
        from urllib.robotparser import RobotFileParser
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = f"{parsed.scheme}://{parsed.netloc}"
        if not hasattr(self, "_robots_cache"):
            self._robots_cache = {}
        if host not in self._robots_cache:
            rp = RobotFileParser()
            rp.set_url(f"{host}/robots.txt")
            try:
                await asyncio.to_thread(rp.read)
                self._robots_cache[host] = rp
            except Exception:
                self._robots_cache[host] = None   # fail open, log once
                structlog.get_logger().warning("robots_fetch_failed", host=host)
        rp = self._robots_cache[host]
        if rp is None:
            return True
        return rp.can_fetch(settings.scraper_user_agent, url)
```

Call it in `run()` before `fetch_listing`, and skip disallowed URLs with a counter. Add `import asyncio` at the top.

**This is a decision, not just code:** if `robots.txt` disallows the listing paths, escalating to fingerprint spoofing (Crawlee) is a deliberate ToS choice. Surface that to the project owner rather than defaulting to evasion.

**DONE WHEN:** `grep -n "_robots_allows" src/scrapers/base.py` shows definition and call site; `python -m pytest -q` passes.

---

# PHASE P2 — Database safety nets

The database is the product. These are the two smallest changes that keep it alive.

## P2-1: Real database backups

**File:** `.github/workflows/backup.yml`

It exists but **nothing schedules it** — it is a workflow, not a cron. A workflow only runs when something triggers it.

**Lazy fix — one line.** Add a schedule trigger at the top of the file:

```yaml
on:
  schedule:
    - cron: "17 3 * * *"   # 03:17 UTC daily; off the :00/:30 marks to avoid load spikes
  workflow_dispatch:
```

Keep the rest of the file exactly as it is — do not rewrite it.

**DONE WHEN:** `grep -n "schedule\|cron" .github/workflows/backup.yml` shows the block.

## P2-2: Protect the DB from bad rows at the schema level

Two safety-net constraints that belong in the database, not in application code:

- **Duplicate-email registrations race.** `auth.py:65-74` checks existence, then inserts. Two concurrent requests for the same new email both pass the check; one INSERT wins, the other gets a 500 and a partial state. A unique constraint makes the loser fail cleanly instead of corrupting.
- **Empty password hash.** `user_account.py` has no `CHECK` — a bug could write a blank `password_hash`. A `CHECK` makes that impossible.

**Create:** `src/db/migrations/versions/xxxx_add_user_account_constraints.py`

Match the existing migration style in `src/db/migrations/versions/` — copy the header, `revision`/`down_revision` chain (get `down_revision` from the latest existing file), and the `upgrade`/`downgrade` functions from an existing migration.

```python
"""Add unique email + non-empty password hash to user_accounts."""
from alembic import op


def upgrade() -> None:
    # Existing duplicates must be purged before the constraint can apply.
    op.execute(
        "DELETE FROM user_accounts a USING user_accounts b "
        "WHERE a.id > b.id AND a.email = b.email"
    )
    op.create_unique_constraint("uq_user_accounts_email", "user_accounts", ["email"])
    op.create_check_constraint(
        "ck_user_accounts_password_hash_not_empty",
        "user_accounts",
        "password_hash IS NOT NULL AND length(password_hash) > 0",
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_accounts_email", "user_accounts", type_="unique")
    op.drop_constraint(
        "ck_user_accounts_password_hash_not_empty", "user_accounts", type_="check"
    )
```

Verify against the actual schema first — `grep -n "user_accounts" src/db/migrations/versions/*.py` — the email column is `email Text` in `user_account.py:11`, so `UNIQUE` is valid.

Then apply:

```bash
alembic -c src/db/migrations/alembic.ini upgrade head
```

**DONE WHEN:** the migration applies cleanly (no output is success), and `python -m pytest -q` still passes.

---

# PHASE P3 — The optional-but-valuable fixes

Do these only after P0–P2. Each is independent; you may skip any or all of them.

## P3-1: Make /metrics private

**File:** `src/api/routes/metrics.py` line 18-19

`/metrics` is currently unauthenticated and publicly reachable (verified live: HTTP 200, no auth). It leaks app version, environment, uptime — small, but free.

**Lazy fix:** require a token. In `src/api/dependencies.py`, find the existing API-key auth (grep for `api_key` / `X-API-Key`). It exists for the models routes. Reuse the same dependency:

```python
from src.api.dependencies import require_api_key

@router.get("/metrics")
async def metrics(_: None = Depends(require_api_key)):
```

Use the exact function name that exists in `dependencies.py`. Do not invent one.

**DONE WHEN:** `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/metrics` returns `403` or `401` without a key, and `200` with one.

## P3-2: Authenticate the url_valuate route

**File:** `src/api/routes/url_valuate.py`

The route fetches arbitrary user-supplied URLs. It currently has **no auth and no rate limit** beyond the global anonymous limit, and `validate_public_url` has `allow_all_domains=True` by default — meaning the allowlist is off unless explicitly enabled.

**Lazy fix:** require a token on the route (same `require_api_key` dependency as P3-1), and flip the domain check to default-on:

In `url_valuate.py`, wherever `validate_public_url` is called, pass `allow_all_domains=False`. If a legitimate need for arbitrary domains exists, gate it behind an explicit env flag — do not default to open.

**DONE WHEN:** calling the route without a token returns `401`/`403`; calling with a token and a non-allowlisted domain returns a 4xx with the allowlist error message.

## P3-3: Refresh token actually re-issues an elevated role

**File:** `src/api/routes/auth.py` line 127

`/auth/refresh` hardcodes `role="consumer"` and never looks up the current role, despite the code comment claiming it does. Combined with a no-op JTI revocation, a user whose role was upgraded to `admin` keeps `consumer` privileges (fail-closed — safe), and a **downgraded** user keeps `admin` until the 15-min access token expires (fail-open — unsafe). The refresh endpoint is where the role should be re-read from the DB.

**Lazy fix:** in the `refresh` handler, replace the hardcoded role with a DB lookup using the session it already opens. The function already imports `get_db` and opens a session. Add:

```python
    from src.auth.rbac import get_user_role
    from src.api.dependencies import get_db as _get_db
    # get_user_role returns Role.CONSUMER for unknown users (safe default)
```

**DONE WHEN:** `grep -n 'role="consumer"' src/api/routes/auth.py` returns nothing, and `python -m pytest -q` passes.

## P3-4: Persistent token revocation

**File:** `src/auth/jwt.py:22`

```python
_revoked_jtis: set[str] = set()
```

In-memory blocklist. It empties on every process restart, and with multiple workers each has its own copy. Logout is effectively cosmetic; a 7-day refresh token survives it.

**Lazy fix — a single DB table, not a service.** Create a `token_revocations` table (one migration, following the P2-2 pattern), and change `revoke_token_jti`/`is_token_revoked` to read/write it. Keep the API identical so nothing else changes:

```python
def revoke_token_jti(jti: str) -> None:
    _revoked_jtis.add(jti)                      # in-memory fast path
    # persist to token_revocations; best-effort, never block auth
```

`is_token_revoked` checks memory first, then the table. The memory set is a cache; the table is the source of truth.

**DONE WHEN:** `python -m pytest -q` passes, and the new table appears in `alembic upgrade head` output.

## P3-5: Close the gaps in the notifications + watchlist routers

**Why this task exists:** these two routers are registered in `main.py:143-144` but were outside the original audit. Both have now been read.

**The important parts are already correct — do not rewrite these files.** Every endpoint has an explicit `if user is None: raise HTTPException(401)`. All SQL is parameterized (`:uid`, `:make`, …) — no injection. `DELETE /watchlist/{item_id}` (`watchlist.py:78`) is correctly scoped `WHERE id = :id AND user_id = :uid`, so there is **no IDOR**. The backing tables exist (`src/models/price_alert.py`, `src/models/saved_valuation.py`, both registered in `src/models/__init__.py`).

Five gaps remain:

**a) No rate limiting.** `auth.py` decorates every route with `@limiter.limit(...)`; neither of these routers does. `POST /watchlist` (`watchlist.py:46`) lets one authenticated user insert unbounded rows. Add the decorator:

```python
from fastapi import Request
from src.api.dependencies import limiter
...
@router.post("/watchlist")
@limiter.limit("30/minute")
async def save_to_watchlist(request: Request, req: SaveValuationRequest, ...):
```

`slowapi` requires the handler to accept `request: Request` as a parameter — see `auth.py:55` for the working pattern. Adding the decorator **without** that parameter raises at runtime, so add both or neither.

**b) `GET /watchlist` has no row cap.** `watchlist.py:29` is `ORDER BY created_at DESC` with no `LIMIT`, while `notifications.py:23` correctly uses `LIMIT 50`. Add `LIMIT 100` to match.

**c) DELETE reports success when nothing was deleted.** `watchlist.py:77-86` returns `{"message": "Removed from watchlist"}` regardless of rowcount — deleting a nonexistent id, or another user's id, is indistinguishable from a real delete. Capture the result and raise 404 when `result.rowcount == 0`.

**d) Possible 500 on a NULL target_price.** `notifications.py:33` formats `{r.target_price:,.0f}` inside the branch taken when `last_triggered_at` is set. If `target_price` is NULL there, that format spec raises `TypeError` → HTTP 500. **Verify before changing:** `grep -n "target_price" src/models/price_alert.py`. If the column is nullable, guard it; if it is `nullable=False`, leave it alone.

**e) Zero API tests.** `grep -rn "watchlist" tests/` hits only `tests/e2e/test_ui_playwright.py` (a frontend test). Add one small `tests/api/test_watchlist.py` asserting 401-without-token on all four endpoints — that single test locks the auth guard in place and is the highest value per line here.

**DONE WHEN:**

```bash
grep -c "limiter.limit" src/api/routes/watchlist.py   # >= 1
grep -c "LIMIT" src/api/routes/watchlist.py           # >= 1
python -m pytest tests/api/test_watchlist.py -q       # passes
python -m pytest -q                                   # still green
```

---

# DONE — what "production ready" now means

When P0–P2 are all merged:

- Scraped listings flow: fetch → validate → normalize → score → **saved to Postgres** → used by `find_comps` → answered by `/valuate`
- `POST /v1/valuate` returns real, non-422 answers with `comp_count >= 5`
- Zero-yield scrapers fail loudly instead of reporting success
- Deploy branch `master` matches `render.yaml`; CORS locked to the Vercel origin; `/metrics` and `url_valuate` authenticated
- DB backups scheduled daily; schema-level constraints protect the user table
- The three data-corrupting scraper bugs (currency, make/model, dedup key) are fixed

P3 items are the remaining hardening — observability/log-shipping and OTel are a separate, deliberate effort beyond this list.

---

# FINAL — audit log for the executing model

Run this once at the end. Copy the output into your final report verbatim.

```bash
echo "=== 1. legacy deletions committed (expect 0 staged, 0 unstaged D) ===" ; git status --porcelain | grep -cE "^(D |.D)" || echo 0
echo "=== 2. deploy branch ===" ; grep "branch:" render.yaml
echo "=== 3. pipeline wired ===" ; grep -c "_persist" src/scrapers/base.py
echo "=== 4. zero-yield alarm ===" ; grep -c "zero_yield" src/pipeline/orchestrator.py
echo "=== 5. quality gate ===" ; grep -n "45" src/config/settings.py src/engine/comp_finder.py
echo "=== 6. CORS allowlist (expect the localhost defaults, NOT a bare ['*']) ===" ; grep -n "api_cors_origins" -A4 src/config/settings.py | head -12
echo "=== 7. yallamotor currency ===" ; grep -c "self.currency" src/scrapers/yallamotor/scraper.py
echo "=== 8. shared title parser ===" ; grep -c "extract_make_model" src/scrapers/title_parser.py
echo "=== 9. dedup guard ===" ; grep -c "not value.strip()" src/pipeline/validator.py
echo "=== 10. pagination cap ===" ; grep -c "_MAX_PAGES" src/scrapers/base.py
echo "=== 11. per-host limiter ===" ; grep -c "get_limiter" src/scrapers/rate_limiter.py
echo "=== 12. robots check ===" ; grep -c "_robots_allows" src/scrapers/base.py
echo "=== 13. backup cron ===" ; grep -c "schedule" .github/workflows/backup.yml
echo "=== 14. watchlist rate limit (P3-5, optional) ===" ; grep -c "limiter.limit" src/api/routes/watchlist.py || echo 0
echo "=== 15. full test run ===" ; python -m pytest -q 2>&1 | tail -3
```



