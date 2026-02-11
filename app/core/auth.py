from datetime import timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    verify_access_token,
    verify_password,
    create_access_token,
    refresh_access_token as refresh_token,
)
from app.models.user import User
from app.schemas.token import TokenResponse
from app.utils.user import get_user_by_id, get_user_by_email
from app.db.database import get_async_session
from app.exceptions.auth import InvalidCredentialsError, InactiveUserError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def authenticate_user(
    session: AsyncSession, email: str, password: str
) -> User | None:
    user = await get_user_by_email(email, session)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    payload = verify_access_token(token)
    if payload is None:
        raise InvalidCredentialsError()

    sub = payload.get("sub")
    if sub is None:
        raise InvalidCredentialsError()

    try:
        user_id = UUID(sub)
    except ValueError:
        raise InvalidCredentialsError()

    user = await get_user_by_id(user_id, session)

    if user is None:
        raise InvalidCredentialsError()

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise InactiveUserError()
    return current_user


get_current_active_user_dependency = Annotated[User, Depends(get_current_active_user)]


def create_token_for_user(user: User) -> TokenResponse:
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=expires
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


def refresh_access_token(token: str) -> str | None:
    """Refresh an access token, even if it's expired.
    
    This allows users to refresh their token after expiration without needing to login again.
    """
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return refresh_token(token, expires_delta=expires)
