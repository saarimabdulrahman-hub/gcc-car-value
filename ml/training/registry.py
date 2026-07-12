"""Model Registry — register, list, promote, archive, rollback, version history."""

import uuid, time, threading
from ml.training.models import ModelEntry, ModelStatus
from ml.training.errors import ModelNotFoundError


class ModelRegistry:
    def __init__(self):
        self._models: dict[str, list[ModelEntry]] = {}  # model_name → versions
        self._active: dict[str, ModelEntry] = {}         # model_name → active version
        self._lock = threading.Lock()

    def register(self, model_name: str, model_type: str = "",
                 experiment_id: str = "", metrics: dict | None = None,
                 feature_importance: dict | None = None,
                 feature_names: list[str] | None = None,
                 artifact_path: str = "",
                 ) -> ModelEntry:
        with self._lock:
            versions = self._models.get(model_name, [])
            entry = ModelEntry(
                model_id=str(uuid.uuid4())[:12],
                model_name=model_name, model_type=model_type,
                version=len(versions) + 1,
                status=ModelStatus.REGISTERED,
                experiment_id=experiment_id,
                metrics=metrics or {},
                feature_importance=feature_importance or {},
                feature_names=feature_names or [],
                artifact_path=artifact_path,
            )
            self._models.setdefault(model_name, []).append(entry)
            return entry

    def promote(self, model_name: str, version: int | None = None) -> ModelEntry:
        """Promote a model to active. Demotes previous active."""
        with self._lock:
            versions = self._models.get(model_name, [])
            if not versions: raise ModelNotFoundError(model_name)

            if version is None:
                entry = versions[-1]
            else:
                matches = [v for v in versions if v.version == version]
                if not matches: raise ModelNotFoundError(f"{model_name} v{version}")
                entry = matches[0]

            # Demote current active
            if model_name in self._active:
                self._active[model_name].status = ModelStatus.ARCHIVED

            entry.status = ModelStatus.ACTIVE
            entry.promoted_at = time.time()
            self._active[model_name] = entry
            return entry

    def rollback(self, model_name: str, reason: str = "") -> ModelEntry:
        with self._lock:
            versions = self._models.get(model_name, [])
            if len(versions) < 2:
                raise ModelNotFoundError(f"No previous version to rollback for {model_name}")

            current = self._active.get(model_name)
            if current:
                current.status = ModelStatus.ROLLED_BACK
                current.rolled_back_at = time.time()
                current.rollback_reason = reason

            # Activate previous version
            previous = versions[-2]
            previous.status = ModelStatus.ACTIVE
            previous.promoted_at = time.time()
            self._active[model_name] = previous
            return previous

    def get(self, model_name: str, version: int | None = None) -> ModelEntry | None:
        versions = self._models.get(model_name, [])
        if not versions: return None
        if version:
            matches = [v for v in versions if v.version == version]
            return matches[0] if matches else None
        return self._active.get(model_name) or versions[-1]

    def list_models(self) -> list[str]:
        return sorted(self._models.keys())

    def list_versions(self, model_name: str) -> list[ModelEntry]:
        return self._models.get(model_name, [])

    def get_active(self) -> list[ModelEntry]:
        return list(self._active.values())

    def archive(self, model_name: str, version: int) -> None:
        entry = self.get(model_name, version)
        if entry: entry.status = ModelStatus.ARCHIVED
