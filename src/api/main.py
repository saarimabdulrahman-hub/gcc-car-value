import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.api.dependencies import limiter
from src.api.routes import (
    admin,
    auth,
    health,
    metrics,
    models,
    notifications,
    url_valuate,
    valuation,
    watchlist,
)
from src.config import get_settings
from src.core.context.middleware import CorrelationMiddleware
from src.observability.logging import setup_logging

settings = get_settings()
setup_logging()

# ------------------------------------------------------------------
# Auto-register application lifecycle metrics
# ------------------------------------------------------------------
from src.core.metrics import Metrics

_start_time = time.time()

try:
    Metrics.info("app.version", "Application version").set_info(
        version=settings.api_version)
    Metrics.info("app.environment", "Deployment environment").set_info(
        environment=settings.environment)
    Metrics.info("app.runtime", "Python runtime info").set_info(
        python_version=sys.version.split()[0])
    Metrics.gauge("app.uptime_seconds", "Process uptime in seconds")
    Metrics.set_gauge("app.uptime_seconds", 0.0)
except Exception:
    pass  # Metrics already registered (reload-safe)

def _update_uptime() -> None:
    """Update the uptime gauge before each /metrics scrape."""
    try:
        Metrics.set_gauge("app.uptime_seconds", time.time() - _start_time)
    except Exception:
        pass  # Never let metrics collection break the app

UI_DIR = Path(__file__).resolve().parent.parent.parent / "ui"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail fast on insecure/missing configuration before accepting traffic.
    # Enforced only in deployed environments; dev/testing use fixture secrets
    # that intentionally don't meet production strength rules.
    if settings.environment in ("production", "staging"):
        from src.config.startup import validate_startup
        await validate_startup()
    # Initialize tracing if enabled (no-op when OTEL_ENABLED=false)
    try:
        from src.core.tracing import init_tracing
        init_tracing()
    except Exception:
        pass

    yield
    # Graceful shutdown: drain connections, flush telemetry
    from src.db.session import engine
    await engine.dispose()
    try:
        from src.core.tracing.provider import shutdown_tracing
        shutdown_tracing()
    except Exception:
        pass


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    lifespan=lifespan,
    request_max_size=1_048_576,  # 1 MB — prevents OOM from oversized payloads
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_credentials=settings.api_cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# Security headers — applied to every response. HSTS is only meaningful over
# HTTPS, so it is emitted only in deployed environments (behind TLS).
_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "img-src 'self' data: https:; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self' 'unsafe-inline'; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    ),
}
_IS_DEPLOYED = settings.environment in ("production", "staging")


@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    for key, value in _SECURITY_HEADERS.items():
        response.headers.setdefault(key, value)
    if _IS_DEPLOYED:
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    return response

# Correlation middleware — must run before all route handlers
app.add_middleware(CorrelationMiddleware)

# HTTP tracing middleware — auto-creates root spans (no-op when OTel disabled)
try:
    from src.core.tracing.instrumentation.http import HTTPInstrumentation
except ImportError:
    HTTPInstrumentation = None
if HTTPInstrumentation is not None:
    app.add_middleware(HTTPInstrumentation)

app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(valuation.router, prefix="/v1", tags=["valuation"])
app.include_router(models.router, prefix="/v1", tags=["models"])
app.include_router(admin.router, prefix="/v1", tags=["admin"])
app.include_router(url_valuate.router, prefix="/v1", tags=["url-valuate"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(auth.router, prefix="/v1", tags=["auth"])
app.include_router(notifications.router, prefix="/v1", tags=["notifications"])
app.include_router(watchlist.router, prefix="/v1", tags=["watchlist"])

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
class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
        return response


if UI_DIR.exists():
    app.mount("/", NoCacheStaticFiles(directory=str(UI_DIR), html=True), name="ui")
