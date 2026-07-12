"""Playwright network helpers — request/response interception (future HAR support)."""


class PlaywrightNetwork:
    """Manages network interception for a Playwright page.

    Future: HAR recording, request blocking, response mocking.
    """

    def __init__(self, pw_page):
        self._pw_page = pw_page

    async def block_images(self) -> None:
        """Block image requests to save bandwidth."""
        try:
            await self._pw_page.route(
                "**/*.{png,jpg,jpeg,gif,svg,webp,ico}",
                lambda route: route.abort(),
            )
        except Exception:
            pass

    async def block_analytics(self) -> None:
        """Block analytics/tracking requests."""
        trackers = ["google-analytics", "googletagmanager", "facebook", "hotjar"]
        for tracker in trackers:
            try:
                await self._pw_page.route(
                    f"**/*{tracker}*",
                    lambda route: route.abort(),
                )
            except Exception:
                pass
