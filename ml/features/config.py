from dataclasses import dataclass, field

@dataclass
class FeatureStoreConfig:
    default_limit: int = 50000
    max_features: int = 200
    strict_validation: bool = True
    export_format: str = "csv"       # csv | jsonl | parquet
    include_checksum: bool = True
