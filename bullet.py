import pygame
import constants as c
import math
import random


class Bullet:

    shadow = None

    def __init__(self, game, x, y, dir, speed=1500, radius=10, spread=14):
        self.game = game
        self.x = x
        self.y = y
        self.dir = dir
        self.speed = speed
        self.radius = 12
        self.spread = spread
        self.apply_spread()

        if Bullet.shadow is None:
            new = pygame.Surface((self.radius*3, self.radius*3))
            new.fill(c.BLACK)
            pygame.draw.circle(new, (255, 255, 100), (self.radius*3//2, self.radius*3//2), self.radius*3//2)
            new.set_colorkey(c.BLACK)
            new.set_alpha(100)
            Bullet.shadow = new

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
        sx, sy = self.game.get_shake_offset()
        surface.blit(self.shadow, (x + sx - self.shadow.get_width()//2, y + sx - self.shadow.get_width()//2))
        pygame.draw.circle(surface, c.WHITE, (int(x + sx), int(y + sy)), int(self.radius * 0.75))
