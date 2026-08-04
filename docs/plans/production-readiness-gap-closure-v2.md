# Production Readiness — Final Gap Closure v2

## HOW TO USE THIS DOCUMENT (read this fully before touching anything)

Close gaps found by a 3-model cross-audit (DeepSeek / Opus 4.8 / GPT 5.6 Sol),
then re-verified against the live code on 2026-08-04. This version is written so
it can be executed literally, top to bottom, with no judgement calls.

### Non-negotiable rules

1. **Order is fixed.** Do tasks in this exact order: **F1 → F2 → C1 → C2 → G2 → G3 → G4 → G1 → O1 → O2**.
   F1/F2 are one-line correctness bugs. C1/C2 are tests. G* are gates. G1/O1/O2 are humans-only (see below).
2. **One task = one commit.** Commit message = the task ID + its title, e.g. `F1: fix drift bug in admin stats`.
3. **Run every command from the repo root** `C:\Users\saari\projects\gcc-car-value`, in Git Bash, **except** where a step literally says `cd ui`.
4. **Every task has a `DONE WHEN` block. Run it. All lines must match before you commit.** If any line does not match, STOP and re-read the task — do not improvise.
5. **Shortest diff. No refactoring. Touch only the files each task names.**
6. **NEVER run `ruff check --fix --unsafe-fixes`.** That flag is what *created* bug F1 (it rewrote `== False` into `not x`). Only ever run `ruff check` (no `--fix`) to check, and `ruff check --fix` (safe fixes only) if you must.
7. **The test suite is the ground truth.** `python -m pytest -q` currently ends with `335 passed`. After each task it must still end with a line that contains `passed` and **must not contain `failed`**. Task C1 raises it to `343 passed`; task C2 raises it to `344 passed`. Never let the number go *down*.

### How to read a `DONE WHEN` block

Each line is a shell command followed by the exact output you must see. If a
command prints the expected text, that line passes. If it prints anything else
(or errors), that line fails. A task is done only when **all** its lines pass.

### Tasks a model CANNOT do (humans only)

**G1, O1, O2 require clicking in the Render / Vercel dashboards or holding cloud
secrets.** A model cannot perform them. For those tasks: do the verification
command, and if it fails, print `NEEDS HUMAN: <task id>` and move on. Do not fake
them.

---

## CONTEXT

Verified gaps (re-confirmed by reading the live source on 2026-08-04):

| # | Defect | Status on 2026-08-04 | Priority |
|---|--------|----------------------|----------|
| **F1** | `admin.py:54` — `not DriftEvent.acknowledged` is `not <Column>` = always `False`. Unacknowledged-drift count is silently always 0. Introduced by ruff `--unsafe-fixes` (E712: `== False` → `not x`). | **STILL PRESENT** (confirmed line 54) | IMMEDIATE |
| **F2** | `main.py:80` imports `shutdown_tracing` from `provider.py`; that function does not exist. `except Exception: pass` swallows the ImportError, so telemetry is never flushed on SIGTERM. | **STILL PRESENT** (confirmed no `def shutdown_tracing`) | IMMEDIATE |
| **C1** | `src/pipeline/validator.py` — 0% coverage. Gate for all scraped data. | **STILL 0%** | HIGH |
| **C2** | Statistical engine direct tests. | **MOSTLY DONE ALREADY** — `tests/engine/test_statistical.py` already exercises confidence, bootstrap CI, and `valuate()` via monkeypatch. Only the mileage-direction assertion is missing. | LOW (was HIGH) |
| **G2** | `mypy src/` = ~117 errors → CI red on master. F1/F2 remove 2 of them. | STILL RED | HIGH |
| **G3** | Frontend `npm run lint` — no ESLint config file exists. | UNCHANGED | HIGH |
| **G4** | Frontend `npm audit` — 2 high (vite GHSA-g4jq, brace-expansion ReDoS GHSA-mh99). | UNCHANGED | MEDIUM |
| **G1** | Production Render `/v1/health/ready` = 503 (old image deployed). | HUMAN ONLY | IMMEDIATE-ops |
| **O1** | Vercel auto-deploy branch not set to `master`. | HUMAN ONLY | MEDIUM |
| **O2** | Backup workflow never verified end-to-end. | HUMAN ONLY | LOW |

---

## PHASE 1: CORRECTNESS BUGS (do first)

### F1: Fix drift bug in admin stats

**File:** `src/api/routes/admin.py`, line 54 (inside `platform_stats`).

