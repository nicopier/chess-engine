from .pieces import Pawn, Color, Rook, Knight, Bishop, Queen, King

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
            # Blancas - fila 0
        self.board[0][0] = Rook(Color.WHITE, (0, 0))
        self.board[0][1] = Knight(Color.WHITE, (0, 1))
        self.board[0][2] = Bishop(Color.WHITE, (0, 2))
        self.board[0][3] = Queen(Color.WHITE, (0, 3))
        self.board[0][4] = King(Color.WHITE, (0, 4))
        self.board[0][5] = Bishop(Color.WHITE, (0, 5))
        self.board[0][6] = Knight(Color.WHITE, (0, 6))
        self.board[0][7] = Rook(Color.WHITE, (0, 7))
        
        # Negras - fila 7
        self.board[7][0] = Rook(Color.BLACK, (7, 0))
        self.board[7][1] = Knight(Color.BLACK, (7, 1))
        self.board[7][2] = Bishop(Color.BLACK, (7, 2))
        self.board[7][3] = Queen(Color.BLACK, (7, 3))
        self.board[7][4] = King(Color.BLACK, (7, 4))
        self.board[7][5] = Bishop(Color.BLACK, (7, 5))
        self.board[7][6] = Knight(Color.BLACK, (7, 6))
        self.board[7][7] = Rook(Color.BLACK, (7, 7))    
                
            
    def get_piece_at(self, position:tuple[int, int]):
        row, col = position
        return self.board[row][col] 
    
    def find_king(self, color: Color):
        for row in range(8):
            for col in range(8):
                piece_position = (row, col)
                piece = self.get_piece_at(piece_position)
                if piece and isinstance(piece, King) and piece.color == color:
                    return piece_position
    
    def is_in_check(self, color: Color):
        king_position = self.find_king(color)
        opponent_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        for row in range(8):
            for col in range(8):
                piece_position = (row, col)
                piece = self.get_piece_at(piece_position)
                if piece and piece.color == opponent_color:
                    if king_position in piece.valid_moves(self):
                        return True
        return False