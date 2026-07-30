"""Tests encoding the TARGET consolidated ``Settings`` interface.

These tests describe the configuration surface AFTER all ``os.environ`` reads
have been folded into ``src.config.Settings``. Many of them fail against the
current code on purpose (RED phase of TDD).

Each test constructs ``Settings()`` directly (not the ``lru_cache``d
``get_settings()``) so it reads the live ``os.environ`` the conftest baseline
populates; ``monkeypatch`` overrides only the vars the test cares about.
"""

import pytest
from pydantic import ValidationError

from src.config import Settings


def test_allowed_hosts_parses_comma_separated_string(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", "web.test, api.test")
    settings = Settings()
    hosts = settings.ALLOWED_HOSTS
    assert hosts == ["web.test", "api.test"]


def test_allowed_origins_parses_comma_separated_string(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://web.test, https://api.test")
    settings = Settings()
    origins = settings.ALLOWED_ORIGINS
    assert origins == ["https://web.test", "https://api.test"]


def test_allowed_hosts_strips_and_drops_empties(monkeypatch):
    monkeypatch.setenv("ALLOWED_HOSTS", " a.com ,, b.com , ")
    settings = Settings()
    hosts = settings.ALLOWED_HOSTS
    assert hosts == ["a.com", "b.com"]


def test_database_url_defaults_when_absent(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings()
    database_url = settings.DATABASE_URL
    assert database_url == "sqlite:///./data/sqlite.db"


def test_app_version_defaults_to_dev_when_absent(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    settings = Settings()
    app_version = settings.APP_VERSION
    assert app_version == "dev"


def test_app_version_reflects_env_when_set(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    settings = Settings()
    app_version = settings.APP_VERSION
    assert app_version == "1.2.3"


def test_storage_driver_defaults_to_local(monkeypatch):
    monkeypatch.delenv("STORAGE_DRIVER", raising=False)
    settings = Settings()
    driver = settings.STORAGE_DRIVER
    assert driver == "local"


def test_storage_local_requires_local_path(monkeypatch):
    monkeypatch.setenv("STORAGE_DRIVER", "local")
    monkeypatch.delenv("STORAGE_LOCAL_PATH", raising=False)
    with pytest.raises(ValidationError):
        Settings()


def test_storage_s3_requires_bucket_and_region(monkeypatch):
    monkeypatch.setenv("STORAGE_DRIVER", "s3")
    monkeypatch.delenv("STORAGE_S3_BUCKET", raising=False)
    monkeypatch.delenv("STORAGE_S3_REGION", raising=False)
    with pytest.raises(ValidationError):
        Settings()


def test_storage_s3_optional_endpoint_and_creds(monkeypatch):
    monkeypatch.setenv("STORAGE_DRIVER", "s3")
    monkeypatch.setenv("STORAGE_S3_BUCKET", "my-bucket")
    monkeypatch.setenv("STORAGE_S3_REGION", "eu-west-1")
    monkeypatch.delenv("STORAGE_S3_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("STORAGE_S3_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("STORAGE_S3_SECRET_ACCESS_KEY", raising=False)
    monkeypatch.delenv("STORAGE_S3_PREFIX", raising=False)

    settings = Settings()

    bucket = settings.STORAGE_S3_BUCKET
    region = settings.STORAGE_S3_REGION
    endpoint = settings.STORAGE_S3_ENDPOINT_URL
    access_key = settings.STORAGE_S3_ACCESS_KEY_ID
    secret_key = settings.STORAGE_S3_SECRET_ACCESS_KEY
    prefix = settings.STORAGE_S3_PREFIX
    assert bucket == "my-bucket"
    assert region == "eu-west-1"
    assert endpoint is None
    assert access_key is None
    assert secret_key is None
    assert prefix == ""


def test_otel_disabled_without_endpoint_is_valid(monkeypatch):
    monkeypatch.setenv("OTEL_ENABLED", "false")
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    settings = Settings()
    assert settings.OTEL_ENABLED is False
    assert settings.OTEL_EXPORTER_OTLP_ENDPOINT == ""


def test_otel_enabled_without_endpoint_raises(monkeypatch):
    monkeypatch.setenv("OTEL_ENABLED", "true")
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    with pytest.raises(ValidationError):
        Settings()


def test_otel_enabled_with_endpoint_is_valid(monkeypatch):
    monkeypatch.setenv("OTEL_ENABLED", "true")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel.test:4318")
    settings = Settings()
    assert settings.OTEL_ENABLED is True
    assert settings.OTEL_EXPORTER_OTLP_ENDPOINT == "http://otel.test:4318"


def test_health_endpoint_reports_version_from_settings(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "dev"
