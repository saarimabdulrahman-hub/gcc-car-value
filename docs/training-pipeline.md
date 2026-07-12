# GCC Car Value — ML Training Pipeline & Experiment Tracking

**Date:** 2026-07-12  
**Package:** `ml/training/`

## Architecture

```
Feature Store → TrainingPipeline.run()
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
Experiment      Train/Test      CrossValidator
Tracker         Split           (kfold, stratified, time-series)
    │               │
    ▼               ▼
Hyperparameter  Model Training
Tracker         (via train_fn)
    │               │
    ▼               ▼
Artifact        ModelEvaluator
Manager         (MAE, RMSE, MAPE, R², median AE)
    │               │
    ▼               ▼
Model           Experiment
Registry        Complete
(promote/rollback/archive)
```

## Usage

```python
from ml.training import TrainingPipeline

pipeline = TrainingPipeline()

def train_fn(X, y, hp):
    model = LightGBMRegressor(**hp).fit(X, y)
    return model

def predict_fn(model, X):
    return model.predict(X)

exp = pipeline.run(
    data=feature_rows,
    model_train_fn=train_fn,
    model_predict_fn=predict_fn,
    model_name="lightgbm_v2",
    hyperparameters={"n_estimators": 200, "max_depth": 7},
    target_column="price",
)

# exp.status → "completed"
# exp.metrics → {"mae": 4500.0, "r2": 0.85, ...}
```

## Model Registry

```python
# Register
pipeline.registry.register("lightgbm_v2", metrics={"mae": 4500})

# Promote to active
pipeline.registry.promote("lightgbm_v2")

# Rollback
pipeline.registry.rollback("lightgbm_v2", reason="worse performance")

# List
pipeline.registry.list_models()  # ["lightgbm_v1", "lightgbm_v2"]
```

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| MAE | Mean Absolute Error |
| RMSE | Root Mean Squared Error |
| MAPE | Mean Absolute Percentage Error |
| R² | Coefficient of determination |
| Median AE | Median Absolute Error |
| Residual Stats | min, max, P10, P90 |

## Verified

- Experiment lifecycle: create → running → completed/failed
- Model registry: register → promote → rollback → archive
- Evaluation: MAE, RMSE, MAPE, R², median AE
- Cross-validation: deterministic train/test split (seed=42), K-fold, time-series
- Full pipeline: mock model trained and evaluated on synthetic data
- Deterministic splits verified (same seed = same split)
- Artifact saving with pickle fallback for non-pickleable models

---

*Training pipeline documented 2026-07-12.*
