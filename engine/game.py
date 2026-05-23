from .board import Board
from .pieces import Pawn, Color, Rook, Knight, Bishop, Queen, King, PieceType, PieceNotation

class Game():
    def __init__(self, move_history: list = None):
        self.board = Board()
        self.current_turn = Color.WHITE
        
        self.white_in_check = False
        self.black_in_check = False
        
        self.result = None
        self.game_over = False
        
        self.move_history = move_history if move_history is not None else []
        self.current_position = 0
        
        self.en_passant_target = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
                
    def make_move(self, from_pos:tuple[int, int], to_pos:tuple[int, int], promotion:str = None):
        if self.current_position != len(self.move_history):
            return False
        if self.game_over:
            return False
        
        piece = self.board.get_piece_at(from_pos)
        if piece is None:
            return False
        if piece.color != self.current_turn:
            return False
        if to_pos not in piece.valid_moves(self.board, en_passant_target=self.en_passant_target):
            return False
        
        # guardar estado anterior
        captured_piece = self.board.get_piece_at(to_pos)
        piece_has_moved = piece.has_moved
        rook_a = self.board.get_piece_at((from_pos[0], 0))
        rook_h = self.board.get_piece_at((from_pos[0], 7))
        rook_a_moved = rook_a.has_moved if rook_a else None
        rook_h_moved = rook_h.has_moved if rook_h else None
        
        self.board.board[to_pos[0]][to_pos[1]] = piece
        self.board.board[from_pos[0]][from_pos[1]] = None
        piece.move(to_pos)
        if piece.piece_type == PieceType.KING:
            self.board.update_king_pos(piece.color, to_pos)
        
        # guardar en passant anterior para ejecutar captura
        old_en_passant_target = self.en_passant_target

        # en passant - actualizar para el próximo turno
        if piece.piece_type == PieceType.PAWN and abs(to_pos[0] - from_pos[0]) == 2:
            self.en_passant_target = ((from_pos[0] + to_pos[0]) // 2, from_pos[1])
        else:
            self.en_passant_target = None

        # ejecutar captura al paso
        captured_en_passant_pawn = None
        captured_en_passant_square = None
        if piece.piece_type == PieceType.PAWN and old_en_passant_target == to_pos:
            captured_en_passant_square = (from_pos[0], to_pos[1])
            captured_en_passant_pawn = self.board.get_piece_at(captured_en_passant_square)
            self.board.board[captured_en_passant_square[0]][captured_en_passant_square[1]] = None
        
        # halfmove clock
        if piece.piece_type == PieceType.PAWN or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # fullmove number
        if self.current_turn == Color.BLACK:
            self.fullmove_number += 1

        # enroque
        castled_rook = None
        castled_rook_from = None
        castled_rook_to = None
        if piece.piece_type == PieceType.KING:
            if to_pos[1] - from_pos[1] == 2:
                castled_rook = self.board.get_piece_at((from_pos[0], 7))
                castled_rook_from = (from_pos[0], 7)
                castled_rook_to = (from_pos[0], 5)
                self.board.board[from_pos[0]][5] = castled_rook
                self.board.board[from_pos[0]][7] = None
                castled_rook.move((from_pos[0], 5))
            elif to_pos[1] - from_pos[1] == -2:
                castled_rook = self.board.get_piece_at((from_pos[0], 0))
                castled_rook_from = (from_pos[0], 0)
                castled_rook_to = (from_pos[0], 3)
                self.board.board[from_pos[0]][3] = castled_rook
                self.board.board[from_pos[0]][0] = None
                castled_rook.move((from_pos[0], 3))

        # si el rey queda en jaque, revertir todo
        if self.board.is_in_check(self.current_turn):
            self.board.board[from_pos[0]][from_pos[1]] = piece
            self.board.board[to_pos[0]][to_pos[1]] = captured_piece
            piece.move(from_pos)
            piece.has_moved = piece_has_moved
            if piece.piece_type == PieceType.KING:
                self.board.update_king_pos(piece.color, from_pos)
            if captured_en_passant_pawn:
                self.board.board[captured_en_passant_square[0]][captured_en_passant_square[1]] = captured_en_passant_pawn
            if castled_rook:
                self.board.board[castled_rook_from[0]][castled_rook_from[1]] = castled_rook
                self.board.board[castled_rook_to[0]][castled_rook_to[1]] = None
                castled_rook.move(castled_rook_from)
                castled_rook.has_moved = False
            else:
                rook_a = self.board.get_piece_at((from_pos[0], 0))
                rook_h = self.board.get_piece_at((from_pos[0], 7))
                if rook_a and rook_a_moved is not None: rook_a.has_moved = rook_a_moved
                if rook_h and rook_h_moved is not None: rook_h.has_moved = rook_h_moved
            return False
        
        # promoción de peón
        _promotion_map = {'queen': Queen, 'rook': Rook, 'bishop': Bishop, 'knight': Knight}
        promo_suffix = ""
        if piece.piece_type == PieceType.PAWN:
            last_rank = 7 if piece.color == Color.WHITE else 0
            if to_pos[0] == last_rank:
                promo_class = _promotion_map.get(promotion, Queen)
                promoted = promo_class(piece.color, to_pos)
                promoted.has_moved = True
                self.board.board[to_pos[0]][to_pos[1]] = promoted
                promo_suffix = "=" + promoted.notation.value

        if self.current_turn == Color.WHITE:
            self.white_in_check = False
            self.current_turn = Color.BLACK
            self.black_in_check = self.board.is_in_check(Color.BLACK)
        else:
            self.black_in_check = False
            self.current_turn = Color.WHITE
            self.white_in_check = self.board.is_in_check(Color.WHITE)

        self.move_history.append({
            "from_pos": from_pos,
            "to_pos": to_pos,
            "piece": piece.piece_type.value,
            "color": piece.color.value,
            "captured": captured_piece.piece_type.value if captured_piece else None,
            "fen": self.board.to_fen(self.current_turn, self.en_passant_target, self.halfmove_clock, self.fullmove_number),
            "san": self.board.to_san(piece, from_pos, to_pos, captured_piece) + promo_suffix
        })
        self.current_position += 1 
        return True
    
    def end_game(self, result: str):
        self.game_over = True
        self.result = result