"""Pydantic schemas for item endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ItemCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""


class ItemUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""


class ItemListResponse(BaseModel):
    items: list[ItemResponse]
    total: int
