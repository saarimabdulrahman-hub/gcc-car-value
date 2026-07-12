"""Network layer — headers, request/response hooks, interceptors."""

from typing import Callable, Awaitable

RequestHook = Callable[["RequestInfo"], Awaitable[None]]
ResponseHook = Callable[["ResponseInfo"], Awaitable[None]]


class RequestInfo:
    def __init__(self, url: str, method: str = "GET",
                 headers: dict | None = None):
        self.url = url
        self.method = method
        self.headers = headers or {}


class ResponseInfo:
    def __init__(self, url: str, status: int = 200,
                 headers: dict | None = None, body: bytes = b""):
        self.url = url
        self.status = status
        self.headers = headers or {}
        self.body = body


class NetworkManager:
    """Manages network interception for a browser page."""

    def __init__(self):
        self._request_hooks: list[RequestHook] = []
        self._response_hooks: list[ResponseHook] = []

    def on_request(self, hook: RequestHook) -> None:
        self._request_hooks.append(hook)

    def on_response(self, hook: ResponseHook) -> None:
        self._response_hooks.append(hook)

    async def _handle_request(self, info: RequestInfo) -> None:
        for hook in self._request_hooks:
            await hook(info)

    async def _handle_response(self, info: ResponseInfo) -> None:
        for hook in self._response_hooks:
            await hook(info)
