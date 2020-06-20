import pygame
import constants as c
import math
import random


class Bullet:

    def __init__(self, game, x, y, dir, speed=1500, radius=10, spread=17):
        self.game = game
        self.x = x
        self.y = y
        self.dir = dir
        self.speed = speed
        self.radius = 12
        self.spread = spread
        self.apply_spread()

    def apply_spread(self):
        angle = math.atan2(self.dir[1], self.dir[0])
        variation = self.spread / 180 * math.pi
        angle += (random.random() - 0.5) * variation
        new_x = math.cos(angle)
        new_y = math.sin(angle)
        self.dir = (new_x, new_y)

    def update(self, dt, events):
        self.x += self.dir[0] * dt * self.speed
        self.y += self.dir[1] * dt * self.speed

    def draw(self, surface):
        x = int(self.x)
        y = int(self.y)
        pygame.draw.circle(surface, c.RED, (x, y), self.radius)
