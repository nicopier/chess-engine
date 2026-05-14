from .pieces import Pawn, Color

class Board():
    def __init__(self):
        self.board = self.create_board()
        self.setup_pieces()

    def create_board(self):
        board = [[None for _ in range(8)] for _ in range(8)]
        return board
    
    def setup_pieces(self):
        for col in range(8):
            self.board[1][col] = Pawn(Color.WHITE, (1, col))
            self.board[6][col] = Pawn(Color.BLACK, (6, col))
            
    def get_pieces_at(self, position:tuple[int, int]):
        row, col = position
        return self.board[row][col] 