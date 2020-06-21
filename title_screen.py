import pygame
import constants as c
from scene import ConnectionScene, Scene
import random
import time


class TitleScreen(Scene):
    def main(self):
        self.car_surf = pygame.image.load("images/subway_car_interior.png")
        clock = pygame.time.Clock()
        self.age = 0

        self.shake_target = [0, 0]
        self.shake_pos = [1, 0]
        self.shake_amp = 15

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade.set_alpha(255)
        self.shade_alpha = 1.0
        self.shade_target_alpha = 0

        self.proceed = False
        self.popup_age = 0
        self.popup_visible = True
        self.title = pygame.image.load("images/title.png")
        self.title = pygame.transform.scale(self.title, (self.title.get_width()*2, self.title.get_height()*2))

        self.frame = pygame.image.load("images/frame.png")

        while True:
            dt = clock.tick(60)/1000
            if dt > 1/30:
                dt = 1/30
            events = self.game.update_globals()
            self.age += dt

            if self.popup_visible:
                self.popup_age += dt

            speed = 2
            if self.shade_alpha > self.shade_target_alpha:
                self.shade_alpha = max(0, self.shade_alpha - speed*dt)
            elif self.shade_alpha < self.shade_target_alpha:
                self.shade_alpha = min(1.0, self.shade_alpha + speed*dt)
            self.shade.set_alpha(self.shade_alpha * 255)


            dx = self.shake_target[0] - self.shake_pos[0]
            dy = self.shake_target[1] - self.shake_pos[1]
            self.shake_pos[0] += dx*dt*4
            self.shake_pos[1] += dy*dt*4

            if c.distance_between_points(*self.shake_pos, *self.shake_target) < 2:
                self.shake_target = [random.random()*2 - 1, random.random()*2 - 1]

            self.game.screen.fill(c.BLACK)
            self.draw_subway_car(self.game.screen)

            text = "PRESS ENTER TO BEGIN"
            if time.time() % 1 < 0.7:
                surf = self.game.ledger_font.render(text, 0, (c.WHITE))
                x = c.WINDOW_WIDTH//2 - surf.get_width()//2
                y = c.WINDOW_HEIGHT - 40
                self.game.screen.blit(surf, (x, y))

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.proceed = True

            x = c.WINDOW_WIDTH//2 - self.title.get_width()//2
            y = 40
            self.game.screen.blit(self.title, (x, y))

            self.game.screen.blit(self.shade, (0, 0))
            pygame.display.flip()

            if self.proceed:
                self.shade_target_alpha = 1
                if self.shade_alpha == 1 and self.shade_target_alpha == 1:
                    self.game.level = 1
                    self.game.score = 0
                    break

    def draw_subway_car(self, surface):
        x = c.WINDOW_WIDTH//2 - self.car_surf.get_width()//2 + self.shake_pos[0] * self.shake_amp
        y = c.WINDOW_HEIGHT//2 - self.car_surf.get_height()//2 + self.shake_pos[1] * self.shake_amp
        surface.blit(self.car_surf, (x, y))


    def next_scene(self):
        return ConnectionScene(self.game)
