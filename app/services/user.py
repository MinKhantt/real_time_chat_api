from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import is_strong_password, get_hashed_password
from app.utils.user import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_email_excluding_id,
    get_all_users,
)


async def create_user_service(user: UserCreate, session: AsyncSession):
    existing_user = await get_user_by_email(user.email, session)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )

    if not is_strong_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet strength requirements.",
        )

    hashed_password = get_hashed_password(user.password)

    new_user = User(
        **user.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


async def get_single_user_service(user_id: UUID, session: AsyncSession):
    user = await get_user_by_id(user_id, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


async def get_all_users_service(skip: int, limit: int, session: AsyncSession):
    return await get_all_users(skip, limit, session)


async def update_user_service(
    user_id: UUID,
    user_update: UserUpdate,
    session: AsyncSession,
):
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_update.email:
        existing_user = await get_user_by_email_excluding_id(
            user_update.email, user_id, session
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user",
            )

    # for var, value in vars(user_update).items():
    #     if value is not None:
    #         setattr(user, var, value)
    for var, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, var, value)


    await session.commit()
    await session.refresh(user)
    return user


async def delete_user_service(
    user_id: UUID,
    session: AsyncSession,
):
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await session.delete(user)
    await session.commit()
    return None
