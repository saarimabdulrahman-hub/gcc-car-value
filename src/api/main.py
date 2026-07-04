from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api.dependencies import limiter
from src.api.routes import health, valuation, models, admin
from src.observability.logging import setup_logging
from src.config import get_settings

settings = get_settings()
setup_logging()


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
