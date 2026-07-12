"""DOM engine interfaces for future parser backends."""

from abc import ABC, abstractmethod


class DOMParser(ABC):
    """Abstract DOM parser. Future backends implement this."""
    @abstractmethod
    def parse(self, html: str) -> "DOMDocument": ...
