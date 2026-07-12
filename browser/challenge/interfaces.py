"""Challenge detection interfaces for future extensions."""

from abc import ABC, abstractmethod
from browser.challenge.models import Challenge


class ChallengeDetectorInterface(ABC):
    """Abstract challenge detector. Implement for custom detection logic."""
    @abstractmethod
    def detect(self, html: str, title: str, url: str,
               http_status: int) -> Challenge | None: ...
