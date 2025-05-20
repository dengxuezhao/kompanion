import mimetypes
import pathlib
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Book(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    document_id: str  # From KOReader metadata
    file_path: str  # Relative path to the book file
    format: Optional[str] = None  # e.g., "epub", "pdf"
    cover_path: Optional[str] = None  # Relative path to the cover image

    @property
    def extension(self) -> str:
        return "".join(pathlib.Path(self.file_path).suffixes)

    @property
    def effective_filename(self) -> str:
        return f"{self.document_id}{self.extension}"

    @property
    def mime_type(self) -> str:
        mime, _ = mimetypes.guess_type(self.file_path)
        return mime or "application/octet-stream"

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "title": "The Hitchhiker's Guide to the Galaxy",
                "author": "Douglas Adams",
                "created_at": "2023-01-01T12:00:00Z",
                "updated_at": "2023-01-01T12:00:00Z",
                "document_id": "some-unique-document-id",
                "file_path": "books/authors/Douglas Adams/The Hitchhiker's Guide to the Galaxy.epub",
                "format": "epub",
                "cover_path": "covers/some-unique-document-id.jpg",
            }
        }
