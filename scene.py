import pygame
import constants as c
from corridor import Corridor
from player import Player
from enemy import *
import random
import time
import math
from sprite_tools import SpriteSheet, Sprite


class Scene:
    def __init__(self, game):
        self.game = game

    def main(self):
        pass

    def next_scene(self):
        raise NotImplementedError("Scene must implement next_scene")


class Controls(Scene):
    def __init__(self, game):
        self.game = game

    def next_scene(self):
        return ConnectionScene(self.game)

    def main(self):
        inst = SpriteSheet("images/controls.png", (2, 1), 2)
        sprite = Sprite(4)
        sprite.add_animation({"Idle": inst})
        sprite.start_animation("Idle")
        clock = pygame.time.Clock()
        age = 0
        shade = pygame.Surface(c.WINDOW_SIZE)
        shade.fill(c.BLACK)
        shade.set_alpha(255)
        while True:
            end = 4
            if age < 0.25:
                shade.set_alpha((0.25 - age)*255/0.25)
            elif age > end - 0.25:
                shade.set_alpha((age - end + 0.25)*255/0.25)
            else:
                shade.set_alpha(0)
            sprite.set_position((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2))
            dt = clock.tick(60)/1000
            age += dt
            events = self.game.update_globals()
            sprite.update(dt)
            sprite.draw(self.game.screen)
            self.game.screen.blit(shade, (0, 0))
            pygame.display.flip()
            if age >= end:
                break


class OnBusScene(Scene):
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

        self.frame = pygame.image.load("images/frame.png")

        self.game.bus_ride.play(-1)

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
            if self.popup_visible:
                self.draw_popup(self.game.screen)

            if self.popup_age > 6.5:
                text = "PRESS ENTER TO CONTINUE"
                if time.time() % 1 < 0.7:
                    surf = self.game.ledger_font.render(text, 0, (c.WHITE))
                    x = c.WINDOW_WIDTH//2 - surf.get_width()//2
                    y = c.WINDOW_HEIGHT - 40
                    self.game.screen.blit(surf, (x, y))

                for event in events:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        if self.proceed == False:
                            self.proceed = True
                            self.game.press_enter.play()

            self.game.screen.blit(self.shade, (0, 0))
            pygame.display.flip()

            if self.proceed and self.popup_age > 5:
                self.game.bus_ride.fadeout(400)
                self.shade_target_alpha = 1
                if self.shade_alpha == 1 and self.shade_target_alpha == 1:
                    self.game.score = self.new_score()
                    self.game.level += 1
                    break

    def draw_subway_car(self, surface):
        x = c.WINDOW_WIDTH//2 - self.car_surf.get_width()//2 + self.shake_pos[0] * self.shake_amp
        y = c.WINDOW_HEIGHT//2 - self.car_surf.get_height()//2 + self.shake_pos[1] * self.shake_amp
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
        return ConnectionScene(self.game)


