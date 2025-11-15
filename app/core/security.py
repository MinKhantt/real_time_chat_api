from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import re

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

SPECIAL_CHARACTERS = r"[@#$%^&*!]"


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def is_token_expired(token: str) -> bool:
    """Check if a JWT token is expired."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        if exp is None:
            return True
        expiration_time = datetime.fromtimestamp(exp, timezone.utc)
        return datetime.now(timezone.utc) > expiration_time
    except JWTError:
        return True


def is_strong_password(password: str) -> bool:
    """Check if the password is strong enough.

    A strong password must be at least 8 characters long, contain at least one uppercase letter,
    one lowercase letter, one digit, and one special character.
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(SPECIAL_CHARACTERS, password):
        return False
    return True


def refresh_access_token(
    token: str, expires_delta: timedelta | None = None
) -> str | None:
    """Refresh an access token by creating a new one with updated expiration."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False},
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        new_data = {"sub": user_id}
        return create_access_token(new_data, expires_delta)
    except JWTError:
        return None


def invalidate_token(token: str) -> bool:
    """Invalidate a token (dummy implementation, as JWTs are stateless)."""
    # In a real-world scenario, you would store the token in a blacklist.
    return True
