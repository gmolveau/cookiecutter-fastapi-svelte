"""Pydantic schemas for API key endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    created_at: datetime
    expires_at: datetime | None
    last_used_at: datetime | None

    model_config = {"from_attributes": True}


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    expires_at: datetime | None = None


class ApiKeyCreateResponse(ApiKeyResponse):
    key: str


class ApiKeyListResponse(BaseModel):
    api_keys: list[ApiKeyResponse]
