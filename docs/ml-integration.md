# GCC Car Value — ML Model Integration

**Date:** 2026-07-12  
**Blueprint Reference:** §6 (Valuation Engine)  
**Files:** `src/ml/`, `src/api/routes/valuation.py`, `src/engine/trainer.py`

---

## 1. Architecture

```
POST /v1/valuate
    │
    ├── 1. Check cache → return cached if hit
    ├── 2. Statistical valuation (always runs — baseline)
    │       ├── Comp finder → percentile bands → adjustments
    │       └── Confidence scoring
    │
    ├── 3. ML prediction (optional — graceful fallback)
    │       ├── ModelLoader queries model_registry for latest active model
    │       ├── PredictionService builds feature vector
    │       ├── LightGBM model.predict() → ML estimate
    │       ├── Cross-reference: if ML disagrees >15% → flag, use statistical
    │       └── If ML agrees → ensemble (average of statistical + ML)
    │
    ├── 4. If ML unavailable/missing/errors → prediction_source="statistical"
    │
    └── 5. Return ValuationResponse with prediction_source and model_version
```

## 2. Components

### 2.1 Model Persistence (`src/ml/model_persistence.py`)

Models are saved to and loaded from `src/ml/models/{model_name}.pkl`.

| Function | Purpose |
|----------|---------|
| `save_model(model, name)` | Pickle model to disk, return path |
| `load_model(name)` | Load model from disk, return None if missing |
| `model_exists(name)` | Check if model file exists |
| `list_saved_models()` | List all saved model names |

The `src/ml/models/` directory is auto-created with a `.gitignore` to prevent accidental commits of large pickle files.

### 2.2 Model Loader (`src/ml/model_loader.py`)

Singleton-style lazy loader. Queries `model_registry` for the latest `status='active'` model.

```
ModelLoader(session)
    ├── get_model() → (model_object, metadata_dict) | (None, None)
    ├── reload()   → force re-check for new active model
    └── is_available() → bool check without loading
```

**Loading flow:**
1. Query `model_registry WHERE status='active' ORDER BY activated_at DESC LIMIT 1`
2. If no active model → return `(None, None)`
3. If cached model matches active model_name → return cached
4. Otherwise: try loading from `model_path` (registry field), then from models directory
5. On load failure → return `(None, None)`
6. Cache successfully loaded model in memory

**Reload trigger:** Call `reload()` after a model activation to pick up the new model without restarting.

### 2.3 Prediction Service (`src/ml/prediction_service.py`)

Translates valuation query parameters into a feature vector and calls `model.predict()`.

```python
svc = PredictionService(model, metadata)
result: PredictionResult = svc.predict(make, model, year, mileage_km, ...)
```

**Feature vector (15 features):**
| Feature | Source | Default |
|---------|--------|---------|
| `mileage_km` | Query param | 0 |
| `vehicle_age_years` | `current_year - year` | — |
| `is_gcc_spec` | spec == "GCC" | 0.0 |
| `is_us_spec` | spec == "US" | 0.0 |
| `is_dealer` | seller_type | 0.0 |
| `has_warranty` | warranty flag | 0.0 |
| `has_service_history` | service_history flag | 0.0 |
| `segment_median_price` | Market context | 0 |
| `segment_liquidity_days` | Market context | 30 |
| `price_volatility` | Market context | 0.05 |
| `market_trend_4w` | Market context | 0.0 |
| `listing_volume` | Market context (comp_count) | 0 |
| `brand_reliability` | Market context | 3.0 |
| `depreciation_rate` | Market context | 0.12 |
| `common_issue_count` | Market context | 0 |

**Confidence score:** Derived from the model's training MAE ratio:
- `cv < 0.10` → confidence 0.90
- `cv < 0.20` → confidence 0.75
- `cv < 0.30` → confidence 0.60
- `cv ≥ 0.30` → confidence 0.40

## 3. Valuation Integration

### 3.1 API Response (new fields)

