# Gap Closure Plan — for Model B

## HOW TO USE THIS DOCUMENT

You are closing 6 defects left open after the previous plan (`docs/PRODUCTION_READINESS_PLAN.md`) was executed. Rules:

1. **Do tasks in order.** G1 unblocks deployment; nothing else matters until it is done.
2. **One task = one commit.** Message = task ID + title, e.g. `G1: fix duplicate alembic revision id`.
3. **Every task has a `DONE WHEN` block. RUN IT.** Two tasks in the last round were marked complete without running their own check, and both were broken. Do not repeat that. If the check needs a database and you cannot start one, say so in your report — do not silently skip it and claim success.
4. **Do not refactor anything a task does not name.** Shortest diff that satisfies `DONE WHEN`.
5. **If a file or line does not match what is written here, STOP and report the mismatch.** Do not guess.
6. `python -m pytest -q` must pass at the end of every task. Baseline right now is **335 passed**. If your change drops that number, fix it in the same task.

**Standing verify commands** (from repo root `C:\Users\saari\projects\gcc-car-value`):

```bash
python -m pytest -q
alembic -c src/db/migrations/alembic.ini heads
ruff check src/ tests/
```

---

## CONTEXT: what is broken and why it matters

The previous plan wired up the pipeline successfully — persistence works, 335 tests pass, coverage went 36% → 60%. Six things were left broken:

| ID | Defect | Consequence |
|----|--------|-------------|
| **G1** | Duplicate alembic revision ID | **Container will not boot.** `alembic upgrade head` fails. |
| **G2** | 41+ untracked files, incl. a migration and a CI script | **Fresh clone is broken.** CI cannot run. No DB backups. |
| **G3** | Seed script inserts nonexistent columns | **Cannot prove the product works.** `/valuate` still unverified. |
| **G4** | Token revocation has no error handling | **HTTP 500 on every authenticated request** if the DB blips. |
| **G5** | Parser glues trim onto model name | **Zero comps** for any listing with a trim in the title. |
| **G6** | `dead_letter` has no index, scanned per auth request | Sequential scan on an unbounded table, every request. |

G1 and G2 are deployment blockers. G3 is the one that proves the product actually works. Do them in that order.

---

# G1: Fix the duplicate alembic revision ID — DEPLOYMENT BLOCKER

**Verified current state:**

```
$ alembic -c src/db/migrations/alembic.ini heads
UserWarning: Revision a1b2c3d4e5f6 is present more than once
1cbe748cf623 (head)
a1b2c3d4e5f6

$ alembic -c src/db/migrations/alembic.ini upgrade head --sql
FAILED: Multiple head revisions are present for given argument 'head'
```

Two files claim `revision = "a1b2c3d4e5f6"`:

| File | revision | down_revision |
|---|---|---|
| `a1b2c3d4e5f6_partition_management.py` | `a1b2c3d4e5f6` | `c42f2f2afaa8` |
| `a1b2c3d4e5f6_add_user_account_constraints.py` | `a1b2c3d4e5f6` ← **collision** | `1cbe748cf623` |

`docker/Dockerfile.api:29` is:

```
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn src.api.main:app --host 0.0.0.0 --port 8000"]
```

The upgrade fails → `&&` short-circuits → uvicorn never runs → **the container never starts.**

**Fix — rename ONLY the NEW file** — that is `a1b2c3d4e5f6_add_user_account_constraints.py`, the one whose `down_revision` is `1cbe748cf623`. Do not touch `a1b2c3d4e5f6_partition_management.py`; it is older, tracked, and may already be applied to a live database.

Two edits to `src/db/migrations/versions/a1b2c3d4e5f6_add_user_account_constraints.py`:

Line 6 — give it a unique ID:

```python
revision: str = "d4e5f6a7b8c9"
```

Line 7 — leave `down_revision` exactly as it is:

```python
down_revision: Union[str, Sequence[str], None] = "1cbe748cf623"
```

Then rename the file to match its new revision (alembic does not require this, but every other file in the directory follows the convention):

```bash
git mv src/db/migrations/versions/a1b2c3d4e5f6_add_user_account_constraints.py \
       src/db/migrations/versions/d4e5f6a7b8c9_add_user_account_constraints.py
```

