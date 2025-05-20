from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Device(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    hashed_password: str  # For KOReader sync
    user_id: Optional[UUID] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "name": "My KOReader Device",
                "hashed_password": "anothersecretpassword",
                "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            }
        }
