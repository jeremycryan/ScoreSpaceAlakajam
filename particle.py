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

class Shell(Particle):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.surf = pygame.image.load("images/shell.png")
        self.surf = pygame.transform.scale(self.surf, (self.surf.get_width()*2, self.surf.get_height()*2))
        self.rotate_speed = random.random() * 0.5 + 0.2
        self.velocity = [-300 - 100 * random.random(), -300 - 100*random.random()]
        self.angle = 0

    def update(self, dt, events):
        super().update(dt, events)
        self.velocity[1] += 2000 * dt
        self.angle += self.rotate_speed * dt
        self.angle %= 1

        if self.y >= self.game.corridor.floor_y() and self.velocity[1] > 0:
            self.velocity[1] = -abs(self.velocity[1]) * 0.3
        if self.y >= self.game.corridor.floor_y() and abs(self.velocity[1]) < 50:
            self.velocity[1] = 0
            self.velocity[0] = -self.game.scroll_speed
            self.rotate_speed = 0

        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt

        if self.x < -500 or self.age > 10:
            self.dead = True

    def draw(self, surface):
        sx, sy = self.game.get_shake_offset()
        x = self.x + sx
        y = self.y + sy
        angle = self.angle * 360
        surf = pygame.transform.rotate(self.surf, int(angle))
        surface.blit(surf, (x - surf.get_width()//2, y - surf.get_height()//2))
