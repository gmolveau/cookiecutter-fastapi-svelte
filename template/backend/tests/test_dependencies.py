"""Unit tests for the session read path: ``get_current_user_from_session``."""

import pytest
from fastapi import HTTPException

from src.dependencies import get_current_user, get_current_user_from_session
from src.services.api_keys import create_api_key


class _FakeRequest:
    """Minimal stand-in exposing a plain-dict ``.session`` and ``.headers``."""

    def __init__(self, session: dict, headers: dict | None = None):
        self.session = session
        self.headers = headers or {}


def test_valid_session_returns_live_user(db, make_user):
    user = make_user(sub="abc-123")
    request = _FakeRequest({"user": {"sub": "abc-123"}})
    result = get_current_user_from_session(request, db)  # ty:ignore[invalid-argument-type]
    assert result.id == user.id
    assert result.sub == "abc-123"


def test_empty_session_raises_401(db):
    request = _FakeRequest({})
    with pytest.raises(HTTPException) as exc:
        get_current_user_from_session(request, db)  # ty:ignore[invalid-argument-type]
    assert exc.value.status_code == 401


def test_missing_user_key_raises_401(db):
    request = _FakeRequest({"something": "else"})
    with pytest.raises(HTTPException) as exc:
        get_current_user_from_session(request, db)  # ty:ignore[invalid-argument-type]
    assert exc.value.status_code == 401


def test_unknown_sub_raises_401(db, make_user):
    make_user(sub="known")
    request = _FakeRequest({"user": {"sub": "does-not-exist"}})
    with pytest.raises(HTTPException) as exc:
        get_current_user_from_session(request, db)  # ty:ignore[invalid-argument-type]
    assert exc.value.status_code == 401


# --- get_current_user: Request-adapter regression locks --------------------
def test_get_current_user_valid_bearer_returns_owner(db, make_user):
    user = make_user()
    _, raw_key = create_api_key(db, user, name="t", expires_at=None)
    request = _FakeRequest({}, {"Authorization": f"Bearer {raw_key}"})
    result = get_current_user(request, db)  # ty:ignore[invalid-argument-type]
    assert result.id == user.id


def test_get_current_user_invalid_bearer_raises_401(db):
    request = _FakeRequest({}, {"Authorization": "Bearer mafsk_nope"})
    with pytest.raises(HTTPException) as exc:
        get_current_user(request, db)  # ty:ignore[invalid-argument-type]
    assert exc.value.status_code == 401


def test_get_current_user_no_header_valid_session(db, make_user):
    user = make_user(sub="session-sub")
    request = _FakeRequest({"user": {"sub": "session-sub"}})
    result = get_current_user(request, db)  # ty:ignore[invalid-argument-type]
    assert result.id == user.id


def test_get_current_user_no_header_stale_session_clears_and_raises(db):
    request = _FakeRequest({"user": {"sub": "ghost"}})
    with pytest.raises(HTTPException) as exc:
        get_current_user(request, db)  # ty:ignore[invalid-argument-type]
    assert exc.value.status_code == 401
    assert request.session == {}
