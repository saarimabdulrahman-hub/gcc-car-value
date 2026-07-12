"""Model persistence — save and load trained ML models to/from disk.

Replaces the tempfile approach in trainer.py with a stable directory.
Models are stored under src/ml/models/ (gitignored) and identified by model_name.
"""
import pickle
import os
from pathlib import Path
import structlog

logger = structlog.get_logger()

MODELS_DIR = Path(__file__).resolve().parent / "models"


def _ensure_models_dir() -> Path:
    """Create models directory if it doesn't exist."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    # Create .gitignore to prevent accidental commits of large model files
    gitignore = MODELS_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Auto-generated — ML model files\n*.pkl\n")
    return MODELS_DIR


def save_model(model: object, model_name: str) -> str:
    """Persist a trained model to disk.

    Returns the absolute path where the model was saved.
    """
    _ensure_models_dir()
    path = MODELS_DIR / f"{model_name}.pkl"
    with open(path, "wb") as f:
        pickle.dump(model, f)
    logger.info("model_saved", model_name=model_name, path=str(path))
    return str(path)


def load_model(model_name: str) -> object | None:
    """Load a model from disk by model_name.

    Returns None if the file doesn't exist or is corrupted.
    """
    path = MODELS_DIR / f"{model_name}.pkl"
    if not path.exists():
        logger.warning("model_file_not_found", model_name=model_name, path=str(path))
        return None

    try:
        with open(path, "rb") as f:
            model = pickle.load(f)
        logger.info("model_loaded", model_name=model_name, path=str(path))
        return model
    except Exception as e:
        logger.error("model_load_failed", model_name=model_name, error=str(e))
        return None


def model_exists(model_name: str) -> bool:
    """Check if a model file exists on disk."""
    path = MODELS_DIR / f"{model_name}.pkl"
    return path.exists()


def list_saved_models() -> list[str]:
    """List all saved model names."""
    _ensure_models_dir()
    return sorted([
        p.stem for p in MODELS_DIR.glob("*.pkl")
    ])
