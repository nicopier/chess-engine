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

# Offsets y direcciones pre-computados como constantes de módulo (se crean una sola vez)
_KNIGHT_OFFSETS = ((2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2))
_KING_OFFSETS   = ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1))
_ROOK_DIRS      = ((0,1),(0,-1),(1,0),(-1,0))
_BISHOP_DIRS    = ((1,1),(1,-1),(-1,1),(-1,-1))
_QUEEN_DIRS     = _ROOK_DIRS + _BISHOP_DIRS


def _slide(piece, board, dirs):
    """Genera movidas para piezas deslizantes (rook, bishop, queen) en las direcciones dadas."""
    moves = []
    row, col = piece.position
    b = board.board   # referencia local evita attr lookup en cada iteración del bucle
    color = piece.color
    for dr, dc in dirs:
        r, c = row + dr, col + dc
        while 0 <= r <= 7 and 0 <= c <= 7:
            p = b[r][c]   # acceso directo al array, sin pasar por get_piece_at()
            if p is None:
                moves.append((r, c))
            elif p.color != color:
                moves.append((r, c))
                break
            else:
                break
            r += dr
            c += dc
    return moves


class Piece:
    # __slots__ elimina el __dict__ interno: atributos en posiciones fijas de memoria,
    # acceso ~20-30% más rápido y menor uso de memoria por instancia.
    __slots__ = ('color', 'position', 'piece_type', 'notation', 'has_moved')

    def __init__(self, color: Color, piece_type: PieceType, position: tuple[int, int], notation: PieceNotation):
        self.color = color
        self.position = position
        self.piece_type = piece_type
        self.notation = notation
        self.has_moved = False

    def __repr__(self):
        return f"{self.color.value} {self.piece_type.value} at {self.position}"

    def move(self, new_position: tuple[int, int]):
        self.position = new_position
        self.has_moved = True

    def is_valid_position(self, position: tuple[int, int]) -> bool:
        row, col = position
        return 0 <= row <= 7 and 0 <= col <= 7

    def add_if_empty(self, moves: list, board, position: tuple[int, int]):
        row, col = position
        if not (0 <= row <= 7 and 0 <= col <= 7):
            return
        if board.board[row][col] is None:
            moves.append(position)

    def add_if_enemy(self, moves: list, board, position: tuple[int, int]):
        row, col = position
        if not (0 <= row <= 7 and 0 <= col <= 7):
            return
        p = board.board[row][col]
        if p is not None and p.color != self.color:
            moves.append(position)


class Pawn(Piece):
    __slots__ = ()

    def __init__(self, color: Color, position: tuple[int, int]):
        super().__init__(color, PieceType.PAWN, position, PieceNotation.PAWN)

    def valid_moves(self, board, en_passant_target=None, **kwargs):
        moves = []
        row, col = self.position
        b = board.board
        if self.color == Color.WHITE:
            if row + 1 <= 7 and b[row+1][col] is None:
                moves.append((row+1, col))
                if row == 1 and b[row+2][col] is None:
                    moves.append((row+2, col))
            self.add_if_enemy(moves, board, (row+1, col-1))
            self.add_if_enemy(moves, board, (row+1, col+1))
            if en_passant_target:
                if en_passant_target == (row+1, col-1) or en_passant_target == (row+1, col+1):
                    moves.append(en_passant_target)
        else:
            if row - 1 >= 0 and b[row-1][col] is None:
                moves.append((row-1, col))
                if row == 6 and b[row-2][col] is None:
                    moves.append((row-2, col))
            self.add_if_enemy(moves, board, (row-1, col-1))
            self.add_if_enemy(moves, board, (row-1, col+1))
            if en_passant_target:
                if en_passant_target == (row-1, col-1) or en_passant_target == (row-1, col+1):
                    moves.append(en_passant_target)
        return moves


class Rook(Piece):
    __slots__ = ()

    def __init__(self, color: Color, position: tuple[int, int]):
        super().__init__(color, PieceType.ROOK, position, PieceNotation.ROOK)

    def valid_moves(self, board, **kwargs):
        return _slide(self, board, _ROOK_DIRS)


class Knight(Piece):
    __slots__ = ()

    def __init__(self, color: Color, position: tuple[int, int]):
        super().__init__(color, PieceType.KNIGHT, position, PieceNotation.KNIGHT)

    def valid_moves(self, board, **kwargs):
        moves = []
        row, col = self.position
        b = board.board
        color = self.color
        for dr, dc in _KNIGHT_OFFSETS:
            r, c = row + dr, col + dc
            if 0 <= r <= 7 and 0 <= c <= 7:
                p = b[r][c]
                if p is None or p.color != color:
                    moves.append((r, c))
        return moves


class Bishop(Piece):
    __slots__ = ()

    def __init__(self, color: Color, position: tuple[int, int]):
        super().__init__(color, PieceType.BISHOP, position, PieceNotation.BISHOP)

    def valid_moves(self, board, **kwargs):
        return _slide(self, board, _BISHOP_DIRS)


class Queen(Piece):
    __slots__ = ()

    def __init__(self, color: Color, position: tuple[int, int]):
        super().__init__(color, PieceType.QUEEN, position, PieceNotation.QUEEN)

    def valid_moves(self, board, **kwargs):
        return _slide(self, board, _QUEEN_DIRS)


class King(Piece):
    __slots__ = ()

    def __init__(self, color: Color, position: tuple[int, int]):
        super().__init__(color, PieceType.KING, position, PieceNotation.KING)

    def valid_moves(self, board, check_castling=True, **kwargs):
        moves = []
        row, col = self.position
        b = board.board
        color = self.color
        for dr, dc in _KING_OFFSETS:
            r, c = row + dr, col + dc
            if 0 <= r <= 7 and 0 <= c <= 7:
                p = b[r][c]
                if p is None or p.color != color:
                    moves.append((r, c))
        if check_castling:
            if board.can_castle_kingside(color):
                moves.append((row, 6))
            if board.can_castle_queenside(color):
                moves.append((row, 2))
        return moves
