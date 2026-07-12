# GCC Car Value — ML Lifecycle Orchestrator

**Date:** 2026-07-12  
**Package:** `ml/lifecycle/`

## Complete Workflow

```
Monitoring detects drift
    │
    ▼
LifecycleOrchestrator.start("valuation", trigger=DRIFT_ALERT)
    │
    ├── QUEUED → DATASET_SELECTED
    ├── TRAINING → EVALUATING → REGISTERED
    ├── WAITING_APPROVAL
    │       ├── APPROVED → DEPLOYING → CANARY → ACTIVE → MONITORING → COMPLETED
    │       └── REJECTED (stop)
    ├── ROLLED_BACK (on canary failure)
    └── FAILED (on error)
```

## Usage

```python
from ml.lifecycle import LifecycleOrchestrator
from ml.lifecycle.models import TriggerSource

orch = LifecycleOrchestrator()

# 1. Start (from monitoring recommendation or manually)
wf = orch.start("valuation", trigger=TriggerSource.DRIFT_ALERT)

# 2. Training pipeline
orch.training_started(wf.workflow_id)
orch.training_completed(wf.workflow_id, experiment_id="exp-42", model_version=3)

# 3. Approval
orch.request_approval(wf.workflow_id)  # Optional — approve() does this automatically
orch.approve(wf.workflow_id, approver="ml-engineer", comment="MAE improved 12%")

# 4. Deployment
orch.deploy(wf.workflow_id, deployment_id="dep-xyz")
orch.start_canary(wf.workflow_id, start_pct=0.05)
# ... canary stable period ...
orch.promote(wf.workflow_id)
orch.start_monitoring(wf.workflow_id)
orch.complete(wf.workflow_id)

# Or reject
orch.reject(wf.workflow_id, approver="reviewer", reason="MAE degraded")
```

## Workflow States

| Stage | Description |
|-------|-------------|
| `QUEUED` | Workflow created, waiting |
| `DATASET_SELECTED` | Dataset version chosen |
| `TRAINING` | Model training in progress |
| `EVALUATING` | Model evaluation running |
| `REGISTERED` | Model registered in registry |
| `WAITING_APPROVAL` | Pending human approval |
| `APPROVED` / `REJECTED` | Approval decision |
| `DEPLOYING` | Deploying to serving |
| `CANARY` | Canary deployment active |
| `ACTIVE` | 100% traffic |
| `MONITORING` | Post-deploy monitoring |
| `COMPLETED` | Done |
| `FAILED` / `ROLLED_BACK` | Error or rollback |

## Key design

- **Coordinates, doesn't duplicate** — calls existing systems (Registry, Deployment, Serving, Monitoring)
- **Approval gating** — optional human approval before deployment
- **Concurrency control** — max_concurrent_workflows prevents resource exhaustion
- **Scheduler cooldown** — minimum retraining interval prevents thrashing
- **Full audit trail** — every stage transition recorded with timestamp

## Verified

- Full workflow: QUEUED → DATASET → TRAINING → REGISTERED → APPROVED → DEPLOY → ACTIVE → MONITORING → COMPLETED
- Rejection: APPROVED → REJECTED
- Rollback: DEPLOY → ROLLED_BACK (canary failure)
- Failure: TRAINING → FAILED (OOM)
- Concurrent limit: 3rd workflow rejected when max=2
- All 727 tests passing

---

*Lifecycle orchestrator documented 2026-07-12.*
