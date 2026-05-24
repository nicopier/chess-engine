import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Room
from ..schemas import RoomCreate, RoomResponse, JoinRoomRequest
from engine.game import Game

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("", response_model=RoomResponse)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    if db.query(Room).filter(Room.id == room.id).first():
        raise HTTPException(status_code=409, detail="Room ID already exists")
    db_room = Room(
        id=room.id,
        fen=Game.INITIAL_FEN,
        player_white=None,
        player_black=None,
        status="waiting",
        time_white=float(room.time_control),
        time_black=float(room.time_control),
        last_move_at=None,
    )
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/{room_id}/join", response_model=RoomResponse)
def join_room(room_id: str, request: JoinRoomRequest, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    if request.color == "white":
        if room.player_white is not None:
            raise HTTPException(status_code=400, detail="White player already joined")
        room.player_white = request.player_id
    elif request.color == "black":
        if room.player_black is not None:
            raise HTTPException(status_code=400, detail="Black player already joined")
        room.player_black = request.player_id

    if room.player_white and room.player_black:
        room.status = "playing"
        room.last_move_at = time.time()

    db.commit()
    db.refresh(room)
    return room
