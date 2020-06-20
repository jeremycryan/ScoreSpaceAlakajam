import pygame
import sys
import constants as c
from scene import *
import math
import time


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        self.corridor = Corridor(self)
        self.player = Player(self)
        self.enemies = []
        self.pickups = []
        self.particles = []
        self.scroll_speed = 350
        self.shake_amp = 0
        self.shake_period = 0
        self.main()

    def update_screenshake(self, dt, events):
        self.shake_period += dt
        self.shake_amp *= 0.05**dt
        self.shake_amp = max(0, self.shake_amp - 30*dt)

    def shake(self, amp):
        self.shake_amp = max(self.shake_amp, amp)
        self.shake_period = 0

    def get_shake_offset(self):
        x = self.shake_amp * math.cos(time.time() * 30)
        y = self.shake_amp * math.cos(time.time() * 24)
        return x, y

    def update_globals(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        return events

    def main(self):
        current_scene = ConnectionScene(self)
        while True:
            current_scene.main()
            current_scene = current_scene.next_scene()



if __name__=="__main__":
    Game()
