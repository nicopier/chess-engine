from pydantic import BaseModel, Field
from typing import Optional, Literal

class RoomCreate(BaseModel):
    id: str = Field(max_length=255, description="Unique identifier for the room")
    time_control: int = Field(default=600, gt=0, le=3600, description="Time per player in seconds")
    

class RoomResponse(BaseModel):
    id: str = Field(max_length=255, description="Unique identifier for the room")
    fen: str = Field(max_length=255, description="FEN string representing the current state of the chess game")
    player_white: Optional[str] = Field(None, max_length=255, description="Identifier for the white player")
    player_black: Optional[str] = Field(None, max_length=255, description="Identifier for the black player")
    status: Literal["waiting","playing","finished"] = Field(description="Current status of the room")
    time_white: Optional[float] = None
    time_black: Optional[float] = None

    class Config:
        from_attributes = True
    
class JoinRoomRequest(BaseModel):
    player_id: str =Field(max_length=255, description="Unique identifier for the player")
    color: Literal["white", "black"] = Field(description="Color the player wants to join as")
    