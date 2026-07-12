# GCC Car Value — ML Monitoring Platform

**Date:** 2026-07-12  
**Package:** `ml/monitoring/`

## Architecture

```
Inference Pipeline → Audit Records + Feedback
                            │
                            ▼
                    MonitoringEngine.run()
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
  DataDriftDetector   ModelDriftDetector   PerformanceMonitor
  (PSI, mean shift)   (MAE/MAPE trend)     (latency, failures)
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                      AlertEngine
                            │
                            ▼
                    RetrainingSignals
                            │
                            ▼
                      MonitoringReport
```

## Usage

```python
from ml.monitoring import MonitoringEngine

engine = MonitoringEngine()

# Set baselines from training
engine.set_baseline("price", training_prices)
engine.set_baseline_mae("valuation", 4500.0)

# Record observations from production
engine.record_feature("price", 125000)
engine.add_feedback("valuation", predicted=120000, actual=118000)
engine.record_performance("valuation", 45.0)

# Run monitoring
report = engine.run("valuation")

if report.retraining_recommended:
    print(f"Retrain: {report.retraining_reason}")

for alert in report.alerts:
    print(f"[{alert.level}] {alert.title}: {alert.message}")
```

## Drift Detection

| Type | Metric | Threshold | Action |
|------|--------|-----------|--------|
| Feature Drift | Mean shift > 10% | WARNING | Monitor |
| Feature Drift | Mean shift > 20% | CRITICAL | Alert |
| Feature Drift | Range outside 0.5-2x | DATA_QUALITY | Alert |
| Model Drift | MAE degradation > 30% | MODEL_DEGRADED | Alert + Retrain Rec |
| Model Drift | MAPE degradation > 30% | WARNING | Alert |

## PSI (Population Stability Index)

```
PSI = Σ (actual% - expected%) × ln(actual% / expected%)
PSI < 0.1: No significant drift
PSI 0.1-0.2: Moderate drift
PSI > 0.2: Significant drift
```

## Verified

- PSI: identical distributions = 0, different = positive
- Mean shift: +50% triggers CRITICAL, +2% triggers nothing
- Model drift: 20K error vs 5K baseline triggers MODEL_DEGRADED
- Alerts: INFO/WARNING/CRITICAL levels, drift-to-alert conversion
- Retraining: recommended with 3+ drift events, not recommended without
- Performance: latency stats, total requests
- Full monitoring run produces a complete report

---

*Monitoring platform documented 2026-07-12.*
