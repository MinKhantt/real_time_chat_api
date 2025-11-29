from pydantic import BaseModel, Field
from uuid import UUID

from app.schemas.user import UserResponse


class TokenData(BaseModel):
    user_id: UUID = Field(
        ..., description="Unique identifier for the user associated with the token"
    )


class UserRegisterResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="The access token string")
    token_type: str = Field(..., description="Type of the token, typically 'bearer'")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="The refresh token to exchange for a new access token")