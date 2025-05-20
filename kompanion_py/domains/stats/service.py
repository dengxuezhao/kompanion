from typing import List, Dict, Optional
from uuid import UUID
from datetime import timedelta

from kompanion_py.models import Book # Assuming Book model is needed for formatted output
from .repository import StatsRepository
from .exceptions import StatsNotFoundError # Potentially use if a user has NO stats at all

# For now, returning dicts. If these become complex, consider Pydantic models.
# Example:
# class UserReadingSummary(BaseModel):
#     total_books_started: int
#     total_books_finished: int
#     total_reading_time_estimate: str # e.g., "HH:MM:SS"
#     average_read_percentage: Optional[float]

# class TopBookStat(BaseModel):
#     book_id: UUID
#     title: str
#     author: Optional[str]
#     percentage_read: float


class StatsService:
    def __init__(self, stats_repository: StatsRepository):
        self.stats_repository = stats_repository

    def get_user_reading_summary(self, user_id: UUID) -> Dict:
        """
        Combines several stats like total books started, finished, reading time, etc.
        """
        total_started = self.stats_repository.get_total_books_started(user_id)
        total_finished = self.stats_repository.get_total_books_finished(user_id) # Uses default threshold
        reading_time_td = self.stats_repository.get_total_reading_time_estimate(user_id)
        avg_percentage = self.stats_repository.get_average_read_percentage(user_id)

        # Convert timedelta to a string representation (e.g., "X hours, Y minutes")
        total_seconds = int(reading_time_td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        reading_time_str = f"{hours} hours, {minutes} minutes"

        # If no stats at all, one might raise StatsNotFoundError,
        # but for a summary, returning zeros/empty values is also acceptable.
        # if total_started == 0 and total_finished == 0 and total_seconds == 0 and avg_percentage is None:
        #     raise StatsNotFoundError(user_id=user_id, details="No reading activity found for summary.")

        return {
            "total_books_started": total_started,
            "total_books_finished": total_finished,
            "total_reading_time_estimate": reading_time_str,
            "average_read_percentage": avg_percentage,
        }

    def get_top_books_for_user(
        self, user_id: UUID, limit: int = 5
    ) -> List[Dict]:
        """
        Formats the output for most read books from the repository.
        """
        most_read_tuples = self.stats_repository.get_most_read_books(
            user_id=user_id, limit=limit
        )
        
        formatted_books: List[Dict] = []
        for book, percentage in most_read_tuples:
            formatted_books.append(
                {
                    "book_id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "percentage_read": round(percentage * 100, 2), # As percentage
                }
            )
        return formatted_books

    def get_user_activity_timeline(
        self, user_id: UUID, period: str = "month"
    ) -> Dict[str, float]:
        """
        Gets reading activity (e.g., books finished) over a specified period.
        """
        activity = self.stats_repository.get_reading_activity_over_time(
            user_id=user_id, period=period
        )
        # If activity is empty, one could raise StatsNotFoundError or return empty dict
        # if not activity:
        #     raise StatsNotFoundError(user_id=user_id, details=f"No activity found for period '{period}'.")
        return activity
