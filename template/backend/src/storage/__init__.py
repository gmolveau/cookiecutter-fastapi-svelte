"""Storage module — builds the active disk singleton from environment variables.

Environment variables
---------------------
STORAGE_DRIVER              ``local`` or ``s3``          default: local
STORAGE_LOCAL_PATH          root dir for local disk       required when driver=local
STORAGE_S3_BUCKET            bucket name                   required when driver=s3
STORAGE_S3_REGION            region                        required when driver=s3
STORAGE_S3_PREFIX            key prefix inside bucket      optional
STORAGE_S3_ENDPOINT_URL      custom endpoint (MinIO, R2…)  optional (omit for AWS)
STORAGE_S3_ACCESS_KEY_ID     explicit credentials          optional
STORAGE_S3_SECRET_ACCESS_KEY explicit credentials          optional
"""

from src.config import get_settings
from src.storage.disk import StorageDisk
from src.storage.local import LocalDisk
from src.storage.s3 import S3Disk

settings = get_settings()

if settings.STORAGE_DRIVER.lower() == "s3":
    bucket = settings.STORAGE_S3_BUCKET
    region = settings.STORAGE_S3_REGION
    if bucket is None or region is None:
        raise RuntimeError(
            "S3 storage requires STORAGE_S3_BUCKET and STORAGE_S3_REGION"
        )
    active_disk: StorageDisk = S3Disk(
        bucket=bucket,
        region=region,
        prefix=settings.STORAGE_S3_PREFIX,
        endpoint_url=settings.STORAGE_S3_ENDPOINT_URL,
        access_key=settings.STORAGE_S3_ACCESS_KEY_ID,
        secret_key=settings.STORAGE_S3_SECRET_ACCESS_KEY,
    )
else:
    local_path = settings.STORAGE_LOCAL_PATH
    if local_path is None:
        raise RuntimeError("Local storage requires STORAGE_LOCAL_PATH")
    active_disk = LocalDisk(
        root=local_path,
        base_url="/api/files",
    )


def get_disk() -> StorageDisk:
    """FastAPI Depends-compatible factory returning the active disk singleton."""
    return active_disk
