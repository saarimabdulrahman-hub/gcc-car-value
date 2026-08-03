# Scraper Status — JS rendering assessment

| Source | Needs JS | Evidence |
|--------|----------|----------|
| Dubizzle UAE | **Yes** | 1169-byte response; no `__NEXT_DATA__`, no prices, no listing links in raw HTML. Next.js SPA. |
| YallaMotor | **Yes** | 5393-byte response; no prices or listing links in raw HTML. Client-rendered. |
| Haraj KSA | **Yes** | 9551-byte response; no prices or listing links in raw HTML. Client-rendered. |

**Recommendation:** All three sources require a JS-capable fetch layer (e.g., `crawl4ai` / Playwright). Do not install until P0-2 is validated with seeded data.
