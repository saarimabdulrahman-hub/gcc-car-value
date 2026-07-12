from dataclasses import dataclass, field

@dataclass
class FingerprintConfig:
    max_profiles: int = 50
    default_country: str = "AE"
    rotation_enabled: bool = False
    strict_validation: bool = True