```json
{
  "estimate": 125000,
  "price_low": 112000,
  "price_high": 145000,
  "confidence": "high",
  "prediction_source": "ensemble",
  "model_version": "lightgbm_v20260712_1400",
  "fallback_used": false
}
```

| Field | Values | Meaning |
|-------|--------|---------|
| `prediction_source` | `"statistical"` | Only statistical engine was used |
| | `"ml"` | Only ML model was used |
| | `"ensemble"` | Statistical + ML averaged together |
| `model_version` | `string` or `null` | Active model name from model_registry |
| `fallback_used` | `bool` | True if ML was attempted but fell back to statistical |

### 3.2 Fallback Triggers

The system falls back to statistical-only when:

| Condition | Behavior |
|-----------|----------|
| No `status='active'` model in registry | `prediction_source="statistical"`, no error |
| Model file missing or corrupted | `prediction_source="statistical"`, log warning |
| Prediction raises an exception | `fallback_used=true`, log warning, return statistical result |
| ML estimate disagrees >15% with statistical | `fallback_used=true`, log warning, use statistical |
| Statistical confidence is "insufficient" | Skip ML entirely (no comps → no baseline) |

**No request ever returns HTTP 500 due to ML unavailability.**

### 3.3 Logging

```python
# Model loaded
logger.info("active_model_loaded", model_name=..., mae=..., feature_version=...)

# Model unavailable
logger.info("ml_model_unavailable", reason="no_active_model")

# Prediction failed
logger.warning("ml_prediction_failed", error=..., make=..., model=...)

# ML vs statistical disagreement
logger.warning("ml_statistical_disagreement",
    statistical_estimate=..., ml_estimate=..., pct_diff=...)

# Valuation computed (includes ML metadata)
logger.info("valuation_computed",
    prediction_source=..., ml_model_version=..., fallback_used=...)
```

## 4. Model Lifecycle

### 4.1 Training → Production Flow

```
1. train_and_register(session)     # Trains model, saves to src/ml/models/,
                                   #   creates ModelRegistry row with status="training"

2. Evaluate model metrics (MAE, MAPE, R²)

3. Promote to shadow:
   UPDATE model_registry SET status='shadow',
   shadow_started_at=NOW() WHERE model_name='...';

4. After shadow period (1+ week), compare shadow vs active metrics

5. Promote to active:
   UPDATE model_registry SET status='active',
   approved_at=NOW(), approved_by='engineer_name',
   activated_at=NOW() WHERE model_name='...';
```

### 4.2 Activation SQL Example

```sql
-- Deactivate current active model
UPDATE model_registry
SET status = 'rolled_back', rolled_back_at = NOW()
WHERE status = 'active';

-- Activate new model
UPDATE model_registry
SET status = 'active',
    approved_at = NOW(),
    approved_by = 'platform-engineer',
    activated_at = NOW()
WHERE model_name = 'lightgbm_v20260712_1400';
```

### 4.3 Reload After Activation

After activating a new model, the running API picks it up on the next valuation request (lazy load). To force immediate reload:

```python
from src.ml.model_loader import ModelLoader
loader = ModelLoader(session)
await loader.reload()
```

## 5. Deployment Considerations

- **Model directory:** `src/ml/models/` must be writable by the training process and readable by the API process
- **Docker:** Include `src/ml/models/` in the Docker image or mount as a volume
- **Multiple instances:** Each API instance loads the model independently. After activation, instances pick up the new model on their next valuation request
- **Memory:** LightGBM models are typically 100KB-2MB — negligible memory impact
- **Cold start:** First valuation request after deployment triggers model load (typically <100ms for LightGBM)
- **Pickle security:** Models are loaded from a controlled local directory, never from user input or external sources

## 6. Testing

```bash
# ML unit tests
pytest tests/ml/ -v

# Full suite
pytest tests/ -v
```

Test coverage:
- `tests/ml/test_model_persistence.py` — save, load, missing model, list models
- `tests/ml/test_prediction_service.py` — prediction with full/missing params, market context, confidence scoring

---

*ML integration documented 2026-07-12.*
