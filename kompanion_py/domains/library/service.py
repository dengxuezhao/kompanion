import abc
import hashlib
from typing import Optional, Tuple
from uuid import UUID, uuid4

from kompanion_py.models import Book
from kompanion_py.infrastructure.storage.base import StorageService
# Ensure correct import for specific storage errors if they need to be caught
# from kompanion_py.infrastructure.storage.filesystem import FileNotFoundInStorageError as FileSystemFileNotFound
from .repository import BookRepository
from .exceptions import BookAlreadyExistsError, BookNotFoundError


class MetadataParser(abc.ABC):
    @abc.abstractmethod
    def parse(self, file_data: bytes, filename: str) -> dict:
        """
        Parses metadata from the given file data.

        Args:
            file_data: The binary data of the file.
            filename: The original name of the file.

        Returns:
            A dictionary containing metadata such as title, author, etc.
            Expected keys: "title" (str), "author" (Optional[str]), "document_id" (Optional[str])
        """
        pass


class LibraryService:
    def __init__(
        self,
        book_repository: BookRepository,
        storage_service: StorageService,
        metadata_parser: MetadataParser,
    ):
        self.book_repository = book_repository
        self.storage_service = storage_service
        self.metadata_parser = metadata_parser

    def add_book(
        self, file_data: bytes, filename: str, owner_user_id: Optional[UUID] = None
    ) -> Book:
        # 1. Parse metadata
        metadata = self.metadata_parser.parse(file_data, filename)

        # 2. Generate or get document_id
        # Prefer document_id from metadata if available, otherwise generate one.
        document_id = metadata.get("document_id")
        if not document_id:
            document_id = hashlib.md5(file_data).hexdigest()

        # 3. Check if book with this document_id already exists
        existing_book = self.book_repository.get_book_by_document_id(document_id)
        if existing_book:
            raise BookAlreadyExistsError(document_id=document_id)

        # 4. Create Book model
        book_id = uuid4()
        title = metadata.get("title", "Unknown Title")
        author = metadata.get("author")

        # 5. Determine the book URI and store the book file
        # The owner_user_id is required by get_book_uri and store_book_file
        if owner_user_id is None:
            # Fallback or error if owner_user_id is critical.
            # For this example, let's create a dummy UUID if not provided,
            # but in a real app, this should be handled based on auth context.
            # This is a significant change from the previous structure where owner_user_id was optional
            # and not directly used by storage service.
            # If user context is always available, this should be a required parameter.
            # For now, let's assume it might not always be available and we need a placeholder
            # or a different strategy if it's missing.
            # Given the current StorageService interface, user_id IS required.
            # This implies add_book must receive a valid owner_user_id.
            # Let's adjust the method signature or raise an error if it's None.
            # For now, I'll assume owner_user_id will be provided. If not, this will fail.
            # A better approach might be to make owner_user_id mandatory for add_book.
            # For the purpose of this subtask, let's assume owner_user_id is always provided.
            # If owner_user_id is not available, the operation should likely fail.
             raise ValueError("owner_user_id is required to add a book.")


        # The URI might not be directly used by store_book_file if it constructs its own path logic,
        # but it's good to get it to see the intended identifier.
        # book_uri = self.storage_service.get_book_uri(owner_user_id, book_id, filename)

        # Store the book file using StorageService. user_id is now required.
        stored_file_path = self.storage_service.store_book_file(
            user_id=owner_user_id, book_id=book_id, file_data=file_data, filename=filename
        )

        book = Book(
            id=book_id,
            title=title,
            author=author,
            document_id=document_id, # document_id from metadata or hash
            file_path=stored_file_path, # This is the path/identifier from storage service
            # format can be derived from filename
            # owner_user_id=owner_user_id, # This field should exist in Book model
        )
        # Attempt to set format from Book's properties if available
        if hasattr(book, 'extension') and book.extension:
            book.format = book.extension.lstrip('.')
        else:
            # Fallback to guess from filename if Book.extension is not reliable
            import os
            _, ext = os.path.splitext(filename)
            if ext:
                book.format = ext.lstrip('.')


        # (Optional: store cover if metadata parser extracts it and storage service supports it)
        # cover_data = metadata.get("cover_image_data")
        # if cover_data:
        #     cover_filename = f"cover_{book_id}.jpg" # Or derive from metadata
        #     stored_cover_path = self.storage_service.store_cover_image(
        #         book_id=book_id, cover_data=cover_data, filename=cover_filename
        #     )
        #     book.cover_path = stored_cover_path

        # 6. Save the Book model using BookRepository
        return self.book_repository.create_book(book)

    def get_book_details(self, book_id: UUID) -> Optional[Book]:
        return self.book_repository.get_book_by_id(book_id)

    def list_all_books(
        self, page: int = 1, page_size: int = 20
    ) -> Tuple[list[Book], int]:
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        offset = (page - 1) * page_size
        return self.book_repository.list_books(offset=offset, limit=page_size)

    def download_book_file(
        self, book_id: UUID
    ) -> Tuple[Optional[bytes], Optional[str]]:
        book = self.book_repository.get_book_by_id(book_id)
        if not book:
            raise BookNotFoundError(book_id=str(book_id))

        try:
            # retrieve_book_file now only takes stored_path
            file_data = self.storage_service.retrieve_book_file(stored_path=book.file_path)
            # Use effective_filename which includes the document_id and original extension
            return file_data, book.effective_filename
        except FileNotFoundError: # This is a generic Python error.
                                 # Specific storage errors should be caught if defined and used.
                                 # e.g. except FileSystemFileNotFound:
            raise BookNotFoundError(book_id=str(book_id))
        # Catching a more specific error from storage service if available
        # except SpecificStorageFileNotFoundError as e:
        #     raise BookNotFoundError(book_id=str(book_id)) from e


    def delete_book(self, book_id: UUID) -> None:
        book = self.book_repository.get_book_by_id(book_id)
        if not book:
            raise BookNotFoundError(book_id=str(book_id))

        # Delete file from storage first
        try:
            # delete_book_file now only takes stored_path
            self.storage_service.delete_book_file(stored_path=book.file_path)
            # Optionally delete cover image if it exists and is tracked
            # if book.cover_path and hasattr(self.storage_service, 'delete_cover_image'):
            #     self.storage_service.delete_cover_image(stored_path=book.cover_path)
        except Exception as e:
            # Log the error, decide if you should proceed to delete the DB record
            # For now, we'll proceed to ensure DB consistency even if file deletion fails.
            # A more robust solution might involve a retry mechanism or marking the book for cleanup.
            print(f"Error deleting book file {book.file_path} for book {book_id} from storage: {e}")


        # Delete book record from repository
        self.book_repository.delete_book(book_id)
