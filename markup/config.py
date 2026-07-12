from dataclasses import dataclass, field

@dataclass
class HTMLConfig:
    remove_scripts: bool = True
    remove_styles: bool = True
    remove_comments: bool = True
    normalize_whitespace: bool = True
    detect_hidden: bool = True
    extract_metadata: bool = True
    parser: str = "lxml"            # lxml | html.parser | html5lib
    max_size_bytes: int = 5_000_000  # 5 MB
