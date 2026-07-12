"""Selector versioning — track versions, deprecation, migration."""

from browser.selectors.models import Selector


class SelectorVersion:
    """Tracks version history for a selector."""

    def __init__(self):
        self._history: dict[str, list[Selector]] = {}  # marketplace:name → versions

    def add_version(self, selector: Selector) -> None:
        key = f"{selector.marketplace}:{selector.name}"
        if key not in self._history:
            self._history[key] = []
        self._history[key].append(selector)

    def get_current(self, marketplace: str, name: str) -> Selector | None:
        key = f"{marketplace}:{name}"
        versions = self._history.get(key, [])
        return versions[-1] if versions else None

    def get_history(self, marketplace: str, name: str) -> list[Selector]:
        key = f"{marketplace}:{name}"
        return self._history.get(key, [])

    def get_latest_version(self, marketplace: str, name: str) -> int:
        current = self.get_current(marketplace, name)
        return current.version if current else 0
