import json, os
from marketplaces.opensooq.config import OpenSooqConfig

class OpenSooqCheckpoint:
    def __init__(self, c: OpenSooqConfig): self._path = c.checkpoint_path; self._on = c.checkpoint_enabled
    def save(self, s):
        if not self._on: return
        try:
            with open(self._path,"w") as f: json.dump(s, f)
        except Exception: pass
    def load(self):
        if not os.path.exists(self._path): return None
        try:
            with open(self._path) as f: return json.load(f)
        except Exception: return None
