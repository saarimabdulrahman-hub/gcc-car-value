# GCC Car Value — Online Inference Pipeline & Prediction Audit

**Date:** 2026-07-12  
**Package:** `ml/inference/`

## Architecture

```
API Request
    │
    ▼
InferencePipeline.predict(model_name, features)
    │
    ├── 1. Validate (required fields, ranges, categorical)
    ├── 2. FeatureSnapshot (immutable, checksummed)
    ├── 3. ModelServer.predict() → PredictionResult
    ├── 4. AuditRecord (immutable, prediction_id + all metadata)
    ├── 5. LineageTracker (dataset → snapshot → model → experiment → feedback)
    └── 6. Return complete response with prediction_id
    │
    ▼ (future)
FeedbackCollector.attach(prediction_id, actual_selling_price=...)
```

## Usage

```python
from ml.inference import InferencePipeline

pipeline = InferencePipeline(server)
result = pipeline.predict("valuation", {
    "make": "Toyota", "model": "Land Cruiser",
    "year": 2018, "mileage_km": 120000,
})

# → {
#     "prediction_id": "abc123...",
#     "prediction": 125000.0,
#     "confidence": 0.85,
#     "model_version": "valuation:v3",
#     "latency_ms": 2.3,
#     "fallback_used": False,
#     ...
# }

# Later: attach feedback
pipeline.attach_feedback("abc123...", actual_price=122000.0)
```

## Immutability

| Object | Mutability | Checksummed |
|--------|-----------|-------------|
| `FeatureSnapshot` | Frozen dataclass | SHA-256 of JSON features |
| `AuditRecord` | Frozen dataclass | Request hash |
| `PredictionFeedback` | Mutable (collected later) | No |

## Lineage Chain

```
Dataset v3 → FeatureSnapshot snap-abc → Model lightgbm:v2
    → Experiment exp-1 → Deployment dep-xyz → Prediction p-1
    → Feedback fb-1 (actual selling price attached later)
```

## Verified

- Validator: required fields, range checks, categorical validation
- FeatureSnapshot: immutable, deterministic checksum
- AuditStore: save, get, list by model, recent queries
- FeedbackCollector: attach, retrieve, pending list
- LineageTracker: record, get, update feedback link
- 698 tests passing with no regression

---

*Inference pipeline documented 2026-07-12.*
