from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import get_current_active_user, get_current_active_user_dependency
from app.db.database import async_session
from app.models.user import User
from app.schemas.token import TokenResponse, UserRegisterResponse, RefreshTokenRequest
from app.schemas.user import UserCreate, UserResponse
from app.services.user import create_user_service
from app.services.auth import (
    login_for_access_token_service,
    signup_service,
    refresh_token_service,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate, 
    session: async_session
):
    return await signup_service(user, session)


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    session: async_session,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return await login_for_access_token_service(session, form_data)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token_request: RefreshTokenRequest,
):
    return await refresh_token_service(refresh_token_request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user
