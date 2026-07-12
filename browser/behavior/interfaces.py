"""Behaviour interfaces for future extensions."""

from abc import ABC, abstractmethod


class InteractionController(ABC):
    """Abstract interaction controller. Each behaviour module implements this."""

    @abstractmethod
    def delay_ms(self) -> float:
        """Return the delay in milliseconds for this interaction."""
        ...
