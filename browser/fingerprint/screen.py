"""Screen profile catalog — curated desktop/laptop resolutions."""

# Curated screen profiles (width, height, dpr, description)
SCREEN_PROFILES = [
    (1920, 1080, 1.0, "Desktop 1080p"),
    (2560, 1440, 1.0, "Desktop 1440p (QHD)"),
    (1680, 1050, 2.0, "MacBook Pro 16\" Retina"),
    (1728, 1117, 2.0, "MacBook Pro 14\" Retina"),
    (1440, 900, 2.0, "MacBook Air 13\" Retina"),
    (3840, 2160, 1.0, "Desktop 4K"),
    (1366, 768, 1.0, "Laptop HD"),
    (1536, 864, 1.0, "Laptop HD+"),
]


def screen_for_resolution(width: int, height: int) -> dict | None:
    """Find a matching screen profile."""
    for w, h, dpr, desc in SCREEN_PROFILES:
        if w == width and h == height:
            return {"width": w, "height": h, "dpr": dpr, "description": desc}
    return None
