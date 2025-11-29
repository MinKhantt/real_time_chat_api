from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator, Annotated
from fastapi import Depends

from app.core.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

async_session_maker  = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession
)

Base = declarative_base()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async_session = Annotated[AsyncSession, Depends(get_async_session)]

# DbSession = Annotated[async_sessionmaker, Depends(get_db)]
