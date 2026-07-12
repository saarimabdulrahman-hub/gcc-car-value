# GCC Car Value Platform — Machine Learning Audit

**Date:** 2026-07-12  
**Blueprint Reference:** §6 (Valuation Engine), §7 (MLOps), §8 (Feature Engineering)  
**Files Audited:** `engine/`, `models/model_registry.py`, `pipeline/`, `api/routes/valuation.py`

---

## 1. Architecture Overview

### Two-Model Design (Blueprint §6.1)

```
POST /v1/valuate
    │
    ├── 1. Statistical Model (always runs) ← CURRENTLY ACTIVE
    │       ├── Comp finder (tiered hard filters)
    │       ├── Percentile bands (P10, P25, P50, P75, P90)
    │       ├── Adjustments (mileage, spec, city)
    │       └── Confidence scoring + Bootstrap CI
    │
    └── 2. ML Model (if active AND confidence threshold met) ← NEVER RUNS
            ├── Feature vector from query + market context
            ├── LightGBM predict
            ├── Cross-reference with statistical
            └── SHAP feature contributions
```

**Actual state:** Only the statistical path runs. The ML path is fully coded but disconnected.

---

## 2. Statistical Valuation Engine

### 2.1 Implementation (`engine/statistical.py`)

**Status:** ✅ Complete, tested, wired to API

**Algorithm:**
1. Find comps via `comp_finder.find_comps()` — returns ranked comparable listings
2. Reject if < 5 comps → `confidence: "insufficient"` → HTTP 422
3. Compute P10, P25, P50, P75, P90 from comp prices
4. Adjust P50 estimate:
   - **Mileage:** 0.25 AED/km × (comp_median_km − query_km)
   - **Spec:** 50% of GCC/non-GCC median price premium
   - **City:** 30% of same-city/different-city median price delta
5. Score confidence: HIGH (≥30 comps, CV<0.15), MEDIUM (≥10, CV<0.30), LOW (≥5), INSUFFICIENT (<5)
6. Bootstrap 80% CI (1000 iterations, seed=42)
7. Return top 10 comps with platform attribution (no URLs exposed)

### 2.2 Hardcoded Constants

| Constant | Value | Location | Calibrated? |
|----------|-------|----------|-------------|
| Depreciation per km | 0.25 AED/km | `statistical.py:72` | ❌ Not market-calibrated |
| Spec premium weight | 0.5 (50%) | `statistical.py:90-99` | ❌ Not market-calibrated |
| City premium weight | 0.3 (30%) | `statistical.py:108-111` | ❌ Not market-calibrated |
| Bootstrap seed | 42 | `statistical.py:168` | N/A |
| Bootstrap iterations | 1000 | `statistical.py:166` | N/A |

**Risk:** These coefficients materially impact valuations. A Land Cruiser with 50,000 extra km gets a −12,500 AED adjustment. These should be derived from market data, not hardcoded.

### 2.3 Comp Finder (`engine/comp_finder.py`)

**Status:** ✅ Complete, tested

**3-tier filter cascade:**

| Tier | Year ± | Mileage ± | Spec | Country | Min comps |
|------|--------|-----------|------|---------|-----------|
| 1 | 2 years | 30% | Same | Same | — |
| 2 | 3 years | 50% | Any | Same | — |
| 3 | 4 years | 75% | Any | Any | — |

Exits when ≥15 comps found. Caps at 50.

**Weighted scoring factors:**

| Factor | Weight | Range |
|--------|--------|-------|
| Recency (days) | −0 to −30 | ≤7d: 0, 8-30d: −5, 31-90d: −15, >90d: −30 |
| Mileage delta (%) | −25 max | `abs(mileage_diff) / query_mileage × 25` |
| Year delta | −8/yr | Per year difference |
| Spec match | 0 to −15 | Same: 0, GCC ref: −5, different: −15 |
| Country match | 0 to −10 | Same country: 0, different: −10 |
| Quality bonus | +0 to +10 | `quality_score / 100 × 10` |
| Sold comp bonus | +5 | Status is sold_confirmed or probably_sold |
| High delisting confidence | +3 | `delisting_confidence > 0.8` |

---

## 3. LightGBM Training Pipeline

