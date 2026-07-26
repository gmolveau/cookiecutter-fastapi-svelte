"""Shared pytest fixtures and test harness bootstrap.

Environment variables MUST be set before anything from ``src`` is imported:
``src.config`` calls ``sys.exit(1)`` on missing vars and several modules
(``src.web``, ``src.storage``) read ``os.environ`` at import time.
"""

import os
import tempfile

# --- Environment bootstrap (must run before any ``src`` import) --------------
_TMP_STORAGE = tempfile.mkdtemp(prefix="test-storage-")

os.environ.update(
    {
        # Auth OIDC
        "OIDC_CLIENT_ID": "test-client-id",
        "OIDC_CLIENT_SECRET": "test-client-secret",  # noqa: S105 (test dummy)
        "OIDC_AUTHORIZE_URL": "https://oidc.test/authorize",
        "OIDC_ACCESS_TOKEN_URL": "https://oidc.test/token",
        "OIDC_JWT_URL": "https://oidc.test/jwks",
        "OIDC_REQUIRE_EMAIL_VERIFIED": "false",
        # Session
        "SESSION_SECRET_KEY": "test-session-secret-key",  # noqa: S105 (test dummy)
        "SESSION_COOKIE_MAX_AGE": "3600",
        # Environment
        "APP_ENV": "dev",
        # Rate limiting
        "RATE_LIMIT": "1000/minute",
        # Logging
        "LOG_LEVEL": "INFO",
        # OpenTelemetry stays disabled in tests
        "OTEL_ENABLED": "false",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://otel.test:4318",
        # web.py middleware
        "ALLOWED_HOSTS": "*",
        "ALLOWED_ORIGINS": "http://localhost",
        # storage
        "STORAGE_LOCAL_PATH": _TMP_STORAGE,
        # database (overridden via fixture, but must be importable)
        "DATABASE_URL": "sqlite://",
    }
)

# --- Imports (safe now that the environment is populated) --------------------
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from src.database import get_db  # noqa: E402
from src.models import BaseModel, Group, Role, User  # noqa: E402


@pytest.fixture(scope="session")
def engine():
    """In-memory SQLite engine shared across connections."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    BaseModel.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine):
    """A fresh database session with all tables truncated between tests."""
    connection = engine.connect()
    transaction = connection.begin()
    TestSession = sessionmaker(
        bind=connection,
        expire_on_commit=False,
        autoflush=True,
    )
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def app(db):
    """Build the FastAPI app with ``get_db`` overridden to the test session."""
    from src.web import create_app

    application = create_app()

    def _override_get_db():
        yield db

    application.dependency_overrides[get_db] = _override_get_db
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """TestClient bound to the app with the test DB override."""
    with TestClient(app) as test_client:
        yield test_client


# --- Factory helpers ---------------------------------------------------------
@pytest.fixture
def make_role(db: Session):
    def _make_role(name: str) -> Role:
        role = Role(name=name)
        db.add(role)
        db.commit()
        return role

    return _make_role


@pytest.fixture
def make_group(db: Session):
    def _make_group(name: str, role: Role | None = None) -> Group:
        group = Group(name=name, role=role)
        db.add(group)
        db.commit()
        return group

    return _make_group


@pytest.fixture
def make_user(db: Session):
    _counter = {"n": 0}

    def _make_user(
        *,
        sub: str | None = None,
        name: str = "Test User",
        email: str | None = None,
        role: Role | None = None,
        groups: list[Group] | None = None,
    ) -> User:
        _counter["n"] += 1
        n = _counter["n"]
        user = User(
            sub=sub or f"sub-{n}",
            name=name,
            email=email or f"user{n}@test.local",
            role=role,
            groups=groups or [],
        )
        db.add(user)
        db.commit()
        return user

    return _make_user