**Why the obvious fix is wrong:** the previous plan said to change it to
`DriftEvent.acknowledged == False`. **Do NOT do that.** The repo's ruff config
selects the `E` rules, so `== False` is an E712 lint error, and `ruff check
--fix --unsafe-fixes` rewrites it straight back to `not DriftEvent.acknowledged`
— reintroducing this exact bug. Use `.is_(False)`, which is correct SQL and
which ruff's E712 never touches (it only matches `==`/`!=` comparisons).

**Make exactly this edit** (find the first string, replace with the second):

FIND:
```python
        .where(not DriftEvent.acknowledged, DriftEvent.threshold_exceeded)
```
REPLACE WITH:
```python
        .where(DriftEvent.acknowledged.is_(False), DriftEvent.threshold_exceeded)
```

**DONE WHEN** (all four lines must pass):
```bash
grep -n "acknowledged.is_(False)" src/api/routes/admin.py        # prints line 54
grep -c "not DriftEvent.acknowledged" src/api/routes/admin.py    # prints 0
python -m ruff check src/api/routes/admin.py                     # prints: All checks passed!
python -m pytest -q 2>&1 | tail -1                                # contains "passed", not "failed"
```
**COMMIT:** `F1: fix drift bug in admin stats`

---

### F2: Add `shutdown_tracing` to the tracing provider

**Problem:** `src/api/main.py` line 80 does
`from src.core.tracing.provider import shutdown_tracing` but that function does
not exist in `src/core/tracing/provider.py`. The import fails and is silently
swallowed, so OpenTelemetry spans are never flushed on shutdown.

**Two edits, two files.**

**Edit 1 — `src/core/tracing/provider.py`.** Insert this new function
immediately **before** the line `def _do_init() -> None:` (currently line 62).

FIND:
```python
def _do_init() -> None:
    """Internal OpenTelemetry SDK initialization."""
```
REPLACE WITH:
```python
def shutdown_tracing() -> None:
    """Flush and shut down the OTel tracer provider. No-op if tracing disabled."""
    try:
        from opentelemetry import trace
        provider = trace.get_tracer_provider()
        if hasattr(provider, "shutdown"):
            provider.shutdown()
    except Exception as e:  # noqa: BLE001 - shutdown must never raise
        logger.warning("tracing_shutdown_failed", error=str(e)[:200])


def _do_init() -> None:
    """Internal OpenTelemetry SDK initialization."""
```

**Edit 2 — `src/core/tracing/__init__.py`.** Export the new name (two lines).

FIND:
```python
from src.core.tracing.provider import init_tracing, is_tracing_enabled
```
REPLACE WITH:
```python
from src.core.tracing.provider import init_tracing, is_tracing_enabled, shutdown_tracing
```

FIND:
```python
    "init_tracing", "is_tracing_enabled",
```
REPLACE WITH:
```python
    "init_tracing", "is_tracing_enabled", "shutdown_tracing",
```

**Do NOT touch `src/api/main.py`** — its import is already correct; it was just
importing a name that didn't exist yet. This task makes it exist.

**DONE WHEN** (all must pass):
```bash
grep -n "def shutdown_tracing" src/core/tracing/provider.py                    # prints one line
python -c "from src.core.tracing import shutdown_tracing; print('ok')"          # prints: ok
python -c "from src.core.tracing.provider import shutdown_tracing; print('ok')" # prints: ok
python -m ruff check src/core/tracing/                                          # All checks passed!
python -m pytest -q 2>&1 | tail -1                                              # "passed", not "failed"
```
**COMMIT:** `F2: add shutdown_tracing to tracing provider`

---

## PHASE 2: COVERAGE

### C1: Test the pipeline validator

**File under test:** `src/pipeline/validator.py`. Its public API (already read
and verified):
- `validate_listing(data: dict) -> ValidationResult`
- `ValidationResult` has: `.is_valid: bool`, `.errors: list[str]`, `.warnings: list[str]`, `.data: dict | None`
- Required fields: `make, model, year, asking_price, city, country, source, external_id`
- Missing/empty/whitespace required field → error string `"missing_required_field: <name>"`
- `country` must be one of `AE, SA, QA, KW, BH, OM`; other values fail schema validation
- `mileage_km > 500000` → still valid, but adds warning `"high_mileage"`

**Create the new file `tests/pipeline/test_validator.py` with EXACTLY this
content** (it was traced against the real code; all 8 tests pass as written — do
not edit the field values, they are chosen to satisfy the pandera schema):

