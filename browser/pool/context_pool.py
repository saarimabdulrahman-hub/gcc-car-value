"""ContextPool — manages context allocation within a browser."""

from browser.base.interfaces import Browser, BrowserContext


class ContextPool:
    """Allocates isolated contexts from a browser.

    Each context has isolated cookies, storage, and cache.
    Contexts never share session data.
    """

    def __init__(self, browser: Browser, max_contexts: int = 20):
        self._browser = browser
        self._max_contexts = max_contexts
        self._contexts: list[BrowserContext] = []

    async def acquire(self) -> BrowserContext:
        """Get a new isolated context."""
        if len(self._contexts) >= self._max_contexts:
            # Recycle oldest context
            oldest = self._contexts.pop(0)
            await oldest.close()
        ctx = await self._browser.new_context()
        self._contexts.append(ctx)
        return ctx

    async def release(self, ctx: BrowserContext) -> None:
        """Return a context to the pool."""
        if ctx in self._contexts:
            self._contexts.remove(ctx)
            await ctx.close()

    async def close_all(self) -> None:
        for ctx in self._contexts:
            await ctx.close()
        self._contexts.clear()
