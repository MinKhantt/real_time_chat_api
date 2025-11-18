from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import get_current_active_user_dependency
from app.db.database import async_session
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.user import create_user_service
from app.services.auth import login_for_access_token_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, session: async_session):
    return await create_user_service(user, session)


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    session: async_session,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return await login_for_access_token_service(session, form_data)


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user=Depends(get_current_active_user_dependency),
):
    return current_user
