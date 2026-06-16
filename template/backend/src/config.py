"""Application settings loaded from environment variables."""

import sys
from functools import lru_cache
from typing import Annotated

from pydantic import ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode


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
    APP_VERSION: str = "dev"

    # Rate limiting (slowapi format: "N/second|minute|hour|day")
    RATE_LIMIT: str

    # Logging
    LOG_LEVEL: str

    # Database
    DATABASE_URL: str = "sqlite:///./data/sqlite.db"

    # HTTP hosts / origins (comma-separated in env)
    ALLOWED_HOSTS: Annotated[list[str], NoDecode]
    ALLOWED_ORIGINS: Annotated[list[str], NoDecode]

    # Storage
    STORAGE_DRIVER: str = "local"
    STORAGE_LOCAL_PATH: str | None = None
    STORAGE_S3_BUCKET: str | None = None
    STORAGE_S3_REGION: str | None = None
    STORAGE_S3_PREFIX: str = ""
    STORAGE_S3_ENDPOINT_URL: str | None = None
    STORAGE_S3_ACCESS_KEY_ID: str | None = None
    STORAGE_S3_SECRET_ACCESS_KEY: str | None = None

    # OpenTelemetry
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "[[ project_slug ]]"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""

    @field_validator("ALLOWED_HOSTS", "ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [s.strip() for s in value.split(",") if s.strip()]
        return value

    @model_validator(mode="after")
    def _validate_dependencies(self) -> "Settings":
        driver = self.STORAGE_DRIVER.lower()
        if driver == "local" and not self.STORAGE_LOCAL_PATH:
            raise ValueError("STORAGE_LOCAL_PATH is required when STORAGE_DRIVER=local")
        if driver == "s3" and not (self.STORAGE_S3_BUCKET and self.STORAGE_S3_REGION):
            raise ValueError(
                "STORAGE_S3_BUCKET and STORAGE_S3_REGION are required when"
                " STORAGE_DRIVER=s3"
            )
        if self.OTEL_ENABLED and not self.OTEL_EXPORTER_OTLP_ENDPOINT:
            raise ValueError(
                "OTEL_EXPORTER_OTLP_ENDPOINT is required when OTEL_ENABLED=true"
            )
        return self


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