If `git mv` fails because the file is untracked, use a plain `mv`.

**The correct chain after this fix:**

```
c42f2f2afaa8 (initial)
  └─ a1b2c3d4e5f6 (partition_management)
       └─ b7c8d9e0f1a2 (integrity_constraints)
            └─ 1cbe748cf623 (performance_indexes)
                 └─ d4e5f6a7b8c9 (user_account_constraints)   ← single head
```

**DONE WHEN — all three must pass:**

```bash
# 1. exactly one head, and no duplicate-revision warning
alembic -c src/db/migrations/alembic.ini heads
#    expect: "d4e5f6a7b8c9 (head)" and NOTHING else, no UserWarning

# 2. the Dockerfile's boot command resolves
alembic -c src/db/migrations/alembic.ini upgrade head --sql > /dev/null && echo "UPGRADE OK"

# 3. tests still green
python -m pytest -q
```

---

# G2: Commit the untracked files — FRESH CLONE + CI ARE BROKEN

**Verified current state:** 43 untracked entries. Three of them break things right now:

| Untracked file | What breaks |
|---|---|
| `src/db/migrations/versions/1cbe748cf623_add_performance_indexes.py` | It is the **parent** of G1's migration. A fresh clone has a dangling `down_revision` and migrations fail entirely. |
| `scripts/validate_routes.py` | `.github/workflows/ci.yml:97` runs `python scripts/validate_routes.py`. **CI fails on a fresh checkout.** |
| `.github/workflows/backup.yml` | Has a working cron (`0 3 * * 0`) and `workflow_dispatch`, but GitHub only runs committed workflows. **No backups exist.** |

**Step 0 — before any group: gitignore the Playwright scratch.** The working tree holds ~32 more untracked entries than the 43 counted by a top-level `??` scan — Playwright profile dirs (`tmp-*`) and audit screenshots (`theme-*.png`), totalling ~191 MB, including Chrome credential stores (`Login Data`). These must never be committed. Add them first:

```bash
cat >> .gitignore <<'EOF'

# ---- Local design/QA scratch (Playwright profiles + audit screenshots) ----
tmp-*/
theme-*.png
EOF
```

Verify they disappear from status:

```bash
git status --porcelain | grep -c "^??"    # was 43, now lower (should be ~11 real files)
```

**This task is triage, not a blanket `git add .`.** Commit in four separate, reviewable groups.

### Group 1 — the files that break the build

```bash
git add src/db/migrations/versions/1cbe748cf623_add_performance_indexes.py
git add scripts/validate_routes.py
git add .github/workflows/backup.yml scripts/backup_db.sh
git commit -m "G2a: track perf-indexes migration, CI route validator, backup workflow"
```

Before committing `backup_db.sh`, read it and confirm it contains **no hardcoded credentials** — `backup.yml` passes `DATABASE_URL_SYNC`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET` in via GitHub secrets, so the script must read them from the environment.

### Group 2 — backend source and tests

```bash
git add src/ tests/ scripts/seed_neon.py .dockerignore
git status --porcelain | grep -E "^(A|M)" | grep -vE "^\?\?"   # review before committing
git commit -m "G2b: commit backend session work — security headers, startup validation, tests"
```

Review `git diff --cached src/api/main.py` before you commit. You are shipping security middleware; confirm it is complete and not half-written.

### Group 3 — frontend

```bash
git add ui/ vercel.json
git commit -m "G2c: commit frontend pages, theme, and Vercel routing config"
```

### Group 4 — docs and config

```bash
git add docs/ README.md .env.example .gitignore .github/ docker/
git commit -m "G2d: commit docs, CI additions, Docker and env config"
```

**Two files to decide on explicitly — do not commit blindly:**

- `run_audit.ps1` — a scratch audit script. Commit only if you judge it reusable; otherwise delete it.
- `.env.example` — **read the diff first.** Confirm it contains only placeholder values, never a real secret.

**After all four groups + the `.env.example` check, dispose of any remaining untracked scratch** (`scripts/dubicars_scraper.py` is broken and untracked — delete it if it is scratch; commit it separately if it is meant to be kept, but do not leave it untracked).

**DONE WHEN:**

```bash
git status --porcelain | grep -c "^??"     # 0 — no untracked files remain
git status --porcelain | grep -c "^ M"     # 0 — no modified files remain (all committed)
git ls-files src/db/migrations/versions/ | wc -l    # expect 5
git ls-files scripts/validate_routes.py .github/workflows/backup.yml   # both listed
python -m pytest -q
```

If either count is non-zero, that is a leftover — resolve it (commit or delete) before marking this done. Do not leave anything untracked.

---

# G3: Rewrite the seed script — THE TASK THAT PROVES THE PRODUCT WORKS

**Verified current state:** `scripts/seed_demo_listings.py` uses raw SQL against columns that do not exist.

```
INSERT references columns not in the table: ['captured_at', 'found_on', 'price_aed']
NOT NULL columns the INSERT omits (14): exchange_rate, exchange_timestamp,
  external_id, first_seen_at, last_seen_at, normalized_price_aed,
  normalizer_version, original_currency, original_price, parser_version,
  pipeline_run_id, schema_version, source, status
