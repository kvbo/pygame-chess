from piece import Pawn, King, Queen, Bishop, Rook, Knight
from lib import constants, g_types
from typing import List
import pygame
from copy import copy
from utils import warp, timing


class Square(pygame.Surface):
  def __init__(self, color, name, x, y):
    self.x = x
    self.y = y
    self.name = name
    super().__init__((constants.SQUARE_WIDTH, constants.SQUARE_HEIGHT))
    self.rect = self.get_rect()
    self.piece = None
    self.color = color
    self.highlight = None

    self.fill(self.color)


  def set_highlight(self, clr: str | None):
    self.highlight = clr
    self.draw()


  def __str__(self):
    return self.name + (f" ->{self.piece.ptype}" if self.piece else "")

  def draw(self):
    self.fill(self.highlight or self.color)

    if self.piece != None:
      self.blit(self.piece.surface, [0, 0])

  def position(self):
    return [ self.rect.width * self.x, self.rect.height * self.y ]
  
  def add_piece(self, piece):
    p = self.piece
    self.piece = piece
    return p
  
  def remove_piece(self):
    p = self.piece
    self.piece = None
    return p

  def copy(self):
    new_square = Square(self.color, self.name, self.x, self.y)
    # Copy necessary attributes
    new_square.rect = copy(self.rect)
    new_square.piece = self.piece.copy() if self.piece else None
    new_square.color = self.color  # If color is immutable, no need for deep copy
    new_square.highlight = self.highlight  # Same for highlight
    
    # If needed, manually copy the surface content
    new_square.blit(self, (0, 0))

    return new_square


class CopyBoardMixin:
  def copy_board(self) -> List[List[Square]]:
    copied_board = []
    for row in self.board:
      copied_row = []
      for square in row:
        # Deep copy each Square instance in the board
        copied_square = square.copy()
        copied_row.append(copied_square)
      copied_board.append(copied_row)
    return copied_board


