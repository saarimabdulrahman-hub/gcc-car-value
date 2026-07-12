from dataclasses import dataclass

@dataclass
class DOMConfig:
    parser: str = "lxml"  # lxml | html.parser | html5lib
    trim_whitespace: bool = True
    max_text_length: int = 10000
    strict_validation: bool = False
