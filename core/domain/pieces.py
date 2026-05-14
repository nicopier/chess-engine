from enum import Enum

class Color(Enum):
    WHITE = "white"
    BLACK = "black"
    
class PieceType(Enum):
    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"
    

class Piece:
    def __init__(self, color:Color, piece_type:PieceType, position:tuple[int, int]):
        self.color = color
        self.position = position
        self.piece_type = piece_type 
        
    def __repr__(self): #funcion para printear la pieza de manera legible
        return f"{self.color.value} {self.piece_type.value} at {self.position}" 
    
    def move(self, new_position:tuple[int,int]):
        self.position = new_position
        
class Pawn(Piece):
    def __init__(self, color:Color, position:tuple[int, int]):
        super().__init__(color, PieceType.PAWN, position)
        
    def valid_moves(self, board):
        moves = []
        row, col = self.position
        if self.color == Color.WHITE:
            moves.append((row+1, col))
            if row == 2:
                moves.append((row+2, col))
                
        elif self.color == Color.BLACK:
            moves.append((row-1, col))
            if row == 7:
                moves.append((row-2, col))

                
            
        
        
        pass