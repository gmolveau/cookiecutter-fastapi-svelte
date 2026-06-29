"""Endpoints for managing the current user's API keys."""

import structlog
from fastapi import APIRouter, HTTPException

from src.dependencies import SessionDep, SessionUserDep
from src.schemas.api_keys import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyListResponse,
    ApiKeyResponse,
)
from src.services import api_keys as api_keys_service

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.get("")
def list_api_keys(user: SessionUserDep, db: SessionDep) -> ApiKeyListResponse:
    keys = api_keys_service.list_api_keys(db, user)
    return ApiKeyListResponse(
        api_keys=[ApiKeyResponse.model_validate(key) for key in keys]
    )


@router.post("", status_code=201)
def create_api_key(
    body: ApiKeyCreateRequest, user: SessionUserDep, db: SessionDep
) -> ApiKeyCreateResponse:
    try:
        api_key, raw_key = api_keys_service.create_api_key(
            db, user, name=body.name, expires_at=body.expires_at
        )
    except (
        api_keys_service.ApiKeyLimitReached,
        api_keys_service.InvalidExpiration,
    ) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    logger.info("api_key.created", user_id=user.id, api_key_id=api_key.id)
    return ApiKeyCreateResponse(
        **ApiKeyResponse.model_validate(api_key).model_dump(), key=raw_key
    )


@router.delete("/{key_id}", status_code=204)
def delete_api_key(key_id: int, user: SessionUserDep, db: SessionDep) -> None:
    if not api_keys_service.delete_api_key(db, user, key_id):
        raise HTTPException(status_code=404, detail="API key not found")
    logger.info("api_key.revoked", user_id=user.id, api_key_id=key_id)