```

The script cannot run. Because it cannot run, `/valuate` has **never been verified end-to-end** — the single most important claim in the whole effort is still unproven.

**Fix:** replace the file with the ORM version below. The ORM version cannot drift from the schema the way hand-written SQL did — that is the entire point of the rewrite. Do not "fix" the raw SQL.

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
from src.models.pipeline_run import PipelineRun

SOURCE = "seed_demo"

# (make, model, base_price_aed, price_drop_per_year)
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
SPECS = ["GCC", "GCC", "GCC", "US", "Japan"]  # GCC-weighted, matches the real market


def build_rows(run_id: str) -> list[Listing]:
    rng = random.Random(42)  # deterministic — reruns produce the same spread
    now = datetime.now(timezone.utc)
    rows: list[Listing] = []

    for make, model, base, per_year in MODELS:
        for year in range(2016, 2024):
            age = 2024 - year
            for _ in range(6):  # 6 per (model, year) => 48 per model, 384 total
                city, country = rng.choice(CITIES)
                spec = rng.choice(SPECS)
                price = base - (per_year * age)
                price *= rng.uniform(0.90, 1.10)          # market spread
                price *= 1.0 if spec == "GCC" else 0.90   # non-GCC discount
                price = round(max(price, 5000.0), 2)
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
                    make=make,
                    model=model,
                    year=year,
                    spec=spec,
                    city=city,
                    country=country,
                    mileage_km=mileage,
                    body_type="SUV" if per_year > 15000 else "sedan",
                    transmission="automatic",
                    fuel_type="petrol",
                    seller_type=rng.choice(["dealer", "private"]),
                    original_price=price,
                    original_currency="AED",
                    exchange_rate=1.0,
                    exchange_timestamp=now,
                    normalized_price_aed=price,
                    quality_score=85,
                    quality_flags=[],
                    schema_version=1,
                    parser_version="seed_v1",
                    normalizer_version="seed_v1",
                    pipeline_run_id=run_id,
                ))
    return rows


async def main() -> None:
    clear = "--clear" in sys.argv
    async with async_session_factory() as session:
        result = await session.execute(delete(Listing).where(Listing.source == SOURCE))
        if clear:
            await session.execute(delete(PipelineRun).where(PipelineRun.source == SOURCE))
            await session.commit()
            print(f"cleared {result.rowcount} seeded rows")
            return

        run_id = str(uuid.uuid4())
        session.add(PipelineRun(
            run_id=run_id,
            source=SOURCE,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            success=True,
        ))
        await session.flush()          # parent must exist before the FK children

        rows = build_rows(run_id)
        session.add_all(rows)
        await session.commit()
        print(f"seeded {len(rows)} listings across {len(MODELS)} models")


if __name__ == "__main__":
    asyncio.run(main())
```

**IMPORTANT — `pipeline_run_id` needs a real parent row.** Verified against the schema:

```
listings.pipeline_run_id: nullable=False
FKs on listings: pipeline_run_id -> pipeline_runs.run_id
```

It is **NOT NULL and carries a foreign key** (`fk_listings_pipeline_run`, added by `1cbe748cf623`). So a bare `uuid.uuid4()` violates the FK, and `None` violates NOT NULL. The seed must insert a `PipelineRun` row first and reuse its `run_id`.