### 3.1 Implementation (`engine/trainer.py`)

**Status:** ✅ Code complete, ❌ Never invoked by any scheduler or API

**Training pipeline:**
1. `build_training_dataset()` — queries ≥1000 quality listings (max 50K), builds DataFrame
2. `_construct_target()` — estimates transaction price from asking price
3. `train_model()` — 85/15 train/holdout split, LightGBM regressor
4. `train_and_register()` — orchestrates full pipeline, saves to `model_registry`

### 3.2 Target Construction

```python
target = asking_price_aed
if status in ("sold_confirmed", "probably_sold"):
    target *= 0.95          # 5% discount for sold listings
if delisting_confidence > 0.8:
    target *= 0.93          # additional 7% for high-confidence delisting
```

**Assessment:** Reasonable approximation. Sold listings typically transact below asking. The multiplicative stacking means a sold_confirmed listing with high delisting confidence gets `asking × 0.95 × 0.93 = asking × 0.8835` — roughly a 12% discount from ask. This is a defensible heuristic for GCC car markets.

### 3.3 LightGBM Hyperparameters

```python
LGBMRegressor(
    n_estimators=200,
    max_depth=7,
    learning_rate=0.05,
    num_leaves=31,
    min_child_samples=30,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbose=-1,
)
```

**Assessment:** Conservative defaults — appropriate for tabular pricing data with ~1K-50K rows. The fixed seed (42) ensures reproducibility.

### 3.4 Training Data

| Parameter | Value | Note |
|-----------|-------|------|
| Source table | `listings` | `quality_score >= 60` |
| Status filter | active, probably_sold, sold_confirmed | Excludes expired/delisted |
| Min rows | 1,000 | Returns None if insufficient |
| Max rows | 50,000 | Hard cap |
| Features | 15 (from FeatureRegistry) | 7 listing + 5 market + 3 vehicle |
| Feature handling | `fillna(0)` | All NaN → 0 before training |

### 3.5 ⚠️ Critical: Model Not Persisted

```python
with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
    pickle.dump(model, f)
    model_path = f.name
```

The trained model is saved to a **temporary file** via `tempfile.NamedTemporaryFile`. The `model_path` stored in `model_registry` points to a file that:
- Will be deleted on next system reboot
- May be cleaned by OS temp file cleanup
- Is not uploaded to S3 or MLflow
- Is not reloadable after the training process exits

**The model is effectively discarded immediately after training.**

### 3.6 Disconnected from API

`train_and_register()` is **never called** by:
- Any API route
- Any APScheduler job
- Any CLI command
- Any Docker entrypoint

The `src/api/` directory has zero references to LightGBM, `trainer.py`, `FeatureRegistry`, or `MarketContext`. The API exclusively uses `engine.statistical.valuate()`.

---

## 4. Feature Engineering

### 4.1 Architecture (`engine/features/`)

| File | Features | Count |
|------|----------|-------|
| `base.py` | `BaseFeature` ABC, `FeatureRegistry`, `MarketContext` | — |
| `listing_features.py` | MileageFeature, VehicleAgeFeature, SpecGCCFeature, SpecUSFeature, SellerDealerFeature, HasWarrantyFeature, HasServiceHistoryFeature | 7 |
| `market_features.py` | SegmentMedianPrice, SegmentLiquidity, PriceVolatilityFeature, MarketTrend4WeekFeature, ListingVolumeFeature | 5 |
| `vehicle_features.py` | BrandReliabilityFeature, DepreciationRateFeature, CommonIssueCountFeature | 3 |

**Total: 15 features** registered via `FeatureRegistry.register()` at import time.

### 4.2 Feature Design Assessment

**Strengths:**
- Modular: each feature is a ~10-line class with single responsibility
- Versioned: each feature has `version = "1.0.0"`
- Dependency graph: topological sort via `FeatureRegistry.ordered()`
- Dual interface: `compute()` for batch training, `compute_single()` for inference

**Weaknesses:**

