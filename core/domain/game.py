from .board import Board
from .pieces import Pawn, Color, Rook, Knight, Bishop, Queen, King

class Game():
    def __init__(self):
        self.board = Board()
        self.current_turn = Color.WHITE
        
    def make_move(self, from_pos:tuple[int, int], to_pos:tuple[int, int]):
        piece = self.board.get_piece_at(from_pos)
        if piece is None:
            return False
        if piece.color != self.current_turn:
            return False
        if to_pos not in piece.valid_moves(self.board):
            return False
        
        self.board.board[to_pos[0]][to_pos[1]] = piece
        self.board.board[from_pos[0]][from_pos[1]] = None
        piece.move(to_pos)
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        return True