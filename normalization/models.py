"""Normalization data models."""

from dataclasses import dataclass, field


@dataclass
class FieldNormalization:
    """Tracks normalization of a single field."""
    field: str
    original: str
    normalized: str
    confidence: float = 1.0       # 0.0–1.0
    rule: str = ""                # Which rule was applied
    alias_used: str = ""          # Which alias matched
    warnings: list[str] = field(default_factory=list)


@dataclass
class NormalizationReport:
    """Complete normalization report for a listing."""
    listing_id: str = ""
    marketplace: str = ""
    fields: list[FieldNormalization] = field(default_factory=list)
    total_fields: int = 0
    changed_fields: int = 0       # Fields that were actually modified
    errors: list[str] = field(default_factory=list)

    @property
    def changed(self) -> list[FieldNormalization]:
        return [f for f in self.fields if f.original != f.normalized]
