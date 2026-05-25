from sqlalchemy import Column, String, Float, Integer, LargeBinary
from .database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(String, primary_key=True)
    creator = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    time_control = Column(Integer, nullable=False)
    player_white = Column(String, nullable=True)
    player_black = Column(String, nullable=True)
    status = Column(String)
    white_token = Column(String, nullable=True)
    black_token = Column(String, nullable=True)
    time_white = Column(Float)
    time_black = Column(Float)
    last_move_at = Column(Float)
    moves = Column(LargeBinary, nullable=True)