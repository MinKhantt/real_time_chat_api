from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.auth import get_current_active_user
from app.db.database import async_session
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreateRequest,
    ConversationListItem,
    ConversationResponse,
)
from app.schemas.message import MessageResponse
from app.services.conversation import (
    get_or_create_one_to_one_conversation,
    is_user_in_conversation,
    list_user_conversations,
)
from app.services.message import get_messages_for_conversation
from app.utils.user import get_user_by_id


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/conversations", response_model=list[ConversationListItem])
async def get_my_conversations(
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    return await list_user_conversations(current_user.id, session)


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreateRequest,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    if payload.recipient_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create a conversation with yourself",
        )

    recipient = await get_user_by_id(payload.recipient_id, session)
    if not recipient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found")

    conversation = await get_or_create_one_to_one_conversation(
        current_user.id, payload.recipient_id, session
    )
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: UUID,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    is_member = await is_user_in_conversation(conversation_id, current_user.id, session)
    if not is_member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    messages = await get_messages_for_conversation(conversation_id, skip, limit, session)
    return messages
