from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_active_user
from app.db.database import async_session
from app.models.user import User
from app.schemas.conversation import (
    AddMemberRequest,
    ConversationResponse,
    GroupCreateRequest,
    GroupDetailResponse,
    GroupMemberResponse,
    GroupUpdateRequest,
    UpdateMemberRoleRequest,
)
from app.services.conversation import (
    ROLE_OWNER,
    add_group_member,
    can_manage_members,
    can_update_group,
    create_group_conversation,
    get_conversation_by_id,
    get_conversation_member_count,
    get_conversation_members,
    get_membership,
    remove_group_member,
    update_group_conversation,
    update_member_role,
)
from app.utils.user import get_user_by_id


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/groups", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    payload: GroupCreateRequest,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    unique_member_ids = set(payload.member_ids)
    unique_member_ids.discard(current_user.id)

    for member_id in unique_member_ids:
        user = await get_user_by_id(member_id, session)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found: {member_id}",
            )

    conversation = await create_group_conversation(
        creator_id=current_user.id,
        name=payload.name,
        description=payload.description,
        avatar_url=payload.avatar_url,
        member_ids=list(unique_member_ids),
        session=session,
    )
    return conversation


@router.get("/groups/{conversation_id}", response_model=GroupDetailResponse)
async def get_group_detail(
    conversation_id: UUID,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    conversation = await _get_group_or_404(conversation_id, session)
    member = await get_membership(conversation_id, current_user.id, session)
    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")

    member_count = await get_conversation_member_count(conversation_id, session)
    return {
        "id": conversation.id,
        "is_group": conversation.is_group,
        "name": conversation.name,
        "description": conversation.description,
        "avatar_url": conversation.avatar_url,
        "created_by": conversation.created_by,
        "created_at": conversation.created_at,
        "member_count": member_count,
    }


@router.patch("/groups/{conversation_id}", response_model=ConversationResponse)
async def update_group(
    conversation_id: UUID,
    payload: GroupUpdateRequest,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    conversation = await _get_group_or_404(conversation_id, session)
    membership = await get_membership(conversation_id, current_user.id, session)
    if not membership or not can_update_group(membership.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return await update_group_conversation(
        conversation=conversation,
        name=payload.name,
        description=payload.description,
        avatar_url=payload.avatar_url,
        session=session,
    )


@router.get("/groups/{conversation_id}/members", response_model=list[GroupMemberResponse])
async def get_group_members(
    conversation_id: UUID,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    await _ensure_group_member(conversation_id, current_user.id, session)
    members = await get_conversation_members(conversation_id, session)
    return [
        {
            "user_id": member.user_id,
            "role": member.role,
            "joined_at": member.joined_at,
        }
        for member in members
    ]


@router.post("/groups/{conversation_id}/members", response_model=GroupMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    conversation_id: UUID,
    payload: AddMemberRequest,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    await _ensure_group_manager(conversation_id, current_user.id, session)

    user = await get_user_by_id(payload.user_id, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existing = await get_membership(conversation_id, payload.user_id, session)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already a member")

    member = await add_group_member(conversation_id, payload.user_id, session)
    return {
        "user_id": member.user_id,
        "role": member.role,
        "joined_at": member.joined_at,
    }


@router.delete("/groups/{conversation_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    conversation_id: UUID,
    user_id: UUID,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    await _ensure_group_manager(conversation_id, current_user.id, session)

    membership = await get_membership(conversation_id, user_id, session)
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    if membership.role == ROLE_OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove owner")

    await remove_group_member(conversation_id, user_id, session)


@router.patch("/groups/{conversation_id}/members/{user_id}/role", response_model=GroupMemberResponse)
async def patch_member_role(
    conversation_id: UUID,
    user_id: UUID,
    payload: UpdateMemberRoleRequest,
    session: async_session,
    current_user: User = Depends(get_current_active_user),
):
    await _ensure_group_manager(conversation_id, current_user.id, session)

    membership = await get_membership(conversation_id, user_id, session)
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    if membership.role == ROLE_OWNER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change owner role")

    updated = await update_member_role(conversation_id, user_id, payload.role, session)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    return {
        "user_id": updated.user_id,
        "role": updated.role,
        "joined_at": updated.joined_at,
    }


async def _get_group_or_404(conversation_id: UUID, session: async_session):
    conversation = await get_conversation_by_id(conversation_id, session)
    if not conversation or not conversation.is_group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return conversation


async def _ensure_group_member(conversation_id: UUID, user_id: UUID, session: async_session):
    await _get_group_or_404(conversation_id, session)
    membership = await get_membership(conversation_id, user_id, session)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member")
    return membership


async def _ensure_group_manager(conversation_id: UUID, user_id: UUID, session: async_session):
    membership = await _ensure_group_member(conversation_id, user_id, session)
    if not can_manage_members(membership.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return membership
