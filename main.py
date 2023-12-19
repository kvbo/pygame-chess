from pympler import asizeof
from lib.g_types import Pos
from lib import constants
from typing import List, Tuple
from game import Game, Square
import math
import pygame


def normalize(pos: Tuple, to_pos=False):
  left = math.floor(pos[0] / constants.SQUARE_WIDTH) 
  top =math.floor(pos[1] / constants.SQUARE_HEIGHT) 
  
  if not to_pos:
    left *= constants.SQUARE_WIDTH
    top *= constants.SQUARE_HEIGHT
    
  return (left, top)

playing = []

def main():
  # pygame setup
  pygame.init()
  screen = pygame.display.set_mode((constants.SQUARE_WIDTH * 8, constants.SQUARE_HEIGHT * 8))
  pygame.display.set_caption("Chess")
  clock = pygame.time.Clock()
  running = True

  game = Game(screen)
  game.init()

  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

      if event.type == pygame.KEYUP:
        if event.key == pygame.K_r:
          game.setup()
          game.init()

      if event.type == pygame.MOUSEBUTTONDOWN:
        previously_highlighted_square = game.highlight_square
        game.highlight_square = normalize(pygame.mouse.get_pos())

        if previously_highlighted_square == game.highlight_square and game.should_highlight:
          game.should_highlight = False

        elif game.promote_at:
          game.promote(normalize(pygame.mouse.get_pos(), to_pos=True))
        else:
          game.should_highlight = True

          square = game.get_square(*normalize(pygame.mouse.get_pos(), to_pos=True))
          game.add_to_played(square)

    game.update()
    game.draw()
          
    pygame.display.flip()

    clock.tick(60) 

  pygame.quit()
  

if __name__ == "__main__":
  main()