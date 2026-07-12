"""Model Loader — lazy loading, reload, version validation, graceful failure."""

from ml.training.registry import ModelRegistry
from ml.training.models import ModelEntry
from ml.serving.errors import ModelNotLoadedError


class ModelLoader:
    """Lazy model loader with version validation.

    Loads model artifacts from the training registry on first request.
    Supports reloads when a new model version is activated.
    """

    def __init__(self, registry: ModelRegistry):
        self._registry = registry
        self._loaded: dict[str, object] = {}     # model_name → model object
        self._entries: dict[str, ModelEntry] = {}  # model_name → metadata

    def load_active(self, model_name: str) -> object | None:
        """Load the active model for a given name. Returns cached if unchanged."""
        entry = self._registry.get(model_name)
        if entry is None: return None

        current = self._entries.get(model_name)
        if current and current.version == entry.version and model_name in self._loaded:
            return self._loaded[model_name]

        # Load new model
        from ml.training.artifacts import ArtifactManager
        am = ArtifactManager()
        try:
            model = am.load_model(entry.artifact_path)
            self._loaded[model_name] = model
            self._entries[model_name] = entry
            return model
        except Exception:
            # If new model fails to load, keep old one as fallback
            if model_name in self._loaded:
                return self._loaded[model_name]
            return None

    def get_active_model(self, model_name: str):
        """Get the currently loaded model or raise."""
        model = self._loaded.get(model_name)
        if model is None:
            model = self.load_active(model_name)
        if model is None:
            raise ModelNotLoadedError(f"No model loaded for '{model_name}'")
        return model

    def get_metadata(self, model_name: str) -> ModelEntry | None:
        return self._entries.get(model_name)

    def reload(self, model_name: str) -> object | None:
        """Force reload of the active model."""
        self._loaded.pop(model_name, None)
        return self.load_active(model_name)

    def is_loaded(self, model_name: str) -> bool:
        return model_name in self._loaded
