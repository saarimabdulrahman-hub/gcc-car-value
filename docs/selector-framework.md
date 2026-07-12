# GCC Car Value — Selector Framework

**Date:** 2026-07-12  
**Package:** `browser/selectors/`

## Architecture

```
Marketplace Scraper
    │
    ▼
SelectorRegistry.get(marketplace, name) → Selector
    │
    ▼
SelectorCompiler.execute(selector, doc) → SelectorExecutionResult
    │
    ├── Try primary CSS → match? → extract value
    ├── Try fallback[0]  → match? → extract value
    ├── Try fallback[1]  → match? → extract value
    └── No match → result.error
    │
    ▼
SelectorDiagnosticsEngine.diagnose(selector, result) → summary
```

## Selector Model

```python
Selector(
    name="listing.title",
    css="h1.title",                     # Primary
    fallbacks=["[class*='title']", "h1"],  # Fallbacks
    required=True,
    selector_type="text",               # text | integer | currency | year | url | attribute
    marketplace="dubizzle_uae",
    group="title",
    version=1,
)
```

## Registry

```python
reg = SelectorRegistry()
await reg.register(Selector(name="listing.price", css=".price", marketplace="dubizzle", group="price"))
s = await reg.get("dubizzle", "listing.price")
await reg.update(s)  # increments version
```

## Execution

```python
compiler = SelectorCompiler()
result = compiler.execute(selector, doc, extractor=Extractor())
# result.matched → True/False
# result.fallback_used → True if fallback was needed
# result.fallback_index → 0=primary, 1=first fallback
# result.value → extracted text
```

## Selector Groups (14 pre-defined)

`listing`, `price`, `title`, `mileage`, `year`, `fuel`, `transmission`, `seller`, `images`, `location`, `spec`, `body_type`, `description`, `contact`

## Verified

- Registry: register, get, update (version increment), list by marketplace/group, duplicate rejection
- Compiler: primary match, fallback match, no-match, typed extraction (text/currency/year)
- Validation: missing name/css/marketplace/group, mismatched parens, self-referential fallback, duplicate fallbacks
- Versioning: multi-version history, latest version lookup
- Diagnostics: ✓/✗ summaries for matched/unmatched executions

---

*Selector framework documented 2026-07-12.*