| Issue | Detail |
|-------|--------|
| **Market features are identity** | All 5 market features return the same value for every row: `pd.Series([val] * len(df))`. They're segment-level constants, not per-listing features. |
| **Vehicle features are identity** | `BrandReliabilityFeature`, `DepreciationRateFeature`, `CommonIssueCountFeature` also return scalar constants replicated across rows. |
| **Only 7 features vary per-row** | Just the listing features (mileage, age, spec flags, seller, warranty, service) are truly per-listing. |
| **`compute_single()` never called** | The API doesn't use features for inference — it uses the statistical model. Every `compute_single()` method is dead code. |
| **MarketContext never populated for inference** | `MarketContext` is only constructed inside `build_training_dataset()`. For individual valuations, no market context is built — the statistical model queries comps directly. |
| **Warranty/Service always NaN** | `HasWarrantyFeature` and `HasServiceHistoryFeature` use `df["warranty"].fillna(False)` — these columns are never populated by any scraper, so these features are always 0.0. |

### 4.3 Feature Dependencies

Only one feature declares dependencies:
```
SegmentLiquidity → depends on → SegmentMedianPrice
```

All other features have no dependencies. The topological sort ensures `SegmentMedianPrice` is resolved before `SegmentLiquidity`.

---

## 5. Model Registry

### 5.1 Schema (`models/model_registry.py`)

The `model_registry` table implements the full blueprint MLOps lifecycle:

```
training → evaluating → shadow → approved → active
                ↓            ↓          ↓
             archived    rolled_back  archived
```

| Lifecycle Field | Type | Purpose |
|-----------------|------|---------|
| `status` | TEXT | Current state (default: "training") |
| `shadow_started_at` | TIMESTAMPTZ | When shadow deployment began |
| `approved_at` | TIMESTAMPTZ | When human approved |
| `approved_by` | TEXT | Who approved |
| `activated_at` | TIMESTAMPTZ | When became production |
| `rolled_back_at` | TIMESTAMPTZ | When rolled back |
| `rollback_reason` | TEXT | Why rolled back |
| `shadow_query_count` | INTEGER | Queries in shadow mode |
| `shadow_mae` | FLOAT | Shadow model performance |
| `shadow_vs_active_pct` | FLOAT | Improvement vs active |

**⚠️ None of these lifecycle transitions are implemented.** The `train_and_register()` function sets `status="training"` and never advances it. There is no:
- Shadow deployment orchestrator
- Human approval UI or CLI
- Model activation logic
- Rollback mechanism
- Performance comparison between active and shadow models

### 5.2 Training Metrics Stored

| Metric | Stored | Computed |
|--------|--------|----------|
| `mae` | ✅ | Mean absolute error on holdout |
| `mape` | ✅ | Mean absolute % error on holdout |
| `r2_score` | ✅ | Correlation coefficient squared |
| `training_rows` | ✅ | Count |
| `holdout_rows` | ✅ | 15% of dataset |
| `training_dataset_hash` | ✅ | SHA-256 of 1000-row sample |
| `feature_version` | ✅ | Hardcoded `"1.0.0"` |
| `hyperparameters` | ✅ | Dict of LightGBM params |
| `features_used` | ✅ | List of 15 feature names |

---

## 6. MLflow

### 6.1 Setup

| Component | Status |
|-----------|--------|
| Docker Compose service | ✅ `mlflow` on port 5000 |
| Image | `python:3.12-slim` (installs mlflow via pip at startup) |
| Backend store | Local filesystem (`/mlflow` volume) |
| Artifact store | Same local volume |
| SDK integration | ❌ No `mlflow` imports anywhere in `src/` |
| Experiment tracking | ❌ No experiments logged |
| Model registry sync | ❌ `model_registry` table not connected to MLflow |

### 6.2 Assessment

MLflow is **running but completely unused.** The `trainer.py` module manually tracks metrics in the `model_registry` PostgreSQL table rather than using MLflow's tracking API. No `mlflow.log_metric()`, `mlflow.log_params()`, or `mlflow.log_model()` calls exist.

---

## 7. SHAP Explainability

### 7.1 Status: NOT IMPLEMENTED

| Component | Status |
|-----------|--------|
| `shap` package | ❌ Not in `pyproject.toml` dependencies |
| `ValuationQuery.shap_values` column | ✅ Exists (JSONB, nullable), never populated |
| `ValuationQuery.feature_importance` column | ✅ Exists (JSONB, nullable), never populated |
| SHAP computation during inference | ❌ Not implemented |
| SHAP in API response | ❌ Blueprint §6.1 step 6 specifies "SHAP values for top 5 features" — not in response |

