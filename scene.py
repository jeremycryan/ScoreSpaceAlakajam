import pygame
import constants as c
from corridor import Corridor
from player import Player
from enemy import Dasher, Crawler, CrawlerCeiling
import random


class Scene:
    def __init__(self, game):
        self.game = game

    def main(self):
        pass

    def next_scene(self):
        raise NotImplementedError("Scene must implement next_scene")


class OnBusScene(Scene):
    def main(self):
        self.car_surf = pygame.image.load("images/subway_car_interior.png")
        clock = pygame.time.Clock()

        while True:
            dt = clock.tick(60)
            events = self.game.update_globals()

    def draw_subway_car(self):
        x = c.WINDOW_WIDTH//2 - self.car_surf.get_width()//2
        y = c.WINDOW_HEIGHT//2 - self.car_surf.get_height()//2

    def next_scene(self):
        return ConnectionScene()


class ConnectionScene(Scene):

    def next_scene(self):
        return ConnectionScene(self.game)

    def main(self):
        clock = pygame.time.Clock()
        self.corridor = Corridor(self.game)
        self.corridor.x = 0
        self.player = self.game.player
        self.player.movement_enabled = True
        self.player.in_bus = False
        self.game.enemies = []
        self.game.pickups = []
        self.since_enemy = 0
        self.game.scroll_speed = 0

        self.circle_radius = 0

        while True:
            dt = clock.tick(60)/1000
            events = self.game.update_globals()

            circle_speed = 800
            if self.scene_over():
                if self.circle_radius <= 0:
                    break
                self.circle_radius -= circle_speed * dt
                if self.circle_radius <= 0:
                    self.circle_radius = 0
                self.player.movement_enabled = False
                self.player.in_bus = True
                dx = self.corridor.end_subway.x + 475 - self.player.x
                dy = c.WINDOW_HEIGHT * 0.7 - self.player.y
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
        return False

    def update_scrolling(self, dt, events):
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
        self.since_enemy += dt
        if self.since_enemy > 1 and self.game.scroll_speed > 100:
            choices = [self.spawn_crawler_wave,
                    self.spawn_crawler_ceiling_wave,
                    self.spawn_dasher]
            random.choice(choices)()
            self.since_enemy = 0
        for enemy in self.game.enemies[::-1]:
            if enemy.dead and enemy.remove_on_death:
                self.game.enemies.remove(enemy)
            elif enemy.x < -500 or enemy.x > c.WINDOW_WIDTH + 500 or enemy.y < -500 or enemy.y > c.WINDOW_HEIGHT + 500:
                self.game.enemies.remove(enemy)

    def spawn_dasher(self):
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
