from dataclasses import dataclass, field

@dataclass
class TrainingConfig:
    random_seed: int = 42
    test_size: float = 0.15
    cv_folds: int = 5
    cv_strategy: str = "kfold"          # kfold | stratified | time_series
    model_type: str = "lightgbm"        # lightgbm | xgboost | random_forest | linear
    target_column: str = "price"
    artifact_dir: str = ".ml_artifacts"
