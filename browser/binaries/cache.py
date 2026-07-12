"""Binary Cache — cache validation results and metadata."""

import time
from browser.binaries.models import BrowserBinary, ValidationResult


class BinaryCache:
    """In-memory cache for validation results with TTL."""

    def __init__(self, ttl_seconds: float = 300.0):
        self._ttl = ttl_seconds
        self._validation_cache: dict[str, tuple[float, ValidationResult]] = {}
        self._lookup_count = 0
        self._hit_count = 0

    def _key(self, binary: BrowserBinary) -> str:
        return f"{binary.browser_type}:{binary.executable_path}"

    def get_validation(self, binary: BrowserBinary) -> ValidationResult | None:
        self._lookup_count += 1
        key = self._key(binary)
        entry = self._validation_cache.get(key)
        if entry is None:
            return None
        timestamp, result = entry
        if time.monotonic() - timestamp > self._ttl:
            del self._validation_cache[key]
            return None
        self._hit_count += 1
        return result

    def set_validation(self, binary: BrowserBinary, result: ValidationResult) -> None:
        self._validation_cache[self._key(binary)] = (time.monotonic(), result)

    def invalidate(self, binary: BrowserBinary) -> None:
        self._validation_cache.pop(self._key(binary), None)

    def clear(self) -> None:
        self._validation_cache.clear()
        self._lookup_count = 0
        self._hit_count = 0

    @property
    def hit_rate(self) -> float:
        if self._lookup_count == 0:
            return 0.0
        return self._hit_count / self._lookup_count
