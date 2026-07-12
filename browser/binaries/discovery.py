"""Binary Discovery — find browser executables on the system."""

import os
import sys
from browser.binaries.models import BrowserBinary, BinaryStatus


class BinaryDiscovery:
    """Discover browser binaries in configured paths, PATH, and standard locations.

    Extensible — add new discovery strategies by appending to self._strategies.
    """

    def __init__(self, configured_paths: list[str] | None = None,
                 search_path: bool = True,
                 search_standard: bool = True):
        self._configured = configured_paths or []
        self._search_path = search_path
        self._search_standard = search_standard

    async def discover(self, browser_type: str) -> list[BrowserBinary]:
        """Find all binaries for a given browser type."""
        found: list[BrowserBinary] = []
        seen_paths: set[str] = set()

        # 1. Configured paths
        for path in self._configured:
            binaries = self._check_path(path, browser_type)
            for b in binaries:
                if b.executable_path not in seen_paths:
                    found.append(b)
                    seen_paths.add(b.executable_path)

        # 2. PATH lookup
        if self._search_path:
            for path_dir in os.environ.get("PATH", "").split(os.pathsep):
                binaries = self._check_path(path_dir, browser_type)
                for b in binaries:
                    if b.executable_path not in seen_paths:
                        found.append(b)
                        seen_paths.add(b.executable_path)

        # 3. Standard locations
        if self._search_standard:
            for loc in _standard_locations(browser_type):
                binaries = self._check_path(loc, browser_type)
                for b in binaries:
                    if b.executable_path not in seen_paths:
                        found.append(b)
                        seen_paths.add(b.executable_path)

        return found

    def _check_path(self, directory: str, browser_type: str) -> list[BrowserBinary]:
        """Check a directory for browser executables."""
        results = []
        exe_names = _executable_names(browser_type)
        for name in exe_names:
            full_path = os.path.join(directory, name)
            if os.path.isfile(full_path):
                results.append(BrowserBinary(
                    browser_type=browser_type,
                    executable_path=full_path,
                    platform=sys.platform,
                    architecture=_detect_arch(),
                    install_source="discovered",
                    status=BinaryStatus.UNKNOWN,
                ))
        return results


def _executable_names(browser_type: str) -> list[str]:
    """Platform-specific executable names for each browser type."""
    is_win = sys.platform == "win32"
    names = {
        "chromium": ["chromium", "chrome", "google-chrome-stable",
                     "chromium-browser"] + (["chromium.exe", "chrome.exe"] if is_win else []),
        "firefox": ["firefox", "firefox-esr"] + (["firefox.exe"] if is_win else []),
        "webkit": ["webkit", "WebKit"] + (["WebKit.exe"] if is_win else []),
    }
    return names.get(browser_type, [browser_type])


def _standard_locations(browser_type: str) -> list[str]:
    """Standard installation directories per platform."""
    if sys.platform == "win32":
        return [
            "C:\\Program Files\\Google\\Chrome\\Application",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application",
            "C:\\Program Files\\Mozilla Firefox",
            f"C:\\Users\\{os.environ.get('USER', '')}\\AppData\\Local\\Chromium\\Application",
        ]
    elif sys.platform == "darwin":
        return [
            "/Applications/Google Chrome.app/Contents/MacOS",
            "/Applications/Firefox.app/Contents/MacOS",
        ]
    else:
        return [
            "/usr/bin", "/usr/local/bin",
            "/opt/google/chrome", "/opt/chromium",
        ]


def _detect_arch() -> str:
    """Detect CPU architecture."""
    import platform
    machine = platform.machine()
    if machine in ("x86_64", "AMD64"):
        return "x64"
    if machine in ("arm64", "aarch64"):
        return "arm64"
    return machine
