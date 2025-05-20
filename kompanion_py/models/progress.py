from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Progress(BaseModel):
    document_id: UUID = Field(..., alias="document") # Corresponds to Book.id
    user_id: Optional[UUID] = None # Corresponds to User.id
    percentage: float
    progress_detail: str = Field(..., alias="progress")  # Detailed progress string from KOReader
    device_name: str = Field(..., alias="device")
    device_id: Optional[UUID] = None # Corresponds to Device.id
    timestamp: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "document_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", # Book ID
                "user_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef", # User ID
                "percentage": 0.5,
                "progress": "page 50 of 100",
                "device_name": "KOReader",
                "device_id": "c4a5b6d7-e8f9-0123-4567-890abcdef0", # Device ID
                "timestamp": "2023-01-01T12:00:00Z",
            }
        }
