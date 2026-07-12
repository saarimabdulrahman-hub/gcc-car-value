from dataclasses import dataclass, field

@dataclass
class SessionManagerConfig:
    default_policy: str = "ephemeral"
    max_sessions: int = 100
    session_max_lifetime: float = 3600.0
    session_max_idle: float = 600.0
    cookie_encryption_enabled: bool = False
    mask_cookies_in_logs: bool = True
