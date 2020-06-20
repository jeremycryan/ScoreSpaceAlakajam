import pygame
import constants as c


class Corridor:
    def __init__(self, game):
        self.game = game
        self.width = 400

        self.margin = 30
        each_height = c.WINDOW_HEIGHT//2 - self.width//2 + self.margin
        self.top = pygame.Surface((c.WINDOW_WIDTH + self.margin * 2, each_height))
        self.bottom = pygame.Surface((c.WINDOW_WIDTH + self.margin * 2, each_height))
        self.top.fill(c.BLACK)
        self.bottom.fill(c.BLACK)
        self.x = 0

        self.bar = pygame.Surface((100, c.WINDOW_HEIGHT))
        self.bar.fill(c.BLACK)
        self.bar.set_alpha(30)

    def update(self, dt, events):
        self.x += self.game.scroll_speed * dt
        pass

    def draw(self, surface):
        sx, sy = self.game.get_shake_offset()

        offset = self.x % 200
        x = -self.x + sx % 200 - 200
        while x < c.WINDOW_WIDTH + 100:
            surface.blit(self.bar, (x, 0))
            x += 200

        surface.blit(self.top, (-self.margin + sx, -self.margin + sy))
        surface.blit(self.bottom, (-self.margin + sx, c.WINDOW_HEIGHT//2 + self.width//2 + sy))
