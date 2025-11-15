from fastapi import APIRouter, status
from typing import List
from uuid import UUID

from app.db.database import DbSession
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
def create_user(user: UserCreate, db: DbSession):
    return create_user_service(user, db)


@router.get("/", response_model=List[UserResponse])
def get_all_users(db: DbSession):
    return get_all_users_service(db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: DbSession):
    return get_single_user_service(user_id, db)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: DbSession,
    current_user: get_current_active_user_dependency,
):
    return update_user_service(user_id, user_update, db)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID, db: DbSession, current_user: get_current_active_user_dependency
):
    return delete_user_service(user_id, db)
