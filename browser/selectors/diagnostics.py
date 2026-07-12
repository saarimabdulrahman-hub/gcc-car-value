"""Selector diagnostics — execution report, failure analysis."""

from browser.selectors.models import Selector, SelectorExecutionResult, SelectorDiagnostics


class SelectorDiagnosticsEngine:
    """Generate diagnostic reports for selector execution."""

    def diagnose(self, selector: Selector,
                 result: SelectorExecutionResult,
                 validation_errors: list[str] | None = None) -> SelectorDiagnostics:
        return SelectorDiagnostics(
            selector=selector,
            result=result,
            all_tried=selector.all_selectors,
            validation_errors=validation_errors or [],
        )

    def summary(self, diag: SelectorDiagnostics) -> str:
        """Human-readable diagnostic summary."""
        if diag.result is None:
            return "No execution result available"

        r = diag.result
        if r.matched:
            msg = f"✓ {r.selector_name}: matched '{r.matched_selector}'"
            if r.fallback_used:
                msg += f" (fallback #{r.fallback_index})"
            msg += f" → '{r.value[:80]}' in {r.execution_time_ms:.1f}ms"
            return msg
        else:
            return (f"✗ {r.selector_name}: no match. "
                    f"Tried: {diag.all_tried}. Error: {r.error}")
