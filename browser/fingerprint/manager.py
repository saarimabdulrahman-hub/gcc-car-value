"""Fingerprint Manager — assigns coherent browser profiles to sessions."""

import asyncio
import random
import structlog

from browser.fingerprint.models import BrowserProfile
from browser.fingerprint.catalog import FingerprintCatalog
from browser.fingerprint.validator import FingerprintValidator
from browser.fingerprint.config import FingerprintConfig
from browser.fingerprint.errors import ProfileNotFoundError, InconsistentProfileError
from browser.fingerprint.headers import generate_headers

logger = structlog.get_logger()


class FingerprintManager:
    """Central manager for browser fingerprint assignment.

    Each browser session receives one BrowserProfile. The profile remains
    stable for the session's lifetime. Profiles are pre-defined and
    validated — no random generation.

    Usage:
        mgr = FingerprintManager()
        profile = mgr.acquire("AE")
        headers = profile.generate_headers()
        # Use headers when creating browser context
    """

    def __init__(self, config: FingerprintConfig | None = None):
        self.config = config or FingerprintConfig()
        self._catalog = FingerprintCatalog()
        self._validator = FingerprintValidator()
        self._assignments: dict[str, str] = {}  # session_id → profile_id
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------
    # Profile acquisition
    # ------------------------------------------------------------------

    def acquire(self, country: str | None = None,
                profile_id: str | None = None) -> BrowserProfile:
        """Get a profile for use. Returns a validated BrowserProfile.

        If profile_id is given, returns that specific profile.
        If country is given, returns a profile for that country.
        Otherwise returns a random profile from the catalog.
        """
        if profile_id:
            profile = self._catalog.get_by_id(profile_id)
            if profile is None:
                raise ProfileNotFoundError(profile_id)
        elif country:
            candidates = self._catalog.list_by_country(country)
            if not candidates:
                candidates = self._catalog.list_all()
            profile = random.choice(candidates) if candidates else None
            if profile is None:
                raise ProfileNotFoundError(f"No profile for country '{country}'")
        else:
            all_profiles = self._catalog.list_all()
            if not all_profiles:
                raise ProfileNotFoundError("Catalog is empty")
            profile = random.choice(all_profiles)

        # Validate before returning
        if self.config.strict_validation:
            self._validator.validate_or_raise(profile)

        return profile

    async def assign_to_session(self, session_id: str,
                                country: str | None = None,
                                profile_id: str | None = None) -> BrowserProfile:
        """Assign a profile to a session and track the assignment."""
        profile = self.acquire(country=country, profile_id=profile_id)
        async with self._lock:
            self._assignments[session_id] = profile.profile_id
        return profile

    async def get_session_profile(self, session_id: str) -> BrowserProfile | None:
        """Get the profile assigned to a session."""
        async with self._lock:
            pid = self._assignments.get(session_id)
        if pid is None:
            return None
        return self._catalog.get_by_id(pid)

    async def release_session(self, session_id: str) -> None:
        """Remove a session's profile assignment."""
        async with self._lock:
            self._assignments.pop(session_id, None)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, profile: BrowserProfile) -> list[str]:
        """Validate a profile. Returns list of errors."""
        return self._validator.validate(profile)

    def validate_or_raise(self, profile: BrowserProfile) -> None:
        self._validator.validate_or_raise(profile)

    # For testing — validate all catalog entries
    def validate_all(self) -> dict[str, list[str]]:
        """Validate every profile in the catalog."""
        results = {}
        for p in self._catalog.list_all():
            errors = self._validator.validate(p)
            if errors:
                results[p.description or p.profile_id] = errors
        return results

    # ------------------------------------------------------------------
    # Headers for Playwright context
    # ------------------------------------------------------------------

    def headers_for_session(self, session_id: str) -> dict[str, str]:
        """Generate HTTP headers for a session's assigned profile."""
        profile = self._catalog.get_by_id(
            self._assignments.get(session_id, "")
        )
        if profile is None:
            return {}
        return generate_headers(profile)
