from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class ConversationCreateRequest(BaseModel):
    recipient_id: UUID = Field(..., description="User id to start a 1-to-1 conversation with")


class ConversationResponse(BaseModel):
    id: UUID = Field(..., description="Conversation id")
    is_group: bool = Field(..., description="Indicates if conversation is a group")
    created_at: datetime = Field(..., description="Created timestamp")

    model_config = ConfigDict(from_attributes=True)