class Game(CopyBoardMixin):
  def __init__(self, screen):
    self.screen = screen
    self.setup()

  def setup(self):
    self.board: List[List[Square]] = []
    self.pre_action = None
    self.post_action = None
    self._moves_count = 0
    self.promote_menu = None
    self.promote_at = None
    self.selected = []
    self._king_tiles = {
      "white": None,
      "black": None
    }

    self.highlight_square = [0, 0]
    self.should_highlight = False
    self.playing = []

    c = [constants.SQUARE_LIGHT, constants.SQUARE_DARK]
    alpha = "A|B|C|D|E|F|G|H".split("|")
    numeric = "1|2|3|4|5|6|7|8".split("|")

    for i in range(0, 8):
      col = []
      for j in range(0, 8):
        s = Square(c[warp(j, 2)],x=i, y=j, name=f"{alpha[i]}{numeric[j]}")
        col.append(s)

      self.board.append(col)
      c.reverse()


  def add_to_played(self, square):
    if len(self.playing) == 0 and square.piece != None:
      self.playing.append(square)

    elif len(self.playing) == 1:
      if square.piece != None and self.playing[0].piece.turn == square.piece.turn:
        self.playing.clear()

      self.playing.append(square)

    else:
      self.playing.clear()

  def update(self):
    if len(self.playing) > 1:
      self.move_piece(*self.playing)
      self.should_highlight = False
      self.playing.clear()

  @property
  def king_tiles(self) -> dict:
    return self._king_tiles
  
  @king_tiles.setter
  def king_tiles(self, value: Square):
    if value.piece == None or value.piece.ptype != g_types.PieceType.KING:
      raise "The square needs to contain a king piece"

    self._king_tiles[value.piece.turn] = value

  

  def promotion_page(self, tile):
    if self.promote_menu == None:
      clr = "#E3D99F"
      surface = pygame.Surface((constants.SQUARE_WIDTH * 8, constants.SQUARE_HEIGHT * 8))
      surface.fill(clr)

      pieces = [Rook, Knight, Bishop, Queen]
      turn = tile.piece.turn
      self.promote_menu = surface

      self.promotion_pieces = []
      for i, piece in enumerate(pieces, 0):

        s = Square(clr, x= i + 2, y=3, name="")
        s.add_piece(piece(turn))
        self.promotion_pieces.append(s)

    return self.promote_menu


  def promote(self, cords):
    tile = self.promote_at
    index = cords[0] - 2
    if index < 0 or index > 3 or cords[1] != 3:
      return False

    tile.add_piece(self.promotion_pieces[index].piece)

    self.promote_at = None
    self.promote_menu = None
    self.promotion_pieces = []


  def draw(self) -> None:
    if bool(self.promote_at):
      surface = self.promotion_page(self.promote_at)
      self.screen.blit(surface, [0, 0])

      for s in self.promotion_pieces:
        surface.blit(s, s.position())
        s.draw()

    else:
      for col in self.board:
        for square in col:
          self.screen.blit(square, square.position())
          square.draw()

    if self.should_highlight: 
      pygame.draw.rect(
        self.screen,
        constants.SQUARE_SECONDARY_HIGHLIGHT, 
        [self.highlight_square[0], self.highlight_square[1], constants.SQUARE_WIDTH, constants.SQUARE_HEIGHT],
        2, 
      )

  def get_square(self, x, y) -> Square | None:
    if x < 0 or x >= len(self.board) or y < 0 or y >= len(self.board[0]):
      return None
      
    return self.board[x][y]

  
  @property
  def moves_count(self):
    return self._moves_count

  @moves_count.setter
  def moves_count(self, value):
    self.turn = warp(self.moves_count ,2)
    self._moves_count = value 

  def init(self):
    for turn in ['white', 'black']:
      col = 0 if turn == "black" else 7
      power_pieces = [
        Rook,
        Knight, 
        Bishop, 
        King, 
        Queen, 
        Bishop, 
        Knight, 
        Rook
      ]

      for i in range(8):
        self.board[i][1 if turn == "black" else 6].add_piece(Pawn(turn))
        p = power_pieces[i](turn)
        s = self.get_square(i, col)
        s.add_piece(p)

        if p.ptype == g_types.PieceType.KING:
          self.king_tiles = s


  def move_piece(self, obj_1, obj_2, **kwargs):
    piece_to_remove = None

    if obj_2.piece == None or obj_2.piece.turn != obj_1.piece.turn:
      is_legal = False

      for move in obj_1.piece.moves:
        is_legal = move.check(obj_1, obj_2, game=self)

        if is_legal:
          print(f"{move}: {obj_1} to {obj_2}" )
          break
      
      if is_legal:
        temp_board = self.copy_board()

        piece_to_move   = obj_1.remove_piece()
        piece_to_remove = obj_2.add_piece(piece_to_move)

        if self.pre_action != None:
          self.pre_action()
          self.pre_action = None

        # check if move exposes king of current player
        turn = piece_to_move.turn
        other = "white" if turn == "black" else "black"

        if len(self.fchecker(self.king_tiles[turn])) > 0:
          self.board = temp_board
          self.print_board()
          self.fchecker(self.king_tiles[turn])
          
        else:
          piece_to_move.num_of_moves += 1
          self.moves_count += 1

          if self.post_action != None:
            self.post_action()
            self.post_action = None

          self.fchecker(self.king_tiles[other])

    return piece_to_remove


  def print_board(self):
    string = ""
    c = 0
    while c < 8: 
      r = 0
      while r < 8:
        piece =  self.board[r][c].piece
        if piece:
          if piece.ptype == g_types.PieceType.KING:
            self.king_tiles = self.board[r][c]
          p = f" {piece.notation} "
        else:
          p = " - "
        string += p
        r += 1
      string += "\n"
      c += 1

    print(string)


  @timing
  def fchecker(self, king_square: Square):   
    [ i.set_highlight(None) for k, i in self.king_tiles.items() ]

    for i in self.selected:
      i.set_highlight(None)

    self.selected = []

    def func(step_count, tuple_to_check , x = None, y = None, ):
      cord  = (
        x if x is not None and x >= 0 else king_square.x, 
        y if y is not None and y >= 0 else king_square.y
      )
      square = self.get_square(*cord)

      if square.piece != None:
        if square.piece.turn == king_square.piece.turn:
          return True
        
        elif square.piece.ptype not in tuple_to_check:
          return True
        
        if (step_count == 1 and square.piece.ptype in tuple_to_check[:2]) \
          or square.piece.ptype in tuple_to_check[2:]:

          self.selected.append(square)
          return True

      square.highlight = None
      return False

    track = [ False ] * 8
    
    step_count = 1

    straights = [g_types.PieceType.KING, g_types.PieceType.KING, g_types.PieceType.QUEEN, g_types.PieceType.ROOK ]
    diagonals = [g_types.PieceType.PAWN, g_types.PieceType.KING, g_types.PieceType.QUEEN, g_types.PieceType.BISHOP ]

    while False in track:
      ypos = king_square.y + step_count
      xpos = king_square.x + step_count
      yneg = king_square.y - step_count
      xneg = king_square.x - step_count 

      # straights
      if not track[0] and ypos < 8:
        track[0] = func(step_count, straights, y=ypos)
      else:
        track[0] = True

      if not track[1] and yneg >= 0:
        track[1] = func(step_count, straights, y=yneg)
      else:
        track[1] = True

      if not track[2] and xpos < 8:
        track[2] = func(step_count, straights, x=xpos)
      else:
        track[2] = True
        
      if not track[3] and xneg >= 0:
        track[3] = func(step_count, straights, x=xneg)
      else:
        track[3] = True


      # diagonals 
      if not track[4] and ypos < 8 and xpos < 8:
        track[4] = func(step_count, diagonals, x=xpos, y=ypos)
      else:
        track[4] = True

      if not track[5] and yneg >= 0 and xneg >= 0:
        track[5] = func(step_count, diagonals, x=xneg, y=yneg)
      else:
        track[5] = True

      if not track[6] and xpos < 8 and yneg >= 0 :
        track[6] = func(step_count, diagonals, x=xpos, y=yneg)
      else:
        track[6] = True
        
      if not track[7] and xneg >= 0 and ypos < 8:
        track[7] = func(step_count, diagonals, x=xneg, y=ypos)
      else:
        track[7] = True

      step_count += 1

    # check_knights
    squares = [
      [1, 2], [1, -2], [2, 1], [2, -1],
      [-1, -2], [-1, 2], [-2, 1], [-2, -1]
    ]

    for cords in squares:
      square = self.get_square(king_square.x + cords[0], king_square.y + cords[1])
      if square is None :
        continue
      
      if square.piece == None:
        square.highlight = None
        continue

      if square.piece.turn != king_square.piece.turn and square.piece.ptype == g_types.PieceType.KNIGHT:
        self.selected.append(square)


    for i in self.selected:
      i.set_highlight(constants.SQUARE_HIGHLIGHT)

      print("check at: ", i)
    
    if len(self.selected):
      king_square.set_highlight(constants.SQUARE_HIGHLIGHT)

    return self.selected