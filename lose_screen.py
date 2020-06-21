import pygame
import time
from scene import Scene
import constants as c
from title_screen import TitleScreen


class LoseScreen(Scene):
    def main(self):
        self.car_surf = pygame.image.load("images/subway_car_interior_empty.png")
        clock = pygame.time.Clock()
        self.age = 0

        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade.set_alpha(255)
        self.shade_alpha = 1.0
        self.shade_target_alpha = 0

        self.proceed = False
        self.popup_age = 0
        self.popup_visible = True
        self.game.player.dead = True

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

            self.game.screen.fill(c.BLACK)
            self.draw_subway_car(self.game.screen)
            if self.popup_visible:
                self.draw_popup(self.game.screen)

            if self.popup_age > 6.5:
                text = "PRESS ENTER TO RESTART"
                if time.time() % 1 < 0.7:
                    surf = self.game.ledger_font.render(text, 0, (c.WHITE))
                    x = c.WINDOW_WIDTH//2 - surf.get_width()//2
                    y = c.WINDOW_HEIGHT - 60
                    self.game.screen.blit(surf, (x, y))

                surf = self.game.score_font.render("GAME OVER", 0, (255, 100, 100))
                x = c.WINDOW_WIDTH//2 - surf.get_width()//2
                y = c.WINDOW_HEIGHT - 110
                self.game.screen.blit(surf, (x, y))

                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.proceed = True

            self.game.screen.blit(self.shade, (0, 0))
            pygame.display.flip()

            if self.proceed and self.popup_age > 5:
                self.shade_target_alpha = 1
                if self.shade_alpha == 1 and self.shade_target_alpha == 1:
                    self.game.level += 1
                    self.game.score = self.new_score()
                    break

    def draw_subway_car(self, surface):
        x = c.WINDOW_WIDTH//2 - self.car_surf.get_width()//2
        y = c.WINDOW_HEIGHT//2 - self.car_surf.get_height()//2
        surface.blit(self.car_surf, (x, y))

    def draw_popup(self, surface):
        lines = ["CASH:", "x LEVEL:", "+ SAVINGS:"]
        if not self.game.player.dead:
            lines.append("- FARE:")

        d = {"CASH:": self.game.player.cash_this_level,
            "x LEVEL:": self.game.level,
            "+ SAVINGS:": self.game.score,
            "- FARE:": 1.50}

        x = c.WINDOW_WIDTH//2
        amt = 5000 * 2**(-self.popup_age * 9)
        y = min(130, 140 - amt)
        surface.blit(self.frame, (c.WINDOW_WIDTH//2 - self.frame.get_width()//2, y-35))
        for i, line in enumerate(lines):
            if self.popup_age < i + 1.5:
                break
            surf = self.game.ledger_font.render(line, 1, c.WHITE)
            color = (255, 100, 100) if line == "- FARE:" else (100, 255, 100)
            value = f"{d[line]}"
            if line in ["CASH:", "- FARE:", "+ SAVINGS:"]:
                value = f"${value}"
            if line == "- FARE:":
                value += "0"
            surf2 = self.game.ledger_font.render(value, 1, color)
            surface.blit(surf, (x - surf.get_width(), y))
            surface.blit(surf2, (x + 10, y))
            y += surf.get_height()*0.85
        if self.popup_age > len(lines) + 1.5:
            surf = self.game.score_font.render(f"${float(self.new_score())}0", 1, c.WHITE)
            surface.blit(surf, (x - surf.get_width()//2, 220))

    def new_score(self):
        new = self.game.score + self.game.player.cash_this_level * self.game.level
        if not self.game.player.dead:
            new -= 1.50
        return new


    def next_scene(self):
        return TitleScreen(self.game)
