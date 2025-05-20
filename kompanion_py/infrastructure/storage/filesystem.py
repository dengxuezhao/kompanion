import os
import pathlib
import shutil
from uuid import UUID

from kompanion_py.core.config import BookStorageSettings
from .base import StorageService


class FileSystemStorageError(Exception):
    """Base class for filesystem storage errors."""

    pass


class FileNotFoundInStorageError(FileSystemStorageError):
    """Raised when a file is not found in filesystem storage."""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"File not found at path: {path}")


class FileSystemStorageService(StorageService):
    def __init__(self, settings: BookStorageSettings):
        if settings.type.lower() != "local":
            raise ValueError(
                "FileSystemStorageService can only be used with 'local' storage type."
            )
        self.base_path = pathlib.Path(settings.path)
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)
        elif not self.base_path.is_dir():
            raise FileSystemStorageError(
                f"Base path '{self.base_path}' exists but is not a directory."
            )

    def _get_actual_path(
        self, user_id: UUID, book_id: UUID, filename: str
    ) -> pathlib.Path:
        # Sanitize filename to prevent directory traversal or invalid characters
        safe_filename = "".join(
            c for c in filename if c.isalnum() or c in ('.', '_', '-')
        ).strip()
        if not safe_filename:
            safe_filename = "untitled"
        
        # Construct path: base_path / user_id / book_id / safe_filename
        return self.base_path / str(user_id) / str(book_id) / safe_filename

    def store_book_file(
        self, user_id: UUID, book_id: UUID, file_data: bytes, filename: str
    ) -> str:
        actual_path = self._get_actual_path(user_id, book_id, filename)
        try:
            actual_path.parent.mkdir(parents=True, exist_ok=True)
            with open(actual_path, "wb") as f:
                f.write(file_data)
            # Return the path relative to the base_path as the stored_path
            return str(actual_path.relative_to(self.base_path))
        except OSError as e:
            raise FileSystemStorageError(f"Error storing file {filename}: {e}")

    def retrieve_book_file(self, stored_path: str) -> bytes:
        actual_path = self.base_path / stored_path
        if not actual_path.exists() or not actual_path.is_file():
            raise FileNotFoundInStorageError(str(actual_path))
        try:
            with open(actual_path, "rb") as f:
                return f.read()
        except OSError as e:
            raise FileSystemStorageError(f"Error retrieving file {stored_path}: {e}")

    def delete_book_file(self, stored_path: str) -> None:
        actual_path = self.base_path / stored_path
        if not actual_path.exists() or not actual_path.is_file():
            # If file doesn't exist, consider it successfully deleted (idempotency)
            return
        try:
            actual_path.unlink()
            # Attempt to clean up empty parent directories
            parent_dir = actual_path.parent
            book_dir = parent_dir.parent # user_id directory
            user_dir = book_dir.parent # base_path
            
            # Delete book_id directory if empty
            if parent_dir.exists() and not any(parent_dir.iterdir()):
                parent_dir.rmdir()
            # Delete user_id directory if empty (and it's not the base_path itself)
            if book_dir.exists() and not any(book_dir.iterdir()) and book_dir != self.base_path:
                 book_dir.rmdir()

        except OSError as e:
            raise FileSystemStorageError(f"Error deleting file {stored_path}: {e}")

    def get_book_uri(self, user_id: UUID, book_id: UUID, filename: str) -> str:
        # The URI itself doesn't guarantee the file exists, it's an identifier.
        # The actual path is constructed in _get_actual_path
        relative_path = self._get_actual_path(user_id, book_id, filename).relative_to(self.base_path)
        return f"filesystem:///{str(relative_path).replace(os.sep, '/')}"
