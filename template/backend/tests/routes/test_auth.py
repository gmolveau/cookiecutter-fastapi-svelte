"""Regression tests against the TARGET design of ``GET /api/auth/me``.

Target: ``/auth/me`` depends on ``get_current_user_from_session`` (which
re-fetches the live ``User`` by ``sub``) and returns
``{"name": user.name, "role": get_effective_role(user)}`` derived LIVE.

These tests authenticate by overriding that dependency. The CURRENT ``me()``
ignores the dependency and reads ``request.session`` directly, so it returns
401 here (no session cookie) -> these are the intended behavioral RED.
"""

from src.dependencies import get_current_user_from_session
from src.services.users import assign_role_to_user


def _authenticate_as(app, user):
    """Override the session dependency so it yields ``user`` as authenticated."""
    app.dependency_overrides[get_current_user_from_session] = lambda: user


def test_me_returns_name_and_live_role(client, app, make_user, make_role):
    role = make_role("editor")
    user = make_user(name="Alice", role=role)
    _authenticate_as(app, user)

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"name": "Alice", "role": "editor"}


def test_me_returns_none_role_when_no_role(client, app, make_user):
    user = make_user(name="Bob")
    _authenticate_as(app, user)

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert response.json() == {"name": "Bob", "role": None}


def test_me_reflects_role_change_without_relogin(client, app, db, make_user, make_role):
    """A role promotion must be visible on the next ``/auth/me`` with no re-login."""
    make_role("admin")
    user = make_user(name="Carol", sub="carol-sub")
    _authenticate_as(app, user)

    first = client.get("/api/auth/me")
    assert first.status_code == 200
    assert first.json() == {"name": "Carol", "role": None}

    # Promote the SAME user, no new session / no re-login.
    assign_role_to_user(db, role_name="admin", sub="carol-sub")

    second = client.get("/api/auth/me")
    assert second.status_code == 200
    assert second.json() == {"name": "Carol", "role": "admin"}


def test_me_unauthenticated_returns_401(client):
    """No dependency override and no session cookie -> 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
