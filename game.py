from piece import Pawn, King, Queen, Bishop, Rook, Knight
from lib import constants, g_types
from typing import List, Dict
import pygame
from copy import copy
from utils import warp, timing, normalize
import mixins


class SFXMixin:
  SFX: Dict[str, pygame.mixer.Sound | None ] = {}

  def add_sound(self, name, fp):
    try:
      sound = pygame.mixer.Sound(fp)
      self.SFX[name] = sound

    except:
      print(f"{fp}:  File not found")


  def play_sound(self, name):
    s = self.SFX.get(name, None)
    if s:
      s.play()

  def remove_sound(self, name):
    del self.SFX[name]


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
    new_square.color = self.color 
    new_square.highlight = self.highlight  
    
    new_square.blit(self, (0, 0))

    return new_square


class Game(mixins.CopyBoardMixin, mixins.GameplayMixin, SFXMixin):
  def __init__(self, screen):
    self.screen = screen
    self.setup()

    sounds: List[str] = [ "./assets/move.ogg", "./assets/illegal.wav", "./assets/capture.wav", "./assets/check.wav" ]

    for i in sounds:
      fp = i
      name = i.split("/")[2][0:-4]
      self.add_sound(name, fp)


  def setup(self):
    self.board: List[List[Square]] = []
    self.pre_action = None
    self.post_action = None
    self.promote_menu = None
    self.promote_at = None
    self.turn = "white"
    self._moves_count = 1
    self.selected = []
    self._king_tiles = {
      "white": None,
      "black": None
    }

    self.highlight_square = [0, 0]
    self._should_highlight = False
    self.playing = []

    c = [constants.SQUARE_LIGHT, constants.SQUARE_DARK]
    alpha = "a|b|c|d|e|f|g|h".split("|")
    numeric = "1|2|3|4|5|6|7|8".split("|")

    for i in range(0, 8):
      col = []
      for j in range(0, 8):
        s = Square(c[warp(j, 2)],x=i, y=j, name=f"{alpha[i]}{numeric[j]}")
        col.append(s)

      self.board.append(col)
      c.reverse()

  @property
  def should_highlight(self):
    return self._should_highlight

  @should_highlight.setter
  def should_highlight(self, value):
    self._should_highlight = value

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
      clr = constants.SQUARE_LIGHT
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
    self.update()

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
        3 
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
    _ = ["white", "black"]

    self.turn = _[ warp(self.moves_count, 2 )]
    print(self.turn, self.moves_count, warp(self.moves_count, 2 ) )
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


  def poll(self, event: pygame.event.Event):
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_r:
        self.setup()
        self.init()

    if event.type == pygame.MOUSEBUTTONDOWN:
      previously_highlighted_square = self.highlight_square
      self.highlight_square = normalize(pygame.mouse.get_pos())


      if previously_highlighted_square == self.highlight_square and self.should_highlight:
        self.should_highlight = False

      elif self.promote_at:

        self.promote(normalize(pygame.mouse.get_pos(), to_pos=True))

      else:
        square = self.get_square(*normalize(pygame.mouse.get_pos(), to_pos=True))
        self.add_to_played(square)