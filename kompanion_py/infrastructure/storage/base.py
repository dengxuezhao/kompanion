import abc
from uuid import UUID


class StorageService(abc.ABC):
    @abc.abstractmethod
    def store_book_file(
        self, user_id: UUID, book_id: UUID, file_data: bytes, filename: str
    ) -> str:
        """
        Stores the book file.

        Args:
            user_id: The ID of the user owning the book (for namespacing).
            book_id: The ID of the book.
            file_data: The binary data of the file.
            filename: The original name of the file.

        Returns:
            The stored path or identifier for the file (e.g., relative path, URI).
        """
        pass

    @abc.abstractmethod
    def retrieve_book_file(self, stored_path: str) -> bytes:
        """
        Retrieves the book file.

        Args:
            stored_path: The path or identifier where the file is stored,
                         as returned by store_book_file.

        Returns:
            The binary data of the file.
        """
        pass

    @abc.abstractmethod
    def delete_book_file(self, stored_path: str) -> None:
        """
        Deletes the book file.

        Args:
            stored_path: The path or identifier where the file is stored.
        """
        pass

    @abc.abstractmethod
    def get_book_uri(self, user_id: UUID, book_id: UUID, filename: str) -> str:
        """
        Returns a URI-like string for the book file.
        This URI can be used as an abstract identifier.

        Args:
            user_id: The ID of the user.
            book_id: The ID of the book.
            filename: The original name of the file.

        Returns:
            A URI-like string (e.g., "filesystem:///user_id/book_id/filename").
        """
        pass