`pipeline_runs` needs nothing mandatory beyond its defaults (`id`, `run_id`, `started_at` all have defaults), so this is three extra lines. Add the import:

```python
from src.models.pipeline_run import PipelineRun
```

Change `build_rows()` to accept the run id instead of generating its own — replace the `run_id = str(uuid.uuid4())` line with a parameter:

```python
def build_rows(run_id: str) -> list[Listing]:
    rng = random.Random(42)  # deterministic — reruns produce the same spread
    now = datetime.now(timezone.utc)
    rows: list[Listing] = []
```

Then in `main()`, create the parent row and flush it before adding listings:

```python
        rows_run_id = str(uuid.uuid4())
        session.add(PipelineRun(
            run_id=rows_run_id,
            source=SOURCE,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            success=True,
        ))
        await session.flush()          # parent must exist before the FK children

        rows = build_rows(rows_run_id)
        session.add_all(rows)
        await session.commit()
        print(f"seeded {len(rows)} listings across {len(MODELS)} models")
```

`--clear` must also remove the seeded parent row, after deleting the listings that reference it:

```python
        if clear:
            await session.execute(delete(PipelineRun).where(PipelineRun.source == SOURCE))
            await session.commit()
            print(f"cleared {result.rowcount} seeded rows")
            return
```

**Do not drop the FK** to make the seed pass. The FK is correct; the seed is what bends.

**DONE WHEN — you must actually run this, not just read it:**

```bash
# 1. migrations applied (needs a running Postgres — see note below)
alembic -c src/db/migrations/alembic.ini upgrade head

# 2. seed
python scripts/seed_demo_listings.py
#    expect: "seeded 384 listings across 8 models"

# 3. start the API
uvicorn src.api.main:app --port 8000

# 4. in a second shell — the real test
curl -s -X POST http://localhost:8000/v1/valuate \
  -H "Content-Type: application/json" \
  -d '{"make":"Toyota","model":"Land Cruiser","year":2019,"mileage_km":90000,"spec":"GCC","country":"AE"}'
```

The response must contain a **non-zero `estimate`**, **`comp_count >= 10`**, and **`confidence` of `medium` or `high`**.

- HTTP 422 → the seed did not land, or `quality_score` is below the gate (`45`, set in `settings.py:31` and `comp_finder.py:86`).
- Connection error → Postgres is not running. Use `docker compose -f docker/docker-compose.yml up -d db`, or a local instance with `DATABASE_URL` pointed at it.

**If you cannot start a database, say so explicitly in your report and mark G3 as UNVERIFIED.** Do not mark it done. This is the exact failure that let a broken seed script ship last round.

---

# G4: Stop a DB blip from 500-ing every authenticated request

**Verified current state** (`src/auth/jwt.py:103-139`), confirmed by AST inspection:

```
revoke_token_jti: has try/except = False
is_token_revoked:  has try/except = False
verify_token except clause catches only: jwt.PyJWTError
```

`verify_token` calls `await is_token_revoked(jti)` inside its `try`, but the only `except` is `jwt.PyJWTError`. A `sqlalchemy.exc.OperationalError` from an unreachable database propagates straight out of `verify_token`, through `get_current_user`, and becomes **HTTP 500 on every authenticated request.** The plan that specified this said "best-effort, never block auth."

A second cost: the in-memory fast path was removed, so every single token verification now makes a database round trip.

**Fix — four edits to `src/auth/jwt.py`.**

**Edit 0 — add the missing `uuid` import.** Verified: `jwt.py` imports `text` (line 20) and `async_session_factory` (line 21), but **not** `uuid`. Add it with the other stdlib imports at the top:

```python
import uuid
```

This is required by Edit 2. Without it the INSERT raises `NameError`.

Edit 1 — restore the in-memory cache. Add near the top, after the `JWT_ALGORITHM` constants:

```python
# In-memory cache of revoked JTIs. The DB is the source of truth; this is a
# fast path that also keeps auth working during a brief DB outage.
_revoked_jtis: set[str] = set()
```

Edit 2 — replace `revoke_token_jti` (line 103):

