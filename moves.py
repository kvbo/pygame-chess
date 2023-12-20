from typing import List
from lib import g_types, piece
from moves import *

class PawnBasic(metaclass=g_types.Move):
  name = "pawn_basic"

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:   
    piece = old_tile.piece

    dir = -1 if piece.turn == "black" else 1

    if old_tile.y - new_tile.y == dir \
      and new_tile.x == old_tile.x \
      and new_tile.piece == None :

      if ( new_tile.y == 0 and dir == 1) \
        or ( new_tile.y == 7 and dir == -1):
        kwargs['game'].post_action = lambda: PawnBasic.promote(new_tile, kwargs['game'])

      return True
    return False

  @staticmethod
  def promote(tile, game):
    game.promote_at = tile


class PawnLeap(metaclass=g_types.Move):
  name = "pawn_leap"

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    piece = old_tile.piece

    board = kwargs['game'].board
    check_squares = [ new_tile, board[new_tile.x][5] if piece.turn == "white" else board[new_tile.x][2]]

    if piece.num_of_moves == 0 \
      and check_squares[0].piece == check_squares[1].piece == None \
      and old_tile.x == old_tile.x \
      and abs(old_tile.y - new_tile.y) == 2:

      kwargs['game'].post_action = lambda: PawnLeap.set_enpassantable(piece, kwargs['game'])
      return True
  
    return False

  @staticmethod
  def set_enpassantable(piece, game):
    piece.enpassantable = True
    piece.snapshot = game.moves_count


class PawnCapture(metaclass=g_types.Move):
  name = "pawn_capture"

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    piece = old_tile.piece  
    captured = new_tile.piece

    dir = -1 if piece.turn == "black" else 1

    if old_tile.y - new_tile.y == dir \
      and abs(new_tile.x - old_tile.x) == 1 \
      and captured:

      if ( new_tile.y == 0 and dir == 1) \
        or ( new_tile.y == 7 and dir == -1):
          
        kwargs['game'].post_action = lambda: PawnBasic.promote(new_tile, kwargs['game'])
      return True

    return False


class PawnEnpassantCapture(metaclass=g_types.Move):
  name = "en_passant"

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    board = kwargs['game'].board
    piece = old_tile.piece  

    dir = -1 if piece.turn == "black" else 1

    tile = board[new_tile.x][old_tile.y]

    if old_tile.y - new_tile.y == dir \
      and abs(new_tile.x - old_tile.x) == 1 \
      and new_tile.piece == None \
      and tile.piece \
      and tile.piece.ptype == g_types.PieceType.PAWN \
      and tile.piece.enpassantable \
      and tile.piece.snapshot == kwargs["game"].moves_count:
      
      kwargs["game"].post_action = lambda: PawnEnpassantCapture.remove_captured(tile)
      return True
    return False

  @staticmethod
  def remove_captured(tile):
    piece_to_remove  = tile.remove_piece()


class RookVertical(metaclass=g_types.Move):
  name = "vertical"

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    board = kwargs['game'].board

    try:
      dir = int((old_tile.y - new_tile.y )/ abs(old_tile.y - new_tile.y))

    except ZeroDivisionError:
      return False

    check_square = []
    i = old_tile.y - dir

    blocked = False

    while i < new_tile.y if dir == -1 else new_tile.y < i:
      if board[old_tile.x][i].piece != None:
        blocked = True
        break 

      i -= dir

    if not blocked and new_tile.x == old_tile.x:
      return True

    return False


class RookHorizontal(metaclass=g_types.Move):
  name = "horizontal"

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    board = kwargs['game'].board
    piece = old_tile.piece

    try:
      dir = int((old_tile.x - new_tile.x )/ abs(old_tile.x - new_tile.x))

    except ZeroDivisionError:
      return False

    check_square = []
    i = old_tile.x - dir

    blocked = False

    while i < new_tile.x if dir == -1 else new_tile.x < i:
      if board[i][old_tile.y].piece != None:
        blocked = True
        break 

      i -= dir

    if not blocked and new_tile.y == old_tile.y:
      return True

    return False


class BishopDiagonal(metaclass=g_types.Move):
  name = "diagonal"

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    board = kwargs['game'].board
    piece = old_tile.piece

    try:
      xdir = int((old_tile.x - new_tile.x ) / abs(old_tile.x - new_tile.x))
      ydir = int((old_tile.y - new_tile.y ) / abs(old_tile.y - new_tile.y))

    except ZeroDivisionError:
      return False

    xi = old_tile.x - xdir
    yi = old_tile.y - ydir

    is_on_path = False
    blocked = False

    while 0 <= xi < len(board) and 0 <= yi < len(board[0]): 
      tile = board[xi][yi]

      if tile.x == new_tile.x and tile.y == new_tile.y:
        is_on_path =  True
        break

      if tile.piece:
        blocked = True
        break

      yi -= ydir
      xi -= xdir

    if not blocked \
      and new_tile.y != old_tile.y \
      and new_tile.x != old_tile.x \
      and new_tile.color == old_tile.color \
      and is_on_path:
      return True

    return False


class KnightMove(metaclass=g_types.Move):
  name = "knight_basic"

  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    if abs(old_tile.x - new_tile.x) == 1 and abs(old_tile.y - new_tile.y) == 2 \
      or (abs(old_tile.y - new_tile.y) == 1 and abs(old_tile.x - new_tile.x) == 2):
      return True

    else:
      return False

class KingMove(metaclass=g_types.Move):
  name = "king_basic"
  
  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    if (abs(old_tile.x - new_tile.x) == 0 and abs(old_tile.y - new_tile.y) == 1) \
      or (abs(old_tile.x - new_tile.x) == 1 and abs(old_tile.y - new_tile.y) == 0) \
      or (abs(old_tile.x - new_tile.x) == 1 and abs(old_tile.y - new_tile.y) == 1):

      kwargs['game'].pre_action = lambda: KingMove.update_pos(new_tile, kwargs["game"])
      
      return True

    return False

  @staticmethod
  def update_pos(new_tile, game):
    game.king_tiles[new_tile.piece.turn] = new_tile


class Castle(metaclass=g_types.Move):
  name = "king_castle"
  
  @staticmethod
  def check(old_tile, new_tile, **kwargs) -> bool:
    board = kwargs['game'].board
    rook = None
    king = old_tile.piece

    if king.num_of_moves > 0:
      return False

    try:
      dir = int((old_tile.x - new_tile.x ) / abs(old_tile.x - new_tile.x))
    except ZeroDivisionError:
      return False

    blocked = False
    tile = None
    i = old_tile.x - dir

    buf_tile = None
    while 8 > i if dir == -1 else i >= 0:

      if buf_tile == None:
        buf_tile = board[i][old_tile.y]

      piece = board[i][old_tile.y].piece

      if piece != None and piece.ptype == g_types.PieceType.ROOK:
        rook = piece
        tile = board[i][old_tile.y]
        break

      if piece != None and piece.ptype != g_types.PieceType.ROOK:
        blocked = True
        break 

      i -= dir

    if rook and rook.num_of_moves == 0 \
       and not blocked \
       and abs(old_tile.x - new_tile.x) == 2 \
       and old_tile.y == new_tile.y:

      kwargs['game'].pre_action = lambda: Castle.move_rook(tile, buf_tile, kwargs["game"], new_tile)
      return True
      
    return False

  @staticmethod
  def move_rook(old_tile, new_tile, game, new_king_tile):
    piece_to_move   = old_tile.remove_piece()
    piece_to_move.num_of_moves += 1
    new_tile.add_piece(piece_to_move)

    KingMove.update_pos(new_king_tile, game)