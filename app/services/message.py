from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


async def create_message(
    conversation_id: UUID, sender_id: UUID, content: str, session: AsyncSession
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def get_messages_for_conversation(
    conversation_id: UUID, skip: int, limit: int, session: AsyncSession
) -> list[Message]:
    result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())
