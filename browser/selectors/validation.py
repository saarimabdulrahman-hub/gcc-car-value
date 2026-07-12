"""Selector validation rules."""

from browser.selectors.models import Selector


class SelectorValidator:
    """Validate selector definitions."""

    @staticmethod
    def validate(selector: Selector) -> list[str]:
        errors = []
        if not selector.name:
            errors.append("name is required")
        if not selector.css:
            errors.append("css is required")
        if not selector.marketplace:
            errors.append("marketplace is required")
        if not selector.group:
            errors.append("group is required")

        # Check for self-referential fallback (a fallback can't reference itself)
        if selector.css in selector.fallbacks:
            errors.append("Primary selector cannot be in its own fallback list")

        # Check for duplicate fallbacks
        if len(selector.fallbacks) != len(set(selector.fallbacks)):
            errors.append("Duplicate fallback selectors")

        return errors

    @staticmethod
    def validate_batch(selectors: list[Selector]) -> dict[str, list[str]]:
        """Validate multiple selectors. Returns {name: errors}."""
        results = {}
        for s in selectors:
            errs = SelectorValidator.validate(s)
            if errs:
                results[s.name] = errs
        return results
