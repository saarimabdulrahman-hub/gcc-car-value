from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from fastapi import Response

valuation_requests = Counter(
    "valuation_requests_total", "Total valuation requests", ["tier", "confidence"]
)
valuation_duration = Histogram(
    "valuation_duration_seconds", "Valuation request duration",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)
scraper_runs = Counter(
    "scraper_runs_total", "Total scraper runs", ["source", "status"]
)
scraper_listings_ingested = Counter(
    "scraper_listings_ingested_total", "Total listings ingested", ["source"]
)
data_freshness_hours = Gauge(
    "data_freshness_hours", "Hours since last successful scrape", ["source"]
)


def metrics_endpoint() -> Response:
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")
