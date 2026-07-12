"""Version Resolver — semver comparison and compatibility checks."""

import re


class VersionResolver:
    """Compare browser versions and check compatibility."""

    @staticmethod
    def parse(version: str) -> tuple[int, ...]:
        """Parse a version string into a comparable tuple."""
        parts = re.findall(r'\d+', version)
        return tuple(int(p) for p in parts) if parts else (0,)

    @staticmethod
    def is_valid(version: str) -> bool:
        return bool(re.match(r'\d+(\.\d+)*', version))

    @staticmethod
    def compare(v1: str, v2: str) -> int:
        """Compare two versions. Returns -1, 0, or 1."""
        p1 = VersionResolver.parse(v1)
        p2 = VersionResolver.parse(v2)
        max_len = max(len(p1), len(p2))
        p1 = p1 + (0,) * (max_len - len(p1))
        p2 = p2 + (0,) * (max_len - len(p2))
        if p1 < p2: return -1
        if p1 > p2: return 1
        return 0

    @staticmethod
    def meets_minimum(version: str, minimum: str) -> bool:
        return VersionResolver.compare(version, minimum) >= 0
