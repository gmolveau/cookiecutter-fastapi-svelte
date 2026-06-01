"""Application settings loaded from environment variables."""

import sys
from functools import lru_cache

from pydantic import ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Auth OIDC
    OIDC_CLIENT_ID: str
    OIDC_CLIENT_SECRET: str
    OIDC_AUTHORIZE_URL: str
    OIDC_ACCESS_TOKEN_URL: str
    OIDC_JWT_URL: str
    OIDC_REQUIRE_EMAIL_VERIFIED: bool

    # Session
    SESSION_SECRET_KEY: str
    SESSION_COOKIE_MAX_AGE: int

    # Environment
    APP_ENV: str

    # Rate limiting (slowapi format: "N/second|minute|hour|day")
    RATE_LIMIT: str

    # Logging
    LOG_LEVEL: str

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "[[ project_slug ]]"
    OTEL_EXPORTER_OTLP_ENDPOINT: str


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()  # ty:ignore[missing-argument]
    except ValidationError as e:
        missing = [err["loc"][0] for err in e.errors() if err["type"] == "missing"]
        if missing:
            print(
                f"Missing required environment variables:"
                f" {', '.join(str(v) for v in missing)}",
                file=sys.stderr,
            )
        else:
            print(f"Invalid configuration:\n{e}", file=sys.stderr)
        sys.exit(1)
