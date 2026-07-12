from dataclasses import dataclass, field

@dataclass
class SelectorConfig:
    max_fallbacks: int = 5
    strict_validation: bool = True
    cache_compiled_selectors: bool = True
