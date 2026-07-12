"""Browser binary data models."""

from dataclasses import dataclass, field
from enum import StrEnum
import time


class BinaryStatus(StrEnum):
    UNKNOWN = "unknown"
    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"


@dataclass
class BrowserBinary:
    """A discovered or registered browser executable."""
    browser_type: str           # chromium, firefox, webkit
    executable_path: str        # Full path to the binary
    version: str = "0.0.0"
    revision: str = ""
    platform: str = ""          # linux, darwin, win32
    architecture: str = ""      # x64, arm64
    install_source: str = ""    # playwright, system, custom
    install_date: float = field(default_factory=time.time)
    checksum: str = ""
    status: BinaryStatus = BinaryStatus.UNKNOWN


@dataclass
class ValidationResult:
    """Result of validating a browser binary."""
    binary: BrowserBinary
    valid: bool = False
    executable_exists: bool = False
    platform_match: bool = False
    arch_match: bool = False
    version_parsed: bool = False
    errors: list[str] = field(default_factory=list)
