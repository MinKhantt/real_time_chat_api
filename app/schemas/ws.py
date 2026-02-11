from pydantic import BaseModel, Field
from typing import Literal
from app.schemas.message import MessageResponse


class WSMessageIn(BaseModel):
    type: Literal["message.send"] = Field(..., description="Client message type")
    content: str = Field(..., min_length=1, max_length=5000)


class WSMessageOut(BaseModel):
    type: Literal["message.new"] = "message.new"
    message: MessageResponse


class WSErrorOut(BaseModel):
    type: Literal["error"] = "error"
    detail: str