---

## 8. Inference Path (What Actually Runs)

```
POST /v1/valuate
    │
    ├── 1. Compute cache_key = SHA256(inputs + today)
    ├── 2. Check valuation_queries for cache hit → return cached
    ├── 3. Call engine.statistical.valuate()
    │       ├── find_comps() — SQL query on listings table
    │       ├── numpy percentile computation
    │       ├── 3 hardcoded adjustments (mileage, spec, city)
    │       ├── Confidence scoring
    │       └── Bootstrap CI
    ├── 4. If insufficient → 422
    ├── 5. Compute deal_indicator (if asking_price provided)
    ├── 6. Store in valuation_queries (model_version="statistical_v1", model_type="statistical")
    └── 7. Return ValuationResponse
```

**ML model is never invoked.** The API hardcodes `model_type="statistical"` and `model_version="statistical_v1"` in the cache row.

---

## 9. Drift Detection

### 9.1 Implementation (`engine/drift.py`)

**Status:** ✅ Code complete, ❌ Never scheduled

| Drift Type | Metric | Threshold | Function |
|------------|--------|-----------|----------|
| Feature | PSI | > 0.2 (warn), > 0.3 (alert) | `check_feature_drift()` |
| Target | Median price % change | > 15% | `check_target_drift()` |
| Prediction | MAE degradation % | > 30% | `check_prediction_drift()` |
| Market | Volume drop / volatility ratio | > 40% / > 2× | `check_market_drift()` |

**PSI implementation:** Uses 10-bin histograms with 0.0001 epsilon to avoid division by zero.

**⚠️ Never called.** There is no APScheduler job, no cron, and no API endpoint that triggers drift detection.

---

## 10. LLM Explainer

### 10.1 Implementation (`engine/llm_explainer.py`)

**Status:** ✅ Complete, callable but not wired to valuation response

- Template-based: always works, returns 3-4 sentence explanation
- Claude API: attempted if `CLAUDE_API_KEY` env var is set
- **⚠️ Invalid model string:** Uses `"claude-sonnet-4-6"` which is not a valid Anthropic model ID
- Falls back to template on any API error

The LLM explainer is called in `test_phase4.py` tests but **never invoked during actual valuation responses.**

---

## 11. Test Coverage

### 11.1 Existing Tests

| Test File | What It Covers | Tests |
|-----------|---------------|-------|
| `tests/engine/test_statistical.py` | Confidence scoring, bootstrap CI | 5 |
| `tests/engine/test_comp_finder.py` | Platform names, scoring, sold bonus | 4 |
| `tests/test_phase4.py` | LLM explainer template output | 2 |

### 11.2 Missing Tests

| Component | Tests |
|-----------|-------|
| `trainer.py` — `build_training_dataset()` | 0 |
| `trainer.py` — `_construct_target()` | 0 |
| `trainer.py` — `train_model()` | 0 |
| `trainer.py` — `train_and_register()` | 0 |
| `engine/drift.py` — all 4 drift checkers + PSI | 0 |
| `engine/features/` — all 15 features | 0 |
| `engine/llm_explainer.py` — Claude API integration | 0 (template only tested) |
| `engine/statistical.py` — `valuate()` integration | 0 (tested indirectly via `test_integration.py`) |
| SHAP explainability | 0 |
| Model registry lifecycle transitions | 0 |

---

## 12. Recommendations Engine (`engine/recommendations.py`)

**Status:** ✅ Complete, not wired to any API endpoint

- Content-based: filters by budget, body type, family size
- Scores by: budget fit (0-3 points), listing volume (0-2 points), model ratings from knowledge base
- Returns top-N `Recommendation` objects
- No API endpoint exposes this (could be `GET /v1/recommendations`)

---

## 13. VIN Decoder (`engine/vin_decoder.py`)

**Status:** ✅ Complete, not wired to any API endpoint

- ISO 3779 validation (17 chars, no I/O/Q)
- WMI lookup: 27 GCC-common manufacturers
- VIN year decoding: 2010–2030
- Returns `needs_api_for_full_decode: True` — no commercial API integration

