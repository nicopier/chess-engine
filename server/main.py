from fastapi import FastAPI
from engine.game import Game
from pydantic import BaseModel
from typing import Literal

from fastapi.middleware.cors import CORSMiddleware

from .routers import websocket

from .database import Base, engine
from .models import Room
from .routers import rooms

Base.metadata.create_all(bind=engine)

class MoveRequest(BaseModel):
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]
    promotion: str | None = None


class EndGameRequest(BaseModel):
    result: Literal["white_wins", "black_wins", "draw"]

app = FastAPI()

app.include_router(rooms.router)
app.include_router(websocket.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
game = Game()

@app.get("/")
def root():
    return {"status": "chess engine running"}

@app.get("/board")
def get_board():
    board_state = []
    for row in game.board.board:
        for piece in row:
            if piece is not None:
                board_state.append({
                    "type": piece.piece_type.value,
                    "color": piece.color.value,
                    "position": piece.position
                })
    return board_state

@app.post("/move")
def make_move(move: MoveRequest):
    result = game.make_move(move.from_pos, move.to_pos, move.promotion)
    if result:
        return {"success": True,
                "turn": game.current_turn.value,
                "white_in_check": game.white_in_check,
                "black_in_check": game.black_in_check
                }
    return {"success": False}

@app.get("/history")
def get_history():
    return game.move_history

@app.post("/end_game")
def end_game(request: EndGameRequest):
    game.end_game(request.result)
    return {"success": True, "result": game.result}

@app.post("/reset")
def reset_game():
    global game
    game = Game()
    return {"success": True}

@app.post("/goto/last")
def goto_last():
    game.current_position = len(game.move_history)
    return {"success": True}

@app.post("/goto/{index}")
def goto_position(index: int):
    if index < 0 or index > len(game.move_history):
        return {"success": False}
    game.current_position = index
    return {"success": True, "fen": game.move_history[index - 1]["fen"] if index > 0 else None}

