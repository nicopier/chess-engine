from domain.board import Board

board = Board()
print(board.board[1][0])  # debería mostrar un peón blanco
print(board.board[6][0])  # debería mostrar un peón negro
print(board.board[3][3])  # debería mostrar None