```python
"""Direct tests for the scraped-listing validator (pipeline gate)."""
from src.pipeline.validator import validate_listing


def _valid(**overrides) -> dict:
    """A minimal listing that passes every validation rule. Override to break it."""
    base = {
        "make": "Toyota",
        "model": "Land Cruiser",
        "year": 2020,
        "asking_price": 250000,
        "mileage_km": 60000,
        "spec": "GCC",
        "city": "Dubai",
        "country": "AE",
        "source": "dubizzle_uae",
        "external_id": "abc-123",
    }
    base.update(overrides)
    return base


def test_valid_listing_passes():
    result = validate_listing(_valid())
    assert result.is_valid is True
    assert result.errors == []


def test_missing_make_fails():
    data = _valid()
    del data["make"]
    result = validate_listing(data)
    assert result.is_valid is False
    assert any("make" in e for e in result.errors)


def test_missing_asking_price_fails():
    data = _valid()
    del data["asking_price"]
    result = validate_listing(data)
    assert result.is_valid is False
    assert any("asking_price" in e for e in result.errors)


def test_empty_external_id_fails():
    result = validate_listing(_valid(external_id=""))
    assert result.is_valid is False
    assert any("external_id" in e for e in result.errors)


def test_whitespace_external_id_fails():
    result = validate_listing(_valid(external_id="   "))
    assert result.is_valid is False
    assert any("external_id" in e for e in result.errors)


def test_none_year_fails():
    result = validate_listing(_valid(year=None))
    assert result.is_valid is False
    assert any("year" in e for e in result.errors)


def test_invalid_country_fails_schema():
    # 'US' is not an allowed country code (AE/SA/QA/KW/BH/OM)
    result = validate_listing(_valid(country="US"))
    assert result.is_valid is False


def test_high_mileage_is_valid_but_warns():
    result = validate_listing(_valid(mileage_km=600000))
    assert result.is_valid is True
    assert "high_mileage" in result.warnings
```

**DONE WHEN** (all must pass):
```bash
python -m pytest tests/pipeline/test_validator.py -q 2>&1 | tail -1   # "8 passed"
python -m pytest -q 2>&1 | tail -1                                     # "343 passed", no "failed"
python -m ruff check tests/pipeline/test_validator.py                 # All checks passed!
```
**COMMIT:** `C1: add direct tests for pipeline validator`

---

### C2: Add the one missing statistical-engine assertion

**READ THIS BEFORE WRITING ANY CODE:** `tests/engine/test_statistical.py`
**already exists** and already covers, directly:
- confidence tiers high / medium / low / insufficient (`_compute_confidence`)
- bootstrap CI bounds + determinism (`_bootstrap_ci`)
- the full `valuate()` money-path via `monkeypatch` of `find_comps` — **no DB needed**
- insufficient-comps returns zero estimate

**Do NOT create `tests/engine/test_statistical_engine.py`.** That would duplicate
existing tests. The only genuinely missing assertion is **mileage adjustment
direction** (more km than the segment → the price is adjusted *down*).

**Append EXACTLY this one test to the END of the existing file
`tests/engine/test_statistical.py`** (it reuses the `make_comp` helper already
defined at the top of that file; traced against the real `valuate()` — it passes):

```python


@pytest.mark.asyncio
async def test_mileage_adjustment_direction_is_downward(monkeypatch):
    """Target has more km than the segment → mileage adjustment must be negative."""
    from src.engine import statistical

    comps = [make_comp(price=80000, days=5) for _ in range(20)]
    for c in comps:
        c.mileage_km = 30000  # segment is low-mileage

    async def mock_find_comps(*args, **kwargs):
        return comps

    monkeypatch.setattr(statistical, "find_comps", mock_find_comps)

    result = await statistical.valuate(
        session=None, make="Toyota", model="Camry", year=2020,
        mileage_km=100000, spec="GCC", country="AE", city="Dubai",
    )

    mileage_adj = [a for a in result.adjustments if a.reason == "mileage"]
    assert mileage_adj, "expected a mileage adjustment"
    assert mileage_adj[0].amount < 0  # more km than segment → price down
```

**DONE WHEN** (all must pass):
```bash
python -m pytest tests/engine/test_statistical.py -q 2>&1 | tail -1        # "13 passed"
python -m pytest tests/engine/test_statistical.py -q -k mileage_adjustment_direction 2>&1 | tail -1  # "1 passed"
python -m pytest -q 2>&1 | tail -1                                          # "344 passed", no "failed"
```
**COMMIT:** `C2: assert mileage adjustment direction in statistical engine`

