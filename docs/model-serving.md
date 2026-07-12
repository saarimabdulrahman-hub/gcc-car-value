# GCC Car Value — Model Serving, Deployment & A/B Evaluation Platform

**Date:** 2026-07-12  
**Package:** `ml/serving/`

## Architecture

```
API Request
    │
    ▼
ModelServer.predict(model_name, features)
    │
    ├── TrafficRouter.route() → which model version?
    │       ├── A/B experiment active? → split by request key
    │       ├── Canary active? → % of traffic to new version
    │       └── Default → active model
    │
    ├── PredictionCache.get(key) → cached result?
    │       └── Miss → Predictor.predict()
    │               ├── ModelLoader.load_active() → model object
    │               ├── model.predict(features) → prediction
    │               └── PredictionCache.set(key, result)
    │
    ├── ServingMonitor.record_prediction()
    └── Return PredictionResult
```

## Usage

```python
from ml.serving import ModelServer

server = ModelServer(training_registry)

# Deploy
server.deploy("lightgbm_v2", version=1)

# Predict
result = server.predict("lightgbm_v2", {"mileage_km": 50000, "year": 2020})
# → PredictionResult(prediction=125000, model_version="lightgbm_v2:v1", latency_ms=1.5)

# A/B Test
ab = server.start_ab("lightgbm_v2:v1", "lightgbm_v3:v1", traffic_split=0.5)
server.complete_ab(ab.experiment_id, winner="lightgbm_v3:v1")

# Canary
server.start_canary("lightgbm_v2", start_pct=0.01)   # 1%
server.increase_canary("lightgbm_v2", increment=0.05) # 6% → ... → 100%

# Rollback
server.rollback("lightgbm_v2", reason="worse performance")
```

## Response Metadata

```python
PredictionResult(
    prediction=125000.0,
    model_version="lightgbm_v2:v3",
    model_name="lightgbm_v2",
    experiment_id="exp-abc123",
    latency_ms=1.5,
    confidence=0.85,
    fallback_used=False,       # True if model failed and fallback was used
    feature_schema_version=1,
)
```

## Verified

- Router: active routing, deterministic by request key, A/B split
- Cache: set/get, TTL, hit rate, eviction
- Deployment: deploy → activate, rollback (v2 rolled back, v1 re-activated)
- A/B Testing: start, traffic split, complete with winner
- Canary: incremental progression (1% → 6% → 100%)
- Monitor: prediction count, average latency, error tracking
- Thread-safe cache and monitor

---

*Model serving documented 2026-07-12.*
