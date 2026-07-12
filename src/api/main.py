from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api.dependencies import limiter
from src.api.routes import health, valuation, models, admin, url_valuate, metrics
from src.observability.logging import setup_logging
from src.core.context.middleware import CorrelationMiddleware
from src.config import get_settings
import time, os, sys

settings = get_settings()
setup_logging()

# ------------------------------------------------------------------
# Auto-register application lifecycle metrics
# ------------------------------------------------------------------
from src.core.metrics import Metrics

_start_time = time.time()

Metrics.info("app.version", "Application version").set_info(
    version=settings.api_version)
Metrics.info("app.environment", "Deployment environment").set_info(
    environment=settings.environment)
Metrics.info("app.runtime", "Python runtime info").set_info(
    python_version=sys.version.split()[0])
Metrics.gauge("app.uptime_seconds", "Process uptime in seconds")

# Set initial uptime (updated on each /metrics scrape via the gauge)
Metrics.set_gauge("app.uptime_seconds", 0.0)

def _update_uptime() -> None:
    """Update the uptime gauge before each /metrics scrape."""
    try:
        Metrics.set_gauge("app.uptime_seconds", time.time() - _start_time)
    except Exception:
        pass  # Never let metrics collection break the app

UI_DIR = Path(__file__).resolve().parent.parent.parent / "ui"


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation middleware — must run before all route handlers
app.add_middleware(CorrelationMiddleware)

# HTTP tracing middleware — auto-creates root spans (no-op when OTel disabled)
from src.core.tracing.instrumentation.http import HTTPInstrumentation
app.add_middleware(HTTPInstrumentation)

app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(valuation.router, prefix="/v1", tags=["valuation"])
app.include_router(models.router, prefix="/v1", tags=["models"])
app.include_router(admin.router, prefix="/v1", tags=["admin"])
app.include_router(url_valuate.router, prefix="/v1", tags=["url-valuate"])
app.include_router(metrics.router, tags=["metrics"])

# Serve UI directly from route — zero caching
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    ui_file = UI_DIR / "index.html"
    if ui_file.exists():
        content = ui_file.read_text(encoding="utf-8")
        return HTMLResponse(content=content, headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        })
    return HTMLResponse(content="<h1>UI not found</h1>", status_code=404)

# Serve other static files (test.html, previews, etc.)
if UI_DIR.exists():
    app.mount("/", StaticFiles(directory=str(UI_DIR), html=True), name="ui")