```python
async def revoke_token_jti(jti: str) -> None:
    """Revoke a token by its JTI. Writes through to the DB, caches in memory."""
    _revoked_jtis.add(jti)
    try:
        async with async_session_factory() as db:
            await db.execute(
                text("INSERT INTO dead_letter (id, source, external_id, rejection_reason, raw_data) "
                     "VALUES (:id, 'auth', :jti, 'revoked_token', '{}')"),
                {"id": str(uuid.uuid4()), "jti": jti},
            )
            await db.commit()
    except Exception as exc:
        # Never let a DB failure block logout. The in-memory set still holds
        # for this process; the revocation is lost on restart.
        logger.error("token_revoke_persist_failed", jti=jti[:8] + "...", error=str(exc)[:200])
    logger.info("token_revoked", jti=jti[:8] + "...")
```

**Why the explicit `id`:** verified — `dead_letter.id` is `NOT NULL` with **no server default** (its only default is the Python-side `uuid.uuid4` on the ORM column, which raw SQL bypasses). The current code omits `id`, so **every revocation INSERT fails**. Wrapping that in `except Exception` without binding `id` would turn a 100%-reproducible failure into a silent one — strictly worse. Bind the id.

Edit 3 — replace `is_token_revoked` (line 114):

```python
async def is_token_revoked(jti: str) -> bool:
    """Check revocation. Memory first, then DB. Fails open on DB error."""
    if jti in _revoked_jtis:
        return True
    try:
        async with async_session_factory() as db:
            result = await db.execute(
                text("SELECT id FROM dead_letter WHERE source = 'auth' "
                     "AND external_id = :jti AND rejection_reason = 'revoked_token'"),
                {"jti": jti},
            )
            revoked = result.fetchone() is not None
    except Exception as exc:
        # Fail OPEN: a DB outage must not 500 every authenticated request.
        # Trade-off: a revoked token stays usable until the DB recovers.
        # ponytail: acceptable for a 15-minute access token; revisit if
        # revocation ever needs to be hard-guaranteed.
        logger.error("token_revocation_check_failed", error=str(exc)[:200])
        return False
    if revoked:
        _revoked_jtis.add(jti)   # cache the hit
    return True if revoked else False
```

**Do not change any function signature.** All three functions are already `async` and every caller already awaits them — `auth.py:111,118,146,148`, `dependencies.py:46`, and 10 `await verify_token(...)` call sites across `tests/test_auth.py` and `tests/auth/test_dependencies.py`. That propagation is correct; leave it alone.

**Note on test coverage:** none of those tests exercise `revoke_token_jti` or `is_token_revoked` directly — both are mocked out (`tests/test_auth.py:15`, `tests/auth/test_dependencies.py:8` patch `is_token_revoked`). So `pytest` passing proves nothing about this task. That is why the behavioural check below is mandatory, not optional.

**DONE WHEN — all three must pass:**

```bash
# 1. structural: both functions have try/except. ASSERTS, so exit code carries the signal.
python -c "
import ast
t = ast.parse(open('src/auth/jwt.py').read())
got = {fn.name: any(isinstance(n, ast.Try) for n in ast.walk(fn))
       for fn in ast.walk(t)
       if isinstance(fn, ast.AsyncFunctionDef)
       and fn.name in ('revoke_token_jti','is_token_revoked')}
assert got == {'revoke_token_jti': True, 'is_token_revoked': True}, got
print('structural OK:', got)
"

# 2. behavioural: with the DB unreachable, is_token_revoked must return False (fail OPEN),
#    not True and not raise. This is the whole point of G4.
python -c "
import asyncio, unittest.mock as m, src.auth.jwt as j
with m.patch.object(j, 'async_session_factory', side_effect=RuntimeError('db down')):
    out = asyncio.run(j.is_token_revoked('deadbeefcafe'))
assert out is False, f'expected False (fail open), got {out!r}'
print('fail-open OK: returned', out)
"

# 3. tests G4 can affect (the two auth suites)
python -m pytest tests/test_auth.py tests/auth/ -q
```

Check 2 is the one that matters. `except Exception: return True` would satisfy check 1 while doing the **exact opposite** of G4's goal — 401-ing every request during a DB outage instead of letting them through.

**On the `dead_letter` table:** the original plan asked for a dedicated `token_revocations` table, and reusing `dead_letter` mixes auth records into the data-quality queue (`promoter.py` writes rejected listings there). It works, and changing it now means another migration right after G1 fixed the chain. **Leave it.** Flag it in your report as a known deviation for a later cleanup.

