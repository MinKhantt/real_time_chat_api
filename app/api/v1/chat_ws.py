from uuid import UUID
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

from app.core.redis import redis_client
from app.core.security import verify_access_token
from app.core.ws import ws_manager
from app.db.database import async_session_maker
from app.schemas.message import MessageResponse
from app.schemas.ws import WSErrorOut, WSMessageIn, WSMessageOut
from app.services.conversation import get_conversation_by_id, is_user_in_conversation
from app.services.message import create_message
from app.utils.user import get_user_by_id


router = APIRouter(prefix="/chat", tags=["Chat"])


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
                json_compatible_payload = jsonable_encoder(payload_out)
                channel = f"conversation:{conversation_id}"
                await redis_client.publish(channel, json.dumps(json_compatible_payload))
            except Exception:
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
