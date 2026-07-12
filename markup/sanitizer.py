"""HTML Sanitizer — re-exports cleaner + whitespace for dedicated sanitization."""

from markup.cleaner import HTMLCleaner
from markup.whitespace import WhitespaceNormalizer

__all__ = ["HTMLCleaner", "WhitespaceNormalizer"]