---

# G5: Stop the parser gluing trim onto the model name

**Verified current state:**

```
'Toyota Camry SE 2021'            -> ('Toyota', 'Camry SE')
'2018 Nissan Patrol Platinum GCC' -> ('Nissan', 'Patrol Platinum')
```

`comp_finder.py:83` matches `Listing.model` **exactly**. Seeded and canonical data store `Camry` and `Patrol`, so a scraped `Camry SE` matches nothing — **zero comps**, which is the exact failure P1-2 existed to prevent.

**Scope — read this before starting.** This task closes the *trailing-trim* case. It does NOT fully close the "zero comps" gap, because a second, independent parser behavior breaks exact matching for hyphenated nameplates:

```
'Mercedes-Benz S500 2019'  -> parser: ('Mercedes Benz', 'S500')   # hyphen → space
seed/normalizer stores     -> ('Mercedes-Benz', ...)              # hyphen kept
exact match?               -> NO
```

`title_parser.py:43` rewrites hyphens to spaces, but `normalize_make` (`normalizer.py:55`) stores the hyphenated canonical form. So any hyphenated make silently mismatches its own stored listings. **Fix that here too — it is two lines and it is the same class of bug.** In `title_parser.py`, add `"mercedes benz"` back to the multi-word match and normalize the output hyphen:

In `_title()` (line 72), normalize `"Mercedes Benz"` to `"Mercedes-Benz"`:

```python
def _title(make: str) -> str:
    if make.lower() == "mercedes benz":
        return "Mercedes-Benz"
    words = make.split()
    return " ".join(w.upper() if w.lower() in _UPPER_MAKES else w.capitalize() for w in words)
```

This makes the parser output match the canonical stored form, so hyphenated makes participate in comps. Verify with the demo case `("Mercedes-Benz S500 2019", ("Mercedes-Benz", "S500"))` — update `demo()` accordingly.

**Report in your final note** which parts of G5 you completed: the trim fix, the hyphen fix, or both.

**Context you need:** the previous model hit this and changed the *test expectation* to match the buggy output instead of fixing the code. Do not do that. The `DONE WHEN` below asserts the correct values.

**Why not "just take one word":** `Lexus LX 570` and `Toyota Land Cruiser` are genuine two-word models. Truncating to one word breaks them. The fix keeps two words but drops a trailing **known trim token**.

**Fix — two edits to `src/scrapers/title_parser.py`.**

Edit 1 — add the trim set next to `MULTI_WORD_MAKES`:

```python
# Trailing tokens that are trim levels, not part of the model name.
# Deliberately excludes ambiguous words that are real model tokens:
# "sport" (Range Rover Sport), "limited", "base", "lx"/"gx" (Lexus models),
# and anything numeric ("LX 570", "320i").
# ALSO excludes "gt"/"gts" (Bentley Continental GT, Mercedes-AMG GT are real
# GCC-market model names) and "ex" (Infiniti EX nameplate).
# ponytail: a curated trim list caps out here; a real model catalogue is the
# proper fix if extraction accuracy ever becomes the bottleneck.
TRIM_WORDS = {
    "se", "le", "xle", "xse", "exl", "sr", "srt", "glx", "gxr", "vxr",
    "platinum", "signature", "ultimate", "touring",
    "premium", "luxury", "prestige", "diamond", "titanium",
    "v6", "v8", "turbo", "awd", "4wd", "4x4", "2dr", "4dr",
    "standard", "comfort",
}
```

Edit 2 — replace `_first_words` (line 65):

```python
def _first_words(text: str, n: int) -> str:
    """Take up to n words, dropping a trailing trim token.

    "Patrol Platinum" -> "Patrol"      (Platinum is a trim)
    "Land Cruiser"    -> "Land Cruiser" (Cruiser is part of the model)
    "LX 570"          -> "LX 570"       (570 is part of the model)
    """
    words = text.split()[:n]
    if len(words) == 2 and words[1].lower() in TRIM_WORDS:
        words = words[:1]
    return " ".join(words).strip()
```

Edit 3 — restore the correct expectation in `demo()` (line 82) and add the regression cases:

