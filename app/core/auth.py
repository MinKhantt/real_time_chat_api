from datetime import datetime, timezone, timedelta
from jose import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_access_token, verify_password, create_access_token
from app.models.user import User
from app.schemas.token import TokenResponse
from app.utils.user import get_user_by_id, get_user_by_email
from app.db.database import get_async_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_access_token(token)
    if payload is None:
        raise credentials_exception

    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception

    try:
        user_id = UUID(sub)
    except ValueError:
        raise credentials_exception

    user = await get_user_by_id(user_id, session)

    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


get_current_active_user_dependency = Annotated[User, Depends(get_current_active_user)]


def create_token_for_user(user: User) -> TokenResponse:
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=expires
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


def refresh_access_token(token: str) -> str | None:
    payload = verify_access_token(token)
    if payload is None:
        return None

    sub = payload.get("sub")
    if sub is None:
        return None

    new_expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    new_payload = {
        "sub": sub,
        "exp": new_expire,
    }

    new_token = jwt.encode(
        new_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return new_token
