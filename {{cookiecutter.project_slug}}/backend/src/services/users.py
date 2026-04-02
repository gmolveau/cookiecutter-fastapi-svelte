"""User service — upsert users and groups from OIDC data."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.models import Group, Role, User


def _get_or_create_group(db: Session, name: str) -> Group:
    group = db.scalar(select(Group).where(Group.name == name))
    if group is None:
        group = Group(name=name)
        db.add(group)
    return group


def assign_role(
    db: Session,
    role_name: str,
    *,
    sub: str | None = None,
    email: str | None = None,
    name: str | None = None,
    user_id: int | None = None,
) -> User | None:
    """Assign a role to a user looked up by any of sub, email, name, or id.
    Returns None if not found."""

    conditions = []
    if sub is not None:
        conditions.append(User.sub == sub)
    if email is not None:
        conditions.append(User.email == email)
    if name is not None:
        conditions.append(User.name == name)
    if user_id is not None:
        conditions.append(user_id)

    if not conditions:
        return None

    user = db.scalar(select(User).where(or_(*conditions)))
    if user is None:
        return None

    role = db.scalar(select(Role).where(Role.name == role_name))
    if role is None:
        return None

    user.role = role
    db.commit()
    return user


def get_effective_role(user: User) -> str | None:
    """Return the user's role name, falling back to their groups' roles."""
    if user.role:
        return user.role.name
    for group in user.groups:
        if group.role:
            return group.role.name
    return None


def upsert_user(
    db: Session,
    sub: str,
    name: str,
    email: str,
    group_names: list[str],
) -> User:
    groups = [_get_or_create_group(db, g) for g in group_names]

    user = db.scalar(select(User).where(User.sub == sub))
    if user is None:
        user = User(sub=sub, name=name, email=email, groups=groups)
        db.add(user)
    else:
        user.name = name
        user.email = email
        user.groups = groups

    db.commit()
    return user
