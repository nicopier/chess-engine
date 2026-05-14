from domain.board import Board

board = Board()
pawn = board.get_piece_at((1, 0))
print(pawn)
print(pawn.valid_moves(board))