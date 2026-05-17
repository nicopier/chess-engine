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
                
    def make_move(self, from_pos:tuple[int, int], to_pos:tuple[int, int]):
        if self.current_position != len(self.move_history):
            return False
        if self.game_over:
            return False
        
        piece = self.board.get_piece_at(from_pos)
        if piece is None:
            return False
        if piece.color != self.current_turn:
            return False
        if to_pos not in piece.valid_moves(self.board, self.en_passant_target):
            return False
        
        # guardar estado anterior
        captured_piece = self.board.get_piece_at(to_pos)
        
        self.board.board[to_pos[0]][to_pos[1]] = piece
        self.board.board[from_pos[0]][from_pos[1]] = None
        piece.move(to_pos)
        
        # guardar en passant anterior para ejecutar captura
        old_en_passant_target = self.en_passant_target

        # en passant - actualizar para el próximo turno
        if piece.piece_type == PieceType.PAWN and abs(to_pos[0] - from_pos[0]) == 2:
            self.en_passant_target = ((from_pos[0] + to_pos[0]) // 2, from_pos[1])
        else:
            self.en_passant_target = None

        # ejecutar captura al paso
        if piece.piece_type == PieceType.PAWN and old_en_passant_target == to_pos:
            captured_en_passant_row = from_pos[0]
            self.board.board[captured_en_passant_row][to_pos[1]] = None
        
        # halfmove clock
        if piece.piece_type == PieceType.PAWN or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # fullmove number
        if self.current_turn == Color.BLACK:
            self.fullmove_number += 1
        # enroque
        if piece.piece_type == PieceType.KING:
            if to_pos[1] - from_pos[1] == 2:  # enroque corto
                rook = self.board.get_piece_at((from_pos[0], 7))
                self.board.board[from_pos[0]][5] = rook
                self.board.board[from_pos[0]][7] = None
                rook.move((from_pos[0], 5))
            elif to_pos[1] - from_pos[1] == -2:  # enroque largo
                rook = self.board.get_piece_at((from_pos[0], 0))
                self.board.board[from_pos[0]][3] = rook
                self.board.board[from_pos[0]][0] = None
                rook.move((from_pos[0], 3))
        
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
        
        #guardamos el movimiento en el historial
        
        self.move_history.append({
                                    "from_pos": from_pos,
                                    "to_pos": to_pos,
                                    "piece": piece.piece_type.value,
                                    "color": piece.color.value,
                                    "captured": captured_piece.piece_type.value if captured_piece else None,
                                    "fen": self.board.to_fen(self.current_turn, self.en_passant_target, self.halfmove_clock, self.fullmove_number),
                                    "san": self.board.to_san(piece, from_pos, to_pos, captured_piece)
                                })
        #sumamos uno al contador de posicion actual en el historial
        self.current_position += 1 
        return True
    
    def end_game(self, result: str):
        self.game_over = True
        self.result = result  # "white_wins", "black_wins", "draw"