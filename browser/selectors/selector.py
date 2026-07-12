"""Selector — re-export with factory helpers."""

from browser.selectors.models import Selector
from browser.selectors.group import create_selector

__all__ = ["Selector", "create_selector"]
