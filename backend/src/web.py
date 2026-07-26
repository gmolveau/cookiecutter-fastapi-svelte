"""FastAPI application factory."""

import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from src.config import get_settings
from src.database import database_engine
from src.limiter import limiter
from src.logging_setup import setup_logging
from src.otel_setup import setup_otel
from src.routes.api_keys import router as api_keys_router
from src.routes.auth import router as auth_router
from src.routes.health import router as health_router
from src.storage import active_disk
from src.storage.local import LocalDisk

logger = structlog.get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=str(uuid.uuid4()),
            method=request.method,
            path=request.url.path,
        )
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup")
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(dev=settings.APP_ENV == "dev", log_level=settings.LOG_LEVEL)

    app: FastAPI = FastAPI(title="MyApp API", lifespan=lifespan)

    app.add_middleware(RequestContextMiddleware)

    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,  # ty:ignore[invalid-argument-type]
    )
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SESSION_SECRET_KEY,
        max_age=settings.SESSION_COOKIE_MAX_AGE,
    )

    app.add_middleware(
        middleware_class=TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

    # Must be outermost: patches request scheme from X-Forwarded-Proto (set by Traefik)
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.OTEL_ENABLED:
        setup_otel(
            app,
            database_engine,
            service_name=settings.OTEL_SERVICE_NAME,
            otlp_endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
        )

    app.mount(
        path="/api/static",
        app=StaticFiles(directory="static"),
        name="static",
    )

    if isinstance(active_disk, LocalDisk):
        active_disk.ensure()
        app.mount(
            path="/api/files",
            app=StaticFiles(directory=active_disk.root),
            name="files",
        )

    api_router = APIRouter(prefix="/api")
    api_router.include_router(router=auth_router)
    api_router.include_router(router=health_router)
    api_router.include_router(router=api_keys_router)
    app.include_router(api_router)

    return app


app = create_app()
