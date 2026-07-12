"""Browser-specific error hierarchy."""


class BrowserError(Exception):
    """Base exception for all browser errors."""


class BrowserLaunchError(BrowserError):
    """Failed to launch browser process."""


class BrowserCrashError(BrowserError):
    """Browser process crashed or was killed."""


class NavigationError(BrowserError):
    """Page navigation failed (timeout, network error, invalid URL)."""


class TimeoutError(BrowserError):
    """Operation timed out waiting for element, navigation, or condition."""


class PageClosedError(BrowserError):
    """Operation attempted on a closed page."""


class ContextError(BrowserError):
    """Browser context creation or configuration failed."""


class DownloadError(BrowserError):
    """Download failed or was interrupted."""


class PermissionError(BrowserError):
    """Permission denied (geolocation, notifications, etc.)."""
