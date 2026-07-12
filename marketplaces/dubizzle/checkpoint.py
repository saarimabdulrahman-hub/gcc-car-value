"""Checkpoint — save/load crawl state for resume."""

import json
import os
from marketplaces.dubizzle.config import DubizzleConfig


class CheckpointManager:
    """Saves and loads crawl state to/from a JSON file."""

    def __init__(self, config: DubizzleConfig):
        self.config = config
        self._path = config.checkpoint_path

    def save(self, state: dict) -> None:
        if not self.config.checkpoint_enabled:
            return
        try:
            with open(self._path, "w") as f:
                json.dump(state, f, indent=2)
        except Exception:
            pass

    def load(self) -> dict | None:
        if not os.path.exists(self._path):
            return None
        try:
            with open(self._path, "r") as f:
                return json.load(f)
        except Exception:
            return None

    def clear(self) -> None:
        if os.path.exists(self._path):
            os.remove(self._path)
