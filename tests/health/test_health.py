"""Test health check framework — registry, checks, status aggregation."""
import pytest
from src.core.health.base import (
    HealthCheck, CheckResult, HealthStatus, CheckSeverity,
)
from src.core.health.registry import HealthRegistry


# ------------------------------------------------------------------
# Mock checks for testing
# ------------------------------------------------------------------

class AlwaysHealthyCheck(HealthCheck):
    def __init__(self, name="test.healthy"):
        super().__init__(name=name)
    async def check(self) -> CheckResult:
        return CheckResult.healthy(name=self.name, duration_ms=1.0)

class AlwaysDegradedCheck(HealthCheck):
    def __init__(self, name="test.degraded"):
        super().__init__(name=name, severity=CheckSeverity.OPTIONAL)
    async def check(self) -> CheckResult:
        return CheckResult.degraded(name=self.name, error="optional down",
                                    duration_ms=1.0)

class AlwaysUnhealthyCheck(HealthCheck):
    def __init__(self, name="test.unhealthy"):
        super().__init__(name=name)
    async def check(self) -> CheckResult:
        return CheckResult.unhealthy(name=self.name, error="critical failure",
                                     duration_ms=1.0)

class SlowCheck(HealthCheck):
    def __init__(self, name="test.slow", delay=10.0):
        super().__init__(name=name, timeout_seconds=0.1)
        self.delay = delay
    async def check(self) -> CheckResult:
        import asyncio
        await asyncio.sleep(self.delay)
        return CheckResult.healthy(name=self.name)

class RaisingCheck(HealthCheck):
    def __init__(self, name="test.raising"):
        super().__init__(name=name)
    async def check(self) -> CheckResult:
        raise RuntimeError("boom")


# ------------------------------------------------------------------
# Tests
# ------------------------------------------------------------------

class TestCheckResult:
    def test_healthy_factory(self):
        r = CheckResult.healthy("db", duration_ms=5.0, pool_size=10)
        assert r.status == HealthStatus.HEALTHY
        assert r.name == "db"
        assert r.details["pool_size"] == 10

    def test_unhealthy_factory(self):
        r = CheckResult.unhealthy("db", error="timeout")
        assert r.status == HealthStatus.UNHEALTHY
        assert r.error == "timeout"

    def test_degraded_factory(self):
        r = CheckResult.degraded("cache", error="miss")
        assert r.status == HealthStatus.DEGRADED
        assert r.severity == CheckSeverity.OPTIONAL


class TestRegistry:
    @pytest.fixture
    def registry(self):
        return HealthRegistry()

    @pytest.mark.asyncio
    async def test_empty_registry_returns_healthy(self, registry):
        result = await registry.run_all()
        assert result["status"] == "healthy"
        assert result["checks"] == []

    @pytest.mark.asyncio
    async def test_single_healthy_check(self, registry):
        registry.register(AlwaysHealthyCheck())
        result = await registry.run_all()
        assert result["status"] == "healthy"
        assert len(result["checks"]) == 1
        assert result["checks"][0]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_optional_degraded_keeps_overall_healthy(self, registry):
        """Optional failures → overall 'degraded', not unhealthy."""
        registry.register(AlwaysHealthyCheck("db"))
        registry.register(AlwaysDegradedCheck("cache"))
        result = await registry.run_all()
        assert result["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_critical_unhealthy_overrides(self, registry):
        """Critical failure → overall 'unhealthy'."""
        registry.register(AlwaysHealthyCheck("db"))
        registry.register(AlwaysUnhealthyCheck("critical"))
        result = await registry.run_all()
        assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_timeout_produces_unhealthy(self, registry):
        registry.register(SlowCheck("test.slow", delay=5.0))
        result = await registry.run_all()
        assert result["status"] == "unhealthy"
        assert "timed out" in result["checks"][0]["error"]

    @pytest.mark.asyncio
    async def test_exception_produces_unhealthy(self, registry):
        registry.register(RaisingCheck())
        result = await registry.run_all()
        assert result["checks"][0]["status"] == "unhealthy"
        assert "boom" in result["checks"][0]["error"]

    @pytest.mark.asyncio
    async def test_concurrent_execution(self, registry):
        """All checks run concurrently."""
        registry.register(AlwaysHealthyCheck("a"))
        registry.register(AlwaysHealthyCheck("b"))
        registry.register(AlwaysHealthyCheck("c"))
        result = await registry.run_all()
        # Total duration should be ~max(individual), not sum
        assert result["duration_ms"] < 500  # 3 checks at 1ms each

    def test_register_and_unregister(self, registry):
        registry.register(AlwaysHealthyCheck("x"))
        assert "x" in registry.list_checks()
        registry.unregister("x")
        assert "x" not in registry.list_checks()

    def test_get_check(self, registry):
        registry.register(AlwaysHealthyCheck("my-check"))
        c = registry.get_check("my-check")
        assert c is not None
        assert c.name == "my-check"
        assert registry.get_check("nonexistent") is None

    @pytest.mark.asyncio
    async def test_run_liveness_always_healthy(self, registry):
        """Liveness doesn't run any registered checks."""
        registry.register(AlwaysUnhealthyCheck("dead"))
        result = await registry.run_liveness()
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_run_readiness_checks_critical_only(self, registry):
        registry.register(AlwaysUnhealthyCheck("critical"))
        result = await registry.run_readiness()
        assert result["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_duration_ms_tracked(self, registry):
        registry.register(AlwaysHealthyCheck())
        result = await registry.run_all()
        assert result["duration_ms"] >= 0
        assert result["checks"][0]["duration_ms"] >= 0


class TestHealthStatusMapping:
    def test_healthy_to_200(self):
        from src.api.routes.health import _status_to_http
        assert _status_to_http("healthy") == 200

    def test_degraded_to_200(self):
        """Degraded still returns 200 — app is serving."""
        from src.api.routes.health import _status_to_http
        assert _status_to_http("degraded") == 200

    def test_unhealthy_to_503(self):
        from src.api.routes.health import _status_to_http
        assert _status_to_http("unhealthy") == 503
