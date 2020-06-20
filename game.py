import pygame
import sys
import constants as c
from scene import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        self.corridor = Corridor(self)
        self.player = Player(self)
        self.enemies = []
        self.scroll_speed = 350
        self.main()

    def update_globals(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        return events

    def main(self):
        current_scene = ConnectionScene(self)
        current_scene.main()



if __name__=="__main__":
    Game()
