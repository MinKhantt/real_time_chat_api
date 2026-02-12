from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


class ConversationCreateRequest(BaseModel):
    recipient_id: UUID = Field(..., description="User id to start a 1-to-1 conversation with")


class ConversationResponse(BaseModel):
    id: UUID = Field(..., description="Conversation id")
    is_group: bool = Field(..., description="Indicates if conversation is a group")
    name: str | None = Field(None, description="Group name")
    description: str | None = Field(None, description="Group description")
    avatar_url: str | None = Field(None, description="Group avatar URL")
    created_by: UUID | None = Field(None, description="Creator user id")
    created_at: datetime = Field(..., description="Created timestamp")

    model_config = ConfigDict(from_attributes=True)


class GroupCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(None, max_length=1000)
    avatar_url: str | None = Field(None, max_length=255)
    member_ids: list[UUID] = Field(default_factory=list)


class GroupUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = Field(None, max_length=1000)
    avatar_url: str | None = Field(None, max_length=255)


class AddMemberRequest(BaseModel):
    user_id: UUID


class UpdateMemberRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(admin|member)$")


class GroupMemberResponse(BaseModel):
    user_id: UUID
    role: str
    joined_at: datetime


class ConversationListItem(BaseModel):
    id: UUID
    is_group: bool
    name: str | None
    description: str | None
    avatar_url: str | None
    created_at: datetime
    last_message: str | None
    last_message_at: datetime | None
    unread_count: int
    member_count: int


class GroupDetailResponse(BaseModel):
    id: UUID
    is_group: bool
    name: str
    description: str | None
    avatar_url: str | None
    created_by: UUID | None
    created_at: datetime
    member_count: int

    model_config = ConfigDict(from_attributes=True)
