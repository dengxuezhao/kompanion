from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    hashed_password: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "username": "testuser",
                "hashed_password": "supersecrethashedpassword",
            }
        }
