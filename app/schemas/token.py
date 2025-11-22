from pydantic import BaseModel, Field
from uuid import UUID


class TokenData(BaseModel):
    user_id: UUID = Field(
        ..., description="Unique identifier for the user associated with the token"
    )


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="The access token string")
    token_type: str = Field(..., description="Type of the token, typically 'bearer'")
