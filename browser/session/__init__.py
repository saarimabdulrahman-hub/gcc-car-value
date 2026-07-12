"""Enterprise Cookie & Session Manager — centralized session lifecycle for browser automation."""
from browser.session.session_manager import SessionManager
from browser.session.cookie_store import CookieStore
from browser.session.models import BrowserSession, Cookie

__all__ = ["SessionManager", "CookieStore", "BrowserSession", "Cookie"]
