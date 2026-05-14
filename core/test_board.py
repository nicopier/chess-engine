from domain.board import Board

board = Board()

# Testeamos algunas piezas
print(board.get_piece_at((0, 0)))  # Rook blanca
print(board.get_piece_at((0, 4)))  # King blanco
print(board.get_piece_at((7, 3)))  # Queen negra
print(board.get_piece_at((1, 3)))  # Pawn blanco

# Testeamos movimientos
knight = board.get_piece_at((0, 1))
print(knight.valid_moves(board))   # Movimientos del caballo blanco