"""Health check endpoint."""

import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck():
    app_version = os.environ.get("APP_VERSION", "dev")
    return JSONResponse(content={"status": "ok", "version": app_version})
