class SyncError(Exception):
    """Base class for synchronization errors."""

    pass


class ProgressNotFoundError(SyncError):
    """Raised when progress for a document/user/device is not found."""

    def __init__(
        self,
        document_id: str = None,
        user_id: str = None,
        device_id: str = None,
    ):
        if document_id and user_id:
            super().__init__(
                f"Progress not found for document '{document_id}' and user '{user_id}'."
            )
        elif document_id and device_id:
            super().__init__(
                f"Progress not found for document '{document_id}' and device '{device_id}'."
            )
        elif document_id:
            super().__init__(f"Progress not found for document '{document_id}'.")
        else:
            super().__init__("Progress not found.")
