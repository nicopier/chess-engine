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
    
class PieceNotation(Enum):
    PAWN = "P"
    KNIGHT = "N"
    BISHOP = "B"
    ROOK = "R"
    QUEEN = "Q"
    KING = "K"    

class Piece:
    def __init__(self, color:Color, piece_type:PieceType, position:tuple[int, int], notation:PieceNotation):
        self.color = color
        self.position = position
        self.piece_type = piece_type
        self.notation = notation
        self.has_moved = False
        
    def __repr__(self): #funcion para printear la pieza de manera legible
        return f"{self.color.value} {self.piece_type.value} at {self.position}" 
    
    def move(self, new_position:tuple[int,int]):
        self.position = new_position
        self.has_moved = True
    
    def is_valid_position(self, position: tuple[int, int]) -> bool:
        row, col = position
        return 0 <= row <= 7 and 0 <= col <= 7
    
    def add_if_empty(self, moves: list, board, position: tuple[int, int]):
        if not self.is_valid_position(position):
            return
        piece = board.get_piece_at(position)
        if piece is None:
            moves.append(position)
    
    def add_if_enemy(self, moves: list, board, position: tuple[int, int]):
        if not self.is_valid_position(position):
            return
        piece = board.get_piece_at(position)
        if piece is not None and piece.color != self.color:
            moves.append(position)
    
    
        
class Pawn(Piece):
    def __init__(self, color:Color, position:tuple[int, int]):
        super().__init__(color, PieceType.PAWN, position, PieceNotation.PAWN)
        
    def valid_moves(self, board, en_passant_target=None, **kwargs):
        moves = []
        row, col = self.position
        if self.color == Color.WHITE:
            self.add_if_empty(moves, board, (row+1, col))
            if row == 1 and board.get_piece_at((row+1, col)) is None: 
                self.add_if_empty(moves, board, (row+2, col))
            self.add_if_enemy(moves, board, (row+1, col-1))
            self.add_if_enemy(moves, board, (row+1, col+1))
            # en passant
            if en_passant_target and en_passant_target == (row+1, col-1):
                moves.append((row+1, col-1))
            if en_passant_target and en_passant_target == (row+1, col+1):
                moves.append((row+1, col+1))
                
        elif self.color == Color.BLACK:
            self.add_if_empty(moves, board, (row-1, col))
            if row == 6 and board.get_piece_at((row-1, col)) is None:
                self.add_if_empty(moves, board, (row-2, col))
            self.add_if_enemy(moves, board, (row-1, col-1))
            self.add_if_enemy(moves, board, (row-1, col+1))
            # en passant
            if en_passant_target and en_passant_target == (row-1, col-1):
                moves.append((row-1, col-1))
            if en_passant_target and en_passant_target == (row-1, col+1):
                moves.append((row-1, col+1))
        
        return moves
            
     

class Rook(Piece):
    def __init__(self, color:Color, position:tuple[int, int]):
        super().__init__(color, PieceType.ROOK, position, PieceNotation.ROOK)
        
    def valid_moves(self, board:'Board', **kwargs):
        moves = []
        row, col = self.position
        
        # derecha
        for i in range(1, 8):
            pos = (row, col + i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break
            
        # izquierda  
        for i in range(1, 8):
            pos = (row, col - i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break

        # abajo
        for i in range(1, 8):
            pos = (row + i, col)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break

        # arriba
        for i in range(1, 8):
            pos = (row - i, col)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break
            
        return moves
            

class Knight(Piece):
    def __init__(self, color:Color, position:tuple[int, int]):
        super().__init__(color, PieceType.KNIGHT, position, PieceNotation.KNIGHT)

    def valid_moves(self, board:'Board', **kwargs):
        moves = []
        row, col = self.position
        
        possible = [
            (row+2, col+1), (row+2, col-1),
            (row-2, col+1), (row-2, col-1),
            (row+1, col+2), (row+1, col-2),
            (row-1, col+2), (row-1, col-2)
        ]
        
        for pos in possible:
            self.add_if_empty(moves, board, pos)
            self.add_if_enemy(moves, board, pos)
        
        return moves    


class Bishop(Piece):
    def __init__(self, color:Color, position:tuple[int, int]):
        super().__init__(color, PieceType.BISHOP, position, PieceNotation.BISHOP)

    def valid_moves(self, board:'Board', **kwargs):
        moves = []
        row, col = self.position
        
        # derecha
        for i in range(1, 8):
            pos = (row + i, col + i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break
            
        # izquierda  
        for i in range(1, 8):
            pos = (row +i, col - i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break

        # abajo
        for i in range(1, 8):
            pos = (row - i, col + i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break

        # arriba
        for i in range(1, 8):
            pos = (row - i, col- i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break
        
        return moves

class Queen(Piece):
    def __init__(self, color:Color, position:tuple[int, int]):
        super().__init__(color, PieceType.QUEEN, position, PieceNotation.QUEEN)

    def valid_moves(self, board:'Board', **kwargs):
        moves = []
        row, col = self.position
        
        # derecha
        for i in range(1, 8):
            pos = (row + i, col + i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break
            
        # izquierda  
        for i in range(1, 8):
            pos = (row +i, col - i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break

        # abajo
        for i in range(1, 8):
            pos = (row - i, col + i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break

        # arriba
        for i in range(1, 8):
            pos = (row - i, col- i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break
        
        # derecha
        for i in range(1, 8):
            pos = (row, col + i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break
            
        # izquierda  
        for i in range(1, 8):
            pos = (row, col - i)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break

        # abajo
        for i in range(1, 8):
            pos = (row + i, col)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break

        # arriba
        for i in range(1, 8):
            pos = (row - i, col)
            if not self.is_valid_position(pos):
                break
            piece = board.get_piece_at(pos)
            if piece is None:
                moves.append(pos)
            elif piece.color != self.color:
                moves.append(pos)
                break
            else:
                break
            
        return moves

class King(Piece):
    def __init__(self, color:Color, position:tuple[int, int]):
        super().__init__(color, PieceType.KING, position, PieceNotation.KING)

    def valid_moves(self, board:'Board',  check_castling=True, **kwargs):
        moves = []
        row, col = self.position
        
        possible = [
            (row+1, col), (row-1, col),
            (row, col+1), (row, col-1),
            (row+1, col+1), (row+1, col-1),
            (row-1, col+1), (row-1, col-1)
        ]
        
        for pos in possible:
            self.add_if_empty(moves, board, pos)
            self.add_if_enemy(moves, board, pos)
            
        if check_castling:  # solo chequea enroque si se lo pedimos
            if board.can_castle_kingside(self.color):
                moves.append((row, 6))
            if board.can_castle_queenside(self.color):
                moves.append((row, 2))
        
        
        
        return moves    
