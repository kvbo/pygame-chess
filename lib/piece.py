import math
from lib import  g_types, constants
from typing import List, Any
import pygame


class Piece(pygame.sprite.Sprite):
  def __init__(self, 
               ptype: "g_types.PieceType", 
               img: str, 
               moves: List[Any], 
               turn: str
               ):
    self.turn = turn
    self.num_of_moves   = 0
    self.ptype          = ptype
    self.moves          = moves
 

    pygame.sprite.Sprite.__init__(self)
    
    self.file_name      = img
    self.img            = pygame.image.load(img)
    img_rect = self.img.get_rect()
    self.surface        = pygame.Surface((constants.SQUARE_WIDTH, constants.SQUARE_HEIGHT), pygame.SRCALPHA)
    self.rect           = self.surface.get_rect()

    self.surface.blit(self.img, 
                      [ math.floor((self.rect.width - img_rect.width ) / 2), 
                        math.floor((self.rect.height - img_rect.height ) / 2),
                      ])
  
  def copy(self):
    new_piece = Piece(self.ptype, self.file_name, self.moves, self.turn)
    # Copy necessary attributes
    new_piece.turn = self.turn
    new_piece.num_of_moves = self.num_of_moves
    new_piece.ptype = self.ptype
    new_piece.moves = self.moves

    # Copy the image and surface content
    
    new_piece.surface = pygame.Surface((constants.SQUARE_WIDTH, constants.SQUARE_HEIGHT), pygame.SRCALPHA)
    new_piece.rect = new_piece.surface.get_rect()
    new_piece.notation =  self.notation 

    if self.ptype == g_types.PieceType.PAWN:
      new_piece.enpassantable = self.enpassantable 
      new_piece.snapshot = self.snapshot 

    new_piece.surface.blit(new_piece.img, (
        math.floor((new_piece.rect.width - new_piece.img.get_width()) / 2),
        math.floor((new_piece.rect.height - new_piece.img.get_height()) / 2),
    ))

    return new_piece