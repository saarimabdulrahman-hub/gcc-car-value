"""ModelLoader — lazy singleton that loads the latest active model.

On first access, queries model_registry for the latest status='active' model.
Caches the loaded model in memory. Reloads when a new active model is detected.

Usage:
    from src.ml.model_loader import ModelLoader
    loader = ModelLoader(session)
    model, metadata = await loader.get_model()
    if model is None:
        # fall back to statistical engine
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.model_registry import ModelRegistry
from src.ml.model_persistence import load_model, model_exists

logger = structlog.get_logger()


class ModelLoader:
    """Singleton-style loader for the production ML model.

    Queries model_registry for the latest active model, loads it from disk,
    and caches in memory. Only reloads when a newer model is activated.
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self._model: object | None = None
        self._metadata: dict | None = None
        self._loaded_model_name: str | None = None

    async def get_model(self) -> tuple[object | None, dict | None]:
        """Return (model_object, metadata_dict).

        Returns (None, None) if no active model is registered or loading fails.
        The metadata dict contains: model_name, model_type, mae, mape,
        feature_version, features_used.
        """
        # Find the latest active model
        registry_entry = await self._get_active_model()

        if registry_entry is None:
            if self._loaded_model_name is not None:
                logger.warning("active_model_removed",
                              previous_model=self._loaded_model_name)
                self._invalidate()
            return None, None

        # Return cached model if it's still the active one
        if (self._model is not None
                and self._loaded_model_name == registry_entry.model_name):
            return self._model, self._metadata

        # New active model detected — load it
        logger.info("loading_active_model",
                    model_name=registry_entry.model_name,
                    previous_model=self._loaded_model_name)

        # First try loading from the path stored in registry
        model = None
        if registry_entry.model_path:
            model = load_model(registry_entry.model_name)

        # Fall back: try loading by model_name from models directory
        if model is None and model_exists(registry_entry.model_name):
            model = load_model(registry_entry.model_name)

        if model is None:
            logger.error("model_load_failed",
                        model_name=registry_entry.model_name,
                        registry_path=registry_entry.model_path)
            return None, None

        self._model = model
        self._loaded_model_name = registry_entry.model_name
        self._metadata = self._build_metadata(registry_entry)

        logger.info("active_model_loaded",
                    model_name=registry_entry.model_name,
                    mae=registry_entry.mae,
                    feature_version=registry_entry.feature_version)

        return self._model, self._metadata

    async def reload(self) -> tuple[object | None, dict | None]:
        """Force a reload of the active model (e.g., after deployment)."""
        self._invalidate()
        return await self.get_model()

    async def is_available(self) -> bool:
        """Check if a model is available without loading it."""
        entry = await self._get_active_model()
        if entry is None:
            return False
        return model_exists(entry.model_name) or (
            entry.model_path is not None
        )

    def _invalidate(self) -> None:
        """Clear cached model (force reload on next get_model)."""
        self._model = None
        self._metadata = None
        self._loaded_model_name = None

    async def _get_active_model(self) -> ModelRegistry | None:
        """Query the latest active model from model_registry."""
        stmt = (select(ModelRegistry)
                .where(ModelRegistry.status == "active")
                .order_by(ModelRegistry.activated_at.desc().nullslast())
                .order_by(ModelRegistry.trained_at.desc())
                .limit(1))
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def _build_metadata(entry: ModelRegistry) -> dict:
        return {
            "model_name": entry.model_name,
            "model_type": entry.model_type,
            "mae": entry.mae,
            "mape": entry.mape,
            "r2_score": entry.r2_score,
            "feature_version": entry.feature_version or "1.0.0",
            "features_used": entry.features_used or [],
            "training_rows": entry.training_rows,
            "trained_at": entry.trained_at.isoformat() if entry.trained_at else None,
        }
