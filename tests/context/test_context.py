"""Test request context — storage, isolation, propagation, helpers."""
import asyncio
import pytest
from src.core.context.models import RequestContext
from src.core.context.storage import (
    set_context, get_context, clear_context,
    update_context, clone_context,
)
from src.core.context import clear_context  # ensure available in all test methods
from src.core.context.context import (
    correlation_id, run_with_context, run_sync_with_context,
)


class TestRequestContextModel:
    def test_empty_context(self):
        ctx = RequestContext.empty()
        assert ctx.correlation_id == ""
        assert ctx.request_id == ""

    def test_context_is_frozen(self):
        ctx = RequestContext(correlation_id="abc")
        with pytest.raises(Exception):  # FrozenInstanceError or similar
            ctx.correlation_id = "def"  # type: ignore

    def test_to_log_fields_includes_non_empty_only(self):
        ctx = RequestContext(correlation_id="cid-1", user_id="u-1")
        fields = ctx.to_log_fields()
        assert "correlation_id" in fields
        assert "user_id" in fields
        assert "country" not in fields  # empty → excluded

    def test_to_response_headers(self):
        ctx = RequestContext(correlation_id="cid-1", request_id="rid-1")
        headers = ctx.to_response_headers()
        assert headers["X-Correlation-ID"] == "cid-1"
        assert headers["X-Request-ID"] == "rid-1"

    def test_empty_context_has_no_headers(self):
        ctx = RequestContext.empty()
        assert ctx.to_response_headers() == {}


class TestContextStorage:
    def test_set_and_get(self):
        ctx = RequestContext(correlation_id="test-cid")
        set_context(ctx)
        assert get_context().correlation_id == "test-cid"
        clear_context()

    def test_default_is_empty(self):
        clear_context()
        ctx = get_context()
        assert ctx.correlation_id == ""
        assert isinstance(ctx, RequestContext)

    def test_update_creates_new_context(self):
        original = RequestContext(correlation_id="orig", user_id="user-1")
        set_context(original)
        updated = update_context(country="AE")
        assert updated.correlation_id == "orig"  # preserved
        assert updated.country == "AE"            # new
        assert original.country == ""             # unchanged
        clear_context()

    def test_clone_is_independent(self):
        ctx = RequestContext(correlation_id="clone-test")
        set_context(ctx)
        cloned = clone_context()
        assert cloned.correlation_id == "clone-test"
        clear_context()
        # Original context cleared, clone still has the value
        assert cloned.correlation_id == "clone-test"


class TestCorrelationId:
    def test_empty_by_default(self):
        clear_context()
        assert correlation_id() == ""


class TestAsyncIsolation:
    @pytest.mark.asyncio
    async def test_contexts_are_isolated(self):
        """Two concurrent tasks should have independent contexts."""
        results = []

        async def task(name, cid):
            ctx = RequestContext(correlation_id=cid, user_id=name)
            set_context(ctx)
            await asyncio.sleep(0.01)  # Let both tasks interleave
            results.append(get_context().correlation_id)

        await asyncio.gather(
            task("task-a", "cid-a"),
            task("task-b", "cid-b"),
        )

        assert "cid-a" in results
        assert "cid-b" in results
        assert len(set(results)) == 2  # Both unique

    @pytest.mark.asyncio
    async def test_context_preserved_across_awaits(self):
        """Context persists across await points within the same task."""
        set_context(RequestContext(correlation_id="persist-test"))

        await asyncio.sleep(0)  # Yield control
        await asyncio.sleep(0)  # Yield again

        assert correlation_id() == "persist-test"
        clear_context()


class TestRunWithContext:
    @pytest.mark.asyncio
    async def test_background_task_inherits_context(self):
        import src.core.context.storage as _s
        parent_ctx = RequestContext(correlation_id="parent-cid")
        _s.set_context(parent_ctx)

        result = []

        async def background_job():
            result.append(correlation_id())

        await run_with_context(background_job(), clone_context())
        assert result[0] == "parent-cid"
        _s.clear_context()

    @pytest.mark.asyncio
    async def test_background_task_cleans_up(self):
        import src.core.context.storage as _s
        _s.set_context(RequestContext(correlation_id="parent"))
        await run_with_context(asyncio.sleep(0), clone_context())
        assert correlation_id() == "parent"
        _s.clear_context()

    def test_sync_runner(self):
        import src.core.context.storage as _s
        ctx = RequestContext(correlation_id="sync-test")

        def worker():
            assert correlation_id() == "sync-test"

        run_sync_with_context(worker, ctx)
        _s.clear_context()
