class StatsError(Exception):
    """Base class for statistics errors."""

    pass


from uuid import UUID

class StatsNotFoundError(StatsError):
    """Raised when specific statistics are not found for a user."""

    def __init__(self, user_id: UUID, details: str = "Statistics not found"):
        self.user_id = user_id
        self.details = details
        super().__init__(f"{details} for user '{str(user_id)}'.")
