"""Translate Playwright exceptions to platform exceptions.

No raw Playwright exceptions escape outside this module.
"""

from browser.errors import (
    BrowserLaunchError, BrowserCrashError, NavigationError,
    TimeoutError as BrowserTimeoutError, PageClosedError,
)


def translate_error(error: Exception) -> Exception:
    """Convert a Playwright (or generic) exception to a platform BrowserError.

    Attempts to detect Playwright error types by class name string matching
    since we can't import Playwright directly.
    """
    cls_name = type(error).__name__
    msg = str(error)[:500]

    if "Timeout" in cls_name or "timeout" in msg.lower():
        return BrowserTimeoutError(msg)
    if "TargetClosed" in cls_name or "closed" in msg.lower():
        return PageClosedError(msg)
    if "BrowserClosed" in cls_name or "browser has been closed" in msg.lower():
        return BrowserCrashError(msg)
    if "Error" in cls_name and "launch" in msg.lower():
        return BrowserLaunchError(msg)
    if "Navigation" in cls_name:
        return NavigationError(msg)

    # Unknown errors wrapped generically
    return BrowserCrashError(f"{cls_name}: {msg}")


def _import_playwright():
    """Lazy import Playwright. Returns (playwright module, error message)."""
    try:
        from playwright.async_api import async_playwright
        return async_playwright, None
    except ImportError:
        return None, (
            "Playwright is not installed. Install it with:\n"
            "  pip install playwright\n"
            "  playwright install chromium\n"
        )
