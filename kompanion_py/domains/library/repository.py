import abc
from typing import Optional, Tuple
from uuid import UUID

from kompanion_py.models import Book

from .exceptions import BookAlreadyExistsError, BookNotFoundError


class BookRepository(abc.ABC):
    @abc.abstractmethod
    def create_book(self, book: Book) -> Book:
        pass

    @abc.abstractmethod
    def get_book_by_id(self, book_id: UUID) -> Optional[Book]:
        pass

    @abc.abstractmethod
    def get_book_by_document_id(self, document_id: str) -> Optional[Book]:
        pass

    @abc.abstractmethod
    def list_books(
        self, offset: int = 0, limit: int = 20
    ) -> Tuple[list[Book], int]:
        pass

    @abc.abstractmethod
    def update_book(self, book: Book) -> Book:
        pass

    @abc.abstractmethod
    def delete_book(self, book_id: UUID) -> None:
        pass


class InMemoryBookRepository(BookRepository):
    def __init__(self):
        self._books: dict[UUID, Book] = {}
        self._books_by_doc_id: dict[str, UUID] = {}
        # For ordered listing and pagination, store IDs in insertion order.
        self._book_order_for_listing: list[UUID] = []

    def create_book(self, book: Book) -> Book:
        if book.id in self._books:
            raise BookAlreadyExistsError(document_id=book.document_id)
        if book.document_id in self._books_by_doc_id:
            raise BookAlreadyExistsError(document_id=book.document_id)

        new_book = book.copy(deep=True)
        self._books[new_book.id] = new_book
        self._books_by_doc_id[new_book.document_id] = new_book.id
        if new_book.id not in self._book_order_for_listing:
            self._book_order_for_listing.append(new_book.id)
        return new_book.copy(deep=True)

    def get_book_by_id(self, book_id: UUID) -> Optional[Book]:
        book = self._books.get(book_id)
        return book.copy(deep=True) if book else None

    def get_book_by_document_id(self, document_id: str) -> Optional[Book]:
        book_id = self._books_by_doc_id.get(document_id)
        if book_id:
            book = self._books.get(book_id)
            return book.copy(deep=True) if book else None
        return None

    def list_books(
        self, offset: int = 0, limit: int = 20
    ) -> Tuple[list[Book], int]:
        total_count = len(self._book_order_for_listing)
        if offset < 0:
            offset = 0
        if limit <= 0:
            limit = 20

        book_ids_page = self._book_order_for_listing[offset : offset + limit]
        books_page = [
            self._books[book_id].copy(deep=True) for book_id in book_ids_page if book_id in self._books
        ]
        return books_page, total_count

    def update_book(self, book: Book) -> Book:
        if book.id not in self._books:
            raise BookNotFoundError(book_id=str(book.id))

        # Ensure document_id consistency if it's being changed (though usually not)
        original_book = self._books[book.id]
        if original_book.document_id != book.document_id:
            if book.document_id in self._books_by_doc_id and self._books_by_doc_id[book.document_id] != book.id:
                raise BookAlreadyExistsError(document_id=book.document_id)
            del self._books_by_doc_id[original_book.document_id]
            self._books_by_doc_id[book.document_id] = book.id
        
        updated_book = book.copy(deep=True)
        self._books[updated_book.id] = updated_book
        return updated_book.copy(deep=True)

    def delete_book(self, book_id: UUID) -> None:
        if book_id not in self._books:
            raise BookNotFoundError(book_id=str(book_id))

        book_to_delete = self._books.pop(book_id)
        if book_to_delete.document_id in self._books_by_doc_id:
            del self._books_by_doc_id[book_to_delete.document_id]
        if book_id in self._book_order_for_listing:
            self._book_order_for_listing.remove(book_id)
