"""Session manager — HTTP sessions, UA rotation, headers, cookies, timeouts."""

import random
from typing import Any
import httpx


# Pool of recent desktop browser User-Agents for rotation
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Safari/605.1.15",
]

# GCC-relevant Accept-Language headers
_ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9,ar;q=0.8",
    "en-GB,en;q=0.9,ar;q=0.7",
    "ar,en;q=0.9",
]


class SessionManager:
    """Manages HTTP client sessions with UA rotation and GCC-optimized headers.

    Usage:
        mgr = SessionManager(user_agent="custom", timeout=30)
        async with mgr.session() as client:
            response = await client.get(url)
    """

    def __init__(self, user_agent: str | None = None,
                 timeout: float = 30.0,
                 headers: dict[str, str] | None = None,
                 cookies: dict[str, str] | None = None,
                 proxy: str | None = None):
        self._user_agent = user_agent
        self._timeout = timeout
        self._base_headers = headers or {}
        self._cookies = cookies or {}
        self._proxy = proxy
        self._client: httpx.AsyncClient | None = None

    def session(self) -> httpx.AsyncClient:
        """Create a new HTTP client session with rotated UA."""
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": random.choice(_ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "User-Agent": self._user_agent or random.choice(_USER_AGENTS),
            **self._base_headers,
        }

        proxy_url = self._proxy
        return httpx.AsyncClient(
            headers=headers,
            cookies=self._cookies,
            timeout=httpx.Timeout(self._timeout),
            follow_redirects=True,
            proxy=proxy_url,
        )

    async def create_session(self) -> httpx.AsyncClient:
        """Async factory — creates and returns a session."""
        if self._client is not None:
            await self._client.aclose()
        self._client = self.session()
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def rotate_user_agent(self) -> str:
        """Return a new random User-Agent string."""
        ua = random.choice(_USER_AGENTS)
        self._user_agent = ua
        return ua
