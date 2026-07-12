"""Session store interface for future persistence backends."""

from abc import ABC, abstractmethod
from browser.session.models import BrowserSession


class SessionStore(ABC):
    """Abstract session persistence backend. Future: Redis, DB, file."""

    @abstractmethod
    async def save(self, session: BrowserSession) -> None: ...
    @abstractmethod
    async def load(self, session_id: str) -> BrowserSession | None: ...
    @abstractmethod
    async def delete(self, session_id: str) -> None: ...
    @abstractmethod
    async def list_all(self) -> list[BrowserSession]: ...
