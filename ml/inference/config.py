from dataclasses import dataclass

@dataclass
class InferenceConfig:
    strict_validation: bool = True
    snapshot_enabled: bool = True
    audit_enabled: bool = True
    max_feature_age_days: int = 30
