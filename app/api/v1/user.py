from fastapi import APIRouter, status
from typing import List
from uuid import UUID

from app.db.database import async_session
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.auth import get_current_active_user_dependency
from app.services.user import (
    create_user_service,
    get_single_user_service,
    get_all_users_service,
    update_user_service,
    delete_user_service,
)

router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: async_session):
    return await create_user_service(user, session)


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    session: async_session,
    skip: int = 0,
    limit: int = 10,
):
    return await get_all_users_service(skip, limit, session)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID, session: async_session):
    return await get_single_user_service(user_id, session)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    session: async_session,
    current_user: get_current_active_user_dependency,
):
    return await update_user_service(user_id, user_update, session)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    session: async_session,
    current_user: get_current_active_user_dependency,
):
    return await delete_user_service(user_id, session)
