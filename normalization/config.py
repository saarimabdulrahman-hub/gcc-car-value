from dataclasses import dataclass

@dataclass
class NormalizationConfig:
    strict_makes: bool = False       # Reject unknown makes
    preserve_originals: bool = True  # Keep original in metadata
    confidence_threshold: float = 0.5
