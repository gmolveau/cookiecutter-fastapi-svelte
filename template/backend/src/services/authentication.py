"""Identity resolution — turn presented credentials into an authenticated User.

Decoupled from FastAPI's Request: callers pass the raw credentials they
extracted (a bearer token and/or a session subject); this module performs the
lookup and enforces precedence.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import User
from src.services.api_keys import authenticate_api_key


class NotAuthenticated(Exception):
    """Raised when presented credentials do not resolve to a user."""


def resolve_user(
    db: Session, *, bearer_token: str | None, session_sub: str | None
) -> User:
    """Resolve the authenticated User from presented credentials.

    A bearer token is authoritative: if one is presented it is the only thing
    consulted (an invalid bearer does NOT fall back to the session). With no
    bearer token, the session subject is used. Raises NotAuthenticated when
    nothing resolves to a user.
    """
    if bearer_token:
        user = authenticate_api_key(db, bearer_token)
        if user is None:
            raise NotAuthenticated
        return user
    if session_sub:
        user = db.scalar(select(User).where(User.sub == session_sub))
        if user is None:
            raise NotAuthenticated
        return user
    raise NotAuthenticated
