from pydantic import BaseModel, Field
from typing import Optional, Literal

class RoomCreate(BaseModel):
    creator: str = Field(max_length=255)
    comment: Optional[str] = Field(None, max_length=255)
    time_control: int = Field(default=600, gt=0, le=3600)

class RoomResponse(BaseModel):
    id: str
    creator: str
    comment: Optional[str] = None
    time_control: int
    player_white: Optional[str] = None
    player_black: Optional[str] = None
    status: Literal["waiting", "playing", "finished"]
    time_white: Optional[float] = None
    time_black: Optional[float] = None

    class Config:
        from_attributes = True

class JoinRoomRequest(BaseModel):
    player_id: str = Field(max_length=255)
    color: Literal["white", "black"]

class JoinRoomResponse(RoomResponse):
    token: str
