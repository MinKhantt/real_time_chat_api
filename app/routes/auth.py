from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import (
    get_current_active_user_dependency,
)
from app.db.database import DbSession
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.user import create_user_service
from app.services.auth import login_for_access_token_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate, db: DbSession):
    return create_user_service(user, db)


@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    db: DbSession, form_data: OAuth2PasswordRequestForm = Depends()
):
    return login_for_access_token_service(db, form_data)


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: get_current_active_user_dependency):
    return current_user
