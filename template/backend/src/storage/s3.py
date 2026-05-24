"""S3-compatible storage disk (AWS S3, MinIO, Cloudflare R2, etc.)."""

from typing import BinaryIO

import boto3

from src.storage.disk import StorageDisk


class S3Disk(StorageDisk):
    def __init__(
        self,
        bucket: str,
        region: str,
        prefix: str,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        self._bucket = bucket
        self._region = region
        self._prefix = prefix.rstrip("/") + "/" if prefix else ""
        self._endpoint_url = endpoint_url.rstrip("/") if endpoint_url else None
        kwargs: dict = {"region_name": region}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        if access_key and secret_key:
            kwargs["aws_access_key_id"] = access_key
            kwargs["aws_secret_access_key"] = secret_key
        self._client = boto3.client("s3", **kwargs)

    def ensure(self) -> None:
        self._client.head_bucket(Bucket=self._bucket)

    def save(self, path: str, file: BinaryIO) -> None:
        self._client.upload_fileobj(file, self._bucket, f"{self._prefix}{path}")

    def delete(self, path: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=f"{self._prefix}{path}")

    def url(self, path: str) -> str:
        if self._endpoint_url:
            return f"{self._endpoint_url}/{self._bucket}/{self._prefix}{path}"
        return f"https://{self._bucket}.s3.{self._region}.amazonaws.com/{self._prefix}{path}"
