"""Training Pipeline — orchestrates load → split → train → evaluate → register."""

import json, os, time
from ml.training.config import TrainingConfig
from ml.training.experiment import ExperimentTracker
from ml.training.evaluation import ModelEvaluator
from ml.training.cross_validation import CrossValidator
from ml.training.registry import ModelRegistry
from ml.training.hyperparameters import HyperparameterTracker
from ml.training.artifacts import ArtifactManager
from ml.training.metrics import MetricsCollector
from ml.training.models import Experiment, ModelEntry, EvaluationResult


class TrainingPipeline:
    """Full ML training pipeline — deterministic and reproducible.

    Usage:
        pipeline = TrainingPipeline()
        experiment = pipeline.run(
            data=feature_rows,
            model_train_fn=lambda X, y, hp: trained_model,
            model_predict_fn=lambda model, X: predictions,
            model_name="lightgbm_v1",
        )
    """

    def __init__(self, config: TrainingConfig | None = None):
        self.config = config or TrainingConfig()
        self._experiments = ExperimentTracker()
        self._evaluator = ModelEvaluator()
        self._cv = CrossValidator(seed=self.config.random_seed)
        self._registry = ModelRegistry()
        self._hp = HyperparameterTracker()
        self._artifacts = ArtifactManager(self.config.artifact_dir)
        self._metrics_collector = MetricsCollector()

    def run(self,
            data: list[dict],
            model_train_fn,
            model_predict_fn,
            model_name: str = "",
            hyperparameters: dict | None = None,
            feature_columns: list[str] | None = None,
            target_column: str = "",
            ) -> Experiment:
        """Execute a full training pipeline.

        Args:
            data: List of dicts (feature rows with target_column).
            model_train_fn: (X_train, y_train, hp) → trained model.
            model_predict_fn: (model, X) → predictions.
            model_name: Name for model registry.
            hyperparameters: Dict of hyperparameters for tracking.
            feature_columns: List of feature column names.
            target_column: Name of target column in data dicts.
        """
        start = time.perf_counter()
        hp = hyperparameters or {}
        target = target_column or self.config.target_column

        # 1. Create experiment
        exp = self._experiments.create(
            model_type=self.config.model_type,
            random_seed=self.config.random_seed,
            hyperparameters=hp,
            notes=model_name,
        )

        try:
            # 2. Extract features and target
            X = [{k: v for k, v in row.items() if k != target} for row in data]
            y = [row[target] for row in data if target in row]
            feature_cols = feature_columns or list(data[0].keys()) if data else []

            # 3. Train/test split
            indices = list(range(len(data)))
            import random
            rng = random.Random(self.config.random_seed)
            rng.shuffle(indices)
            split = int(len(indices) * (1 - self.config.test_size))
            train_idx = indices[:split]
            test_idx = indices[split:]

            X_train = [X[i] for i in train_idx]
            y_train = [y[i] for i in train_idx]
            X_test = [X[i] for i in test_idx]
            y_test = [y[i] for i in test_idx]

            # 4. Train model
            model = model_train_fn(X_train, y_train, hp)

            # 5. Predict
            y_pred = model_predict_fn(model, X_test)

            # 6. Evaluate
            eval_result = self._evaluator.evaluate(y_test, y_pred)

            # 7. Complete experiment
            metrics = {
                "mae": eval_result.mae, "rmse": eval_result.rmse,
                "mape": eval_result.mape, "r2": eval_result.r2,
                "median_ae": eval_result.median_absolute_error,
            }
            self._experiments.complete(exp.experiment_id, metrics)

            # 8. Register model
            self._registry.register(
                model_name=model_name or f"model_{int(time.time())}",
                model_type=self.config.model_type,
                experiment_id=exp.experiment_id,
                metrics=metrics,
                feature_names=feature_cols,
                artifact_path=self._artifacts.save_model(model, model_name),
            )

            # 9. Save artifacts
            self._artifacts.save_metrics(exp.experiment_id, metrics)
            self._artifacts.save_config(exp.experiment_id, {
                "hyperparameters": hp, "feature_columns": feature_cols,
                "random_seed": self.config.random_seed,
            })

            self._metrics_collector.record_success()
        except Exception as e:
            self._experiments.fail(exp.experiment_id, str(e))
            self._metrics_collector.record_failure()
            raise

        return exp

    @property
    def registry(self) -> ModelRegistry: return self._registry

    @property
    def experiments(self) -> ExperimentTracker: return self._experiments
