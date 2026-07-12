# GCC Car Value — Health Check Framework

**Date:** 2026-07-12  
**Package:** `src.core.health`

---

## 1. Architecture

```
Kubernetes / Load Balancer / Monitoring
    │
    ├── GET /health/live    → run_liveness()   → HTTP 200 (always, if alive)
    ├── GET /health/ready   → run_readiness()  → HTTP 200 | 503
    ├── GET /health/startup → run_readiness()  → HTTP 200 | 503
    └── GET /health         → run_all()        → HTTP 200 | 503
                                  │
                                  ▼
                          HealthRegistry
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              DatabaseCheck  MemoryCheck  ConfigurationCheck
              SecretsCheck   MetricsRegistryCheck
```

## 2. Endpoints

| Endpoint | Purpose | HTTP on Failure | Checks External Deps? |
|----------|---------|-----------------|----------------------|
| `GET /health` | Full health — all dependencies | 503 if critical fails, 200 if degraded | Yes |
| `GET /health/live` | Liveness — is the process alive? | Always 200 | No |
| `GET /health/ready` | Readiness — can we serve traffic? | 503 if critical fails | Yes (critical only) |
| `GET /health/startup` | Startup — has init completed? | 503 if critical fails | Yes (critical only) |

## 3. Status Aggregation

| Critical Check | Optional Check | Overall Status | HTTP Code |
|----------------|---------------|----------------|-----------|
| All healthy | All healthy | `healthy` | 200 |
| All healthy | Some degraded | `degraded` | 200 |
| Any unhealthy | Any | `unhealthy` | 503 |

- **Critical checks** (database, secrets, config) → failure = `unhealthy`
- **Optional checks** (metrics registry, cache, external APIs) → failure = `degraded`

## 4. Built-in Checks

| Check | Severity | What it verifies |
|-------|----------|-----------------|
| `DatabaseCheck` | Critical | `SELECT 1`, migration table exists |
| `MemoryCheck` | Critical | RSS < 90% of system memory |
| `ConfigurationCheck` | Critical | JWT secret set + valid, DATABASE_URL set, valid environment |
| `SecretsCheck` | Critical | Provider ready, JWT_SECRET retrievable |
| `MetricsRegistryCheck` | Optional | Registry initialized, lifecycle metrics present |

## 5. Adding a New Health Check

```python
from src.core.health.base import HealthCheck, CheckResult, CheckSeverity

class RedisCheck(HealthCheck):
    def __init__(self, redis_client):
        super().__init__(
            name="redis",
            severity=CheckSeverity.OPTIONAL,  # Degraded if Redis is down
            timeout_seconds=3.0,
        )
        self._client = redis_client

    async def check(self) -> CheckResult:
        try:
            await self._client.ping()
            return CheckResult.healthy(name=self.name)
        except Exception as e:
            return CheckResult.degraded(
                name=self.name,
                error=str(e)[:200],
            )
```

Then register in `src/api/routes/health.py`:

```python
from src.core.health.checks import RedisCheck
health_registry.register(RedisCheck(redis_client))
```

## 6. Timeout Handling

Every check has a configurable timeout (default 5s for critical, 2-3s for others). The registry runs all checks concurrently with `asyncio.wait_for()`. A timed-out check returns `unhealthy` with an error message. Other checks are unaffected.

```python
class MyCheck(HealthCheck):
    def __init__(self):
        super().__init__(
            name="my-check",
            timeout_seconds=10.0,  # Allow up to 10s
        )
```

## 7. Metrics Integration

Health check execution automatically publishes to the metrics registry:

| Metric | Type | Labels |
|--------|------|--------|
| `health.checks_total` | Counter | `name`, `status` |
| `health.check_duration_ms` | Histogram | `name` |
| `health.total_duration_ms` | Gauge | — |

## 8. Kubernetes Probe Configuration

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10

startupProbe:
  httpGet:
    path: /health/startup
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 5
  failureThreshold: 30  # 2.5 minutes to start
```

## 9. Response Format

```json
{
  "status": "healthy",
  "checks": [
    {
      "name": "database",
      "status": "healthy",
      "severity": "critical",
      "duration_ms": 3.45,
      "error": null,
      "connectivity": "ok",
      "migrations": "ok"
    },
    {
      "name": "memory",
      "status": "healthy",
      "severity": "critical",
      "duration_ms": 1.23,
      "rss_mb": 156.7,
      "rss_pct": 12.3
    }
  ],
  "duration_ms": 4.68
}
```

---

*Health framework documented 2026-07-12.*
