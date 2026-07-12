"""Test model persistence — save/load/list cycle."""
import pytest
import numpy as np
from src.ml.model_persistence import save_model, load_model, model_exists, list_saved_models


class DummyModel:
    """A minimal model-like object for testing persistence."""
    def __init__(self, value=42):
        self.value = value

    def predict(self, X):
        return np.array([self.value] * len(X))


def test_save_and_load_model():
    model = DummyModel(99)
    name = "test_model_save_load"

    path = save_model(model, name)
    assert model_exists(name)

    loaded = load_model(name)
    assert loaded is not None
    assert loaded.value == 99


def test_load_nonexistent_model():
    loaded = load_model("nonexistent_model_xyz")
    assert loaded is None


def test_model_exists_for_missing():
    assert not model_exists("definitely_not_a_real_model_12345")


def test_list_saved_models():
    # Save a model first so the list is non-empty
    save_model(DummyModel(1), "test_list_models")
    models = list_saved_models()
    assert "test_list_models" in models
    assert isinstance(models, list)
