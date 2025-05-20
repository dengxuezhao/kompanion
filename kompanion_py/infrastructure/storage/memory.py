import os
from uuid import UUID

from .base import StorageService


class MemoryStorageError(Exception):
    """Base class for in-memory storage errors."""

    pass


class FileNotInMemoryStorageError(MemoryStorageError):
    """Raised when a file is not found in memory storage."""

    def __init__(self, uri: str):
        self.uri = uri
        super().__init__(f"File not found at URI: {uri}")


class InMemoryStorageService(StorageService):
    def __init__(self):
        self._storage: dict[str, bytes] = {}

    def store_book_file(
        self, user_id: UUID, book_id: UUID, file_data: bytes, filename: str
    ) -> str:
        # Sanitize filename for URI
        safe_filename = "".join(
            c for c in filename if c.isalnum() or c in ('.', '_', '-')
        ).strip()
        if not safe_filename:
            safe_filename = "untitled"

        uri = self.get_book_uri(user_id, book_id, safe_filename)
        self._storage[uri] = file_data
        return uri  # The URI is the stored_path for in-memory storage

    def retrieve_book_file(self, stored_path: str) -> bytes: # stored_path is the URI
        if stored_path not in self._storage:
            raise FileNotInMemoryStorageError(stored_path)
        return self._storage[stored_path]

    def delete_book_file(self, stored_path: str) -> None: # stored_path is the URI
        if stored_path in self._storage:
            del self._storage[stored_path]
        # If not found, it's idempotent, so no error

    def get_book_uri(self, user_id: UUID, book_id: UUID, filename: str) -> str:
        # Sanitize filename for URI (consistency with store_book_file)
        safe_filename = "".join(
            c for c in filename if c.isalnum() or c in ('.', '_', '-')
        ).strip()
        if not safe_filename:
            safe_filename = "untitled"
            
        # Ensure consistent URI format, similar to how it might be stored.
        # Using os.path.join-like behavior for path components is not directly applicable
        # for URI construction, but we want to ensure clean slashes.
        uri_path_parts = [str(user_id), str(book_id), safe_filename]
        uri_path = "/".join(uri_path_parts)
        return f"memory:///{uri_path}"