---

## 14. Summary Matrix

| Component | Code | Tested | Wired to API | Scheduled | Production Ready |
|-----------|------|--------|-------------|-----------|-----------------|
| Statistical engine | ✅ | ✅ | ✅ | — (per-request) | ✅ |
| Comp finder | ✅ | ✅ | ✅ | — | ✅ |
| LightGBM trainer | ✅ | ❌ | ❌ | ❌ | ❌ |
| Feature engineering | ✅ | ❌ | ❌ | ❌ | ❌ |
| Model registry | ✅ | ❌ | ❌ | ❌ | ❌ (table only) |
| MLflow | ✅ (container) | ❌ | ❌ | ❌ | ❌ (unused) |
| SHAP explainability | ❌ | ❌ | ❌ | ❌ | ❌ |
| Drift detection | ✅ | ❌ | ❌ | ❌ | ❌ |
| LLM explainer | ✅ | ⚠️ Partial | ❌ | ❌ | ❌ |
| Recommendations | ✅ | ❌ | ❌ | ❌ | ❌ |
| VIN decoder | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 15. Key Weaknesses

### 🔴 Critical
1. **ML model never used in production** — The API uses only the statistical engine. The entire LightGBM pipeline is dead code at runtime.
2. **Model not persisted** — `pickle.dump()` to a temp file that gets cleaned up. If training ever ran, the model would be lost.
3. **No model activation workflow** — `model_registry` has the full lifecycle schema but zero code to advance status from training → shadow → active.
4. **No scheduler for training** — `train_and_register()` is never called by any cron, APScheduler, or CLI.

### 🟡 High
5. **Hardcoded adjustment coefficients** — 0.25 AED/km, 50% spec weight, 30% city weight are not calibrated from market data.
6. **MarketContext never populated for inference** — The 15 features are registered but `compute_single()` is never called during `/v1/valuate`.
7. **Invalid Claude model string** — `"claude-sonnet-4-6"` is not a valid Anthropic model ID.
8. **Drift detection never runs** — Logic exists but no trigger.
9. **7 of 15 features are scalar constants** — The market + vehicle features return the same value for every row, adding no discriminative power.
10. **Warranty/Service features always zero** — No scraper populates these columns.

### 🟢 Medium
11. **MLflow unused** — Running in Docker but no experiments tracked.
12. **SHAP not installed** — Not in dependencies, no computation code.
13. **No model evaluation comparison** — No code compares active vs shadow model performance.
14. **No backtesting framework** — Can't evaluate how the model would have performed historically.
15. **LLM explainer disconnected** — Not called during valuation responses.

---

## 16. Future Improvements

### Short-Term
1. **Wire drift detection to a weekly APScheduler job** — 30-minute effort, immediate value
2. **Fix Claude model string** — Change to valid Anthropic model ID
3. **Calibrate adjustment coefficients** — Run regression on historical delisting data to derive mileage depreciation per segment
4. **Wire LLM explainer into valuation response** — Add `explanation` field to `ValuationResponse`

### Medium-Term
5. **Schedule weekly training** — APScheduler job: build dataset → train → register → compare with active
6. **Implement shadow deployment** — Load active + shadow models, predict with both, log comparison
7. **Integrate MLflow tracking** — Replace manual `model_registry` logging with `mlflow.log_*()` calls
8. **Persist models to S3** — Upload pickle to S3, store S3 key in `model_path`
9. **Populate MarketContext for inference** — Build context from DB for each valuation query, enabling feature-based ML prediction
10. **Install and integrate SHAP** — Compute SHAP values after ML prediction, store in `valuation_queries`

### Long-Term
11. **A/B test statistical vs LightGBM** — Serve statistical to control group, ML to treatment, compare user satisfaction
12. **Automated hyperparameter tuning** — Optuna or similar for LightGBM hyperparameters
13. **Ensemble model** — Weighted average of statistical + LightGBM predictions
14. **Online learning** — Update model incrementally as new listings arrive rather than weekly batch
15. **Segment-specific models** — Train per-segment models (SUV vs sedan, GCC vs non-GCC, luxury vs economy)

---

*ML audit completed 2026-07-12. No production code modified.*
