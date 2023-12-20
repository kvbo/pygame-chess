from pympler import asizeof
from lib.g_types import Pos
from lib import constants
from typing import List, Tuple
from game import Game
import pygame


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

      game.poll(event)

    game.draw()   
    pygame.display.flip()
    clock.tick(60) 

  pygame.quit()
  

if __name__ == "__main__":
  main()