"""Test binary manager — registry, validation, cache, version, discovery."""
import os
import asyncio
import pytest
from browser.binaries.models import BrowserBinary, BinaryStatus, ValidationResult
from browser.binaries.registry import BinaryRegistry
from browser.binaries.validator import BinaryValidator
from browser.binaries.cache import BinaryCache
from browser.binaries.version import VersionResolver
from browser.binaries.discovery import BinaryDiscovery
from browser.binaries.manager import BinaryManager
from browser.binaries.config import BinaryManagerConfig
from browser.binaries.errors import BinaryNotFoundError, BinaryRegistrationError


@pytest.fixture
def sample_binary():
    return BrowserBinary(
        browser_type="chromium",
        executable_path="/usr/bin/chromium",
        version="120.0.6099.109",
        platform="linux",
        architecture="x64",
    )


class TestVersionResolver:
    def test_parse(self):
        assert VersionResolver.parse("120.0.6099.109") == (120, 0, 6099, 109)
        assert VersionResolver.parse("1.2.3") == (1, 2, 3)

    def test_compare(self):
        assert VersionResolver.compare("120", "119") == 1
        assert VersionResolver.compare("100", "100") == 0
        assert VersionResolver.compare("99", "100") == -1

    def test_meets_minimum(self):
        assert VersionResolver.meets_minimum("120.0", "100.0")
        assert not VersionResolver.meets_minimum("99.0", "100.0")

    def test_is_valid(self):
        assert VersionResolver.is_valid("120.0.6099")
        assert not VersionResolver.is_valid("not-a-version")


class TestBinaryRegistry:
    @pytest.mark.asyncio
    async def test_register_and_find(self, sample_binary):
        reg = BinaryRegistry()
        await reg.register(sample_binary)
        found = await reg.find("chromium")
        assert found is not None
        assert found.executable_path == "/usr/bin/chromium"

    @pytest.mark.asyncio
    async def test_find_by_version(self):
        reg = BinaryRegistry()
        await reg.register(BrowserBinary("chromium", "/usr/bin/chromium", version="120.0"))
        await reg.register(BrowserBinary("chromium", "/usr/local/bin/chromium", version="110.0"))
        found = await reg.find("chromium", version="115.0")
        assert found is not None
        assert found.version == "120.0"  # Highest >= 115

    @pytest.mark.asyncio
    async def test_duplicate_raises(self, sample_binary):
        reg = BinaryRegistry()
        await reg.register(sample_binary)
        with pytest.raises(BinaryRegistrationError):
            await reg.register(sample_binary)

    @pytest.mark.asyncio
    async def test_find_nonexistent(self):
        reg = BinaryRegistry()
        found = await reg.find("chromium")
        assert found is None


class TestBinaryValidator:
    def test_validates_existing_file(self):
        """Python executable should always exist and be valid."""
        import sys
        binary = BrowserBinary("chromium", sys.executable,
                              platform=sys.platform)
        validator = BinaryValidator()
        result = validator.validate(binary)
        assert result.executable_exists
        assert result.platform_match

    def test_invalidates_missing_file(self):
        binary = BrowserBinary("chromium", "/nonexistent/path/browser")
        validator = BinaryValidator()
        result = validator.validate(binary)
        assert not result.valid
        assert not result.executable_exists


class TestBinaryCache:
    def test_cache_hit_and_miss(self, sample_binary):
        cache = BinaryCache(ttl_seconds=60)
        result = ValidationResult(binary=sample_binary, valid=True)
        assert cache.get_validation(sample_binary) is None  # Miss
        cache.set_validation(sample_binary, result)
        cached = cache.get_validation(sample_binary)
        assert cached is not None
        assert cached.valid

    def test_cache_expiry(self, sample_binary):
        cache = BinaryCache(ttl_seconds=0.001)
        cache.set_validation(sample_binary, ValidationResult(binary=sample_binary, valid=True))
        import time; time.sleep(0.01)
        assert cache.get_validation(sample_binary) is None  # Expired

    def test_hit_rate(self, sample_binary):
        cache = BinaryCache()
        cache.get_validation(sample_binary)  # miss
        cache.set_validation(sample_binary, ValidationResult(binary=sample_binary))
        cache.get_validation(sample_binary)  # hit
        assert cache.hit_rate == 0.5


class TestBinaryManager:
    @pytest.mark.asyncio
    async def test_resolve_fails_with_no_binaries(self):
        mgr = BinaryManager(BinaryManagerConfig(
            search_path=False, search_standard_locations=False,
        ))
        # Don't initialize — no binaries registered
        with pytest.raises(BinaryNotFoundError):
            await mgr.resolve("chromium")


class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_registrations(self):
        reg = BinaryRegistry()
        async def register_one(i):
            await reg.register(BrowserBinary(
                f"browser-{i}", f"/usr/bin/browser-{i}",
                version=f"{i}.0.0"
            ))
        await asyncio.gather(*[register_one(i) for i in range(50)])
        all_bins = await reg.list_all()
        assert len(all_bins) == 50