---

## TRACK G — CI / Code Quality Gates

### G2: Drive `mypy src/` to zero errors

Run `python -m mypy src/` and fix top to bottom. F1 and F2 already removed 2
errors (`admin.py:54` arg-type and `main.py:80` attr-defined). For the rest:

| Category | How to resolve |
|----------|----------------|
| `name-defined` (missing import) | **Fix** — add the missing import. Never suppress. |
| `return-value` (e.g. `core/metrics/registry.py`) | **Fix** — correct the return type or the returned value. |
| `arg-type` on SQLAlchemy `Column[T]` | Suppress with `# type: ignore[arg-type]` on that line. |
| `assignment` on `Column[T]` impedance | Suppress with `# type: ignore[assignment]` on that line. |
| `attr-defined` | If the attribute is real at runtime, `# type: ignore[attr-defined]`; if it's a typo, fix it. |
| everything else | Read the message; fix if it's a real bug, else per-line `# type: ignore[<code>]`. |

Rule: **fix `name-defined` and `return-value` (they are real bugs); per-line-ignore
the SQLAlchemy `Column[T]` noise.** Never add a blanket file-level ignore.

**DONE WHEN:**
```bash
python -m mypy src/ 2>&1 | tail -1     # "Success: no issues found in 138 source files"
python -m ruff check src/              # All checks passed!
python -m pytest -q 2>&1 | tail -1     # "passed", not "failed"
```
**COMMIT:** `G2: mypy src/ to zero errors`

---

### G3: Give the frontend a working ESLint config

**Root cause (verified 2026-08-04):** a stray `~/eslint.config.js` in the home
directory gets picked up by ESLint's upward config search and forces flat-config
mode — so `--ext` is rejected and any project `.eslintrc.json` is ignored. Also,
`ui/src` is **TypeScript**, so ESLint needs `@typescript-eslint/parser` or it
cannot parse `.tsx` at all. A project-local **flat** config fixes both (nearest
config wins over the home-dir one).

**Step 1 — install the TS parser:**
```bash
cd ui && npm install --save-dev @typescript-eslint/parser@^7
```

**Step 2 — change the lint script** in `ui/package.json` (drop `--ext`, invalid in flat mode):
```json
"lint": "eslint ."
```

**Step 3 — delete the dead `ui/.eslintrc.json`** if present (ignored in flat mode).

**Step 4 — create `ui/eslint.config.js`** (CommonJS; `ui` has no `"type":"module"`):
```js
const js = require("@eslint/js");
const react = require("eslint-plugin-react");
const reactHooks = require("eslint-plugin-react-hooks");
const globals = require("globals");
const tsParser = require("@typescript-eslint/parser");

module.exports = [
  { ignores: ["dist/**", "node_modules/**", "assets/**", "react-browse.html", "**/*.config.{js,cjs,mjs,ts}"] },
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: { ...globals.browser },
    },
    plugins: { react, "react-hooks": reactHooks },
    settings: { react: { version: "detect" } },
    rules: {
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      "no-undef": "off",
      "no-unused-vars": "warn",
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",
      // benign legacy-JS patterns in the hand-written js/index.js bundle
      "no-redeclare": "warn",
      "no-empty": "warn",
      "no-inner-declarations": "warn",
    },
  },
];
```

**DONE WHEN** (must exit 0, only warnings):
```bash
test -f ui/eslint.config.js && echo EXISTS                 # prints: EXISTS
cd ui && npm run lint; echo "exit=$?"                       # exit=0, "N problems (0 errors, ...)"
```
**COMMIT:** `G3: add flat ESLint config + TS parser for frontend`


---

### G4: The npm "high" is dev-only — scope the gate, don't break the build

**Verified 2026-08-04:** the remaining `1 high` is esbuild GHSA-67mh (dev-server
request bypass), pulled in transitively by **vite**. Both are `devDependencies`,
and per the README `ui/src` + `ui/dist/react-browse/` are an **experimental
sub-application, not the production artifact**. So this advisory has **zero
production exposure** — nothing esbuild/vite touch is shipped to Vercel.

