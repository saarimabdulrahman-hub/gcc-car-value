from dataclasses import dataclass

@dataclass
class SchemaConfig:
    current_version: int = 1
    strict_validation: bool = True
    max_image_urls: int = 50
    min_year: int = 1990
