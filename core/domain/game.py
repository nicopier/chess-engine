from .board import Board
from .pieces import Pawn, Color, Rook, Knight, Bishop, Queen, King

class Game():
    def __init__(self):
        self.board = Board()
        self.current_turn = Color.WHITE
        self.white_in_check = False
        self.black_in_check = False
        
    def make_move(self, from_pos:tuple[int, int], to_pos:tuple[int, int]):
        piece = self.board.get_piece_at(from_pos)
        if piece is None:
            return False
        if piece.color != self.current_turn:
            return False
        if to_pos not in piece.valid_moves(self.board):
            return False
        
        # guardar estado anterior
        captured_piece = self.board.get_piece_at(to_pos)
        
        self.board.board[to_pos[0]][to_pos[1]] = piece
        self.board.board[from_pos[0]][from_pos[1]] = None
        piece.move(to_pos)
        
        #checkeando jaques
        if self.board.is_in_check(self.current_turn):
            #revertir el movimiento
            self.board.board[from_pos[0]][from_pos[1]] = piece
            self.board.board[to_pos[0]][to_pos[1]] = captured_piece
            piece.move(from_pos)
            return False
        
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE
        
        #checkea globalemnte si ahy jaque para ambos jugadores
        self.white_in_check = self.board.is_in_check(Color.WHITE)
        self.black_in_check = self.board.is_in_check(Color.BLACK)
        return True
    