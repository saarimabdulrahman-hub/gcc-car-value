"""DOM data models."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractionResult:
    """Result of a typed extraction operation."""
    value: Any = None
    raw: str = ""
    success: bool = False
    error: str | None = None
    selector: str = ""
    field_name: str = ""


@dataclass
class DocumentStats:
    """Statistics about a parsed document."""
    node_count: int = 0
    text_length: int = 0
    links_count: int = 0
    images_count: int = 0
    forms_count: int = 0
    tables_count: int = 0