```python
    cases = [
        ("Toyota Camry 2020 GCC 50,000 km", ("Toyota", "Camry")),
        ("Land Rover Range Rover Vogue 2019", ("Land Rover", "Range Rover")),
        ("2018 Nissan Patrol Platinum GCC", ("Nissan", "Patrol")),
        ("Mercedes Benz C200 2021", ("Mercedes Benz", "C200")),
        ("BMW 320i 2017 | 80,000 km", ("BMW", "320i")),
        ("Lexus LX 570 2020 GCC Spec", ("Lexus", "LX 570")),
        ("Toyota Camry SE 2021", ("Toyota", "Camry")),
        ("Nissan Altima SR 2019", ("Nissan", "Altima")),
        ("Toyota Land Cruiser 2019 GCC", ("Toyota", "Land Cruiser")),
        ("Mitsubishi Pajero 2020", ("Mitsubishi", "Pajero")),
    ]
```

All ten of these have been verified to pass with the fix above. If any fails, the bug is in your edit, not in the expectation.

**Edit 4 — fix the second copy of the buggy expectation.** Verified: `tests/scrapers/test_dubizzle_parser.py:41` asserts the buggy behavior:

```python
assert _extract_make_model("2022 Toyota Camry SE") == ("Toyota", "Camry SE")
```

After Edit 3, this test **fails** — the buggy expectation now lives in two places, and the plan's `DONE WHEN` runs `python -m pytest -q`, which would catch it. Change line 41 to the correct value:

```python
assert _extract_make_model("2022 Toyota Camry SE") == ("Toyota", "Camry")
```

**The "do not change the expectation" warning above applies to `demo()`'s already-correct values — not to this test.** This test is the *buggy* copy; it must change. If `pytest` fails after Edit 3, grep the tests for `"Camry SE"` or `"Patrol Platinum"` — a leftover buggy assertion is the cause.

**DONE WHEN:**

```bash
python -m src.scrapers.title_parser     # "title_parser: 10 cases passed"
python -m pytest -q
```

---

# G6: Index `dead_letter` for the per-request revocation lookup

**Do this only after G1 is merged and the migration chain is verified single-head.**

**Verified current state:** `dead_letter` has **no index on `(source, external_id)`** — only the implicit primary-key index on `id`, which this query cannot use. G4's `is_token_revoked` runs this on every authenticated request that misses the in-memory cache:

```sql
SELECT id FROM dead_letter
WHERE source = 'auth' AND external_id = :jti AND rejection_reason = 'revoked_token'
```

`dead_letter` also receives every quality-rejected listing from `promoter.py:18-26`, so it grows without bound. That is a sequential scan over a growing table, per request.

**Fix — create exactly this file:**

`src/db/migrations/versions/e5f6a7b8c9d0_index_dead_letter.py`

The path matters. Alembic only discovers migrations in `src/db/migrations/versions/`. A file placed anywhere else is **silently ignored**, and the head check below would still pass while the index was never created.

```python
"""Index dead_letter for token-revocation lookups."""
from typing import Sequence, Union
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"   # G1's new id
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_dead_letter_source_external_id",
        "dead_letter",
        ["source", "external_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_dead_letter_source_external_id", table_name="dead_letter")
```

**Also declare the index on the model, in the same commit.** Otherwise the database and `Base.metadata` diverge, and the next `alembic revision --autogenerate` will see an index in the DB that is absent from metadata and helpfully emit a `drop_index` for it.

Verified: `src/models/dead_letter.py` has no `__table_args__` today, and does not import `Index`. Two edits — line 2, add `Index` to the existing import:

```python
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func, Index
```

and after line 7 (`__tablename__`), add:

```python
    __table_args__ = (
        Index("ix_dead_letter_source_external_id", "source", "external_id"),
    )
```

**DONE WHEN:**

```bash
# head is exactly the new revision — asserts identity, not just count
alembic -c src/db/migrations/alembic.ini heads | grep -q "e5f6a7b8c9d0 (head)" \
  && echo "HEAD OK" || echo "HEAD WRONG — is the file in versions/?"

# offline: proves the chain resolves and the DDL compiles, no live DB needed
alembic -c src/db/migrations/alembic.ini upgrade head --sql > /dev/null \
  && echo "UPGRADE OK" || echo "UPGRADE FAILED"

python -m pytest -q
```

