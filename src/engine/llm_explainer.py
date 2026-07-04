"""LLM valuation explanation — translates structured data into natural language.

Uses Claude API when available, falls back to template-based explanations.
API key configured via CLAUDE_API_KEY env var.
"""
from dataclasses import dataclass
from src.config import get_settings

settings = get_settings()


@dataclass
class ValuationContext:
    make: str
    model: str
    year: int
    mileage_km: int | None
    spec: str | None
    city: str | None
    estimate: float
    price_low: float
    price_high: float
    confidence: str
    comp_count: int
    adjustments: list[dict]
    knowledge: dict | None = None


def explain_valuation(ctx: ValuationContext) -> str:
    """Generate a natural-language explanation of a valuation.

    Uses Claude API if CLAUDE_API_KEY is set, otherwise uses templates.
    """
    api_key = getattr(settings, 'claude_api_key', None)

    if api_key:
        return _explain_with_claude(ctx, api_key)
    return _explain_with_template(ctx)


def _explain_with_template(ctx: ValuationContext) -> str:
    """Template-based explanation — no API call needed."""

    parts = [
        f"A {ctx.year} {ctx.make} {ctx.model}",
        f"with {ctx.mileage_km:,} km" if ctx.mileage_km else "",
        f"({ctx.spec} spec)" if ctx.spec else "",
        f"in {ctx.city}" if ctx.city else "",
    ]
    header = " ".join(p for p in parts if p)

    body = (
        f"has an estimated fair market value of {ctx.estimate:,.0f} AED, "
        f"with a typical range of {ctx.price_low:,.0f} to {ctx.price_high:,.0f} AED. "
    )

    if ctx.confidence == "high":
        body += (
            f"This estimate is based on {ctx.comp_count} comparable listings "
            f"currently active in the market, giving us high confidence in this valuation."
        )
    elif ctx.confidence == "medium":
        body += (
            f"This estimate is based on {ctx.comp_count} comparable listings. "
            f"More listings would increase our confidence."
        )
    else:
        body += (
            f"Only {ctx.comp_count} comparable listings were found, so this estimate "
            f"should be used as a general guide rather than a precise valuation."
        )

    # Adjustment explanations
    if ctx.adjustments:
        body += " Key factors affecting this price: "
        adj_texts = []
        for adj in ctx.adjustments:
            adj_texts.append(adj.get("detail", f"{adj.get('reason')}: {adj.get('amount'):+,.0f} AED"))
        body += ". ".join(adj_texts) + "."

    # Knowledge base insights
    if ctx.knowledge:
        if ctx.knowledge.get("known_issues"):
            body += f" Note: This model has {len(ctx.knowledge['known_issues'])} known issues to watch for. "
        if ctx.knowledge.get("annual_maintenance_estimate"):
            body += f"Annual maintenance is estimated at {ctx.knowledge['annual_maintenance_estimate']}. "
        if ctx.knowledge.get("market_liquidity"):
            body += f"Similar cars typically sell within {ctx.knowledge['market_liquidity']}. "

    return header + " " + body


def _explain_with_claude(ctx: ValuationContext, api_key: str) -> str:
    """Use Claude API for a more natural explanation. Falls back to template on error."""
    try:
        import httpx
        import json

        prompt = _build_claude_prompt(ctx)
        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=15,
        )
        if response.status_code == 200:
            data = response.json()
            return data["content"][0]["text"]
    except Exception:
        pass

    return _explain_with_template(ctx)


def _build_claude_prompt(ctx: ValuationContext) -> str:
    return (
        f"Explain this car valuation in 3-4 sentences for a consumer audience. "
        f"Car: {ctx.year} {ctx.make} {ctx.model}, {ctx.mileage_km}km, {ctx.spec or 'unknown'} spec, "
        f"in {ctx.city or 'GCC'}. "
        f"Estimated value: {ctx.estimate:,.0f} AED (range: {ctx.price_low:,.0f}-{ctx.price_high:,.0f}). "
        f"Confidence: {ctx.confidence} based on {ctx.comp_count} comparable listings. "
        + ("Adjustments: " + "; ".join(
            a.get("detail", "") for a in ctx.adjustments
        ) if ctx.adjustments else "")
    )
