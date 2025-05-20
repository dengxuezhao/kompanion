import abc
from collections import defaultdict
from datetime import timedelta, datetime
from typing import List, Tuple, Dict, Optional
from uuid import UUID

from kompanion_py.models import Book, Progress
from kompanion_py.domains.sync.repository import ProgressRepository # Assuming this path
from kompanion_py.domains.library.repository import BookRepository # Assuming this path


class StatsRepository(abc.ABC):
    @abc.abstractmethod
    def get_total_books_started(self, user_id: UUID) -> int:
        pass

    @abc.abstractmethod
    def get_total_books_finished(self, user_id: UUID, finish_threshold: float = 0.95) -> int:
        pass

    @abc.abstractmethod
    def get_total_reading_time_estimate(self, user_id: UUID) -> timedelta:
        """Estimates total reading time. Highly dependent on data availability."""
        pass

    @abc.abstractmethod
    def get_most_read_books(
        self, user_id: UUID, limit: int = 5, count_as_finished_threshold: float = 0.95
    ) -> List[Tuple[Book, float]]:
        """Returns tuples of Book object and percentage read."""
        pass

    @abc.abstractmethod
    def get_reading_activity_over_time(
        self, user_id: UUID, period: str = "month"
    ) -> Dict[str, float]:
        """e.g., books finished per month or percentage read per month."""
        pass

    @abc.abstractmethod
    def get_average_read_percentage(self, user_id: UUID) -> Optional[float]:
        pass


class InMemoryStatsRepository(StatsRepository):
    def __init__(
        self,
        progress_repository: ProgressRepository,
        book_repository: BookRepository,
    ):
        self.progress_repository = progress_repository
        self.book_repository = book_repository

    def get_total_books_started(self, user_id: UUID) -> int:
        all_progress = self.progress_repository.get_all_progress_for_user(user_id)
        if not all_progress:
            return 0
        # Count unique document_ids for which any progress exists
        started_book_ids = {p.document_id for p in all_progress if p.percentage > 0}
        return len(started_book_ids)

    def get_total_books_finished(self, user_id: UUID, finish_threshold: float = 0.95) -> int:
        all_progress = self.progress_repository.get_all_progress_for_user(user_id)
        if not all_progress:
            return 0
        
        finished_book_ids = set()
        # For each document, find the max progress
        latest_progress_per_book = {}
        for p in all_progress:
            if p.document_id not in latest_progress_per_book or p.timestamp > latest_progress_per_book[p.document_id].timestamp:
                latest_progress_per_book[p.document_id] = p
        
        for doc_id, progress_entry in latest_progress_per_book.items():
            if progress_entry.percentage >= finish_threshold:
                finished_book_ids.add(doc_id)
        return len(finished_book_ids)

    def get_total_reading_time_estimate(self, user_id: UUID) -> timedelta:
        # This is a very naive estimation.
        # It assumes progress entries are somewhat sequential and time between them is reading time.
        # This will be highly inaccurate without more sophisticated session tracking.
        # For a simple placeholder:
        all_progress = self.progress_repository.get_all_progress_for_user(user_id)
        if not all_progress or len(all_progress) < 2:
            return timedelta(0)

        all_progress.sort(key=lambda p: p.timestamp)
        
        total_time = timedelta(0)
        # Group progress by document_id
        progress_by_doc = defaultdict(list)
        for p in all_progress:
            progress_by_doc[p.document_id].append(p)

        for doc_id, progresses in progress_by_doc.items():
            if len(progresses) < 2:
                continue
            progresses.sort(key=lambda p: p.timestamp)
            # Sum time differences between consecutive progress entries for the same book
            # Cap time difference to avoid huge gaps if user comes back after a long time.
            MAX_SESSION_GAP_SECONDS = 2 * 60 * 60 # 2 hours
            for i in range(len(progresses) - 1):
                time_diff = progresses[i+1].timestamp - progresses[i].timestamp
                if time_diff.total_seconds() < MAX_SESSION_GAP_SECONDS and time_diff.total_seconds() > 0:
                     # Only add if progress actually increased
                    if progresses[i+1].percentage > progresses[i].percentage:
                        total_time += time_diff
        
        return total_time


    def get_most_read_books(
        self, user_id: UUID, limit: int = 5, count_as_finished_threshold: float = 0.95
    ) -> List[Tuple[Book, float]]:
        all_progress = self.progress_repository.get_all_progress_for_user(user_id)
        if not all_progress:
            return []

        latest_progress_per_book = {}
        for p in all_progress:
            if p.document_id not in latest_progress_per_book or p.timestamp > latest_progress_per_book[p.document_id].timestamp:
                latest_progress_per_book[p.document_id] = p
        
        # Sort by percentage read, descending
        sorted_progress_tuples = sorted(
            latest_progress_per_book.items(),
            key=lambda item: item[1].percentage,
            reverse=True,
        )

        result: List[Tuple[Book, float]] = []
        for doc_id, progress_entry in sorted_progress_tuples[:limit]:
            book = self.book_repository.get_book_by_id(doc_id) # document_id in Progress is Book.id
            if book:
                result.append((book, progress_entry.percentage))
        return result

    def get_reading_activity_over_time(
        self, user_id: UUID, period: str = "month" 
    ) -> Dict[str, float]:
        # Example: Count of books finished per period
        all_progress = self.progress_repository.get_all_progress_for_user(user_id)
        if not all_progress:
            return {}

        activity: Dict[str, float] = defaultdict(float)
        
        # Get latest progress for each book to determine finish date
        latest_progress_per_book = {}
        for p in all_progress:
            if p.document_id not in latest_progress_per_book or p.timestamp > latest_progress_per_book[p.document_id].timestamp:
                latest_progress_per_book[p.document_id] = p

        for doc_id, p in latest_progress_per_book.items():
            if p.percentage >= 0.95: # Consider finished
                if period == "month":
                    period_key = p.timestamp.strftime("%Y-%m") # e.g., "2023-01"
                elif period == "year":
                    period_key = p.timestamp.strftime("%Y") # e.g., "2023"
                else: # Default to day
                    period_key = p.timestamp.strftime("%Y-%m-%d")
                activity[period_key] += 1 # Increment count of books finished in this period
        
        # Sort by period key for chronological order
        return dict(sorted(activity.items()))

    def get_average_read_percentage(self, user_id: UUID) -> Optional[float]:
        all_progress = self.progress_repository.get_all_progress_for_user(user_id)
        if not all_progress:
            return None

        latest_progress_per_book = {}
        for p in all_progress:
            if p.document_id not in latest_progress_per_book or p.timestamp > latest_progress_per_book[p.document_id].timestamp:
                latest_progress_per_book[p.document_id] = p
        
        if not latest_progress_per_book:
            return None
            
        total_percentage = sum(p.percentage for p in latest_progress_per_book.values())
        return total_percentage / len(latest_progress_per_book)
