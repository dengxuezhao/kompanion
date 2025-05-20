class LibraryError(Exception):
    """Base class for library errors."""

    pass


class BookNotFoundError(LibraryError):
    """Raised when a book is not found."""

    def __init__(self, book_id: str = None, document_id: str = None):
        if book_id:
            super().__init__(f"Book with ID '{book_id}' not found.")
        elif document_id:
            super().__init__(f"Book with document ID '{document_id}' not found.")
        else:
            super().__init__("Book not found.")


class BookAlreadyExistsError(LibraryError):
    """Raised when trying to add a book that already exists."""

    def __init__(self, title: str = None, document_id: str = None):
        if document_id:
            super().__init__(
                f"Book with document ID '{document_id}' already exists."
            )
        elif title:
            super().__init__(f"Book with title '{title}' already exists.")
        else:
            super().__init__("Book already exists.")
