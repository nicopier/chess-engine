from domain.game import Game

game = Game()

# Mover peón blanco de (1,0) a (2,0)
print(game.make_move((1, 0), (2, 0)))  # True
print(game.board.get_piece_at((2, 0)))  # white pawn at (2, 0)
print(game.board.get_piece_at((1, 0)))  # None
print(game.current_turn)               # Color.BLACK

# Intentar mover blanco de nuevo (es turno negro)
print(game.make_move((2, 0), (3, 0)))  # False
