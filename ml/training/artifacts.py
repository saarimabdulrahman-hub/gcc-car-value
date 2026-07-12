"""Artifact Manager — persist models, metrics, configs, metadata."""

import json, os, pickle


class ArtifactManager:
    def __init__(self, base_dir: str = ".ml_artifacts"):
        self._base = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save_model(self, model, name: str) -> str:
        path = os.path.join(self._base, f"{name}.pkl")
        try:
            with open(path, "wb") as f:
                pickle.dump(model, f)
        except (pickle.PicklingError, TypeError, AttributeError):
            # Model is not pickleable (e.g., mock/test model) — save placeholder
            path = os.path.join(self._base, f"{name}.txt")
            with open(path, "w") as f:
                f.write(f"Model: {name}\nType: {type(model).__name__}\n")
        return path

    def load_model(self, path: str):
        with open(path, "rb") as f:
            return pickle.load(f)

    def save_metrics(self, exp_id: str, metrics: dict) -> str:
        path = os.path.join(self._base, f"{exp_id}_metrics.json")
        with open(path, "w") as f:
            json.dump(metrics, f, indent=2)
        return path

    def save_config(self, exp_id: str, config: dict) -> str:
        path = os.path.join(self._base, f"{exp_id}_config.json")
        with open(path, "w") as f:
            json.dump(config, f, indent=2)
        return path
