from typing import List
from lib import g_types, piece
from moves import *

ext = {
  'white': 'lt',
  'black': 'dt'
}

class Pawn(piece.Piece):
  def __init__(self, turn):
    self.enpassantable = False
    self.snapshot = None
    self.notation = "p"
    
    super().__init__(g_types.PieceType.PAWN, f"./assets/Chess_p{ext[turn]}45.svg", [
      PawnBasic,
      PawnLeap,
      PawnCapture,
      PawnEnpassantCapture,
    ], turn)

class Rook(piece.Piece):
  def __init__(self, turn):
    self.notation = "R"

    super().__init__(g_types.PieceType.ROOK, f"./assets/Chess_r{ext[turn]}45.svg", [
      RookVertical,
      RookHorizontal,
    ], turn)


class Knight(piece.Piece):

  def __init__(self, turn):
    self.notation = "N"
    
    super().__init__(g_types.PieceType.KNIGHT, f"./assets/Chess_n{ext[turn]}45.svg", [
      KnightMove
    ], turn)


class Bishop(piece.Piece):
  def __init__(self, turn):
    self.notation = "B"

    super().__init__(g_types.PieceType.BISHOP, f"./assets/Chess_b{ext[turn]}45.svg", [
      BishopDiagonal
    ], turn)


class Queen(piece.Piece):
  def __init__(self, turn):
    self.notation = "Q"

    super().__init__(g_types.PieceType.QUEEN, f"./assets/Chess_q{ext[turn]}45.svg", [
      RookVertical,
      RookHorizontal,
      BishopDiagonal,
    ], turn)


class King(piece.Piece):
  def __init__(self, turn):
    self.notation = "K"

    super().__init__(g_types.PieceType.KING, f"./assets/Chess_k{ext[turn]}45.svg", [
      KingMove,
      Castle
    ], turn)


