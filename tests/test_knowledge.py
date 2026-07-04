"""Test knowledge base seed data."""
import pytest
from src.knowledge.seed import MODELS, DEPRECIATION


def test_all_makes_have_models():
    """Every make has at least one model."""
    assert len(MODELS) >= 12
    for make, models in MODELS.items():
        assert len(models) >= 1, f"{make} has no models"


def test_all_models_have_generations():
    """Every model has at least one generation."""
    for make, models in MODELS.items():
        for model_name, generations in models.items():
            assert len(generations) >= 1, f"{make} {model_name} has no generations"


def test_all_generations_have_specs():
    """Every generation has required fields."""
    for make, models in MODELS.items():
        for model_name, generations in models.items():
            for gen_name, gen_data in generations.items():
                assert gen_data.get("engine"), f"{make} {model_name} {gen_name}: missing engine"
                assert gen_data.get("fuel_economy"), f"{make} {model_name} {gen_name}: missing fuel_economy"
                assert gen_data.get("maintenance"), f"{make} {model_name} {gen_name}: missing maintenance"
                assert gen_data.get("ratings"), f"{make} {model_name} {gen_name}: missing ratings"


def test_depreciation_covers_all_models():
    """Every model has a depreciation curve."""
    for make, models in MODELS.items():
        for model_name in models:
            assert (make, model_name) in DEPRECIATION, \
                f"Missing depreciation for {make} {model_name}"


def test_all_ratings_in_range():
    """All ratings are between 1 and 5."""
    for make, models in MODELS.items():
        for model_name, generations in models.items():
            for gen_data in generations.values():
                r = gen_data["ratings"]
                for key in ["reliability", "comfort", "performance", "fuel_economy", "resale", "overall"]:
                    val = r.get(key)
                    assert val is not None, f"{make} {model_name}: missing rating {key}"
                    assert 1 <= val <= 5, f"{make} {model_name}: {key}={val} out of range"


def test_top_gcc_models_present():
    """Verify the top 5 most popular GCC models are in the seed."""
    expected = [
        ("Toyota", "Land Cruiser"),
        ("Toyota", "Camry"),
        ("Nissan", "Patrol"),
        ("Toyota", "Prado"),
        ("Lexus", "LX"),
    ]
    for make, model in expected:
        assert make in MODELS, f"Missing make: {make}"
        assert model in MODELS[make], f"Missing model: {make} {model}"


def test_model_count():
    """We have at least 25 unique make/model combinations (target was 50+ across generations)."""
    count = sum(len(models) for models in MODELS.values())
    assert count >= 25, f"Expected >= 25 models, got {count}"
