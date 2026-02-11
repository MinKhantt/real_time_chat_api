from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember


async def get_conversation_by_id(conversation_id: UUID, session: AsyncSession) -> Conversation | None:
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    return result.scalar_one_or_none()


async def is_user_in_conversation(
    conversation_id: UUID, user_id: UUID, session: AsyncSession
) -> bool:
    result = await session.execute(
        select(ConversationMember)
        .where(ConversationMember.conversation_id == conversation_id)
        .where(ConversationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


async def get_one_to_one_conversation_between(
    user_id: UUID, recipient_id: UUID, session: AsyncSession
) -> Conversation | None:
    # Conversations where both users are members
    both_members_subq = (
        select(ConversationMember.conversation_id)
        .where(ConversationMember.user_id.in_([user_id, recipient_id]))
        .group_by(ConversationMember.conversation_id)
        .having(func.count(ConversationMember.user_id) == 2)
        .subquery()
    )

    # Conversations with exactly 2 total members
    total_members_subq = (
        select(ConversationMember.conversation_id)
        .group_by(ConversationMember.conversation_id)
        .having(func.count(ConversationMember.user_id) == 2)
        .subquery()
    )

    result = await session.execute(
        select(Conversation)
        .where(Conversation.is_group.is_(False))
        .where(Conversation.id.in_(select(both_members_subq.c.conversation_id)))
        .where(Conversation.id.in_(select(total_members_subq.c.conversation_id)))
    )
    return result.scalar_one_or_none()


async def get_or_create_one_to_one_conversation(
    user_id: UUID, recipient_id: UUID, session: AsyncSession
) -> Conversation:
    existing = await get_one_to_one_conversation_between(user_id, recipient_id, session)
    if existing:
        return existing

    conversation = Conversation(is_group=False)
    session.add(conversation)
    await session.flush()

    session.add_all(
        [
            ConversationMember(conversation_id=conversation.id, user_id=user_id),
            ConversationMember(conversation_id=conversation.id, user_id=recipient_id),
        ]
    )
    await session.commit()
    await session.refresh(conversation)
    return conversation
