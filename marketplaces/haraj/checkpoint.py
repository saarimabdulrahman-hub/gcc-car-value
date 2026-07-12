"""Haraj checkpoint — save/load crawl state."""

import json, os
from marketplaces.haraj.config import HarajConfig


class HarajCheckpoint:
    def __init__(self, config: HarajConfig): self._path = config.checkpoint_path; self._enabled = config.checkpoint_enabled
    def save(self, state: dict):
        if not self._enabled: return
        try:
            with open(self._path, "w") as f: json.dump(state, f, indent=2)
        except Exception: pass
    def load(self) -> dict | None:
        if not os.path.exists(self._path): return None
        try:
            with open(self._path, "r") as f: return json.load(f)
        except Exception: return None
