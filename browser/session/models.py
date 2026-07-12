"""Session and cookie data models."""

from dataclasses import dataclass, field
from enum import StrEnum
import time
import uuid


class SessionStatus(StrEnum):
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    DESTROYED = "destroyed"


class SessionPolicy(StrEnum):
    EPHEMERAL = "ephemeral"       # New session every time
    PERSISTENT = "persistent"     # Reuse across restarts
    AUTHENTICATED = "authenticated"  # Login session
    GUEST = "guest"               # No login
    READONLY = "readonly"         # Browse only, no form fills
    DISPOSABLE = "disposable"     # Destroy after single use


@dataclass
class Cookie:
    """A single browser cookie."""
    name: str
    value: str
    domain: str = ""
    path: str = "/"
    expires: float | None = None
    http_only: bool = False
    secure: bool = False
    same_site: str = "Lax"

    def to_dict(self) -> dict:
        return {
            "name": self.name, "value": self.value,
            "domain": self.domain, "path": self.path,
            "expires": self.expires or -1,
            "httpOnly": self.http_only, "secure": self.secure,
            "sameSite": self.same_site,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cookie":
        return cls(
            name=data.get("name", ""),
            value=data.get("value", ""),
            domain=data.get("domain", ""),
            path=data.get("path", "/"),
            expires=data.get("expires") if data.get("expires", -1) > 0 else None,
            http_only=data.get("httpOnly", False),
            secure=data.get("secure", False),
            same_site=data.get("sameSite", data.get("same_site", "Lax")),
        )


@dataclass
class BrowserSession:
    """A browser session with cookies and storage state."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    marketplace: str = ""
    browser_type: str = "chromium"
    policy: SessionPolicy = SessionPolicy.EPHEMERAL
    status: SessionStatus = SessionStatus.ACTIVE
    cookies: list[Cookie] = field(default_factory=list)
    storage_state: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    expires_at: float | None = None
    max_lifetime_seconds: float = 3600.0
    max_idle_seconds: float = 600.0
    request_count: int = 0
    metadata: dict = field(default_factory=dict)

    @property
    def is_expired(self) -> bool:
        if self.status == SessionStatus.EXPIRED:
            return True
        if self.expires_at and time.time() > self.expires_at:
            return True
        if time.time() - self.last_used > self.max_idle_seconds:
            return True
        return False

    @property
    def cookie_count(self) -> int:
        return len(self.cookies)

    def touch(self) -> None:
        self.last_used = time.time()
        self.request_count += 1
