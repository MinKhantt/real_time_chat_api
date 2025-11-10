from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import authenticate_user, create_token_for_user, get_current_active_user_dependency
from app.db.database import DbSession
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User
from app.core.security import is_strong_password, get_hashed_password

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: DbSession):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if not is_strong_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet strength requirements",
        )
    
    hashed_password = get_hashed_password(user.password)

    new_user = User(
        **user.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(
    db: DbSession,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_token_for_user(user)

@router.get("/me", response_model=UserResponse)
def read_users_me(
    current_user: get_current_active_user_dependency
):
    return current_user
