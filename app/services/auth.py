from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import authenticate_user, create_token_for_user, refresh_access_token
from app.schemas.token import UserRegisterResponse, TokenResponse
from app.schemas.user import UserCreate
from app.services.user import create_user_service
from app.exceptions.auth import IncorrectCredentialsError, InvalidCredentialsError


async def signup_service(
    user: UserCreate,
    session: AsyncSession
):
    new_user = await create_user_service(user, session)

    token_data =  create_token_for_user(new_user)

    return UserRegisterResponse(
        user=new_user,
        access_token=token_data.access_token,
        token_type=token_data.token_type
    )




async def login_for_access_token_service(
    session: AsyncSession,  
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise IncorrectCredentialsError()

    return create_token_for_user(user)


async def refresh_token_service(refresh_token: str) -> TokenResponse:
    """Refresh an access token using a valid refresh token."""
    new_token = refresh_access_token(refresh_token)
    
    if new_token is None:
        raise InvalidCredentialsError(detail="Invalid or expired refresh token")
    
    return TokenResponse(access_token=new_token, token_type="bearer")
