"""Reusable FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.database import get_db
from src.models import User
from src.services.authentication import NotAuthenticated, resolve_user
from src.services.users import get_effective_role
from src.storage import get_disk
from src.storage.disk import StorageDisk

SessionDep = Annotated[Session, Depends(get_db)]

DiskDep = Annotated[StorageDisk, Depends(get_disk)]

ADMIN_ROLES = {"admin", "superadmin"}


def get_current_user_from_session(
    request: Request, db: Session = Depends(get_db)
) -> User:
    """Return the logged-in User ORM object, or raise 401 if not authenticated."""
    session_user = request.session.get("user")
    session_sub = session_user.get("sub") if session_user else None
    try:
        return resolve_user(db, bearer_token=None, session_sub=session_sub)
    except NotAuthenticated:
        if session_user:
            request.session.clear()
        raise HTTPException(status_code=401, detail="Not authenticated") from None


SessionUserDep = Annotated[User, Depends(get_current_user_from_session)]


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Return the User from an API key Bearer token, or fall back to the session.

    Raise 401 if neither yields an authenticated user.
    """
    scheme, _, token = request.headers.get("Authorization", "").partition(" ")
    bearer_token = token if scheme.lower() == "bearer" and token else None
    session_user = request.session.get("user")
    session_sub = session_user.get("sub") if session_user else None
    try:
        return resolve_user(db, bearer_token=bearer_token, session_sub=session_sub)
    except NotAuthenticated:
        if bearer_token is None and session_user:
            request.session.clear()
        raise HTTPException(status_code=401, detail="Not authenticated") from None


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUserDep) -> None:
    """Raise 401 if not logged in, 403 if not an admin."""
    if get_effective_role(user) not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin role required")


AdminDep = Depends(require_admin)
