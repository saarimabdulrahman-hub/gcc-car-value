"""Training versioning — tracks model versions per name."""

class VersionTracker:
    def __init__(self): self._versions: dict[str, int] = {}
    def next(self, name: str) -> int:
        v = self._versions.get(name, 0) + 1
        self._versions[name] = v
        return v
