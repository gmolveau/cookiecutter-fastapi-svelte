"""FastAPI application factory."""

import os
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from src.config import get_settings
from src.database import database_engine
from src.logging_setup import setup_logging
from src.otel_setup import setup_otel
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
    active_disk.ensure()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(dev=settings.APP_ENV == "dev", log_level=settings.LOG_LEVEL)

    app: FastAPI = FastAPI(title="[[ project_name ]] API", lifespan=lifespan)

    app.add_middleware(RequestContextMiddleware)

    limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])
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

    allowed_hosts: list[str] = os.environ["ALLOWED_HOSTS"].split(sep=",")
    app.add_middleware(
        middleware_class=TrustedHostMiddleware, allowed_hosts=allowed_hosts
    )

    allowed_origins: list[str] = os.environ["ALLOWED_ORIGINS"].split(sep=",")
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=allowed_origins,
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

    if isinstance(active_disk, LocalDisk):
        app.mount(
            path="/api/static", app=StaticFiles(directory="static"), name="static"
        )

    api_router = APIRouter(prefix="/api")
    api_router.include_router(router=auth_router)
    api_router.include_router(router=health_router)
    app.include_router(api_router)

    return app


app = create_app()
