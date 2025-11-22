from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_id(user_id, session: AsyncSession):
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_email(email, session: AsyncSession):
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_email_excluding_id(email: str, user_id, session: AsyncSession):
    query = select(User).where(and_(User.email == email, User.id != user_id))
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_all_users(skip: int, limit: int, session: AsyncSession):
    result = await session.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()
