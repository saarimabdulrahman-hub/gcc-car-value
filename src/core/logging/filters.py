"""Logging filters — sensitive data masking for log output.

Automatically masks passwords, tokens, API keys, JWT tokens, and
other secrets before they reach stdout/stderr or external collectors.

Reuses the masking strategy from src.config.secrets.
"""

import re

# Patterns that indicate a value should be fully masked
_MASK_VALUE_PATTERNS = [
    re.compile(r'^eyJ', re.IGNORECASE),      # JWT tokens (base64 header)
    re.compile(r'^sk-'),                      # OpenAI/Claude API keys
    re.compile(r'^gccv_'),                    # Our API keys
    re.compile(r'^AKIA'),                     # AWS access keys
    re.compile(r'^Bearer\s', re.IGNORECASE),  # Authorization headers
    re.compile(r'^Basic\s', re.IGNORECASE),   # Basic auth headers
]

# Field names that should always be masked
_MASK_FIELD_PATTERNS = re.compile(
    r'(password|secret|token|api_key|credential|authorization|'
    r'cookie|private_key|access_key)',
    re.IGNORECASE,
)

MASKED = "***MASKED***"


def mask_field(key: str, value: object) -> object:
    """Mask a log field value if the key or value looks sensitive.

    Returns MASKED for sensitive values, original value otherwise.
    None values pass through unchanged.
    """
    if value is None:
        return None

    # Check if the field name indicates sensitive content
    if _MASK_FIELD_PATTERNS.search(key):
        return MASKED

    # Check if the value looks like a known secret pattern
    value_str = str(value)
    for pattern in _MASK_VALUE_PATTERNS:
        if pattern.search(value_str):
            return MASKED

    # Handle database URLs — mask just the password
    if 'database_url' in key.lower():
        return _mask_db_url_password(value_str)

    return value


def mask_event_dict(event_dict: dict) -> dict:
    """Mask sensitive values in an entire log event dict.

    Called as a structlog processor to sanitize output.
    """
    cleaned = {}
    for key, value in event_dict.items():
        cleaned[key] = mask_field(key, value)
    return cleaned


def _mask_db_url_password(url: str) -> str:
    """Replace password in database URL with ***MASKED***."""
    return re.sub(
        r'(://[^:]+:)([^@]+)(@)',
        r'\1***MASKED***\3',
        url,
    )
