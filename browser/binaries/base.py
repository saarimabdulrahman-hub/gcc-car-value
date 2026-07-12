"""Base binary class for driver-specific extensions."""

from browser.binaries.models import BrowserBinary, BinaryStatus
import sys


class BaseBinary(BrowserBinary):
    """Pre-populated binary with current platform info."""

    def __init__(self, browser_type: str, executable_path: str, version: str = "0.0.0"):
        super().__init__(
            browser_type=browser_type,
            executable_path=executable_path,
            version=version,
            platform=sys.platform,
            architecture=_detect_arch(),
            status=BinaryStatus.UNKNOWN,
        )


def _detect_arch() -> str:
    import platform
    m = platform.machine()
    if m in ("x86_64", "AMD64"): return "x64"
    if m in ("arm64", "aarch64"): return "arm64"
    return m
