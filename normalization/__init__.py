"""Vehicle Canonicalization Engine — normalize marketplace values to canonical forms."""
from normalization.engine import NormalizationEngine
from normalization.models import NormalizationReport, FieldNormalization

__all__ = ["NormalizationEngine", "NormalizationReport", "FieldNormalization"]