class ConnectionScene(Scene):

    def next_scene(self):
        if self.game.player.dead:
            from lose_screen import LoseScreen
            return LoseScreen(self.game)
        return OnBusScene(self.game)

    def main(self):
        clock = pygame.time.Clock()
        self.corridor = Corridor(self.game, length=3000 + 3000*self.game.level)
        self.corridor.x = 0
        self.player = self.game.player
        self.player.movement_enabled = True
        self.player.in_bus = False
        self.player.cash_this_level = 0
        self.player.dead = False
        self.player.hp = 3
        self.player.sprite.start_animation("Running")
        self.player.y = self.corridor.floor_y() - 48
        self.player.y_velocity = -600
        self.game.enemies = []
        self.game.pickups = []
        self.since_enemy = 0
        self.game.scroll_speed = 0

        self.flash = pygame.Surface(c.WINDOW_SIZE)
        self.flash.fill(c.WHITE)
        self.flash.set_alpha(0)

        self.bone = pygame.image.load("images/bone.png")
        self.bone = pygame.transform.scale(self.bone, (self.bone.get_width()*3//2, self.bone.get_height()*3//2))

        self.circle_radius = 0

        self.cash_disp = 0
        self.age = 0
        self.since_death = 0

        self.game.battle_music.play(-1)

        while True:
            dt = clock.tick(60)/1000
            events = self.game.update_globals()
            self.game.update_slowdown(dt, events)
            dt *= self.game.slowdown
            if dt > 1/30:
                dt = 1/30
            self.age += dt


            self.flash.set_alpha(self.game.flash_alpha)
            self.game.flash_alpha = max(0, self.game.flash_alpha - 1000*dt)

            if self.game.player.dead:
                self.since_death += dt

            circle_speed = 800
            if self.scene_over():
                self.game.battle_music.fadeout(800)
                if self.circle_radius <= 0:
                    break
                self.circle_radius -= circle_speed * dt
                if self.circle_radius <= 0:
                    self.circle_radius = 0
                self.player.movement_enabled = False
                self.player.in_bus = True
                dx = self.corridor.end_subway.x + 475 - self.player.x
                dy = c.WINDOW_HEIGHT * 0.7 - self.player.y
                if not self.player.dead:
                    self.player.x += dx*dt*4
                    self.player.y += dy*dt*4
            else:
                self.circle_radius += circle_speed * dt
                if self.circle_radius >= c.WINDOW_WIDTH:
                    self.circle_radius = c.WINDOW_WIDTH

            self.corridor.update(dt, events)
            self.player.update(dt, events)
            self.game.update_screenshake(dt, events)
            self.update_scrolling(dt, events)
            self.update_enemies(dt, events)
            self.update_pickups(dt, events)
            self.update_particles(dt, events)

            self.game.screen.fill((120, 120, 120))
            self.corridor.draw(self.game.screen)
            for particle in self.game.particles:
                particle.draw(self.game.screen)
            for enemy in self.game.enemies:
                enemy.draw(self.game.screen)
            for pickup in self.game.pickups:
                pickup.draw(self.game.screen)
            self.player.draw(self.game.screen)
            self.draw_score(self.game.screen, dt)
            if self.flash.get_alpha() > 0:
                self.game.screen.blit(self.flash, (0, 0))
            self.draw_circle(self.game.screen)
            pygame.display.flip()

    def draw_circle(self, surface):
        width = max(1, int(700 - self.circle_radius))
        if self.circle_radius >= c.WINDOW_WIDTH:
            return
        rad = int(self.circle_radius)
        x, y = int(self.game.player.x), int(self.game.player.y)
        pygame.draw.circle(surface, c.BLACK, (x, y), rad + width, width)

    def scene_over(self):
        if self.corridor.end_subway.x + 430 + 80 >= self.player.x >= self.corridor.end_subway.x + 430 and self.player.y >= c.WINDOW_HEIGHT//2:
            return True
        if self.since_death > 1:
            return True
        return False

    def update_scrolling(self, dt, events):
        if self.game.player.dead:
            return
        if self.game.scroll_speed < 350:
            self.game.scroll_speed += 200 * dt
            if self.game.scroll_speed >= 350:
                self.game.scroll_speed = 350

    def update_pickups(self, dt, events):
        for item in self.game.pickups[::-1]:
            item.update(dt, events)
            if c.distance_between_points(item.x, item.y, self.player.x, self.player.y) < self.player.width//2:
                item.get()
                self.game.pickups.remove(item)

    def update_particles(self, dt, events):
        for particle in self.game.particles[::-1]:
            particle.update(dt, events)
            if particle.dead:
                self.game.particles.remove(particle)

    def update_enemies(self, dt, events):
        for enemy in self.game.enemies:
            enemy.update(dt, events)

        self.update_spawning(dt, events)

        for enemy in self.game.enemies[::-1]:
            if enemy.dead and enemy.remove_on_death:
                self.game.enemies.remove(enemy)
            elif enemy.x < -500 or enemy.x > c.WINDOW_WIDTH + 500 or enemy.y < -500 or enemy.y > c.WINDOW_HEIGHT + 500:
                self.game.enemies.remove(enemy)

    def spawn_dasher(self, length=1):
        new_enemy = Dasher(self.game, 0, 0)
        y_min = c.WINDOW_HEIGHT//2 - self.corridor.width//2 + new_enemy.radius
        y_max = y_min + self.corridor.width - new_enemy.radius*2
        y = random.random() * (y_max - y_min) + y_min
        x = c.WINDOW_WIDTH + new_enemy.radius
        new_enemy.y = y
        new_enemy.x = x
        self.game.enemies.append(new_enemy)

    def spawn_crawler_wave(self, length=3):
        spacing = 72
        for i in range(length):
            new_enemy = Crawler(self.game, c.WINDOW_WIDTH + 50 + spacing*i, 0)
            self.game.enemies.append(new_enemy)

    def spawn_crawler_ceiling_wave(self, length=3):
        spacing = 72
        for i in range(length):
            new_enemy = CrawlerCeiling(self.game, c.WINDOW_WIDTH + 50 + spacing*i, 0)
            self.game.enemies.append(new_enemy)

    def spawn_blocker(self, num=None):
        new_enemy = Blocker(self.game)
        self.game.enemies.append(new_enemy)

    def update_spawning(self, dt, events):
        if self.game.player.dead:
            return

        self.since_enemy += dt
        period = 0.2 + 6/(self.game.level + 2)
        if self.since_enemy > period and self.game.scroll_speed > 200:
            self.since_enemy = 0
            if self.game.level == 1:
                choices = [self.spawn_crawler_wave]
                num = random.choice([1, 2])
                random.choice(choices)(num)
            elif self.game.level == 2:
                choices = [self.spawn_crawler_wave,
                    self.spawn_crawler_ceiling_wave]
                num = random.choice([1, 2, 2, 3])
                random.choice(choices)(num)
            elif self.game.level == 3:
                choices = [self.spawn_crawler_wave,
                    self.spawn_crawler_ceiling_wave,
                    self.spawn_blocker]
                num = random.choice([2, 3])
                random.choice(choices)(num)
            elif self.game.level == 4:
                choices = [self.spawn_crawler_wave,
                    self.spawn_crawler_ceiling_wave,
                    self.spawn_dasher,
                    self.spawn_blocker]
                num = random.choice([2, 3, 3, 3, 4])
                random.choice(choices)(num)
            else:
                choices = [self.spawn_crawler_wave,
                    self.spawn_crawler_ceiling_wave,
                    self.spawn_dasher,
                    self.spawn_blocker]
                num = random.choice([3, 4, 4])
                random.choice(choices)(num)

    def draw_score(self, surface, dt):
        dc = self.game.player.cash_this_level - self.cash_disp
        self.cash_disp = min(self.game.player.cash_this_level, self.cash_disp + dc * 10 * dt)

        text = f"${float(round(self.cash_disp, 1))}0"

        color = 180 + 75 * min(dc/5, 1)
        scale = 1 + 1.2*min(dc/30, 1)
        surf = self.game.score_font.render(text, 1, (color, color, color))
        surf = pygame.transform.scale(surf, (int(surf.get_width() * scale), int(surf.get_height() * scale)))
        score_text = f"SAVINGS: ${float(self.game.score)}0"
        score_surf = self.game.ledger_font.render(score_text, 1, (180, 180, 180))

        y = 40
        surface.blit(surf, (c.WINDOW_WIDTH//2 - surf.get_width()//2, y - surf.get_height()//2))
        surface.blit(score_surf, (c.WINDOW_WIDTH//2 - score_surf.get_width()//2, y + surf.get_height()*0.3))

        level = f"LEVEL {self.game.level}"
        if self.age < 5:
            surf = self.game.ledger_font.render(level, 1, (180, 180, 180))
            surf2 = pygame.Surface(surf.get_size())
            surf2.fill(c.BLACK)
            surf2.blit(surf, (0, 0))
            surf2.set_colorkey(c.BLACK)
            if self.age > 3:
                surf2.set_alpha((5 - self.age)/2*255)
            surface.blit(surf2, (c.WINDOW_WIDTH//2 - surf2.get_width()//2, c.WINDOW_HEIGHT - 50))

        bone = self.bone.copy()
        color = min(180 * self.player.since_hit, 180)
        color2 = 255 - min(75, 75 * self.player.since_hit)
        bone.fill((color2, color, color), special_flags=pygame.BLEND_MULT)
        surface.blit(bone, (35, 25))
        surf = self.game.score_font.render(f"x{max(self.game.player.hp, 0)}", 1, (color2, color, color))
        surface.blit(surf, (65, 30))
