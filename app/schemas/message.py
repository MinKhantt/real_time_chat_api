from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
