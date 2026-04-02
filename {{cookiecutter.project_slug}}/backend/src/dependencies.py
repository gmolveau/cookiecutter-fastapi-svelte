"""Reusable FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.database import get_db
from src.models import User
from src.storage import get_disk
from src.storage.disk import StorageDisk

SessionDep = Annotated[Session, Depends(get_db)]

DiskDep = Annotated[StorageDisk, Depends(get_disk)]

ADMIN_ROLES = {"admin", "superadmin"}


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Return the logged-in User ORM object, or raise 401 if not authenticated."""
    session_user = request.session.get("user")
    if not session_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    sub = session_user.get("sub")
    if not sub:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = db.query(User).filter(User.sub == sub).first()
    if user is None:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_admin(request: Request) -> None:
    """Raise 401 if not logged in, 403 if not an admin."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin role required")


AdminDep = Depends(require_admin)
