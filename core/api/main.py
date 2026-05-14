from fastapi import FastAPI
from domain.game import Game

app = FastAPI()
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