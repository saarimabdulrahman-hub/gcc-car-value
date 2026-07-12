"""Test training pipeline — experiment, registry, evaluation, cross-validation, pipeline."""
import pytest
from ml.training.experiment import ExperimentTracker
from ml.training.registry import ModelRegistry
from ml.training.evaluation import ModelEvaluator
from ml.training.cross_validation import CrossValidator
from ml.training.pipeline import TrainingPipeline
from ml.training.hyperparameters import HyperparameterTracker
from ml.training.models import ModelStatus


class TestExperimentTracker:
    def test_create_and_complete(self):
        tracker = ExperimentTracker()
        exp = tracker.create(model_type="lightgbm", random_seed=42)
        assert exp.experiment_id
        assert exp.status == "running"

        tracker.complete(exp.experiment_id, {"mae": 5000.0})
        completed = tracker.get(exp.experiment_id)
        assert completed.status == "completed"
        assert completed.metrics["mae"] == 5000.0

    def test_fail(self):
        tracker = ExperimentTracker()
        exp = tracker.create(model_type="lightgbm")
        tracker.fail(exp.experiment_id, "out of memory")
        assert tracker.get(exp.experiment_id).status == "failed"


class TestModelRegistry:
    def test_register_and_promote(self):
        reg = ModelRegistry()
        reg.register("lightgbm_v1", model_type="lightgbm",
                     experiment_id="exp-1", metrics={"mae": 5000})

        entry = reg.promote("lightgbm_v1")
        assert entry.status == ModelStatus.ACTIVE
        assert entry.version == 1

    def test_rollback(self):
        reg = ModelRegistry()
        reg.register("lightgbm_v1", model_type="lightgbm", metrics={"mae": 5000})
        reg.register("lightgbm_v1", model_type="lightgbm", metrics={"mae": 4500})
        reg.promote("lightgbm_v1")  # promote v2
        rolled = reg.rollback("lightgbm_v1", reason="worse performance")
        assert rolled.version == 1
        assert rolled.status == ModelStatus.ACTIVE

    def test_list_models(self):
        reg = ModelRegistry()
        reg.register("model_a")
        reg.register("model_b")
        assert "model_a" in reg.list_models()


class TestEvaluation:
    def test_evaluate(self):
        evaluator = ModelEvaluator()
        y_true = [100000, 120000, 110000, 130000, 115000]
        y_pred = [98000, 122000, 108000, 128000, 117000]
        result = evaluator.evaluate(y_true, y_pred)
        assert result.mae > 0
        assert result.rmse > 0
        assert result.r2 > 0  # Should have good R² with close predictions


class TestCrossValidation:
    def test_train_test_split(self):
        cv = CrossValidator(seed=42)
        data = list(range(100))
        train, test = cv.train_test_split(data, test_size=0.2)
        assert len(train) == 80
        assert len(test) == 20

    def test_deterministic(self):
        data = list(range(100))
        cv1 = CrossValidator(seed=42)
        cv2 = CrossValidator(seed=42)
        t1, _ = cv1.train_test_split(data)
        t2, _ = cv2.train_test_split(data)
        assert t1 == t2  # Same seed = same split

    def test_kfold(self):
        cv = CrossValidator(seed=42)
        data = list(range(100))
        folds = cv.kfold(data, folds=5)
        assert len(folds) == 5


class TestTrainingPipeline:
    def test_run_pipeline(self):
        """Full pipeline with a mock model — just averages features."""
        pipeline = TrainingPipeline()

        # Generate fake data
        data = []
        import random
        rng = random.Random(42)
        for i in range(200):
            price = 50000 + rng.randint(0, 50000)
            data.append({
                "mileage_km": rng.randint(10000, 200000),
                "year": 2015 + rng.randint(0, 9),
                "price": price,
            })

        def train_fn(X, y, hp):
            # "Model" is just the average price
            class AvgModel:
                def __init__(self, avg): self.avg = avg
            return AvgModel(sum(y) / len(y))

        def predict_fn(model, X):
            return [model.avg] * len(X)

        exp = pipeline.run(
            data=data,
            model_train_fn=train_fn,
            model_predict_fn=predict_fn,
            model_name="test_model",
            target_column="price",
        )

        assert exp.status == "completed"
        assert "mae" in exp.metrics
        assert exp.metrics["r2"] <= 0.5  # Raw average shouldn't fit well

    def test_hyperparameter_defaults(self):
        hp = HyperparameterTracker.default_lightgbm()
        assert hp["n_estimators"] == 200
        assert hp["learning_rate"] == 0.05
