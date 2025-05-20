import abc
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from kompanion_py.models import Progress


class ProgressRepository(abc.ABC):
    @abc.abstractmethod
    def save_progress(self, progress: Progress) -> Progress:
        """Saves (upserts) progress for a document, user, and device."""
        pass

    @abc.abstractmethod
    def get_latest_progress(
        self, document_id: UUID, user_id: UUID
    ) -> Optional[Progress]:
        """Gets the most recent progress for a specific document and user."""
        pass

    @abc.abstractmethod
    def get_all_progress_for_user(self, user_id: UUID) -> List[Progress]:
        """Gets all progress entries for a specific user."""
        pass

    @abc.abstractmethod
    def get_progress_for_document_and_device(
        self, document_id: UUID, device_id: UUID
    ) -> Optional[Progress]:
        """Gets the latest progress for a specific document and device."""
        pass


class InMemoryProgressRepository(ProgressRepository):
    def __init__(self):
        # Stores progress entries. A list is simple, but for upserting and lookups,
        # a dictionary keyed by a tuple (document_id, user_id, device_id) might be more efficient.
        # For now, a list will work, but performance might degrade with many entries.
        self._progress_entries: List[Progress] = []

    def save_progress(self, progress: Progress) -> Progress:
        # Attempt to find an existing entry to update.
        # KOReader sync primarily identifies progress by (document_id, device_id)
        # and timestamp for ordering. User_id is for server-side organization.
        
        # If progress is uniquely identified by (document_id, device_id) for KOReader,
        # we might want to replace based on that, or always append and rely on get_latest.
        # The current requirement implies an upsert.
        # A simple approach for InMemory: remove old, add new.
        
        # Filter out any existing progress for the same document and device.
        # This assumes that for a given (document, device) pair, we only care about the latest.
        # If user_id is also a key, the filter needs to include it.
        # Let's assume progress is unique per (document_id, device_id) for KOReader sync purposes,
        # and user_id is for server-side association.
        
        new_entries = []
        updated = False
        for entry in self._progress_entries:
            if (
                entry.document_id == progress.document_id
                and entry.device_id == progress.device_id # device_id must exist for this logic
            ):
                # Replace if the new one is more recent or if timestamps are same (overwrite)
                if progress.timestamp >= entry.timestamp:
                    if not updated: # Add the new progress only once
                        new_entries.append(progress.copy(deep=True))
                        updated = True
                else: # Keep the old one if it's newer
                    new_entries.append(entry)
            else:
                new_entries.append(entry)
        
        if not updated: # If no existing entry was found and replaced
            new_entries.append(progress.copy(deep=True))
            
        self._progress_entries = new_entries
        return progress.copy(deep=True)


    def get_latest_progress(
        self, document_id: UUID, user_id: UUID
    ) -> Optional[Progress]:
        user_doc_progress = [
            p
            for p in self._progress_entries
            if p.document_id == document_id and p.user_id == user_id
        ]
        if not user_doc_progress:
            return None
        # Sort by timestamp descending to get the latest
        user_doc_progress.sort(key=lambda p: p.timestamp, reverse=True)
        return user_doc_progress[0].copy(deep=True)

    def get_all_progress_for_user(self, user_id: UUID) -> List[Progress]:
        user_progress = [
            p.copy(deep=True)
            for p in self._progress_entries
            if p.user_id == user_id
        ]
        # Optionally sort them, e.g., by document and then by timestamp
        user_progress.sort(key=lambda p: (p.document_id, p.timestamp), reverse=True)
        return user_progress

    def get_progress_for_document_and_device(
        self, document_id: UUID, device_id: UUID
    ) -> Optional[Progress]:
        doc_device_progress = [
            p
            for p in self._progress_entries
            if p.document_id == document_id and p.device_id == device_id
        ]
        if not doc_device_progress:
            return None
        # Sort by timestamp descending
        doc_device_progress.sort(key=lambda p: p.timestamp, reverse=True)
        return doc_device_progress[0].copy(deep=True)
