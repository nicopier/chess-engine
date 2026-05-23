from .pieces import Pawn, Color, Rook, Knight, Bishop, Queen, King, PieceType

class Board():
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        # Posición de cada rey tracked directamente — find_king pasa de O(64) a O(1)
        self._king_pos = {}
        self.setup_pieces()

    def setup_pieces(self):
        for col in range(8):
            self.board[1][col] = Pawn(Color.WHITE, (1, col))
            self.board[6][col] = Pawn(Color.BLACK, (6, col))
        self.board[0][0] = Rook(Color.WHITE, (0, 0))
        self.board[0][1] = Knight(Color.WHITE, (0, 1))
        self.board[0][2] = Bishop(Color.WHITE, (0, 2))
        self.board[0][3] = Queen(Color.WHITE, (0, 3))
        self.board[0][4] = King(Color.WHITE, (0, 4))
        self.board[0][5] = Bishop(Color.WHITE, (0, 5))
        self.board[0][6] = Knight(Color.WHITE, (0, 6))
        self.board[0][7] = Rook(Color.WHITE, (0, 7))

        self.board[7][0] = Rook(Color.BLACK, (7, 0))
        self.board[7][1] = Knight(Color.BLACK, (7, 1))
        self.board[7][2] = Bishop(Color.BLACK, (7, 2))
        self.board[7][3] = Queen(Color.BLACK, (7, 3))
        self.board[7][4] = King(Color.BLACK, (7, 4))
        self.board[7][5] = Bishop(Color.BLACK, (7, 5))
        self.board[7][6] = Knight(Color.BLACK, (7, 6))
        self.board[7][7] = Rook(Color.BLACK, (7, 7))

        self._king_pos[Color.WHITE] = (0, 4)
        self._king_pos[Color.BLACK] = (7, 4)

    def get_piece_at(self, position: tuple[int, int]):
        row, col = position
        return self.board[row][col]

    def update_king_pos(self, color: Color, pos: tuple[int, int]):
        self._king_pos[color] = pos

    def find_king(self, color: Color):
        return self._king_pos[color]
    
    def is_in_check(self, color: Color):
        king_position = self.find_king(color)
        return self.is_square_attacked(king_position, color)
    
    def to_fen(self, current_turn: Color, en_passant_target=None, halfmove_clock=0, fullmove_number=1):
        final_fen = ""
        for row in reversed(self.board):
            row_fen = ""
            none_escaques = 0
            for piece in row:
                if piece is None:
                    none_escaques += 1
                else:
                    if none_escaques > 0:
                        row_fen += str(none_escaques)
                        none_escaques = 0
                    row_fen += piece.notation.value if piece.color == Color.WHITE else piece.notation.value.lower()
            if none_escaques > 0:
                row_fen += str(none_escaques)
            final_fen += row_fen + "/"
        
        turn = "w" if current_turn == Color.WHITE else "b"
        
        castling = ""
        white_king = self.get_piece_at((0, 4))
        white_rook_h = self.get_piece_at((0, 7))
        white_rook_a = self.get_piece_at((0, 0))
        black_king = self.get_piece_at((7, 4))
        black_rook_h = self.get_piece_at((7, 7))
        black_rook_a = self.get_piece_at((7, 0))
        if white_king and not white_king.has_moved:
            if white_rook_h and not white_rook_h.has_moved: castling += "K"
            if white_rook_a and not white_rook_a.has_moved: castling += "Q"
        if black_king and not black_king.has_moved:
            if black_rook_h and not black_rook_h.has_moved: castling += "k"
            if black_rook_a and not black_rook_a.has_moved: castling += "q"
        if not castling:
            castling = "-"
        
        cols = ['a','b','c','d','e','f','g','h']
        ep = "-"
        if en_passant_target:
            ep = cols[en_passant_target[1]] + str(en_passant_target[0] + 1)
        
        return f"{final_fen.rstrip('/')} {turn} {castling} {ep} {halfmove_clock} {fullmove_number}"
    
    def to_san(self, piece, from_pos, to_pos, captured_piece):
        cols = ['a','b','c','d','e','f','g','h']
        col_letter = cols[to_pos[1]]
        row_number = str(to_pos[0] + 1)
        destination = col_letter + row_number
        
        # peón
        if piece.piece_type == PieceType.PAWN:
            if captured_piece:
                return cols[from_pos[1]] + 'x' + destination
            return destination
        
        # disambiguación - buscar si hay otra pieza del mismo tipo que puede ir al mismo destino
        piece_letter = piece.notation.value
        same_type = []
        for row in range(8):
            for col in range(8):
                other = self.get_piece_at((row, col))
                if other and other != piece and type(other) == type(piece) and other.color == piece.color:
                    if to_pos in other.valid_moves(self):
                        same_type.append((row, col))
        
        # enroque
        if piece.piece_type == PieceType.KING:
            if to_pos[1] - from_pos[1] == 2:
                return "O-O"
            elif to_pos[1] - from_pos[1] == -2:
                return "O-O-O"
        
        disambiguation = ""
        if same_type:
            disambiguation = cols[from_pos[1]]
        
        capture = "x" if captured_piece else ""
        return piece_letter + disambiguation + capture + destination
    
    def is_square_attacked(self, position: tuple[int, int], color: Color) -> bool:
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        row, col = position

        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            r, c = row+dr, col+dc
            if 0 <= r <= 7 and 0 <= c <= 7:
                p = self.board[r][c]
                if p and p.color == opponent and p.piece_type == PieceType.KNIGHT:
                    return True

        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            for i in range(1, 8):
                r, c = row+dr*i, col+dc*i
                if not (0 <= r <= 7 and 0 <= c <= 7):
                    break
                p = self.board[r][c]
                if p:
                    if p.color == opponent and p.piece_type in (PieceType.ROOK, PieceType.QUEEN):
                        return True
                    break

        for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            for i in range(1, 8):
                r, c = row+dr*i, col+dc*i
                if not (0 <= r <= 7 and 0 <= c <= 7):
                    break
                p = self.board[r][c]
                if p:
                    if p.color == opponent and p.piece_type in (PieceType.BISHOP, PieceType.QUEEN):
                        return True
                    break

        pawn_dir = 1 if color == Color.WHITE else -1
        for dc in [-1, 1]:
            r, c = row+pawn_dir, col+dc
            if 0 <= r <= 7 and 0 <= c <= 7:
                p = self.board[r][c]
                if p and p.color == opponent and p.piece_type == PieceType.PAWN:
                    return True

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row+dr, col+dc
                if 0 <= r <= 7 and 0 <= c <= 7:
                    p = self.board[r][c]
                    if p and p.color == opponent and p.piece_type == PieceType.KING:
                        return True

        return False
            
    def can_castle_kingside(self, color: Color) -> bool:
        row = 0 if color == Color.WHITE else 7
        king = self.get_piece_at((row, 4))
        rook = self.get_piece_at((row, 7))
        return (king and not king.has_moved and
                rook and not rook.has_moved and
                self.get_piece_at((row, 5)) is None and
                self.get_piece_at((row, 6)) is None and
                not self.is_square_attacked((row, 4), color) and  # rey no en jaque
                not self.is_square_attacked((row, 5), color) and  # no pasa por casilla atacada
                not self.is_square_attacked((row, 6), color))     # destino no atacado

    def can_castle_queenside(self, color: Color) -> bool:
        row = 0 if color == Color.WHITE else 7
        king = self.get_piece_at((row, 4))
        rook = self.get_piece_at((row, 0))
        
        
        return (king and not king.has_moved and
                rook and not rook.has_moved and
                self.get_piece_at((row, 1)) is None and
                self.get_piece_at((row, 2)) is None and
                self.get_piece_at((row, 3)) is None and
                not self.is_square_attacked((row, 4), color) and # rey no en jaque
                not self.is_square_attacked((row, 2), color) and # no pasa por casilla atacada
                not self.is_square_attacked((row, 3), color))    # destino no atacado