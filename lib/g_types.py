from enum import Enum
from lib import piece, constants


class Pos:
  def __init__(self, x: int, y: int) -> None:
    self.x = x
    self.y = y

  def get_pixel_pos(self, size=64):
    return [self.x * constants.SQUARE_WIDTH, self.y * constants.SQUARE_HEIGHT]
  
  def get_pos(self):
    return [ self.x, self.y ]


class PieceType(Enum):
  PAWN      = "pawn"
  KNIGHT    = "knight"
  BISHOP    = "bishop"
  ROOK      = "rook"
  QUEEN     = "queen"
  KING      = "king"


class Move(type):
  name = None

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    ...

  def __str__(self):
    return self.name if self.name else ""