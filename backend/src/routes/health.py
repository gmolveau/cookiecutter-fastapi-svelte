"""Health check endpoint."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from src.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck():
    return JSONResponse(content={"status": "ok", "version": get_settings().APP_VERSION})
