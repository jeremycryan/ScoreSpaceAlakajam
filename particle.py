import pygame
import random
import math


class Particle:
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.age = 0
        self.dead = False

    def update(self, dt, events):
        self.age += dt

    def draw(self, surface):
        pass


class DasherSmoke(Particle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        angle = random.random() * 2 * math.pi
        distance = random.random() * 80
        self.x = distance * math.sin(angle) + x
        self.y = distance * math.cos(angle) + y
        self.radius = 30
        self.max_radius = 0
        self.color = (255, 133, 40)

    def update(self, dt, events):
        super().update(dt, events)
        self.radius = max(40 - self.age*30, 0)
        if self.radius == 0:
            self.dead = True
        self.max_radius += 100 * dt

        self.y -= 100 * dt

    def draw(self, surface):
        color = self.color
        rad = min(self.max_radius, self.radius)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(rad))

class DasherSmokeRed(DasherSmoke):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.color = (220, 70, 60)
        self.radius = 40
