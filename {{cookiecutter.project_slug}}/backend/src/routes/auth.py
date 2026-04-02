import secrets
from typing import Annotated
from urllib.parse import urlparse

import structlog
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config import get_settings
from src.dependencies import SessionDep
from src.services.users import get_effective_role, upsert_user

logger = structlog.get_logger(__name__)

oauth = OAuth()
router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()

oauth.register(
    name="keycloak",
    client_id=settings.KEYCLOAK_CLIENT_ID,
    client_secret=settings.KEYCLOAK_CLIENT_SECRET,
    authorize_url=settings.KEYCLOAK_AUTHORIZE_URL,
    access_token_url=settings.KEYCLOAK_ACCESS_TOKEN_URL,
    jwks_uri=settings.KEYCLOAK_JWT_URL,
    client_kwargs={"scope": "openid email profile"},
)


def is_next_url_valid(url: str) -> bool:
    """Accept relative paths; in dev also accept any absolute URL."""
    parsed = urlparse(url)
    if not parsed.scheme and not parsed.netloc:
        return url.startswith("/")
    if settings.APP_ENV == "dev":
        return bool(parsed.scheme and parsed.netloc)
    return False


@router.get("/login")
async def login_endpoint(
    request: Request, next_url: Annotated[str | None, Query(alias="next")] = None
):
    nonce = secrets.token_urlsafe(16)
    request.session["nonce"] = nonce
    redirect_uri = request.url_for("authorize_endpoint")

    if next_url and is_next_url_valid(next_url):
        request.session["next_url"] = next_url

    return await oauth.keycloak.authorize_redirect(request, redirect_uri, nonce=nonce)


@router.get("/authorize", name="authorize_endpoint")
async def authorize_endpoint(request: Request, db: SessionDep):
    nonce = request.session.pop("nonce", None)
    if not nonce:
        raise HTTPException(status_code=401, detail="Missing nonce")
    oidc_token = await oauth.keycloak.authorize_access_token(request)
    data = await oauth.keycloak.parse_id_token(oidc_token, nonce)
    sub: str = data["sub"]
    name: str = data["name"]
    email: str = data["email"]
    group_names: list[str] = data["groups"]

    user = upsert_user(db, sub=sub, name=name, email=email, group_names=group_names)
    logger.info("user.login", sub=sub, name=name, email=email)

    request.session["user"] = {
        "sub": sub,
        "name": name,
        "email": email,
        "groups": group_names,
        "role": get_effective_role(user),
    }

    next_url = request.session.pop("next_url", "/")
    response = RedirectResponse(url=next_url)
    # has_session is an indicator cookie, hence the httponly set to false
    # so that the frontend can detect if the user is logged in
    response.set_cookie(
        key="has_session",
        value="1",
        max_age=settings.SESSION_COOKIE_MAX_AGE,
        httponly=False,
        samesite="lax",
    )
    return response


@router.get("/logout")
def logout(request: Request) -> JSONResponse:
    user = request.session.get("user")
    if user:
        logger.info("user.logout", sub=user.get("sub"))
    request.session.clear()
    response = JSONResponse(content={"status": "logged out"})
    response.delete_cookie(
        key="has_session",
    )
    return response


@router.get("/me")
def me(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "name": user["name"],
        "role": user.get("role"),
    }
