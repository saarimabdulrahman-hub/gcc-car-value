"""Enterprise Browser Fingerprint Manager — coherent browser identity profiles."""
from browser.fingerprint.manager import FingerprintManager
from browser.fingerprint.profile import BrowserProfile
from browser.fingerprint.catalog import FingerprintCatalog

__all__ = ["FingerprintManager", "BrowserProfile", "FingerprintCatalog"]
