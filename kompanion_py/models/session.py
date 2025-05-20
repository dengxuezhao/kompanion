from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Session(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    session_key: str
    user_id: UUID
    user_agent: Optional[str] = None
    client_ip: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "c4a5b6d7-e8f9-0123-4567-890abcdef0",
                "session_key": "averylongandrandomsessionkey",
                "user_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
                "client_ip": "192.168.1.100",
                "created_at": "2023-01-01T12:00:00Z",
                "expires_at": "2023-01-02T12:00:00Z",
            }
        }
