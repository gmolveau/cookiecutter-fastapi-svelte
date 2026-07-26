"""Local filesystem storage disk."""

import shutil
from pathlib import Path
from typing import BinaryIO

from src.storage.disk import StorageDisk


class LocalDisk(StorageDisk):
    def __init__(self, root: str, base_url: str) -> None:
        self.root = Path(root)
        self._base_url = base_url.rstrip("/")

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, path: str, file: BinaryIO) -> None:
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("wb") as buf:
            shutil.copyfileobj(file, buf)

    def delete(self, path: str) -> None:
        (self.root / path).unlink(missing_ok=True)

    def url(self, path: str) -> str:
        return f"{self._base_url}/{path}"
