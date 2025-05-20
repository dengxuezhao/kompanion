from datetime import datetime
from typing import List, Optional
from uuid import UUID

from kompanion_py.models import Progress

from .exceptions import ProgressNotFoundError
from .repository import ProgressRepository


class ProgressService:
    def __init__(self, progress_repository: ProgressRepository):
        self.progress_repository = progress_repository

    def submit_progress(
        self,
        user_id: UUID,
        document_id: UUID, # This is Book.id
        percentage: float,
        progress_detail: Optional[str],
        device_name: str, # Name of the device (e.g., "KOReader")
        device_id: Optional[UUID], # This is Device.id, if the device is registered
        timestamp_int: int, # Unix timestamp
    ) -> Progress:
        # Convert Unix timestamp to datetime object
        dt_timestamp = datetime.utcfromtimestamp(timestamp_int)

        progress_data = Progress(
            document_id=document_id,
            user_id=user_id,
            percentage=percentage,
            progress_detail=progress_detail or "", # Ensure it's not None
            device_name=device_name,
            device_id=device_id,
            timestamp=dt_timestamp,
        )
        return self.progress_repository.save_progress(progress_data)

    def get_document_progress(
        self, user_id: UUID, document_id: UUID
    ) -> Optional[Progress]:
        progress = self.progress_repository.get_latest_progress(
            document_id=document_id, user_id=user_id
        )
        if not progress:
            # The subtask description doesn't explicitly ask to raise ProgressNotFoundError here,
            # but it's good practice if the expectation is that progress should exist.
            # For now, adhering to Optional[Progress] return type.
            # raise ProgressNotFoundError(document_id=str(document_id), user_id=str(user_id))
            return None
        return progress

    def get_all_user_progress(self, user_id: UUID) -> List[Progress]:
        return self.progress_repository.get_all_progress_for_user(user_id=user_id)

    def get_device_specific_progress(
        self, document_id: UUID, device_id: UUID
    ) -> Optional[Progress]:
        """
        Gets the latest progress for a specific document and device.
        This might be useful for KOReader sync which identifies progress by document and device.
        """
        progress = self.progress_repository.get_progress_for_document_and_device(
            document_id=document_id, device_id=device_id
        )
        # if not progress:
        #     raise ProgressNotFoundError(document_id=str(document_id), device_id=str(device_id))
        return progress
