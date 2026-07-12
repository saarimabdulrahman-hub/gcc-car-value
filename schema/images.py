"""Images sub-model."""

from dataclasses import dataclass, field


@dataclass
class Images:
    """Listing images."""
    cover_image: str = ""
    gallery: list[str] = field(default_factory=list)
    image_count: int = 0
    video_available: bool = False
