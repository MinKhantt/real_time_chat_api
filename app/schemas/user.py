from pydantic import BaseModel, Field, EmailStr
from uuid import UUID
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="The user's email address")
    password: str = Field(..., description="The user's password")
    full_name: Optional[str] = Field(None, description="The user's full name")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="The user's email address")
    full_name: Optional[str] = Field(None, description="The user's full name")
    is_active: Optional[bool] = Field(None, description="Indicates if the user is active")  

class UserResponse(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the user")
    email: EmailStr = Field(..., description="The user's email address")
    full_name: Optional[str] = Field(None, description="The user's full name")
    is_active: bool = Field(..., description="Indicates if the user is active")
    is_superuser: bool = Field(..., description="Indicates if the user has superuser privileges")
    created_at: datetime = Field(..., description="Timestamp when the user was created")
    updated_at: Optional[datetime] = Field(None, description="Timestamp when the user was last updated")

    class Config:
        from_attributes = True 

        