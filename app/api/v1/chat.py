from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError
from fastapi.encoders import jsonable_encoder

from app.core.auth import get_current_active_user
from app.core.security import verify_access_token
from app.core.ws import ws_manager
from app.core.redis import redis_client
from app.db.database import async_session, async_session_maker
from app.models.user import User
from app.schemas.conversation import ConversationCreateRequest, ConversationResponse
from app.schemas.message import MessageResponse
from app.schemas.ws import WSMessageIn, WSMessageOut, WSErrorOut
from app.services.conversation import (
    get_conversation_by_id,
    get_or_create_one_to_one_conversation,
    is_user_in_conversation,
)
from app.services.message import create_message, get_messages_for_conversation
from app.utils.user import get_user_by_id


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreateRequest,
    session: async_session,
    current_user: User = Depends(get_current_active_user)
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


@router.websocket("/ws/conversations/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: UUID):
    token = _get_bearer_token(websocket)
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    payload = verify_access_token(token)
    if payload is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    if user_id is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        user_uuid = UUID(user_id)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with async_session_maker() as session:
        user = await get_user_by_id(user_uuid, session)
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        conversation = await get_conversation_by_id(conversation_id, session)
        if not conversation:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        is_member = await is_user_in_conversation(conversation_id, user.id, session)
        if not is_member:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await websocket.accept()
    await ws_manager.connect(conversation_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            try:
                message_in = WSMessageIn.model_validate(data)
            except ValidationError as exc:
                await websocket.send_json(WSErrorOut(detail=str(exc)).model_dump())
                continue

            async with async_session_maker() as session:
                message = await create_message(
                    conversation_id=conversation_id,
                    sender_id=user_uuid,
                    content=message_in.content,
                    session=session,
                )

            message_out = MessageResponse.model_validate(message)
            payload_out = WSMessageOut(message=message_out).model_dump()

            try:
                # Convert UUIDs and Datetimes to strings so JSON can handle them
                json_compatible_payload = jsonable_encoder(payload_out)
                
                channel = f"conversation:{conversation_id}"
                # Publish the SAFE payload to Redis
                await redis_client.publish(channel, json.dumps(json_compatible_payload))
            except Exception as e:
                # If Redis fails, we send an error to the sender but DON'T disconnect them
                print(f"Redis Publish Error: {e}")
                await websocket.send_json({"type": "error", "detail": "Message saved but broadcast failed."})

    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(conversation_id, websocket)


def _get_bearer_token(websocket: WebSocket) -> str | None:
    auth_header = websocket.headers.get("authorization")
    if not auth_header:
        return None

    parts = auth_header.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]
