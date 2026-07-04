from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api.dependencies import limiter
from src.api.routes import health, valuation, models, admin, url_valuate
from src.observability.logging import setup_logging
from src.config import get_settings

settings = get_settings()
setup_logging()

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

app.include_router(health.router, prefix="/v1", tags=["health"])
app.include_router(valuation.router, prefix="/v1", tags=["valuation"])
app.include_router(models.router, prefix="/v1", tags=["models"])
app.include_router(admin.router, prefix="/v1", tags=["admin"])
app.include_router(url_valuate.router, prefix="/v1", tags=["url-valuate"])

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
