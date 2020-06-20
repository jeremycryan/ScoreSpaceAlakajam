import pygame
import constants as c
from subway import Subway


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

        backdrop = pygame.Surface((c.WINDOW_WIDTH, self.width+2*self.margin))
        backdrop.blit(pygame.image.load("images/subway_platform_back.png"), (0, -c.WINDOW_HEIGHT//2 + self.width//2 + self.margin))
        self.backdrop_1 = pygame.Surface((c.WINDOW_WIDTH//2, backdrop.get_height()))
        self.backdrop_2 = pygame.Surface((c.WINDOW_WIDTH - self.backdrop_1.get_width(), backdrop.get_height()))
        self.backdrop_1.blit(backdrop, (0, 0))
        self.backdrop_2.blit(backdrop, (-self.backdrop_1.get_width(), 0))

        self.platform_tile = pygame.image.load("images/platform_tile.png")

        self.subway = Subway(self.game)


    def update(self, dt, events):
        self.x += self.game.scroll_speed * dt
        self.subway.update(dt, events)
        pass

    def draw(self, surface):

        sx, sy = self.game.get_shake_offset()

        boffset = -(self.x/5 % c.WINDOW_WIDTH)
        y = c.WINDOW_HEIGHT//2 - self.backdrop_1.get_height()//2
        surface.blit(self.backdrop_1, (boffset, y))
        surf = False
        while boffset < c.WINDOW_WIDTH:
            if boffset < -c.WINDOW_WIDTH/2:
                pass
            elif surf:
                surface.blit(self.backdrop_1, (boffset + sx//3, y + sy//3))
            else:
                surface.blit(self.backdrop_2, (boffset + sx//3, y + sy//3))
            boffset += c.WINDOW_WIDTH/2
            surf = not surf

        surface.blit(self.top, (-self.margin + sx, -self.margin + sy))
        surface.blit(self.bottom, (-self.margin + sx, c.WINDOW_HEIGHT//2 + self.width//2 + sy))

        self.subway.draw(surface)

        w = self.platform_tile.get_width()
        x = -self.x + sx % w - w
        while x < c.WINDOW_WIDTH + w:
            surface.blit(self.platform_tile, (x, c.WINDOW_HEIGHT//2 + self.width//2 - 28 + sy))
            x += w
