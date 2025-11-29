from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import json

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import is_strong_password, get_hashed_password
from app.utils.user import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_email_excluding_id,
    get_all_users,
)
from app.core.redis import redis_client
from app.exceptions.user import (
    UserNotFoundError,
    UserEmailExistsError,
    UserEmailAlreadyRegisteredError,
    WeakPasswordError,
)


async def create_user_service(user: UserCreate, session: AsyncSession):
    existing_user = await get_user_by_email(user.email, session)

    if existing_user:
        raise UserEmailExistsError()

    if not is_strong_password(user.password):
        raise WeakPasswordError()

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

    redis_key = f"user:{user_id}"

    cached_user = await redis_client.get(redis_key)
    if cached_user:
        return json.loads(cached_user)

    user = await get_user_by_id(user_id, session)

    if not user:
        raise UserNotFoundError()
    
    # Convert ORM object to dict before caching and returning 
    # (using to_dict() for consistency with get_all_users_service)
    user_dict = user.to_dict()
    
    await redis_client.set(redis_key, json.dumps(user_dict), ex=50)
    return user_dict


async def get_all_users_service(skip: int, limit: int, session: AsyncSession):
    redis_key = f"users:{skip}:{limit}"
    cached_user = await redis_client.get(redis_key)
    if cached_user:
        return json.loads(cached_user)

    users = await get_all_users(skip, limit, session)

    users_dict = [user.to_dict() for user in users]

    await redis_client.set(redis_key, json.dumps(users_dict), ex=60)

    return users_dict


async def update_user_service(
    user_id: UUID,
    user_update: UserUpdate,
    session: AsyncSession,
):
    user = await get_user_by_id(user_id, session)
    if not user:
        raise UserNotFoundError()

    if user_update.email:
        existing_user = await get_user_by_email_excluding_id(
            user_update.email, user_id, session
        )
        if existing_user:
            raise UserEmailAlreadyRegisteredError()

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
        raise UserNotFoundError()

    await session.delete(user)
    await session.commit()
    return None
