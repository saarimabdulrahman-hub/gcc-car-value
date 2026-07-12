"""Test fingerprint manager, catalog, validator, headers, locale/timezone consistency."""
import pytest
from browser.fingerprint.models import BrowserProfile
from browser.fingerprint.catalog import FingerprintCatalog, CATALOG
from browser.fingerprint.validator import FingerprintValidator
from browser.fingerprint.manager import FingerprintManager
from browser.fingerprint.headers import generate_headers
from browser.fingerprint.timezone import timezone_for_country, is_valid_timezone
from browser.fingerprint.locale import locale_for_country
from browser.fingerprint.errors import InconsistentProfileError, ProfileNotFoundError


class TestCatalog:
    def test_catalog_has_gcc_countries(self):
        catalog = FingerprintCatalog()
        countries = set(p.country for p in catalog.list_all())
        assert "AE" in countries
        assert "SA" in countries

    def test_get_by_country(self):
        catalog = FingerprintCatalog()
        profile = catalog.get_by_country("AE")
        assert profile is not None
        assert profile.country == "AE"

    def test_get_nonexistent_country(self):
        catalog = FingerprintCatalog()
        assert catalog.get_by_country("XX") is None

    def test_all_profiles_have_unique_ids(self):
        catalog = FingerprintCatalog()
        ids = [p.profile_id for p in catalog.list_all()]
        assert len(ids) == len(set(ids))

    def test_catalog_count_by_country(self):
        catalog = FingerprintCatalog()
        counts = catalog.count_by_country()
        assert counts["AE"] >= 3  # At least 3 UAE profiles


class TestValidator:
    def test_valid_profile_passes(self):
        validator = FingerprintValidator()
        profile = BrowserProfile(
            operating_system="Windows", browser_family="Chrome",
            timezone="Asia/Dubai", country="AE", locale="en-AE",
            viewport_width=1920, viewport_height=1080,
            screen_width=1920, screen_height=1080,
        )
        errors = validator.validate(profile)
        assert len(errors) == 0

    def test_invalid_os_browser_rejected(self):
        validator = FingerprintValidator()
        profile = BrowserProfile(
            operating_system="Windows", browser_family="Safari",
        )
        errors = validator.validate(profile)
        assert any("Invalid OS/browser" in e for e in errors)

    def test_timezone_country_mismatch_rejected(self):
        validator = FingerprintValidator()
        profile = BrowserProfile(
            timezone="Asia/Tokyo", country="AE",
        )
        errors = validator.validate(profile)
        assert any("timezone" in e.lower() for e in errors)

    def test_viewport_exceeds_screen_rejected(self):
        validator = FingerprintValidator()
        profile = BrowserProfile(
            viewport_width=4000, viewport_height=3000,
            screen_width=1920, screen_height=1080,
        )
        errors = validator.validate(profile)
        assert any("viewport" in e.lower() for e in errors)

    def test_all_catalog_profiles_are_valid(self):
        """Every profile in the catalog must pass validation."""
        validator = FingerprintValidator()
        catalog = FingerprintCatalog()
        for profile in catalog.list_all():
            errors = validator.validate(profile)
            assert len(errors) == 0, f"{profile.description}: {errors}"


class TestHeaders:
    def test_generates_complete_headers(self):
        profile = BrowserProfile(browser_family="Chrome", browser_version="131.0.0.0",
                                operating_system="Windows", operating_system_version="10")
        headers = generate_headers(profile)
        assert "User-Agent" in headers
        assert "Chrome/131" in headers["User-Agent"]
        assert "Sec-CH-UA" in headers
        assert "Chromium" in headers["Sec-CH-UA"]

    def test_user_agent_matches_os(self):
        profile = BrowserProfile(browser_family="Chrome", browser_version="131.0.0.0",
                                operating_system="Windows", operating_system_version="10")
        ua = profile.user_agent
        assert "Windows NT 10" in ua
        assert "Chrome/131" in ua


class TestTimezoneLocale:
    def test_uae_timezone(self):
        assert timezone_for_country("AE") == "Asia/Dubai"

    def test_saudi_timezone(self):
        assert timezone_for_country("SA") == "Asia/Riyadh"

    def test_valid_timezone_check(self):
        assert is_valid_timezone("AE", "Asia/Dubai")
        assert not is_valid_timezone("AE", "Asia/Tokyo")

    def test_locale_for_country(self):
        assert locale_for_country("AE") == "en-AE"
        assert locale_for_country("SA") == "ar-SA"


class TestFingerprintManager:
    def test_acquire_by_country(self):
        mgr = FingerprintManager()
        profile = mgr.acquire(country="AE")
        assert profile.country == "AE"

    def test_acquire_nonexistent_country_falls_back(self):
        mgr = FingerprintManager()
        profile = mgr.acquire(country="XX")
        assert profile is not None  # Falls back to random

    @pytest.mark.asyncio
    async def test_assign_to_session(self):
        mgr = FingerprintManager()
        profile = await mgr.assign_to_session("session-1", country="AE")
        retrieved = await mgr.get_session_profile("session-1")
        assert retrieved.profile_id == profile.profile_id

    @pytest.mark.asyncio
    async def test_release_session(self):
        mgr = FingerprintManager()
        await mgr.assign_to_session("session-2", country="AE")
        await mgr.release_session("session-2")
        assert await mgr.get_session_profile("session-2") is None

    def test_validate_all_catalog(self):
        """Every built-in profile must pass validation."""
        mgr = FingerprintManager()
        failures = mgr.validate_all()
        assert len(failures) == 0, f"Catalog has invalid profiles: {failures}"
