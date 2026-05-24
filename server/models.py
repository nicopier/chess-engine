from sqlalchemy import Column, String, Float, Text
from .database import Base


class Room(Base):
    __tablename__= "rooms"

    id = Column(String, primary_key=True)
    fen = Column(String)
    player_white = Column(String)
    player_black = Column(String)
    status = Column(String)
    time_white = Column(Float)
    time_black = Column(Float)
    last_move_at = Column(Float)
    history = Column(Text, nullable=True)