"""Driver manager configuration."""

from dataclasses import dataclass, field


@dataclass
class DriverManagerConfig:
    preferred_driver: str = ""         # Preferred driver name
    fallback_driver: str = ""          # Fallback if preferred unavailable
    launch_timeout: float = 30.0       # Seconds to wait for browser launch
    health_check_interval: float = 30.0
    auto_recovery: bool = True         # Auto-restart failed drivers
    compatibility_checks: bool = True  # Validate driver compat before launch
    feature_flags: dict[str, bool] = field(default_factory=dict)
