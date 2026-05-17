from fastapi import FastAPI
from domain.game import Game
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware




class MoveRequest(BaseModel):
    from_pos: tuple[int, int]
    to_pos: tuple[int, int]
    
app = FastAPI()

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
    piece = game.board.get_piece_at(move.from_pos)
    print(piece)
    print(piece.valid_moves(game.board))
    result = game.make_move(move.from_pos, move.to_pos)
    if result:
        return {"success": True,
                "turn": game.current_turn.value,
                "white_in_check": game.white_in_check,
                "black_in_check": game.black_in_check
                }
    return {"success": False}