Use `--sql` (offline). Without it, alembic connects to a real database, which this check does not need and which will fail for reasons unrelated to G6.

---

# NOT IN SCOPE — deliberately

Do not do these. They are noted so you do not "helpfully" pick them up.

- **683 ruff errors.** Pre-existing baseline (`src/core/` alone has 64, and nobody touched it this round). CI does gate on `ruff check src/ tests/`, so it needs an owner — but it is a separate, mechanical, ~40-file commit and does not belong mixed into these fixes.
- **8 `invalid-syntax` errors in `scripts/dubicars_scraper.py`.** Real — the file does not parse — but it is an untracked scratch file outside `src/` and `tests/`, so CI never sees it. Either delete it or fix it in its own commit, not here.
- **The `dead_letter` reuse for auth revocations** (see G4). Works; deviates from the original design. Flag, do not fix.
- **The P0-6 mis-attributed commit.** The CORS allowlist fix is correct and present in HEAD; it just landed inside commit `a71f6ba` labelled P0-4. Rewriting 16 commits of history to relabel it is not worth the risk.

---

# FINAL AUDIT — run this and paste the output verbatim into your report

```bash
echo "=== 1. single alembic head, no duplicate warning ==="
alembic -c src/db/migrations/alembic.ini heads 2>&1

echo "=== 2. Dockerfile boot command resolves ==="
alembic -c src/db/migrations/alembic.ini upgrade head --sql > /dev/null 2>&1 && echo "UPGRADE OK" || echo "UPGRADE FAILED"

echo "=== 3. nothing left uncommitted (both must be 0) ==="
echo "untracked: $(git status --porcelain | grep -c '^??')"
echo "modified:  $(git status --porcelain | grep -c '^ M')"

echo "=== 4. critical files tracked ==="
git ls-files scripts/validate_routes.py .github/workflows/backup.yml src/db/migrations/versions/1cbe748cf623_add_performance_indexes.py

echo "=== 5. seed script has no bogus columns (expect 0) ==="
grep -c "price_aed\|found_on\|captured_at" scripts/seed_demo_listings.py || echo 0

echo "=== 6. jwt: structural + behavioural fail-open ==="
python -c "
import ast, asyncio, unittest.mock as m
t = ast.parse(open('src/auth/jwt.py').read())
got = {fn.name: any(isinstance(n, ast.Try) for n in ast.walk(fn))
       for fn in ast.walk(t)
       if isinstance(fn, ast.AsyncFunctionDef) and fn.name in ('revoke_token_jti','is_token_revoked')}
assert got == {'revoke_token_jti': True, 'is_token_revoked': True}, got
import src.auth.jwt as j
with m.patch.object(j, 'async_session_factory', side_effect=RuntimeError('db down')):
    out = asyncio.run(j.is_token_revoked('deadbeefcafe'))
assert out is False, f'expected fail-open False, got {out!r}'
print('jwt OK: structural', got, '| fail-open returned', out)
"

echo "=== 7. parser drops trim, keeps real 2-word models ==="
python -m src.scrapers.title_parser
grep -rn "Camry SE\|Patrol Platinum" tests/ --include=*.py && echo "^^ LEFTOVER BUGGY ASSERTION" || echo "no stale assertions"

echo "=== 8. full test suite (baseline: 335 passed) ==="
python -m pytest -q 2>&1 | tail -3
```

**Also report, in prose:**

1. Did you run G3's `/valuate` curl against a live database? Paste the JSON response. If you could not start a database, say so plainly and mark G3 UNVERIFIED.
2. Any task where the file or line numbers did not match this document.
3. Any `DONE WHEN` check you could not run, and why.
4. For G5: did you do the trim fix, the hyphen fix, or both?
5. Anything you chose to delete (e.g. `run_audit.ps1`, `scripts/dubicars_scraper.py`) and why.

**A note on `python -m pytest -q`:** the baseline is **335 passed**, verified on a clean tree. The e2e/Playwright suite (`tests/e2e/`, 23 tests) passed on two consecutive runs during verification, so it should be stable — but it drives a real browser, so if it fails intermittently, re-run it once before assuming your change caused it. Do not start editing e2e or frontend code to make the gate pass; if e2e fails twice in a row and your diff does not touch `ui/`, report it and move on.
