"""Hyperparameter Tracker — model type, learning rate, depth, estimators, regularization."""

class HyperparameterTracker:
    def __init__(self): self._runs: list[dict] = []

    def track(self, params: dict) -> None: self._runs.append(params)

    def list_runs(self) -> list[dict]: return self._runs

    @staticmethod
    def default_lightgbm() -> dict:
        return {"n_estimators": 200, "max_depth": 7, "learning_rate": 0.05,
                "num_leaves": 31, "min_child_samples": 30,
                "subsample": 0.8, "colsample_bytree": 0.8}

    @staticmethod
    def default_xgboost() -> dict:
        return {"n_estimators": 200, "max_depth": 6, "learning_rate": 0.05,
                "subsample": 0.8, "colsample_bytree": 0.8}
