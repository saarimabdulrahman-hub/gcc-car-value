"""HTML cleaning data models."""

from dataclasses import dataclass, field


@dataclass
class CleaningReport:
    """Report produced after cleaning an HTML document."""
    original_size: int = 0           # bytes
    cleaned_size: int = 0            # bytes
    scripts_removed: int = 0
    styles_removed: int = 0
    comments_removed: int = 0
    hidden_nodes_found: int = 0
    validation_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    processing_time_ms: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class HTMLMetadata:
    """Metadata extracted from an HTML document."""
    title: str = ""
    description: str = ""
    canonical_url: str = ""
    keywords: str = ""
    language: str = ""
    charset: str = ""
    generator: str = ""
    viewport: str = ""
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""
    og_type: str = ""
    twitter_card: str = ""
    twitter_title: str = ""
