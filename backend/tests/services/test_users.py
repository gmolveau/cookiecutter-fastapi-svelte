"""Unit tests for the single source of truth: ``get_effective_role``."""

from src.services.users import get_effective_role


def test_direct_role_takes_precedence(make_user, make_role):
    role = make_role("editor")
    user = make_user(role=role)
    assert get_effective_role(user) == "editor"


def test_falls_back_to_group_role(make_user, make_role, make_group):
    group_role = make_role("admin")
    group = make_group("admins", role=group_role)
    user = make_user(groups=[group])
    assert get_effective_role(user) == "admin"


def test_direct_role_wins_over_group_role(make_user, make_role, make_group):
    direct_role = make_role("editor")
    group_role = make_role("admin")
    group = make_group("admins", role=group_role)
    user = make_user(role=direct_role, groups=[group])
    assert get_effective_role(user) == "editor"


def test_returns_none_when_no_role(make_user):
    user = make_user()
    assert get_effective_role(user) is None
