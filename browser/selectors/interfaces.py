"""Selector interfaces for future extension."""

from abc import ABC, abstractmethod
from browser.selectors.models import Selector, SelectorExecutionResult


class SelectorExecutor(ABC):
    """Abstract selector executor. Future: XPath, JS evaluation, etc."""
    @abstractmethod
    def execute(self, selector: Selector, doc) -> SelectorExecutionResult: ...
