"""Selector Compiler — validates, compiles, and executes selectors against DOM documents."""

import time
import re
from browser.selectors.models import Selector, SelectorExecutionResult
from browser.selectors.errors import SelectorCompilationError


class SelectorCompiler:
    """Compiles a Selector into an execution plan and runs it against a DOMDocument.

    Usage:
        compiler = SelectorCompiler()
        result = compiler.execute(selector, doc)
        if result.matched:
            print(result.value)
    """

    def validate(self, selector: Selector) -> list[str]:
        """Validate a selector definition. Returns list of errors."""
        errors = []
        if not selector.name:
            errors.append("Selector name is required")
        if not selector.css:
            errors.append("Primary CSS selector is required")
        if not selector.marketplace:
            errors.append("Marketplace is required")
        if not selector.group:
            errors.append("Group is required")

        # Validate CSS syntax (basic check — doesn't require a DOM)
        for i, css in enumerate(selector.all_selectors):
            if not css.strip():
                errors.append(f"Selector {i} ('{css}') is empty")
                continue
            # Basic CSS sanity: should not contain unmatched brackets
            if css.count('(') != css.count(')'):
                errors.append(f"Selector '{css}' has mismatched parentheses")
            if css.count('[') != css.count(']'):
                errors.append(f"Selector '{css}' has mismatched brackets")

        max_fallbacks = 5
        if len(selector.fallbacks) > max_fallbacks:
            errors.append(f"Too many fallbacks ({len(selector.fallbacks)}), max {max_fallbacks}")

        return errors

    def execute(self, selector: Selector, doc,
                extractor=None) -> SelectorExecutionResult:
        """Execute a selector against a DOM document.

        Tries the primary CSS selector first, then each fallback in order.
        Returns the first successful match with extracted value.
        """
        start = time.perf_counter()
        result = SelectorExecutionResult(
            selector_id=selector.selector_id,
            selector_name=selector.name,
        )

        for i, css in enumerate(selector.all_selectors):
            node = doc.select_one(css)
            if node is not None:
                result.matched = True
                result.matched_selector = css
                result.fallback_used = i > 0
                result.fallback_index = i
                result.nodes_found = 1

                # Extract value based on selector type
                if extractor is not None:
                    extracted = self._extract(node, selector, extractor)
                    result.value = str(extracted.value) if extracted.success else ""
                else:
                    result.value = node.text_stripped
                break

        result.execution_time_ms = (time.perf_counter() - start) * 1000
        if not result.matched:
            result.error = f"No selector matched: tried {selector.all_selectors}"

        return result

    def _extract(self, node, selector: Selector, extractor):
        """Extract value from node based on selector_type."""
        if selector.selector_type == "text":
            return extractor.text(node, field=selector.name)
        if selector.selector_type == "integer":
            return extractor.integer(node, field=selector.name)
        if selector.selector_type == "currency":
            return extractor.currency(node, field=selector.name)
        if selector.selector_type == "year":
            return extractor.year(node, field=selector.name)
        if selector.selector_type == "float":
            return extractor.float_val(node, field=selector.name)
        if selector.selector_type == "url":
            return extractor.url(node, field=selector.name)
        if selector.selector_type == "attribute":
            val = node.attr(selector.attribute_name) if selector.attribute_name else node.text_stripped
            from browser.dom.models import ExtractionResult
            return ExtractionResult(success=bool(val), value=val or "",
                                  field_name=selector.name)
        return extractor.text(node, field=selector.name)
