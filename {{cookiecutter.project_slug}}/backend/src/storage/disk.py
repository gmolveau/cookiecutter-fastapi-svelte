"""Abstract base class for storage disks."""

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageDisk(ABC):
    @abstractmethod
    def save(self, path: str, file: BinaryIO) -> None:
        """Persist file contents at the given path."""

    @abstractmethod
    def delete(self, path: str) -> None:
        """Remove the file at the given path."""

    @abstractmethod
    def url(self, path: str) -> str:
        """Return a publicly accessible URL for the given path."""

    @abstractmethod
    def ensure(self) -> None:
        """Initialise the storage backend (create dirs, validate bucket, etc.)."""