**Do NOT force `esbuild >=0.25` under vite@4.** vite@4.5.14 pins `esbuild ^0.18`;
forcing a major esbuild bump is API-incompatible and **breaks `npm run build`**
(confirmed). Fixing a non-shipped dev-server advisory by breaking a working build
is the wrong trade.

**The fix that already holds:** keep the `brace-expansion` override (real,
resolved) and scope the production-readiness gate to what ships.

**DONE WHEN:**
```bash
cd ui && npm audit --omit=dev 2>&1 | tail -1     # "found 0 vulnerabilities"  (production is clean)
cd ui && npm run build 2>&1 | tail -1            # build succeeds in a real env (esbuild postinstall must be allowed)
```
The residual dev-tree `high` is an accepted, documented risk until the vite line
is upgraded (out of scope — experimental sub-app). If you later want it gone from
`npm audit` entirely, upgrade to vite@6+ (esbuild 0.25+) **and re-verify the
build** — do not just pin esbuild.
**COMMIT:** `G4: keep brace-expansion override; document dev-only esbuild advisory`


---

## TRACK G-ops / TRACK O — HUMANS ONLY (a model cannot click dashboards)

### G1: Redeploy the Render API (human)

Production `/v1/health/ready` is 503 because the deployed image predates the
master merge. **A human must:** Render Dashboard → `gcc-car-value-api` →
Manual Deploy → **Deploy latest commit**.

**⚠️ This is the first time `alembic upgrade head` runs on the production Neon DB.**
The chain was verified locally on a fresh DB. If it fails the container won't
boot — have the Neon dashboard open. If unsure, pair with a DBA.

**DONE WHEN:**
```bash
curl -s https://gcc-car-value.onrender.com/v1/health/ready \
  | python -c "import sys,json; print(json.load(sys.stdin).get('status','UNKNOWN'))"
# must print: healthy      (if not, print "NEEDS HUMAN: G1" and stop this task)
```

### O1: Point Vercel production deploys at `master` (human)

Vercel Dashboard → `gcc-car-value` → Settings → Git → Production Branch → `master`.
**DONE WHEN:** the next `git push origin master` auto-deploys with no manual `vercel --prod`.

### O2: Verify the backup workflow end-to-end (human)

1. Confirm GitHub secrets exist: `DATABASE_URL_SYNC`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BACKUP_BUCKET`.
2. `gh workflow run "Weekly DB Backup" --ref master`
3. `gh run list --workflow "Weekly DB Backup" --limit 1` → newest run is `completed / success`.

---

## NOT IN SCOPE (do not attempt)

- Full Arabic content translation
- CSP proper fix (external JS + hashes)
- Redirect SSRF re-validation
- Non-hermetic D2 build
- Production monitoring/alerting (separate ops project)
- DB backup infra beyond verifying the existing workflow (O2)

---

## FINAL AUDIT (run from repo root; every line must match its comment)

```bash
echo "=== F1: drift filter fixed and old bug gone ==="
grep -q "acknowledged.is_(False)" src/api/routes/admin.py && echo "F1 OK" || echo "F1 MISSING"
grep -q "not DriftEvent.acknowledged" src/api/routes/admin.py && echo "F1 REGRESSED" || echo "F1 clean"

echo "=== F2: shutdown_tracing exists and is exported ==="
grep -q "def shutdown_tracing" src/core/tracing/provider.py && echo "F2 OK" || echo "F2 MISSING"
python -c "from src.core.tracing import shutdown_tracing" && echo "F2 export OK"

echo "=== C1 + C2: new tests present and green ==="
python -m pytest tests/pipeline/test_validator.py tests/engine/test_statistical.py -q 2>&1 | tail -1

echo "=== G2: mypy clean ==="
python -m mypy src/ 2>&1 | tail -1

echo "=== ruff still clean (proves F1 used .is_(False), not == False) ==="
python -m ruff check src/ 2>&1 | tail -1

echo "=== G3: eslint config present ==="
test -f ui/.eslintrc.json && echo "G3 OK" || echo "G3 MISSING"

echo "=== G4: npm audit clean ==="
cd ui && npm audit --audit-level=high 2>&1 | grep -E "found 0|0 high" || echo "G4 vulns remain"; cd ..

echo "=== G1: production health (human task) ==="
curl -s https://gcc-car-value.onrender.com/v1/health/ready | python -c "import sys,json; print(json.load(sys.stdin).get('status','UNKNOWN'))" 2>&1

echo "=== Full suite ==="
python -m pytest -q 2>&1 | tail -1     # expect: 344 passed, 0 failed
```
