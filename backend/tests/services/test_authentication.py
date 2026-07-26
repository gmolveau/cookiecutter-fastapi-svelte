"""Unit tests for the pure identity resolver ``resolve_user``.

These drive the not-yet-existing ``src.services.authentication`` module
(the RED phase): they encode the bearer-vs-session precedence matrix that
``resolve_user`` must satisfy, decoupled from FastAPI's ``Request``.
"""

from datetime import datetime, timedelta, timezone

import pytest

from src.services.api_keys import create_api_key
from src.services.authentication import NotAuthenticated, resolve_user


def _past_naive_utc() -> datetime:
    """A past datetime matching the naive-UTC convention in services/api_keys."""
    return (datetime.now(timezone.utc) - timedelta(days=1)).replace(tzinfo=None)


def test_valid_bearer_returns_owner(db, make_user):
    user = make_user()
    _, raw_key = create_api_key(db, user, name="t", expires_at=None)
    result = resolve_user(db, bearer_token=raw_key, session_sub=None)
    assert result.id == user.id


def test_unknown_bearer_raises(db):
    with pytest.raises(NotAuthenticated):
        resolve_user(db, bearer_token="mafsk_nope", session_sub=None)


def test_bearer_is_authoritative_over_session(db, make_user):
    user_a = make_user(sub="user-a")
    user_b = make_user(sub="user-b")
    _, raw_key = create_api_key(db, user_a, name="t", expires_at=None)
    result = resolve_user(db, bearer_token=raw_key, session_sub=user_b.sub)
    assert result.id == user_a.id


def test_invalid_bearer_does_not_fall_back_to_session(db, make_user):
    user = make_user(sub="valid-session-sub")
    with pytest.raises(NotAuthenticated):
        resolve_user(db, bearer_token="mafsk_nope", session_sub=user.sub)


def test_no_bearer_valid_session_returns_user(db, make_user):
    user = make_user(sub="session-only")
    result = resolve_user(db, bearer_token=None, session_sub=user.sub)
    assert result.id == user.id


def test_no_bearer_unknown_session_raises(db):
    with pytest.raises(NotAuthenticated):
        resolve_user(db, bearer_token=None, session_sub="ghost")


def test_no_bearer_no_session_raises(db):
    with pytest.raises(NotAuthenticated):
        resolve_user(db, bearer_token=None, session_sub=None)


def test_expired_bearer_raises(db, make_user):
    user = make_user()
    api_key, raw_key = create_api_key(db, user, name="t", expires_at=None)
    api_key.expires_at = _past_naive_utc()
    db.commit()
    with pytest.raises(NotAuthenticated):
        resolve_user(db, bearer_token=raw_key, session_sub=None)
