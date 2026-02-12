from uuid import UUID
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.conversation_member import ConversationMember
from app.models.message import Message

ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_MEMBER = "member"


async def get_conversation_by_id(conversation_id: UUID, session: AsyncSession) -> Conversation | None:
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    return result.scalar_one_or_none()


async def get_membership(
    conversation_id: UUID, user_id: UUID, session: AsyncSession
) -> ConversationMember | None:
    result = await session.execute(
        select(ConversationMember)
        .where(ConversationMember.conversation_id == conversation_id)
        .where(ConversationMember.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def is_user_in_conversation(
    conversation_id: UUID, user_id: UUID, session: AsyncSession
) -> bool:
    membership = await get_membership(conversation_id, user_id, session)
    return membership is not None


async def get_conversation_member_count(conversation_id: UUID, session: AsyncSession) -> int:
    result = await session.execute(
        select(func.count(ConversationMember.id)).where(
            ConversationMember.conversation_id == conversation_id
        )
    )
    return int(result.scalar_one() or 0)


async def get_conversation_members(
    conversation_id: UUID, session: AsyncSession
) -> list[ConversationMember]:
    result = await session.execute(
        select(ConversationMember)
        .where(ConversationMember.conversation_id == conversation_id)
        .order_by(ConversationMember.joined_at.asc())
    )
    return list(result.scalars().all())


async def get_one_to_one_conversation_between(
    user_id: UUID, recipient_id: UUID, session: AsyncSession
) -> Conversation | None:
    both_members_subq = (
        select(ConversationMember.conversation_id)
        .where(ConversationMember.user_id.in_([user_id, recipient_id]))
        .group_by(ConversationMember.conversation_id)
        .having(func.count(ConversationMember.user_id) == 2)
        .subquery()
    )

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
            ConversationMember(
                conversation_id=conversation.id,
                user_id=user_id,
                role=ROLE_MEMBER,
            ),
            ConversationMember(
                conversation_id=conversation.id,
                user_id=recipient_id,
                role=ROLE_MEMBER,
            ),
        ]
    )
    await session.commit()
    await session.refresh(conversation)
    return conversation


async def create_group_conversation(
    creator_id: UUID,
    name: str,
    description: str | None,
    avatar_url: str | None,
    member_ids: list[UUID],
    session: AsyncSession,
) -> Conversation:
    unique_members = set(member_ids)
    unique_members.discard(creator_id)

    conversation = Conversation(
        is_group=True,
        name=name,
        description=description,
        avatar_url=avatar_url,
        created_by=creator_id,
    )
    session.add(conversation)
    await session.flush()

    session.add(
        ConversationMember(
            conversation_id=conversation.id,
            user_id=creator_id,
            role=ROLE_OWNER,
        )
    )

    for member_id in unique_members:
        session.add(
            ConversationMember(
                conversation_id=conversation.id,
                user_id=member_id,
                role=ROLE_MEMBER,
            )
        )

    await session.commit()
    await session.refresh(conversation)
    return conversation


async def update_group_conversation(
    conversation: Conversation,
    name: str | None,
    description: str | None,
    avatar_url: str | None,
    session: AsyncSession,
) -> Conversation:
    if name is not None:
        conversation.name = name
    if description is not None:
        conversation.description = description
    if avatar_url is not None:
        conversation.avatar_url = avatar_url

    await session.commit()
    await session.refresh(conversation)
    return conversation


async def add_group_member(
    conversation_id: UUID, user_id: UUID, session: AsyncSession
) -> ConversationMember:
    membership = ConversationMember(
        conversation_id=conversation_id,
        user_id=user_id,
        role=ROLE_MEMBER,
    )
    session.add(membership)
    await session.commit()
    await session.refresh(membership)
    return membership


async def remove_group_member(
    conversation_id: UUID, user_id: UUID, session: AsyncSession
) -> None:
    membership = await get_membership(conversation_id, user_id, session)
    if not membership:
        return

    await session.delete(membership)
    await session.commit()


async def update_member_role(
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    session: AsyncSession,
) -> ConversationMember | None:
    membership = await get_membership(conversation_id, user_id, session)
    if not membership:
        return None

    membership.role = role
    await session.commit()
    await session.refresh(membership)
    return membership


async def list_user_conversations(
    user_id: UUID, session: AsyncSession
) -> list[dict]:
    conversations_result = await session.execute(
        select(Conversation)
        .join(
            ConversationMember,
            ConversationMember.conversation_id == Conversation.id,
        )
        .where(ConversationMember.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = list(conversations_result.scalars().all())

    items: list[dict] = []
    for conversation in conversations:
        message_result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_message = message_result.scalar_one_or_none()

        unread_result = await session.execute(
            select(func.count(Message.id)).where(
                and_(
                    Message.conversation_id == conversation.id,
                    Message.sender_id != user_id,
                    Message.is_read.is_(False),
                )
            )
        )
        unread_count = int(unread_result.scalar_one() or 0)

        member_count = await get_conversation_member_count(conversation.id, session)

        items.append(
            {
                "id": conversation.id,
                "is_group": conversation.is_group,
                "name": conversation.name,
                "description": conversation.description,
                "avatar_url": conversation.avatar_url,
                "created_at": conversation.created_at,
                "last_message": last_message.content if last_message else None,
                "last_message_at": last_message.created_at if last_message else None,
                "unread_count": unread_count,
                "member_count": member_count,
            }
        )

    return items


def can_manage_members(role: str) -> bool:
    return role in {ROLE_OWNER, ROLE_ADMIN}


def can_update_group(role: str) -> bool:
    return role in {ROLE_OWNER, ROLE_ADMIN}
